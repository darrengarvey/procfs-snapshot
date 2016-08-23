from util import LOGGER
from model import SystemStats


_interesting_vmstat_vars = [
    'nr_free_pages',
    'pgpgin',
    'pgpgout',
    'pswpin',
    'pswpout',
    'pgalloc_normal',
    'pgfree',
    'pgactivate',
    'pgdeactivate',
    'pgfault',
    'pgmajfault',
    'pageoutrun',
    'allocstall',
]

def parse_vmstat(stats, data):
    if not isinstance(stats, SystemStats):
        raise TypeError('%s is not of type SystemStats' % type(stats))

    # Parse data from /proc/vmstat.
    for line in data.split('\n'):
        parts = line.split()
        if len(parts) and parts[0] in _interesting_vmstat_vars:
            stats.vmstats[parts[0]] = int(parts[1])
