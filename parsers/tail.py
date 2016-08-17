import re
from smaps import parse_smaps_memory_region


class Process(object):
    def __init__(self, pid, argv=[]):
        self.pid = pid
        self.argv = argv
        # Memory maps in the process' address space.
        self.maps = []

    @property
    def name(self):
        return self.argv[0]


class ProcessList(object):
    def __init__(self):
        self.processes = {}

    def get(self, pid):
        try:
            return self.processes[pid]
        except KeyError:
            proc = Process(pid)
            self.processes[pid] = proc
            return proc

    def __len__(self):
        return len(self.processes)


def read_tailed_files(stream):
    section_name = ''
    data = ''
    processes = ProcessList()
    current_process = None

    print ('*****')

    #while True:
    for line in stream:
        #line = stream.readline()
        #print ('line', line)
        if line == '':
            continue
        # tail gives us lines like:
        #
        #     ==> /proc/99/smaps <==
        #
        # between files
        elif line.startswith('==>'):
            if current_process and section_name != '':
                # First finish off the previous section.
                if 'smaps' == section_name:
                    print ('got smaps entry: %s' % data)
                    data = data.strip()

                    if data != '':
                        region = parse_smaps_memory_region(data.split('\n'))
                        current_process.maps.append(region)
                    else:
                        # It's OK if the smaps file is empty.
                        print ('Skipping empty smaps file')
                elif 'cmdline' == section_name:
                    # Some command lines have a number of empty arguments. Ignore
                    # that because it's not interesting here.
                    current_process.argv = filter(len, data.strip().split('\0'))
                    print ('got cmdline: %s' % current_process.argv)
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
                    print ('Error parsing tail line: %s' % line)
            else:
                section_name = match.group(2)
                current_process = processes.get(pid=int(match.group(1)))

        elif section_name != '':
            data += line
        else:
            print ('Skipping line: %s' % line)

    print ('#####')
    return processes