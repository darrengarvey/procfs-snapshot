
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


class MemoryStats(object):
    def __init__(self):
        # Decent documentation of /proc/meminfo:
        # https://www.centos.org/docs/5/html/5.2/Deployment_Guide/s2-proc-meminfo.html
        # https://access.redhat.com/solutions/406773
        self.maps = []
        self.meminfo = {}
        self.total = 0
        self.free = 0
        self.buffers = 0
        self.cached = 0
        self.swap_cached = 0
        self.active = 0
        self.inactive = 0
        self.active_anon = 0
        self.inactive_anon = 0
        self.active_file = 0
        self.inactive_file = 0
        self.unevictable = 0
        self.mlocked = 0
        self.high_total = 0
        self.high_free = 0
        self.low_total = 0
        self.low_free = 0
        self.swap_total =0
        self.swap_free = 0
        self.dirty = 0
        self.writeback = 0
        self.anon_pages = 0
        self.mapped = 0
        self.slab = 0
        self.slab_reclaimable = 0
        self.slab_unreclaimable = 0
        self.page_tables = 0
        self.nfs_unstable = 0
        self.bounce = 0
        self.writeback_tmp = 0
        self.commit_limit = 0
        self.committed_as = 0
        self.vmalloc_total = 0
        self.vmalloc_used = 0
        self.vmalloc_chunk = 0


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
