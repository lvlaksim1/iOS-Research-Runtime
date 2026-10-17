#!/usr/bin/env python3
"""Repair the ioprint executable bit in an iOS CLI tools tar archive.

Offline archive operation only: this does not install, run, or attest to
execution of ioprint in an iOS guest. Designed for the Windows repack step
where host File.Copy can produce a tar member with mode 0666.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tarfile
import tempfile
from pathlib import Path
from typing import Any

ENTRY = "sysroot/usr/local/bin/ioprint"
REQUIRED_MODE = 0o755


def _canonical_path(name: str) -> str:
    while name.startswith("./"):
        name = name[2:]
    return name


def _digest(stream: Any) -> str:
    h = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        h.update(chunk)
    return h.hexdigest()


def _member_signature(archive: tarfile.TarFile) -> list[tuple[Any, ...]]:
    signatures: list[tuple[Any, ...]] = []
    for member in archive.getmembers():
        content_hash = None
        if member.isfile():
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"unreadable regular entry: {member.name!r}")
            with stream:
                content_hash = _digest(stream)
        signatures.append((member.name, member.type, member.mode & 0o7777,
                           member.size, member.uid, member.gid, member.uname,
                           member.gname, member.mtime, member.linkname,
                           tuple(sorted(member.pax_headers.items())), content_hash))
    return signatures


def repair_archive(archive_path: Path) -> dict[str, Any]:
    """Atomically rewrite tar metadata, with readback and full-member audit.

    Fail closed if the target is missing/ambiguous/nonregular. The original
    archive is not replaced unless all member content and metadata read back
    unchanged except the target's executable mode.
    """
    archive_path = Path(archive_path)
    temp_path: Path | None = None
    try:
        with tarfile.open(archive_path, "r:*") as source:
            members = source.getmembers()
            matches = [i for i, m in enumerate(members) if _canonical_path(m.name) == ENTRY]
            if len(matches) != 1:
                return {"status": "ENTRY_COUNT_INVALID", "count": len(matches), "entry": ENTRY}
            target_index = matches[0]
            target = members[target_index]
            if not target.isfile():
                return {"status": "ENTRY_NOT_REGULAR_FILE", "entry": ENTRY}
            original_mode = target.mode & 0o7777
            if original_mode == REQUIRED_MODE:
                return {"status": "ALREADY_CORRECT", "entry": ENTRY, "mode": "0755"}
            before = _member_signature(source)
            compressed = archive_path.name.endswith((".tar.gz", ".tgz"))
            if not compressed and not archive_path.name.endswith(".tar"):
                return {"status": "UNSUPPORTED_ARCHIVE_EXTENSION", "entry": ENTRY}
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".m3-ioprint-", suffix=".tmp",
                dir=archive_path.parent, delete=False
            ) as temporary:
                temp_path = Path(temporary.name)
            with tarfile.open(temp_path, "w:gz" if compressed else "w:") as output:
                for i, member in enumerate(members):
                    updated = copy.deepcopy(member)
                    if i == target_index:
                        updated.mode = REQUIRED_MODE
                        # Prevent a conflicting pax mode override.
                        updated.pax_headers.pop("SCHILY.mode", None)
                    if member.isfile():
                        content = source.extractfile(member)
                        if content is None:
                            raise ValueError(f"unreadable regular entry: {member.name!r}")
                        with content:
                            output.addfile(updated, content)
                    else:
                        output.addfile(updated)
        with tarfile.open(temp_path, "r:*") as rewritten:
            after = _member_signature(rewritten)
        if len(before) != len(after):
            raise ValueError("member count changed")
        for i, (old, new) in enumerate(zip(before, after)):
            if i == target_index:
                expected = list(old)
                expected[2] = REQUIRED_MODE
                # If the source contained a SCHILY.mode pax extension,
                # its removal is intentional; compare the remainder.
                expected[10] = tuple((k, v) for k, v in old[10] if k != "SCHILY.mode")
                if tuple(expected) != new:
                    raise ValueError("target content or metadata changed unexpectedly")
            elif old != new:
                raise ValueError(f"non-target member changed at index {i}")
        with tarfile.open(temp_path, "r:*") as verified:
            final_matches = [m for m in verified.getmembers() if _canonical_path(m.name) == ENTRY]
            if len(final_matches) != 1 or not final_matches[0].isfile() or (final_matches[0].mode & 0o7777) != REQUIRED_MODE:
                raise ValueError("target mode readback failed")
        os.replace(temp_path, archive_path)
        temp_path = None
        return {"status": "ARCHIVE_EXEC_MODE_REPAIRED", "entry": ENTRY,
                "previous_mode": f"{original_mode:04o}", "mode": "0755",
                "scope": "tar_metadata_and_content_readback_only"}
    except (OSError, EOFError, tarfile.TarError, ValueError) as exc:
        return {"status": "REPAIR_FAILED", "entry": ENTRY,
                "reason": type(exc).__name__, "detail": str(exc)[:180]}
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Repacked .tar/.tar.gz/.tgz archive")
    args = parser.parse_args(argv)
    result = repair_archive(args.archive)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] in ("ARCHIVE_EXEC_MODE_REPAIRED", "ALREADY_CORRECT") else 2


if __name__ == "__main__":
    raise SystemExit(main())
