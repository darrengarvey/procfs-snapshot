pragma foreign_keys = on;

create table MemoryType
(
    id              integer primary key,
    str             string
);

create table Snapshot
(
    id              integer primary key,
    ts              string,
    hostname        string
);

create table Library
(
    id              integer primary key,
    base_id         integer default null,
    name            string unique
);

create table Process
(
    snapshot_id     integer,
    pid             integer,
    cmd             string,
    argv            string,

    primary key(snapshot_id, pid),
    foreign key(snapshot_id) references Snapshot(id) on delete cascade on update cascade
);

create table MemoryRegion
(
    snapshot_id         integer,
    pid                 integer,
    library_id          integer,
    memory_type         integer,
    free                boolean,
    start_addr          unsigned big int,
    end_addr            unsigned big int,
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
    foreign key(snapshot_id, pid) references Process(snapshot_id, pid) on delete cascade on update cascade,
    foreign key(library_id) references Library(id) on delete cascade,
    foreign key(memory_type) references MemoryType(id)

);