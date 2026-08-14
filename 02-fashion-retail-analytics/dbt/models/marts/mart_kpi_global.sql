-- Les 4 indicateurs de la page d'accueil.
-- Contrainte testée : nb_transactions * panier_moyen = ca_total.

select
    count(*)                                as nb_transactions,   -- 2 750
    count(distinct client_id)               as nb_clients,        -- 166
    sum(montant)                            as ca_total_usd,      -- 430 952,00
    avg(montant)                            as panier_moyen_usd,  -- 156,71 — par TRANSACTION
    median(montant)                         as panier_median_usd, -- 110,00
    avg(note)                               as note_moyenne,
    min(date_transaction)                   as debut_periode,
    max(date_transaction)                   as fin_periode
from {{ ref('stg_transactions') }}
