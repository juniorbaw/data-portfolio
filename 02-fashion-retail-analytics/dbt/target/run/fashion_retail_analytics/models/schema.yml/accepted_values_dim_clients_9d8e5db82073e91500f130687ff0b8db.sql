
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        segment_valeur as value_field,
        count(*) as n_records

    from "fashion_retail"."main"."dim_clients"
    group by segment_valeur

)

select *
from all_values
where value_field not in (
    '1. Occasionnel','2. Régulier','3. Fidèle','4. VIP'
)



  
  
      
    ) dbt_internal_test