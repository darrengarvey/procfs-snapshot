insert into process values (
    :snapshot_id,
    :pid,
    :cmd,
    :argv,
    :comm,
    :minor_faults,
    :major_faults,
    :user_time,
    :system_time,
    :start_time
);