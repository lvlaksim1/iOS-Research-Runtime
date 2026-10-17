"""Offline synthetic tests for the ioprint tar-mode preflight."""

from __future__ import annotations

import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_m3_ioprint_tar_mode.py"
SPEC = importlib.util.spec_from_file_location("check_m3_ioprint_tar_mode", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IoprintArchiveModeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "tools.tar.gz"

    def build(self, entries):
        with tarfile.open(self.archive, "w:gz") as archive:
            for name, mode, kind in entries:
                info = tarfile.TarInfo(name)
                info.mode = mode
                info.uid = 0
                info.gid = 0
                if kind == "file":
                    data = b"synthetic-test-only"
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
                elif kind == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "somewhere"
                    archive.addfile(info)
                elif kind == "hardlink":
                    info.type = tarfile.LNKTYPE
                    info.linkname = "somewhere"
                    archive.addfile(info)
                elif kind == "directory":
                    info.type = tarfile.DIRTYPE
                    archive.addfile(info)
                else:
                    raise AssertionError(kind)

    def test_exact_0755_regular_file_passes(self):
        self.build([(MODULE.ENTRY, 0o755, "file")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_dot_slash_prefix_passes(self):
        self.build([("./" + MODULE.ENTRY, 0o755, "file")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_windows_0666_fails(self):
        self.build([(MODULE.ENTRY, 0o666, "file")])
        result = MODULE.audit_archive(self.archive)
        self.assertEqual(result["status"], "EXEC_MODE_INVALID")
        self.assertEqual(result["observed_mode"], "0666")

    def test_0644_fails(self):
        self.build([(MODULE.ENTRY, 0o644, "file")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "EXEC_MODE_INVALID")

    def test_0775_fails_closed(self):
        self.build([(MODULE.ENTRY, 0o775, "file")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "EXEC_MODE_INVALID")

    def test_setuid_fails_closed(self):
        self.build([(MODULE.ENTRY, 0o4755, "file")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "EXEC_MODE_INVALID")

    def test_missing_entry_fails(self):
        self.build([("sysroot/other", 0o755, "file")])
        result = MODULE.audit_archive(self.archive)
        self.assertEqual((result["status"], result["count"]), ("ENTRY_COUNT_INVALID", 0))

    def test_duplicate_entry_fails(self):
        self.build([(MODULE.ENTRY, 0o755, "file"), (MODULE.ENTRY, 0o755, "file")])
        result = MODULE.audit_archive(self.archive)
        self.assertEqual((result["status"], result["count"]), ("ENTRY_COUNT_INVALID", 2))

    def test_symlink_fails(self):
        self.build([(MODULE.ENTRY, 0o755, "symlink")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ENTRY_NOT_REGULAR_FILE")

    def test_hardlink_fails(self):
        self.build([(MODULE.ENTRY, 0o755, "hardlink")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ENTRY_NOT_REGULAR_FILE")

    def test_directory_fails(self):
        self.build([(MODULE.ENTRY, 0o755, "directory")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ENTRY_NOT_REGULAR_FILE")

    def test_wrong_path_fails(self):
        self.build([("/" + MODULE.ENTRY, 0o755, "file")])
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ENTRY_COUNT_INVALID")

    def test_unreadable_archive_fails(self):
        self.archive.write_bytes(b"not-a-tar-archive")
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ARCHIVE_UNREADABLE")

    def test_nonexistent_archive_fails(self):
        self.assertEqual(MODULE.audit_archive(self.archive)["status"], "ARCHIVE_UNREADABLE")

    def test_cli_pass_exit_zero_and_json(self):
        self.build([(MODULE.ENTRY, 0o755, "file")])
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = MODULE.main([str(self.archive)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_cli_fail_exit_two_and_json(self):
        self.build([(MODULE.ENTRY, 0o666, "file")])
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = MODULE.main([str(self.archive)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stdout.getvalue())["status"], "EXEC_MODE_INVALID")


if __name__ == "__main__":
    unittest.main()
