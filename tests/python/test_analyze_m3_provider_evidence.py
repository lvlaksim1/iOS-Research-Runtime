"""Synthetic-only fixtures: no guest PCIe/NVMe or Stage1 runtime acceptance."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "scripts" / "analyze_m3_provider_evidence.py"
spec = importlib.util.spec_from_file_location("analyze_m3_provider_evidence", MODULE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def classify(text: str) -> dict:
    return module.analyze(text.encode("utf-8"))


class ProviderEvidenceTests(unittest.TestCase):
    def test_recovery_boot_proof_never_accepts_stage1(self):
        evidence = classify("BOOT_PROOF_OK\nIOS_M2_BOUNDARY_PROBE_OK\n")
        self.assertTrue(evidence["recovery_root_shell_marker_seen"])
        self.assertEqual(evidence["probe_state"], "NOT_OBSERVED")
        self.assertFalse(evidence["stage1_accepted"])

    def test_panic_missing_ports_is_earliest_blocker(self):
        evidence = classify("panic: lookupDTProperty failed #ports ApplePCIEDTHelpers.h:48\n")
        self.assertEqual(evidence["earliest_blocker"], "GUEST_PCIE_ADT_MISSING_PORTS_PANIC")
        self.assertEqual(evidence["missing_ports_panic"]["line"], 1)

    def test_complete_probe_reports_explicit_absence(self):
        evidence = classify("\n".join((module.BEGIN, module.IOPRINT_DT,
            module.IOPRINT_SERVICE, module.IOPRINT_CLASSES, module.CLASSES_ABSENT, module.END)))
        self.assertEqual(evidence["probe_state"], "CLASSES_ABSENT_MARKER")
        self.assertEqual(evidence["earliest_blocker"], "NO_PCIE_NVME_CLASSES_OBSERVED")
        self.assertEqual(evidence["candidate_class_names_text_only"], [])

    def test_ioprint_unavailable_distinct_from_absence(self):
        evidence = classify("\n".join((module.BEGIN, module.IOPRINT_UNAVAILABLE, module.END)))
        self.assertEqual(evidence["probe_state"], "IOPRINT_UNAVAILABLE")
        self.assertEqual(evidence["earliest_blocker"], "IOPRINT_UNAVAILABLE")

    def test_class_text_never_proves_binding(self):
        evidence = classify("\n".join((module.BEGIN, module.IOPRINT_SERVICE,
            module.IOPRINT_CLASSES, "+-o AppleT8140PCIe", "  +-o AppleNVMe", module.END)))
        self.assertEqual(evidence["probe_state"], "CLASS_NAMES_IN_TEXT_ONLY")
        self.assertEqual(evidence["candidate_class_names_text_only"], ["AppleNVMe", "AppleT8140PCIe"])
        self.assertEqual(evidence["guest_nvme_bound_device"], "UNPROVEN")
        self.assertFalse(evidence["stage1_accepted"])

    def test_shell_echo_and_grep_commands_not_evidence(self):
        evidence = classify("\n".join(("echo " + module.BEGIN,
            module.BEGIN, module.IOPRINT_CLASSES,
            "echo AppleNVMe", "grep -E 'AppleT8140PCIe|AppleNVMe'", module.END)))
        self.assertEqual(evidence["candidate_class_names_text_only"], [])
        self.assertEqual(evidence["probe_begin_count"], 1)

    def test_latest_incomplete_probe_overrides_old_complete(self):
        evidence = classify("\n".join((module.BEGIN, module.CLASSES_ABSENT, module.END,
            module.BEGIN, module.IOPRINT_CLASSES, "AppleNVMe")))
        self.assertEqual(evidence["probe_state"], "INCOMPLETE")
        self.assertIsNone(evidence["probe_end_line"])
        self.assertEqual(evidence["candidate_class_names_text_only"], [])

    def test_non_utf8_and_empty_are_bounded(self):
        self.assertEqual(module.analyze(b"\xff")["probe_state"], "NOT_OBSERVED")
        self.assertEqual(module.analyze(b"")["input_size_bytes"], 0)


if __name__ == "__main__":
    unittest.main()
