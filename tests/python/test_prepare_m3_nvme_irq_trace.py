"""Synthetic tests for the non-executing QEMU NVMe IRQ trace launch planner."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "prepare_m3_nvme_irq_trace.py"
spec = importlib.util.spec_from_file_location("m3_nvme_irq_trace_plan", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TracePreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "qemu-system-aarch64.exe"
        self.binary.write_bytes(b"synthetic qemu test fixture; NOT a real QEMU executable")
        self.expected = hashlib.sha256(self.binary.read_bytes()).hexdigest()
        self.events = self.root / "events.txt"
        self.stderr = self.root / "boot.stderr.log"
        self.plan = self.root / "plan.json"

    def params(self):
        return dict(qemu_binary=self.binary, expected_binary_sha256=self.expected,
                    qemu_source_commit=module.PINNED_QEMU,
                    product_main_commit=module.BASELINE_MAIN,
                    trace_events=self.events, stderr_log=self.stderr,
                    output_plan=self.plan)

    def test_valid_plan_exact_three_events(self):
        result = module.prepare(**self.params())
        self.assertEqual(result["status"], "PLAN_PREPARED_NOT_EXECUTED")
        self.assertEqual(self.events.read_bytes(), module.EVENT_FILE_BYTES)
        plan = json.loads(self.plan.read_text())
        self.assertEqual(plan["qemu_trace_arguments"], ["-trace", f"events={self.events}"])
        self.assertEqual(plan["analyzer_command"].count(str(self.stderr)), 2)
        self.assertEqual(plan["expected_trace_backend"], "log")
        self.assertFalse(plan["trace_backend_runtime_verified"])
        self.assertFalse(plan["full_ios_stage1_proven"])
        self.assertFalse(self.stderr.exists())

    def test_repeated_exact_plan_reuses_without_rewrite(self):
        module.prepare(**self.params())
        second = module.prepare(**self.params())
        self.assertEqual(second["trace_events"], "REUSED_EXACT")
        self.assertEqual(second["plan"], "REUSED_EXACT")

    def test_wrong_qemu_sha_fails_before_file_writes(self):
        params = self.params()
        params["expected_binary_sha256"] = "0" * 64
        with self.assertRaisesRegex(module.InvalidPreparation, "qemu_binary_sha256_mismatch"):
            module.prepare(**params)
        self.assertFalse(self.events.exists())

    def test_bad_expected_sha_format(self):
        params = self.params()
        params["expected_binary_sha256"] = "ABCD"
        with self.assertRaisesRegex(module.InvalidPreparation, "invalid_expected_binary_sha256"):
            module.prepare(**params)

    def test_wrong_pinned_qemu_commit(self):
        params = self.params()
        params["qemu_source_commit"] = "0" * 40
        with self.assertRaisesRegex(module.InvalidPreparation, "source_or_product_commit_mismatch"):
            module.prepare(**params)

    def test_wrong_product_main_commit(self):
        params = self.params()
        params["product_main_commit"] = "f" * 40
        with self.assertRaisesRegex(module.InvalidPreparation, "source_or_product_commit_mismatch"):
            module.prepare(**params)

    def test_missing_binary(self):
        self.binary.unlink()
        with self.assertRaisesRegex(module.InvalidPreparation, "qemu_binary_missing_or_not_regular_file"):
            module.prepare(**self.params())

    def test_empty_binary(self):
        self.binary.write_bytes(b"")
        params = self.params()
        params["expected_binary_sha256"] = hashlib.sha256(b"").hexdigest()
        with self.assertRaisesRegex(module.InvalidPreparation, "qemu_binary_empty_or_exceeds_bounded_hash_limit"):
            module.prepare(**params)

    def test_conflicting_event_file_fails_closed(self):
        self.events.write_text("pci_nvme_irq_msix\n")
        with self.assertRaisesRegex(module.InvalidPreparation, "existing_trace_events_conflicts"):
            module.prepare(**self.params())
        self.assertFalse(self.plan.exists())

    def test_conflicting_plan_file_fails_without_creating_events(self):
        self.plan.write_text("{\"forged\":true}\n")
        with self.assertRaisesRegex(module.InvalidPreparation, "existing_output_plan_conflicts"):
            module.prepare(**self.params())
        self.assertFalse(self.events.exists())

    def test_comma_in_event_path_rejected(self):
        params = self.params()
        params["trace_events"] = self.root / "bad,events.txt"
        with self.assertRaisesRegex(module.InvalidPreparation, "unsafe_trace_events_path"):
            module.prepare(**params)

    def test_comma_in_stderr_path_rejected(self):
        params = self.params()
        params["stderr_log"] = self.root / "bad,stderr.log"
        with self.assertRaisesRegex(module.InvalidPreparation, "unsafe_stderr_log_path"):
            module.prepare(**params)

    def test_duplicate_paths_rejected(self):
        params = self.params()
        params["output_plan"] = self.events
        with self.assertRaisesRegex(module.InvalidPreparation, "paths_must_be_distinct"):
            module.prepare(**params)

    def test_binary_sha_is_actual_file_hash(self):
        module.prepare(**self.params())
        plan = json.loads(self.plan.read_text())
        self.assertEqual(plan["qemu_binary_sha256_verified"], self.expected)
        self.assertEqual(plan["qemu_binary_size"], self.binary.stat().st_size)

    def test_event_file_sha256_exact(self):
        module.prepare(**self.params())
        plan = json.loads(self.plan.read_text())
        self.assertEqual(plan["trace_event_file_sha256"], hashlib.sha256(self.events.read_bytes()).hexdigest())

    def test_cli_valid_and_no_guest_launch(self):
        args = [sys.executable, str(SCRIPT), "--qemu-binary", str(self.binary),
                "--expected-binary-sha256", self.expected,
                "--qemu-source-commit", module.PINNED_QEMU,
                "--product-main-commit", module.BASELINE_MAIN,
                "--trace-events", str(self.events),
                "--stderr-log", str(self.stderr), "--output-plan", str(self.plan)]
        proc = subprocess.run(args, text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["status"], "PLAN_PREPARED_NOT_EXECUTED")
        self.assertFalse(self.stderr.exists())

    def test_cli_invalid_exit_code(self):
        args = [sys.executable, str(SCRIPT), "--qemu-binary", str(self.binary),
                "--expected-binary-sha256", "f" * 64,
                "--qemu-source-commit", module.PINNED_QEMU,
                "--product-main-commit", module.BASELINE_MAIN,
                "--trace-events", str(self.events),
                "--stderr-log", str(self.stderr), "--output-plan", str(self.plan)]
        proc = subprocess.run(args, text=True, capture_output=True, check=False)
        self.assertEqual(proc.returncode, 3)
        self.assertEqual(json.loads(proc.stderr)["status"], "INVALID_PREPARATION")
        self.assertFalse(self.events.exists())

    def test_synthetic_only_never_claims_runtime_evidence(self):
        module.prepare(**self.params())
        plan = json.loads(self.plan.read_text())
        for key in ("guest_nvme_iokit_binding_proven", "aic_interrupt_delivery_proven",
                    "non_ramdisk_disk_proven", "full_ios_stage1_proven"):
            self.assertIs(plan[key], False)
        self.assertTrue(plan["plan_only_no_qemu_execution"])


if __name__ == "__main__":
    unittest.main()
