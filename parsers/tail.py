import re
from smaps import parse_smaps_memory_region, is_memory_region_header
from model import Process, ProcessList, MemoryRegionList
from util import LOGGER

def _save_smaps_region(output, output2, data):
    data = data.strip()

    if data != '':
        region = parse_smaps_memory_region(data.split('\n'))
        output.append(region)
        output2.append(region)
    else:
        # It's OK if the smaps file is empty.
        #print ('Skipping empty smaps region')
        pass


def read_tailed_files(stream):
    section_name = ''
    data = ''
    processes = ProcessList()
    maps = MemoryRegionList()
    current_process = None

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
            if current_process and section_name != '':
                # Hit a new file, consolidate what we have so far.
                if 'smaps' == section_name:
                    _save_smaps_region(current_process.maps, maps, data)
                elif 'cmdline' == section_name:
                    # Some command lines have a number of empty arguments. Ignore
                    # that because it's not interesting here.
                    current_process.argv = filter(len, data.strip().split('\0'))
                    #print ('got cmdline: %s' % current_process.argv)
            data = ''
            section_name = ''

            # Now parse the new line.
            match = re.match(r'==> /proc/([0-9]+)/([\w]+) <==', line)
            if match is None:
                if '/proc/self/' in line or '/proc/thread-self/' in line:
                    # We just ignore these entries.
                    pass
                else:
                    # There's probably been an error in the little state machine.
                    LOGGER.error('Error parsing tail line: %s' % line)
            else:
                section_name = match.group(2)
                #print ('Parsing new file: %s' % line)
                current_process = processes.get(pid=int(match.group(1)))

        elif current_process and section_name == 'smaps' and is_memory_region_header(line):
            # We get here on reaching a new memory region in a smaps file.
            _save_smaps_region(current_process.maps, maps, data)
            data = line
        elif section_name != '':
            data += line
        else:
            LOGGER.debug('Skipping line: %s' % line)

    return processes, maps