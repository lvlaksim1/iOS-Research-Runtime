#!/usr/bin/env python3
"""Read-only, bounded QEMU GPEX ECAM/wiring evidence classifier.

This examines text logs only. QEMU stderr markers are not proof of a guest
IOKit match, NVMe driver binding, an APFS mount, or full iOS boot. The caller
must separately establish that the input came from the pinned runtime.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ECAM_BASE = 0x3F000000
ECAM_SIZE = 0x01000000
MMIO_BASE = 0x10000000
MAX_PRINTED_ACCESSES = 128
MAX_LOG_BYTES = 16 * 1024 * 1024
SOURCE_BLOBS = {
    "gpex_window_patch_0006": "2163f92f4266b6fd64dff4cdb8aef4b5442d2cb3",
    "ecam_trace_patch_0017": "74578450191264ec9079874b0eecabc5a8511664",
    "wiring_trace_patch_0018": "e9bde4f642f631cba4598539b29ebc9b5327b97b",
}

# Require full, raw QEMU diagnostic lines, not quoted snippets or command echoes.
ECAM_LINE = re.compile(
    r"^\[ios-m3-pcie-ecam\] op=(read|write) addr=0x([0-9a-fA-F]+) "
    r"len=([0-9]+) device=(present|absent)$"
)
WIRING_LINE = re.compile(
    r"^\[ios-m3-pcie-wiring\] ecam=0x([0-9a-fA-F]+) "
    r"mmio=0x([0-9a-fA-F]+) host=([a-zA-Z0-9_-]+)$"
)


def _bdf_from_relative_ecam(offset: int) -> dict[str, int | str]:
    bus = offset >> 20
    device = (offset >> 15) & 0x1F
    function = (offset >> 12) & 7
    register = offset & 0xFFF
    return {
        "bus": bus,
        "device": device,
        "function": function,
        "register": register,
        "bdf": f"{bus:02x}:{device:02x}.{function}",
    }


def analyze(lines: list[str]) -> dict:
    """Classify source markers without asserting guest-origin or driver binding."""
    records: list[dict] = []
    wiring: list[dict] = []
    errors: list[dict] = []
    for line_number, raw in enumerate(lines, 1):
        line = raw.rstrip("\r\n")
        if line.startswith("[ios-m3-pcie-ecam]"):
            m = ECAM_LINE.fullmatch(line)
            if not m:
                errors.append({"line": line_number, "reason": "MALFORMED_ECAM_MARKER"})
                continue
            op, addr_hex, length_str, device_state = m.groups()
            addr, length = int(addr_hex, 16), int(length_str)
            if addr >= ECAM_SIZE or length not in (1, 2, 4, 8):
                errors.append({"line": line_number, "reason": "ECAM_RANGE_OR_WIDTH_INVALID"})
                continue
            decoded = _bdf_from_relative_ecam(addr)
            if decoded["register"] + length > 4096:
                errors.append({"line": line_number, "reason": "FUNCTION_BOUNDARY_CROSSING"})
                continue
            records.append({
                "line": line_number, "operation": op,
                "ecam_relative_offset": addr, "length": length,
                "qemu_device_lookup": device_state, **decoded,
            })
        elif line.startswith("[ios-m3-pcie-wiring]"):
            m = WIRING_LINE.fullmatch(line)
            if not m:
                errors.append({"line": line_number, "reason": "MALFORMED_WIRING_MARKER"})
                continue
            ecam, mmio, host = int(m[1], 16), int(m[2], 16), m[3]
            matches = ecam == ECAM_BASE and mmio == MMIO_BASE and host == "gpex-pcihost"
            wiring.append({"line": line_number, "ecam_base": ecam,
                           "mmio_base": mmio, "host": host,
                           "matches_pinned_source": matches})
            if not matches:
                errors.append({"line": line_number, "reason": "WIRING_CONTRACT_MISMATCH"})

    if len(records) > MAX_PRINTED_ACCESSES:
        errors.append({"line": None, "reason": "MORE_THAN_128_ECAM_MARKERS"})
    if len(wiring) > 1:
        errors.append({"line": None, "reason": "MULTIPLE_WIRING_MARKERS_UNSEGMENTED_LOG"})

    lookup_counts = Counter(r["qemu_device_lookup"] for r in records)
    operation_counts = Counter(r["operation"] for r in records)
    observed_bdfs = sorted({r["bdf"] for r in records})
    present_bdfs = sorted({r["bdf"] for r in records if r["qemu_device_lookup"] == "present"})
    if errors:
        classification = "INVALID_OR_MIXED_DIAGNOSTIC_LOG"
    elif records and wiring:
        classification = "HOST_ECAM_HANDLER_ACTIVITY_WITH_WIRING_MARKER"
    elif records:
        classification = "HOST_ECAM_HANDLER_ACTIVITY_WIRING_UNVERIFIED"
    elif wiring:
        classification = "WIRING_MARKER_ONLY_NO_ECAM_ACTIVITY_OBSERVED"
    else:
        classification = "NO_RECOGNIZED_QEMU_PCIE_DIAGNOSTICS"

    return {
        "schema": "ios-m3-ecam-evidence-v1",
        "classification": classification,
        "source_contract_git_blobs": SOURCE_BLOBS,
        "pinned_ecam_base": ECAM_BASE,
        "pinned_ecam_size": ECAM_SIZE,
        "pinned_mmio_base": MMIO_BASE,
        "ecam_addresses_are_relative_offsets": True,
        "wiring_marker_count": len(wiring),
        "wiring_markers": wiring,
        "ecam_access_count": len(records),
        "ecam_accesses": records,
        "operation_counts": dict(operation_counts),
        "qemu_lookup_counts": dict(lookup_counts),
        "observed_bdfs": observed_bdfs,
        "qemu_present_bdfs": present_bdfs,
        "errors": errors,
        "evidence_scope": "QEMU host memory-region handler and wiring text only",
        "input_log_runtime_provenance_verified": False,
        "guest_origin_verified": False,
        "apple_iokit_provider_bound": False,
        "guest_nvme_bound": False,
        "guest_nonramdisk_disk_proven": False,
        "apfs_system_preboot_data_mounted": False,
        "system_launchd_core_userland_proven": False,
        "stage1_full_ios_boot_accepted": False,
        "interpretation": (
            "device=present denotes QEMU PCI config lookup only, not NVMe identity "
            "or guest driver matching; ECAM offset is not guest physical address. "
            "Absence of a bounded marker does not prove no access."
        ),
    }


def analyze_file(path: Path) -> dict:
    if path.stat().st_size > MAX_LOG_BYTES:
        raise ValueError("LOG_EXCEEDS_16_MIB_LIMIT")
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        return analyze(stream.readlines())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze_file(args.log)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
