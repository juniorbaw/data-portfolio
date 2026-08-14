
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  



select
    1
from "fashion_retail"."main"."dim_clients"

where not(count(*) = 166)


  
  
      
    ) dbt_internal_test