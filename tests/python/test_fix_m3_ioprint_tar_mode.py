"""Synthetic tar-only tests; not a guest boot or ioprint runtime test."""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from fix_m3_ioprint_tar_mode import ENTRY, repair_archive  # noqa: E402
from check_m3_ioprint_tar_mode import audit_archive  # noqa: E402


def make_tar(path: Path, *, mode: int = 0o666, duplicate: bool = False,
             link: bool = False, prefix: str = "", with_extra: bool = True) -> None:
    with tarfile.open(path, "w:gz" if path.suffix == ".gz" else "w:") as archive:
        if with_extra:
            other = tarfile.TarInfo("sysroot/etc/config.txt")
            data = b"unaltered-content\n"
            other.size = len(data)
            other.mode = 0o644
            other.uid = 12
            other.gid = 13
            archive.addfile(other, io.BytesIO(data))
        for _ in range(2 if duplicate else 1):
            member = tarfile.TarInfo(prefix + ENTRY)
            member.mode = mode
            member.uid = 42
            member.gid = 43
            member.mtime = 12345
            member.uname = "root"
            member.gname = "wheel"
            if link:
                member.type = tarfile.SYMTYPE
                member.linkname = "another-file"
                archive.addfile(member)
            else:
                data = b"pretend Mach-O bytes\x00\xff"
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))


class RepairModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "tools.tar.gz"

    def test_repairs_0666_and_gate_passes(self):
        make_tar(self.path)
        self.assertEqual(audit_archive(self.path)["status"], "EXEC_MODE_INVALID")
        self.assertEqual(repair_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_REPAIRED")
        self.assertEqual(audit_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_repair_0644(self):
        make_tar(self.path, mode=0o644)
        self.assertEqual(repair_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_REPAIRED")
        self.assertEqual(audit_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_repair_0775(self):
        make_tar(self.path, mode=0o775)
        self.assertEqual(repair_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_REPAIRED")
        self.assertEqual(audit_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_repair_setuid(self):
        make_tar(self.path, mode=0o4755)
        self.assertEqual(repair_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_REPAIRED")
        self.assertEqual(audit_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_already_correct_preserves_exact_archive_bytes(self):
        make_tar(self.path, mode=0o755)
        old = self.path.read_bytes()
        self.assertEqual(repair_archive(self.path)["status"], "ALREADY_CORRECT")
        self.assertEqual(old, self.path.read_bytes())

    def test_repair_preserves_non_target_and_target_bytes(self):
        make_tar(self.path)
        with tarfile.open(self.path) as z:
            before = [(m.name, m.uid, m.gid, m.uname, m.gname, m.mtime,
                       z.extractfile(m).read() if m.isfile() else None) for m in z]
        repair_archive(self.path)
        with tarfile.open(self.path) as z:
            after = [(m.name, m.uid, m.gid, m.uname, m.gname, m.mtime,
                      z.extractfile(m).read() if m.isfile() else None) for m in z]
        self.assertEqual(before, after)

    def test_prefix_dot_slash(self):
        make_tar(self.path, prefix="./")
        self.assertEqual(repair_archive(self.path)["status"], "ARCHIVE_EXEC_MODE_REPAIRED")

    def test_missing_entry_preserves_bytes(self):
        with tarfile.open(self.path, "w:gz") as z:
            info = tarfile.TarInfo("sysroot/etc/other")
            z.addfile(info, io.BytesIO(b""))
        old = self.path.read_bytes()
        self.assertEqual(repair_archive(self.path)["status"], "ENTRY_COUNT_INVALID")
        self.assertEqual(old, self.path.read_bytes())

    def test_duplicate_entry_preserves_bytes(self):
        make_tar(self.path, duplicate=True)
        old = self.path.read_bytes()
        self.assertEqual(repair_archive(self.path)["status"], "ENTRY_COUNT_INVALID")
        self.assertEqual(old, self.path.read_bytes())

    def test_symlink_preserves_bytes(self):
        make_tar(self.path, link=True)
        old = self.path.read_bytes()
        self.assertEqual(repair_archive(self.path)["status"], "ENTRY_NOT_REGULAR_FILE")
        self.assertEqual(old, self.path.read_bytes())

    def test_invalid_tar_preserves_bytes(self):
        self.path.write_bytes(b"not a tar")
        old = self.path.read_bytes()
        self.assertEqual(repair_archive(self.path)["status"], "REPAIR_FAILED")
        self.assertEqual(old, self.path.read_bytes())

    def test_unrecognized_extension_preserves_bytes(self):
        path = Path(self.tmp.name) / "tools.zip"
        make_tar(path)
        old = path.read_bytes()
        self.assertEqual(repair_archive(path)["status"], "UNSUPPORTED_ARCHIVE_EXTENSION")
        self.assertEqual(old, path.read_bytes())

    def test_uncompressed_tar(self):
        path = Path(self.tmp.name) / "tools.tar"
        make_tar(path)
        self.assertEqual(repair_archive(path)["status"], "ARCHIVE_EXEC_MODE_REPAIRED")
        self.assertEqual(audit_archive(path)["status"], "ARCHIVE_EXEC_MODE_PASS")

    def test_cli_exit_codes(self):
        make_tar(self.path)
        cmd = [sys.executable, str(ROOT / "scripts" / "fix_m3_ioprint_tar_mode.py"), str(self.path)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.path.write_bytes(b"broken")
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)

    def test_no_temp_files_after_success(self):
        make_tar(self.path)
        repair_archive(self.path)
        self.assertFalse(list(self.path.parent.glob(".m3-ioprint-*.tmp")))

    def test_no_temp_files_after_invalid_archive(self):
        self.path.write_bytes(b"invalid")
        repair_archive(self.path)
        self.assertFalse(list(self.path.parent.glob(".m3-ioprint-*.tmp")))


if __name__ == "__main__":
    unittest.main()
