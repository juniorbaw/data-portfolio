-- GRAIN : 1 ligne = 1 client.  166 lignes attendues.
-- Seul endroit du projet où vivent les agrégats client.
-- Recopier ca_client ou nb_achats dans la table de faits produit un fan-out :
-- c'est ce qui affichait 7 585 581 au lieu de 430 952 en v1.

with base as (

    select
        client_id,
        count(*)                        as nb_achats,
        sum(montant)                    as ca_client,
        avg(montant)                    as panier_moyen,
        min(date_transaction)           as premier_achat,
        max(date_transaction)           as dernier_achat,
        avg(note)                       as note_moyenne,
        count(distinct article)         as nb_articles_distincts
    from "fashion_retail"."main"."stg_transactions"
    group by client_id

),

borne as (select max(date_transaction) as date_ref from "fashion_retail"."main"."stg_transactions"),

scored as (

    select
        b.*,
        date_diff('day', b.dernier_achat, r.date_ref)                       as recence_jours,
        ntile(4) over (order by date_diff('day', b.dernier_achat, r.date_ref) desc) as r_score,
        ntile(4) over (order by b.nb_achats)                                as f_score,
        ntile(4) over (order by b.ca_client)                                as m_score
    from base b cross join borne r

)

select
    *,
    cast(r_score as varchar) || cast(f_score as varchar) || cast(m_score as varchar) as rfm,
    -- Quartile de valeur : chaque segment pèse ~25 % des CLIENTS par construction.
    -- Ne jamais présenter ces parts comme des parts de chiffre d'affaires.
    case m_score
        when 4 then '4. VIP'
        when 3 then '3. Fidèle'
        when 2 then '2. Régulier'
        else        '1. Occasionnel'
    end as segment_valeur
from scored