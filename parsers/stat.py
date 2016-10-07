import parser
from model import Process, Thread

proc_stat_format = {
    1: ('pid', '%d', 'The process ID.'),
    2: ('comm', '%s', 'The  filename of the executable, in parentheses.  This is visible whether or not the executable is swapped out.'),
    3: ('state', '%c', 'One of the following characters, indicating process state:', {
        'R': 'Running',
        'S': 'Sleeping',
        'D': 'Waiting',
        'Z': 'Zombie',
        'T': 'Stopped',
        't': 'Tracing stop',
        'W': 'Paging',
        'X': 'Dead',
        'x': 'Dead',
        'K': 'Wakekill',
        'W': 'Waking',
        'P': 'Parked'}),
    4: ('ppid', '%d', 'The PID of the parent of this process.'),
    5: ('pgrp', '%d', 'The process group ID of the process.'),
    6: ('session', '%d', 'The session ID of the process.'),
    7: ('tty_nr', '%d', 'The controlling terminal of the  process.'),
    8: ('tpgid', '%d', 'The ID of the foreground process group of the controlling  terminal of the process.'),
    9: ('flags', '%u', 'The  kernel  flags  word of the process. Details depend on the kernel version.'),
    10: ('minflt', '%lu', 'The  number of minor faults the process has made which have not required loading a memory page from disk.'),
    11: ('cminflt', '%lu', 'The number of minor faults that the process\'s waited-for  children have made.'),
    12: ('majflt', '%lu', 'The  number  of  major  faults  the process has made which have required loading a memory page from disk.'),
    13: ('cmajflt', '%lu', 'The number of major faults that the process\'s waited-for  children have made.'),
    14: ('utime', '%lu', 'Amount  of  time  that  this process has been scheduled in user mode, measured in clock ticks.'),
    15: ('stime', '%lu', 'Amount of time that this process has been scheduled  in  kernel mode, measured in clock ticks.'),
    16: ('cutime', '%ld', 'Amount  of  time  that  this process\'s waited-for children have been scheduled in user mode, measured in clock ticks.'),
    17: ('cstime', '%ld', 'Amount  of  time  that  this process\'s waited-for children have been scheduled in kernel mode, measured in clock ticks.'),
    18: ('priority', '%ld', 'For processes running a real-time scheduling policy.'),
    19: ('nice', '%ld', 'The nice value (see setpriority(2), a value in  the  range  19(low priority) to -(high priority).'), 
    20: ('num_threads', '%ld', 'Number  of  threads  in this process'),
    21: ('itrealvalue', '%ld', 'The  time  in  jiffies  before  the next SIGALRM is sent to the process due to an interval timer'),
    22: ('starttime', '%llu', 'The  time  the  process  started after system boot.'),
    23: ('vsize', '%lu', 'Virtual memory size in bytes.'),
    24: ('rss', '%ld', 'Resident Set Size: number of pages the process has in real memory.'),
    25: ('rsslim', '%lu', 'Current  soft limit in bytes on the rss of the process; see the description of RLIMIT_RSS in getrlimit(2).'),
    26: ('startcode', '%lu', 'The address above which program text can run.'),
    27: ('endcode', '%lu', 'The address below which program text can run.'),
    28: ('startstack', '%lu', 'The address of the start (i.e., bottom) of the stack.'),
    29: ('kstkesp', '%lu', 'The current value of ESP (stack pointer)), as found in the  kernel stack page for the process.'),
    30: ('kstkeip', '%lu', 'The current EIP (instruction pointer).'),
    31: ('signal', '%lu', 'The  bitmap  of pending signals, displayed as a decimal number. Obsolete, because it does not provide information on  real-time'),
    32: ('blocked', '%lu', 'The  bitmap  of blocked signals, displayed as a decimal number. Obsolete, because it does not provide information on  real-time'),
    33: ('sigignore', '%lu', 'The  bitmap  of ignored signals, displayed as a decimal number. Obsolete, because it does not provide information on  real-time'),
    34: ('sigcatch', '%lu', 'The  bitmap  of  caught signals, displayed as a decimal number. Obsolete, because it does not provide information on  real-time'),
    35: ('wchan', '%lu', 'This  is  the "channel" in which the process is waiting.'),
    36: ('nswap', '%lu', 'Number of pages swapped (not maintained).'),
    37: ('cnswap', '%lu', 'Cumulative nswap for child processes (not maintained).'),
    38: ('exit_signal', '%d', 'Signal to be sent to parent when we die.'),
    39: ('processor', '%d', 'CPU number last executed on.'),
    40: ('rt_priority', '%u', 'Real-time scheduling priority.'),
    41: ('policy', '%u', 'Scheduling policy (see  sched_setscheduler(2)).'),
    42: ('delayacct_blkio_ticks', '%llu', 'Aggregated block I/O delays, measured in clock ticks (centiseconds).'),
    43: ('guest_time', '%lu', 'Guest time of the process (time spent running a virtual CPU for a  guest  operating system)), measured in clock ticks'),
    44: ('cguest_time', '%ld', 'Guest time of the process\'s children, measured in  clock  ticks divide by sysconf(SC_CLK_TCK)).'),
    45: ('start_data', '%lu', 'Address above which program initialized and uninitialized (BSS) data are placed.'),
    46: ('end_data', '%lu', 'Address below which program initialized and uninitialized (BSS) data are placed.'),
    47: ('start_brk', '%lu', 'Address above which program heap can be expanded with brk(2).'),
    48: ('arg_start', '%lu', 'Address  above  which program command-line arguments (argv) are placed.'),
    49: ('arg_end', '%lu', 'Address below program command-line arguments (argv) are placed.'),
    50: ('env_start', '%lu', 'Address above which program environment is placed.'),
    51: ('env_end', '%lu', 'Address below which program environment is placed.'),
    52: ('exit_code', '%d', 'The thread\'s exit status in the form reported by waitpid(2).')}


def convert(formatter, value):
    if not formatter.startswith('%'):
        raise TypeError('Wrong formatter? : [{0}]'.format(formatter))
    if formatter[1] in ['d', 'l', 'u', 'i']:
        return int(value)
    elif formatter[1] in ['f', 'x']:
        return float(value)
    elif formatter[1] in ['s', 'c']:
        return value.strip('()')
    else:
        raise TypeError('Unknown format? : [{0}]'.format(formatter[1:]))


class Parser_stat(parser.Parser):
    def parse(self, data, out):
        if not out.has_key('proc_stat'):
            out['proc_stat'] = dict()
        parts = data.split()

        fmts = proc_stat_format

        for i in range(1, len(parts) + 1):
            fmt = fmts[i]
            name = fmt[0]
            formatter = fmt[1]
            try:
                value = convert(formatter, parts[i - 1])
                out['proc_stat'][name] = value
                if len(fmt) > 3:
                    out['proc_stat'][name] = fmt[3].get(value, value)
            except:
                pass
        return out



def parse_stat(obj, data):
    if not (isinstance(obj, Process) or isinstance(obj, Thread)):
        raise TypeError('%s is not of type Process or Thread' % type(obj))

    parser = Parser_stat()
    res = parser.parse(data, dict())['proc_stat']

    # comm %s
    # (2) The filename of the executable, in parentheses. This is visible
    # whether or not the executable is swapped out.
    # Note that this is also the thread name, if set.
    obj.comm = res['comm']

    # minflt %lu
    # (10) The number of minor faults the process has made which have not
    # required loading a memory page from disk.
    obj.minor_faults = res['minflt']

    # majflt %lu
    # (12) The number of major faults the process has made which have
    # required loading a memory page from disk.
    obj.major_faults = res['majflt']

    # utime %lu
    # (14) Amount of time that this process has been scheduled in user
    # mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).
    # This includes guest time, guest_time (time spent running a virtual
    # CPU, see below), so that applications that are not aware of the
    # guest time field do not lose that time from their calculations.
    obj.user_time = res['utime']

    # stime %lu
    # (15) Amount of time that this process has been scheduled in kernel
    # mode, measured in clock ticks (divide by sysconf(_SC_CLK_TCK)).
    obj.system_time = res['stime']

    # starttime %llu (was %lu before Linux 2.6) 
    # (22) The time the process started after system boot. In kernels
    # before Linux 2.6, this value was expressed in jiffies. Since Linux
    # 2.6, the value is expressed in clock ticks (divide by
    #   ).
    obj.start_time = res['starttime']
