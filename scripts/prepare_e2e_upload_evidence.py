#!/usr/bin/env python3
"""Build a bounded, content-minimized CI upload from local E2E evidence.

Never publish raw integration logs, QEMU listings, ADT properties, or boot logs.
This is a host-side evidence summary; it cannot prove guest Stage1 boot.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path

from collect_text_evidence import (
    _assert_plain_directory_chain,
    _ensure_plain_directory,
    _is_link_or_junction,
    _read_regular_file,
)

INPUT_NAMES = (
    "integration.log",
    "runtime-summary.txt",
    "standalone-machine-list.txt",
    "native-apcie-properties.json",
    "native-apcie-capture-status.txt",
    "text-evidence-copy-status.txt",
    "revisions.txt",
    "qemu-gate-origin-check.json",
    "qemu-gate-staged-origin-check.json",
)
CAPTURE_STATES = frozenset({"CAPTURE_OK_TEXT_ONLY", "CAPTURE_FAILED", "RAW_ADT_NOT_AVAILABLE"})
TEXT_STATES = frozenset({"TEXT_EVIDENCE_FAILED", "LOG_DIRECTORY_NOT_AVAILABLE"})
TEXT_COUNTER = re.compile(r"TEXT_EVIDENCE_(OK|PARTIAL) files=([0-9]+) bytes=([0-9]+) skipped=([0-9]+)\Z")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_NATIVE_JSON = 65536
MAX_STATUS_BYTES = 256
MAX_OUTPUT_BYTES = 8192
MAX_REVISIONS_BYTES = 512
MAX_GATE_CHECK_JSON = 2048
MAX_GATE_RUNTIME_BYTES = 512 * 1024 * 1024
HEX_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
RUN_ID = re.compile(r"[1-9][0-9]{0,18}\Z")
QEMU_UPSTREAM_PIN = "2867d847d3471560e773120ee50c42dbcbb6d60b"
REVISION_KEYS = (
    "QEMU_GATE_RUN", "QEMU_GATE_SHA", "APPLICATION_SHA",
    "QEMU_GATE_MODE", "QEMU_UPSTREAM_SHA",
)


def _regular_metadata(path: Path) -> int | None:
    """Return ordinary-file size without following links or reparse points."""
    if _is_link_or_junction(path):
        raise ValueError("linked evidence input")
    try:
        meta = path.stat(follow_symlinks=False)
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(meta.st_mode):
        raise ValueError("non-regular evidence input")
    return meta.st_size


def _bounded_text(path: Path, limit: int) -> str | None:
    size = _regular_metadata(path)
    if size is None:
        return None
    if size > limit:
        raise ValueError("evidence input exceeds size limit")
    data = _read_regular_file(path)
    if data is None or len(data) != size:
        raise ValueError("evidence input changed or is not valid UTF-8 text")
    return data.decode("utf-8-sig").strip()


def _status(path: Path, kind: str) -> str:
    value = _bounded_text(path, MAX_STATUS_BYTES)
    if value is None:
        return "NOT_AVAILABLE"
    if kind == "capture":
        if value not in CAPTURE_STATES:
            raise ValueError("unexpected native capture status")
        return value
    if value in TEXT_STATES:
        return value
    match = TEXT_COUNTER.fullmatch(value)
    if match is None:
        raise ValueError("unexpected text evidence status")
    counts = tuple(int(part) for part in match.groups()[1:])
    if counts[0] > 64 or counts[1] > 4194304 or counts[2] > 100000:
        raise ValueError("text evidence counters out of range")
    return value


def _native_summary(path: Path, capture_status: str) -> dict | None:
    value = _bounded_text(path, MAX_NATIVE_JSON)
    if value is None:
        if capture_status == "CAPTURE_OK_TEXT_ONLY":
            raise ValueError("successful native capture lacks properties")
        return None
    if capture_status != "CAPTURE_OK_TEXT_ONLY":
        raise ValueError("native properties present without successful capture")
    def reject_duplicate_keys(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate native JSON key")
            result[key] = item
        return result

    try:
        data = json.loads(
            value,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=lambda _v: (_ for _ in ()).throw(ValueError("nonfinite")),
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid native JSON") from exc
    if not isinstance(data, dict) or set(data) != {
        "schema", "source", "input_sha256", "input_size_bytes", "apcie_path",
        "apcie_properties", "apcie_ports_u32_le", "bridge_nodes",
        "qemu_root_port_to_apple_ports_mapping", "guest_iokit_binding", "stage1_accepted",
    }:
        raise ValueError("unexpected native evidence schema")
    if type(data["schema"]) is not int or data["schema"] != 1 or data["source"] != "exact_native_adt_bytes":
        raise ValueError("unrecognized native evidence")
    if not isinstance(data["input_sha256"], str) or not HEX_SHA256.fullmatch(data["input_sha256"]):
        raise ValueError("invalid ADT digest")
    if type(data["input_size_bytes"]) is not int or not 0 < data["input_size_bytes"] <= 4294967295:
        raise ValueError("invalid ADT size")
    ports = data["apcie_ports_u32_le"]
    if ports is not None and (type(ports) is not int or not 0 <= ports <= 4294967295):
        raise ValueError("invalid native #ports")
    if not isinstance(data["bridge_nodes"], list) or len(data["bridge_nodes"]) > 128:
        raise ValueError("invalid bridge count")
    if not isinstance(data["apcie_properties"], dict) or not isinstance(data["apcie_path"], str):
        raise ValueError("invalid native evidence structure")
    if (data["qemu_root_port_to_apple_ports_mapping"] != "UNPROVEN"
        or data["guest_iokit_binding"] != "UNPROVEN" or data["stage1_accepted"] is not False):
        raise ValueError("native capture falsely asserts guest boot")
    return {
        "input_sha256": data["input_sha256"],
        "input_size_bytes": data["input_size_bytes"],
        "apcie_ports_u32_le": ports,
        "bridge_count": len(data["bridge_nodes"]),
        "qemu_root_port_to_apple_ports_mapping": "UNPROVEN",
        "guest_iokit_binding": "UNPROVEN",
        "stage1_accepted": False,
    }


def _validate_expected_identity(expected_run_id: str | None, expected_sha: str | None) -> None:
    """Require a bounded caller-supplied run identity even without a receipt."""
    if (not isinstance(expected_run_id, str)
        or RUN_ID.fullmatch(expected_run_id) is None
        or int(expected_run_id) > 9223372036854775807):
        raise ValueError("missing or invalid expected workflow run id")
    if not isinstance(expected_sha, str) or HEX_COMMIT.fullmatch(expected_sha) is None:
        raise ValueError("missing or invalid expected workflow commit")


def _tested_revisions(path: Path, expected_run_id: str | None, expected_sha: str | None) -> dict | None:
    """Accept only same-run, exact-SHA, bounded revision provenance."""
    _validate_expected_identity(expected_run_id, expected_sha)
    value = _bounded_text(path, MAX_REVISIONS_BYTES)
    if value is None:
        return None  # Earlier failure may leave no revision receipt; never infer one.
    lines = value.splitlines()
    if len(lines) != len(REVISION_KEYS):
        raise ValueError("unexpected tested revisions count")
    fields = {}
    for key, line in zip(REVISION_KEYS, lines):
        prefix = key + "="
        if not line.startswith(prefix):
            raise ValueError("unexpected or reordered tested revision key")
        fields[key] = line[len(prefix):]
    run_id = fields["QEMU_GATE_RUN"]
    if RUN_ID.fullmatch(run_id) is None or int(run_id) > 9223372036854775807:
        raise ValueError("invalid gate run id")
    if run_id != expected_run_id:
        raise ValueError("gate run id differs from this workflow run")
    for key in ("QEMU_GATE_SHA", "APPLICATION_SHA", "QEMU_UPSTREAM_SHA"):
        if HEX_COMMIT.fullmatch(fields[key]) is None:
            raise ValueError("invalid revision SHA")
    if fields["QEMU_GATE_SHA"] != expected_sha or fields["APPLICATION_SHA"] != expected_sha:
        raise ValueError("gate/application SHA differs from this workflow")
    if fields["QEMU_GATE_MODE"] != "SAME_RUN_REUSABLE_WORKFLOW":
        raise ValueError("unexpected gate mode")
    if fields["QEMU_UPSTREAM_SHA"] != QEMU_UPSTREAM_PIN:
        raise ValueError("unexpected QEMU upstream revision")
    return {
        "qemu_gate_run_id": run_id,
        "qemu_gate_sha": fields["QEMU_GATE_SHA"],
        "application_sha": fields["APPLICATION_SHA"],
        "qemu_gate_mode": fields["QEMU_GATE_MODE"],
        "qemu_upstream_sha": fields["QEMU_UPSTREAM_SHA"],
        # The workflow currently echoes its own run id and SHA into the
        # receipt; equality does not independently attest the QEMU gate.
        "qemu_gate_attestation": "SELF_REPORTED_UNVERIFIED",
    }



def _gate_check(path: Path, expected_run_id: str, expected_sha: str) -> dict | None:
    """Validate only a bounded, exact-schema host-side QEMU check receipt."""
    value = _bounded_text(path, MAX_GATE_CHECK_JSON)
    if value is None:
        return None

    def unique_object(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate QEMU gate check key")
            result[key] = item
        return result

    try:
        data = json.loads(
            value,
            object_pairs_hook=unique_object,
            parse_constant=lambda _v: (_ for _ in ()).throw(ValueError("nonfinite")),
        )
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid QEMU gate check JSON") from exc
    if not isinstance(data, dict) or set(data) != {
        "schema", "purpose", "gate_run_id", "gate_sha", "qemu_upstream_sha",
        "qemu_runtime_sha256", "qemu_runtime_size_bytes", "gate_job_attestation",
        "guest_iokit_binding", "stage1_accepted",
    }:
        raise ValueError("unexpected QEMU gate check schema")
    if type(data["schema"]) is not int or data["schema"] != 1:
        raise ValueError("unrecognized QEMU gate check version")
    if data["purpose"] != "host_only_qemu_gate_origin_check":
        raise ValueError("unexpected QEMU gate check purpose")
    if data["gate_run_id"] != expected_run_id or data["gate_sha"] != expected_sha:
        raise ValueError("QEMU gate check does not match workflow identity")
    if data["qemu_upstream_sha"] != QEMU_UPSTREAM_PIN:
        raise ValueError("QEMU gate check upstream differs from pin")
    if (not isinstance(data["qemu_runtime_sha256"], str)
        or HEX_SHA256.fullmatch(data["qemu_runtime_sha256"]) is None):
        raise ValueError("invalid QEMU gate runtime digest")
    size = data["qemu_runtime_size_bytes"]
    if type(size) is not int or not 0 < size <= MAX_GATE_RUNTIME_BYTES:
        raise ValueError("invalid QEMU gate runtime size")
    if (data["gate_job_attestation"] != "SELF_REPORTED_HASH_MATCHED_NOT_CRYPTOGRAPHICALLY_ATTESTED"
        or data["guest_iokit_binding"] != "UNPROVEN"
        or data["stage1_accepted"] is not False):
        raise ValueError("QEMU gate check falsely claims attestation or guest boot")
    return {
        "gate_run_id": expected_run_id,
        "gate_sha": expected_sha,
        "qemu_upstream_sha": QEMU_UPSTREAM_PIN,
        "qemu_runtime_sha256": data["qemu_runtime_sha256"],
        "qemu_runtime_size_bytes": size,
    }


def _gate_origin_summary(source: Path, expected_run_id: str, expected_sha: str,
                         tested_revisions: dict | None) -> dict:
    downloaded = _gate_check(source / "qemu-gate-origin-check.json", expected_run_id, expected_sha)
    staged = _gate_check(source / "qemu-gate-staged-origin-check.json", expected_run_id, expected_sha)
    if staged is not None and downloaded is None:
        raise ValueError("staged QEMU check without downloaded check")
    if downloaded is not None:
        if tested_revisions is None:
            raise ValueError("QEMU gate check without matching tested revisions")
        if (tested_revisions["qemu_gate_run_id"] != expected_run_id
            or tested_revisions["qemu_gate_sha"] != expected_sha
            or tested_revisions["qemu_upstream_sha"] != QEMU_UPSTREAM_PIN):
            raise ValueError("QEMU gate check and revisions disagree")
    if staged is not None and staged != downloaded:
        raise ValueError("staged QEMU runtime differs from downloaded runtime")
    return {
        "status": ("HOST_ONLY_TWO_STAGE_HASH_MATCHED" if staged is not None else
                   "HOST_ONLY_PRE_STAGE_ONLY" if downloaded is not None else "NOT_AVAILABLE"),
        "qemu_runtime_sha256": downloaded["qemu_runtime_sha256"] if downloaded else None,
        "qemu_runtime_size_bytes": downloaded["qemu_runtime_size_bytes"] if downloaded else None,
        "gate_job_attestation": "SELF_REPORTED_NOT_CRYPTOGRAPHICALLY_ATTESTED" if downloaded else "NOT_AVAILABLE",
        "guest_iokit_binding": "UNPROVEN",
        "stage1_accepted": False,
    }


def prepare(source: Path, destination: Path, *, expected_run_id: str | None = None, expected_sha: str | None = None) -> dict:
    """Create fixed-name, bounded derived files; reject unsafe path components."""
    _validate_expected_identity(expected_run_id, expected_sha)
    _assert_plain_directory_chain(source.parent)
    _assert_plain_directory_chain(destination)
    if _is_link_or_junction(source):
        raise ValueError("evidence source is a link or reparse point")
    if source.exists():
        _assert_plain_directory_chain(source)
        if not source.is_dir() or _is_link_or_junction(source):
            raise ValueError("evidence source is not an ordinary directory")
    if source.resolve() == destination.resolve() or source.resolve() in destination.resolve().parents:
        raise ValueError("upload destination must not be inside evidence source")
    _ensure_plain_directory(destination)
    sizes = {name: _regular_metadata(source / name) for name in INPUT_NAMES}
    capture_status = _status(source / "native-apcie-capture-status.txt", "capture")
    text_status = _status(source / "text-evidence-copy-status.txt", "text")
    native = _native_summary(source / "native-apcie-properties.json", capture_status)
    tested_revisions = _tested_revisions(source / "revisions.txt", expected_run_id, expected_sha)
    gate_origin = _gate_origin_summary(source, expected_run_id, expected_sha, tested_revisions)
    summary = {
        "schema": 1,
        "purpose": "host_only_e2e_evidence_summary",
        "capture_status": capture_status,
        "text_evidence_status": text_status,
        "input_presence_and_sizes": {name: {"present": sizes[name] is not None, "size_bytes": sizes[name]} for name in INPUT_NAMES},
        "native_apcie": native,
        "tested_revisions": tested_revisions,
        "qemu_gate_origin": gate_origin,
        "guest_iokit_binding": "UNPROVEN",
        "stage1_accepted": False,
        "raw_logs_uploaded": False,
        "raw_native_properties_uploaded": False,
    }
    content = (json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    inventory = "".join(f"{name}\t{sizes[name]}\n" for name in INPUT_NAMES if sizes[name] is not None).encode("ascii")
    if len(content) > MAX_OUTPUT_BYTES or len(inventory) > MAX_OUTPUT_BYTES:
        raise ValueError("derived evidence exceeds output limit")
    # No input content is copied. Only two deterministic, fixed-name outputs.
    for name, data in (("evidence-summary.json", content), ("evidence-files.txt", inventory)):
        target = destination / name
        if _is_link_or_junction(target) or target.exists():
            raise ValueError("upload destination already contains output")
        with target.open("xb") as stream:
            stream.write(data)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--expected-run-id", required=True)
    parser.add_argument("--expected-sha", required=True)
    args = parser.parse_args()
    try:
        prepare(args.source, args.destination, expected_run_id=args.expected_run_id, expected_sha=args.expected_sha)
    except (OSError, ValueError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
