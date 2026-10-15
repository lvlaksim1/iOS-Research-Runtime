#!/usr/bin/env python3
"""Conservative, read-only classifier for IOS-M3 recovery provider-probe logs.

Source contract: tools/IOSResearchRuntime.Integration/Program.cs at
50fff7ab8fc33fa1324ea204416f7a773a191033 (blob
1b0071cf1378d8006d4c0cfeb5c2634a117119a3).

The harness uses recovery rd=md0 and can print BOOT_PROOF_OK after a recovery
root shell. Neither that marker nor a textual IORegistry class occurrence
establishes PCIe provider binding, guest NVMe, APFS SystemOS, or system launchd.
This tool NEVER makes a Stage1 acceptance decision and never changes the guest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

BEGIN = "__IOS_M3_PROVIDER_PROBE_BEGIN__"
END = "__IOS_M3_PROVIDER_PROBE_END__"
IOPRINT_UNAVAILABLE = "__IOS_M3_IOPRINT_UNAVAILABLE__"
CLASSES_ABSENT = "__IOS_M3_PCIE_NVME_CLASSES_ABSENT__"
IOPRINT_DT = "__IOS_M3_IOPRINT_DEVICETREE__"
IOPRINT_SERVICE = "__IOS_M3_IOPRINT_IOSERVICE__"
IOPRINT_CLASSES = "__IOS_M3_IOPRINT_PCIE_NVME_CLASSES__"
CLASS_NAMES = ("AppleT8140PCIe", "AppleT8140PCIePort", "IOPCIHostBridgeData", "AppleNVMe")
PANIC_RE = re.compile(r"(?:lookupDTProperty.{0,150}#ports|#ports.{0,150}ApplePCIEDTHelpers)", re.I)


def _exact_marker(line: str) -> str:
    """Only an exact shell-output marker qualifies, not a printed command."""
    return line.strip()


def analyze(data: bytes) -> dict:
    lines = data.decode("utf-8", errors="replace").splitlines()
    first_panic = next(((i + 1, line[:250]) for i, line in enumerate(lines)
                        if PANIC_RE.search(line)), None)
    starts = [i for i, line in enumerate(lines) if _exact_marker(line) == BEGIN]
    latest_start = starts[-1] if starts else None
    end_index = None
    if latest_start is not None:
        end_index = next((i for i in range(latest_start + 1, len(lines))
                          if _exact_marker(lines[i]) == END), None)
    probe = lines[latest_start + 1:end_index] if end_index is not None else []
    markers = {_exact_marker(line) for line in probe}
    absent = CLASSES_ABSENT in markers
    unavailable = IOPRINT_UNAVAILABLE in markers
    # A line in a shell command, echo, or marker is not class evidence.
    class_section = IOPRINT_CLASSES in markers
    candidates: set[str] = set()
    if class_section and not unavailable and not absent:
        marker_idx = next(i for i, line in enumerate(probe)
                          if _exact_marker(line) == IOPRINT_CLASSES)
        for line in probe[marker_idx + 1:]:
            stripped = line.strip()
            if (not stripped or stripped.startswith("__IOS_")
                    or stripped.startswith("echo ") or "grep -E" in stripped
                    or "if [" in stripped or stripped.startswith("bash-")):
                continue
            for cls in CLASS_NAMES:
                if re.search(r"(?<![A-Za-z0-9_])" + re.escape(cls) + r"(?![A-Za-z0-9_])", stripped):
                    candidates.add(cls)
    if latest_start is None:
        probe_state = "NOT_OBSERVED"
    elif end_index is None:
        probe_state = "INCOMPLETE"
    elif unavailable:
        probe_state = "IOPRINT_UNAVAILABLE"
    elif absent:
        probe_state = "CLASSES_ABSENT_MARKER"
    elif candidates:
        probe_state = "CLASS_NAMES_IN_TEXT_ONLY"
    else:
        probe_state = "COMPLETE_WITHOUT_CLASS_EVIDENCE"
    if first_panic is not None:
        earliest_blocker = "GUEST_PCIE_ADT_MISSING_PORTS_PANIC"
    elif probe_state in ("NOT_OBSERVED", "INCOMPLETE"):
        earliest_blocker = "PROVIDER_PROBE_NOT_COMPLETED"
    elif unavailable:
        earliest_blocker = "IOPRINT_UNAVAILABLE"
    elif absent:
        earliest_blocker = "NO_PCIE_NVME_CLASSES_OBSERVED"
    else:
        earliest_blocker = "GUEST_PCIE_NVME_BINDING_UNPROVEN"
    return {
        "schema": 1,
        "source": "read_only_guest_console_or_integration_log",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "input_size_bytes": len(data),
        "probe_begin_count": len(starts),
        "probe_state": probe_state,
        "probe_begin_line": latest_start + 1 if latest_start is not None else None,
        "probe_end_line": end_index + 1 if end_index is not None else None,
        "ioprint_devicetree_section": IOPRINT_DT in markers,
        "ioprint_ioservice_section": IOPRINT_SERVICE in markers,
        "ioprint_class_section": class_section,
        "candidate_class_names_text_only": sorted(candidates),
        "missing_ports_panic": {"line": first_panic[0], "excerpt": first_panic[1]}
            if first_panic else None,
        "recovery_root_shell_marker_seen": any("BOOT_PROOF_OK" in line for line in lines),
        "earliest_blocker": earliest_blocker,
        "qemu_root_port_to_apple_ports_mapping": "UNPROVEN",
        "guest_pcie_provider_binding": "UNPROVEN",
        "guest_nvme_bound_device": "UNPROVEN",
        "guest_nonramdisk_disk": "UNPROVEN",
        "apfs_system_preboot_data": "UNPROVEN",
        "system_launchd": "UNPROVEN",
        "stage1_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.input.read_bytes())
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
