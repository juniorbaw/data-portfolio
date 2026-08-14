
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select montant
from "fashion_retail"."main"."stg_transactions"
where montant is null



  
  
      
    ) dbt_internal_test