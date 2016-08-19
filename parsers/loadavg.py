from util import LOGGER
from model import SystemStats

def parse_loadavg(stats, data):
    if not isinstance(stats, SystemStats):
        raise TypeError('%s is not of type SystemStats' % type(stats))

    parts = data.split()
    # Parse data from /proc/loadavg.
    # eg. 0.36 0.34 0.23 2/726 24671
    stats.one_minute_load = float(parts[0])
    stats.five_minute_load = float(parts[1])
    stats.fifteen_minute_load = float(parts[2])
    stats.running_threads, stats.total_threads = map(int, parts[3].split('/'))
    stats.last_pid = int(parts[4])
