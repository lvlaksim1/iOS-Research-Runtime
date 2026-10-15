"""Host-only build-gate tests; no Apple SDK, iOS compile or guest execution."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve()
MODULE = HERE.parents[2] / "scripts" / "build_ios_m3_ioreg_lineage.py"
SOURCE = HERE.parents[2] / "scripts" / "ios_m3_ioreg_lineage.c"
spec = importlib.util.spec_from_file_location("m3_build", MODULE)
m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m3)


def macho(platform=2, *, cpu_type=None, ncmds=1, sizeofcmds=24, cmdsize=24):
    cpu = m3.ARM64_CPU_TYPE if cpu_type is None else cpu_type
    header = m3.MH_MAGIC_64_LE + struct.pack("<IIIIIII", cpu, 0, 2, ncmds, sizeofcmds, 0, 0)
    command = struct.pack("<IIIIII", m3.LC_BUILD_VERSION, cmdsize, platform, 0, 0, 0)
    return header + command


def legacy_macho(command=m3.LC_VERSION_MIN_IPHONEOS):
    header = m3.MH_MAGIC_64_LE + struct.pack("<IIIIIII", m3.ARM64_CPU_TYPE, 0, 2, 1, 16, 0, 0)
    return header + struct.pack("<IIII", command, 16, 0x000C0000, 0x000C0000)


class BuildGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "collector.c"
        self.src.write_text("/* IOS_M3_HOST_TEST IORegistryEntryGetParentEntry */\n")
        self.out = self.root / "collector"

    def test_dry_run_reports_no_compilation_or_guest_proof(self):
        result = m3.build(self.src, self.out, dry_run=True)
        self.assertEqual(result["status"], "NOT_COMPILED")
        self.assertEqual(result["sdk"], "iphoneos")
        self.assertEqual(result["architecture"], "arm64")
        self.assertFalse(result["full_system_boot_accepted"])
        self.assertFalse(self.out.exists())

    def test_linux_fails_without_output(self):
        with self.assertRaisesRegex(m3.BuildGateError, "requires_macos"):
            m3.build(self.src, self.out, host_system="Linux")
        self.assertFalse(self.out.exists())

    def test_existing_output_is_never_overwritten(self):
        self.out.write_bytes(b"preserve")
        with self.assertRaisesRegex(m3.BuildGateError, "output_already_exists"):
            m3.build(self.src, self.out, dry_run=True)
        self.assertEqual(self.out.read_bytes(), b"preserve")

    def test_missing_expected_api_fails(self):
        self.src.write_text("int main(void) { return 0; }")
        with self.assertRaisesRegex(m3.BuildGateError, "not_expected_collector"):
            m3.build(self.src, self.out, dry_run=True)

    def test_missing_xcrun_fails_closed(self):
        with mock.patch.object(m3.shutil, "which", return_value=None):
            with self.assertRaisesRegex(m3.BuildGateError, "xcrun_not_available"):
                m3.build(self.src, self.out, host_system="Darwin")

    def test_macho_arch_and_type_rejection(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(b"not-a-macho")
        with self.assertRaisesRegex(m3.BuildGateError, "output_not_thin_macho64"):
            m3._macho_arm64_executable(candidate)
        candidate.write_bytes(m3.MH_MAGIC_64_LE + struct.pack("<III", 7, 0, 2) + b"\0" * 20)
        with self.assertRaisesRegex(m3.BuildGateError, "wrong_arch"):
            m3._macho_arm64_executable(candidate)
        candidate.write_bytes(m3.MH_MAGIC_64_LE + struct.pack("<III", m3.ARM64_CPU_TYPE, 0, 6) + b"\0" * 20)
        with self.assertRaisesRegex(m3.BuildGateError, "wrong_arch"):
            m3._macho_arm64_executable(candidate)
        candidate.write_bytes(macho())
        m3._macho_arm64_executable(candidate)

    def test_macos_arm64_is_rejected_as_wrong_platform(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(macho(platform=1))
        with self.assertRaisesRegex(m3.BuildGateError, "not_iphoneos_platform"):
            m3._macho_arm64_executable(candidate)

    def test_legacy_iphoneos_version_command_is_accepted(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(legacy_macho())
        m3._macho_arm64_executable(candidate)

    def test_legacy_macos_version_command_is_rejected(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(legacy_macho(m3.LC_VERSION_MIN_MACOSX))
        with self.assertRaisesRegex(m3.BuildGateError, "not_iphoneos_platform"):
            m3._macho_arm64_executable(candidate)

    def test_missing_build_version_is_rejected(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(m3.MH_MAGIC_64_LE + struct.pack("<IIIIIII", m3.ARM64_CPU_TYPE, 0, 2, 0, 0, 0, 0))
        with self.assertRaisesRegex(m3.BuildGateError, "invalid_load_commands"):
            m3._macho_arm64_executable(candidate)

    def test_truncated_load_commands_are_rejected(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(macho()[:-1])
        with self.assertRaisesRegex(m3.BuildGateError, "invalid_load_commands"):
            m3._macho_arm64_executable(candidate)

    def test_invalid_command_size_is_rejected(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(macho(cmdsize=0))
        with self.assertRaisesRegex(m3.BuildGateError, "invalid_load_commands"):
            m3._macho_arm64_executable(candidate)

    def test_ios_arm64_platform_is_accepted_but_not_guest_proof(self):
        candidate = self.root / "candidate"
        candidate.write_bytes(macho(platform=2))
        m3._macho_arm64_executable(candidate)

    def test_compiler_failure_never_creates_target(self):
        sdk = self.root / "iPhoneOS.sdk"
        sdk.mkdir()
        clang = self.root / "clang"
        clang.write_text("mock")
        def fake_run(cmd, **kwargs):
            if "--show-sdk-path" in cmd:
                return str(sdk)
            if "--find" in cmd:
                return str(clang)
            raise m3.BuildGateError("tool_failed:exit=1:command=xcrun")
        with mock.patch.object(m3.shutil, "which", return_value="/fake/xcrun"):
            with mock.patch.object(m3, "_run", side_effect=fake_run):
                with self.assertRaisesRegex(m3.BuildGateError, "tool_failed"):
                    m3.build(self.src, self.out, host_system="Darwin")
        self.assertFalse(self.out.exists())

    def test_fake_macho_output_not_misreported_as_guest_proof(self):
        sdk = self.root / "iPhoneOS.sdk"
        sdk.mkdir()
        clang = self.root / "clang"
        clang.write_text("mock")
        commands = []
        def fake_run(cmd, **kwargs):
            commands.append(cmd)
            if "--show-sdk-path" in cmd:
                return str(sdk)
            if "--find" in cmd:
                return str(clang)
            target = Path(cmd[cmd.index("-o") + 1])
            target.write_bytes(macho(platform=2))
            return ""
        with mock.patch.object(m3.shutil, "which", return_value="/fake/xcrun"):
            with mock.patch.object(m3, "_run", side_effect=fake_run):
                result = m3.build(self.src, self.out, host_system="Darwin")
        self.assertEqual(result["status"], "COMPILED_MACHO_ARM64_UNSIGNED_UNSTAGED")
        self.assertFalse(result["guest_execution_proven"])
        self.assertFalse(result["driver_binding_proven"])
        self.assertFalse(result["full_system_boot_accepted"])
        self.assertTrue(self.out.exists())
        cmd = commands[-1]
        self.assertEqual(cmd[cmd.index("-arch") + 1], "arm64")
        self.assertEqual(cmd[cmd.index("-target") + 1], "arm64-apple-ios")
        self.assertEqual(cmd[cmd.index("-isysroot") + 1], str(sdk))
        self.assertIn("IOKit", cmd)
        self.assertNotIn("codesign", cmd)

    def test_actual_collector_dry_run_is_only_a_plan(self):
        self.assertTrue(SOURCE.is_file())
        result = m3.build(SOURCE, self.out, dry_run=True)
        self.assertEqual(result["status"], "NOT_COMPILED")
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
