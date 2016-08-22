select snapshot.ts, process.snapshot_id, process.pid, process.cmd, process.pss
from process
join snapshot
on snapshot.id = process.snapshot_id
where cmd like :name;