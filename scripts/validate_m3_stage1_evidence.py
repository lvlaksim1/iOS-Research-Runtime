#!/usr/bin/env python3
"""Fail-closed Stage 1 evidence *contract* check; never certify a guest boot.

This is an offline structural/cross-record validator. JSON input, even if internally
consistent, cannot authenticate a guest or prove that an OS actually booted.
Stage 1 acceptance therefore remains false until an independent runtime evidence
chain and attestation gate are implemented and verified.
"""

import argparse
import json
import re
from pathlib import Path

SCHEMA = "ios-m3-stage1-evidence-v1"
STAGES = ("pcie_iokit_binding", "nvme_io", "bsd_disk", "apfs", "system_launchd")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DISK = re.compile(r"disk[0-9]+\Z")
BDF = re.compile(r"[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-7]\Z")
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z")


def _keys(obj, required, name, errors):
    if not isinstance(obj, dict) or set(obj) != set(required):
        errors.append(f"{name}: expected exactly {sorted(required)}")
        return False
    return True


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _match(value, pattern):
    return isinstance(value, str) and bool(pattern.fullmatch(value))


def _positive(value):
    return type(value) is int and value > 0


def _record(data, required, label, errors):
    return _keys(data, required, label, errors)


def _validate(bundle):
    """Validate internal contract, without authenticating runtime claims."""
    errors = []
    result = {"schema": "ios-m3-stage1-contract-check-v1", "contract_complete": False,
              "stage1_accepted": False, "status": "NOT_PROVEN", "errors": errors,
              "limitation": "JSON/host QMP and synthetic fixtures cannot authenticate guest runtime; independent capture/attestation and E2E evidence required"}
    if not _keys(bundle, ("schema", "provenance", "host_receipt", "guest"), "bundle", errors):
        return result
    if bundle["schema"] != SCHEMA:
        errors.append("unsupported evidence schema")
    p = bundle["provenance"]
    h = bundle["host_receipt"]
    pk = ("repository", "head_sha", "qemu_sha256", "run_id", "boot_nonce", "serial_sha256", "evidence_kind")
    hk = ("head_sha", "qemu_sha256", "run_id", "boot_nonce", "serial_sha256", "qmp_nvme_present")
    if not _keys(p, pk, "provenance", errors) or not _keys(h, hk, "host_receipt", errors):
        return result
    if p["repository"] != "lvlaksim1/iOS-Research-Runtime" or p["evidence_kind"] != "guest_runtime":
        errors.append("unexpected repository or non-runtime evidence kind")
    if not _match(p["head_sha"], HEX40) or not _match(p["qemu_sha256"], HEX64) or not _match(p["serial_sha256"], HEX64):
        errors.append("invalid source SHA")
    if not _nonempty(p["run_id"]) or not _nonempty(p["boot_nonce"]) or p["run_id"] == p["boot_nonce"]:
        errors.append("invalid run identity")
    for key in ("head_sha", "qemu_sha256", "run_id", "boot_nonce", "serial_sha256"):
        if h[key] != p[key]:
            errors.append(f"host/guest provenance mismatch: {key}")
    if h["qmp_nvme_present"] is not True:
        errors.append("host NVMe PCI receipt absent (not sufficient alone)")
    guest = bundle["guest"]
    if not isinstance(guest, list) or len(guest) != len(STAGES):
        errors.append("five ordered guest stages required")
        return result
    data = {}
    for index, (stage, event) in enumerate(zip(STAGES, guest), start=1):
        ek = ("stage", "sequence", "origin", "run_id", "boot_nonce", "raw_artifact_sha256", "data")
        if not _keys(event, ek, f"guest[{index}]", errors):
            continue
        if event["stage"] != stage or type(event["sequence"]) is not int or event["sequence"] != index:
            errors.append(f"guest[{index}] stage/sequence mismatch")
        if event["origin"] != "guest_runtime" or event["run_id"] != p["run_id"] or event["boot_nonce"] != p["boot_nonce"]:
            errors.append(f"guest[{index}] source/boot mismatch")
        if not _match(event["raw_artifact_sha256"], HEX64):
            errors.append(f"guest[{index}] missing raw artifact digest")
        data[stage] = event["data"]
    if len(data) != len(STAGES):
        return result

    a = data["pcie_iokit_binding"]
    if _record(a, ("provider_class", "controller_class", "bdf", "nvme_bdf", "provider_instance_id", "controller_instance_id", "iokit_attached", "device_tree_only"), "pcie", errors):
        if not all(_nonempty(a[k]) for k in ("provider_class", "controller_class", "provider_instance_id", "controller_instance_id")):
            errors.append("PCIe IOKit instance/class identity missing")
        if a["provider_instance_id"] == a["controller_instance_id"]:
            errors.append("provider and controller must be distinct instances")
        if not _match(a["bdf"], BDF) or a["bdf"] != a["nvme_bdf"]:
            errors.append("PCIe/NVMe BDF lineage mismatch")
        if a["iokit_attached"] is not True or a["device_tree_only"] is not False:
            errors.append("actual IOKit attachment, not ADT-only, required")

    b = data["nvme_io"]
    if _record(b, ("bdf", "controller_instance_id", "namespace_id", "irq_delivered", "io_completed"), "nvme", errors):
        if b["bdf"] != a.get("nvme_bdf") or b["controller_instance_id"] != a.get("controller_instance_id"):
            errors.append("NVMe controller lineage mismatch")
        if not _positive(b["namespace_id"]) or not _positive(b["io_completed"]) or b["irq_delivered"] is not True:
            errors.append("guest NVMe namespace I/O and IRQ not proven")

    c = data["bsd_disk"]
    if _record(c, ("bsd_name", "ramdisk", "backing_kind", "namespace_id", "media_instance_id", "probe_image"), "disk", errors):
        if not _match(c["bsd_name"], DISK) or c["ramdisk"] is not False or c["probe_image"] is not False:
            errors.append("nonramdisk /dev/disk* required, not md0 or empty probe")
        if c["backing_kind"] != "nvme_namespace" or c["namespace_id"] != b.get("namespace_id") or not _nonempty(c["media_instance_id"]):
            errors.append("BSD disk lacks NVMe namespace lineage")

    d = data["apfs"]
    if _record(d, ("physical_store", "container_uuid", "volumes"), "apfs", errors):
        if d["physical_store"] != c.get("bsd_name") or not _match(d["container_uuid"], UUID):
            errors.append("APFS container/physical store mismatch")
        volumes = d["volumes"]
        if not isinstance(volumes, list) or len(volumes) != 3:
            errors.append("APFS requires exactly three mounted volume roles")
        else:
            roles = set()
            ids = set()
            for i, v in enumerate(volumes):
                if not _record(v, ("role", "volume_uuid", "mounted", "physical_store"), f"apfs.volumes[{i}]", errors):
                    continue
                if not _match(v["volume_uuid"], UUID) or v["volume_uuid"] in ids:
                    errors.append("APFS volume UUID invalid or duplicated")
                if v["role"] not in ("SystemOS", "Preboot", "Data") or v["role"] in roles:
                    errors.append("APFS role invalid or duplicated")
                if v["mounted"] is not True or v["physical_store"] != c.get("bsd_name"):
                    errors.append("APFS volume not mounted from NVMe physical store")
                ids.add(v["volume_uuid"])
                roles.add(v["role"])
            if roles != {"SystemOS", "Preboot", "Data"}:
                errors.append("APFS SystemOS/Preboot/Data roles incomplete")

    e = data["system_launchd"]
    if _record(e, ("pid", "executable", "boot_mode", "root_volume_uuid", "data_volume_uuid", "recovery", "core_userland_started"), "launchd", errors):
        vols = d.get("volumes") if isinstance(d, dict) else None
        role_ids = {v.get("role"): v.get("volume_uuid") for v in vols if isinstance(v, dict)} if isinstance(vols, list) else {}
        if type(e["pid"]) is not int or e["pid"] != 1 or e["executable"] != "/sbin/launchd" or e["boot_mode"] != "system":
            errors.append("system launchd PID1 required")
        if e["recovery"] is not False or e["core_userland_started"] is not True:
            errors.append("recovery shell or absent core userland")
        if e["root_volume_uuid"] != role_ids.get("SystemOS") or e["data_volume_uuid"] != role_ids.get("Data"):
            errors.append("launchd volume lineage mismatch")
    result["contract_complete"] = not errors
    return result


def validate(bundle):
    """Reject malformed input without throwing or implying Stage 1 acceptance."""
    try:
        return _validate(bundle)
    except (TypeError, AttributeError, KeyError, ValueError, IndexError):
        return {"schema": "ios-m3-stage1-contract-check-v1", "contract_complete": False,
                "stage1_accepted": False, "status": "NOT_PROVEN",
                "errors": ["malformed evidence structure"],
                "limitation": "No authenticated guest runtime evidence"}


def reject_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--check-contract-only", action="store_true", help="Exit 0 for structural consistency only; NEVER stage1 acceptance")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.evidence.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
        report = validate(document)
    except (OSError, UnicodeError, ValueError) as exc:
        report = {"schema": "ios-m3-stage1-contract-check-v1", "contract_complete": False,
                  "stage1_accepted": False, "status": "NOT_PROVEN", "errors": [type(exc).__name__]}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.check_contract_only and report["contract_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
