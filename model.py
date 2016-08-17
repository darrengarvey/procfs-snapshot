
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
        self.start_addr = 0
        self.end_addr = 0
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
        self.anonymous_huge = 0
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

    def __lt__(self, other):
        """MemoryRegions are sorted by their position in memory"""
        return self.start_addr < other.start_addr

    def __gt__(self, other):
        """MemoryRegions are sorted by their position in memory"""
        return self.start_addr > other.start_addr

class MemoryRegionList(object):
    def __init__(self):
        self.maps = []

    def append(self, memory_region):
        # Don't sort now, sort when getting an iterator.
        self.maps.append(memory_region)

    def __iter__(self):
        # Always return memory regions in sorted order
        self.maps.sort()
        return self.maps

    def __len__(self):
        return len(self.maps)

    def __repr__(self):
        self.maps.sort()
        return """<MemoryRegionList: len={}, from=0x{:02x}, to=0x{:02x}>""".format(
            len(self.maps), self.maps[0].start_addr, self.maps[-1].end_addr)

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
