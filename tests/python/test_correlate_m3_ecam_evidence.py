"""Synthetic evidence-contract tests, not guest runtime acceptance."""
import importlib.util
import pathlib
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "correlate_m3_ecam_evidence.py"
SPEC = importlib.util.spec_from_file_location("correlate_m3_ecam_evidence", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EcamEvidenceTests(unittest.TestCase):
    WIRING = "[ios-m3-pcie-wiring] ecam=0x3f000000 mmio=0x10000000 host=gpex-pcihost\n"

    def test_wiring_without_ecam_is_not_guest_evidence(self):
        r = MOD.analyze([self.WIRING])
        self.assertEqual(r["classification"], "WIRING_MARKER_ONLY_NO_ECAM_ACTIVITY_OBSERVED")
        self.assertEqual(r["ecam_access_count"], 0)
        self.assertFalse(r["stage1_full_ios_boot_accepted"])

    def test_ecam_relative_address_decodes_bus_device_function(self):
        r = MOD.analyze([self.WIRING, "[ios-m3-pcie-ecam] op=read addr=0x120034 len=4 device=present\n"])
        self.assertEqual(r["classification"], "HOST_ECAM_HANDLER_ACTIVITY_WITH_WIRING_MARKER")
        a = r["ecam_accesses"][0]
        self.assertEqual((a["bus"], a["device"], a["function"], a["register"]), (1, 4, 0, 0x34))
        self.assertEqual(r["qemu_present_bdfs"], ["01:04.0"])
        self.assertFalse(r["guest_origin_verified"])
        self.assertFalse(r["guest_nvme_bound"])

    def test_absent_lookup_does_not_mean_no_bus_activity(self):
        r = MOD.analyze(["[ios-m3-pcie-ecam] op=write addr=0x000008 len=4 device=absent\n"])
        self.assertEqual(r["ecam_access_count"], 1)
        self.assertEqual(r["qemu_lookup_counts"], {"absent": 1})
        self.assertEqual(r["classification"], "HOST_ECAM_HANDLER_ACTIVITY_WIRING_UNVERIFIED")

    def test_physical_ecam_address_must_not_be_decoded_as_relative(self):
        r = MOD.analyze(["[ios-m3-pcie-ecam] op=read addr=0x3f000000 len=4 device=present\n"])
        self.assertEqual(r["errors"][0]["reason"], "ECAM_RANGE_OR_WIDTH_INVALID")
        self.assertFalse(r["apple_iokit_provider_bound"])

    def test_wrong_wiring_fails_closed(self):
        r = MOD.analyze(["[ios-m3-pcie-wiring] ecam=0x3e000000 mmio=0x10000000 host=gpex-pcihost\n"])
        self.assertEqual(r["errors"][0]["reason"], "WIRING_CONTRACT_MISMATCH")

    def test_echo_and_quoted_source_not_accepted(self):
        r = MOD.analyze(['echo "[ios-m3-pcie-ecam] op=read addr=0x0 len=4 device=present"\n',
                         ' + fprintf(stderr, "[ios-m3-pcie-ecam] op=%s ...");\n'])
        self.assertEqual(r["ecam_access_count"], 0)

    def test_boundary_and_invalid_width_rejected(self):
        r = MOD.analyze(["[ios-m3-pcie-ecam] op=read addr=0xfff len=4 device=present\n",
                         "[ios-m3-pcie-ecam] op=read addr=0x0 len=3 device=present\n"])
        self.assertEqual(len(r["errors"]), 2)
        self.assertEqual(r["ecam_access_count"], 0)

    def test_over_128_markers_or_multiple_wiring_not_one_runtime(self):
        access = "[ios-m3-pcie-ecam] op=read addr=0x0 len=4 device=present\n"
        r = MOD.analyze([self.WIRING, self.WIRING] + [access] * 129)
        self.assertIn("MORE_THAN_128_ECAM_MARKERS", [e["reason"] for e in r["errors"]])
        self.assertIn("MULTIPLE_WIRING_MARKERS_UNSEGMENTED_LOG", [e["reason"] for e in r["errors"]])

    def test_no_markers_no_inference(self):
        r = MOD.analyze(["Recovery root shell ready\n", "BOOT_PROOF_OK\n"])
        self.assertEqual(r["classification"], "NO_RECOGNIZED_QEMU_PCIE_DIAGNOSTICS")
        self.assertFalse(r["stage1_full_ios_boot_accepted"])

    def test_bounded_file_read_and_cli_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "log.txt"
            p.write_text(self.WIRING, encoding="utf-8")
            r = MOD.analyze_file(p)
            self.assertEqual(r["wiring_marker_count"], 1)


if __name__ == "__main__":
    unittest.main()
