#!/usr/bin/env python3
"""Capture bounded raw native Apple ADT PCIe properties as text evidence.

This is a read-only evidence tool, not a PCIe port mapper. It imports the
published ADT parser without modifying the separately pending diagnostic patch.
It does not change the guest DeviceTree or assert that iOS booted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from inspect_adt_pcie import AdtFormatError, parse_adt

MAX_CAPTURED_NODES = 128
MAX_PROPERTY_BYTES = 4096
BRIDGE_PATTERN = re.compile(r"pci-bridge[0-9]+\Z")
ROOT_KEYS = frozenset({
    "#ports", "compatible", "reg", "ranges", "interrupts", "interrupt-parent",
    "interrupt-map", "msi-parent", "msi-parent-controller", "msi-vector-base",
    "#msi-vectors", "iommu-parent", "phandle", "AAPL,phandle",
})
PORT_KEYS = ROOT_KEYS | frozenset({
    "apcie-port", "AAPL,unit-string", "apcie-piodma", "iommu-parent-pcie0",
    "iommu-parent-pcie1", "iommu-parent-pcie2",
})


def _node_name(node: dict) -> str:
    return node["properties"].get("name", b"").split(b"\x00", 1)[0].decode(
        "utf-8", errors="replace"
    )


def _raw_properties(node: dict, keys: frozenset[str]) -> dict:
    result = {}
    for name, value in sorted(node["properties"].items()):
        if name not in keys:
            continue
        if len(value) > MAX_PROPERTY_BYTES:
            raise AdtFormatError(f"selected property {name!r} exceeds evidence limit")
        result[name] = {"size_bytes": len(value), "raw_hex": value.hex()}
    return result


def capture_native_apcie(data: bytes) -> dict:
    """Return exact selected bytes; never infer a QEMU-to-Apple port mapping."""
    root = parse_adt(data)
    matches = []
    examined = 0

    def walk(node: dict, parent: str) -> None:
        nonlocal examined
        examined += 1
        if examined > 100_000:
            raise AdtFormatError("ADT evidence traversal limit exceeded")
        name = _node_name(node)
        path = f"{parent}/{name}" if parent else f"/{name}"
        if name == "apcie" and b"apcie" in node["properties"].get("compatible", b"").lower():
            matches.append((path, node))
        for child in node["children"]:
            walk(child, path)

    walk(root, "")
    if len(matches) != 1:
        raise AdtFormatError(f"expected one native apcie node, found {len(matches)}")
    path, apcie = matches[0]
    bridge_nodes = []
    for bridge in apcie["children"]:
        name = _node_name(bridge)
        if not BRIDGE_PATTERN.fullmatch(name):
            continue
        bridge_path = f"{path}/{name}"
        descendants = []

        def capture_descendants(node: dict, parent: str, depth: int) -> None:
            if depth > 2:
                return
            for child in node["children"]:
                child_path = f"{parent}/{_node_name(child)}"
                props = _raw_properties(child, PORT_KEYS)
                if props:
                    descendants.append({"path": child_path, "properties": props})
                    if len(descendants) > MAX_CAPTURED_NODES:
                        raise AdtFormatError("too many relevant bridge descendants")
                capture_descendants(child, child_path, depth + 1)

        capture_descendants(bridge, bridge_path, 1)
        bridge_nodes.append({
            "path": bridge_path,
            "properties": _raw_properties(bridge, PORT_KEYS),
            "child_names": [_node_name(child) for child in bridge["children"]],
            "descendants": descendants,
        })
        if len(bridge_nodes) > MAX_CAPTURED_NODES:
            raise AdtFormatError("too many native apcie bridge nodes")
    raw_ports = apcie["properties"].get("#ports")
    return {
        "schema": 1,
        "source": "exact_native_adt_bytes",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "input_size_bytes": len(data),
        "apcie_path": path,
        "apcie_properties": _raw_properties(apcie, ROOT_KEYS),
        "apcie_ports_u32_le": struct.unpack("<I", raw_ports)[0]
            if raw_ports is not None and len(raw_ports) == 4 else None,
        "bridge_nodes": bridge_nodes,
        "qemu_root_port_to_apple_ports_mapping": "UNPROVEN",
        "guest_iokit_binding": "UNPROVEN",
        "stage1_accepted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = capture_native_apcie(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
