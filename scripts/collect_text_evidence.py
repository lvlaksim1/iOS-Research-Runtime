#!/usr/bin/env python3
"""Copy bounded, UTF-8 diagnostic logs; never copy raw firmware or arbitrary files.

This is a host-side evidence minimizer, not a guest PCIe or boot verifier.
A permitted text extension does not establish absence of secrets in its contents.
"""
from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

EXTENSIONS = frozenset({".log", ".txt", ".json", ".jsonl", ".csv"})
MAX_FILE_BYTES = 1_048_576
MAX_TOTAL_BYTES = 4_194_304
MAX_FILES = 64
MAX_DEPTH = 8


def _is_link_or_junction(path: Path) -> bool:
    """Reject symbolic links, junctions and other Windows reparse points."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    return (
        stat.S_ISLNK(metadata.st_mode)
        or bool(getattr(metadata, "st_file_attributes", 0)
                & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
        or bool(getattr(os.path, "isjunction", lambda _p: False)(path))
    )


def _assert_plain_directory_chain(path: Path) -> None:
    """Reject existing linked/reparse ancestors BEFORE creating or writing.

    Recheck immediately before use; this guards pre-existing paths, not
    concurrent adversarial directory replacement (which needs handle-relative
    Windows I/O to exclude completely).
    """
    if ".." in path.parts:
        raise ValueError("parent traversal is not allowed")
    absolute = path.absolute()
    for component in reversed((absolute, *absolute.parents)):
        try:
            metadata = component.lstat()
        except FileNotFoundError:
            continue
        if _is_link_or_junction(component) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError("directory chain contains a link, reparse point or non-directory")


def _ensure_plain_directory(path: Path) -> None:
    _assert_plain_directory_chain(path)
    path.mkdir(parents=True, exist_ok=True)
    _assert_plain_directory_chain(path)


def _write_status(status: Path, value: str) -> None:
    _ensure_plain_directory(status.parent)
    if _is_link_or_junction(status):
        raise ValueError("status path is a link or reparse point")
    try:
        before = status.lstat()
    except FileNotFoundError:
        before = None
    if before is not None and not stat.S_ISREG(before.st_mode):
        raise ValueError("status must be an ordinary file")
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(status, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before is not None and
            (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
            raise ValueError("status changed during open")
        stream.truncate(0)
        stream.write(value)


def _safe_name(name: str) -> bool:
    lower = name.casefold()
    return (
        bool(name)
        and not name.startswith(".")
        and not lower.startswith("devicetree.")
        and not lower.startswith("dtree.")
        and lower != "dtree"
        and all(ord(c) >= 32 and c not in "/\\" for c in name)
    )


def _safe_text(data: bytes) -> bool:
    try:
        text = data.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return False
    return all((ord(c) >= 32 and not 127 <= ord(c) <= 159) or c in "\r\n\t" for c in text)


def _read_regular_file(path: Path) -> bytes | None:
    if _is_link_or_junction(path):
        return None
    try:
        before = path.stat(follow_symlinks=False)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE_BYTES:
            return None
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (opened.st_dev, opened.st_ino, opened.st_size) != (before.st_dev, before.st_ino, before.st_size):
                return None
            data = stream.read(MAX_FILE_BYTES + 1)
        after = path.stat(follow_symlinks=False)
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
            before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns
        ):
            return None
        if len(data) != before.st_size or not _safe_text(data):
            return None
        return data
    except (OSError, ValueError):
        return None


def collect(source: Path, destination: Path, status: Path) -> tuple[int, int, int]:
    """Return copied files, copied bytes, skipped entries; status has counts only."""
    _assert_plain_directory_chain(source.parent)
    _assert_plain_directory_chain(destination)
    _assert_plain_directory_chain(status.parent)
    if not source.exists():
        _write_status(status, "LOG_DIRECTORY_NOT_AVAILABLE\n")
        return (0, 0, 0)
    _assert_plain_directory_chain(source)
    if not source.is_dir() or _is_link_or_junction(source):
        raise ValueError("source must be an ordinary directory")
    if source.resolve() == destination.resolve() or source.resolve() in destination.resolve().parents:
        raise ValueError("destination cannot be inside source")
    _ensure_plain_directory(destination)
    _ensure_plain_directory(status.parent)
    copied = total = skipped = 0
    for root, dirs, files in os.walk(source, topdown=True, followlinks=False):
        base = Path(root)
        relative = base.relative_to(source)
        depth = len(relative.parts)
        kept = []
        for name in sorted(dirs):
            candidate = base / name
            if depth < MAX_DEPTH and _safe_name(name) and not _is_link_or_junction(candidate):
                kept.append(name)
            else:
                skipped += 1
        dirs[:] = kept
        for name in sorted(files):
            path = base / name
            if not _safe_name(name) or path.suffix.casefold() not in EXTENSIONS:
                skipped += 1
                continue
            if copied >= MAX_FILES:
                skipped += 1
                continue
            data = _read_regular_file(path)
            if data is None or total + len(data) > MAX_TOTAL_BYTES:
                skipped += 1
                continue
            target = destination / relative / name
            _ensure_plain_directory(target.parent)
            if _is_link_or_junction(target) or target.exists():
                skipped += 1
                continue
            with target.open("xb") as stream:
                stream.write(data)
            copied += 1
            total += len(data)
    label = "TEXT_EVIDENCE_PARTIAL" if skipped else "TEXT_EVIDENCE_OK"
    _write_status(status, f"{label} files={copied} bytes={total} skipped={skipped}\n")
    return (copied, total, skipped)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    try:
        collect(args.source, args.destination, args.status)
    except (OSError, ValueError):
        try:
            _write_status(args.status, "TEXT_EVIDENCE_FAILED\n")
        except (OSError, ValueError):
            pass  # Never follow an unsafe status path to report an error.
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
