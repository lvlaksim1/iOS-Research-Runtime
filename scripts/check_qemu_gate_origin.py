#!/usr/bin/env python3
"""Fail-closed host-side check of a QEMU gate-job origin receipt.

The gate job reports its own identity and runtime hash. Matching those values
against the consumer's expected run and the actual executable is useful, but
is NOT cryptographic attestation or evidence of guest PCIe/NVMe/APFS boot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from pathlib import Path

UPSTREAM_PIN = "2867d847d3471560e773120ee50c42dbcbb6d60b"
KEYS = ("GATE_RUN_ID", "GATE_SHA", "QEMU_UPSTREAM_SHA", "QEMU_RUNTIME_SHA256")
RUN_ID = re.compile(r"[1-9][0-9]{0,18}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
MAX_RUN_ID = 9223372036854775807
MAX_RECEIPT_BYTES = 512
MAX_BINARY_BYTES = 512 * 1024 * 1024


def _identity(run_id: str, sha: str) -> None:
    if not isinstance(run_id, str) or RUN_ID.fullmatch(run_id) is None or int(run_id) > MAX_RUN_ID:
        raise ValueError("invalid expected gate run id")
    if not isinstance(sha, str) or COMMIT.fullmatch(sha) is None:
        raise ValueError("invalid expected gate commit")


def _ordinary_file(path: Path, *, limit: int) -> int:
    # Reject links and non-regular files without following the last component.
    # Ancestor reparse-point rejection is handled by the consuming workflow.
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size <= 0 or metadata.st_size > limit:
        raise ValueError("missing, linked, empty or oversized gate evidence")
    return metadata.st_size


def _parse_receipt(path: Path) -> dict[str, str]:
    size = _ordinary_file(path, limit=MAX_RECEIPT_BYTES)
    with path.open("rb") as stream:
        raw = stream.read(MAX_RECEIPT_BYTES + 1)
    if len(raw) != size or b"\x00" in raw or b"\r" in raw:
        raise ValueError("gate receipt bytes invalid")
    try:
        data = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("gate receipt must be ASCII") from exc
    lines = data.splitlines()
    if len(lines) != len(KEYS) or not data.endswith("\n"):
        raise ValueError("gate receipt key count or terminator invalid")
    fields = {}
    for key, line in zip(KEYS, lines):
        prefix = key + "="
        if not line.startswith(prefix):
            raise ValueError("gate receipt has reordered or unknown key")
        fields[key] = line[len(prefix):]
    return fields


def verify(receipt: Path, binary: Path, *, expected_run_id: str, expected_sha: str) -> dict:
    _identity(expected_run_id, expected_sha)
    fields = _parse_receipt(receipt)
    run_id = fields["GATE_RUN_ID"]
    if RUN_ID.fullmatch(run_id) is None or int(run_id) > MAX_RUN_ID or run_id != expected_run_id:
        raise ValueError("gate job run id mismatch")
    if COMMIT.fullmatch(fields["GATE_SHA"]) is None or fields["GATE_SHA"] != expected_sha:
        raise ValueError("gate job commit mismatch")
    if fields["QEMU_UPSTREAM_SHA"] != UPSTREAM_PIN:
        raise ValueError("gate upstream pin mismatch")
    expected_digest = fields["QEMU_RUNTIME_SHA256"]
    if DIGEST.fullmatch(expected_digest) is None:
        raise ValueError("invalid gate runtime digest")
    size = _ordinary_file(binary, limit=MAX_BINARY_BYTES)
    digest = hashlib.sha256()
    read_bytes = 0
    with binary.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            read_bytes += len(block)
            if read_bytes > MAX_BINARY_BYTES:
                raise ValueError("gate binary grew beyond bound")
    if read_bytes != size or digest.hexdigest() != expected_digest:
        raise ValueError("gate executable differs from producer receipt")
    return {
        "schema": 1,
        "purpose": "host_only_qemu_gate_origin_check",
        "gate_run_id": run_id,
        "gate_sha": expected_sha,
        "qemu_upstream_sha": UPSTREAM_PIN,
        "qemu_runtime_sha256": expected_digest,
        "qemu_runtime_size_bytes": read_bytes,
        "gate_job_attestation": "SELF_REPORTED_HASH_MATCHED_NOT_CRYPTOGRAPHICALLY_ATTESTED",
        "guest_iokit_binding": "UNPROVEN",
        "stage1_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--expected-run-id", required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.receipt, args.binary, expected_run_id=args.expected_run_id,
                        expected_sha=args.expected_sha)
        if args.output.is_symlink() or args.output.exists():
            raise ValueError("output already exists or is a link")
        # Exclusive creation; no partial evidence on failed validation.
        with args.output.open("xb") as stream:
            stream.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode("ascii"))
    except (OSError, ValueError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
