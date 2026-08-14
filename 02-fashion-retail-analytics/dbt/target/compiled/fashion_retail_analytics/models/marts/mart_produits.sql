-- Performance et satisfaction par article.
-- C'est le croisement des deux qui porte le risque commercial, pas chacun isolément.

with p as (

    select
        article,
        count(*)                                as nb_ventes,
        sum(montant)                            as ca_usd,
        avg(montant)                            as panier_moyen,
        avg(note)                               as note_moyenne,
        count(*) filter (where note is null)    as notes_manquantes,
        count(distinct client_id)               as nb_clients
    from "fashion_retail"."main"."stg_transactions"
    group by article

)

select
    *,
    ca_usd * 100.0 / sum(ca_usd) over ()        as pct_ca,
    rank() over (order by ca_usd desc)          as rang_ca,
    case
        when note_moyenne < 2.70 then 'CRITIQUE'
        when note_moyenne < 3.00 then 'VIGILANCE'
        else 'OK'
    end                                          as alerte_satisfaction,
    case
        when note_moyenne < 2.70 and rank() over (order by ca_usd desc) <= 10
            then 'RISQUE PRIORITAIRE : fort contributeur au CA et mal noté. Auditer la qualité avant toute action d''acquisition.'
        when note_moyenne < 2.70
            then 'Surveiller : satisfaction basse, enjeu de chiffre d''affaires limité.'
        else 'Aucune action spécifique.'
    end                                          as recommandation
from p
order by ca_usd desc