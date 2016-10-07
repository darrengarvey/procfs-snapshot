class SystemStats(object):
    def __init__(self):
        self.uptime = 0.
        self.uptime_idle = 0.
        self.one_minute_load = 0.
        self.five_minute_load = 9.
        self.fifteen_minute_load = 0.
        self.running_threads = 0
        self.total_threads = 0
        self.last_pid = 0
        self.vmstats = {}

class SmapsPermissions(object):
    def __init__(self):
        self.readable = False
        self.writable = False
        self.executable = False
        self.shared = False
        self.private = False

class MemoryRegion(object):
    def __init__(self, free):
        self.free = free
        self.pid = -1
        self.start_addr = 0L
        self.end_addr = 0L
        self.offset = 0L
        self.permissions = SmapsPermissions()
        self.name = ''
        self.rss = 0
        self.pss = 0
        self.shared_clean = 0
        self.shared_dirty = 0
        self.private_clean = 0
        self.private_dirty = 0
        self.referenced = 0
        self.anonymous = 0
        self.anon_huge_pages = 0
        self.shared_hugetlb = 0
        self.private_hugetlb = 0
        self.swap = 0
        self.swap_pss = 0
        self.kernel_page_size = 0
        self.mmu_page_size = 0
        self.locked = 0
        self.vm_flags = []

    @property
    def size(self):
        return self.end_addr - self.start_addr

    @property
    def readonly(self):
        return (self.permissions.readable and
                not self.permissions.writable and
                not self.permissions.executable)

    @property
    def rw(self):
        return (self.permissions.readable and
                self.permissions.writable and
                not self.permissions.executable)

    @property
    def rx(self):
        return (self.permissions.readable and
                not self.permissions.writable and
                self.permissions.executable)

    @property
    def rwx(self):
        return (self.permissions.readable and
                self.permissions.writable and
                self.permissions.executable)

    @property
    def ro_shared(self):
        return self.readonly and self.permissions.shared

    @property
    def ro_private(self):
        return self.readonly and self.permissions.private

    @property
    def rw_shared(self):
        return self.rw and self.permissions.shared

    @property
    def rw_private(self):
        return self.rw and self.permissions.private

    @property
    def rx_shared(self):
        return self.rx and self.permissions.shared

    @property
    def rx_private(self):
        return self.rx and self.permissions.private

    @property
    def rwx_shared(self):
        return self.rwx and self.permissions.shared

    @property
    def rwx_private(self):
        return self.rwx and self.permissions.private

    def __lt__(self, other):
        """MemoryRegions are sorted by their position in memory"""
        return self.start_addr < other.start_addr

    def __gt__(self, other):
        """MemoryRegions are sorted by their position in memory"""
        return self.start_addr > other.start_addr


class MemoryStats(object):
    def __init__(self):
        self.maps = []
        self.meminfo = {}

    def append(self, memory_region):
        # Don't sort now, sort when getting an iterator.
        self.maps.append(memory_region)

    def get(self, key, default=None):
        return self.meminfo.get(key, default)

    def __iter__(self):
        # Always return memory regions in sorted order
        self.maps.sort()
        return self.maps

    def __len__(self):
        return len(self.maps)

    def __repr__(self):
        if len(self.maps) == 0:
            return """<MemoryStats: empty>"""
        else:
            self.maps.sort()
            return """<MemoryStats: regions={}, from=0x{:02x}, to=0x{:02x}>""".format(
                len(self.maps), self.maps[0].start_addr, self.maps[-1].end_addr)


class Library(object):
    def __init__(self, name, inode, snapshot_id):
        self.name = name
        self.inode = inode
        self.snapshot_id = snapshot_id
        self.pss = 0
        self.num_fragments = 0
        self.shared_count = 0


class Thread(object):
    def __init__(self, thread_id):
        self.process_id = 0
        self.thread_id = thread_id
        # For documentation of these see parsers/stat.py
        self.comm = ''
        self.minor_faults = 0
        self.major_faults = 0
        self.user_time = 0
        self.system_time = 0
        self.start_time = 0


# Private helper functions
def _is_stack(mem):
    # stack space can show up as [stack] or [stack:1234]
    return mem.name[:6] == '[stack'

def _is_heap(mem):
    # stack space can show up as [stack] or [stack:1234]
    return mem.name == '[heap]'

def _not_heap_or_stack(mem):
    # stack space can show up as [stack] or [stack:1234]
    return not mem.name[:6] in ['[heap]', '[stack']


class Process(object):
    def __init__(self, pid, argv=[]):
        self.pid = pid
        self.argv = argv
        # Memory maps in the process' address space.
        self.maps = []
        self.threads = {}
        # For documentation of these see parsers/stat.py
        self.comm = ''
        self.minor_faults = 0
        self.major_faults = 0
        self.user_time = 0
        self.system_time = 0
        self.start_time = 0

    def get_thread(self, thread_id):
        try:
            return self.threads[thread_id]
        except KeyError:
            thread = Thread(thread_id)
            self.threads[thread_id] = thread
            return thread

    @property
    def name(self):
        return self.argv[0]

    @property
    def num_fragments(self):
        return len(self.maps)

    @property
    def pss(self):
        return sum([mem.pss for mem in self.maps])

    @property
    def heap(self):
        return sum([mem.pss for mem in self.maps if _is_heap(mem)])

    @property
    def stack(self):
        return sum([mem.pss for mem in self.maps if _is_stack(mem)])

    @property
    def ro_shared(self):
        return sum([mem.pss for mem in self.maps
                    if mem.ro_shared and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def ro_shared_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.ro_shared and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def ro_private(self):
        return sum([mem.pss for mem in self.maps
                    if mem.ro_private and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def ro_private_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.ro_private and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rw_shared(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rw_shared and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def rw_shared_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rw_shared and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rw_private(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rw_private and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def rw_private_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rw_private and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rx_shared(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rx_shared and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def rx_shared_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rx_shared and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rx_private(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rx_private and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def rx_private_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rx_private and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rwx_shared(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rwx_shared and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rwx_shared_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rwx_shared and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def rwx_private(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rwx_private and _not_heap_or_stack(mem)
                    and mem.inode == 0])

    @property
    def rwx_private_file(self):
        return sum([mem.pss for mem in self.maps
                    if mem.rwx_private and _not_heap_or_stack(mem)
                    and mem.inode != 0])

    @property
    def shared_clean(self):
        return sum([mem.shared_clean for mem in self.maps])

    @property
    def shared_dirty(self):
        return sum([mem.shared_dirty for mem in self.maps])

    @property
    def private_clean(self):
        return sum([mem.private_clean for mem in self.maps])

    @property
    def private_dirty(self):
        return sum([mem.private_dirty for mem in self.maps])

    @property
    def referenced(self):
        return sum([mem.referenced for mem in self.maps])

    @property
    def anonymous(self):
        return sum([mem.anonymous for mem in self.maps])


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

    def __iter__(self):
        for process in self.processes.values():
            yield process
