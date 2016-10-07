import re
from smaps import parse_smaps_memory_region, is_memory_region_header

from model import SystemStats, Process, Thread, ProcessList, MemoryStats
from util import LOGGER

import parsers


def _save_smaps_region(output, output2, pid, data):
    data = data.strip()

    if data != '':
        region = parse_smaps_memory_region(pid, data.split('\n'))
        if region:
            output.append(region)
            output2.append(region)
    else:
        # It's OK if the smaps file is empty.
        #print ('Skipping empty smaps region')
        pass


def _save_stat(obj, res):
    if not (isinstance(obj, Process) or isinstance(obj, Thread)):
        raise TypeError('%s is not of type Process or Thread' % type(obj))

    obj.comm = res.get('comm')
    obj.minor_faults = res.get('minflt')
    obj.major_faults = res.get('majflt')
    obj.user_time = res.get('utime')
    obj.system_time = res.get('stime')
    obj.start_time = res.get('starttime')

def _parse_section(section_name, current_process, current_thread, data, out):

    try:
        parser = parsers.get_parser(section_name)
        parser.parse(data, out)
    except:
        pass

    if current_thread and section_name == 'stat':
        _save_stat(current_thread, out['stat'])
    elif current_process and section_name != '':
        # Hit a new file, consolidate what we have so far.
        if 'smaps' == section_name:
            _save_smaps_region(current_process.maps, out['meminfo'], current_process.pid, data)
        elif 'cmdline' == section_name:
            # Some command lines have a number of empty arguments. Ignore
            # that because it's not interesting here.
            current_process.argv = filter(len, data.strip().split('\0'))
        elif 'stat' == section_name:
            _save_stat(current_process, out['stat'])
        else:
            LOGGER.error('Unrecognised section name: %s' % section_name)


def read_tailed_files(stream):
    section_name = ''
    data = ''
    processes = ProcessList()
    current_process = None
    current_thread = None
    out = {}
    out['stats'] = SystemStats()
    out['meminfo'] = MemoryStats()

    for line in stream:
        LOGGER.debug('Got line: %s' % line)
        if line == '':
            continue
        # tail gives us lines like:
        #
        #     ==> /proc/99/smaps <==
        #
        # between files
        elif line.startswith('==>'):
            _parse_section(section_name, current_process, current_thread, data, out)
            data = ''
            section_name = ''
            current_process = None
            current_thread = None

            if '/proc/loadavg' in line:
                section_name = 'loadavg'
                continue
            elif '/proc/uptime' in line:
                section_name = 'uptime'
                continue
            elif '/proc/vmstat' in line:
                section_name = 'vmstat'
                continue
            elif '/proc/net/stat' in line:
                # We don't care about this entry. Skip it.
                continue

            # Now parse the new line.
            match = re.match(r'==> /proc/([0-9]+)/([\w]+) <==', line)
            if match is None:
                if any(x in line for x in ['/proc/stat', '/proc/self/', '/proc/thread-self/']):
                    # We just ignore these entries, interetesting as they are,
                    # for now.
                    pass
                elif '/proc/meminfo' in line:
                    section_name = 'meminfo'
                else:
                    match = re.match(r'==> /proc/([0-9]+)/task/([0-9]+)/stat <==', line)
                    if match is None:
                        # The line might not be parsed here. There are a few
                        LOGGER.warn('Unrecognised line, skipping: %s' % line)
                    else:
                        section_name = 'stat'
                        pid=int(match.group(1)) # process id
                        tid=int(match.group(2)) # thread id
                        current_thread = processes.get(pid).get_thread(tid)
            else:
                section_name = match.group(2)
                current_process = processes.get(pid=int(match.group(1)))

        elif current_process and section_name == 'smaps' and is_memory_region_header(line):
            # We get here on reaching a new memory region in a smaps file.
            _save_smaps_region(current_process.maps, out['meminfo'], current_process.pid, data)
            data = line
        elif section_name != '':
            data += "\n" + line
        else:
            LOGGER.debug('Skipping line: %s' % line)

    # We've hit the end, parse the section we were in.
    _parse_section(section_name, current_process, current_thread, data, out)

    return out['stats'], processes, out['meminfo']
