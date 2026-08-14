-- GRAIN : 1 ligne = 1 transaction.  2 750 lignes attendues.
-- Aucune colonne agrégée au niveau client ne doit exister dans ce modèle.
-- Périmètre : les 650 lignes sans montant (19,1 % de la source) sont exclues du
-- chiffre d'affaires. Voir docs/rapport_qualite_donnees.md, section 1.

with source as (

    select * from {{ ref('fashion_retail_sales') }}

),

cleaned as (

    select
        cast("Customer Reference ID" as varchar)              as client_id,
        trim("Item Purchased")                                as article,
        cast("Purchase Amount (USD)" as double)               as montant,
        strptime("Date Purchase", '%d-%m-%Y')::date           as date_transaction,
        cast("Review Rating" as double)                       as note,
        case trim("Payment Method")
            when 'Credit Card' then 'Credit Card'
            when 'Cash'        then 'Cash'
            else 'Unknown'
        end                                                   as paiement,
        "Purchase Amount (USD)" is null                       as is_montant_manquant,
        "Review Rating" is null                               as is_note_manquante
    from source

),

final as (

    select
        'TX' || lpad(cast(row_number() over (
            order by date_transaction, client_id, article, montant
        ) as varchar), 5, '0')                                as transaction_id,
        client_id,
        article,
        montant,
        date_transaction,
        strftime(date_transaction, '%Y-%m')                    as mois,
        year(date_transaction)                                 as annee,
        strftime(date_transaction, '%A')                       as jour_semaine,
        note,
        is_note_manquante,
        paiement
    from cleaned
    where not is_montant_manquant
      and montant > 0
      and client_id is not null

)

select * from final
