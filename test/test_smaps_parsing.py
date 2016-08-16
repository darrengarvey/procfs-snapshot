
import unittest
from parsers.smaps import (
    parse_smaps_header
)

class SmapsParserTest(unittest.TestCase):
    
    def setUp(self):
        import os
        with open(os.path.join(os.path.dirname(__file__), 'firefox.smaps'), 'rb') as f:
            self.data = f.read()
        # Another bunch of example lines for various cases.
        self.process_line = '55917d4f7000-55917d514000 r-xp 00000000 08:06 542715                     /usr/lib/firefox/firefox'
        self.lib_line = '7f5c3f7fd000-7f5c3f7fe000 rw-p 00049000 08:06 532533                     /usr/lib/x86_64-linux-gnu/libopus.so.0.5.2'
        self.heap_line = '011e6000-01239000 rw-p 00000000 00:00 0                                  [heap]'
        self.stack_line = '7ffefddd2000-7ffefde0d000 rw-p 00000000 00:00 0                          [stack]'
        self.vdso_line = '7ffefdebc000-7ffefdebe000 r-xp 00000000 00:00 0                          [vdso]'
        self.shared_mem_line = '7f5cabdce000-7f5cabe4e000 rw-s 00000000 00:05 1605639                    /SYSV00000000 (deleted)'
        self.anonymous_line = '7f5cabd5d000-7f5cabd61000 rw-p 00000000 00:00 0 '

    def test_heap_parsing(self):
        info = parse_smaps_header(self.heap_line)
        self.assertEqual(int('011e6000', 16), info.start_addr)
        self.assertEqual(int('01239000', 16), info.end_addr)
        self.assertEqual(int('01239000', 16) - int('011e6000', 16), info.size)
        # Check perms
        self.assertTrue(info.permissions.readable)
        self.assertTrue(info.permissions.writable)
        self.assertFalse(info.permissions.executable)
        self.assertTrue(info.permissions.private)
        self.assertFalse(info.permissions.shared)

        self.assertEqual('[heap]', info.name)




if __name__ == '__main__':
    unittest.main()