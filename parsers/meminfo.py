import re
from util import LOGGER
from model import SystemStats

# Decent documentation of /proc/meminfo:
# https://www.centos.org/docs/5/html/5.2/Deployment_Guide/s2-proc-meminfo.html
# https://access.redhat.com/solutions/406773

# An example is in test/meminfo.tail

def parse_meminfo(stats, data):
    if not isinstance(stats, SystemStats):
        raise TypeError('%s is not of type SystemStats' % type(stats))

    for line in data.split('\n'):
        parts = re.split('[ :]+', line.strip())
        if len(parts) < 2:
            LOGGER.debug('Skipping meminfo line that is too short: %s' % line)
        elif len(parts) == 2:
            # This is a number. eg HugePages_Total, HugePages_Free,
            # HugePages_Rsvd, HugePages_Surp
            stats.meminfo[parts[0]] = int(parts[1])
        else:
            # These are sizes, with unit kB in the third column.
            # eg. AnonHugePages:   2355200 kB
            stats.meminfo[parts[0]] = int(parts[1]) * 1024