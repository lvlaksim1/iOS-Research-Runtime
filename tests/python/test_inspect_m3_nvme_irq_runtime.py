"""Synthetic negative and positive controls; NOT guest E2E evidence."""
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[2] / "scripts/inspect_m3_nvme_irq_runtime.py"
spec = importlib.util.spec_from_file_location("m3irq", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RuntimeIrqEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.binary = self.root / "qemu.exe"
        self.binary.write_bytes(b"synthetic binary, not QEMU")
        self.digest = hashlib.sha256(self.binary.read_bytes()).hexdigest()
        self.trace = self.root / "trace.log"
        self.stderr = self.root / "stderr.log"
        self.events = self.root / "events.txt"
        self.trace.write_text("", encoding="utf-8")
        self.stderr.write_text("", encoding="utf-8")
        self.events.write_text("\n".join(m.EVENT_TEXT) + "\n", encoding="utf-8")

    def check(self):
        return m.inspect(self.binary, self.digest, self.trace, self.stderr, self.events,
                         m.PINNED_QEMU, m.BASELINE_MAIN)

    def test_empty_is_unknown_not_success(self):
        d = self.check()
        self.assertEqual(d["irq_branch_observation"], "NO_NVME_IRQ_EVENT_OBSERVED")
        self.assertFalse(d["full_ios_stage1_proven"])

    def test_msix_vector_branch_only(self):
        self.trace.write_text("123@1608130130.441188:pci_nvme_irq_msix raising MSI-X IRQ vector 3\n")
        d = self.check()
        self.assertEqual(d["irq_branch_observation"], "MSIX_BRANCH_OBSERVED")
        self.assertEqual(d["msix_vectors_observed"], [3])
        self.assertFalse(d["aic_interrupt_delivery_proven"])

    def test_intx_branch_only(self):
        self.trace.write_text("123@1608130130.441188:pci_nvme_irq_pin pulsing IRQ pin\n")
        self.assertEqual(self.check()["irq_branch_observation"], "INTX_BRANCH_OBSERVED")

    def test_mixed_branch_not_sole_msix(self):
        self.trace.write_text("123@1.1:pci_nvme_irq_msix raising MSI-X IRQ vector 2\n123@1.2:pci_nvme_irq_pin pulsing IRQ pin\n")
        self.assertEqual(self.check()["irq_branch_observation"], "BOTH_MSIX_AND_INTX_BRANCHES_OBSERVED")

    def test_only_masked(self):
        self.trace.write_text("123@1.1:pci_nvme_irq_masked IRQ is masked\n")
        self.assertEqual(self.check()["irq_branch_observation"], "ONLY_MASKED_IRQ_OBSERVED")

    def test_reject_unanchored_spoof(self):
        self.trace.write_text("example: 123@1.1:pci_nvme_irq_msix raising MSI-X IRQ vector 2\n")
        d = self.check()
        self.assertEqual(d["rejected_event_like_lines"], 1)
        self.assertEqual(d["nvme_irq_event_counts"]["pci_nvme_irq_msix"], 0)

    def test_reject_bad_event_message(self):
        self.trace.write_text("123@1.1:pci_nvme_irq_msix delivered to AIC\n")
        self.assertEqual(self.check()["rejected_event_like_lines"], 1)

    def test_warning_unattributed(self):
        self.stderr.write_text("qemu: warning: MSI-X is not supported by interrupt controller\n")
        d = self.check()
        self.assertEqual(d["unattributed_msix_unsupported_warnings"], 1)
        self.assertEqual(d["msix_init_return_value"], "UNKNOWN")

    def test_binary_mismatch_rejected(self):
        with self.assertRaisesRegex(m.InvalidEvidence, "binary_sha256_mismatch"):
            m.inspect(self.binary, "0" * 64, self.trace, self.stderr, self.events, m.PINNED_QEMU, m.BASELINE_MAIN)

    def test_wrong_source_commit_rejected(self):
        with self.assertRaisesRegex(m.InvalidEvidence, "source_or_product_commit_mismatch"):
            m.inspect(self.binary, self.digest, self.trace, self.stderr, self.events, "0" * 40, m.BASELINE_MAIN)

    def test_missing_trace_event_rejected(self):
        self.events.write_text("pci_nvme_irq_msix\n", encoding="utf-8")
        with self.assertRaisesRegex(m.InvalidEvidence, "required_nvme_trace_events_not_enabled"):
            self.check()

    def test_disabled_trace_event_rejected(self):
        self.events.write_text("pci_nvme_irq_msix\npci_nvme_irq_pin\n-pci_nvme_irq_masked\n", encoding="utf-8")
        with self.assertRaisesRegex(m.InvalidEvidence, "required_nvme_trace_events_not_enabled"):
            self.check()

    def test_later_disabled_trace_event_rejected(self):
        self.events.write_text("\n".join(m.EVENT_TEXT) + "\n-pci_nvme_irq_pin\n", encoding="utf-8")
        with self.assertRaisesRegex(m.InvalidEvidence, "required_nvme_trace_events_not_enabled"):
            self.check()

    def test_bad_utf8_rejected(self):
        self.trace.write_bytes(b"\xff\xfe")
        with self.assertRaisesRegex(m.InvalidEvidence, "non_utf8_trace"):
            self.check()

    def test_log_over_size_rejected(self):
        with self.trace.open("wb") as f:
            f.truncate(m.MAX_LOG_BYTES + 1)
        with self.assertRaisesRegex(m.InvalidEvidence, "file_too_large"):
            self.check()

    def test_cli_no_trace_returns_2(self):
        args = ["--qemu-binary", str(self.binary), "--expected-binary-sha256", self.digest,
                "--trace-log", str(self.trace), "--stderr-log", str(self.stderr),
                "--trace-events", str(self.events), "--qemu-source-commit", m.PINNED_QEMU,
                "--product-main-commit", m.BASELINE_MAIN]
        self.assertEqual(m.main(args), 2)

    def test_cli_invalid_returns_3(self):
        self.assertEqual(m.main(["--qemu-binary", str(self.binary),
                "--expected-binary-sha256", "0" * 64,
                "--trace-log", str(self.trace), "--stderr-log", str(self.stderr),
                "--trace-events", str(self.events), "--qemu-source-commit", m.PINNED_QEMU,
                "--product-main-commit", m.BASELINE_MAIN]), 3)

    def test_json_serializable(self):
        self.assertIn('"full_ios_stage1_proven": false', json.dumps(self.check()))


if __name__ == "__main__":
    unittest.main()
