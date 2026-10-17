"""Static fail-closed cache/configuration provenance checks for Windows QEMU gate.

These tests validate workflow structure only; they do not prove a Windows
build, a QEMU runtime, guest PCIe/NVMe or a full iOS boot.
"""
from pathlib import Path
import unittest
import tempfile
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/qemu-sptm-windows.yml'
CACHE_KEY = "qemu-sptm-win64-2867d847-headless-v3-${{ hashFiles('runtime/qemu/patches/*.patch', '.github/workflows/qemu-sptm-windows.yml') }}"
UPSTREAM = '2867d847d3471560e773120ee50c42dbcbb6d60b'


class CacheProvenanceWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(WORKFLOW.read_text(encoding='utf-8'))
        cls.steps = cls.data['jobs']['build-qemu']['steps']
        cls.by_name = {step['name']: step for step in cls.steps}
        if len(cls.by_name) != len(cls.steps):
            raise AssertionError('Duplicate workflow step names')

    def test_exact_cache_key_uses_workflow_and_patches(self):
        restore = self.by_name['Restore QEMU build cache']
        self.assertEqual(restore['with']['key'], CACHE_KEY)
        self.assertNotIn('restore-keys', restore['with'])
        self.assertEqual(restore['id'], 'qemu-build-cache')
        self.assertEqual(restore['uses'], 'actions/cache/restore@v4')

    def test_cache_save_matches_restore_key(self):
        save = self.by_name['Save QEMU build cache']
        self.assertEqual(save['with']['key'], CACHE_KEY)
        self.assertEqual(save['uses'], 'actions/cache/save@v4')
        self.assertIn("steps.qemu-build-cache.outputs.cache-hit != 'true'", save['if'])

    def test_configure_fails_closed_on_cache_mismatch(self):
        configure = self.by_name['Configure qemu-sptm']['run']
        self.assertIn('if [ -f build.ninja ]; then', configure)
        self.assertIn('Unexpected build.ninja without an exact cache hit', configure)
        self.assertIn('Exact cache hit lacks config-host.h', configure)
        self.assertIn('Exact cache hit lacks build.ninja', configure)
        self.assertIn('steps.qemu-build-cache.outputs.cache-hit', configure)
        self.assertIn('../configure', configure)
        self.assertEqual(configure.count('exit 1'), 3)

    def _run_configure_case(self, hit, ninja=False, header=False):
        # Linux shell simulation of cache-branch control flow, not a QEMU build.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build = root / 'qemu-sptm' / 'build'
            build.mkdir(parents=True)
            if ninja:
                (build / 'build.ninja').write_text('rule test\n')
            if header:
                (build / 'config-host.h').write_text('#define TEST 1\n')
            fake = root / 'qemu-sptm' / 'configure'
            fake.write_text('#!/bin/sh\nprintf "rule test\\n" > build.ninja\nprintf "#define TEST 1\\n" > config-host.h\n')
            fake.chmod(0o755)
            script = self.by_name['Configure qemu-sptm']['run']
            script = script.replace('${{ steps.qemu-build-cache.outputs.cache-hit }}', hit)
            proc = subprocess.run(['bash', '-e', '-c', script], cwd=root,
                                  text=True, capture_output=True)
            return (proc.returncode, proc.stdout, proc.stderr,
                    (build / 'build.ninja').exists(), (build / 'config-host.h').exists())

    def test_configure_cache_miss_creates_fresh_files(self):
        rc, _, stderr, ninja, header = self._run_configure_case('false')
        self.assertEqual(rc, 0, stderr)
        self.assertTrue(ninja and header)

    def test_configure_exact_hit_with_complete_files(self):
        rc, _, stderr, ninja, header = self._run_configure_case('true', ninja=True, header=True)
        self.assertEqual(rc, 0, stderr)
        self.assertTrue(ninja and header)

    def test_configure_exact_hit_missing_header_fails(self):
        rc, _, stderr, _, _ = self._run_configure_case('true', ninja=True)
        self.assertNotEqual(rc, 0)
        self.assertIn('lacks config-host.h', stderr)

    def test_configure_exact_hit_missing_ninja_fails(self):
        rc, _, stderr, _, _ = self._run_configure_case('true')
        self.assertNotEqual(rc, 0)
        self.assertIn('lacks build.ninja', stderr)

    def test_configure_miss_with_stale_ninja_fails(self):
        rc, _, stderr, _, _ = self._run_configure_case('false', ninja=True)
        self.assertNotEqual(rc, 0)
        self.assertIn('Unexpected build.ninja', stderr)

    def test_provenance_requires_real_outputs_and_pinned_upstream(self):
        step = self.by_name['Record QEMU cache and build provenance']
        run = step['run']
        self.assertEqual(step['env']['QEMU_CACHE_KEY'], CACHE_KEY)
        self.assertIn('steps.qemu-build-cache.outputs.cache-hit', step['env']['QEMU_CACHE_HIT'])
        self.assertIn('set -euo pipefail', run)
        self.assertIn('test -f qemu-sptm/build/build.ninja', run)
        self.assertIn('test -f qemu-sptm/build/config-host.h', run)
        self.assertIn('test -f qemu-sptm/build/qemu-system-aarch64.exe', run)
        self.assertIn('git -C qemu-sptm rev-parse HEAD', run)
        self.assertIn(UPSTREAM, run)
        for path in ('build.ninja', 'config-host.h', 'qemu-system-aarch64.exe'):
            self.assertIn('qemu-sptm/build/' + path, run)
        self.assertIn('sha256sum ', run)
        self.assertIn('CACHE_HIT=', run)
        self.assertIn('CACHE_KEY=', run)
        self.assertIn('UPSTREAM_SHA=', run)

    def test_provenance_artifact_survives_failure(self):
        step = self.by_name['Upload QEMU cache and build provenance']
        self.assertEqual(step['if'], 'always()')
        self.assertEqual(step['uses'], 'actions/upload-artifact@v4')
        self.assertEqual(step['with']['name'], 'qemu-sptm-cache-config-provenance')
        self.assertEqual(step['with']['path'], 'qemu-proof/cache-config-provenance.txt')
        self.assertEqual(step['with']['if-no-files-found'], 'warn')

    def test_provenance_precedes_checker_and_cache_save(self):
        names = [step['name'] for step in self.steps]
        required = ['Restore QEMU build cache', 'Configure qemu-sptm',
                    'Build qemu-sptm', 'Record QEMU cache and build provenance',
                    'Upload QEMU cache and build provenance',
                    'Verify compiled QEMU NVMe IRQ trace capability',
                    'Save QEMU build cache']
        indices = [names.index(name) for name in required]
        self.assertEqual(indices, sorted(indices))

    def test_prior_header_artifact_is_preserved(self):
        step = self.by_name['Upload generated QEMU Meson configuration header']
        self.assertEqual(step['if'], 'always()')
        self.assertEqual(step['with']['path'], 'qemu-sptm/build/config-host.h')


if __name__ == '__main__':
    unittest.main()
