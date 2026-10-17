"""Static Windows integration contract plus synthetic tar round-trip.

This is NOT a C# build, a Windows runtime test, or an iOS guest execution proof.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = ROOT / "tools/IOSResearchRuntime.Integration/Program.cs"
FIXER = ROOT / "scripts/fix_m3_ioprint_tar_mode.py"
GATE = ROOT / "scripts/check_m3_ioprint_tar_mode.py"
ENTRY = "sysroot/usr/local/bin/ioprint"
FIXER_SHA = "3cf0aae8c4d006c137ae98a61a71c4b6317f674c50dccfd56dcc2cb2564ae3a0"
GATE_SHA = "cd60562732f2ddc5d2ed4f63a78f6f588368d2048bce03660462c85f078560dd"


class WindowsIntegrationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = PROGRAM.read_text(encoding="utf-8")

    def test_pinned_source_scripts_match_exact_parent_bytes(self):
        self.assertEqual(hashlib.sha256(FIXER.read_bytes()).hexdigest(), FIXER_SHA)
        self.assertEqual(hashlib.sha256(GATE.read_bytes()).hexdigest(), GATE_SHA)

    def test_mode_repair_and_gate_precede_archive_replacement(self):
        source = self.program
        names = [
            "var repackResult = await processRunner.RunAsync(",
            "var ioprintRepairResult = await processRunner.RunAsync(",
            "var ioprintGateResult = await processRunner.RunAsync(",
            "var archiveModeEvidence = await processRunner.RunAsync(",
            "File.Move(repackedSysroot, layout.IosCliToolsArchive, overwrite: true);",
        ]
        positions = [source.index(name) for name in names]
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(all(source.count(name) == 1 for name in names))

    def test_missing_or_mutated_script_fails_closed(self):
        source = self.program
        self.assertIn('throw new FileNotFoundException("Pinned ioprint archive-mode script is missing."', source)
        self.assertIn('throw new InvalidDataException($"Pinned ioprint script hash mismatch:', source)
        self.assertIn('SHA256.HashData(scriptStream)', source)
        self.assertIn(FIXER_SHA, source)
        self.assertIn(GATE_SHA, source)

    def test_nonzero_and_invalid_json_status_fails_closed(self):
        source = self.program
        for needle in (
            "if (ioprintRepairResult.ExitCode != 0)",
            "if (ioprintGateResult.ExitCode != 0)",
            "JsonDocument.Parse(ioprintRepairResult.StandardOutput)",
            "JsonDocument.Parse(ioprintGateResult.StandardOutput)",
            'repairMode != "0755"',
            'repairStatus != "ARCHIVE_EXEC_MODE_REPAIRED"',
            'repairStatus != "ALREADY_CORRECT"',
            'GetProperty("status").GetString() != "ARCHIVE_EXEC_MODE_PASS"',
            'GetProperty("observed_mode").GetString() != "0755"',
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, source)

    def test_scripts_resolve_from_checkout_and_no_network(self):
        source = self.program
        self.assertIn('Environment.GetEnvironmentVariable("GITHUB_WORKSPACE")', source)
        self.assertIn('Path.Combine(scriptsRoot, "scripts", "fix_m3_ioprint_tar_mode.py")', source)
        self.assertIn('Path.Combine(scriptsRoot, "scripts", "check_m3_ioprint_tar_mode.py")', source)
        self.assertIn('new[] { "-B", ioprintRepairScript, repackedSysroot }', source)
        self.assertIn('new[] { "-B", ioprintGateScript, repackedSysroot }', source)

    def test_missing_pinned_ioprint_is_a_hard_failure(self):
        source = self.program
        self.assertIn('if (pinnedIoprint is null)', source)
        self.assertIn('throw new FileNotFoundException(', source)
        self.assertIn('Pinned ioprint executable was not found with the required SHA-256', source)
        self.assertLess(source.index('if (pinnedIoprint is null)'),
                        source.index('if (pinnedIoprint is not null)'))

    def test_tar_extraction_is_fail_closed(self):
        source = self.program
        self.assertIn('var extractionResult = await processRunner.RunAsync(', source)
        self.assertIn('if (extractionResult.ExitCode != 0)', source)
        self.assertIn('Extracting iOS CLI tools failed with exit code', source)
        self.assertIn('if (!Directory.Exists(Path.Combine(repackRoot, "sysroot")))', source)
        self.assertLess(source.index('if (extractionResult.ExitCode != 0)'),
                        source.index('File.Copy(pinnedIoprint.FullName, stagedIoprint'))

    def test_guest_proof_not_claimed_by_archive_gate(self):
        source = self.program
        self.assertIn("IOPRINT_TAR_MODE_GATE=", source)
        self.assertLess(source.index("IOPRINT_TAR_MODE_GATE="), source.index('Console.WriteLine("[integration] Boot start.")'))

    def test_synthetic_0666_to_0755_then_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            archive = Path(d) / "sample.tar.gz"
            with tarfile.open(archive, "w:gz") as tf:
                for name, content, mode in (
                    (ENTRY, b"fixture ioprint, not executable code", 0o666),
                    ("sysroot/keep.txt", b"unchanged", 0o644),
                ):
                    info = tarfile.TarInfo(name)
                    info.mode = mode
                    info.size = len(content)
                    tf.addfile(info, io.BytesIO(content))
            def run(script):
                completed = subprocess.run([sys.executable, "-B", str(script), str(archive)],
                                           capture_output=True, text=True, check=False)
                return completed.returncode, json.loads(completed.stdout)
            before, detail = run(GATE)
            self.assertEqual(before, 2)
            self.assertEqual(detail["status"], "EXEC_MODE_INVALID")
            changed, detail = run(FIXER)
            self.assertEqual(changed, 0)
            self.assertEqual(detail["status"], "ARCHIVE_EXEC_MODE_REPAIRED")
            passed, detail = run(GATE)
            self.assertEqual(passed, 0)
            self.assertEqual(detail["status"], "ARCHIVE_EXEC_MODE_PASS")
            second, detail = run(FIXER)
            self.assertEqual(second, 0)
            self.assertEqual(detail["status"], "ALREADY_CORRECT")
            with tarfile.open(archive, "r:gz") as tf:
                self.assertEqual(tf.getmember(ENTRY).mode & 0o7777, 0o755)
                self.assertEqual(tf.getmember("sysroot/keep.txt").mode & 0o7777, 0o644)
                self.assertEqual(tf.extractfile("sysroot/keep.txt").read(), b"unchanged")


if __name__ == "__main__":
    unittest.main()
