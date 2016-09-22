select sum(pss)
from process
where snapshot_id = :snapshot_id and cmd like :name;
