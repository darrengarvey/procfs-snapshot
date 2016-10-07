import unittest
import parsers

class StatParserTest(unittest.TestCase):

    def setUp(self):
        # The format is the same for both processes and threads.
        self.example = '3103 (tracker-miner-f) S 2944 2944 2944 0 -1 4194304 3359 0 14 0 502 57 0 0 39 19 4 0 22414 730193920 5331 18446744073709551615 4194304 4311892 140732085204768 140732085204240 139660743339661 0 0 4096 16386 0 0 0 17 5 0 0 6 0 0 6409568 6413320 39149568 140732085209372 140732085209406 140732085209406 140732085211094 0'
        self.expected = {'majflt': 14, 'rss': 5331, 'cguest_time': 0, 'cstime': 0, 'pid': 3103,
                         'session': 2944, 'startstack': 140732085204768, 'env_end': 140732085211094,
                         'startcode': 4194304, 'cmajflt': 0, 'blocked': 0, 'arg_start': 140732085209372,
                         'exit_signal': 17, 'minflt': 3359, 'rsslim': 18446744073709551615L, 'nswap': 0,
                         'exit_code': 0, 'priority': 39, 'state': 'Sleeping',
                         'delayacct_blkio_ticks': 6, 'policy': 0, 'rt_priority': 0, 'ppid': 2944,
                         'arg_end': 140732085209406, 'nice': 19, 'cutime': 0, 'end_data': 6413320,
                         'endcode': 4311892, 'wchan': 0, 'num_threads': 4, 'sigcatch': 16386,
                         'comm': 'tracker-miner-f', 'stime': 57, 'start_data': 6409568, 'sigignore': 4096,
                         'tty_nr': 0, 'kstkeip': 139660743339661, 'guest_time': 0, 'utime': 502,
                         'signal': 0, 'env_start': 140732085209406, 'pgrp': 2944, 'flags': 4194304,
                         'tpgid':-1, 'itrealvalue': 0, 'kstkesp': 140732085204240, 'cnswap': 0,
                         'starttime': 22414, 'cminflt': 0, 'start_brk': 39149568, 'vsize': 730193920,
                         'processor': 5}

    def test_stat_parsing(self):
        parser = parsers.get_parser('stat')
        res = parser.parse(self.example, dict())['proc_stat']
        self.assertEqual(res['comm'], 'tracker-miner-f', 'comm not as expected? {0}'.format(res['comm']))
        self.assertEqual(res, self.expected, 'Did not parse /proc/stat correctly?')

if __name__ == '__main__':
    unittest.main()
