
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

if __name__ == '__main__':
    unittest.main()
