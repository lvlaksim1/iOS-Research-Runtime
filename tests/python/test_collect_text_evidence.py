"""Host-only fail-closed text-evidence tests; no guest or Windows CI claim."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/collect_text_evidence.py"
spec = importlib.util.spec_from_file_location("collect_text_evidence", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TextEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "logs"
        self.source.mkdir()
        self.destination = self.base / "out" / "boot-logs"
        self.status = self.base / "out" / "text-evidence-copy-status.txt"

    def put(self, name: str, data: bytes) -> Path:
        p = self.source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def run_collect(self):
        return module.collect(self.source, self.destination, self.status)

    def test_safe_nested_utf8_files_are_copied_exactly(self):
        self.put("boot/run.log", "PCIe device: обнаружен\n".encode())
        self.put("events.json", b'{"device":"NVMe"}\n')
        copied, size, skipped = self.run_collect()
        self.assertEqual((copied, skipped), (2, 0))
        self.assertEqual(size, len("PCIe device: обнаружен\n".encode()) + len(b'{"device":"NVMe"}\n'))
        self.assertEqual((self.destination / "boot/run.log").read_bytes(), "PCIe device: обнаружен\n".encode())
        self.assertIn("TEXT_EVIDENCE_OK", self.status.read_text())

    def test_raw_and_arbitrary_binary_extensions_never_copy(self):
        for name in ("dtree.raw", "DeviceTree.txt", "firmware.bin", "backup.zip", "private.pem", "dtree.log"):
            self.put(name, b"printable but forbidden")
        self.assertEqual(self.run_collect(), (0, 0, 6))
        self.assertFalse(list(self.destination.rglob("*")))

    def test_binary_disguised_as_log_rejected(self):
        self.put("binary.log", b"abc\x00def")
        self.put("control.txt", b"abc\x1b[31m")
        self.put("invalid.json", b"\xff\xfe")
        self.assertEqual(self.run_collect(), (0, 0, 3))

    def test_utf8_bom_and_tabs_are_accepted(self):
        self.put("report.csv", b"\xef\xbb\xbfcol\tvalue\r\n")
        self.assertEqual(self.run_collect(), (1, 14, 0))

    def test_hidden_names_and_dirs_are_excluded(self):
        self.put(".env", b"TOKEN=secret")
        self.put(".private/hidden.log", b"secret")
        self.put("ordinary.log", b"ok")
        self.assertEqual(self.run_collect(), (1, 2, 2))

    def test_oversized_log_is_excluded(self):
        self.put("big.log", b"x" * (module.MAX_FILE_BYTES + 1))
        self.assertEqual(self.run_collect(), (0, 0, 1))

    def test_total_byte_budget_enforced(self):
        for i in range(5):
            self.put(f"{i}.log", b"a" * module.MAX_FILE_BYTES)
        copied, size, skipped = self.run_collect()
        self.assertEqual((copied, size, skipped), (4, module.MAX_TOTAL_BYTES, 1))

    def test_file_count_budget_enforced(self):
        for i in range(module.MAX_FILES + 3):
            self.put(f"{i:03}.log", b"x")
        self.assertEqual(self.run_collect(), (module.MAX_FILES, module.MAX_FILES, 3))

    def test_symlinked_file_and_directory_are_skipped(self):
        outside = self.base / "outside.log"
        outside.write_text("private", encoding="utf-8")
        try:
            (self.source / "alias.log").symlink_to(outside)
            (self.source / "linked").symlink_to(self.base, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        self.put("good.log", b"good")
        self.assertEqual(self.run_collect(), (1, 4, 2))

    def test_existing_destination_is_not_overwritten(self):
        self.put("safe.log", b"new")
        self.destination.mkdir(parents=True)
        (self.destination / "safe.log").write_bytes(b"old")
        self.assertEqual(self.run_collect(), (0, 0, 1))
        self.assertEqual((self.destination / "safe.log").read_bytes(), b"old")

    def test_missing_source_is_explicit_not_success_evidence(self):
        self.source.rmdir()
        self.assertEqual(self.run_collect(), (0, 0, 0))
        self.assertEqual(self.status.read_text(), "LOG_DIRECTORY_NOT_AVAILABLE\n")

    def test_symlink_source_is_rejected(self):
        other = self.base / "other"
        other.mkdir()
        self.source.rmdir()
        try:
            self.source.symlink_to(other, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        with self.assertRaises(ValueError):
            self.run_collect()

    def test_existing_nested_destination_symlink_cannot_write_outside(self):
        self.put("nested/ok.log", b"SENTINEL")
        outside = self.base / "outside"
        outside.mkdir()
        self.destination.mkdir(parents=True)
        try:
            (self.destination / "nested").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        with self.assertRaises(ValueError):
            self.run_collect()
        self.assertFalse((outside / "ok.log").exists())

    def test_destination_parent_symlink_cannot_write_outside(self):
        self.put("ok.log", b"SENTINEL")
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.base / "out").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        with self.assertRaises(ValueError):
            self.run_collect()
        self.assertFalse((outside / "boot-logs" / "ok.log").exists())

    def test_status_parent_symlink_is_rejected(self):
        self.put("ok.log", b"SENTINEL")
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.base / "out").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        status = self.base / "out" / "evil.log"
        with self.assertRaises(ValueError):
            module.collect(self.source, self.base / "clean", status)
        self.assertFalse((outside / "evil.log").exists())

    def test_status_symlink_cannot_overwrite_outside(self):
        self.put("ok.log", b"SENTINEL")
        self.status.parent.mkdir(parents=True)
        outside = self.base / "outside.txt"
        outside.write_bytes(b"UNCHANGED")
        try:
            self.status.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        with self.assertRaises(ValueError):
            self.run_collect()
        self.assertEqual(outside.read_bytes(), b"UNCHANGED")

    def test_junction_marker_in_existing_destination_ancestor_rejected(self):
        self.put("nested/ok.log", b"SENTINEL")
        self.destination.mkdir(parents=True)
        (self.destination / "nested").mkdir()
        original = getattr(os.path, "isjunction", lambda _p: False)
        def fake_isjunction(path):
            return Path(path) == self.destination / "nested" or original(path)
        with patch.object(os.path, "isjunction", fake_isjunction, create=True):
            with self.assertRaises(ValueError):
                self.run_collect()
        self.assertFalse((self.destination / "nested" / "ok.log").exists())

    def test_source_ancestor_symlink_is_rejected(self):
        outside = self.base / "outside"
        (outside / "logs").mkdir(parents=True)
        (outside / "logs" / "ok.log").write_bytes(b"SENTINEL")
        try:
            (self.base / "linked").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unsupported")
        with self.assertRaises(ValueError):
            module.collect(self.base / "linked" / "logs", self.destination, self.status)

    def test_destination_inside_source_rejected(self):
        with self.assertRaises(ValueError):
            module.collect(self.source, self.source / "out", self.status)

    def test_cli_fails_closed_and_records_failure(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source / "missing.log"),
                                 "--destination", str(self.destination), "--status", str(self.status)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.status.read_text(), "LOG_DIRECTORY_NOT_AVAILABLE\n")
        self.status.unlink()
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source / "notdir"),
                                 "--destination", str(self.destination), "--status", str(self.status)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.status.read_text(), "LOG_DIRECTORY_NOT_AVAILABLE\n")
        self.put("bad.log", b"hi")
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", str(self.source / "bad.log"),
                                 "--destination", str(self.destination), "--status", str(self.status)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.status.read_text(), "TEXT_EVIDENCE_FAILED\n")


if __name__ == "__main__":
    unittest.main()
