from util import LOGGER
from model import SystemStats
import parser

class Parser_uptime(parser.Parser):
    def parse(self, data, out):
        if not out.has_key('stats'):
            out['stats'] = SystemStats()
        parts = data.split()
        # Parse data from /proc/loadavg.
        # eg. 450032.49 3339822.26
        out['stats'].uptime = float(parts[0])
        out['stats'].uptime_idle = float(parts[1])
        return out
