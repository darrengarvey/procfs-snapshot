select pid, cmd, pss, num_fragments,
       heap, stack, ro_shared, ro_private,
       rw_shared, rw_private, rx_shared, rx_private,
       rwx_shared, rwx_private
from process
where snapshot_id = :snapshot_id and cmd like :name;