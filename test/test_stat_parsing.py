import unittest
from parsers.stat import parse_stat
from model import Process

class StatParserTest(unittest.TestCase):

    def setUp(self):
        self.example = '(sqlitebrowser) 46582 70 6605 429 8244322'

    def test_correct_type_must_be_passed_into_parse_loadavg(self):
        self.assertRaises(TypeError, parse_stat, None, self.example)

    def test_process_stat_parsing(self):
        process = Process(pid=1234)
        parse_stat(process, self.example)
        self.assertEqual('sqlitebrowser', process.comm)
        self.assertEqual(46582, process.minor_faults)
        self.assertEqual(70, process.major_faults)
        self.assertEqual(6605, process.user_time)
        self.assertEqual(429, process.system_time)
        self.assertEqual(8244322, process.start_time)


if __name__ == '__main__':
    unittest.main()
