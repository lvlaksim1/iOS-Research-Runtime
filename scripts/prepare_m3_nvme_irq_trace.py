#!/usr/bin/env python3
"""Prepare an opt-in, non-executing QEMU NVMe IRQ trace launch plan.

This tool only writes an exact event selection file and an immutable JSON plan.
It does not start QEMU, prove that trace was enabled, or accept an iOS boot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PINNED_QEMU = "2867d847d3471560e773120ee50c42dbcbb6d60b"
BASELINE_MAIN = "50fff7ab8fc33fa1324ea204416f7a773a191033"
EVENTS = ("pci_nvme_irq_msix", "pci_nvme_irq_pin", "pci_nvme_irq_masked")
EVENT_FILE_BYTES = ("\n".join(EVENTS) + "\n").encode("ascii")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MAX_BINARY_BYTES = 1024 * 1024 * 1024  # bounded read, not a QEMU size assertion


class InvalidPreparation(ValueError):
    pass


def _sha256_file(path: Path) -> tuple[str, int]:
    if not path.is_file():
        raise InvalidPreparation("qemu_binary_missing_or_not_regular_file")
    size = path.stat().st_size
    if size == 0 or size > MAX_BINARY_BYTES:
        raise InvalidPreparation("qemu_binary_empty_or_exceeds_bounded_hash_limit")
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest(), size


def _checked_path(value: Path, label: str) -> Path:
    # QEMU's key-value -trace argument uses comma separators. Reject ambiguous
    # paths instead of escaping with unverified command-line semantics.
    path = value.expanduser().resolve(strict=False)
    if any(character in str(path) for character in (",", "\r", "\n", "\x00")):
        raise InvalidPreparation(f"unsafe_{label}_path")
    return path


def _write_immutable(path: Path, data: bytes, label: str) -> str:
    if path.exists():
        if not path.is_file() or path.read_bytes() != data:
            raise InvalidPreparation(f"existing_{label}_conflicts")
        return "REUSED_EXACT"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as target:
            target.write(data)
            target.flush()
    except FileExistsError as exc:
        # Unknown concurrent writer: never overwrite or assume its contents.
        raise InvalidPreparation(f"concurrent_{label}_creation") from exc
    return "CREATED"


def prepare(*, qemu_binary: Path, expected_binary_sha256: str,
            qemu_source_commit: str, product_main_commit: str,
            trace_events: Path, stderr_log: Path, output_plan: Path) -> dict:
    if qemu_source_commit != PINNED_QEMU or product_main_commit != BASELINE_MAIN:
        raise InvalidPreparation("source_or_product_commit_mismatch")
    if SHA256.fullmatch(expected_binary_sha256) is None:
        raise InvalidPreparation("invalid_expected_binary_sha256")
    binary = _checked_path(qemu_binary, "qemu_binary")
    event_file = _checked_path(trace_events, "trace_events")
    stderr = _checked_path(stderr_log, "stderr_log")
    plan_file = _checked_path(output_plan, "output_plan")
    if len({str(binary), str(event_file), str(stderr), str(plan_file)}) != 4:
        raise InvalidPreparation("paths_must_be_distinct")
    actual_sha, binary_size = _sha256_file(binary)
    if actual_sha != expected_binary_sha256:
        raise InvalidPreparation("qemu_binary_sha256_mismatch")
    if event_file.exists() and (not event_file.is_file() or event_file.read_bytes() != EVENT_FILE_BYTES):
        raise InvalidPreparation("existing_trace_events_conflicts")
    plan = {
        "schema": "ios-m3-nvme-irq-trace-launch-plan-v1",
        "source_commit": qemu_source_commit,
        "product_main_commit": product_main_commit,
        "qemu_binary": str(binary),
        "qemu_binary_sha256_verified": actual_sha,
        "qemu_binary_size": binary_size,
        "trace_event_file": str(event_file),
        "trace_event_file_sha256": hashlib.sha256(EVENT_FILE_BYTES).hexdigest(),
        "qemu_trace_arguments": ["-trace", f"events={event_file}"],
        "expected_trace_backend": "log",
        "trace_backend_runtime_verified": False,
        "stderr_capture_path": str(stderr),
        "trace_and_stderr_same_stream": True,
        "analyzer_command": [
            "python", "scripts/inspect_m3_nvme_irq_runtime.py",
            "--qemu-binary", str(binary),
            "--expected-binary-sha256", actual_sha,
            "--trace-log", str(stderr),
            "--stderr-log", str(stderr),
            "--trace-events", str(event_file),
            "--qemu-source-commit", PINNED_QEMU,
            "--product-main-commit", BASELINE_MAIN,
        ],
        "plan_only_no_qemu_execution": True,
        "guest_nvme_iokit_binding_proven": False,
        "aic_interrupt_delivery_proven": False,
        "non_ramdisk_disk_proven": False,
        "full_ios_stage1_proven": False,
        "limitations": [
            "The caller must append qemu_trace_arguments as separate argv elements.",
            "The QEMU log backend emits trace lines on stderr, not a separate trace file.",
            "The caller must independently verify the actual QEMU build trace backend.",
            "A prepared plan does not prove that QEMU ran or enabled trace events.",
            "An observed IRQ branch is not proof of Apple AIC delivery or iOS boot.",
        ],
    }
    data = (json.dumps(plan, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if plan_file.exists() and (not plan_file.is_file() or plan_file.read_bytes() != data):
        raise InvalidPreparation("existing_output_plan_conflicts")
    event_state = _write_immutable(event_file, EVENT_FILE_BYTES, "trace_events")
    plan_state = _write_immutable(plan_file, data, "output_plan")
    return {"status": "PLAN_PREPARED_NOT_EXECUTED", "trace_events": event_state,
            "plan": plan_state, "plan_path": str(plan_file), "plan_sha256": hashlib.sha256(data).hexdigest()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu-binary", required=True, type=Path)
    parser.add_argument("--expected-binary-sha256", required=True)
    parser.add_argument("--qemu-source-commit", required=True)
    parser.add_argument("--product-main-commit", required=True)
    parser.add_argument("--trace-events", required=True, type=Path)
    parser.add_argument("--stderr-log", required=True, type=Path)
    parser.add_argument("--output-plan", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = prepare(**vars(args))
    except (InvalidPreparation, OSError) as exc:
        print(json.dumps({"status": "INVALID_PREPARATION", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 3
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
