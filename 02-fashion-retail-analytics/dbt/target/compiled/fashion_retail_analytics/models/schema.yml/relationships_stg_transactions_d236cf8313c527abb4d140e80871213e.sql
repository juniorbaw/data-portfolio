
    
    

with child as (
    select client_id as from_field
    from "fashion_retail"."main"."stg_transactions"
    where client_id is not null
),

parent as (
    select client_id as to_field
    from "fashion_retail"."main"."dim_clients"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


