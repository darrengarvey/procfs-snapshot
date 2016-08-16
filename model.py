
class SmapsPermissions(object):
    def __init__(self):
        self.readable = False
        self.writable = False
        self.executable = False
        self.shared = False
        self.private = False

class MemoryRegion(object):
    def __init__(self):
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