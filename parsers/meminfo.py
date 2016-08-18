import re
from util import LOGGER

# Decent documentation of /proc/meminfo:
# https://www.centos.org/docs/5/html/5.2/Deployment_Guide/s2-proc-meminfo.html
# https://access.redhat.com/solutions/406773

# An example is in test/proc-meminfo.tail

def parse_meminfo(stats, data):
    for line in data:
        parts = re.split('[ :]+', line.strip())
        if len(parts) < 2:
            LOGGER.debug('Skipping meminfo line that is too short: %s' % line)
        else:
            stats.meminfo[parts[0]] = int(parts[1]) * 1024