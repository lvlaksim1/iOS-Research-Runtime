#!/usr/bin/env python3
"""Read-only Apple DeviceTree PCIe topology evidence extractor.

The ADT wire layout matches the pinned AppleDeviceTreePatcher parser: each node
starts with little-endian u32 property/child counts; properties have 32-byte
names, a u32 length with an optional high flag, and 4-byte-aligned data.

No Apple PCIe port mapping is inferred from QEMU root-port configuration.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

MAX_DEPTH = 64
MAX_NODES = 100_000
MAX_PROPERTIES_PER_NODE = 10_000
MAX_CHILDREN_PER_NODE = 10_000


class AdtFormatError(ValueError):
    pass


def _name(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("utf-8", errors="replace")


def parse_adt(data: bytes) -> dict:
    """Parse a complete ADT without changing its bytes or interpreting PCIe ABI."""
    offset = 0
    nodes = 0

    def read(count: int) -> bytes:
        nonlocal offset
        if count < 0 or offset + count > len(data):
            raise AdtFormatError(f"truncated ADT at offset {offset}, need {count} bytes")
        result = data[offset:offset + count]
        offset += count
        return result

    def node(depth: int) -> dict:
        nonlocal nodes
        if depth > MAX_DEPTH or nodes >= MAX_NODES:
            raise AdtFormatError("ADT depth/node limit exceeded")
        nodes += 1
        property_count, child_count = struct.unpack("<II", read(8))
        if property_count > MAX_PROPERTIES_PER_NODE or child_count > MAX_CHILDREN_PER_NODE:
            raise AdtFormatError("ADT property/child count limit exceeded")
        properties = {}
        for _ in range(property_count):
            header = read(36)
            name = _name(header[:32])
            length = struct.unpack_from("<I", header, 32)[0] & 0x7fffffff
            padded = (length + 3) & ~3
            raw = read(padded)[:length]
            if name in properties:
                raise AdtFormatError(f"duplicate property {name!r}")
            properties[name] = raw
        children = [node(depth + 1) for _ in range(child_count)]
        return {"properties": properties, "children": children}

    root = node(0)
    if offset != len(data):
        raise AdtFormatError(f"trailing ADT bytes: {len(data) - offset}")
    return root


def _decode_u32(raw: bytes | None) -> int | None:
    return struct.unpack("<I", raw)[0] if raw is not None and len(raw) == 4 else None


def _candidate(name: str, compatible: bytes) -> bool:
    return "pcie" in name.lower() or b"apcie" in compatible.lower()


def inspect_pcie(data: bytes) -> dict:
    root = parse_adt(data)
    findings: list[dict] = []

    def walk(node: dict, parent: str) -> None:
        props = node["properties"]
        name = _name(props.get("name", b""))
        path = f"{parent}/{name}" if parent else f"/{name}"
        compatible = props.get("compatible", b"")
        if _candidate(name, compatible):
            raw_ports = props.get("#ports")
            findings.append({
                "path": path,
                "compatible_hex": compatible.hex(),
                "ports_present": raw_ports is not None,
                "ports_length": len(raw_ports) if raw_ports is not None else None,
                "ports_raw_hex": raw_ports.hex() if raw_ports is not None else None,
                "ports_u32_le": _decode_u32(raw_ports),
                "children": [_name(c["properties"].get("name", b"")) for c in node["children"]],
                "properties": {key: {"length": len(value), "hex": value.hex()}
                               for key, value in sorted(props.items())
                               if key in ("#ports", "reg", "ranges", "bus-range", "interrupt-map", "interrupt-parent")},
            })
        for child in node["children"]:
            walk(child, path)

    walk(root, "")
    return {
        "schema": 1,
        "source": "read_only_native_adt_bytes",
        "pcie_nodes": findings,
        "qemu_root_port_to_apple_ports_mapping": "UNPROVEN",
        "stage1_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Exact native ADT binary")
    parser.add_argument("--output", type=Path, required=True, help="JSON evidence destination")
    args = parser.parse_args()
    data = args.input.read_bytes()
    evidence = inspect_pcie(data)
    evidence["input_size_bytes"] = len(data)
    import hashlib
    evidence["input_sha256"] = hashlib.sha256(data).hexdigest()
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
