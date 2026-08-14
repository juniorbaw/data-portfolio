-- Le périmètre doit rester à 2 750 transactions. Si ce nombre change,
-- c'est que la règle d'exclusion des montants nuls a bougé : il faut alors
-- mettre à jour tous les documents qui publient ce chiffre.
-- Doit renvoyer 0 ligne.

select count(*) as n
from {{ ref('stg_transactions') }}
having count(*) <> 2750
