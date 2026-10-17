#!/usr/bin/env python3
"""Fail-closed, offline audit of the iOS M3 ioprint archive entry mode.

This is an archive preflight only. A passing result is NOT evidence that
launchd started, that ioprint executed, or that iOS booted successfully.
"""

from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path
from typing import Any

ENTRY = "sysroot/usr/local/bin/ioprint"
REQUIRED_MODE = 0o755


def _canonical_member_path(name: str) -> str:
    # GNU tar may prefix member names with './'. Do not accept arbitrary
    # path normalization: '..', absolute paths and backslashes are unsafe.
    while name.startswith("./"):
        name = name[2:]
    return name


def audit_archive(archive: Path) -> dict[str, Any]:
    """Inspect metadata only; never extract or execute archive contents."""
    try:
        with tarfile.open(archive, mode="r:*") as stream:
            matches = [
                member for member in stream
                if _canonical_member_path(member.name) == ENTRY
            ]
    except (OSError, EOFError, tarfile.TarError) as exc:
        return {
            "status": "ARCHIVE_UNREADABLE",
            "reason": type(exc).__name__,
            "entry": ENTRY,
        }

    if len(matches) != 1:
        return {
            "status": "ENTRY_COUNT_INVALID",
            "count": len(matches),
            "entry": ENTRY,
        }

    member = matches[0]
    if not member.isfile():
        return {
            "status": "ENTRY_NOT_REGULAR_FILE",
            "entry": ENTRY,
            "member_type": member.type.decode("ascii", errors="replace")
            if isinstance(member.type, bytes) else str(member.type),
        }

    mode = member.mode & 0o7777
    if mode != REQUIRED_MODE:
        return {
            "status": "EXEC_MODE_INVALID",
            "entry": ENTRY,
            "observed_mode": f"{mode:04o}",
            "required_mode": f"{REQUIRED_MODE:04o}",
        }

    return {
        "status": "ARCHIVE_EXEC_MODE_PASS",
        "entry": ENTRY,
        "observed_mode": f"{mode:04o}",
        "required_mode": f"{REQUIRED_MODE:04o}",
        "scope": "tar_metadata_only_no_guest_runtime_claim",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Repacked .tar or .tar.gz archive")
    args = parser.parse_args(argv)
    result = audit_archive(args.archive)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "ARCHIVE_EXEC_MODE_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
