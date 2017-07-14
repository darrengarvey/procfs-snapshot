import os
import unittest
import parsers

class MeminfoParserTest(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), 'meminfo.tail'), 'rb') as f:
            self.example = f.read()

    def test_parse_meminfo(self):
        print (self.example)

        parser = parsers.get_parser('meminfo')
        results = parser.parse(self.example, dict())
        meminfo = results['meminfo']


        self.assertEqual(45, len(meminfo.meminfo))
        self.assertEqual(20507388 * 1024, meminfo.get('MemTotal'))
        self.assertEqual(8326068 * 1024, meminfo.get('MemFree'))
        self.assertEqual(20559872 * 1024, meminfo.get('DirectMap2M'))

        self.assertEqual(1, meminfo.get('HugePages_Total'))
        self.assertEqual(2, meminfo.get('HugePages_Free'))
        self.assertEqual(3, meminfo.get('HugePages_Rsvd'))
        self.assertEqual(4, meminfo.get('HugePages_Surp'))

if __name__ == '__main__':
    unittest.main()
