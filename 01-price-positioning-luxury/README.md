# Analyse d'écarts de prix — marché mode & luxe

**En une phrase :** 119 produits collectés par API pour mesurer comment le prix et la remise se
comportent selon le segment de marché.

| | |
|---|---|
| **Stack** | Python (collecte API Channel3) · SQL · Looker Studio |
| **Périmètre** | 119 produits · 7 catégories · prix en USD · août 2026 |
| **Dashboard** | *(lien Looker Studio publié à insérer)* |

---

## Ce que disent les données

**1. Le marché n'est pas un continuum, il est segmenté.**

| Segment | n | Prix médian | Prix moyen | Min – Max |
|---|---:|---:|---:|---|
| Accessible | 41 | 123 $ | 233 $ | 14 – 1 300 $ |
| Mid | 37 | 275 $ | 1 251 $ | 90 – 10 500 $ |
| Luxe | 41 | 1 667 $ | 6 546 $ | 259 – 76 000 $ |

Facteur **13,6** entre les médianes Accessible et Luxe. Sur une catégorie comparable, l'écart est
bien plus violent : médiane 4 875 $ sur les montres contre 100 $ sur les chaussures, soit **49x**.

**2. Le luxe ne se brade pas — et le gradient est net.**
La remise pondérée décroît de manière monotone avec le segment de prix :

| Segment | n avec prix de référence | Remise pondérée |
|---|---:|---:|
| Accessible | 25 | **42,3 %** |
| Mid | 16 | 36,5 % |
| Luxe | 14 | **19,9 %** |

Corrélation de rang prix / taux de remise : **ρ = −0,58**. Les marques premium protègent leur prix,
les marques accessibles utilisent la remise comme levier commercial.

**3. La moyenne ment ici plus qu'ailleurs.**
Prix médian **376 $**, prix moyen **2 725 $** — un rapport de 7. La distribution est dominée par
quelques montres à cinq chiffres. Toute lecture de ce marché à la moyenne est fausse.

---

## Méthode et limites

- **Échantillon non représentatif.** Recherche par mots-clés sur l'API Channel3, six requêtes
  catégorielles, ~20 résultats chacune. Ce n'est pas un catalogue exhaustif et la sélection est
  soumise au classement du moteur.
- **Seuls 55 des 119 produits (46 %) affichent un prix de référence.** Tous les indicateurs de
  remise ne portent que sur ce sous-ensemble, jamais sur les 119.
- **Deux mesures de remise sont publiées et ne doivent pas être confondues.**
  Remise moyenne simple = moyenne des taux produit par produit → **39,4 %**.
  Remise pondérée = `SUM(prix_barré − prix) / SUM(prix_barré)` → **23,3 %**.
  La seconde est la bonne mesure au niveau marché ; la première surpondère les petits articles très
  démarqués.
- Prix en **USD** uniquement, après nettoyage. Aucune conversion de devise.
- Les KPI vérifiés sont figés dans [`data/kpi_verifies.csv`](data/kpi_verifies.csv) : tout chiffre
  publié doit s'y retrouver.
