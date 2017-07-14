from parsers import parser
from model import SystemStats

class Parser_loadavg(parser.Parser):
    def parse(self, data, out):
        parts = data.split()
        # Parse data from /proc/loadavg.
        # eg. 0.36 0.34 0.23 2/726 24671
        if not out.has_key('stats'):
            out['stats'] = SystemStats()
        out['stats'].one_minute_load = float(parts[0])
        out['stats'].five_minute_load = float(parts[1])
        out['stats'].fifteen_minute_load = float(parts[2])
        out['stats'].running_threads, out['stats'].total_threads = map(int, parts[3].split('/'))
        out['stats'].last_pid = int(parts[4])
        return out

