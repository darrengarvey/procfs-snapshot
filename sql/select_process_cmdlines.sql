select distinct pid, cmd || ' ' || argv
from process
where cmd like :name
order by pss desc;