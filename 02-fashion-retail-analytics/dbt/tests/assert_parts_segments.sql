-- Les parts de clients et les parts de chiffre d'affaires doivent chacune
-- sommer à 100 %.  Doit renvoyer 0 ligne.

select
    sum(pct_clients) as total_clients,
    sum(pct_ca)      as total_ca
from {{ ref('mart_segments') }}
having abs(sum(pct_clients) - 100) > 0.1
    or abs(sum(pct_ca) - 100) > 0.1
