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

    def _get_sql(self, name):
        path = os.path.join(os.path.dirname(__file__), 'sql', name)
        assert(os.path.exists(path))
        with open(path, 'r') as f:
            return f.read()

    def _create_db(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(self._get_sql('schema.sql'))
        self.conn.commit()

    def add(self, name, memory_stats, processes):
        """Add all collected info in one go"""
        sql = self._get_sql('insert_snapshot.sql')
        snapshot_id = self.conn.execute(sql, [name]).lastrowid

        sql = self._get_sql('insert_meminfo.sql')
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
        self.conn.commit()

