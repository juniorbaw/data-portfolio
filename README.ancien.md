# Data Analytics Portfolio — Souleymane N'DIAYE

**Data Analyst — Retail & Luxe** · SQL · Python · BigQuery · Looker Studio · Power BI *(en cours)*

Je travaille sur des données de retail et de luxe. Ce que je cherche à montrer ici n'est pas
seulement un résultat, mais la manière d'y arriver : profilage de la source, règles de gestion
explicitées, tests de cohérence, et limites publiées à côté des chiffres.

[LinkedIn](https://www.linkedin.com/in/souleymane-nd) · soujunior94@gmail.com

---

### 🏷️ [Analyse d'écarts de prix — marché mode & luxe](01-price-positioning-luxury/)

119 produits collectés par API. Le luxe ne se brade pas : la remise pondérée décroît de 42,3 % sur
le segment accessible à 19,9 % sur le luxe (ρ = −0,58 entre prix et taux de remise). Écart de
médiane d'un facteur 13,6 entre segments — 49 entre montres et chaussures.
**Limite publiée :** 55 des 119 produits seulement ont un prix de référence exploitable.

### 🛍️ [Fashion Retail Analytics — segmentation & qualité de données](02-fashion-retail-analytics/)

2 750 transactions, 166 clients, 430 952 USD. Le quartile supérieur pèse 51,4 % du CA — non par
fréquence d'achat, mais par un panier 2,7x supérieur. Le premier contributeur au CA est aussi
l'article le plus mal noté (2,54/5).
**Ce projet documente une erreur de grain trouvée dans ma propre v1** et le test qui l'empêche de
revenir : [rapport de qualité de données](02-fashion-retail-analytics/docs/rapport_qualite_donnees.md).

---

### Stack

| | |
|---|---|
| Langages | SQL (CTE, window functions), Python (pandas) |
| Entrepôt | BigQuery |
| Modélisation | Approche dbt — staging / marts, tests, documentation |
| Restitution | Looker Studio · Power BI *(portage en cours)* |
| Versioning | Git / GitHub |
