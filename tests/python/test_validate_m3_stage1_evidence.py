"""Synthetic structural tests; not guest boot or hardware acceptance tests."""
import copy
import importlib.util
import random
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_m3_stage1_evidence.py"
spec = importlib.util.spec_from_file_location("stage1", SCRIPT)
stage1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage1)


def fixture():
    p = {"repository": "lvlaksim1/iOS-Research-Runtime", "head_sha": "a" * 40,
         "qemu_sha256": "b" * 64, "serial_sha256": "c" * 64,
         "run_id": "test-run", "boot_nonce": "test-nonce", "evidence_kind": "guest_runtime"}
    h = {k: p[k] for k in ("head_sha", "qemu_sha256", "serial_sha256", "run_id", "boot_nonce")}
    h["qmp_nvme_present"] = True
    uuid = lambda n: f"00000000-0000-4000-8000-{n:012d}"
    stages = [
        {"provider_class": "PCIeProvider", "controller_class": "NVMeController", "bdf": "0000:00:01.0", "nvme_bdf": "0000:00:01.0", "provider_instance_id": "provider-1", "controller_instance_id": "nvme-1", "iokit_attached": True, "device_tree_only": False},
        {"bdf": "0000:00:01.0", "controller_instance_id": "nvme-1", "namespace_id": 1, "irq_delivered": True, "io_completed": 2},
        {"bsd_name": "disk2", "ramdisk": False, "backing_kind": "nvme_namespace", "namespace_id": 1, "media_instance_id": "media-1", "probe_image": False},
        {"physical_store": "disk2", "container_uuid": uuid(4), "volumes": [{"role": role, "volume_uuid": uuid(i), "mounted": True, "physical_store": "disk2"} for i, role in enumerate(("SystemOS", "Preboot", "Data"), 1)]},
        {"pid": 1, "executable": "/sbin/launchd", "boot_mode": "system", "root_volume_uuid": uuid(1), "data_volume_uuid": uuid(3), "recovery": False, "core_userland_started": True},
    ]
    events = [{"stage": s, "sequence": i, "origin": "guest_runtime", "run_id": p["run_id"],
               "boot_nonce": p["boot_nonce"], "raw_artifact_sha256": f"{i:x}" * 64, "data": d}
              for i, (s, d) in enumerate(zip(stage1.STAGES, stages), 1)]
    return {"schema": stage1.SCHEMA, "provenance": p, "host_receipt": h, "guest": events}


class TestStage1Evidence(unittest.TestCase):
    def test_complete_synthetic_never_proves_boot(self):
        report = stage1.validate(fixture())
        self.assertTrue(report["contract_complete"], report["errors"])
        self.assertFalse(report["stage1_accepted"])
        self.assertEqual(report["status"], "NOT_PROVEN")

    def test_missing_evidence(self):
        for name, mutator in (
            ("missing stage", lambda x: x["guest"].pop()),
            ("md0", lambda x: x["guest"][2]["data"].update(bsd_name="md0")),
            ("ramdisk", lambda x: x["guest"][2]["data"].update(ramdisk=True)),
            ("probe image", lambda x: x["guest"][2]["data"].update(probe_image=True)),
            ("ADT only", lambda x: x["guest"][0]["data"].update(device_tree_only=True)),
            ("no binding", lambda x: x["guest"][0]["data"].update(iokit_attached=False)),
            ("BDF mismatch", lambda x: x["guest"][1]["data"].update(bdf="0000:00:02.0")),
            ("no IRQ", lambda x: x["guest"][1]["data"].update(irq_delivered=False)),
            ("no I/O", lambda x: x["guest"][1]["data"].update(io_completed=0)),
            ("namespace mismatch", lambda x: x["guest"][2]["data"].update(namespace_id=2)),
            ("missing APFS", lambda x: x["guest"][3]["data"]["volumes"].pop()),
            ("duplicate APFS", lambda x: x["guest"][3]["data"]["volumes"][2].update(volume_uuid=x["guest"][3]["data"]["volumes"][0]["volume_uuid"])),
            ("APFS unmounted", lambda x: x["guest"][3]["data"]["volumes"][0].update(mounted=False)),
            ("not PID1", lambda x: x["guest"][4]["data"].update(pid=2)),
            ("recovery", lambda x: x["guest"][4]["data"].update(recovery=True)),
            ("no userland", lambda x: x["guest"][4]["data"].update(core_userland_started=False)),
            ("crossboot", lambda x: x["guest"][2].update(boot_nonce="different")),
            ("host mismatch", lambda x: x["host_receipt"].update(run_id="different")),
            ("host-only", lambda x: x["guest"][0].update(origin="host_qmp")),
            ("no host PCI", lambda x: x["host_receipt"].update(qmp_nvme_present=False)),
            ("missing source hash", lambda x: x["provenance"].update(serial_sha256="")),
            ("unknown key", lambda x: x["guest"][0]["data"].update(untrusted=True)),
            ("false bool as int", lambda x: x["guest"][4]["data"].update(pid=True)),
            ("sequence order", lambda x: x["guest"][1].update(sequence=1)),
            ("unknown evidence kind", lambda x: x["provenance"].update(evidence_kind="synthetic")),
        ):
            with self.subTest(name=name):
                sample = fixture()
                mutator(sample)
                report = stage1.validate(sample)
                self.assertFalse(report["contract_complete"], name)
                self.assertFalse(report["stage1_accepted"], name)

    def test_non_object_input(self):
        for item in (None, [], "", 42, {}):
            with self.subTest(item=item):
                report = stage1.validate(item)
                self.assertFalse(report["contract_complete"])
                self.assertFalse(report["stage1_accepted"])

    def test_malformed_json_shapes_never_accept(self):
        rng = random.Random(960021)
        choices = [None, [], {}, 0, True, "", ["a"], {"invalid": "shape"}]
        for i in range(2000):
            sample = fixture()
            index = rng.randrange(5)
            if index == 0:
                sample["provenance"] = rng.choice(choices)
            elif index == 1:
                sample["host_receipt"] = rng.choice(choices)
            elif index == 2:
                sample["guest"][rng.randrange(5)]["data"] = rng.choice(choices)
            elif index == 3:
                sample["guest"][rng.randrange(5)] = rng.choice(choices)
            else:
                sample["guest"] = rng.choice(choices)
            with self.subTest(case=i):
                result = stage1.validate(sample)
                self.assertFalse(result["contract_complete"])
                self.assertFalse(result["stage1_accepted"])

    def test_duplicate_json_keys_rejected(self):
        import json
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"schema":"x","schema":"y"}', object_pairs_hook=stage1.reject_duplicate_keys)


if __name__ == "__main__":
    unittest.main()
