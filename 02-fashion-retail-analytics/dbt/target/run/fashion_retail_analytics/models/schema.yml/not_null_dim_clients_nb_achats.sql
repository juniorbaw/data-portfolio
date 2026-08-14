
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select nb_achats
from "fashion_retail"."main"."dim_clients"
where nb_achats is null



  
  
      
    ) dbt_internal_test