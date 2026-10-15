"""Host-mocked tests only. They do NOT demonstrate guest IOService binding."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2] / 'scripts' / 'ios_m3_ioreg_lineage.c'
HEADER = r'''
#ifndef IOS_M3_IOREG_TEST_SHIM_H
#define IOS_M3_IOREG_TEST_SHIM_H
#include <stdint.h>
typedef unsigned io_object_t;
typedef unsigned io_registry_entry_t;
typedef unsigned io_iterator_t;
typedef int kern_return_t;
typedef char io_name_t[128];
#define KERN_SUCCESS 0
#define kIOMasterPortDefault 0
#define kIOServicePlane "IOService"
#define kIORegistryIterateRecursively 1
kern_return_t IORegistryCreateIterator(unsigned,const char*,unsigned,io_iterator_t*);
io_registry_entry_t IOIteratorNext(io_iterator_t);
kern_return_t IORegistryEntryGetRegistryEntryID(io_registry_entry_t,uint64_t*);
kern_return_t IORegistryEntryGetName(io_registry_entry_t,io_name_t);
kern_return_t IOObjectGetClass(io_object_t,io_name_t);
kern_return_t IORegistryEntryGetParentEntry(io_registry_entry_t,const char*,io_registry_entry_t*);
kern_return_t IOObjectRelease(io_object_t);
#endif
'''
MOCK = r'''
#include "ios_m3_ioreg_test_shim.h"
#include <stdlib.h>
#include <string.h>
static unsigned index_ = 0;
kern_return_t IORegistryCreateIterator(unsigned port,const char *plane,unsigned flags,io_iterator_t *out) {
    if (port != 0 || strcmp(plane,"IOService") || flags != 1) return 9;
    if (getenv("IOS_M3_FAIL_ITERATOR")) return 13;
    *out = 900; return 0;
}
io_registry_entry_t IOIteratorNext(io_iterator_t it) {
    if (it != 900) return 0;
    if (index_ >= 3) return 0;
    return 101 + index_++;
}
kern_return_t IORegistryEntryGetRegistryEntryID(io_registry_entry_t obj,uint64_t *id) {
    if (getenv("IOS_M3_FAIL_ID") && obj == 102) return 7;
    if (obj < 101 || obj > 103) return 8;
    *id = obj; return 0;
}
kern_return_t IORegistryEntryGetName(io_registry_entry_t obj,io_name_t out) {
    if (obj < 101 || obj > 103) return 8;
    strcpy(out,obj==101?"pcie-root":obj==102?"pcie-child":"nvme\\\"node"); return 0;
}
kern_return_t IOObjectGetClass(io_object_t obj,io_name_t out) {
    if (obj < 101 || obj > 103) return 8;
    strcpy(out,obj==101?"AppleT8140PCIe":obj==102?"IOPCIDevice":"AppleNVMe"); return 0;
}
kern_return_t IORegistryEntryGetParentEntry(io_registry_entry_t obj,const char *plane,io_registry_entry_t *out) {
    if (strcmp(plane,"IOService")) return 9;
    if (obj==101) return 1;
    if (obj==103 && getenv("IOS_M3_MISSING_PARENT")) return 4;
    if (obj==102 || obj==103) { *out=obj-1; return 0; }
    return 8;
}
kern_return_t IOObjectRelease(io_object_t obj) { (void)obj; return 0; }
'''

@unittest.skipUnless(shutil.which('cc'), 'host C compiler unavailable')
class ReadOnlyLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        (root/'ios_m3_ioreg_test_shim.h').write_text(HEADER)
        (root/'mock.c').write_text(MOCK)
        cls.exe = root/'lineage'
        cmd = ['cc','-std=c11','-Wall','-Wextra','-Werror','-DIOS_M3_HOST_TEST',
               '-I',str(root),str(SOURCE),str(root/'mock.c'),'-o',str(cls.exe)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_probe(self, **env):
        e = dict(os.environ)
        for k in ('IOS_M3_FAIL_ITERATOR','IOS_M3_FAIL_ID','IOS_M3_MISSING_PARENT'):
            e.pop(k,None)
        e.update(env)
        p = subprocess.run([str(self.exe)],capture_output=True,text=True,env=e)
        return p, [json.loads(line) for line in p.stdout.splitlines()]

    def test_direct_parent_id_not_inferred_from_line_order(self):
        p, rows = self.run_probe()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual([r['id'] for r in rows[:3]], [f'0x{x:016x}' for x in (101,102,103)])
        self.assertEqual(rows[2]['parent_id'],'0x0000000000000066')
        self.assertEqual(rows[1]['parent_id'],'0x0000000000000065')
        self.assertIsNone(rows[0]['parent_id'])
        self.assertEqual(rows[0]['parent_status'],1)
        self.assertEqual(rows[-1]['kind'],'summary')
        self.assertFalse(rows[-1]['full_system_boot_accepted'])

    def test_missing_parent_never_guessed(self):
        p, rows = self.run_probe(IOS_M3_MISSING_PARENT='1')
        self.assertEqual(p.returncode,0)
        self.assertIsNone(rows[2]['parent_id'])
        self.assertEqual(rows[2]['parent_status'],4)

    def test_id_failure_produces_error_and_nonzero(self):
        p, rows = self.run_probe(IOS_M3_FAIL_ID='1')
        self.assertEqual(p.returncode,3)
        self.assertTrue(any(r.get('kind')=='entry_error' for r in rows))
        self.assertEqual(rows[-1]['errors'],1)

    def test_iterator_failure_fails_closed(self):
        p, rows = self.run_probe(IOS_M3_FAIL_ITERATOR='1')
        self.assertEqual(p.returncode,2)
        self.assertEqual(rows[0]['step'],'iterator')

    def test_json_escaping_and_bounded_read_only(self):
        p, rows = self.run_probe()
        self.assertEqual(p.returncode,0)
        self.assertIn('"',rows[2]['name'])
        source = SOURCE.read_text()
        self.assertIn('IOS_M3_MAX_ENTRIES 4096U',source)
        self.assertNotIn('IORegistryEntrySetCFProperties',source)
        self.assertNotIn('IOServiceOpen(',source)
        self.assertIn('IORegistryEntryGetParentEntry',source)

if __name__ == '__main__':
    unittest.main()
