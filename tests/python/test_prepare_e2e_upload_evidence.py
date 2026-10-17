"""Synthetic-only tests: no Windows runner, guest, or CI evidence implied."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from prepare_e2e_upload_evidence import prepare as _prepare


def prepare(source, destination, *, expected_run_id="123456", expected_sha="b" * 40):
    return _prepare(source, destination, expected_run_id=expected_run_id, expected_sha=expected_sha)


def sample_native():
    return {
        "schema": 1, "source": "exact_native_adt_bytes", "input_sha256": "a" * 64,
        "input_size_bytes": 4096, "apcie_path": "/device/apcie", "apcie_properties": {},
        "apcie_ports_u32_le": None, "bridge_nodes": [{"path": "/secret/name"}],
        "qemu_root_port_to_apple_ports_mapping": "UNPROVEN", "guest_iokit_binding": "UNPROVEN",
        "stage1_accepted": False,
    }


class PrepareE2EUploadEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "e2e-evidence"
        self.source.mkdir()
        self.destination = self.root / "e2e-upload"

    def gate_check(self, *, staged=False, **overrides):
        receipt = {
            "schema": 1,
            "purpose": "host_only_qemu_gate_origin_check",
            "gate_run_id": "123456",
            "gate_sha": "b" * 40,
            "qemu_upstream_sha": "2867d847d3471560e773120ee50c42dbcbb6d60b",
            "qemu_runtime_sha256": "d" * 64,
            "qemu_runtime_size_bytes": 1024,
            "gate_job_attestation": "SELF_REPORTED_HASH_MATCHED_NOT_CRYPTOGRAPHICALLY_ATTESTED",
            "guest_iokit_binding": "UNPROVEN",
            "stage1_accepted": False,
        }
        receipt.update(overrides)
        name = "qemu-gate-staged-origin-check.json" if staged else "qemu-gate-origin-check.json"
        (self.source / name).write_text(json.dumps(receipt) + "\n", encoding="ascii")
        return self.source / name

    def test_gate_origin_two_stage_host_only_digest_summary(self):
        self.revisions()
        self.gate_check()
        self.gate_check(staged=True)
        result = prepare(self.source, self.destination)
        self.assertEqual(result["qemu_gate_origin"]["status"], "HOST_ONLY_TWO_STAGE_HASH_MATCHED")
        self.assertEqual(result["qemu_gate_origin"]["qemu_runtime_sha256"], "d" * 64)
        self.assertEqual(result["qemu_gate_origin"]["qemu_runtime_size_bytes"], 1024)
        self.assertEqual(result["qemu_gate_origin"]["guest_iokit_binding"], "UNPROVEN")
        self.assertFalse(result["stage1_accepted"])
        self.assertFalse(result["qemu_gate_origin"]["stage1_accepted"])
        self.assertEqual(sorted(p.name for p in self.destination.iterdir()), ["evidence-files.txt", "evidence-summary.json"])
        text = (self.destination / "evidence-summary.json").read_text()
        self.assertNotIn('"purpose": "host_only_qemu_gate_origin_check"', text)
        self.assertNotIn('"gate_run_id"', text)

    def test_gate_origin_only_pre_stage_is_explicitly_partial(self):
        self.revisions()
        self.gate_check()
        result = prepare(self.source, self.destination)
        self.assertEqual(result["qemu_gate_origin"]["status"], "HOST_ONLY_PRE_STAGE_ONLY")
        self.assertFalse(result["stage1_accepted"])

    def test_gate_origin_missing_is_not_claimed(self):
        self.revisions()
        result = prepare(self.source, self.destination)
        self.assertEqual(result["qemu_gate_origin"]["status"], "NOT_AVAILABLE")
        self.assertIsNone(result["qemu_gate_origin"]["qemu_runtime_sha256"])

    def test_staged_without_downloaded_rejected(self):
        self.revisions()
        self.gate_check(staged=True)
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_gate_origin_without_revisions_rejected(self):
        self.gate_check()
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_gate_origin_mismatched_staged_digest_rejected(self):
        self.revisions()
        self.gate_check()
        self.gate_check(staged=True, qemu_runtime_sha256="e" * 64)
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_gate_origin_mismatched_staged_size_rejected(self):
        self.revisions()
        self.gate_check()
        self.gate_check(staged=True, qemu_runtime_size_bytes=1025)
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_gate_origin_identity_and_upstream_mismatch_rejected(self):
        for key, value in (("gate_run_id", "123457"), ("gate_sha", "c" * 40),
                           ("qemu_upstream_sha", "c" * 40)):
            with self.subTest(key=key):
                self.revisions()
                path = self.gate_check(**{key: value})
                with self.assertRaises(ValueError): prepare(self.source, self.destination)
                path.unlink()

    def test_gate_origin_false_boot_or_attestation_claim_rejected(self):
        for key, value in (("stage1_accepted", True), ("guest_iokit_binding", "PROVEN"),
                           ("gate_job_attestation", "CRYPTOGRAPHICALLY_ATTESTED"),
                           ("purpose", "guest_boot_evidence")):
            with self.subTest(key=key):
                self.revisions()
                path = self.gate_check(**{key: value})
                with self.assertRaises(ValueError): prepare(self.source, self.destination)
                path.unlink()

    def test_gate_origin_invalid_runtime_size_rejected(self):
        for size in (0, -1, True, 1.5, 512 * 1024 * 1024 + 1):
            with self.subTest(size=size):
                self.revisions()
                path = self.gate_check(qemu_runtime_size_bytes=size)
                with self.assertRaises(ValueError): prepare(self.source, self.destination)
                path.unlink()

    def test_gate_origin_invalid_digest_rejected(self):
        for digest in ("D" * 64, "d" * 63, "g" * 64, None):
            with self.subTest(digest=digest):
                self.revisions()
                path = self.gate_check(qemu_runtime_sha256=digest)
                with self.assertRaises(ValueError): prepare(self.source, self.destination)
                path.unlink()

    def test_gate_origin_duplicate_and_unknown_keys_rejected(self):
        self.revisions()
        path = self.gate_check()
        raw = path.read_text()
        path.write_text(raw.replace('"schema": 1', '"schema": 1, "schema": 1'))
        with self.assertRaises(ValueError): prepare(self.source, self.destination)
        self.gate_check(unexpected_key="no")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_gate_origin_nonfinite_and_oversize_rejected(self):
        self.revisions()
        path = self.gate_check()
        path.write_text(path.read_text().replace('"qemu_runtime_size_bytes": 1024', '"qemu_runtime_size_bytes": NaN'))
        with self.assertRaises(ValueError): prepare(self.source, self.destination)
        path.write_bytes(b"x" * 2049)
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_gate_origin_symlink_rejected(self):
        self.revisions()
        other = self.root / "outside.json"
        other.write_text("SECRET")
        try: os.symlink(other, self.source / "qemu-gate-origin-check.json")
        except OSError: self.skipTest("symlinks unavailable")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_no_raw_logs_and_no_absolute_paths(self):
        (self.source / "integration.log").write_text("SECRET=not_for_upload\n", encoding="utf-8")
        (self.source / "runtime-summary.txt").write_text("password=hidden\n", encoding="utf-8")
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        (self.source / "text-evidence-copy-status.txt").write_text("TEXT_EVIDENCE_OK files=1 bytes=12 skipped=0\n")
        (self.source / "native-apcie-properties.json").write_text(json.dumps(sample_native()))
        result = prepare(self.source, self.destination)
        self.assertIsNone(result["native_apcie"]["apcie_ports_u32_le"])
        self.assertEqual(result["native_apcie"]["bridge_count"], 1)
        self.assertEqual(sorted(p.name for p in self.destination.iterdir()), ["evidence-files.txt", "evidence-summary.json"])
        output = b"".join(p.read_bytes() for p in self.destination.iterdir())
        for forbidden in (b"SECRET=", b"password=", b"/secret/name", str(self.root).encode()):
            self.assertNotIn(forbidden, output)
        self.assertIn(b"integration.log\t", output)

    def revisions(self, run="123456", sha="b" * 40):
        (self.source / "revisions.txt").write_text(
            f"QEMU_GATE_RUN={run}\nQEMU_GATE_SHA={sha}\nAPPLICATION_SHA={sha}\n"
            "QEMU_GATE_MODE=SAME_RUN_REUSABLE_WORKFLOW\n"
            "QEMU_UPSTREAM_SHA=2867d847d3471560e773120ee50c42dbcbb6d60b\n",
            encoding="utf-8",
        )

    def test_exact_same_run_provenance_is_uploaded_without_raw_file(self):
        self.revisions()
        result = prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)
        self.assertEqual(result["tested_revisions"]["qemu_gate_run_id"], "123456")
        self.assertEqual(result["tested_revisions"]["qemu_gate_sha"], "b" * 40)
        self.assertEqual(result["tested_revisions"]["application_sha"], "b" * 40)
        self.assertEqual(result["tested_revisions"]["qemu_gate_attestation"], "SELF_REPORTED_UNVERIFIED")
        self.assertNotIn(b"QEMU_GATE_RUN=", (self.destination / "evidence-summary.json").read_bytes())
        self.assertIn(b"revisions.txt\t", (self.destination / "evidence-files.txt").read_bytes())
        self.assertEqual(len(list(self.destination.iterdir())), 2)

    def test_missing_revision_receipt_is_explicit_null(self):
        result = prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)
        self.assertIsNone(result["tested_revisions"])

    def test_missing_receipt_rejects_missing_expected_identity(self):
        for run, sha in ((None, "b" * 40), ("123456", None), (None, None)):
            with self.subTest(run=run, sha=sha), self.assertRaises(ValueError):
                _prepare(self.source, self.destination, expected_run_id=run, expected_sha=sha)
        self.assertFalse(self.destination.exists())

    def test_missing_receipt_rejects_invalid_expected_run(self):
        for run in ("0", "01", "-1", "abc", "9223372036854775808", "9" * 20, 123456, True):
            with self.subTest(run=run), self.assertRaises(ValueError):
                _prepare(self.source, self.destination, expected_run_id=run, expected_sha="b" * 40)
        self.assertFalse(self.destination.exists())

    def test_missing_receipt_rejects_invalid_expected_sha(self):
        for sha in ("A" * 40, "g" * 40, "b" * 39, "b" * 41, "", 123, None):
            with self.subTest(sha=sha), self.assertRaises(ValueError):
                _prepare(self.source, self.destination, expected_run_id="123456", expected_sha=sha)
        self.assertFalse(self.destination.exists())

    def test_missing_receipt_valid_identity_is_explicit_null_not_attested(self):
        result = _prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)
        self.assertIsNone(result["tested_revisions"])
        self.assertFalse(result["stage1_accepted"])

    def test_powershell_crlf_utf8_bom_and_no_bom(self):
        for bom in (False, True):
            with self.subTest(bom=bom):
                self.revisions()
                path = self.source / "revisions.txt"
                data = path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8")
                if bom:
                    data = b"\xef\xbb\xbf" + data
                path.write_bytes(data)
                destination = self.root / ("with-bom" if bom else "without-bom")
                result = _prepare(self.source, destination, expected_run_id="123456", expected_sha="b" * 40)
                self.assertEqual(result["tested_revisions"]["qemu_gate_attestation"], "SELF_REPORTED_UNVERIFIED")
                self.assertFalse(result["stage1_accepted"])

    def test_revision_requires_expected_run_and_sha(self):
        self.revisions()
        with self.assertRaises(ValueError): _prepare(self.source, self.destination)

    def test_wrong_run_id_rejected(self):
        self.revisions()
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123457", expected_sha="b" * 40)

    def test_wrong_application_sha_rejected(self):
        self.revisions()
        p = self.source / "revisions.txt"
        p.write_text(p.read_text().replace("APPLICATION_SHA=" + "b" * 40, "APPLICATION_SHA=" + "c" * 40))
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)

    def test_duplicate_or_extra_revision_rejected(self):
        self.revisions()
        with (self.source / "revisions.txt").open("a") as f: f.write("APPLICATION_SHA=" + "b" * 40 + "\n")
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)

    def test_revision_upstream_pin_mismatch_rejected(self):
        self.revisions()
        p = self.source / "revisions.txt"
        p.write_text(p.read_text().replace("2867d847d3471560e773120ee50c42dbcbb6d60b", "c" * 40))
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)

    def test_revision_oversized_rejected(self):
        (self.source / "revisions.txt").write_bytes(b"X" * 513)
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)

    def test_revision_symlink_rejected(self):
        outside = self.root / "private.txt"; outside.write_text("secret")
        try: os.symlink(outside, self.source / "revisions.txt")
        except OSError: self.skipTest("symlink creation not permitted")
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)

    def test_invalid_gate_mode_rejected(self):
        self.revisions()
        p = self.source / "revisions.txt"
        p.write_text(p.read_text().replace("SAME_RUN_REUSABLE_WORKFLOW", "UNVERIFIED"))
        with self.assertRaises(ValueError): prepare(self.source, self.destination, expected_run_id="123456", expected_sha="b" * 40)

    def test_missing_evidence_is_safe(self):
        result = prepare(self.source, self.destination)
        self.assertEqual(result["capture_status"], "NOT_AVAILABLE")
        self.assertIsNone(result["native_apcie"])

    def test_native_ports_are_preserved_only_if_observed(self):
        value = sample_native();value["apcie_ports_u32_le"] = 7
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        (self.source / "native-apcie-properties.json").write_text(json.dumps(value))
        self.assertEqual(prepare(self.source, self.destination)["native_apcie"]["apcie_ports_u32_le"], 7)

    def test_native_claim_of_boot_is_rejected(self):
        value = sample_native();value["stage1_accepted"] = True
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        (self.source / "native-apcie-properties.json").write_text(json.dumps(value))
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_native_bool_ports_is_rejected(self):
        value = sample_native();value["apcie_ports_u32_le"] = True
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        (self.source / "native-apcie-properties.json").write_text(json.dumps(value))
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_native_json_missing_with_success_status_is_rejected(self):
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_unexpected_status_is_rejected(self):
        (self.source / "text-evidence-copy-status.txt").write_text("SECRET=should_never_copy\n")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_oversized_status_is_rejected(self):
        (self.source / "native-apcie-capture-status.txt").write_bytes(b"X" * 257)
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_source_symlink_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        linked = self.root / "linked"
        try: os.symlink(self.source, linked, target_is_directory=True)
        except OSError: self.skipTest("symlink creation not permitted")
        with self.assertRaises(ValueError): prepare(linked, self.destination)

    def test_input_symlink_is_rejected(self):
        other = self.root / "private.txt";other.write_text("SECRET")
        try: os.symlink(other, self.source / "integration.log")
        except OSError: self.skipTest("symlink creation not permitted")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_destination_symlink_is_rejected(self):
        other = self.root / "outside";other.mkdir()
        try: os.symlink(other, self.destination, target_is_directory=True)
        except OSError: self.skipTest("symlink creation not permitted")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)
        self.assertEqual(list(other.iterdir()), [])

    def test_existing_output_not_overwritten(self):
        self.destination.mkdir();p=self.destination / "evidence-summary.json";p.write_text("ORIGINAL")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)
        self.assertEqual(p.read_text(), "ORIGINAL")

    def test_nested_destination_under_source_rejected(self):
        with self.assertRaises(ValueError): prepare(self.source, self.source / "upload")

    def test_status_counts_bounds(self):
        (self.source / "text-evidence-copy-status.txt").write_text("TEXT_EVIDENCE_OK files=65 bytes=1 skipped=0")
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_absolute_path_inventory_input_is_ignored(self):
        (self.source / "evidence-files.txt").write_text("C:\\Users\\runner\\secret.txt 2048\n")
        prepare(self.source, self.destination)
        result = (self.destination / "evidence-files.txt").read_text()
        self.assertNotIn("C:", result)
        self.assertNotIn("secret.txt", result)

    def test_duplicate_native_json_key_rejected(self):
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        value = json.dumps(sample_native()).replace('"schema": 1', '"schema": 1, "schema": 1')
        (self.source / "native-apcie-properties.json").write_text(value)
        with self.assertRaises(ValueError): prepare(self.source, self.destination)

    def test_broken_source_symlink_rejected(self):
        try: os.symlink(self.root / "missing", self.root / "broken", target_is_directory=True)
        except OSError: self.skipTest("symlink creation not permitted")
        with self.assertRaises(ValueError): prepare(self.root / "broken", self.destination)

    def test_native_nonfinite_rejected(self):
        (self.source / "native-apcie-capture-status.txt").write_text("CAPTURE_OK_TEXT_ONLY\n")
        (self.source / "native-apcie-properties.json").write_text(json.dumps(sample_native()).replace('"input_size_bytes": 4096', '"input_size_bytes": NaN'))
        with self.assertRaises(ValueError): prepare(self.source, self.destination)


if __name__ == "__main__": unittest.main()
