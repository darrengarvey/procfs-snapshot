import os
import sqlite3


class Database(object):

    def __init__(self, path, overwrite=False):

        self.path = path
        if os.path.exists(path):
            if overwrite:
                os.unlink(path)
                self._create_db(path)
            else:
                self.conn = sqlite3.connect(path)
        else:
            self._create_db(path)
        self.known_libs = {}

    def _get_sql(self, name):
        path = os.path.join(os.path.dirname(__file__), 'sql', name)
        assert(os.path.exists(path))
        with open(path, 'r') as f:
            return f.read()

    def _create_db(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(self._get_sql('schema.sql'))
        self.conn.commit()

    def add(self, name, system_stats, memory_stats, processes):

        snapshot_id = self._add_snapshot(name, system_stats, commit=True)
        self._add_meminfo(snapshot_id, memory_stats)
        self._add_processes(snapshot_id, processes)
        self._add_memory_stats(snapshot_id, memory_stats)
        self.conn.commit()

    def _add_snapshot(self, name, system_stats, commit=False):
        """Add all collected info in one go"""
        sql = self._get_sql('insert_snapshot.sql')
        snapshot_id = self.conn.execute(sql, {
            'hostname': name,
            'uptime': system_stats.uptime,
            'uptime_idle': system_stats.uptime_idle,
            'one_minute_load': system_stats.one_minute_load,
            'five_minute_load': system_stats.five_minute_load,
            'fifteen_minute_load': system_stats.fifteen_minute_load,
            'running_threads': system_stats.running_threads,
            'total_threads': system_stats.total_threads,
            'last_pid': system_stats.last_pid
        }).lastrowid
        if commit:
            self.conn.commit()
        return snapshot_id

    def _add_meminfo(self, snapshot_id, memory_stats, commit=False):
        sql = self._get_sql('insert_meminfo.sql')
        # I'm being intentionally explicit here to avoid any issues
        # if fields are added, removed or reordered.
        self.conn.execute(sql, {
            'snapshot_id': snapshot_id,
            'total': memory_stats.get('MemTotal', 0),
            'free': memory_stats.get('MemFree', 0),
            'mem_available': memory_stats.get('MemAvailable', 0),
            'buffers': memory_stats.get('Buffers', 0),
            'cached': memory_stats.get('Cached', 0),
            'swap_cached': memory_stats.get('SwapCached', 0),
            'active': memory_stats.get('Active', 0),
            'inactive': memory_stats.get('Inactive', 0),
            'active_anon': memory_stats.get('Active(anon, 0)', 0),
            'inactive_anon': memory_stats.get('Inactive(anon, 0)', 0),
            'active_file': memory_stats.get('Active(file, 0)', 0),
            'inactive_file': memory_stats.get('Inactive(file, 0)', 0),
            'unevictable': memory_stats.get('Unevictable', 0),
            'mlocked': memory_stats.get('Mlocked', 0),
            'high_total': memory_stats.get('HighTotal', 0),
            'high_free': memory_stats.get('HighFree', 0),
            'low_total': memory_stats.get('LowTotal', 0),
            'low_free': memory_stats.get('LowFree', 0),
            'swap_total': memory_stats.get('SwapTotal', 0),
            'swap_free': memory_stats.get('SwapFree', 0),
            'dirty': memory_stats.get('Dirty', 0),
            'writeback': memory_stats.get('Writeback', 0),
            'anon_pages': memory_stats.get('AnonPages', 0),
            'mapped': memory_stats.get('Mapped', 0),
            'shmem': memory_stats.get('Shmem', 0),
            'slab': memory_stats.get('Slab', 0),
            'slab_reclaimable': memory_stats.get('SReclaimable', 0),
            'slab_unreclaimable': memory_stats.get('SUnreclaim', 0),
            'kernel_stack': memory_stats.get('KernelStack', 0),
            'page_tables': memory_stats.get('PageTables', 0),
            'nfs_unstable': memory_stats.get('NFS_Unstable', 0),
            'bounce': memory_stats.get('Bounce', 0),
            'writeback_tmp': memory_stats.get('WritebackTmp', 0),
            'commit_limit': memory_stats.get('CommitLimit', 0),
            'committed_as': memory_stats.get('Committed_AS', 0),
            'vmalloc_total': memory_stats.get('VmallocTotal', 0),
            'vmalloc_used': memory_stats.get('VmallocUsed', 0),
            'vmalloc_chunk': memory_stats.get('VmallocChunk', 0),
            'hardware_corrupted': memory_stats.get('HardwareCorrupted', 0),
            'anon_huge_pages': memory_stats.get('AnonHugePages', 0),
            'cma_total': memory_stats.get('CmaTotal', 0),
            'cma_free': memory_stats.get('CmaFree', 0),
            'huge_pages_total': memory_stats.get('HugePages_Total', 0),
            'huge_pages_free': memory_stats.get('HugePages_Free', 0),
            'huge_pages_rsvd': memory_stats.get('HugePages_Rsvd', 0),
            'huge_pages_surp': memory_stats.get('HugePages_Surp', 0),
            'huge_page_size': memory_stats.get('Hugepagesize', 0),
            'direct_map_4k': memory_stats.get('DirectMap4k', 0),
            'direct_map_2m': memory_stats.get('DirectMap2M', 0)
        })
        if commit:
            self.conn.commit()


    def _add_processes(self, snapshot_id, processes, commit=False):
        sql = self._get_sql('insert_process.sql')
        for process in processes:
            cmd = process.argv[0] if len(process.argv) else ''

            if len(process.argv) > 1:
                argv = ' '.join(process.argv[1:])
            else:
                argv = ''
            #print ('%s: argv' % process.argv[0], argv)
            self.conn.execute(sql, {
                'snapshot_id': snapshot_id,
                'pid': process.pid,
                'cmd': cmd,
                'argv': argv,
                'comm': process.comm,
                'minor_faults': process.minor_faults,
                'major_faults': process.major_faults,
                'user_time': process.user_time,
                'system_time': process.system_time,
                'start_time': process.start_time,
                'num_fragments': process.num_fragments,
                'pss': process.pss,
                'heap': process.heap,
                'stack': process.stack,
                'ro_shared': process.ro_shared,
                'ro_private': process.ro_private,
                'rw_shared': process.rw_shared,
                'rw_private': process.rw_private,
                'rx_shared': process.rx_shared,
                'rx_private': process.rx_private,
                'rwx_shared': process.rwx_shared,
                'rwx_private': process.rwx_private,
                'shared_clean': process.shared_clean,
                'shared_dirty': process.shared_dirty,
                'private_clean': process.private_clean,
                'private_dirty': process.private_dirty,
                'referenced': process.referenced,
                'anonymous': process.anonymous
            })
        if commit:
            self.conn.commit()


    def _add_or_get_library(self, name, commit=False):
        """There are likely to be lots of duplicated library names
           across a normal system, so cache libraries to avoid looking
           them up in the db repeatedly."""
        library_id = self.known_libs.get(name, 0)

        if library_id == 0:
            sql = self._get_sql('insert_library.sql')
            self.conn.execute(sql, [name])
            sql = self._get_sql('select_library.sql')
            library_id = self.conn.execute(sql, [name]).fetchone()[0]
            if commit:
                self.conn.commit()
            self.known_libs[name] = library_id
        return library_id


    def _add_memory_stats(self, snapshot_id, memory_stats, commit=False):
        sql = self._get_sql('insert_memory_stats.sql')
        for region in memory_stats.maps:
            #print('region', region.name, region.pid, region.start_addr, region.end_addr)
            library_id = self._add_or_get_library(region.name)
            self.conn.execute(sql, {
                'snapshot_id': snapshot_id,
                'pid': region.pid,
                'library_id': library_id,
                'free': region.free,
                'start_addr': region.start_addr,
                'end_addr': region.end_addr,
                'size': region.size,
                'offset': region.offset,
                'inode': region.inode,
                'readable': region.permissions.readable,
                'writable': region.permissions.writable,
                'executable': region.permissions.executable,
                'shared': region.permissions.shared,
                'private': region.permissions.private,
                'name': region.name,
                'rss': region.rss,
                'pss': region.pss,
                'shared_clean': region.shared_clean,
                'shared_dirty': region.shared_dirty,
                'private_clean': region.private_clean,
                'private_dirty': region.private_dirty,
                'referenced': region.referenced,
                'anonymous': region.anonymous,
                'anonymous_huge': region.anonymous_huge,
                'shared_hugetlb': region.shared_hugetlb,
                'private_hugetlb': region.private_hugetlb,
                'swap': region.swap,
                'swap_pss': region.swap_pss,
                'kernel_page_size': region.kernel_page_size,
                'mmu_page_size': region.mmu_page_size,
                'locked': region.locked,
                'vm_flags': ' '.join(region.vm_flags)
            })
        if commit:
            self.conn.commit()
