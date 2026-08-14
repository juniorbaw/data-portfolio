



select
    1
from "fashion_retail"."main"."dim_clients"

where not(count(*) = 166)

