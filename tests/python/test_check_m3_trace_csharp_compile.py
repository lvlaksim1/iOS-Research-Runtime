"""Source integrity and fail-closed tests; no .NET compiler in this environment."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/check_m3_trace_csharp_compile.py"
spec = importlib.util.spec_from_file_location("csharp_gate", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)


class CompileGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ROOT

    def invoke(self, root: Path, *, plan_only: bool, dotnet: str = "nonexistent-dotnet-pp-rm"):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = mod.run(root, dotnet, plan_only, 10)
        return code, json.loads(buffer.getvalue())

    def test_verified_source_identity(self):
        sources = mod.read_exact_sources(self.root)
        self.assertEqual(set(sources), {"QemuCommandBuilder.cs", "QemuNvmeTraceOptIn.cs", "RuntimeLayout.cs"})
        self.assertEqual(mod.git_blob_sha1(sources["RuntimeLayout.cs"]), mod.LAYOUT_BLOB)

    def test_plan_only_never_compiles(self):
        code, record = self.invoke(self.root, plan_only=True)
        self.assertEqual(code, 0)
        self.assertEqual(record["status"], "PLAN_ONLY_NO_CSHARP_COMPILATION")
        self.assertEqual(len(record["sources"]), 3)

    def test_no_dotnet_does_not_claim_compile(self):
        code, record = self.invoke(self.root, plan_only=False)
        self.assertEqual(code, 2)
        self.assertEqual(record["status"], "NOT_RUN_DOTNET_UNAVAILABLE")

    def test_rejects_mutated_builder(self):
        self.assert_mutation_rejected("QemuCommandBuilder.cs")

    def test_rejects_mutated_optin(self):
        self.assert_mutation_rejected("QemuNvmeTraceOptIn.cs")

    def test_rejects_mutated_layout(self):
        self.assert_mutation_rejected("RuntimeLayout.cs")

    def assert_mutation_rejected(self, name: str):
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            for source_name, (relative, _) in mod.SOURCES.items():
                dest = temp_root / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, dest)
            layout = temp_root / mod.LAYOUT_PATH
            layout.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / mod.LAYOUT_PATH, layout)
            relative = mod.LAYOUT_PATH if name == "RuntimeLayout.cs" else mod.SOURCES[name][0]
            changed = temp_root / relative
            changed.write_bytes(changed.read_bytes() + b"\n// changed\n")
            code, record = self.invoke(temp_root, plan_only=True)
            self.assertEqual(code, 3)
            self.assertEqual(record["status"], "INVALID_SOURCE")

    def test_isolated_project_only_three_sources(self):
        self.assertEqual(mod.PROJECT.count('<Compile Include="src/'), 3)
        self.assertIn("<TargetFramework>net8.0</TargetFramework>", mod.PROJECT)
        self.assertIn("<EnableDefaultCompileItems>false</EnableDefaultCompileItems>", mod.PROJECT)
        self.assertNotIn("<Exec", mod.PROJECT)

    def test_offline_restore_and_no_implicit_network(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"--source", str(work / "offline-feed")', source)
        self.assertIn('"--no-restore"', source)
        self.assertNotIn("dotnet new", source)
        self.assertNotIn("git clone", source)

    def test_invalid_timeout_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as invalid_zero:
                mod.main(["--source-root", str(ROOT), "--timeout", "0"])
            with self.assertRaises(SystemExit) as invalid_high:
                mod.main(["--source-root", str(ROOT), "--timeout", "601"])
        self.assertEqual(invalid_zero.exception.code, 2)
        self.assertEqual(invalid_high.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
