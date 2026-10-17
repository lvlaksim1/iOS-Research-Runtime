#!/usr/bin/env python3
"""Build a fail-closed, HOST-ONLY QEMU boot evidence receipt.

This consumes existing BootEvidenceCapture and QMP host observations. It does
not authenticate guest output, PCIe/IOKit binding, APFS, or full-system boot.
No Stage1 acceptance is possible from this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import stat
import time
from pathlib import Path
from typing import Any

_HEX32 = re.compile(r"[0-9a-f]{32}\Z")
_SHA40 = re.compile(r"[0-9a-f]{40}\Z")
_SHA64 = re.compile(r"[0-9a-f]{64}\Z")


def _read_file(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"not a regular non-symlink file: {path.name}")
    return path.read_bytes()


def _sha_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"not a regular non-symlink file: {path.name}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    # JSON object key collisions can silently replace command identity or PCI
    # fields. The host-only receipt must not accept ambiguous evidence bytes.
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON object key")
        obj[key] = value
    return obj


def _reject_nonfinite_json_constant(value: str) -> Any:
    # Python accepts NaN and +/-Infinity by default, although they are not
    # JSON numbers. Even unused evidence metadata must be valid JSON.
    raise ValueError(f"nonstandard JSON numeric constant: {value}")


def _parse_finite_json_float(value: str) -> float:
    # Exponent overflow (e.g. 1e999) becomes inf in Python's default JSON
    # decoder without invoking parse_constant. Reject it in every field,
    # including otherwise ignored host evidence metadata.
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite JSON floating-point number")
    return number


def _json_loads_strict(raw: bytes) -> Any:
    return json.loads(raw, object_pairs_hook=_reject_duplicate_keys,
                      parse_constant=_reject_nonfinite_json_constant,
                      parse_float=_parse_finite_json_float)


def _json_file(path: Path) -> dict[str, Any]:
    obj = _json_loads_strict(_read_file(path))
    if not isinstance(obj, dict):
        raise ValueError(f"not a JSON object: {path.name}")
    return obj


def _candidate(bus: int, device: dict[str, Any]) -> dict[str, Any] | None:
    cls = device.get("class_info")
    value = cls.get("class") if isinstance(cls, dict) else None
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    if value != 0x0108 and value >> 8 != 0x0108:
        return None
    def number(key: str, default: int) -> int:
        x = device.get(key)
        return x if type(x) is int else default
    qdev = device.get("qdev_id")
    return {"Bus": number("bus", bus), "Slot": number("slot", -1),
            "Function": number("function", -1),
            "QdevId": qdev if isinstance(qdev, str) else None}


def _pci_number(value: Any, label: str, maximum: int) -> int:
    # bool is a subclass of int, but it is never a valid QMP PCI address.
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"QMP invalid {label}")
    return value


def _walk(devices: Any, bus: int, result: list[dict[str, Any]],
          seen: set[tuple[int, int, int]], seen_buses: set[int],
          depth: int = 0) -> None:
    if depth > 16:
        raise ValueError("QMP PCI bridge depth exceeded")
    if not isinstance(devices, list):
        raise ValueError("QMP PCI devices must be a list")
    for device in devices:
        if not isinstance(device, dict):
            raise ValueError("QMP PCI device must be an object")
        slot = _pci_number(device.get("slot"), "slot", 31)
        function = _pci_number(device.get("function"), "function", 7)
        device_bus = _pci_number(device.get("bus", bus), "device bus", 255)
        if device_bus != bus:
            raise ValueError("QMP device bus differs from containing bus")
        address = (bus, slot, function)
        if address in seen:
            raise ValueError("QMP duplicate PCI bus/slot/function")
        seen.add(address)
        if "class_info" in device:
            cls = device["class_info"]
            if (not isinstance(cls, dict) or
                    type(cls.get("class")) is not int or
                    not 0 <= cls["class"] <= 0xFFFFFF):
                raise ValueError("QMP invalid PCI class_info")
        if "qdev_id" in device and device["qdev_id"] is not None and not isinstance(device["qdev_id"], str):
            raise ValueError("QMP invalid qdev_id")
        candidate = _candidate(bus, device)
        if candidate is not None:
            result.append(candidate)
        if "pci_bridge" in device:
            bridge = device["pci_bridge"]
            if not isinstance(bridge, dict) or not isinstance(bridge.get("bus"), dict):
                raise ValueError("QMP invalid PCI bridge")
            secondary = _pci_number(bridge["bus"].get("secondary"), "secondary bus", 255)
            # QEMU's PciBridgeInfo.devices is optional. An unconfigured bridge
            # (secondary=0) has no downstream bus and does not expose devices.
            # Do not interpret bus zero as a child alias or invent a child NVMe.
            if secondary == 0:
                if "devices" in bridge:
                    raise ValueError("QMP unconfigured bridge exposes devices")
                continue
            # A configured bridge must not alias an ancestor or sibling bus.
            # A missing devices member is possible if QEMU cannot find that bus.
            if secondary in seen_buses:
                raise ValueError("QMP duplicate or cyclic PCI bus")
            seen_buses.add(secondary)
            if "devices" in bridge:
                _walk(bridge["devices"], secondary, result, seen, seen_buses, depth + 1)


def _classify(raw: bytes, expected_id: str) -> tuple[list[dict[str, Any]], str]:
    obj = _json_loads_strict(raw)
    # QemuRuntime sends query-pci with iosm3-query-pci-<boot_nonce> and
    # preserves the matching raw response. An event, wrong ID, or extra
    # envelope field must never be accepted as that command's response.
    if (not isinstance(obj, dict) or set(obj) != {"id", "return"} or
            type(obj.get("id")) is not str or obj["id"] != expected_id or
            not isinstance(obj.get("return"), list)):
        raise ValueError("QMP raw response is not correlated query-pci success")
    result: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int]] = set()
    seen_buses: set[int] = set()
    for bus in obj["return"]:
        if not isinstance(bus, dict):
            raise ValueError("QMP bus is not an object")
        number = _pci_number(bus.get("bus"), "bus", 255)
        if number in seen_buses:
            raise ValueError("QMP duplicate or cyclic PCI bus")
        seen_buses.add(number)
        _walk(bus.get("devices"), number, result, seen, seen_buses)
    classification = ("HOST_NVME_CLASS_OBSERVED_GUEST_BINDING_UNPROVEN" if result
                      else "NO_HOST_NVME_CLASS_OBSERVED")
    return result, classification


def _same_name(value: Any, path: Path) -> bool:
    return isinstance(value, str) and value == path.name and Path(value).name == value


def build_receipt(*, qemu: Path, serial: Path, stderr: Path, capture: Path,
                  qmp_raw: Path, qmp_evidence: Path, wait_seconds: float = 0) -> dict[str, Any]:
    """Return an explicit receipt. Missing/inconsistent host evidence never passes."""
    reasons: list[str] = []
    receipt: dict[str, Any] = {
        "schema": 1, "source": "HOST_QEMU_CAPTURE_ONLY",
        "host_complete": False, "stage1_accepted": False,
        "guest_nvme_bound": False, "boot_nonce": None, "run_id": None,
        "head_sha": None, "qemu_sha256": None, "serial_sha256": None,
        "stderr_sha256": None, "qmp_raw_sha256": None,
        "qmp_receipt_sha256": None, "host_nvme_candidates": [],
        "classification": "HOST_EVIDENCE_INCOMPLETE", "errors": reasons,
    }
    for label, path in (("qemu", qemu), ("serial", serial), ("stderr", stderr)):
        try:
            receipt[label + "_sha256"] = _sha_file(path)
        except (OSError, ValueError) as exc:
            reasons.append(f"{label}: {type(exc).__name__}")

    try:
        meta = _json_file(capture)
        nonce, run_id, head = meta.get("boot_nonce"), meta.get("run_id"), meta.get("head_sha")
        if not isinstance(nonce, str) or not _HEX32.fullmatch(nonce):
            reasons.append("capture: invalid boot_nonce")
        else:
            receipt["boot_nonce"] = nonce
        if not isinstance(run_id, str) or not run_id.strip():
            reasons.append("capture: missing run_id")
        else:
            receipt["run_id"] = run_id
        if not isinstance(head, str) or not _SHA40.fullmatch(head):
            reasons.append("capture: invalid head_sha")
        else:
            receipt["head_sha"] = head
        if (type(meta.get("schema")) is not int or meta["schema"] != 1 or
                meta.get("stage1_accepted") is not False):
            reasons.append("capture: unexpected schema or stage1 flag")
        if not _same_name(meta.get("serial_file"), serial) or not _same_name(meta.get("stderr_file"), stderr):
            reasons.append("capture: stream file name mismatch")
        recorded = meta.get("serial_sha256")
        if not isinstance(recorded, str) or not _SHA64.fullmatch(recorded) or recorded != receipt["serial_sha256"]:
            reasons.append("capture: serial SHA256 mismatch")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"capture: {type(exc).__name__}")

    # The C# QMP task writes its evidence JSON after writing/flushing raw JSON.
    # Waiting for that file is a bounded observational barrier, NOT proof the
    # task itself has completed. A future C# integration must await the Task.
    deadline = time.monotonic() + max(0, wait_seconds)
    while not qmp_evidence.exists() and time.monotonic() < deadline:
        time.sleep(min(0.1, max(0, deadline - time.monotonic())))
    try:
        qmp = _json_file(qmp_evidence)
        raw = _read_file(qmp_raw)
        receipt["qmp_raw_sha256"] = hashlib.sha256(raw).hexdigest()
        receipt["qmp_receipt_sha256"] = _sha_file(qmp_evidence)
        if receipt["boot_nonce"] is None:
            raise ValueError("QMP query ID cannot be correlated without boot_nonce")
        candidates, classification = _classify(
            raw, "iosm3-query-pci-" + receipt["boot_nonce"])
        if (type(qmp.get("schema")) is not int or qmp["schema"] != 1 or
                qmp.get("source") != "QMP_QUERY_PCI_HOST_ONLY"):
            reasons.append("qmp: unexpected schema or source")
        if qmp.get("boot_nonce") != receipt["boot_nonce"] or receipt["boot_nonce"] is None:
            reasons.append("qmp: boot_nonce mismatch")
        if qmp.get("run_id") != receipt["run_id"] or receipt["run_id"] is None:
            reasons.append("qmp: run_id mismatch")
        if qmp.get("head_sha") != receipt["head_sha"] or receipt["head_sha"] is None:
            reasons.append("qmp: head_sha mismatch")
        if not _same_name(qmp.get("raw_reply_file"), qmp_raw):
            reasons.append("qmp: raw_reply_file mismatch")
        if qmp.get("guest_nvme_bound") is not False or qmp.get("stage1_accepted") is not False:
            reasons.append("qmp: guest/Stage1 flags must be false")
        if qmp.get("valid_query_pci_reply") is not True:
            reasons.append("qmp: valid_query_pci_reply not true")
        if qmp.get("host_nvme_candidates") != candidates or qmp.get("classification") != classification:
            reasons.append("qmp: classification differs from raw PCI topology")
        receipt["host_nvme_candidates"] = candidates
        receipt["classification"] = classification
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"qmp: {type(exc).__name__}")

    receipt["host_complete"] = not reasons
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("qemu", "serial", "stderr", "capture", "qmp-raw", "qmp-evidence", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--wait-seconds", type=float, default=0)
    args = parser.parse_args(argv)
    if not 0 <= args.wait_seconds <= 30:
        parser.error("--wait-seconds must be between 0 and 30")
    result = build_receipt(qemu=args.qemu, serial=args.serial, stderr=args.stderr,
                           capture=args.capture, qmp_raw=args.qmp_raw,
                           qmp_evidence=args.qmp_evidence, wait_seconds=args.wait_seconds)
    if args.output.is_symlink() or args.output.exists():
        parser.error("output must not exist (immutable receipt)")
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return 0 if result["host_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
