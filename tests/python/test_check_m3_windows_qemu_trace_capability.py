"""Synthetic unit tests; these never execute a real QEMU or a guest."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_m3_windows_qemu_trace_capability.py"
spec = importlib.util.spec_from_file_location("qemu_gate", SCRIPT)
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gate)


class TestTraceCapability(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "qemu-system-aarch64.exe"
        self.binary.write_bytes(b"fake-QEMU-binary-synthetic-only")
        (self.root / "meson-info").mkdir()
        self.options = self.root / "meson-info" / "intro-buildoptions.json"
        self.options.write_text(json.dumps([{"name": "trace_backends", "value": ["log"]}]), encoding="utf-8")
        self.header = self.root / "config-host.h"
        self.header.write_text("#define CONFIG_TRACE_LOG 1\n", encoding="utf-8")
        self.trace_text = "\n".join(gate.EVENTS) + "\n"
        self.machine_text = "Supported machines are:\ndarwin Apple Darwin machine\n"

    def runner(self, args, **kwargs):
        if args[1:] == ["-trace", "help"]:
            return subprocess.CompletedProcess(args, 0, self.trace_text.encode(), b"")
        if args[1:] == ["-M", "help"]:
            return subprocess.CompletedProcess(args, 0, self.machine_text.encode(), b"")
        raise AssertionError(args)

    def check(self, **kwargs):
        return gate.run_gate(self.root, self.binary, runner=self.runner, **kwargs)

    def test_pass_is_catalog_only(self):
        r = self.check()
        self.assertEqual(r["catalog_capability"], "VERIFIED_FOR_THIS_BINARY_SHA256")
        self.assertEqual(r["runtime_irq_emission"], "NOT_OBSERVED")
        self.assertEqual(r["full_ios_system_boot"], "NOT_PROVEN")
        self.assertEqual(len(r["binary_sha256"]), 64)

    def test_exact_expected_sha(self):
        r = self.check(expected_sha256=gate.sha256_file(self.binary))
        self.assertTrue(r["binary_sha256_matches_expected"])

    def test_mismatched_expected_sha_fails(self):
        r = self.check(expected_sha256="0" * 64)
        self.assertIn("BINARY_SHA256_MISMATCH", r["reasons"])

    def test_event_substring_not_accepted(self):
        self.trace_text = "prefix_pci_nvme_irq_msix_suffix\n" + "\n".join(gate.EVENTS[1:])
        r = self.check()
        self.assertFalse(r["registered_nvme_irq_trace_events"]["pci_nvme_irq_msix"])

    def test_missing_event_fails(self):
        self.trace_text = "\n".join(gate.EVENTS[:2])
        self.assertIn("NVME_IRQ_TRACE_EVENTS_MISSING", self.check()["reasons"])

    def test_nonlog_meson_fails(self):
        self.options.write_text(json.dumps([{"name": "trace_backends", "value": ["nop"]}]))
        self.assertIn("MESON_LOG_BACKEND_NOT_VERIFIED", self.check()["reasons"])

    def test_missing_config_define_fails(self):
        self.header.write_text("/* CONFIG_TRACE_LOG absent */\n")
        self.assertIn("CONFIG_TRACE_LOG_NOT_DEFINED", self.check()["reasons"])

    def test_missing_meson_file_fails(self):
        self.options.unlink()
        self.assertIn("MESON_BUILD_OPTIONS_UNREADABLE", self.check()["reasons"])

    def test_duplicate_trace_backend_option_fails(self):
        self.options.write_text(json.dumps([{"name": "trace_backends", "value": ["log"]}] * 2))
        self.assertIn("MESON_LOG_BACKEND_NOT_VERIFIED", self.check()["reasons"])

    def test_machine_absent_fails(self):
        self.machine_text = "virt QEMU virt machine\n"
        self.assertIn("DARWIN_MACHINE_NOT_LISTED", self.check()["reasons"])

    def test_nonzero_command_fails(self):
        def failing(args, **kwargs):
            return subprocess.CompletedProcess(args, 1, b"", b"error")
        r = gate.run_gate(self.root, self.binary, runner=failing)
        self.assertIn("TRACE_COMMAND_EXIT_1", r["reasons"])
        self.assertIn("MACHINE_COMMAND_EXIT_1", r["reasons"])

    def test_timeout_fails(self):
        def timeout(args, **kwargs):
            raise subprocess.TimeoutExpired(args, 20)
        r = gate.run_gate(self.root, self.binary, runner=timeout)
        self.assertIn("TRACE_COMMAND_UNAVAILABLE_TimeoutExpired", r["reasons"])

    def test_external_binary_fails(self):
        other = self.root / "outside"
        other.mkdir()
        path = other / "qemu-system-aarch64.exe"
        path.write_bytes(b"synthetic")
        r = gate.run_gate(self.root, path, runner=self.runner)
        self.assertEqual(r["reasons"], ["BINARY_NOT_IN_BUILD_ROOT"])

    def test_missing_binary_fails(self):
        self.binary.unlink()
        self.assertEqual(self.check()["reasons"], ["BINARY_NOT_IN_BUILD_ROOT"])

    def test_oversized_output_fails(self):
        self.trace_text = "x" * (gate.MAX_CAPTURE_BYTES + 1)
        self.assertIn("TRACE_OUTPUT_TOO_LARGE", self.check()["reasons"])

    def test_event_listing_parser_ignores_noise(self):
        r = gate.parse_trace_catalog("trace: pci_nvme_irq_msix\n" + "\n".join(gate.EVENTS[1:]))
        self.assertFalse(r["pci_nvme_irq_msix"])


if __name__ == "__main__":
    unittest.main()
