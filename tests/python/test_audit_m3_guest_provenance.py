"""Synthetic source fixtures; never treated as guest runtime evidence."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "scripts" / "audit_m3_guest_provenance.py"
spec = importlib.util.spec_from_file_location("audit_m3_guest_provenance", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PROGRAM = '''
if (line.StartsWith("[proof] Диагностика завершена;", StringComparison.Ordinal)) { proofCompleted.TrySetResult(); }
if (line.StartsWith("bash-", StringComparison.Ordinal)) { bootProgress.TrySetResult(); }
if (string.Equals(line.Trim(), "__IOS_M3_PROVIDER_PROBE_END__", StringComparison.Ordinal)) { providerProbeCompleted.TrySetResult(); }
SHA256.HashData(stream)
await proofCompleted.Task.WaitAsync(rootShellFallback.Token);
Console.WriteLine("IOS-M3 read-only provider probe start");
"echo __IOS_M3_PROVIDER_PROBE_BEGIN__",
"echo __IOS_M3_PROVIDER_PROBE_END__"
"echo __IOS_M3_IOPRINT_SHA256_EXPECTED_123__"
"/usr/local/bin/ioprint -p IOService 2>&1 | grep -E -i -C 6"
Console.WriteLine("[integration] IOS-M3 read-only provider probe did not reach its terminal marker; continuing existing proof path.");
Console.WriteLine("BOOT_PROOF_OK");
await boundaryProbeCompleted.Task.WaitAsync(boundaryProbeTimeout.Token);
'''
WORKFLOW = 'name: Windows End-to-End Boot\n- name: Run provisioning and Darwin root-shell proof\nthrow "End-to-end integration harness failed with exit code $LASTEXITCODE"\n'


class TestProvenance(unittest.TestCase):
    def test_known_source_is_not_stage1(self):
        x = module.inspect(PROGRAM, WORKFLOW)
        self.assertTrue(x["source_contract_recognized"])
        self.assertFalse(x["interpretation"]["harness_success_proves_stage1"])
        self.assertFalse(x["interpretation"]["guest_iokit_provider_binding_proven"])

    def test_marker_not_equal_binding(self):
        x = module.inspect(PROGRAM, WORKFLOW)
        self.assertTrue(x["checks"]["provider_probe_completed_by_marker"])
        self.assertFalse(x["interpretation"]["guest_nvme_device_proven"])

    def test_no_guest_digest_check(self):
        x = module.inspect(PROGRAM, WORKFLOW)
        self.assertTrue(x["checks"]["guest_ioprint_digest_only_expected_echo"])
        self.assertFalse(x["interpretation"]["system_launchd_proven"])

    def test_nonfatal_provider_timeout(self):
        x = module.inspect(PROGRAM, WORKFLOW)
        self.assertTrue(x["checks"]["provider_probe_timeout_nonfatal"])
        self.assertFalse(x["interpretation"]["apfs_system_preboot_data_proven"])

    def test_missing_provider_end_fails_closed(self):
        x = module.inspect(PROGRAM.replace('"echo __IOS_M3_PROVIDER_PROBE_END__"', '"echo something_else"'), WORKFLOW)
        self.assertFalse(x["source_contract_recognized"])

    def test_missing_workflow_fails_closed(self):
        x = module.inspect(PROGRAM, "")
        self.assertFalse(x["source_contract_recognized"])

    def test_wrong_proof_order_fails_closed(self):
        x = module.inspect(PROGRAM.replace('Console.WriteLine("BOOT_PROOF_OK");', ''), WORKFLOW)
        self.assertFalse(x["source_contract_recognized"])

    def test_git_blob_hash(self):
        self.assertEqual(module.git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_cli_mismatched_blob_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p, w = Path(d)/"Program.cs", Path(d)/"windows-e2e.yml"
            p.write_text(PROGRAM)
            w.write_text(WORKFLOW)
            self.assertEqual(module.main(["--program", str(p), "--workflow", str(w), "--program-blob", "0"*40, "--workflow-blob", "0"*40, "--output", str(Path(d)/"out.json")]), 2)

    def test_cli_matching_synthetic_blobs(self):
        with tempfile.TemporaryDirectory() as d:
            p, w = Path(d)/"Program.cs", Path(d)/"windows-e2e.yml"
            p.write_text(PROGRAM)
            w.write_text(WORKFLOW)
            self.assertEqual(module.main(["--program", str(p), "--workflow", str(w), "--program-blob", module.git_blob_sha(p.read_bytes()), "--workflow-blob", module.git_blob_sha(w.read_bytes()), "--output", str(Path(d)/"out.json")]), 0)

if __name__ == "__main__":
    unittest.main()
