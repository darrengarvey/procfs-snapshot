select snapshot.ts, process.snapshot_id, process.pid, process.cmd, process.pss, sum(memory_region.rss) as rss, sum(memory_region.private_clean) + sum(memory_region.private_dirty) as uss
from process
join snapshot
on snapshot.id = process.snapshot_id
join memory_region
on snapshot.id = memory_region.snapshot_id and process.pid = memory_region.pid
where process.cmd like :name
group by process.snapshot_id, process.pid;
