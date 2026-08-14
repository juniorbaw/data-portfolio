
    
    

with all_values as (

    select
        paiement as value_field,
        count(*) as n_records

    from "fashion_retail"."main"."stg_transactions"
    group by paiement

)

select *
from all_values
where value_field not in (
    'Credit Card','Cash','Unknown'
)


