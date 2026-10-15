"""Static/source contract checks only; not a substitute for C# compile or QEMU runtime."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "src/IOSResearchRuntime/Services/QemuCommandBuilder.cs"
OPTIN = ROOT / "src/IOSResearchRuntime/Services/QemuNvmeTraceOptIn.cs"
BASE_BLOB = "023ef24eba4a3c96aa53caf0e69142864a308451"
INSERTION = ("        // Explicit opt-in only. Default boot arguments and guest devices stay intact.\n"
             "        // Invalid plans fail before QEMU starts, rather than silently losing evidence.\n"
             "        arguments.AddRange(QemuNvmeTraceOptIn.GetArguments(_layout));\n")


class WiringSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = BUILDER.read_text(encoding="utf-8")
        cls.optin = OPTIN.read_text(encoding="utf-8")
        source = ROOT / "scripts/prepare_m3_nvme_irq_trace.py"
        spec = importlib.util.spec_from_file_location("gen43_planner", source)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        cls.planner = module

    def test_exact_baseline_builder_single_insertion(self):
        self.assertEqual(self.builder.count(INSERTION), 1)
        baseline = self.builder.replace(INSERTION, "")
        original = baseline.encode("utf-8")
        blob = hashlib.sha1(f"blob {len(original)}\0".encode("ascii") + original).hexdigest()
        self.assertEqual(blob, BASE_BLOB)

    def test_default_off_without_environment_variable(self):
        self.assertIn('Environment.GetEnvironmentVariable(EnvironmentVariable)', self.optin)
        self.assertIn('if (requestedPlan is null)', self.optin)
        self.assertIn('return Array.Empty<string>();', self.optin)
        self.assertEqual(self.builder.count('QemuNvmeTraceOptIn.GetArguments(_layout)'), 1)

    def test_no_guest_topology_or_boot_argument_mutation(self):
        self.assertIn('"-M", "darwin"', self.builder)
        self.assertIn('"-device", "nvme,drive=iosm3nvme,serial=IOSM3PROBE,bus=iosm3rp"', self.builder)
        self.assertIn('"-args", "rd=md0', self.builder)
        self.assertIn('"-serial", "stdio"', self.builder)

    def test_plan_and_identity_match_real_gen43_planner(self):
        self.assertIn('ios-m3-nvme-irq-trace-launch-plan-v1', self.optin)
        self.assertIn(self.planner.PINNED_QEMU, self.optin)
        self.assertIn(self.planner.BASELINE_MAIN, self.optin)
        self.assertIn('IOS_M3_NVME_IRQ_TRACE_PLAN', self.optin)

    def test_exact_trace_event_names(self):
        for event in self.planner.EVENTS:
            self.assertIn(event, self.optin)
        self.assertEqual(self.planner.EVENT_FILE_BYTES,
                         b'pci_nvme_irq_msix\npci_nvme_irq_pin\npci_nvme_irq_masked\n')

    def test_binary_is_rehashed_and_size_bounded(self):
        self.assertIn('SHA256.HashData(stream)', self.optin)
        self.assertIn('qemu_binary_sha256_verified', self.optin)
        self.assertIn('qemu_binary_size', self.optin)
        self.assertIn('MaxQemuBytes', self.optin)
        self.assertIn('qemu_binary_path_mismatch', self.optin)

    def test_events_are_byte_verified_not_just_named(self):
        self.assertIn('File.ReadAllBytes(eventPath).AsSpan().SequenceEqual(EventBytes)', self.optin)
        self.assertIn('trace_event_file_sha256', self.optin)
        self.assertIn('trace_event_file_content_mismatch', self.optin)

    def test_paths_fail_closed_and_are_confined(self):
        for part in ('Path.IsPathFullyQualified', 'Path.GetRelativePath',
                     'FileAttributes.ReparsePoint', 'RequireInsideDirectory(planPath',
                     'RequireInsideDirectory(eventPath', "'\\0'", "','"):
            self.assertIn(part, self.optin)

    def test_trace_argv_exact_two_elements(self):
        self.assertIn('arguments.GetArrayLength() != 2', self.optin)
        self.assertIn('arguments[0].GetString() != "-trace"', self.optin)
        self.assertIn('arguments[1].GetString() != $"events={eventPath}"', self.optin)
        self.assertIn('return new[] { "-trace", $"events={eventPath}" };', self.optin)

    def test_invalid_plan_rejects_instead_of_silent_fallback(self):
        self.assertIn('throw Invalid("plan_identity_or_backend_mismatch")', self.optin)
        self.assertIn('throw Invalid("qemu_binary_sha256_mismatch")', self.optin)
        self.assertIn('throw Invalid("qemu_trace_arguments_mismatch")', self.optin)

    def test_gen43_plan_compatibility_synthetic(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "qemu-synthetic.exe"
            binary.write_bytes(b"FAKE_QEMU_BINARY_NOT_EXECUTABLE")
            digest = hashlib.sha256(binary.read_bytes()).hexdigest()
            events = root / "logs" / "events.txt"
            stderr = root / "logs" / "boot.stderr.log"
            output = root / "logs" / "plan.json"
            receipt = self.planner.prepare(
                qemu_binary=binary, expected_binary_sha256=digest,
                qemu_source_commit=self.planner.PINNED_QEMU,
                product_main_commit=self.planner.BASELINE_MAIN,
                trace_events=events, stderr_log=stderr, output_plan=output)
            plan = json.loads(output.read_text())
            self.assertEqual(receipt['status'], 'PLAN_PREPARED_NOT_EXECUTED')
            self.assertEqual(plan['qemu_trace_arguments'], ['-trace', f'events={events.resolve()}'])
            self.assertEqual(events.read_bytes(), self.planner.EVENT_FILE_BYTES)
            self.assertEqual(plan['trace_event_file_sha256'], hashlib.sha256(events.read_bytes()).hexdigest())
            self.assertFalse(plan['full_ios_stage1_proven'])


if __name__ == '__main__':
    unittest.main()
