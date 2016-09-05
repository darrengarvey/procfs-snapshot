import os
import unittest
from parsers.meminfo import parse_meminfo
from model import MemoryStats

class MeminfoParserTest(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), 'meminfo.tail'), 'rb') as f:
            self.example = f.read()

    def test_parse_meminfo(self):
        print (self.example)
        stats = MemoryStats()
        parse_meminfo(stats, self.example)

        self.assertEqual(45, len(stats.meminfo))
        self.assertEqual(20507388 * 1024, stats.get('MemTotal'))
        self.assertEqual(8326068 * 1024, stats.get('MemFree'))
        self.assertEqual(20559872 * 1024, stats.get('DirectMap2M'))

        self.assertEqual(1, stats.get('HugePages_Total'))
        self.assertEqual(2, stats.get('HugePages_Free'))
        self.assertEqual(3, stats.get('HugePages_Rsvd'))
        self.assertEqual(4, stats.get('HugePages_Surp'))

if __name__ == '__main__':
    unittest.main()
