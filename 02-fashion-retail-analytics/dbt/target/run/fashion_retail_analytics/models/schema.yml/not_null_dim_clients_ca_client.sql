
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ca_client
from "fashion_retail"."main"."dim_clients"
where ca_client is null



  
  
      
    ) dbt_internal_test