"""Synthetic ADT byte fixtures only; these cannot prove real iOS PCIe binding."""
from __future__ import annotations

import hashlib
import struct
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from capture_native_apcie_properties import capture_native_apcie, AdtFormatError  # noqa: E402


def node(props: dict[str, bytes], children: list[bytes] | None = None) -> bytes:
    children = children or []
    buf = bytearray(struct.pack("<II", len(props), len(children)))
    for name, raw in props.items():
        encoded = name.encode("ascii")
        assert len(encoded) < 32
        buf.extend(encoded.ljust(32, b"\x00"))
        buf.extend(struct.pack("<I", len(raw)))
        buf.extend(raw)
        buf.extend(b"\x00" * (-len(raw) % 4))
    return bytes(buf) + b"".join(children)


def sample() -> bytes:
    leaf = node({"name": b"wlan\0", "iommu-parent-pcie0": b"\x50\x01\x00\x00"})
    bridge0 = node({"name": b"pci-bridge0\0", "compatible": b"apcie-bridge\0",
                    "apcie-port": b"\x00\x00\x00\x00", "AAPL,unit-string": b"00000000\0",
                    "msi-vector-base": b"\x20\x00\x00\x00", "#msi-vectors": b"\x08\x00\x00\x00"}, [leaf])
    bridge1 = node({"name": b"pci-bridge1\0", "apcie-port": b"\x01\x00\x00\x00"})
    bridge2 = node({"name": b"pci-bridge2\0", "apcie-port": b"\x02\x00\x00\x00"})
    apcie = node({"name": b"apcie\0", "compatible": b"apcie,t8140\0",
                  "#ports": struct.pack("<I", 3), "interrupts": b"\x11\x22\x33\x44"},
                 [bridge0, bridge1, bridge2])
    synthetic = node({"name": b"pcie\0", "compatible": b"apcie,t8140\0"})
    return node({"name": b"device-tree\0"}, [node({"name": b"arm-io\0"}, [apcie, synthetic])])


class NativeApcieRawEvidenceTests(unittest.TestCase):
    def test_exact_selected_bytes_and_no_mapping_claim(self):
        raw = sample()
        evidence = capture_native_apcie(raw)
        self.assertEqual(evidence["input_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(evidence["input_size_bytes"], len(raw))
        self.assertEqual(evidence["apcie_path"], "/device-tree/arm-io/apcie")
        self.assertEqual(evidence["apcie_ports_u32_le"], 3)
        self.assertEqual(evidence["apcie_properties"]["#ports"], {"size_bytes": 4, "raw_hex": "03000000"})
        self.assertEqual(len(evidence["bridge_nodes"]), 3)
        self.assertEqual(evidence["bridge_nodes"][0]["properties"]["msi-vector-base"]["raw_hex"], "20000000")
        self.assertEqual(evidence["bridge_nodes"][0]["descendants"][0]["properties"]["iommu-parent-pcie0"]["raw_hex"], "50010000")
        self.assertEqual(evidence["qemu_root_port_to_apple_ports_mapping"], "UNPROVEN")
        self.assertEqual(evidence["guest_iokit_binding"], "UNPROVEN")
        self.assertFalse(evidence["stage1_accepted"])

    def test_synthetic_pcie_does_not_count_as_native_apcie(self):
        raw = node({"name": b"pcie\0", "compatible": b"apcie,t8140\0"})
        with self.assertRaisesRegex(AdtFormatError, "found 0"):
            capture_native_apcie(raw)

    def test_duplicate_native_apcie_rejected(self):
        apcie = node({"name": b"apcie\0", "compatible": b"apcie,t8140\0"})
        raw = node({"name": b"device-tree\0"}, [apcie, apcie])
        with self.assertRaisesRegex(AdtFormatError, "found 2"):
            capture_native_apcie(raw)

    def test_truncated_adt_rejected(self):
        with self.assertRaises(AdtFormatError):
            capture_native_apcie(sample()[:-1])

    def test_selected_property_over_limit_rejected(self):
        apcie = node({"name": b"apcie\0", "compatible": b"apcie,t8140\0",
                      "interrupts": b"\x01" * 4097})
        with self.assertRaisesRegex(AdtFormatError, "exceeds evidence limit"):
            capture_native_apcie(apcie)

    def test_short_ports_not_guessed(self):
        apcie = node({"name": b"apcie\0", "compatible": b"apcie,t8140\0", "#ports": b"\x03\x00"})
        result = capture_native_apcie(apcie)
        self.assertIsNone(result["apcie_ports_u32_le"])
        self.assertEqual(result["apcie_properties"]["#ports"]["raw_hex"], "0300")


if __name__ == "__main__":
    unittest.main()
