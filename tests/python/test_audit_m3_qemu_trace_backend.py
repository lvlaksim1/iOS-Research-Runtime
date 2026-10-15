import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / 'scripts/audit_m3_qemu_trace_backend.py'
spec = importlib.util.spec_from_file_location('audit_m3_qemu_trace_backend', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

WORKFLOW = '''uses: actions/cache/restore@v4
restore-keys: |
  qemu-win64-v2-
if [ ! -f build.ninja ]; then
  ../configure --target-list=aarch64-softmmu
fi
./qemu-system-aarch64.exe -M help
'''
OPTIONS = "option('trace_backends', type: 'array', value: ['log'], choices: ['log', 'nop'])"
MESON = "foreach k : get_option('trace_backends')\n  config_host_data.set('CONFIG_TRACE_' + k.to_upper(), true)\nendforeach"
EVENTS = '\n'.join(name + '(void) "event"' for name in mod.EVENTS)

class StaticAuditTests(unittest.TestCase):
    def result(self, w=WORKFLOW, o=OPTIONS, m=MESON, e=EVENTS):
        return mod.analyze(w, o, m, e)

    def test_default_log(self):
        self.assertTrue(self.result()['pinned_meson_default_log'])

    def test_meson_wiring(self):
        self.assertTrue(self.result()['meson_trace_backend_wiring'])

    def test_event_declarations(self):
        self.assertTrue(all(self.result()['nvme_irq_event_declarations'].values()))

    def test_cached_ninja_risk(self):
        self.assertIn('CACHED_BUILD_NINJA_CAN_BYPASS_RECONFIGURE', self.result()['unresolved'])

    def test_prefix_cache_risk(self):
        self.assertIn('CACHE_PREFIX_RESTORE_CAN_REUSE_PRIOR_CONFIGURATION', self.result()['unresolved'])

    def test_no_runtime_evidence(self):
        self.assertEqual('UNKNOWN', self.result()['compiled_windows_trace_backend'])
        self.assertEqual('NOT_PROVEN', self.result()['full_ios_system_boot'])

    def test_explicit_backend_override(self):
        self.assertTrue(self.result(w=WORKFLOW + '\n-Dtrace_backends=log\n')['workflow_explicit_backend_selection'])

    def test_runtime_trace_help(self):
        self.assertTrue(self.result(w=WORKFLOW + '\n./qemu-system-aarch64.exe -trace help\n')['workflow_runtime_trace_help_probe'])

    def test_missing_event(self):
        self.assertFalse(all(self.result(e=EVENTS.replace('pci_nvme_irq_pin', 'other'))['nvme_irq_event_declarations'].values()))

    def test_no_false_default(self):
        self.assertFalse(self.result(o="option('trace_backends', type: 'array', value: ['nop'])")['pinned_meson_default_log'])

    def test_cli_success_and_failure(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)
            for name, val in [('w',WORKFLOW),('o',OPTIONS),('m',MESON),('e',EVENTS)]: (d/name).write_text(val)
            cmd=[sys.executable,str(SRC),'--workflow',str(d/'w'),'--meson-options',str(d/'o'),'--meson-build',str(d/'m'),'--nvme-events',str(d/'e')]
            p=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(0,p.returncode,p.stderr)
            self.assertEqual('UNKNOWN',json.loads(p.stdout)['compiled_windows_trace_backend'])
            (d/'o').write_text('not a meson options file')
            p=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(2,p.returncode)

if __name__ == '__main__': unittest.main()
