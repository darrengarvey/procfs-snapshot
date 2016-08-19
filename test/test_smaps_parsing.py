
import unittest
from parsers.smaps import (
    parse_smaps_header,
    parse_smaps_memory_region
)

class SmapsHeaderParserTest(unittest.TestCase):
    
    def setUp(self):
        import os
        with open(os.path.join(os.path.dirname(__file__), 'firefox.smaps'), 'rb') as f:
            self.data = f.read()
        # Another bunch of example lines for various cases.
        # These are faked a bit to make the tests more useful
        # (eg. offsets are faked).
        self.pid = 12345
        self.process_line = '55917d4f7000-55917d514000 r-xp 00100000 08:06 542715                     /usr/lib/firefox/firefox'
        self.lib_line = '7f5c3f7fd000-7f5c3f7fe000 rw-p 00049000 08:06 532533                     /usr/lib/x86_64-linux-gnu/libopus.so.0.5.2'
        self.heap_line = '011e6000-01239000 rw-p 00003000 00:00 0                                  [heap]'
        self.stack_line = '7ffefddd2000-7ffefde0d000 rw-p 00001f00 00:00 0                          [stack]'
        self.vdso_line = '7ffefdebc000-7ffefdebe000 r-xp 00000020 00:00 0                          [vdso]'
        self.shared_mem_line = '7f5cabdce000-7f5cabe4e000 rw-s 0060e000 00:05 1605639                    /SYSV00000000 (deleted)'
        self.anonymous_line = '7f5cabd5d000-7f5cabd61000 rw-p 00007000 00:00 0 '

    def test_heap_parsing(self):
        info = parse_smaps_header(self.heap_line)

        self.assertEqual(0x011e6000, info.start_addr)
        self.assertEqual(0x01239000, info.end_addr)
        self.assertEqual(0x01239000 - 0x011e6000, info.size)
        # Check perms
        self.assertTrue(info.permissions.readable)
        self.assertTrue(info.permissions.writable)
        self.assertFalse(info.permissions.executable)
        self.assertTrue(info.permissions.private)
        self.assertFalse(info.permissions.shared)

        self.assertEqual(0x00003000, info.offset)

        self.assertEqual(0, info.major_dev)
        self.assertEqual(0, info.minor_dev)

        self.assertEqual(0, info.inode)

        self.assertEqual('[heap]', info.name)

        self.assertFalse(info.deleted)


    def test_shared_mem_parsing(self):
        info = parse_smaps_header(self.shared_mem_line)

        self.assertEqual(0x7f5cabdce000, info.start_addr)
        self.assertEqual(0x7f5cabe4e000, info.end_addr)
        self.assertEqual(0x7f5cabe4e000 - 0x7f5cabdce000, info.size)
        # Check perms
        self.assertTrue(info.permissions.readable)
        self.assertTrue(info.permissions.writable)
        self.assertFalse(info.permissions.executable)
        self.assertFalse(info.permissions.private)
        self.assertTrue(info.permissions.shared)

        self.assertEqual(0x0060e000, info.offset)

        self.assertEqual(0, info.major_dev)
        self.assertEqual(5, info.minor_dev)

        self.assertEqual(1605639, info.inode)

        self.assertEqual('/SYSV00000000', info.name)

        self.assertTrue(info.deleted)


class SmapsMemoryRegionParserTest(unittest.TestCase):

    def setUp(self):
        self.pid = 2345
    
    def test_parsing_a_full_smaps_memory_region(self):
        # Here's a full example of what we get in smaps for a memory region
        # The numbers are faked to make the test more useful.
        data = """7f5c8550e000-7f5c85554000 r--p 00000000 08:06 1309629   /fonts/Arial_Bold.ttf
Size:                280 kB
Rss:                 152 kB
Pss:                  86 kB
Shared_Clean:        132 kB
Shared_Dirty:         12 kB
Private_Clean:        20 kB
Private_Dirty:         1 kB
Referenced:          152 kB
Anonymous:             2 kB
AnonHugePages:         3 kB
Shared_Hugetlb:        4 kB
Private_Hugetlb:       5 kB
Swap:                  6 kB
SwapPss:               7 kB
KernelPageSize:        8 kB
MMUPageSize:           9 kB
Locked:               10 kB
VmFlags: rd mr mw me sd"""

        info = parse_smaps_memory_region(self.pid, data.split('\n'))

        self.assertEqual(self.pid, info.pid)

        # We ignore the "Size" line since it's less useful than the calculated
        # size.
        self.assertEqual(0x7f5c85554000 - 0x7f5c8550e000, info.size)

        self.assertEqual(152 * 1024, info.rss)
        self.assertEqual( 86 * 1024, info.pss)

        self.assertEqual(132 * 1024, info.shared_clean)
        self.assertEqual( 12 * 1024, info.shared_dirty)

        self.assertEqual( 20 * 1024, info.private_clean)
        self.assertEqual(  1 * 1024, info.private_dirty)

        self.assertEqual(152 * 1024, info.referenced)

        self.assertEqual(  2 * 1024, info.anonymous)
        self.assertEqual(  3 * 1024, info.anonymous_huge)

        self.assertEqual(  4 * 1024, info.shared_hugetlb)
        self.assertEqual(  5 * 1024, info.private_hugetlb)

        self.assertEqual(  6 * 1024, info.swap)
        self.assertEqual(  7 * 1024, info.swap_pss)

        self.assertEqual(  8 * 1024, info.kernel_page_size)
        self.assertEqual(  9 * 1024, info.mmu_page_size)

        self.assertEqual( 10 * 1024, info.locked)

        self.assertEqual(['rd', 'mr', 'mw', 'me', 'sd'],
                         info.vm_flags)

    def test_smaps_header_missing_filename(self):
        data='7f180c38f000-7f180c393000 rw-p 00000000 00:00 0\n'
        info = parse_smaps_memory_region(self.pid, data.split('\n'))

        self.assertEqual(0x7f180c393000 - 0x7f180c38f000, info.size)

if __name__ == '__main__':
    unittest.main()