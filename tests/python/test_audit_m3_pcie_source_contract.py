"""Synthetic source fixtures; no claim of Apple guest runtime coverage."""
import importlib.util
import sys
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / 'scripts' / 'audit_m3_pcie_source_contract.py'
spec = importlib.util.spec_from_file_location('m3_static_audit', MODULE)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)

QEMU = '''DeviceState *pcie = qdev_new("gpex-pcihost");
object_property_set_int(OBJECT(pcie), "num-irqs", 0, &error_fatal);
const hwaddr pcie_mmio_base = 0x10000000;
const hwaddr pcie_mmio_size = 0x10000000;
const hwaddr pcie_ecam_base = 0x3f000000;
const hwaddr pcie_ecam_size = 0x01000000;'''
ADT = '''private static void AddPcieDiscoveryNode(AdtNode armIo) {
var pcie = new AdtNode();
pcie.Properties["compatible"] = "apcie,t8140";
pcie.Properties["reg"] = EncodeRegRanges(
 (0x3f000000UL, 0x01000000UL),
 (0x10000000UL, 0x10000000UL));
armIo.Children.Add(pcie);
}
private static byte[] EncodeRegRanges(params (ulong Address, ulong Size)[] ranges) {}'''
CMD = '''"-args", "rd=md0 serial=3", "-device", "pcie-root-port,id=iosm3rp,bus=pcie.0",
"-device", "nvme,drive=iosm3nvme,serial=IOSM3PROBE"'''
BLOBS = {k: '0'*40 for k in ('qemu_patch','adt_patcher','command_builder')}


def result(q=QEMU, a=ADT, c=CMD, expected=None):
    return audit.audit(q,a,c,BLOBS,expected)


class StaticContractTests(unittest.TestCase):
    def test_exact_windows_match_but_no_stage1(self):
        r=result()
        self.assertEqual(r['classification'], 'HOST_ADT_WINDOWS_MATCH_PROVIDER_ABI_UNPROVEN')
        self.assertEqual(r['facts']['qemu_windows'], r['facts']['adt_windows'])
        self.assertFalse(r['stage1_accepted'])
        self.assertFalse(r['guest_nvme_bound'])
        self.assertFalse(r['facts']['adt_ports_property_assigned'])
        self.assertFalse(r['facts']['adt_explicit_port_children_added'])

    def test_window_mismatch(self):
        r=result(a=ADT.replace('0x01000000UL', '0x02000000UL'))
        self.assertEqual(r['classification'], 'HOST_ADT_WINDOW_MISMATCH')

    def test_missing_adt_method(self):
        self.assertEqual(result(a='class Placeholder {}')['classification'],
                         'INSUFFICIENT_STATIC_SOURCE_EVIDENCE')

    def test_missing_nvme(self):
        self.assertEqual(result(c=CMD.replace('nvme,drive=iosm3nvme', 'virtio-blk'))['classification'],
                         'INSUFFICIENT_STATIC_SOURCE_EVIDENCE')

    def test_sha_mismatch_takes_priority(self):
        expected={**BLOBS, 'qemu_patch': '1'*40}
        self.assertEqual(result(expected=expected)['classification'], 'SOURCE_SHA_MISMATCH')

    def test_no_apple_port_count_inference(self):
        r=result(a=ADT.replace('armIo.Children.Add(pcie);',
                               'pcie.Properties["#ports"] = 3u; armIo.Children.Add(pcie);'))
        self.assertTrue(r['facts']['adt_ports_property_assigned'])
        self.assertFalse(r['stage1_accepted'])
        self.assertEqual(r['classification'], 'HOST_ADT_WINDOWS_MATCH_PROVIDER_ABI_UNPROVEN')

    def test_duplicate_qemu_constant_fails_closed(self):
        self.assertEqual(result(q=QEMU+'\nconst hwaddr pcie_ecam_base = 0x3f000000;')
                         ['classification'], 'INSUFFICIENT_STATIC_SOURCE_EVIDENCE')

    def test_git_blob_fingerprint(self):
        self.assertEqual(audit.git_blob_sha1(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')


if __name__ == '__main__':
    unittest.main()
