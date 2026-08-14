
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Les trois indicateurs affichés côte à côte doivent vérifier
-- nb_transactions x panier_moyen = ca_total. C'est l'égalité que la v1 violait
-- d'un facteur 17,6.  Doit renvoyer 0 ligne.

select *
from "fashion_retail"."main"."mart_kpi_global"
where abs(nb_transactions * panier_moyen_usd - ca_total_usd) > 1
  
  
      
    ) dbt_internal_test