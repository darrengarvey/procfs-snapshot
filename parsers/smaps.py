from model import SmapsPermissions, MemoryRegion


def parse_smaps_header(header):
    info = MemoryRegion()
    # Example line is:
    # 011e6000-01239000 rw-p 00000000 00:00 0    [heap]
    # 8ec00000-8ec01000 rw-s 00000000 00:14 20   /dev/shm/NS2371 (deleted)
    # All numbers are hex except for the inode
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

    info.offset = int(parts[2], 16)

    # eg. 08:06
    info.major_dev, info.minor_dev = [int(x, 16) for x in parts[3].split(':')]

    # The inode isn't a hex number
    info.inode = int(parts[4])

    # eg. [heap]
    # or  /dev/shm/NS2371
    info.name = parts[5]

    info.deleted = header.endswith('(deleted)')

    return info