import unittest
from parsers.loadavg import parse_loadavg
from model import SystemStats

class TailParserTest(unittest.TestCase):

    def setUp(self):
        self.example = '0.15 0.22 0.43 1/650 3914'

    def test_correct_type_must_be_passed_into_parse_loadavg(self):
        self.assertRaises(TypeError, parse_loadavg, None, self.example)

    def test_loadavg_parsing(self):
        """Simple format, simple test"""
        stats = SystemStats()
        parse_loadavg(stats, self.example)
        self.assertEqual(0.15, stats.one_minute_load)
        self.assertEqual(0.22, stats.five_minute_load)
        self.assertEqual(0.43, stats.fifteen_minute_load)
        self.assertEqual(1, stats.running_threads)
        self.assertEqual(650, stats.total_threads)
        self.assertEqual(3914, stats.last_pid)


if __name__ == '__main__':
    unittest.main()
