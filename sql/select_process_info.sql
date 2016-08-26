select pid, cmd, pss, num_fragments,
       heap, stack,
       ro_shared, ro_shared_file,
       ro_private, ro_private_file,
       rw_shared, rw_shared_file,
       rw_private, rw_private_file,
       rx_shared, rx_shared_file,
       rx_private, rx_private_file,
       rwx_shared, rwx_shared_file,
       rwx_private, rwx_private_file
from process
where snapshot_id = :snapshot_id and cmd like :name;