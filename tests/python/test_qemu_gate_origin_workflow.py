"""Static contract tests for QEMU gate-origin producer and consumer wiring.

Host-only: these tests do not run Windows Actions or an iOS guest.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / '.github/workflows/qemu-sptm-windows.yml'
CONSUMER = ROOT / '.github/workflows/windows-e2e.yml'


def _steps(path: Path, job: str) -> list[dict]:
    workflow = yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
    return workflow['jobs'][job]['steps']


def _step(steps: list[dict], name: str) -> dict:
    matches = [s for s in steps if s.get('name') == name]
    if len(matches) != 1:
        raise AssertionError(f'exactly one {name!r} required; got {len(matches)}')
    return matches[0]


class QemuGateOriginWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.producer = _steps(PRODUCER, 'build-qemu')
        cls.consumer = _steps(CONSUMER, 'boot-proof')

    def test_producer_writes_before_artifact_upload(self):
        names = [s['name'] for s in self.producer]
        self.assertLess(names.index('Stage standalone QEMU runtime'), names.index('Record QEMU gate job origin'))
        self.assertLess(names.index('Verify standalone QEMU runtime'), names.index('Record QEMU gate job origin'))
        self.assertLess(names.index('Record QEMU gate job origin'), names.index('Upload proof artifact'))

    def test_producer_uses_same_run_identity_and_checkout(self):
        body = _step(self.producer, 'Record QEMU gate job origin')['run']
        for term in ('$env:GITHUB_RUN_ID', '$env:GITHUB_SHA', 'git rev-parse HEAD', '$checkedOutSha -cne $headSha'):
            self.assertIn(term, body)
        self.assertIn('TryParse', body)
        self.assertIn("'^[0-9a-f]{40}$'", body)

    def test_producer_reads_real_pinned_upstream(self):
        body = _step(self.producer, 'Record QEMU gate job origin')['run']
        self.assertIn('git -C qemu-sptm rev-parse HEAD', body)
        self.assertIn('2867d847d3471560e773120ee50c42dbcbb6d60b', body)
        self.assertIn('Get-FileHash -LiteralPath $binary -Algorithm SHA256', body)
        self.assertIn('qemu-proof/runtime/qemu-system-aarch64.exe', body)

    def test_producer_receipt_exact_keys_ascii_lf(self):
        body = _step(self.producer, 'Record QEMU gate job origin')['run']
        keys = re.findall(r'"(GATE_RUN_ID|GATE_SHA|QEMU_UPSTREAM_SHA|QEMU_RUNTIME_SHA256)=', body)
        self.assertEqual(keys, ['GATE_RUN_ID', 'GATE_SHA', 'QEMU_UPSTREAM_SHA', 'QEMU_RUNTIME_SHA256'])
        self.assertIn('[Text.Encoding]::ASCII.GetBytes(($lines -join "`n") + "`n")', body)
        self.assertIn('[IO.File]::WriteAllBytes($receipt, $asciiLf)', body)
        self.assertNotIn('Set-Content', body)

    def test_producer_refuses_overwrite_or_linked_binary(self):
        body = _step(self.producer, 'Record QEMU gate job origin')['run']
        self.assertIn('Test-Path -LiteralPath $receipt', body)
        self.assertIn('[IO.FileAttributes]::ReparsePoint', body)

    def test_producer_upload_contains_origin_receipt(self):
        upload = _step(self.producer, 'Upload proof artifact')
        self.assertEqual(upload['with']['name'], 'qemu-sptm-windows-gate')
        self.assertEqual(upload['with']['path'], 'qemu-proof/**')
        self.assertIn("'qemu-proof/gate-origin.txt'", _step(self.producer, 'Record QEMU gate job origin')['run'])

    def test_consumer_download_then_verify_then_stage(self):
        names = [s['name'] for s in self.consumer]
        self.assertLess(names.index('Download QEMU runtime from gate'), names.index('Verify downloaded QEMU gate origin'))
        self.assertLess(names.index('Setup Python for QEMU gate origin verification'), names.index('Verify downloaded QEMU gate origin'))
        self.assertLess(names.index('Verify downloaded QEMU gate origin'), names.index('Stage tested QEMU runtime'))

    def test_consumer_verifies_actual_downloaded_binary(self):
        step = _step(self.consumer, 'Verify downloaded QEMU gate origin')
        body = step['run']
        self.assertIn('scripts/check_qemu_gate_origin.py', body)
        self.assertIn('--receipt qemu-gate-artifact/gate-origin.txt', body)
        self.assertIn('--binary qemu-gate-artifact/runtime/qemu-system-aarch64.exe', body)
        self.assertIn('--output e2e-evidence/qemu-gate-origin-check.json', body)
        self.assertIn('if ($LASTEXITCODE -ne 0)', body)
        self.assertIn('[IO.FileAttributes]::ReparsePoint', body)

    def test_consumer_identity_bound_to_same_workflow_run(self):
        consumer = _step(self.consumer, 'Verify downloaded QEMU gate origin')
        self.assertEqual(consumer['env']['EXPECTED_GATE_RUN'], '${{ steps.qemu.outputs.run_id }}')
        self.assertEqual(consumer['env']['EXPECTED_GATE_SHA'], '${{ steps.qemu.outputs.head_sha }}')
        self.assertIn('--expected-run-id $env:EXPECTED_GATE_RUN', consumer['run'])
        self.assertIn('--expected-sha $env:EXPECTED_GATE_SHA', consumer['run'])
        qemu = _step(self.consumer, 'Bind QEMU gate to current workflow run')['run']
        self.assertIn('github.run_id', qemu)
        self.assertIn('github.sha', qemu)

    def test_consumer_verifies_staged_executable_again(self):
        stage = _step(self.consumer, 'Stage tested QEMU runtime')
        body = stage['run']
        self.assertIn('scripts/check_qemu_gate_origin.py', body)
        self.assertIn('--binary (Join-Path $destination "qemu-system-aarch64.exe")', body)
        self.assertIn('--output e2e-evidence/qemu-gate-staged-origin-check.json', body)
        self.assertLess(body.index('Copy-Item (Join-Path $source "*")'), body.index('scripts/check_qemu_gate_origin.py'))
        self.assertLess(body.index('scripts/check_qemu_gate_origin.py'), body.index('qemu-system-aarch64.exe") -M help'))

    def test_workflow_source_change_triggers_e2e_gate(self):
        workflow = yaml.load(CONSUMER.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
        paths = workflow['on']['push']['paths']
        self.assertIn('.github/workflows/windows-e2e.yml', paths)
        self.assertIn('.github/workflows/qemu-sptm-windows.yml', paths)
        self.assertIn('scripts/check_qemu_gate_origin.py', paths)

    def test_consumer_does_not_promote_host_receipt_to_guest_proof(self):
        body = _step(self.consumer, 'Verify downloaded QEMU gate origin')['run']
        self.assertNotIn('STAGE1_ACCEPTED', body)
        self.assertNotIn('GUEST_IOKIT_BINDING_PROVEN', body)
        source = (ROOT / 'scripts/check_qemu_gate_origin.py').read_text(encoding='utf-8')
        self.assertIn('"stage1_accepted": False', source)
        self.assertIn('SELF_REPORTED_HASH_MATCHED_NOT_CRYPTOGRAPHICALLY_ATTESTED', source)


if __name__ == '__main__':
    unittest.main()
