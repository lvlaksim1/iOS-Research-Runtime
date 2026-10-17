"""Static CI prerequisite gate; not a Windows run or iOS boot proof."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/windows-e2e.yml"


class WindowsPythonSetupContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_path_triggers_include_unpublished_dependencies(self):
        for path in (
            ".github/workflows/windows-e2e.yml",
            "scripts/check_m3_ioprint_tar_mode.py",
            "scripts/fix_m3_ioprint_tar_mode.py",
            "tests/python/test_check_m3_ioprint_tar_mode.py",
            "tests/python/test_fix_m3_ioprint_tar_mode.py",
            "tests/python/test_m3_ioprint_windows_integration.py",
            "tests/python/test_m3_ioprint_windows_python_setup.py",
        ):
            with self.subTest(path=path):
                self.assertIn("      - '" + path + "'", self.source)

    def test_python_setup_is_explicit_and_version_pinned(self):
        self.assertIn("uses: actions/setup-python@v5", self.source)
        self.assertIn("python-version: '3.12'", self.source)
        self.assertIn('sys.version_info[:2] == (3, 12)', self.source)

    def test_python_setup_precedes_checks_and_integration(self):
        source = self.source
        names = (
            "- name: Setup pinned Python for ioprint archive checks",
            "- name: Verify Python and run ioprint pre-boot tests",
            "- name: Download QEMU runtime from gate",
            "- name: Restore integration harness",
            "- name: Run provisioning and Darwin root-shell proof",
        )
        positions = [source.index(name) for name in names]
        self.assertEqual(positions, sorted(positions))
        for name in names:
            self.assertEqual(source.count(name), 1)

    def test_python_preflight_is_fail_closed(self):
        source = self.source
        self.assertIn("python -B -m py_compile", source)
        self.assertIn("python -B -m unittest discover -s tests/python -p 'test_*ioprint*.py' -v", source)
        self.assertIn('if ($LASTEXITCODE -ne 0) { throw "ioprint Python syntax checks failed" }', source)
        self.assertIn('if ($LASTEXITCODE -ne 0) { throw "ioprint pre-boot tests failed" }', source)

    def test_compile_checks_both_archive_scripts_and_all_three_test_suites(self):
        preflight = self.source.split("- name: Verify Python and run ioprint pre-boot tests", 1)[1]
        preflight = preflight.split("- name: Download QEMU runtime from gate", 1)[0]
        for path in (
            "scripts/check_m3_ioprint_tar_mode.py",
            "scripts/fix_m3_ioprint_tar_mode.py",
            "tests/python/test_check_m3_ioprint_tar_mode.py",
            "tests/python/test_fix_m3_ioprint_tar_mode.py",
            "tests/python/test_m3_ioprint_windows_integration.py",
            "tests/python/test_m3_ioprint_windows_python_setup.py",
        ):
            with self.subTest(path=path):
                self.assertIn(path, preflight)

    def test_pinned_ioprint_sha_matches_integration_and_fails_early(self):
        program = (WORKFLOW.parents[2] / "tools/IOSResearchRuntime.Integration/Program.cs").read_text(encoding="utf-8")
        expected = re.search(r'var pinnedIoprintSha256 = "([0-9a-f]{64})";', program)
        workflow_pin = re.search(r'\$pinnedIoprintSha256 = "([0-9a-f]{64})"', self.source)
        self.assertIsNotNone(expected, "C# integration must pin the ioprint executable")
        self.assertIsNotNone(workflow_pin, "Windows workflow must independently pin ioprint")
        self.assertEqual(workflow_pin.group(1), expected.group(1))
        self.assertIn('if ($ioprintHash -ne $pinnedIoprintSha256)', self.source)
        self.assertIn('throw "Pinned iokit-utils 1.4.0 ioprint SHA-256 mismatch:', self.source)
        self.assertIn('"IOKIT_UTILS_IOS_IOPRINT_SHA256_EXPECTED=$pinnedIoprintSha256"', self.source)
        self.assertLess(self.source.index('if ($ioprintHash -ne $pinnedIoprintSha256)'),
                        self.source.index('"IOKIT_UTILS_IOS_IOPRINT_SHA256=$ioprintHash"'))

    def test_exact_sha_and_qemu_gate_semantics_unchanged(self):
        source = self.source
        self.assertIn("ref: ${{ github.sha }}", source)
        self.assertIn("uses: ./.github/workflows/qemu-sptm-windows.yml", source)
        self.assertIn("needs: qemu-gate", source)
        self.assertIn("QEMU_GATE_MODE=SAME_RUN_REUSABLE_WORKFLOW", source)

    def test_no_claim_of_full_ios_boot(self):
        self.assertIn("- name: Run provisioning and Darwin root-shell proof", self.source)
        self.assertNotIn("FULL_IOS_SYSTEM_BOOT_PROVEN", self.source)


if __name__ == "__main__":
    unittest.main()
