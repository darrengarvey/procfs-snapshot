from util import LOGGER
from model import Process, Thread

def parse_stat(obj, data):
    if not (isinstance(obj, Process) or isinstance(obj, Thread)):
        raise TypeError('%s is not of type Process or Thread' % type(obj))

    parts = data.split()
    # Parse data from /proc/*/stat or /proc/*/task/*/stat.
    # We only collect a subset of this to reduce the amount of data that
    # needs to be collected. More can be collected if it's useful.
    # eg. (sqlitebrowser) 46582 70 6605 429 8244323

    # comm %s
    # (2) The filename of the executable, in parentheses. This is visible
    # whether or not the executable is swapped out.
    # Note that this is also the thread name, if set.
    obj.comm = parts[0][1:-1] # omit the brackets

    # minflt %lu
    # (10) The number of minor faults the process has made which have not
    # required loading a memory page from disk.
    obj.minor_faults = int(parts[1])

    # majflt %lu
    # (12) The number of major faults the process has made which have
    # required loading a memory page from disk.
    obj.major_faults = int(parts[2])

    # utime %lu
    # (14) Amount of time that this process has been scheduled in user
    # mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).
    # This includes guest time, guest_time (time spent running a virtual
    # CPU, see below), so that applications that are not aware of the
    # guest time field do not lose that time from their calculations.
    obj.user_time = int(parts[3])

    # stime %lu
    # (15) Amount of time that this process has been scheduled in kernel
    # mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).
    obj.system_time = int(parts[4])

    # starttime %llu (was %lu before Linux 2.6) 
    # (22) The time the process started after system boot. In kernels
    # before Linux 2.6, this value was expressed in jiffies. Since Linux
    # 2.6, the value is expressed in clock ticks (divide by
    #   ).
    obj.start_time = int(parts[5])
