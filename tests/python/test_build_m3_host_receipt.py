"""Synthetic host-only receipt checks; no guest boot or QEMU run is claimed."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_m3_host_receipt.py"
spec = importlib.util.spec_from_file_location("build_m3_host_receipt", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

NONCE = "1" * 32
HEAD = "a" * 40
QUERY_ID = "iosm3-query-pci-" + NONCE


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.paths = {name: self.root / name for name in (
            "qemu", "serial", "stderr", "capture", "qmp_raw", "qmp_evidence")}
        self.paths["qemu"].write_bytes(b"fake-qemu-executable")
        self.paths["serial"].write_bytes(b"Darwin recovery shell only\n")
        self.paths["stderr"].write_bytes(b"host stderr\n")
        self.capture = {
            "schema": 1, "boot_nonce": NONCE, "run_id": "run-101", "head_sha": HEAD,
            "serial_file": "serial", "stderr_file": "stderr",
            "serial_sha256": hashlib.sha256(self.paths["serial"].read_bytes()).hexdigest(),
            "stage1_accepted": False,
        }
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{
            "class_info": {"class": 0x0108}, "slot": 1, "function": 0,
            "qdev_id": "nvme0"}]}]}
        self.qmp = {
            "schema": 1, "boot_nonce": NONCE, "run_id": "run-101", "head_sha": HEAD,
            "source": "QMP_QUERY_PCI_HOST_ONLY", "raw_reply_file": "qmp_raw",
            "valid_query_pci_reply": True,
            "host_nvme_candidates": [{"Bus": 0, "Slot": 1, "Function": 0, "QdevId": "nvme0"}],
            "classification": "HOST_NVME_CLASS_OBSERVED_GUEST_BINDING_UNPROVEN",
            "guest_nvme_bound": False, "stage1_accepted": False,
        }
        self.save()

    def save(self):
        for key, obj in (("capture", self.capture), ("qmp_raw", self.raw), ("qmp_evidence", self.qmp)):
            self.paths[key].write_text(json.dumps(obj), encoding="utf-8")

    def receipt(self):
        return module.build_receipt(qemu=self.paths["qemu"], serial=self.paths["serial"],
                                    stderr=self.paths["stderr"], capture=self.paths["capture"],
                                    qmp_raw=self.paths["qmp_raw"], qmp_evidence=self.paths["qmp_evidence"])

    def test_host_only_success_still_not_stage1(self):
        result = self.receipt()
        self.assertTrue(result["host_complete"], result["errors"])
        self.assertFalse(result["stage1_accepted"])
        self.assertFalse(result["guest_nvme_bound"])
        self.assertEqual(result["classification"], self.qmp["classification"])
        self.assertEqual(result["qemu_sha256"], hashlib.sha256(b"fake-qemu-executable").hexdigest())

    def test_missing_qmp_is_fail_closed(self):
        self.paths["qmp_evidence"].unlink()
        self.assertFalse(self.receipt()["host_complete"])

    def test_missing_qemu_is_fail_closed(self):
        self.paths["qemu"].unlink()
        self.assertFalse(self.receipt()["host_complete"])

    def test_tampered_serial_is_fail_closed(self):
        self.paths["serial"].write_bytes(b"changed")
        self.assertIn("capture: serial SHA256 mismatch", self.receipt()["errors"])

    def test_cross_boot_identity_is_fail_closed(self):
        for field, value in (("boot_nonce", "2" * 32), ("run_id", "other"), ("head_sha", "b" * 40)):
            with self.subTest(field=field):
                self.qmp[field] = value
                self.save()
                self.assertFalse(self.receipt()["host_complete"])
                self.qmp[field] = self.capture[field]

    def test_raw_qmp_tampering_is_fail_closed(self):
        self.raw["return"][0]["devices"].clear()
        self.save()
        self.assertIn("qmp: classification differs from raw PCI topology", self.receipt()["errors"])

    def test_qmp_error_reply_is_fail_closed(self):
        self.raw = {"id": QUERY_ID, "error": {"class": "CommandNotFound"}}
        self.save()
        self.assertFalse(self.receipt()["host_complete"])

    def test_host_nvme_flag_cannot_claim_guest(self):
        self.qmp["guest_nvme_bound"] = True
        self.save()
        self.assertFalse(self.receipt()["host_complete"])
        self.assertFalse(self.receipt()["stage1_accepted"])

    def test_qmp_stage1_flag_cannot_claim_guest(self):
        self.qmp["stage1_accepted"] = True
        self.save()
        self.assertFalse(self.receipt()["host_complete"])

    def test_symlink_rejected(self):
        self.paths["qemu"].unlink()
        self.paths["qemu"].symlink_to(self.paths["serial"])
        self.assertFalse(self.receipt()["host_complete"])

    def test_bridge_nested_nvme(self):
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{"slot": 2, "function": 0,
            "pci_bridge": {"bus": {"secondary": 5}, "devices": [
            {"class_info": {"class": 0x010802}, "slot": 3, "function": 0}]}}]}]}
        self.qmp["host_nvme_candidates"] = [{"Bus": 5, "Slot": 3, "Function": 0, "QdevId": None}]
        self.save()
        self.assertTrue(self.receipt()["host_complete"])

    def test_unconfigured_bridge_without_devices_is_valid_host_only(self):
        # QEMU omits pci_bridge.devices when secondary bus is zero.
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
            {"slot": 2, "function": 0, "class_info": {"class": 0x0604},
             "pci_bridge": {"bus": {"number": 0, "secondary": 0, "subordinate": 0}}}]}]}
        self.qmp["host_nvme_candidates"] = []
        self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
        self.save()
        result = self.receipt()
        self.assertTrue(result["host_complete"], result["errors"])
        self.assertEqual([], result["host_nvme_candidates"])
        self.assertFalse(result["guest_nvme_bound"])
        self.assertFalse(result["stage1_accepted"])

    def test_configured_bridge_without_devices_is_valid_host_only(self):
        # QEMU may omit the optional member when a secondary bus is not found.
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
            {"slot": 2, "function": 0,
             "pci_bridge": {"bus": {"secondary": 5}}}]}]}
        self.qmp["host_nvme_candidates"] = []
        self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
        self.save()
        result = self.receipt()
        self.assertTrue(result["host_complete"], result["errors"])
        self.assertFalse(result["stage1_accepted"])

    def test_duplicate_configured_secondary_without_devices_rejected(self):
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
            {"slot": 1, "function": 0, "pci_bridge": {"bus": {"secondary": 5}}},
            {"slot": 2, "function": 0, "pci_bridge": {"bus": {"secondary": 5}}}]}]}
        self.qmp["host_nvme_candidates"] = []
        self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
        self.save()
        result = self.receipt()
        self.assertFalse(result["host_complete"])
        self.assertFalse(result["stage1_accepted"])

    def test_missing_or_nonlist_devices_rejected(self):
        malformed = [None, "corrupt", {}, [None], ["invalid"], [1]]
        for value in malformed:
            with self.subTest(devices=value):
                self.raw = {"id": QUERY_ID, "return": [{"bus": 0}]}
                if value is not None:
                    self.raw["return"][0]["devices"] = value
                self.qmp["host_nvme_candidates"] = []
                self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                self.assertFalse(result["stage1_accepted"])

    def test_invalid_root_bus_rejected(self):
        for bus in (-1, 256, True, "0", None):
            with self.subTest(bus=bus):
                self.raw = {"id": QUERY_ID, "return": [{"bus": bus, "devices": []}]}
                self.qmp["host_nvme_candidates"] = []
                self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
                self.save()
                self.assertFalse(self.receipt()["host_complete"])

    def test_invalid_bdf_rejected(self):
        for field, invalid in (("slot", -1), ("slot", 32), ("slot", True),
                               ("slot", "1"), ("function", -1),
                               ("function", 8), ("function", True),
                               ("bus", -1), ("bus", 256), ("bus", 1)):
            with self.subTest(field=field, invalid=invalid):
                self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{
                    "class_info": {"class": 0x0108}, "slot": 1,
                    "function": 0, "qdev_id": "nvme0", field: invalid}]}]}
                self.qmp["host_nvme_candidates"] = [{
                    "Bus": 0, "Slot": 1, "Function": 0, "QdevId": "nvme0"}]
                self.qmp["classification"] = "HOST_NVME_CLASS_OBSERVED_GUEST_BINDING_UNPROVEN"
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                self.assertFalse(result["stage1_accepted"])

    def test_missing_bdf_and_duplicate_addresses_rejected(self):
        for missing in ("slot", "function"):
            with self.subTest(missing=missing):
                self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{
                    "class_info": {"class": 0x0108}, "slot": 1, "function": 0}]}]}
                del self.raw["return"][0]["devices"][0][missing]
                self.save()
                self.assertFalse(self.receipt()["host_complete"])
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
            {"slot": 1, "function": 0}, {"slot": 1, "function": 0}]}]}
        self.qmp["host_nvme_candidates"] = []
        self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
        self.save()
        self.assertFalse(self.receipt()["host_complete"])

    def test_invalid_bridge_structure_rejected(self):
        for bridge in (None, {}, {"devices": []},
                       {"bus": {}, "devices": []},
                       {"bus": {"secondary": -1}, "devices": []},
                       {"bus": {"secondary": 1}, "devices": "corrupt"}):
            with self.subTest(bridge=bridge):
                self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
                    {"slot": 2, "function": 0, "pci_bridge": bridge}]}]}
                self.qmp["host_nvme_candidates"] = []
                self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
                self.save()
                self.assertFalse(self.receipt()["host_complete"])

    def test_invalid_class_and_qdev_rejected(self):
        for field, value in (("class_info", {"class": True}),
                             ("class_info", {"class": -1}),
                             ("class_info", "bad"), ("qdev_id", 123)):
            with self.subTest(field=field, value=value):
                self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
                    {"slot": 1, "function": 0, field: value}]}]}
                self.qmp["host_nvme_candidates"] = []
                self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
                self.save()
                self.assertFalse(self.receipt()["host_complete"])

    def test_duplicate_root_bus_rejected_even_without_bdf_collision(self):
        for devices in ([], [{"slot": 2, "function": 0,
                             "class_info": {"class": 0x0108}, "qdev_id": "nvme1"}]):
            with self.subTest(devices=devices):
                self.raw = {"id": QUERY_ID, "return": [
                    {"bus": 0, "devices": [{"slot": 1, "function": 0,
                                            "class_info": {"class": 0x0108},
                                            "qdev_id": "nvme0"}]},
                    {"bus": 0, "devices": devices}]}
                self.qmp["host_nvme_candidates"] = [
                    {"Bus": 0, "Slot": 1, "Function": 0, "QdevId": "nvme0"}]
                if devices:
                    self.qmp["host_nvme_candidates"].append(
                        {"Bus": 0, "Slot": 2, "Function": 0, "QdevId": "nvme1"})
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                self.assertFalse(result["stage1_accepted"])

    def test_bridge_secondary_bus_alias_rejected(self):
        for raw in (
            # A bridge points back to its root/ancestor bus.
            {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{"slot": 1, "function": 0,
                "pci_bridge": {"bus": {"secondary": 0}, "devices": []}}]}]},
            # Two bridges point to the same secondary bus.
            {"id": QUERY_ID, "return": [{"bus": 0, "devices": [
                {"slot": 1, "function": 0, "pci_bridge": {
                    "bus": {"secondary": 5}, "devices": []}},
                {"slot": 2, "function": 0, "pci_bridge": {
                    "bus": {"secondary": 5}, "devices": []}}]}]},
            # A root bus aliases a secondary bus visited earlier.
            {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{"slot": 1, "function": 0,
                "pci_bridge": {"bus": {"secondary": 5}, "devices": []}}]},
                {"bus": 5, "devices": []}]},
        ):
            with self.subTest(raw=raw):
                self.raw = raw
                self.qmp["host_nvme_candidates"] = []
                self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                self.assertFalse(result["stage1_accepted"])

    def test_mixed_qmp_return_and_error_rejected(self):
        for error in ({"class": "GenericError"}, None):
            with self.subTest(error=error):
                self.raw["error"] = error
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                self.assertFalse(result["stage1_accepted"])
                del self.raw["error"]

    def test_distinct_roots_and_bridge_buses_remain_host_only(self):
        self.raw = {"id": QUERY_ID, "return": [
            {"bus": 0, "devices": [{"slot": 2, "function": 0,
                "pci_bridge": {"bus": {"secondary": 5}, "devices": [
                    {"slot": 3, "function": 0,
                     "class_info": {"class": 0x010802}, "qdev_id": "nvme5"}]}}]},
            {"bus": 1, "devices": [{"slot": 4, "function": 0,
                "class_info": {"class": 0x0200}}]}]}
        self.qmp["host_nvme_candidates"] = [
            {"Bus": 5, "Slot": 3, "Function": 0, "QdevId": "nvme5"}]
        self.save()
        result = self.receipt()
        self.assertTrue(result["host_complete"], result["errors"])
        self.assertFalse(result["stage1_accepted"])
        self.assertFalse(result["guest_nvme_bound"])

    def test_valid_no_nvme_remains_host_only(self):
        self.raw = {"id": QUERY_ID, "return": [{"bus": 0, "devices": [{
            "class_info": {"class": 0x0200}, "slot": 1, "function": 0}]}]}
        self.qmp["host_nvme_candidates"] = []
        self.qmp["classification"] = "NO_HOST_NVME_CLASS_OBSERVED"
        self.save()
        result = self.receipt()
        self.assertTrue(result["host_complete"], result["errors"])
        self.assertFalse(result["stage1_accepted"])

    def test_raw_reply_filename_mismatch(self):
        self.qmp["raw_reply_file"] = "../qmp_raw"
        self.save()
        self.assertFalse(self.receipt()["host_complete"])

    def test_empty_run_id_is_fail_closed(self):
        self.capture["run_id"] = ""
        self.qmp["run_id"] = ""
        self.save()
        self.assertFalse(self.receipt()["host_complete"])

    def test_qmp_query_id_must_match_boot_nonce(self):
        for bad in (None, "iosm3-query-pci-" + "2" * 32,
                    "iosm3-capabilities-" + NONCE, True, 1):
            with self.subTest(id=bad):
                self.raw["id"] = bad
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                self.assertFalse(result["stage1_accepted"])
        del self.raw["id"]
        self.save()
        self.assertFalse(self.receipt()["host_complete"])

    def test_qmp_event_or_extra_envelope_field_rejected(self):
        for extra in ({"event": "DEVICE_DELETED"},
                      {"timestamp": {"seconds": 1}}, {"error": None}):
            with self.subTest(extra=extra):
                self.raw.update(extra)
                self.save()
                result = self.receipt()
                self.assertFalse(result["host_complete"])
                for key in extra:
                    del self.raw[key]

    def test_duplicate_json_keys_rejected_in_raw_and_metadata(self):
        # json.loads normally retains the final value of duplicate keys.
        for text in (
            '{"id":"' + QUERY_ID + '","id":"' + QUERY_ID + '","return":[]}',
            '{"id":"' + QUERY_ID + '","return":[{"bus":0,"devices":['
            '{"slot":1,"slot":1,"function":0,"class_info":{"class":264}}]}]}',
        ):
            with self.subTest(text=text[:60]):
                self.save()
                self.paths["qmp_raw"].write_bytes(text.encode("utf-8"))
                self.assertFalse(self.receipt()["host_complete"])
        self.save()
        self.paths["capture"].write_text(
            json.dumps(self.capture)[:-1] + ',"boot_nonce":"' + NONCE + '"}',
            encoding="utf-8")
        self.assertFalse(self.receipt()["host_complete"])
        self.save()
        self.paths["qmp_evidence"].write_text(
            json.dumps(self.qmp)[:-1] + ',"run_id":"run-101"}',
            encoding="utf-8")
        self.assertFalse(self.receipt()["host_complete"])

    def test_nonstandard_json_numeric_constants_rejected_everywhere(self):
        # Python's default decoder accepts these non-JSON tokens, even when
        # they appear only in ignored metadata or nested PCI fields.
        for label in ("capture", "qmp_evidence", "qmp_raw"):
            for value in (float("nan"), float("inf"), -float("inf")):
                with self.subTest(label=label, value=repr(value)):
                    self.save()
                    if label == "capture":
                        obj = dict(self.capture, unused_metric=value)
                    elif label == "qmp_evidence":
                        obj = dict(self.qmp, unused_metric=value)
                    else:
                        obj = json.loads(json.dumps(self.raw))
                        obj["return"][0]["devices"][0]["unused_metric"] = value
                    self.paths[label].write_text(json.dumps(obj), encoding="utf-8")
                    result = self.receipt()
                    self.assertFalse(result["host_complete"], result)
                    self.assertFalse(result["stage1_accepted"])
                    self.assertFalse(result["guest_nvme_bound"])
                    prefix = "capture: ValueError" if label == "capture" else "qmp: ValueError"
                    self.assertIn(prefix, result["errors"])
        self.save()
        self.assertTrue(self.receipt()["host_complete"])

    def test_finite_unused_json_numbers_remain_valid_host_only(self):
        for label in ("capture", "qmp_evidence", "qmp_raw"):
            with self.subTest(label=label):
                self.save()
                if label == "capture":
                    obj = dict(self.capture, unused_metric=1.5)
                elif label == "qmp_evidence":
                    obj = dict(self.qmp, unused_metric=-2.5)
                else:
                    obj = json.loads(json.dumps(self.raw))
                    obj["return"][0]["devices"][0]["unused_metric"] = 0.125
                self.paths[label].write_text(json.dumps(obj), encoding="utf-8")
                result = self.receipt()
                self.assertTrue(result["host_complete"], result["errors"])
                self.assertFalse(result["stage1_accepted"])
                self.assertFalse(result["guest_nvme_bound"])

    def _write_raw_exponent(self, label: str, value: str) -> None:
        self.save()
        if label == "qmp_raw":
            raw = self.paths[label].read_text(encoding="utf-8")
            needle = '"qdev_id": "nvme0"'
            self.assertEqual(raw.count(needle), 1)
            raw = raw.replace(needle, needle + ', "unused_metric": ' + value, 1)
        else:
            raw = self.paths[label].read_text(encoding="utf-8")
            self.assertTrue(raw.endswith("}"))
            raw = raw[:-1] + ', "unused_metric": ' + value + "}"
        self.paths[label].write_text(raw, encoding="utf-8")

    def test_json_exponent_overflow_rejected_everywhere(self):
        # 1e999 is valid JSON syntax, but float() overflows to infinity.
        # The parse_constant hook cannot catch this representation.
        for label in ("capture", "qmp_evidence", "qmp_raw"):
            for value in ("1e999", "-1e999", "1e309"):
                with self.subTest(label=label, value=value):
                    self._write_raw_exponent(label, value)
                    result = self.receipt()
                    self.assertFalse(result["host_complete"], result)
                    self.assertFalse(result["stage1_accepted"])
                    self.assertFalse(result["guest_nvme_bound"])
                    prefix = "capture: ValueError" if label == "capture" else "qmp: ValueError"
                    self.assertIn(prefix, result["errors"])
                    with self.assertRaisesRegex(ValueError, "nonfinite JSON floating-point number"):
                        module._json_loads_strict(self.paths[label].read_bytes())
        self.save()
        self.assertTrue(self.receipt()["host_complete"])

    def test_large_finite_json_exponent_remains_host_only(self):
        for label in ("capture", "qmp_evidence", "qmp_raw"):
            with self.subTest(label=label):
                self._write_raw_exponent(label, "1e308")
                result = self.receipt()
                self.assertTrue(result["host_complete"], result["errors"])
                self.assertFalse(result["stage1_accepted"])
                self.assertFalse(result["guest_nvme_bound"])
        self.save()
        self.assertTrue(self.receipt()["host_complete"])

    def test_boolean_schema_is_not_version_one(self):
        for field in ("capture", "qmp"):
            with self.subTest(field=field):
                target = self.capture if field == "capture" else self.qmp
                target["schema"] = True
                self.save()
                self.assertFalse(self.receipt()["host_complete"])
                target["schema"] = 1
        self.save()
        self.assertTrue(self.receipt()["host_complete"])


if __name__ == "__main__":
    unittest.main()
