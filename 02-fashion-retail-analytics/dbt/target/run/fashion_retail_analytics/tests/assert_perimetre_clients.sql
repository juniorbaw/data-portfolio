-- Le périmètre doit rester à 166 clients distincts. Si ce nombre change, tous les
-- documents qui publient « 166 » deviennent faux. Doit renvoyer 0 ligne.

select count(*) as n
from {{ ref('dim_clients') }}
having count(*) <> 166
