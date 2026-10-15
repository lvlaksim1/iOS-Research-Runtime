"""Host-only negative and synthetic tests for the iPhoneOS ABI prerequisite probe."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "probe_ios_m3_iokit_abi.py"
spec = importlib.util.spec_from_file_location("probe_ios_m3_iokit_abi", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def macho(platform=2, *, legacy=False, truncate=False, no_commands=False, conflict=False):
    if no_commands:
        commands = b""
    elif legacy:
        commands = struct.pack("<IIII", module.LC_VERSION_MIN_IPHONEOS, 16,
                               0x000C0000, 0x000C0000)
    else:
        commands = struct.pack("<IIIIII", module.LC_BUILD_VERSION, 24,
                               platform, 0x000C0000, 0x000C0000, 0)
    if conflict:
        commands += struct.pack("<IIII", module.LC_VERSION_MIN_MACOSX, 16,
                                0x000C0000, 0x000C0000)
    count = (0 if no_commands else 1) + int(conflict)
    header = b"\xcf\xfa\xed\xfe" + struct.pack("<IIIIIII", module.MACHO_ARM64_CPU,
                    0, module.MACHO_EXECUTE, count, len(commands), 0, 0)
    result = header + commands
    return result[:-1] if truncate else result


class TestProbe(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "collector.c"
        self.src.write_text("int IORegistryCreateIterator; int IORegistryEntryGetParentEntry;", encoding="utf-8")
        self.sdk = self.root / "iPhoneOS.sdk"
        self.sdk.mkdir()
        self.clang = self.root / "clang"
        self.clang.write_bytes(b"fake")
        self.calls = []

    def run_fake(self, cmd, *, stage):
        self.calls.append((stage, cmd))
        if "--show-sdk-path" in cmd:
            return str(self.sdk)
        if "--show-sdk-version" in cmd:
            return "18.0"
        if "--find" in cmd:
            return str(self.clang)
        if stage == "OBJECT_COMPILE":
            Path(cmd[cmd.index("-o") + 1]).write_bytes(b"fake-object")
        if stage == "IOKIT_LINK":
            Path(cmd[cmd.index("-o") + 1]).write_bytes(macho())
        return ""

    def go(self, run=None, host_system="Darwin", which=None):
        return module.probe(self.src, host_system=host_system,
                            which=which or (lambda x: "/fake/xcrun"),
                            run=run or self.run_fake)

    def test_non_macos_fails_closed(self):
        r = self.go(host_system="Linux")
        self.assertEqual((r["stage"], r["reason"]), ("SDK", "requires_macos"))
        self.assertFalse(r["full_system_boot_accepted"])
        self.assertFalse(self.calls)

    def test_missing_xcrun(self):
        r = self.go(which=lambda x: None)
        self.assertEqual(r["reason"], "xcrun_missing")

    def test_source_missing(self):
        self.src.unlink()
        self.assertEqual(self.go()["stage"], "SOURCE")

    def test_source_wrong(self):
        self.src.write_text("int main(void){return 0;}")
        self.assertEqual(self.go()["reason"], "not_expected_ioreg_collector")

    def test_sdk_absent(self):
        self.sdk.rmdir()
        self.assertEqual(self.go()["reason"], "missing_sdk_path_or_version")

    def test_header_failure_distinct(self):
        def run(cmd, *, stage):
            if stage == "HEADER_DECLARATIONS":
                raise module.ProbeFailure(stage, "exit_1")
            return self.run_fake(cmd, stage=stage)
        r = self.go(run=run)
        self.assertEqual(r["stage"], "HEADER_DECLARATIONS")
        self.assertFalse(r["header_declarations_verified"])

    def test_object_failure_distinct(self):
        def run(cmd, *, stage):
            if stage == "OBJECT_COMPILE":
                raise module.ProbeFailure(stage, "exit_1")
            return self.run_fake(cmd, stage=stage)
        r = self.go(run=run)
        self.assertTrue(r["header_declarations_verified"])
        self.assertEqual(r["stage"], "OBJECT_COMPILE")

    def test_link_failure_distinct(self):
        def run(cmd, *, stage):
            if stage == "IOKIT_LINK":
                raise module.ProbeFailure(stage, "exit_1")
            return self.run_fake(cmd, stage=stage)
        r = self.go(run=run)
        self.assertTrue(r["object_compiled"])
        self.assertEqual(r["stage"], "IOKIT_LINK")
        self.assertFalse(r["iokit_linked"])

    def test_wrong_macho_fails_closed(self):
        def run(cmd, *, stage):
            result = self.run_fake(cmd, stage=stage)
            if stage == "IOKIT_LINK":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(b"not-a-mach-o")
            return result
        self.assertEqual(self.go(run=run)["stage"], "MACHO_VERIFY")

    def test_synthetic_success_is_only_prerequisite(self):
        r = self.go()
        self.assertEqual(r["status"], "COMPILE_LINK_PREREQUISITE_ONLY")
        self.assertTrue(r["sdk_identity_verified"])
        self.assertTrue(r["iokit_linked"])
        self.assertFalse(r["guest_execution_proven"])
        self.assertFalse(r["driver_binding_proven"])
        self.assertFalse(r["full_system_boot_accepted"])
        self.assertEqual([x[0] for x in self.calls].count("HEADER_DECLARATIONS"), 1)
        for stage, cmd in self.calls:
            if stage in ("HEADER_DECLARATIONS", "OBJECT_COMPILE", "IOKIT_LINK"):
                self.assertEqual(cmd[cmd.index("-target") + 1], "arm64-apple-ios")
                self.assertEqual(cmd[cmd.index("-isysroot") + 1], str(self.sdk))

    def test_macos_arm64_executable_is_rejected(self):
        def fake(cmd, *, stage):
            result = self.run_fake(cmd, stage=stage)
            if stage == "IOKIT_LINK":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(macho(platform=1))
            return result
        r = self.go(run=fake)
        self.assertEqual((r["stage"], r["reason"]), ("MACHO_VERIFY", "not_iphoneos_platform"))
        self.assertFalse(r["iokit_linked"])

    def test_legacy_iphoneos_executable_is_accepted(self):
        def fake(cmd, *, stage):
            result = self.run_fake(cmd, stage=stage)
            if stage == "IOKIT_LINK":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(macho(legacy=True))
            return result
        self.assertEqual(self.go(run=fake)["status"], "COMPILE_LINK_PREREQUISITE_ONLY")

    def test_missing_platform_is_rejected(self):
        def fake(cmd, *, stage):
            result = self.run_fake(cmd, stage=stage)
            if stage == "IOKIT_LINK":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(macho(no_commands=True))
            return result
        self.assertEqual(self.go(run=fake)["reason"], "invalid_load_commands")

    def test_truncated_platform_command_is_rejected(self):
        def fake(cmd, *, stage):
            result = self.run_fake(cmd, stage=stage)
            if stage == "IOKIT_LINK":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(macho(truncate=True))
            return result
        self.assertEqual(self.go(run=fake)["reason"], "invalid_load_commands")

    def test_conflicting_platform_commands_are_rejected(self):
        def fake(cmd, *, stage):
            result = self.run_fake(cmd, stage=stage)
            if stage == "IOKIT_LINK":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(macho(conflict=True))
            return result
        self.assertEqual(self.go(run=fake)["reason"], "not_iphoneos_platform")

    def test_no_persistent_output(self):
        self.go()
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["clang", "collector.c", "iPhoneOS.sdk"])


if __name__ == "__main__":
    unittest.main()
