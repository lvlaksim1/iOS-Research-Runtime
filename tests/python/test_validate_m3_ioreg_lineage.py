"""Synthetic negative/positive tests; no iOS guest evidence is asserted."""
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[2] / 'scripts' / 'validate_m3_ioreg_lineage.py'
spec = importlib.util.spec_from_file_location('validator', MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
A, B, C = ('0x' + str(i).zfill(16) for i in (1, 2, 3))


def entry(eid, parent=None, status=1):
    return {'kind': 'entry', 'plane': 'IOService', 'id': eid, 'parent_id': parent,
            'parent_status': status, 'class': 'UntrustedClass', 'name': 'UntrustedName'}


def capture(records=None, errors=0, truncated=False, count=None):
    records = [entry(A, B, 0), entry(B, C, 0), entry(C)] if records is None else records
    summary = {'kind': 'summary', 'plane': 'IOService', 'entries': len(records) if count is None else count,
               'errors': errors, 'truncated': truncated, 'full_system_boot_accepted': False}
    return ('\n'.join(json.dumps(x, separators=(',', ':')) for x in records + [summary]) + '\n').encode()


class TestLineage(unittest.TestCase):
    def check_unproven(self, data, child=A, ancestor=C):
        r = validator.inspect(data, child, ancestor)
        self.assertEqual(r['status'], 'UNPROVEN', r)
        self.assertFalse(r['full_system_boot_accepted'])
        return r

    def test_explicit_chain_only(self):
        r = validator.inspect(capture(), A, C)
        self.assertEqual(r['status'], 'STRUCTURALLY_CONSISTENT_CHAIN_ONLY')
        self.assertEqual(r['chain_ids_child_to_ancestor'], [A, B, C])
        self.assertFalse(r['driver_binding_proven'])
        self.assertFalse(r['guest_origin_authenticated'])
        self.assertFalse(r['full_system_boot_accepted'])

    def test_missing_parent(self):
        self.check_unproven(capture([entry(A, B, 0), entry(C)]))

    def test_missing_ancestor(self):
        self.check_unproven(capture([entry(A, B, 0), entry(B)]))

    def test_cycle(self):
        self.check_unproven(capture([entry(A, B, 0), entry(B, A, 0), entry(C)]))

    def test_duplicate_id(self):
        self.check_unproven(capture([entry(A, B, 0), entry(A, C, 0), entry(B), entry(C)]))

    def test_parent_status_mismatch(self):
        self.check_unproven(capture([entry(A, B, 1), entry(B, C, 0), entry(C)]))

    def test_summary_count_mismatch(self):
        self.check_unproven(capture(count=5))

    def test_truncation(self):
        self.check_unproven(capture(truncated=True))

    def test_entry_error(self):
        data = capture([entry(A, B, 0), entry(B, C, 0), entry(C),
                        {'kind': 'entry_error', 'step': 'class', 'status': 5}], errors=1)
        self.check_unproven(data)

    def test_duplicate_json_key(self):
        data = capture().replace(b'"kind":"entry"', b'"kind":"entry","kind":"entry"', 1)
        self.check_unproven(data)

    def test_no_final_newline(self):
        self.check_unproven(capture().rstrip(b'\n'))

    def test_after_summary(self):
        self.check_unproven(capture() + (json.dumps(entry(A)) + '\n').encode())

    def test_self_parent(self):
        self.check_unproven(capture([entry(A, A, 0), entry(B, C, 0), entry(C)]))

    def test_no_class_name_inference(self):
        self.check_unproven(capture([entry(A), entry(B), entry(C)]))

    def test_bad_ids(self):
        self.check_unproven(capture(), 'not_an_id', C)

    def test_empty(self):
        self.check_unproven(b'')


if __name__ == '__main__':
    unittest.main()
