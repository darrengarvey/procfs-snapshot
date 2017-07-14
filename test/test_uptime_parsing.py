import unittest
import parsers

class UptimeParserTest(unittest.TestCase):

    def setUp(self):
        self.example = '84983.36 434057.28'

    def test_process_stat_parsing(self):
        parser = parsers.get_parser('uptime')
        stats = parser.parse(self.example, dict())['stats']
        self.assertEqual(84983.36, stats.uptime)
        self.assertEqual(434057.28, stats.uptime_idle)

if __name__ == '__main__':
    unittest.main()
