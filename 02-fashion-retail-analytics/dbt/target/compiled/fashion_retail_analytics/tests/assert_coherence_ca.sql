-- LE test du projet.
-- Il compare le chiffre d'affaires calculé au grain transaction et au grain client.
-- C'est ce test qui aurait détecté l'erreur de la v1 : SUM(total_depense) = 7 585 581
-- contre SUM(montant) = 430 952, soit chaque client compté 16,6 fois.
-- Doit renvoyer 0 ligne.

select
    f.ca_faits,
    d.ca_dim,
    abs(f.ca_faits - d.ca_dim) as ecart
from (select sum(montant)    as ca_faits from "fashion_retail"."main"."stg_transactions") f
cross join
     (select sum(ca_client)  as ca_dim   from "fashion_retail"."main"."dim_clients") d
where abs(f.ca_faits - d.ca_dim) > 0.01