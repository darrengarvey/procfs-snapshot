from model import SmapsPermissions, MemoryRegion


def parse_smaps_header(header):
    info = MemoryRegion()
    # Example line is:
    # 011e6000-01239000 rw-p 00000000 00:00 0  [heap]
    parts = header.split()
    print (parts)

    # Parse the address range
    info.start_addr, info.end_addr = [int(x, 16) for x in parts[0].split('-')]

    # Parse the permissions
    permissions = parts[1]
    info.permissions.readable = "r" in permissions
    info.permissions.writable = "w" in permissions
    info.permissions.executable = "x" in permissions
    info.permissions.private = "p" in permissions
    info.permissions.shared = "s" in permissions

    info.name = parts[-1]

    return info