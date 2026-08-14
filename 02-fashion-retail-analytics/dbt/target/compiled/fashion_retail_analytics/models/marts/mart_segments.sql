-- Performance par segment. Construit sur dim_clients : 1 ligne par client.

with s as (

    select
        segment_valeur,
        count(*)            as nb_clients,
        sum(ca_client)      as ca_segment,
        sum(nb_achats)      as nb_achats,
        avg(panier_moyen)   as panier_moyen_client,
        avg(recence_jours)  as recence_moyenne
    from "fashion_retail"."main"."dim_clients"
    group by segment_valeur

)

select
    segment_valeur,
    nb_clients,
    nb_clients * 100.0 / sum(nb_clients) over ()   as pct_clients,
    ca_segment,
    ca_segment * 100.0 / sum(ca_segment) over ()   as pct_ca,
    nb_achats,
    panier_moyen_client,
    recence_moyenne,
    case segment_valeur
        when '4. VIP' then
            'Levier = panier, pas fréquence : 2,7x le panier des autres segments pour un volume d''achats comparable aux Fidèles.'
        when '3. Fidèle' then
            'Volume d''achats le plus élevé du portefeuille mais panier bas : cible prioritaire de montée en gamme.'
        when '2. Régulier' then
            'Panier identique aux Fidèles, moins actif : levier de fréquence.'
        else
            'Faible valeur individuelle. Tester le coût d''activation avant d''investir.'
    end as lecture_business
from s