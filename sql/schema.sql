pragma foreign_keys = on;

create table memory_type
(
    id              integer primary key,
    str             string
);

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

create table library
(
    id              integer primary key,
    base_id         integer default null,
    name            string unique
);

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

    primary key(snapshot_id, pid)
    foreign key(snapshot_id) references snapshot(id) on delete cascade on update cascade
);

create table memory_region
(
    snapshot_id         integer,
    pid                 integer,
    library_id          integer,
    memory_type         integer,
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
    --foreign key(memory_type) references memory_type(id)

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
