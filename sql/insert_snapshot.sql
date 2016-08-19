insert into snapshot values (
    null,
    strftime('%Y-%m-%d %H:%M:%f', 'now'),
    :hostname,
    :uptime,
    :uptime_idle,
    :one_minute_load,
    :five_minute_load,
    :fifteen_minute_load,
    :running_threads,
    :total_threads,
    :last_pid
);