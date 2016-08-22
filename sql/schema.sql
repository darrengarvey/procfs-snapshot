pragma foreign_keys = on;

create table snapshot
(
    id              integer primary key,
    ts              string,
    hostname        string,
    -- system uptime (seconds)
    uptime          real,
    -- seconds any CPU has spent idling, summed across all CPUs
    uptime_idle     real,
    one_minute      real,
    five_minute     real,
    fifteen_minute  real,
    running_threads integer,
    total_threads   integer,
    -- the pid of the last spwaned process
    last_pid        integer
);

create index snapshot_ts_idx on snapshot(ts);

create table library
(
    id              integer primary key,
    base_id         integer default null,
    name            string unique
);

-- libraries are queried by name during an update.
create index library_name_idx on library(name);

create table process
(
    snapshot_id     integer,
    pid             integer,
    cmd             string,
    argv            string,
    -- the name of the executable
    comm            string,
    minor_faults    integer,
    major_faults    integer,
    user_time       integer,
    system_time     integer,
    start_time      integer,

    num_fragments   integer,
    pss             integer,
    heap            integer,
    stack           integer,

    -- summed pss of read-only shared pages
    ro_shared       integer,
    -- summed pss of read-only private pages
    ro_private      integer,
    -- summed pss of read-write shared pages
    rw_shared       integer,
    -- summed pss of read-write private pages
    rw_private      integer,
    -- summed pss of readable and executable shared pages
    rx_shared       integer,
    -- summed pss of readable and executable private pages
    rx_private      integer,
    -- you'd really not expect shared rwx pages. sounds dangerous!
    rwx_shared      integer,
    -- potentially dangerous, but on some architectures (eg. MIPS),
    -- the heap and stack fit into this category.
    rwx_private     integer,

    -- summed shared_clean values from memory regions. These
    -- values are RSS though, so a bit misleading.
    shared_clean    integer,
    -- summed shared_dirty values from memory regions. These
    -- values are RSS though, so a bit misleading.
    shared_dirty    integer,
    -- summed private_clean values from memory regions. These
    -- values are RSS but as they are private the numbers are
    -- useful.
    private_clean   integer,
    -- summed private_dirty values from memory regions. These
    -- values are RSS but as they are private the numbers are
    -- useful.
    private_dirty   integer,
    -- summed referenced values from memory regions. This is useful
    -- to see how much memory the process is actually using. See
    -- /proc/sys/vm/clear_refs for how to make best use of this.
    referenced      integer,
    anonymous       integer,

    primary key(snapshot_id, pid)
    foreign key(snapshot_id) references snapshot(id) on delete cascade on update cascade
);

create index process_snap_id_idx on process(snapshot_id);
create index process_cmd_idx on process(cmd);

create table memory_region
(
    snapshot_id         integer,
    pid                 integer,
    library_id          integer,
    free                boolean,
    start_addr          unsigned big int,
    end_addr            unsigned big int,
    size                unsigned big int,
    offset              unsigned big int,
    inode               integer,
    readable            boolean,
    writable            boolean,
    executable          boolean,
    shared              boolean,
    private             boolean,
    name                string,
    rss                 integer,
    pss                 integer,
    shared_clean        integer,
    shared_dirty        integer,
    private_clean       integer,
    private_dirty       integer,
    referenced          integer,
    anonymous           integer,
    anonymous_huge      integer,
    shared_hugetlb      integer,
    private_hugetlb     integer,
    swap                integer,
    swap_pss            integer,
    kernel_page_size    integer,
    mmu_page_size       integer,
    locked              integer,
    vm_flags            string,

    primary key(snapshot_id, pid, library_id, start_addr)
    foreign key(snapshot_id, pid) references process(snapshot_id, pid) on delete cascade on update cascade
    foreign key(library_id) references library(id) on delete cascade
);

create table memory_stats
(
    id                  integer primary key,
    snapshot_id         integer not null,
    total               integer,
    free                integer,
    mem_available       integer,
    buffers             integer,
    cached              integer,
    swap_cached         integer,
    active              integer,
    inactive            integer,
    active_anon         integer,
    inactive_anon       integer,
    active_file         integer,
    inactive_file       integer,
    unevictable         integer,
    mlocked             integer,
    high_total          integer,
    high_free           integer,
    low_total           integer,
    low_free            integer,
    swap_total          integer,
    swap_free           integer,
    dirty               integer,
    writeback           integer,
    anon_pages          integer,
    mapped              integer,
    shmem               integer,
    slab                integer,
    slab_reclaimable    integer,
    slab_unreclaimable  integer,
    kernel_stack        integer,
    page_tables         integer,
    nfs_unstable        integer,
    bounce              integer,
    writeback_tmp       integer,
    commit_limit        integer,
    committed_as        integer,
    vmalloc_total       integer,
    vmalloc_used        integer,
    vmalloc_chunk       integer,
    hardware_corrupted  integer,
    anon_huge_pages     integer,
    cma_total           integer,
    cma_free            integer,
    huge_pages_total    integer,
    huge_pages_free     integer,
    huge_pages_rsvd     integer,
    huge_pages_surp     integer,
    huge_page_size      integer,
    direct_map_4k       integer,
    direct_map_2m       integer,

    foreign key(snapshot_id) references snapshot(id) on delete cascade on update cascade
);
