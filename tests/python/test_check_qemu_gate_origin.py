"""Synthetic host-only tests: no QEMU guest execution or stage1 claim."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_qemu_gate_origin import UPSTREAM_PIN, verify

RUN = "38711142120"
SHA = "a" * 40
DATA = b"synthetic qemu executable bytes\x00\xff"


class GateOriginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.binary = self.root / "qemu-system-aarch64.exe"
        self.binary.write_bytes(DATA)
        self.receipt = self.root / "gate-origin.txt"
        self.write_receipt()

    def write_receipt(self, *, run=RUN, sha=SHA, upstream=UPSTREAM_PIN, digest=None, raw=None):
        if raw is None:
            raw = (f"GATE_RUN_ID={run}\nGATE_SHA={sha}\nQEMU_UPSTREAM_SHA={upstream}\n"
                   f"QEMU_RUNTIME_SHA256={digest or hashlib.sha256(DATA).hexdigest()}\n").encode("ascii")
        self.receipt.write_bytes(raw)

    def check(self):
        return verify(self.receipt, self.binary, expected_run_id=RUN, expected_sha=SHA)

    def test_valid_receipt_and_binary(self):
        result = self.check()
        self.assertEqual(result["qemu_runtime_sha256"], hashlib.sha256(DATA).hexdigest())
        self.assertEqual(result["gate_job_attestation"], "SELF_REPORTED_HASH_MATCHED_NOT_CRYPTOGRAPHICALLY_ATTESTED")
        self.assertIs(result["stage1_accepted"], False)
        self.assertEqual(result["guest_iokit_binding"], "UNPROVEN")

    def test_run_mismatch(self):
        self.write_receipt(run="38711142121")
        with self.assertRaises(ValueError): self.check()

    def test_sha_mismatch(self):
        self.write_receipt(sha="b" * 40)
        with self.assertRaises(ValueError): self.check()

    def test_upstream_mismatch(self):
        self.write_receipt(upstream="c" * 40)
        with self.assertRaises(ValueError): self.check()

    def test_binary_mismatch(self):
        self.binary.write_bytes(DATA + b"changed")
        with self.assertRaises(ValueError): self.check()

    def test_digest_invalid(self):
        self.write_receipt(digest="A" * 64)
        with self.assertRaises(ValueError): self.check()

    def test_missing_receipt(self):
        self.receipt.unlink()
        with self.assertRaises(OSError): self.check()

    def test_missing_binary(self):
        self.binary.unlink()
        with self.assertRaises(OSError): self.check()

    def test_empty_binary(self):
        self.binary.write_bytes(b"")
        with self.assertRaises(ValueError): self.check()

    def test_duplicate_key(self):
        self.receipt.write_bytes(self.receipt.read_bytes() + b"GATE_SHA=" + SHA.encode() + b"\n")
        with self.assertRaises(ValueError): self.check()

    def test_reordered_keys(self):
        lines = self.receipt.read_bytes().splitlines(keepends=True)
        self.receipt.write_bytes(b"".join([lines[1], lines[0], *lines[2:]]))
        with self.assertRaises(ValueError): self.check()

    def test_crlf(self):
        self.receipt.write_bytes(self.receipt.read_bytes().replace(b"\n", b"\r\n"))
        with self.assertRaises(ValueError): self.check()

    def test_non_ascii(self):
        self.receipt.write_bytes(self.receipt.read_bytes() + b"\xff")
        with self.assertRaises(ValueError): self.check()

    def test_oversized(self):
        self.receipt.write_bytes(b"x" * 513)
        with self.assertRaises(ValueError): self.check()

    def test_no_final_newline(self):
        self.receipt.write_bytes(self.receipt.read_bytes().rstrip(b"\n"))
        with self.assertRaises(ValueError): self.check()

    def test_invalid_expected_run_even_with_valid_receipt(self):
        with self.assertRaises(ValueError):
            verify(self.receipt, self.binary, expected_run_id="0", expected_sha=SHA)

    def test_invalid_expected_sha_even_with_valid_receipt(self):
        with self.assertRaises(ValueError):
            verify(self.receipt, self.binary, expected_run_id=RUN, expected_sha="A" * 40)

    def test_receipt_symlink(self):
        target = self.root / "target"
        target.write_bytes(self.receipt.read_bytes())
        self.receipt.unlink()
        try: self.receipt.symlink_to(target)
        except (OSError, NotImplementedError): self.skipTest("symlink not supported")
        with self.assertRaises(ValueError): self.check()

    def test_binary_symlink(self):
        target = self.root / "target"
        target.write_bytes(DATA)
        self.binary.unlink()
        try: self.binary.symlink_to(target)
        except (OSError, NotImplementedError): self.skipTest("symlink not supported")
        with self.assertRaises(ValueError): self.check()

    def test_cli_writes_bounded_json(self):
        output = self.root / "summary.json"
        p = subprocess.run([sys.executable, str(ROOT / "scripts/check_qemu_gate_origin.py"),
            "--receipt", str(self.receipt), "--binary", str(self.binary),
            "--expected-run-id", RUN, "--expected-sha", SHA,
            "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(json.loads(output.read_text())["stage1_accepted"])

    def test_cli_rejects_mismatch_without_output(self):
        output = self.root / "summary.json"
        self.binary.write_bytes(b"changed")
        p = subprocess.run([sys.executable, str(ROOT / "scripts/check_qemu_gate_origin.py"),
            "--receipt", str(self.receipt), "--binary", str(self.binary),
            "--expected-run-id", RUN, "--expected-sha", SHA,
            "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(output.exists())

    def test_cli_rejects_overwrite(self):
        output = self.root / "summary.json"
        output.write_text("prior")
        p = subprocess.run([sys.executable, str(ROOT / "scripts/check_qemu_gate_origin.py"),
            "--receipt", str(self.receipt), "--binary", str(self.binary),
            "--expected-run-id", RUN, "--expected-sha", SHA,
            "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(output.read_text(), "prior")


if __name__ == "__main__": unittest.main()
