import os
import sqlite3
from model import Library


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

    def get_process_cmdlines(self, name='%'):
        sql = self._get_sql('select_process_cmdlines.sql')
        for process in self.conn.execute(sql, { 'name': name }):
            yield process

    def get_process_stats(self, name='%'):
        sql = self._get_sql('select_process_stats.sql')
        for process in self.conn.execute(sql, { 'name': name }):
            yield process

    def get_process_info(self, snapshot_id, name='%'):
        sql = self._get_sql('select_process_info.sql')
        for process in self.conn.execute(sql, {
                'snapshot_id': snapshot_id,
                'name': name }):
            yield process

    def get_snapshot_id(self, timestamp):
        sql = self._get_sql('select_snapshot_id.sql')
        return self.conn.execute(sql, { 'ts': timestamp }).fetchone()[0]

    def add(self, name, system_stats, memory_stats, processes):

        snapshot_id = self._add_snapshot(name, system_stats, commit=True)
        self._add_meminfo(snapshot_id, memory_stats)
        self._add_processes(snapshot_id, processes)
        self._add_memory_stats(snapshot_id, memory_stats)
        self._add_libraries()
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
            'minor_page_faults': system_stats.vmstats.get('pgfault'),
            'major_page_faults': system_stats.vmstats.get('pgmajfault'),
            'total_threads': system_stats.total_threads,
            'last_pid': system_stats.last_pid,
            'free_pages': system_stats.vmstats.get('nr_free_pages'),
            'pages_paged_in': system_stats.vmstats.get('pgpgin'),
            'pages_paged_out': system_stats.vmstats.get('pgpgout'),
            'pages_swapped_in': system_stats.vmstats.get('pswpin'),
            'pages_swapped_out': system_stats.vmstats.get('pswpout'),
            'pages_allocated_normal': system_stats.vmstats.get('pgalloc_normal'),
            'pages_freed': system_stats.vmstats.get('pgfree'),
            'pages_activated': system_stats.vmstats.get('pgactivate'),
            'pages_deactivated': system_stats.vmstats.get('pgdeactivate'),
            'pages_outrun': system_stats.vmstats.get('pageoutrun'),
            'alloc_stalled': system_stats.vmstats.get('allocstall'),
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
                'ro_shared_file': process.ro_shared_file,
                'ro_private': process.ro_private,
                'ro_private_file': process.ro_private_file,
                'rw_shared': process.rw_shared,
                'rw_shared_file': process.rw_shared_file,
                'rw_private': process.rw_private,
                'rw_private_file': process.rw_private_file,
                'rx_shared': process.rx_shared,
                'rx_shared_file': process.rx_shared_file,
                'rx_private': process.rx_private,
                'rx_private_file': process.rx_private_file,
                'rwx_shared': process.rwx_shared,
                'rwx_shared_file': process.rwx_shared_file,
                'rwx_private': process.rwx_private,
                'rwx_private_file': process.rwx_private_file,
                'shared_clean': process.shared_clean,
                'shared_dirty': process.shared_dirty,
                'private_clean': process.private_clean,
                'private_dirty': process.private_dirty,
                'referenced': process.referenced,
                'anonymous': process.anonymous
            })

            self._add_threads(snapshot_id, process.pid,
                              process.threads.values(),
                              commit=commit)

        if commit:
            self.conn.commit()

    def _add_threads(self, snapshot_id, pid, threads, commit=False):
        sql = self._get_sql('insert_thread.sql')
        for thread in threads:
            self.conn.execute(sql, {
                'snapshot_id': snapshot_id,
                'process_id': pid,
                'thread_id': thread.thread_id,
                'comm': thread.comm,
                'minor_faults': thread.minor_faults,
                'major_faults': thread.major_faults,
                'user_time': thread.user_time,
                'system_time': thread.system_time,
                'start_time': thread.start_time,
            })

        if commit:
            self.conn.commit()

    def _account_library(self, snapshot_id, inode, name, pss):
        """There are likely to be lots of duplicated library names
           across a normal system, so cache libraries to avoid looking
           them up in the db repeatedly."""

        # inode 0 is for memory fragments that aren't real files,
        # eg. [heap], [vdso], etc.
        if inode == 0:
            return

        # When using sandboxing, bind-mounting or symlinks, libraries may
        # show up in smaps with different paths. If the inode is the same
        # - on the same snapshot - then we can be sure the library is
        # actually the same one. The libraries are added to their own table
        # so statistics can be aggregated for them.
        basename = os.path.basename(name)
        if inode in self.known_libs:
            library = self.known_libs[inode]
        else:
            library = Library(basename, inode, snapshot_id)
            self.known_libs[inode] = library

        library.pss += pss
        library.shared_count += 1
        library.num_fragments += 1

    def _add_libraries(self, commit=False):
        for lib in self.known_libs.values():
            sql = self._get_sql('insert_library.sql')
            self.conn.execute(sql, {
                'snapshot_id': lib.snapshot_id,
                'inode': lib.inode,
                'name': lib.name,
                'pss': lib.pss,
                'num_fragments': lib.num_fragments,
                'shared_count': lib.shared_count
            })

        if commit:
            self.conn.commit()

    def _add_memory_stats(self, snapshot_id, memory_stats, commit=False):
        sql = self._get_sql('insert_memory_stats.sql')
        for region in memory_stats.maps:
            #print('region', region.name, region.pid, region.start_addr, region.end_addr)
            self._account_library(snapshot_id,
                                  region.inode,
                                  region.name,
                                  region.pss)
            self.conn.execute(sql, {
                'snapshot_id': snapshot_id,
                'pid': region.pid,
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
                'anon_huge_pages': region.anon_huge_pages,
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
