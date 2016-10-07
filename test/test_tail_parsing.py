
from cStringIO import StringIO
import os
import tempfile
import unittest
from parsers.tail import read_tailed_files

class TailParserTest(unittest.TestCase):

    def test_reading_empty_string(self):
        _, processes, _ = read_tailed_files(StringIO(''))
        self.assertEqual(0, len(processes))

    def test_reading_empty_file(self):
        with tempfile.TemporaryFile('rb') as f:
            _, processes, _ = read_tailed_files(f)
            self.assertEqual(0, len(processes))


    def test_reading_realistic_file(self):
        with open(os.path.join(os.path.dirname(__file__), 'procfs.tail'), 'rb') as f:
            _, processes, _ = read_tailed_files(f)
            self.assertEqual(6, len(processes))


    def test_loadavg(self):
        s = StringIO('==> /proc/loadavg <==\n0.15 0.22 0.43 1/650 3914\n')
        stats = read_tailed_files(s)[0]
        self.assertEqual(0.15, stats.one_minute_load)
        self.assertEqual(0.22, stats.five_minute_load)
        self.assertEqual(0.43, stats.fifteen_minute_load)
        self.assertEqual(1, stats.running_threads)
        self.assertEqual(650, stats.total_threads)
        self.assertEqual(3914, stats.last_pid)


if __name__ == '__main__':
    unittest.main()
