#!/usr/bin/env python3
"""Read-only, fail-closed analysis of pinned QEMU NVMe IRQ trace evidence.

This inspects LOCAL files only; it never launches QEMU or accepts an iOS boot.
A hash match proves file identity, not that the trace was emitted by that file.
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
EVENT_TEXT = {
    "pci_nvme_irq_msix": re.compile(r"raising MSI-X IRQ vector ([0-9]+)\Z"),
    "pci_nvme_irq_pin": re.compile(r"pulsing IRQ pin\Z"),
    "pci_nvme_irq_masked": re.compile(r"IRQ is masked\Z"),
}
TRACE_LINE = re.compile(
    r"^(?P<thread>[0-9]+)@(?P<time>[0-9]+(?:\.[0-9]+)?):"
    r"(?P<event>pci_nvme_irq_(?:msix|pin|masked)) (?P<message>[^\r\n]*)$"
)
UNSUPPORTED_WARNING = "MSI-X is not supported by interrupt controller"
MAX_LOG_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 100000


class InvalidEvidence(ValueError):
    pass


def _bytes(path: Path, limit: int | None = MAX_LOG_BYTES) -> bytes:
    if not path.is_file():
        raise InvalidEvidence(f"missing_file:{path}")
    if limit is not None and path.stat().st_size > limit:
        raise InvalidEvidence(f"file_too_large:{path}")
    return path.read_bytes()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _text(data: bytes, label: str) -> str:
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise InvalidEvidence(f"non_utf8_{label}") from exc


def inspect(binary: Path, expected_sha: str, trace: Path, stderr: Path,
            event_file: Path, source_commit: str, product_commit: str) -> dict:
    if source_commit != PINNED_QEMU or product_commit != BASELINE_MAIN:
        raise InvalidEvidence("source_or_product_commit_mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise InvalidEvidence("invalid_expected_binary_sha256")
    # Hash in chunks so the binary is never loaded into RAM in full.
    if not binary.is_file():
        raise InvalidEvidence("missing_qemu_binary")
    digest = hashlib.sha256()
    with binary.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    binary_sha = digest.hexdigest()
    if binary_sha != expected_sha:
        raise InvalidEvidence("qemu_binary_sha256_mismatch")

    config_data = _bytes(event_file)
    config_lines = [s.strip() for s in _text(config_data, "events").splitlines()]
    enabled: set[str] = set()
    for entry in config_lines:
        if not entry or entry.startswith("#"):
            continue
        if entry.startswith("-"):
            enabled.discard(entry[1:])
        else:
            enabled.add(entry)
    if not set(EVENT_TEXT).issubset(enabled):
        raise InvalidEvidence("required_nvme_trace_events_not_enabled")
    trace_data, stderr_data = _bytes(trace), _bytes(stderr)
    trace_lines = _text(trace_data, "trace").splitlines()
    stderr_lines = _text(stderr_data, "stderr").splitlines()
    counts = {event: 0 for event in EVENT_TEXT}
    vectors: set[int] = set()
    threads: set[int] = set()
    rejected = 0
    for line in trace_lines:
        match = TRACE_LINE.fullmatch(line)
        if not match:
            if "pci_nvme_irq_" in line:
                rejected += 1
            continue
        event = match.group("event")
        detail = EVENT_TEXT[event].fullmatch(match.group("message"))
        if detail is None:
            rejected += 1
            continue
        counts[event] += 1
        threads.add(int(match.group("thread")))
        if event == "pci_nvme_irq_msix":
            vectors.add(int(detail.group(1)))
        if sum(counts.values()) > MAX_EVENTS:
            raise InvalidEvidence("too_many_nvme_trace_events")

    has_msix = counts["pci_nvme_irq_msix"] > 0
    has_pin = counts["pci_nvme_irq_pin"] > 0
    if has_msix and has_pin:
        branch = "BOTH_MSIX_AND_INTX_BRANCHES_OBSERVED"
    elif has_msix:
        branch = "MSIX_BRANCH_OBSERVED"
    elif has_pin:
        branch = "INTX_BRANCH_OBSERVED"
    elif counts["pci_nvme_irq_masked"]:
        branch = "ONLY_MASKED_IRQ_OBSERVED"
    else:
        branch = "NO_NVME_IRQ_EVENT_OBSERVED"

    warnings = sum(UNSUPPORTED_WARNING in s for s in stderr_lines)
    return {
        "schema": "ios-m3-nvme-irq-runtime-evidence-v1",
        "source_commit_declared": source_commit,
        "product_commit_declared": product_commit,
        "qemu_binary_sha256_verified": binary_sha,
        "qemu_binary_size": binary.stat().st_size,
        "trace_log_sha256": _sha(trace_data),
        "stderr_log_sha256": _sha(stderr_data),
        "trace_event_config_sha256": _sha(config_data),
        "trace_backend_required": "log",
        "nvme_irq_event_counts": counts,
        "msix_vectors_observed": sorted(vectors),
        "trace_thread_ids": sorted(threads),
        "rejected_event_like_lines": rejected,
        "unattributed_msix_unsupported_warnings": warnings,
        "irq_branch_observation": branch,
        "msi_nonbroken_runtime_value": "UNKNOWN",
        "msix_init_return_value": "UNKNOWN",
        "msix_capability_guest_enabled": "UNKNOWN",
        "aic_interrupt_delivery_proven": False,
        "guest_nvme_iokit_binding_proven": False,
        "non_ramdisk_guest_disk_proven": False,
        "full_ios_stage1_proven": False,
        "provenance_level": "LOCAL_FILES_HASHED_UNATTESTED_EXECUTION",
        "limitations": [
            "Trace text is not cryptographically bound to the hashed executable.",
            "An IRQ branch trace does not prove delivery to Apple AIC or IOKit binding.",
            "A generic MSI-X unsupported warning is not attributable to NVMe alone.",
            "No trace event is not evidence that MSI-X or NVMe is absent.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--qemu-binary", type=Path, required=True)
    p.add_argument("--expected-binary-sha256", required=True)
    p.add_argument("--trace-log", type=Path, required=True)
    p.add_argument("--stderr-log", type=Path, required=True)
    p.add_argument("--trace-events", type=Path, required=True)
    p.add_argument("--qemu-source-commit", required=True)
    p.add_argument("--product-main-commit", required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    try:
        result = inspect(args.qemu_binary, args.expected_binary_sha256, args.trace_log,
                         args.stderr_log, args.trace_events, args.qemu_source_commit,
                         args.product_main_commit)
    except (InvalidEvidence, OSError) as exc:
        print(json.dumps({"status": "INVALID_EVIDENCE", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 3
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0 if sum(result["nvme_irq_event_counts"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
