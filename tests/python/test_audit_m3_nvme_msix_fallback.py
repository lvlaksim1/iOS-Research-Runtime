"""Synthetic, deliberately bounded tests; not a QEMU or guest runtime test."""
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts/audit_m3_nvme_msix_fallback.py"
spec = importlib.util.spec_from_file_location("m3_msix_gate", MODULE_PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    return {
        "hw/nvme/ctrl.c": '''
            static bool nvme_init_pci(NvmeCtrl *n, PCIDevice *pci_dev, Error **errp) {
                ret = msix_init_exclusive_bar(pci_dev, n->params.msix_qsize, 4, errp);
                ret = msix_init(pci_dev, nr_vectors, &n->bar0, 0, msix_table_offset,
                                &n->bar0, 0, msix_pba_offset, 0, errp);
                if (ret == -ENOTSUP) {
                    warn_report_err(*errp); *errp = NULL;
                } else if (ret < 0) { return false; }
                return true;
            }
            static void nvme_irq_assert(NvmeCtrl *n, NvmeCQueue *cq) {
                if (cq->irq_enabled) {
                    if (msix_enabled(pci)) { msix_notify(pci, cq->vector); }
                    else { n->irq_status |= 1; nvme_irq_check(n); }
                }
            }''',
        "hw/pci/msix.c": '''
            int msix_init(PCIDevice *dev, uint32_t nentries, Error **errp) {
                if (!msi_nonbroken) { error_setg(errp, "MSI-X unsupported"); return -ENOTSUP; }
                return 0;
            }
            int msix_init_exclusive_bar(PCIDevice *dev, Error **errp) {
                return msix_init(dev, 1, errp);
            }
            void msix_notify(PCIDevice *dev, unsigned vector) {
                MSIMessage msg = msix_get_message(dev, vector);
                msi_send_message(dev, msg);
            }''',
        "hw/pci/msi.c": '''
            void msi_send_message(PCIDevice *dev, MSIMessage msg) {
                dev->msi_trigger(dev, msg);
            }''',
        "hw/pci/pci.c": '''
            static void pci_msi_trigger(PCIDevice *dev, MSIMessage msg) {
                address_space_stl_le(&dev->bus_master_as, msg.address, msg.data, attrs, NULL);
            }''',
        "hw/arm/darwin.c": '''
            static void init_aic(struct dtree_node *dt_root, uint64_t iobase) {
                alloc_zeroed("aic", base, aic_reg[0].len);
            }''',
    }


class TestSourceContract(unittest.TestCase):
    def test_valid_contract_still_not_guest_proof(self):
        report = m.audit_texts(fixture())
        self.assertEqual(report["proof_level"], "STATIC_SOURCE_CONTRACT_ONLY")
        self.assertEqual(report["guest_interrupt_delivered"], "NOT_PROVEN")
        self.assertEqual(report["runtime_msi_nonbroken"], "UNKNOWN")

    def test_missing_enotsup_fallback_rejected(self):
        f = fixture(); f["hw/nvme/ctrl.c"] = f["hw/nvme/ctrl.c"].replace("ret == -ENOTSUP", "ret == -EINVAL")
        with self.assertRaisesRegex(m.ContractError, "ENOTSUP"):
            m.audit_texts(f)

    def test_missing_nvme_intx_branch_rejected(self):
        f = fixture(); f["hw/nvme/ctrl.c"] = f["hw/nvme/ctrl.c"].replace("nvme_irq_check(n)", "do_nothing(n)")
        with self.assertRaisesRegex(m.ContractError, "INTx"):
            m.audit_texts(f)

    def test_missing_msix_guard_rejected(self):
        f = fixture(); f["hw/pci/msix.c"] = f["hw/pci/msix.c"].replace("!msi_nonbroken", "msi_nonbroken")
        with self.assertRaisesRegex(m.ContractError, "guard"):
            m.audit_texts(f)

    def test_missing_exclusive_delegation_rejected(self):
        f = fixture(); f["hw/pci/msix.c"] = f["hw/pci/msix.c"].replace("return msix_init(dev, 1, errp)", "return 0")
        with self.assertRaisesRegex(m.ContractError, "delegates"):
            m.audit_texts(f)

    def test_missing_msix_send_rejected(self):
        f = fixture(); f["hw/pci/msix.c"] = f["hw/pci/msix.c"].replace("msi_send_message(dev, msg)", "silent_drop(dev, msg)")
        with self.assertRaisesRegex(m.ContractError, "dispatch"):
            m.audit_texts(f)

    def test_missing_msi_callback_rejected(self):
        f = fixture(); f["hw/pci/msi.c"] = f["hw/pci/msi.c"].replace("dev->msi_trigger", "dev->other")
        with self.assertRaisesRegex(m.ContractError, "callback"):
            m.audit_texts(f)

    def test_missing_busmaster_write_rejected(self):
        f = fixture(); f["hw/pci/pci.c"] = f["hw/pci/pci.c"].replace("&dev->bus_master_as", "&address_space_memory")
        with self.assertRaisesRegex(m.ContractError, "bus-master"):
            m.audit_texts(f)

    def test_new_aic_irq_logic_forces_recheck(self):
        f = fixture(); f["hw/arm/darwin.c"] = f["hw/arm/darwin.c"].replace("alloc_zeroed(\"aic\", base, aic_reg[0].len);", "alloc_zeroed(\"aic\", base, aic_reg[0].len); qemu_set_irq(line, 1);")
        with self.assertRaisesRegex(m.ContractError, "initializer has changed"):
            m.audit_texts(f)

    def test_darwin_msi_flag_assignment_forces_recheck(self):
        f = fixture(); f["hw/arm/darwin.c"] += "\nvoid other(void) { msi_nonbroken = true; }\n"
        with self.assertRaisesRegex(m.ContractError, "assignment changed"):
            m.audit_texts(f)

    def test_missing_input_fails_closed(self):
        f = fixture(); del f["hw/pci/pci.c"]
        with self.assertRaisesRegex(m.ContractError, "missing source inputs"):
            m.audit_texts(f)

    def test_git_blob_hash(self):
        self.assertEqual(m.git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_git_blob_mismatch_fails_before_analysis(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for path in m.PINNED_BLOBS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(fixture()[path])
            with self.assertRaisesRegex(m.ContractError, "Git blob mismatch"):
                m.audit_directory(root)

    def test_c_comments_and_string_braces_do_not_break_parser(self):
        src = '''static void foo(void) { /* } */ const char *x="}"; if (1) { return; } }'''
        body = m.c_function(src, "foo")
        self.assertIn('if (1)', body)

    def test_missing_function_fails_closed(self):
        with self.assertRaisesRegex(m.ContractError, "expected one definition"):
            m.c_function("void unrelated(void) {}", "foo")

    def test_ambiguous_function_fails_closed(self):
        with self.assertRaisesRegex(m.ContractError, "found 2"):
            m.c_function("void foo(void) {} void foo(int x) {}", "foo")

    def test_unterminated_comment_fails_closed(self):
        with self.assertRaisesRegex(m.ContractError, "unterminated C comment"):
            m.c_function("void foo(void) { /* bad", "foo")


if __name__ == "__main__":
    unittest.main()
