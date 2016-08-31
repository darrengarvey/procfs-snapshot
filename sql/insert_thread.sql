insert into thread values (
    :snapshot_id,
    :process_id,
    :thread_id,
    :comm,
    :minor_faults,
    :major_faults,
    :user_time,
    :system_time,
    :start_time
);