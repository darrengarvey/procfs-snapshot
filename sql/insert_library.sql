insert or ignore into library values (
    :snapshot_id,
    :inode,
    :name,
    :pss,
    :num_fragments,
    :shared_count
);