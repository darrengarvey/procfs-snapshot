
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

    @property
    def size(self):
        return self.end_addr - self.start_addr