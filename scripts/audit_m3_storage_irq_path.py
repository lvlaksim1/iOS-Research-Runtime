#!/usr/bin/env python3
"""Conservative source-only PCIe/NVMe interrupt-path prerequisite audit.

Reads exact source snapshots, not guest logs. Never asserts IOKit binding,
NVMe functionality, APFS mounting, or a full-system iOS boot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

# Git blob IDs from source read at the indicated immutable commits.
EXPECTED_BLOBS = {
    "upstream_darwin": "51d240b112907e9bd2ef4d9be836a1a04a865db5",
    "upstream_gpex": "e66784ce516e60a98db2ae3ddd6ed4b6ddd14599",
    "gpex_patch": "2163f92f4266b6fd64dff4cdb8aef4b5442d2cb3",
    "adt_patcher": "eb3d6168e370ba91c609fc25c2709e3ba0dc2676",
    "command_builder": "023ef24eba4a3c96aa53caf0e69142864a308451",
}
PINNED_QEMU_SHA = "2867d847d3471560e773120ee50c42dbcbb6d60b"
BASELINE_MAIN_SHA = "50fff7ab8fc33fa1324ea204416f7a773a191033"
MAX_SOURCE_BYTES = 2 * 1024 * 1024


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def strip_comments(text: str) -> str:
    """Remove comments without stripping C string literals used by this audit."""
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)


def function_body(text: str, name: str) -> str | None:
    """Locate one C function definition by name and balanced braces."""
    clean = strip_comments(text)
    matches = list(re.finditer(r"\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{", clean))
    if len(matches) != 1:
        return None
    begin = matches[0].end()
    depth = 1
    for i in range(begin, len(clean)):
        if clean[i] == "{":
            depth += 1
        elif clean[i] == "}":
            depth -= 1
            if depth == 0:
                return clean[begin:i]
    return None


def audit_sources(sources: dict[str, str]) -> dict:
    missing = sorted(set(EXPECTED_BLOBS) - set(sources))
    if missing:
        raise ValueError("missing source inputs: " + ", ".join(missing))
    upstream = sources["upstream_darwin"]
    gpex = sources["upstream_gpex"]
    patch = sources["gpex_patch"]
    adt = sources["adt_patcher"]
    cmd = sources["command_builder"]
    aic = function_body(upstream, "init_aic")
    gpex_realize = function_body(gpex, "gpex_host_realize")
    gpex_swizzle = function_body(gpex, "gpex_swizzle_map_irq_fn")
    # Patch lines are explicitly '+' prefixed. Only added lines count.
    additions = "\n".join(line[1:] for line in patch.splitlines()
                          if line.startswith("+") and not line.startswith("+++"))
    additions = strip_comments(additions)
    adt_method_start = adt.find("private static void AddPcieDiscoveryNode(")
    adt_method_end = adt.find("private static byte[] EncodeRegRanges(", adt_method_start)
    adt_method = adt[adt_method_start:adt_method_end] if adt_method_start >= 0 and adt_method_end > adt_method_start else ""

    facts = {
        "upstream_aic_function_found": aic is not None,
        "upstream_aic_registers_allocated_zeroed": bool(aic and 'alloc_zeroed("aic"' in aic),
        "upstream_aic_no_irq_delivery_calls": bool(aic and not re.search(
            r"\b(?:sysbus_connect_irq|qdev_connect_gpio_out|qemu_set_irq|qemu_irq_raise|qemu_irq_pulse)\s*\(", aic)),
        "gpex_root_bus_registered": bool(gpex_realize and 'pci_register_root_bus(dev, "pcie.0"' in gpex_realize),
        "gpex_intx_swizzle_modulo_nirq": bool(gpex_swizzle and re.search(r"%\s*bus->nirq\b", gpex_swizzle)),
        "gpex_intx_sysbus_irq_exposed": bool(gpex_realize and "sysbus_init_irq(sbd" in gpex_realize),
        "gpex_patch_instantiates_host": 'qdev_new("gpex-pcihost")' in additions,
        "gpex_patch_num_irqs_zero": bool(re.search(r'object_property_set_int\s*\(\s*OBJECT\(pcie\)\s*,\s*"num-irqs"\s*,\s*0\s*,', additions)),
        "gpex_patch_has_irq_connection_call": bool(re.search(r"\b(?:sysbus_connect_irq|qdev_connect_gpio_out|qemu_irq_intercept_in)\s*\(", additions)),
        "adt_msi_parent_advertised": 'pcie.Properties["msi-parent-controller"]' in adt_method,
        "adt_msi_vectors_advertised": 'pcie.Properties["#msi-vectors"]' in adt_method,
        "qemu_nvme_endpoint_requested": '"nvme,drive=iosm3nvme' in cmd,
        "qemu_pcie_root_port_requested": '"pcie-root-port,id=iosm3rp' in cmd,
    }
    observations = []
    if not facts["upstream_aic_function_found"]:
        observations.append("AIC_FUNCTION_NOT_LOCATED_IN_PINNED_SOURCE")
    elif facts["upstream_aic_registers_allocated_zeroed"] and facts["upstream_aic_no_irq_delivery_calls"]:
        observations.append("PINNED_AIC_IS_REGISTER_STUB_NO_IRQ_DELIVERY_OBSERVED")
    if facts["gpex_patch_num_irqs_zero"]:
        observations.append("GPEX_INTX_COUNT_ZERO_IN_INSPECTED_PATCH")
        if facts["gpex_intx_swizzle_modulo_nirq"]:
            observations.append("POTENTIAL_INTX_SWIZZLE_ZERO_NIRQ_HAZARD_IF_INVOKED")
    if facts["gpex_patch_instantiates_host"] and not facts["gpex_patch_has_irq_connection_call"]:
        observations.append("NO_GPEX_IRQ_CONNECTION_CALL_IN_INSPECTED_PATCH")
    if facts["adt_msi_parent_advertised"] and facts["adt_msi_vectors_advertised"]:
        observations.append("ADT_MSI_ADVERTISEMENT_NOT_EQUIVALENT_TO_IRQ_DELIVERY")
    if not (facts["qemu_nvme_endpoint_requested"] and facts["qemu_pcie_root_port_requested"]):
        observations.append("NVME_OR_ROOT_PORT_CLI_INTENT_NOT_FOUND")
    source_blockers = (not facts["upstream_aic_function_found"] or
                       (facts["upstream_aic_registers_allocated_zeroed"] and facts["upstream_aic_no_irq_delivery_calls"]) or
                       facts["gpex_patch_num_irqs_zero"] or
                       (facts["gpex_patch_instantiates_host"] and not facts["gpex_patch_has_irq_connection_call"]))
    return {
        "schema": "ios-m3-storage-irq-source-audit-v1",
        "source_pins": {"qemu_commit": PINNED_QEMU_SHA, "application_commit": BASELINE_MAIN_SHA},
        "facts": facts,
        "observations": observations,
        "classification": "IRQ_DELIVERY_PREREQUISITE_NOT_ESTABLISHED" if source_blockers else "SOURCE_ONLY_IRQ_DELIVERY_NOT_VERIFIED",
        "source_only": True,
        "guest_nvme_bound": False,
        "non_ramdisk_disk_proven": False,
        "apfs_system_volumes_mounted": False,
        "system_launchd_proven": False,
        "stage1_full_ios_boot_accepted": False,
    }


def read_pinned_sources(paths: dict[str, Path]) -> dict[str, str]:
    result = {}
    for key, expected in EXPECTED_BLOBS.items():
        path = paths[key]
        if path.stat().st_size > MAX_SOURCE_BYTES:
            raise ValueError(f"{key}: source exceeds byte limit")
        raw = path.read_bytes()
        actual = git_blob_sha1(raw)
        if actual != expected:
            raise ValueError(f"{key}: git blob mismatch expected={expected} actual={actual}")
        result[key] = raw.decode("utf-8", errors="strict")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in EXPECTED_BLOBS:
        parser.add_argument("--" + key.replace("_", "-"), required=True, type=Path)
    args = parser.parse_args()
    paths = {k: getattr(args, k) for k in EXPECTED_BLOBS}
    try:
        report = audit_sources(read_pinned_sources(paths))
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({"classification": "SOURCE_EVIDENCE_INVALID", "reason": str(exc),
                          "stage1_full_ios_boot_accepted": False}, sort_keys=True))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
