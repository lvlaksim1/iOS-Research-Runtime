"""Synthetic Mach-O format checks; not a substitute for a real iOS guest run."""

import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_m3_ioprint_macho_platform", ROOT / "scripts/check_m3_ioprint_macho_platform.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def command(cmd, payload=b""):
    if cmd == 0x32:
        return struct.pack("<IIIIII", cmd, 24, payload if isinstance(payload, int) else 2, 0, 0, 0)
    if cmd in (0x25, 0x24, 0x2F, 0x30):
        return struct.pack("<IIII", cmd, 16, 0, 0)
    return struct.pack("<II", cmd, 8)


def thin(commands=None, cpu=0x0100000C, subtype=0, filetype=2, ncmds=None, sizeofcmds=None):
    commands = [command(0x25)] if commands is None else commands
    raw = b"".join(commands)
    return struct.pack("<IiiIIIII", 0xFEEDFACF, cpu, subtype, filetype,
                       len(commands) if ncmds is None else ncmds,
                       len(raw) if sizeofcmds is None else sizeofcmds, 0, 0) + raw


def fat(parts, wide=False):
    head = struct.pack(">II", 0xCAFEBABF if wide else 0xCAFEBABE, len(parts))
    entry_size = 32 if wide else 20
    off = 8 + len(parts) * entry_size
    entries = b""
    body = b""
    for cpu, subtype, payload in parts:
        if wide:
            entries += struct.pack(">iiQQII", cpu, subtype, off, len(payload), 0, 0)
        else:
            entries += struct.pack(">iiIII", cpu, subtype, off, len(payload), 0)
        body += payload
        off += len(payload)
    return head + entries + body


class MachOGateTests(unittest.TestCase):
    def check_reject(self, data):
        with self.assertRaises(MODULE.MachOValidationError):
            MODULE.validate_macho(data)

    def test_thin_ios_version_min(self):
        result = MODULE.validate_macho(thin())
        self.assertEqual((result["container"], result["platform"]), ("thin64", "iOS"))

    def test_thin_ios_build_version(self):
        self.assertEqual(MODULE.validate_macho(thin([command(0x32)]))["platform"], "iOS")

    def test_both_ios_platform_commands(self):
        self.assertEqual(len(MODULE.validate_macho(thin([command(0x25), command(0x32)]))["platform_evidence"]), 2)

    def test_arm64e_subtype(self):
        self.assertEqual(MODULE.validate_macho(thin(subtype=2))["cpu_subtype"], 2)

    def test_reject_x86_64(self):
        self.check_reject(thin(cpu=0x01000007))

    def test_reject_dylib(self):
        self.check_reject(thin(filetype=6))

    def test_reject_macos_version_min(self):
        self.check_reject(thin([command(0x24)]))

    def test_reject_simulator_build_platform(self):
        self.check_reject(thin([command(0x32, 7)]))

    def test_reject_missing_platform(self):
        self.check_reject(thin([command(0x1)]))

    def test_reject_duplicate_platform(self):
        self.check_reject(thin([command(0x25), command(0x25)]))

    def test_reject_truncated_header(self):
        self.check_reject(thin()[:20])

    def test_reject_zero_load_command_size(self):
        self.check_reject(thin([struct.pack("<II", 0x25, 0)]))

    def test_reject_unaligned_load_command(self):
        self.check_reject(thin([struct.pack("<II", 0x25, 9) + b"x"]))

    def test_reject_load_region_short(self):
        self.check_reject(thin(sizeofcmds=4))

    def test_reject_ncmds_mismatch(self):
        self.check_reject(thin(ncmds=2))

    def test_reject_load_region_extra(self):
        self.check_reject(thin(sizeofcmds=24) + b"extra123")

    def test_reject_build_version_short(self):
        self.check_reject(thin([struct.pack("<II", 0x32, 8)]))

    def test_reject_build_version_truncated_tools(self):
        self.check_reject(thin([struct.pack("<IIIIII", 0x32, 24, 2, 0, 0, 1)]))

    def test_fat32_arm64_and_x86(self):
        payload = fat([(0x01000007, 3, b"x" * 32), (0x0100000C, 0, thin())])
        self.assertEqual(MODULE.validate_macho(payload)["container"], "fat32")

    def test_fat64_arm64(self):
        self.assertEqual(MODULE.validate_macho(fat([(0x0100000C, 0, thin())], True))["container"], "fat64")

    def test_reject_fat32_misaligned_arm64_slice(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())]))
        struct.pack_into(">I", payload, 8 + 16, 5)  # offset 28, requires 32-byte alignment
        self.check_reject(bytes(payload))

    def test_reject_fat64_misaligned_arm64_slice(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())], True))
        struct.pack_into(">I", payload, 8 + 24, 5)  # offset 40, requires 32-byte alignment
        self.check_reject(bytes(payload))

    def test_reject_fat64_nonzero_reserved(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())], True))
        struct.pack_into(">I", payload, 8 + 28, 1234)
        self.check_reject(bytes(payload))

    def test_reject_fat32_impossible_alignment_exponent(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())]))
        struct.pack_into(">I", payload, 8 + 16, 31)
        self.check_reject(bytes(payload))

    def test_reject_fat64_impossible_alignment_exponent(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())], True))
        struct.pack_into(">I", payload, 8 + 24, 63)
        self.check_reject(bytes(payload))

    def test_fat32_aligned_slice_is_accepted(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())]))
        struct.pack_into(">I", payload, 8 + 16, 5)
        struct.pack_into(">I", payload, 8 + 8, 32)
        payload[28:28] = b"\0" * 4
        self.assertEqual(MODULE.validate_macho(bytes(payload))["container"], "fat32")

    def test_fat64_aligned_slice_is_accepted(self):
        payload = bytearray(fat([(0x0100000C, 0, thin())], True))
        struct.pack_into(">I", payload, 8 + 24, 5)
        struct.pack_into(">Q", payload, 8 + 8, 64)
        payload[40:40] = b"\0" * 24
        self.assertEqual(MODULE.validate_macho(bytes(payload))["container"], "fat64")

    def test_reject_fat_no_arm64(self):
        self.check_reject(fat([(0x01000007, 3, b"x" * 32)]))

    def test_reject_fat_duplicate_arm64(self):
        self.check_reject(fat([(0x0100000C, 0, thin()), (0x0100000C, 0, thin())]))

    def test_reject_fat_slice_subtype_mismatch(self):
        self.check_reject(fat([(0x0100000C, 2, thin(subtype=0))]))

    def test_reject_fat_table_truncated(self):
        self.check_reject(b"\xca\xfe\xba\xbe\x00\x00\x00\x02")

    def test_reject_fat_overlap(self):
        payload = bytearray(fat([(0x0100000C, 0, thin()), (0x01000007, 3, b"x" * 32)]))
        struct.pack_into(">I", payload, 8 + 20 + 8, 48)
        self.check_reject(bytes(payload))

    def test_cli_pass_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            inp, out = Path(td) / "ioprint", Path(td) / "result.json"
            inp.write_bytes(thin())
            args = [sys.executable, "-B", str(ROOT / "scripts/check_m3_ioprint_macho_platform.py"),
                    "--input", str(inp), "--output", str(out)]
            good = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(out.read_text())["platform"], "iOS")
            out.unlink()
            inp.write_bytes(b"invalid")
            bad = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertFalse(out.exists())

    def test_workflow_orders_fail_closed_gate(self):
        workflow = (ROOT / ".github/workflows/windows-e2e.yml").read_text(encoding="utf-8")
        self.assertLess(workflow.index("Setup pinned Python for ioprint archive checks"),
                        workflow.index("Validate pinned ioprint Mach-O arm64 iOS platform"))
        self.assertLess(workflow.index("Validate pinned ioprint Mach-O arm64 iOS platform"),
                        workflow.index("Verify Python and run ioprint pre-boot tests"))
        self.assertIn("scripts/check_m3_ioprint_macho_platform.py", workflow)
        self.assertIn("tests/python/test_m3_ioprint_macho_platform.py", workflow)
        self.assertIn('if ($LASTEXITCODE -ne 0) { throw "ioprint Mach-O platform gate failed" }', workflow)


if __name__ == "__main__":
    unittest.main()
