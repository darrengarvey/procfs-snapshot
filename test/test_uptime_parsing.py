import unittest
from parsers.uptime import parse_uptime
from model import SystemStats

class UptimeParserTest(unittest.TestCase):

    def setUp(self):
        self.example = '84983.36 434057.28'

    def test_correct_type_must_be_passed_into_parse_loadavg(self):
        self.assertRaises(TypeError, parse_uptime, None, self.example)

    def test_process_stat_parsing(self):
        stats = SystemStats()
        parse_uptime(stats, self.example)
        self.assertEqual(84983.36, stats.uptime)
        self.assertEqual(434057.28, stats.uptime_idle)


if __name__ == '__main__':
    unittest.main()
