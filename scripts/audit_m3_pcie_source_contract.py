#!/usr/bin/env python3
"""Read-only, fail-closed source audit of synthetic M3 PCIe storage prerequisites.

Compares the QEMU GPEX ECAM/MMIO declarations with the synthetic ADT node
emitted by AppleDeviceTreePatcher and records the QEMU command-line intent.
This audit NEVER infers Apple's #ports ABI, IOKit matching, guest NVMe binding,
non-ramdisk disks, APFS mounts, or a completed SystemOS boot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

QEMU_FIELDS = ("ecam_base", "ecam_size", "mmio_base", "mmio_size")


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _source_bytes(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    return raw.decode("utf-8"), git_blob_sha1(raw)


def _bounded_method(source: str, signature: str, next_signature: str) -> str | None:
    start = source.find(signature)
    if start < 0:
        return None
    end = source.find(next_signature, start + len(signature))
    return source[start:end] if end >= 0 else None


def _qemu_windows(source: str) -> dict[str, int] | None:
    found: dict[str, int] = {}
    for m in re.finditer(r"const\s+hwaddr\s+pcie_(ecam|mmio)_(base|size)\s*=\s*(0x[0-9a-fA-F]+)\s*;", source):
        key = m.group(1) + "_" + m.group(2)
        if key in found:
            return None
        found[key] = int(m.group(3), 16)
    return found if set(found) == set(QEMU_FIELDS) else None


def _adt_windows(method: str) -> dict[str, int] | None:
    m = re.search(
        r'pcie\.Properties\["reg"\]\s*=\s*EncodeRegRanges\s*\(\s*'
        r'\(\s*(0x[0-9a-fA-F]+)UL\s*,\s*(0x[0-9a-fA-F]+)UL\s*\)\s*,\s*'
        r'\(\s*(0x[0-9a-fA-F]+)UL\s*,\s*(0x[0-9a-fA-F]+)UL\s*\)\s*\)',
        method,
    )
    if not m:
        return None
    return dict(zip(QEMU_FIELDS, (int(v, 16) for v in m.groups())))


def audit(qemu_patch: str, adt_patcher: str, command_builder: str,
          source_blobs: dict[str, str], expected_blobs: dict[str, str] | None = None) -> dict:
    method = _bounded_method(
        adt_patcher,
        "private static void AddPcieDiscoveryNode(AdtNode armIo)",
        "private static byte[] EncodeRegRanges",
    )
    qemu = _qemu_windows(qemu_patch)
    adt = _adt_windows(method) if method is not None else None
    sha_matches = {
        name: (expected_blobs is None or source_blobs[name] == expected_blobs.get(name))
        for name in ("qemu_patch", "adt_patcher", "command_builder")
    }
    compatible = re.search(r'pcie\.Properties\["compatible"\]\s*=\s*"([^"]+)"', method or "")
    facts = {
        "qemu_gpex_host_declared": 'qdev_new("gpex-pcihost")' in qemu_patch,
        "qemu_gpex_num_irqs_zero": bool(re.search(r'"num-irqs"\s*,\s*0\s*,', qemu_patch)),
        "qemu_windows": qemu,
        "adt_windows": adt,
        "adt_compatible_literal": compatible.group(1) if compatible else None,
        "adt_ports_property_assigned": bool(re.search(r'pcie\.Properties\["#ports"\]', method or "")),
        "adt_explicit_port_children_added": bool(re.search(r'pcie\.Children\.Add\s*\(', method or "")),
        "qemu_root_port_requested": 'pcie-root-port,id=iosm3rp' in command_builder,
        "qemu_nvme_requested": 'nvme,drive=iosm3nvme' in command_builder,
        "qemu_ramdisk_root_requested": 'rd=md0' in command_builder,
    }
    source_valid = all(sha_matches.values())
    complete = (qemu is not None and adt is not None and
                facts["qemu_gpex_host_declared"] and facts["qemu_root_port_requested"] and
                facts["qemu_nvme_requested"])
    if not source_valid:
        classification = "SOURCE_SHA_MISMATCH"
    elif not complete:
        classification = "INSUFFICIENT_STATIC_SOURCE_EVIDENCE"
    elif qemu != adt:
        classification = "HOST_ADT_WINDOW_MISMATCH"
    else:
        classification = "HOST_ADT_WINDOWS_MATCH_PROVIDER_ABI_UNPROVEN"
    return {
        "schema": 1,
        "source_blobs": source_blobs,
        "expected_blobs_match": sha_matches,
        "facts": facts,
        "classification": classification,
        "guest_pcie_provider_bound": False,
        "guest_nvme_bound": False,
        "guest_nonramdisk_disk_proven": False,
        "apfs_system_preboot_data_proven": False,
        "system_launchd_proven": False,
        "stage1_accepted": False,
        "limitations": [
            "Static host/ADT window equality does not establish an Apple IOKit provider ABI.",
            "Presence or absence of #ports assignment is not a decoded Apple #ports contract.",
            "Host QEMU NVMe model and recovery rd=md0 do not prove guest storage enumeration.",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--qemu-patch", type=Path, required=True)
    p.add_argument("--adt-patcher", type=Path, required=True)
    p.add_argument("--command-builder", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected-blobs", type=Path, help="Optional JSON map of expected Git blob SHAs")
    args = p.parse_args()
    paths = {"qemu_patch": args.qemu_patch, "adt_patcher": args.adt_patcher,
             "command_builder": args.command_builder}
    sources = {name: _source_bytes(path) for name, path in paths.items()}
    expected = json.loads(args.expected_blobs.read_text(encoding="utf-8")) if args.expected_blobs else None
    result = audit(*(sources[name][0] for name in paths),
                   {name: sources[name][1] for name in paths}, expected)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["classification"] == "HOST_ADT_WINDOWS_MATCH_PROVIDER_ABI_UNPROVEN" else 2


if __name__ == "__main__":
    raise SystemExit(main())
