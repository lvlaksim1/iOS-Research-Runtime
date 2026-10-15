"""Offline contract for G48 Windows QEMU trace gate integration.

Requires the separately verified G47 checker as a dependency. These static
checks do not execute Windows QEMU or prove a guest interrupt is delivered.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/qemu-sptm-windows.yml"
CHECKER = ROOT / "scripts/check_m3_windows_qemu_trace_capability.py"


def step_names(text: str) -> list[str]:
    return re.findall(r"(?m)^      - name: ([^\n]+)$", text)


class WindowsTraceGateContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.checker = CHECKER.read_text(encoding="utf-8")
        cls.steps = step_names(cls.workflow)

    def test_same_build_step_order(self) -> None:
        ordered = [
            "Build qemu-sptm",
            "Verify compiled QEMU NVMe IRQ trace capability",
            "Upload compiled QEMU trace capability evidence",
            "Save QEMU build cache",
            "Verify Darwin machine",
            "Stage standalone QEMU runtime",
            "Upload proof artifact",
        ]
        positions = [self.steps.index(s) for s in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_unique_gate_and_evidence_upload(self) -> None:
        for name in ("Verify compiled QEMU NVMe IRQ trace capability",
                     "Upload compiled QEMU trace capability evidence"):
            self.assertEqual(self.steps.count(name), 1)

    def test_gate_is_fail_closed(self) -> None:
        segment = self.workflow.split(
            "      - name: Verify compiled QEMU NVMe IRQ trace capability\n", 1
        )[1].split("      - name: Upload compiled QEMU trace capability evidence\n", 1)[0]
        self.assertIn("set -euo pipefail", segment)
        self.assertNotIn("|| true", segment)
        self.assertNotIn("continue-on-error", segment)
        self.assertIn("python scripts/check_m3_windows_qemu_trace_capability.py", segment)

    def test_binary_and_configuration_share_build_root(self) -> None:
        self.assertIn("--build-root qemu-sptm/build", self.workflow)
        self.assertIn("--binary qemu-sptm/build/qemu-system-aarch64.exe", self.workflow)
        self.assertIn("ninja qemu-system-aarch64.exe", self.workflow)

    def test_json_evidence_upload_even_on_gate_failure(self) -> None:
        self.assertIn("--output qemu-proof/nvme-irq-trace-capability.json", self.workflow)
        segment = self.workflow.split(
            "      - name: Upload compiled QEMU trace capability evidence\n", 1
        )[1].split("      - name: Save QEMU build cache\n", 1)[0]
        self.assertIn("if: always()", segment)
        self.assertIn("path: qemu-proof/nvme-irq-trace-capability.json", segment)
        self.assertIn("if-no-files-found: warn", segment)

    def test_pinned_qemu_and_existing_cache_preserved(self) -> None:
        self.assertIn("git checkout 2867d847d3471560e773120ee50c42dbcbb6d60b", self.workflow)
        self.assertIn("qemu-sptm-win64-2867d847-headless-v2-", self.workflow)
        self.assertIn("if [ ! -f build.ninja ]; then", self.workflow)

    def test_restored_checker_requires_config_and_real_binary(self) -> None:
        for required in ("intro-buildoptions.json", "config-host.h", "CONFIG_TRACE_LOG",
                         '"-trace", "help"', '"-M", "help"', "sha256_file(binary)"):
            self.assertIn(required, self.checker)
        self.assertIn('return 0 if report["catalog_capability"]', self.checker)

    def test_no_guest_e2e_added_to_workflow(self) -> None:
        self.assertNotIn("ios-system-boot", self.workflow)
        self.assertNotIn("guest-e2e", self.workflow)
        self.assertNotIn("--kernel", self.workflow)

    def test_checker_is_dependency_not_changed_file(self) -> None:
        self.assertTrue(CHECKER.is_file())
        self.assertIn("NOT_PROVEN", self.checker)


if __name__ == "__main__":
    unittest.main()
