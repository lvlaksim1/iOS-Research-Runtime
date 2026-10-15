"""Synthetic source-contract tests; no real guest or iPhoneOS build proof."""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

P = pathlib.Path(__file__).resolve().parents[2] / 'scripts/audit_m3_storage_irq_path.py'
spec = importlib.util.spec_from_file_location('m3_irq_audit', P)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

UPSTREAM = '''static void init_aic(struct dtree_node *root, uint64_t base) {
  alloc_zeroed("aic", base, 0x1000);
  address_space_write(&address_space_memory, base + 0xC, attrs, &num_irqs, 4);
}'''
GPEX = '''static int gpex_swizzle_map_irq_fn(PCIDevice *dev, int pin) {
 return (PCI_SLOT(dev->devfn) + pin) % bus->nirq;
}
static void gpex_host_realize(DeviceState *dev, Error **errp) {
 sysbus_init_irq(sbd, &s->irq[i].irq);
 pci->bus = pci_register_root_bus(dev, "pcie.0", gpex_set_irq,
   gpex_swizzle_map_irq_fn, s, &s->io_mmio, &s->io_ioport, 0,
   s->num_irqs, TYPE_PCIE_BUS);
}'''
PATCH = '''diff --git a/hw/arm/darwin.c b/hw/arm/darwin.c
+++ b/hw/arm/darwin.c
+DeviceState *pcie = qdev_new("gpex-pcihost");
+object_property_set_int(OBJECT(pcie), "num-irqs", 0, &error_fatal);
+sysbus_realize_and_unref(SYS_BUS_DEVICE(pcie), &error_fatal);
'''
ADT = '''private static void AddPcieDiscoveryNode(AdtNode armIo) {
 pcie.Properties["msi-parent-controller"] = 32u;
 pcie.Properties["#msi-vectors"] = 96u;
}
private static byte[] EncodeRegRanges() {}'''
CMD = '''"-device", "pcie-root-port,id=iosm3rp,bus=pcie.0", "-device", "nvme,drive=iosm3nvme,serial=IOSM3PROBE"'''


def sources(**overrides):
    result = dict(upstream_darwin=UPSTREAM, upstream_gpex=GPEX,
                  gpex_patch=PATCH, adt_patcher=ADT, command_builder=CMD)
    result.update(overrides)
    return result


class IRQAuditTests(unittest.TestCase):
    def test_exact_source_contract_flags_missing_irq_delivery(self):
        r = mod.audit_sources(sources())
        self.assertEqual(r['classification'], 'IRQ_DELIVERY_PREREQUISITE_NOT_ESTABLISHED')
        self.assertIn('PINNED_AIC_IS_REGISTER_STUB_NO_IRQ_DELIVERY_OBSERVED', r['observations'])
        self.assertIn('GPEX_INTX_COUNT_ZERO_IN_INSPECTED_PATCH', r['observations'])
        self.assertIn('NO_GPEX_IRQ_CONNECTION_CALL_IN_INSPECTED_PATCH', r['observations'])

    def test_zero_nirq_modulo_is_potential_not_asserted_crash(self):
        r = mod.audit_sources(sources())
        self.assertIn('POTENTIAL_INTX_SWIZZLE_ZERO_NIRQ_HAZARD_IF_INVOKED', r['observations'])
        self.assertNotIn('CRASH_PROVEN', r['observations'])

    def test_msi_adt_not_delivery_proof(self):
        r = mod.audit_sources(sources())
        self.assertTrue(r['facts']['adt_msi_parent_advertised'])
        self.assertIn('ADT_MSI_ADVERTISEMENT_NOT_EQUIVALENT_TO_IRQ_DELIVERY', r['observations'])
        self.assertFalse(r['stage1_full_ios_boot_accepted'])

    def test_guest_acceptance_never_inferred(self):
        r = mod.audit_sources(sources())
        for k in ['guest_nvme_bound','non_ramdisk_disk_proven','apfs_system_volumes_mounted','system_launchd_proven','stage1_full_ios_boot_accepted']:
            self.assertFalse(r[k])

    def test_added_patch_line_not_removed_context(self):
        p = PATCH.replace('+object_property_set_int', '-object_property_set_int')
        r = mod.audit_sources(sources(gpex_patch=p))
        self.assertFalse(r['facts']['gpex_patch_num_irqs_zero'])

    def test_comment_does_not_fake_aic_delivery(self):
        u = UPSTREAM.replace('  address_space_write', '  // sysbus_connect_irq(pcie, 0, aic);\n  address_space_write')
        r = mod.audit_sources(sources(upstream_darwin=u))
        self.assertTrue(r['facts']['upstream_aic_no_irq_delivery_calls'])

    def test_explicit_aic_irq_call_not_stub(self):
        u = UPSTREAM.replace('  address_space_write', '  sysbus_connect_irq(pcie, 0, aic);\n  address_space_write')
        r = mod.audit_sources(sources(upstream_darwin=u))
        self.assertFalse(r['facts']['upstream_aic_no_irq_delivery_calls'])

    def test_added_gpex_irq_wiring_detected(self):
        p = PATCH + '+sysbus_connect_irq(SYS_BUS_DEVICE(pcie), 0, irq);\n'
        r = mod.audit_sources(sources(gpex_patch=p))
        self.assertTrue(r['facts']['gpex_patch_has_irq_connection_call'])

    def test_missing_aic_function_is_unknown_not_positive(self):
        r = mod.audit_sources(sources(upstream_darwin='static void other(void) {}'))
        self.assertIn('AIC_FUNCTION_NOT_LOCATED_IN_PINNED_SOURCE', r['observations'])

    def test_missing_input_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing source inputs'):
            mod.audit_sources({'upstream_darwin': UPSTREAM})

    def test_blob_hash_known_git_construction(self):
        import hashlib
        raw=b'hello\n'
        self.assertEqual(mod.git_blob_sha1(raw),hashlib.sha1(b'blob 6\0hello\n').hexdigest())

    def test_source_hash_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'source.c';p.write_text('fake source')
            with self.assertRaisesRegex(ValueError, 'git blob mismatch'):
                mod.read_pinned_sources({k:p for k in mod.EXPECTED_BLOBS})

    def test_no_root_port_not_proven(self):
        r = mod.audit_sources(sources(command_builder='"-device", "nvme,drive=iosm3nvme"'))
        self.assertFalse(r['facts']['qemu_pcie_root_port_requested'])
        self.assertIn('NVME_OR_ROOT_PORT_CLI_INTENT_NOT_FOUND',r['observations'])

    def test_function_body_balanced(self):
        u = UPSTREAM.replace('  address_space_write', '  if (x) { y(); }\n  address_space_write')
        self.assertIn('address_space_write',mod.function_body(u,'init_aic'))


if __name__=='__main__':
    unittest.main()
