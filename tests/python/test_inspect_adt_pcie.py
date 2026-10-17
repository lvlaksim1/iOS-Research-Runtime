"""Bounded synthetic ADT fixtures: these do not prove actual guest binding."""
from __future__ import annotations

import importlib.util
import struct
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "scripts" / "inspect_adt_pcie.py"
spec = importlib.util.spec_from_file_location("inspect_adt_pcie", MODULE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def adt_node(properties: dict[str, bytes], children: list[bytes] | None = None) -> bytes:
    children = children or []
    data = bytearray(struct.pack("<II", len(properties), len(children)))
    for name, value in properties.items():
        name_bytes = name.encode("ascii")
        assert len(name_bytes) < 32
        data.extend(name_bytes.ljust(32, b"\x00"))
        data.extend(struct.pack("<I", len(value)))
        data.extend(value)
        data.extend(b"\x00" * ((-len(value)) % 4))
    return bytes(data) + b"".join(children)


class PcieAdtEvidenceTests(unittest.TestCase):
    def test_native_and_synthetic_are_not_equated(self):
        native = adt_node({"name": b"apcie\0", "compatible": b"apcie,t8140\0", "#ports": struct.pack("<I", 3)},
                          [adt_node({"name": b"port0\0"})])
        synthetic = adt_node({"name": b"pcie\0", "compatible": b"apcie,t8140\0"})
        tree = adt_node({"name": b"device-tree\0"}, [adt_node({"name": b"arm-io\0"}, [native, synthetic])])
        evidence = module.inspect_pcie(tree)
        self.assertEqual(len(evidence["pcie_nodes"]), 2)
        self.assertEqual(evidence["pcie_nodes"][0]["ports_u32_le"], 3)
        self.assertEqual(evidence["pcie_nodes"][0]["children"], ["port0"])
        self.assertFalse(evidence["pcie_nodes"][1]["ports_present"])
        self.assertIsNone(evidence["pcie_nodes"][1]["ports_u32_le"])
        self.assertEqual(evidence["qemu_root_port_to_apple_ports_mapping"], "UNPROVEN")
        self.assertFalse(evidence["stage1_accepted"])

    def test_bad_port_width_is_not_guessed(self):
        tree = adt_node({"name": b"pcie\0", "#ports": b"\x01\x00"})
        entry = module.inspect_pcie(tree)["pcie_nodes"][0]
        self.assertEqual(entry["ports_length"], 2)
        self.assertIsNone(entry["ports_u32_le"])

    def test_synthetic_reg_pairs_are_raw_not_apple_ports(self):
        reg = struct.pack("<QQQQ", 0x3f000000, 0x01000000, 0x10000000, 0x10000000)
        tree = adt_node({"name": b"pcie\0", "compatible": b"apcie,t8140\0", "reg": reg})
        entry = module.inspect_pcie(tree)["pcie_nodes"][0]
        self.assertEqual(entry["reg_u64_le_pairs"], [
            {"first_u64_le": 0x3f000000, "second_u64_le": 0x01000000},
            {"first_u64_le": 0x10000000, "second_u64_le": 0x10000000},
        ])
        self.assertFalse(entry["ports_present"])
        self.assertEqual(module.inspect_pcie(tree)["qemu_root_port_to_apple_ports_mapping"], "UNPROVEN")

    def test_malformed_reg_width_remains_uninterpreted(self):
        tree = adt_node({"name": b"pcie\0", "reg": b"\x00" * 17})
        entry = module.inspect_pcie(tree)["pcie_nodes"][0]
        self.assertIsNone(entry["reg_u64_le_pairs"])
        self.assertEqual(entry["properties"]["reg"]["length"], 17)

    def test_no_candidate(self):
        tree = adt_node({"name": b"device-tree\0"}, [adt_node({"name": b"arm-io\0"})])
        self.assertEqual(module.inspect_pcie(tree)["pcie_nodes"], [])

    def test_truncated_rejected(self):
        with self.assertRaises(module.AdtFormatError):
            module.parse_adt(adt_node({"name": b"pcie\0"})[:-1])

    def test_trailing_rejected(self):
        with self.assertRaises(module.AdtFormatError):
            module.parse_adt(adt_node({"name": b"pcie\0"}) + b"\0")

    def test_duplicate_property_rejected(self):
        header = struct.pack("<II", 2, 0)
        prop = b"name".ljust(32, b"\0") + struct.pack("<I", 4) + b"pcie"
        with self.assertRaises(module.AdtFormatError):
            module.parse_adt(header + prop + prop)


if __name__ == "__main__":
    unittest.main()
