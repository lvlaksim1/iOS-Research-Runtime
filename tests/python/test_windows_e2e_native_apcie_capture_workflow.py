"""Static workflow contract for G141 native ADT evidence; not an iOS boot test."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/windows-e2e.yml"


class NativeApcieCaptureWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.workflow = yaml.safe_load(cls.text)
        cls.steps = cls.workflow["jobs"]["boot-proof"]["steps"]

    def step(self, name):
        matches = [s for s in self.steps if s.get("name") == name]
        self.assertEqual(len(matches), 1, name)
        return matches[0]

    def test_capture_runs_even_when_harness_fails(self):
        setup = self.step("Setup Python for native ADT evidence")
        collect = self.step("Collect failure evidence")
        self.assertEqual(str(setup["if"]), "always()")
        self.assertEqual(str(collect["if"]), "always()")
        self.assertEqual(setup["uses"], "actions/setup-python@v5")
        self.assertEqual(setup["with"]["python-version"], "3.13")
        self.assertLess(self.steps.index(setup), self.steps.index(collect))

    def test_source_and_exact_native_raw_path(self):
        run = self.step("Collect failure evidence")["run"]
        self.assertIn('$raw = Join-Path $logs "dtree.raw"', run)
        self.assertIn('scripts/capture_native_apcie_properties.py --input $raw --output $capture', run)
        self.assertIn('native-apcie-properties.json', run)
        self.assertIn('native-apcie-capture-status.txt', run)
        self.assertTrue((WORKFLOW.parents[2] / "scripts/capture_native_apcie_properties.py").is_file())

    def test_missing_or_failed_capture_is_not_reported_as_success(self):
        run = self.step("Collect failure evidence")["run"]
        self.assertIn('"RAW_ADT_NOT_AVAILABLE"', run)
        self.assertIn('"CAPTURE_FAILED"', run)
        self.assertIn('"CAPTURE_OK_TEXT_ONLY"', run)
        self.assertIn('if ($LASTEXITCODE -ne 0)', run)
        self.assertIn('Remove-Item -LiteralPath $capture -Force', run)
        self.assertIn('Test-Path -LiteralPath $capture -PathType Leaf', run)

    def test_json_is_bounded_and_raw_not_copied(self):
        run = self.step("Collect failure evidence")["run"]
        self.assertIn('Length -gt 65536', run)
        self.assertIn('scripts/collect_text_evidence.py --source $logs --destination $bootLogs --status $textStatus', run)
        self.assertIn('TEXT_EVIDENCE_FAILED', run)
        self.assertNotIn('Get-ChildItem -LiteralPath $logs -Recurse -File', run)
        self.assertNotRegex(run, r'Copy-Item\s+\$logs\s+')
        self.assertNotRegex(run, r'Copy-Item\s+\$raw\s+')

    def test_success_path_no_longer_copies_raw_logs(self):
        run = self.step("Run provisioning and Darwin root-shell proof")["run"]
        self.assertNotIn('Copy-Item $bootLogs', run)
        self.assertNotIn('Copy-Item (Join-Path $data "logs")', run)

    def test_upload_is_gated_on_minimized_evidence_only(self):
        prepare = self.step("Prepare minimized E2E upload")
        upload = self.step("Upload end-to-end evidence")
        self.assertEqual(str(prepare["if"]), "always()")
        self.assertEqual(prepare["id"], "prepare_upload")
        self.assertIn("scripts/prepare_e2e_upload_evidence.py --source e2e-evidence --destination e2e-upload", prepare["run"])
        self.assertLess(self.steps.index(prepare), self.steps.index(upload))
        self.assertIn('--expected-run-id "${{ github.run_id }}"', prepare["run"])
        self.assertIn('--expected-sha "${{ github.sha }}"', prepare["run"])
        self.assertEqual(str(upload["if"]), "always() && steps.prepare_upload.outcome == 'success'")
        paths = [p.strip() for p in upload["with"]["path"].splitlines() if p.strip()]
        self.assertEqual(paths, ["e2e-upload/evidence-summary.json", "e2e-upload/evidence-files.txt"])
        self.assertFalse(any("dtree.raw" in path.lower() or "devicetree." in path.lower() for path in paths))
        self.assertTrue((WORKFLOW.parents[2] / "scripts/prepare_e2e_upload_evidence.py").is_file())

    def test_qemu_runtime_not_reuploaded_in_e2e(self):
        self.step("Download QEMU runtime from gate")
        self.step("Stage tested QEMU runtime")
        self.assertFalse(any(s.get("name") == "Upload tested QEMU runtime" for s in self.steps))
        self.assertFalse(any(s.get("with", {}).get("name") == "qemu-runtime-tested" for s in self.steps))
        for step in self.steps:
            if step.get("uses", "").startswith("actions/upload-artifact"):
                self.assertNotIn("qemu-gate-artifact/runtime", str(step.get("with", {}).get("path", "")))

    def test_capture_only_change_does_not_trigger_e2e(self):
        # YAML 1.1 interprets "on" as boolean True; both forms are accepted here.
        events = self.workflow.get("on", self.workflow.get(True))
        paths = events["push"]["paths"]
        self.assertNotIn("scripts/capture_native_apcie_properties.py", paths)
        # Editing the workflow itself must trigger a check of its new wiring.
        self.assertIn(".github/workflows/windows-e2e.yml", paths)
        self.assertEqual(self.workflow["jobs"]["boot-proof"]["needs"], "qemu-gate")

    def test_evidence_helpers_are_explicit_push_triggers(self):
        events = self.workflow.get("on", self.workflow.get(True))
        self.assertEqual(events["push"]["branches"], ["main"])
        paths = events["push"]["paths"]
        for path in (
            "scripts/prepare_e2e_upload_evidence.py",
            "scripts/collect_text_evidence.py",
            "scripts/check_qemu_gate_origin.py",
            ".github/workflows/windows-e2e.yml",
        ):
            with self.subTest(path=path):
                self.assertEqual(paths.count(path), 1)
        self.assertNotIn("scripts/**", paths)
        self.assertNotIn("scripts/*", paths)

    def test_evidence_helpers_run_before_minimized_upload(self):
        collect = self.step("Collect failure evidence")
        prepare = self.step("Prepare minimized E2E upload")
        upload = self.step("Upload end-to-end evidence")
        self.assertIn("scripts/collect_text_evidence.py", collect["run"])
        self.assertIn("scripts/prepare_e2e_upload_evidence.py", prepare["run"])
        self.assertLess(self.steps.index(collect), self.steps.index(prepare))
        self.assertLess(self.steps.index(prepare), self.steps.index(upload))
        self.assertEqual(str(prepare["if"]), "always()")
        self.assertEqual(str(upload["if"]), "always() && steps.prepare_upload.outcome == 'success'")
        paths = [p.strip() for p in upload["with"]["path"].splitlines() if p.strip()]
        self.assertEqual(paths, ["e2e-upload/evidence-summary.json", "e2e-upload/evidence-files.txt"])
        self.assertFalse(any("raw" in path.lower() for path in paths))

    def test_evidence_only_does_not_claim_guest_binding(self):
        run = self.step("Collect failure evidence")["run"]
        self.assertNotIn('apcie-port =', run)
        self.assertNotIn('"#ports"', run)
        self.assertNotIn('stage1_accepted = true', run.lower())
        self.assertNotIn('git push', run)


if __name__ == "__main__":
    unittest.main()
