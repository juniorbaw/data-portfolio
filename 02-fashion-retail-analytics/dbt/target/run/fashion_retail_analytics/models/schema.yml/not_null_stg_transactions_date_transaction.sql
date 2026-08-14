
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date_transaction
from "fashion_retail"."main"."stg_transactions"
where date_transaction is null



  
  
      
    ) dbt_internal_test