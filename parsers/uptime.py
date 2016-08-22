from util import LOGGER
from model import SystemStats


def parse_uptime(stats, data):
    if not isinstance(stats, SystemStats):
        raise TypeError('%s is not of type SystemStats' % type(stats))

    parts = data.split()
    # Parse data from /proc/loadavg.
    # eg. 450032.49 3339822.26
    stats.uptime = float(parts[0])
    stats.uptime_idle = float(parts[1])