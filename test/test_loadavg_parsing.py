import unittest
import parsers

class Test_Parser_loadavg(unittest.TestCase):
    def setUp(self):
        self.example = '0.15 0.22 0.43 1/650 3914'

    def test_parsing(self):
        """Simple format, simple test"""
        parser = parsers.get_parser('loadavg')
        results = dict()
        parser.parse(self.example, results)
        stats = results['stats']
        self.assertEqual(0.15, stats.one_minute_load)
        self.assertEqual(0.22, stats.five_minute_load)
        self.assertEqual(0.43, stats.fifteen_minute_load)
        self.assertEqual(1, stats.running_threads)
        self.assertEqual(650, stats.total_threads)
        self.assertEqual(3914, stats.last_pid)

if __name__ == '__main__':
    unittest.main()
