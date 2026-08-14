# Rapport de qualité de données — Fashion Retail Analytics

**Auteur :** Souleymane N'DIAYE · **Version :** 2.0 · **Date :** 12 août 2026
**Source :** `data/raw/Fashion_Retail_Sales.csv` (3 400 lignes, données synthétiques)

> Ce rapport documente le profilage de la source, les anomalies détectées, **et une erreur de
> modélisation présente dans la version 1 du projet**, corrigée ici. Il est publié tel quel :
> une analyse dont on ne peut pas auditer les limites n'a pas de valeur.

---

## 1. Profilage de la source

| Contrôle | Résultat |
|---|---|
| Lignes brutes | 3 400 |
| Clients distincts | **166** |
| Articles distincts | 50 |
| Période couverte | 2 octobre 2022 → 1er octobre 2023 |
| `Purchase Amount (USD)` manquant | **650 lignes — 19,1 %** |
| `Review Rating` manquant | 324 lignes — 9,5 % |
| Devise | **USD** (aucune donnée en euros dans la source) |
| Modes de paiement | Credit Card 1 770 · Cash 1 630 |

**Décision de périmètre.** Les 650 lignes sans montant sont exclues du calcul de chiffre
d'affaires : le périmètre analysé est de **2 750 transactions**. C'est une perte de 19,1 % du
volume, à mentionner systématiquement à côté de tout agrégat. Ces lignes sont conservées pour
l'analyse de satisfaction, où la note est renseignée.

---

## 2. Anomalie majeure corrigée — erreur de grain (fan-out)

**Symptôme.** La version 1 du dashboard affichait trois indicateurs mutuellement incompatibles :

| KPI affiché (v1) | Test | Verdict |
|---|---|---|
| 2 750 transactions | — | ✅ exact |
| Panier moyen 156,7 € | — | ✅ exact (mais en USD, pas en €) |
| CA 7,6 M€ | 2 750 × 156,7 = **430 925** | ❌ facteur 17,6 |
| 2 800 clients | 2 800 clients > 2 750 transactions | ❌ impossible |

**Cause racine.** Le fichier alimentant le dashboard mélangeait deux grains dans une seule table.
Les colonnes `total_depense` et `nb_achats` sont des **agrégats client**, répétés à l'identique sur
chacune des lignes de transaction de ce client. Un client ayant 17 achats voyait son chiffre
d'affaires total compté 17 fois par la somme de l'outil de restitution.

```
SUM(montant)        =   430 952 USD   ← grain transaction, correct
SUM(total_depense)  = 7 585 581 USD   ← agrégat client × nombre de lignes, faux
                                         166 clients × 16,6 achats en moyenne
```

Le « 2 800 clients » avait la même origine : il s'agissait du décompte des lignes `client_id`
(2 750, arrondi à 2,8 k par l'affichage), et non du nombre de clients distincts. **Il y a 166 clients.**

**Correction.** Séparation stricte en deux tables :

- `fct_transactions` — grain : une ligne = une transaction. Aucune colonne agrégée.
- `dim_clients` — grain : une ligne = un client. Les agrégats vivent ici et nulle part ailleurs.

Toute mesure client-level du dashboard doit désormais pointer vers `dim_clients`.

---

## 3. Anomalie corrigée — segmentation mal interprétée

**Symptôme.** La v1 annonçait « 8,9 % des clients (VIP) génèrent 54,1 % du CA », et intitulait le
camembert « Répartition des clients par statut » alors qu'il affichait 54,1 / 22,4 / 14,7 / 8,9.

**Cause racine.** Deux erreurs superposées.

1. Ces quatre valeurs sont la répartition du **chiffre d'affaires** dans la version fan-out, pas
   celle des clients. Le titre du graphique était faux.
2. La série 8,9 / 14,7 / 22,4 / 54,1 a ensuite été relue à l'envers, la part de CA des Occasionnels
   (8,9 %) devenant par erreur la « part de clients VIP ».

**Réalité mesurée.** La segmentation est construite sur des **quartiles**, donc les quatre segments
comptent mécaniquement environ 25 % des clients chacun.

| Segment | Clients | % clients | CA (USD) | % CA | Panier moyen | Nb achats |
|---|---:|---:|---:|---:|---:|---:|
| 4. VIP | 42 | 25,3 % | 221 653 | **51,4 %** | **304,02** | 777 |
| 3. Fidèle | 41 | 24,7 % | 87 279 | 20,3 % | 110,68 | 794 |
| 2. Régulier | 41 | 24,7 % | 70 477 | 16,4 % | 110,72 | 644 |
| 1. Occasionnel | 42 | 25,3 % | 51 543 | 12,0 % | 98,57 | 535 |

**Ce que l'erreur masquait — et qui est plus intéressant.** Les VIP réalisent **777 achats, soit
moins que les Fidèles (794)**. Leur surperformance ne vient donc pas de la fréquence mais du
panier : 304 USD contre 111 USD, soit **2,7 fois plus par transaction**. La v1 concluait que les
VIP « combinent nombre d'achats élevé et dépense totale importante » ; c'est faux. Le levier n'est
pas la fréquence, c'est la montée en gamme.

---

## 4. Alerte satisfaction — le point d'attention business

Cinq articles passent sous 2,7/5 de note moyenne. Le premier d'entre eux est aussi **le premier
contributeur au chiffre d'affaires**.

| Article | CA (USD) | Rang CA | Note moyenne | Statut |
|---|---:|---:|---:|---|
| Tunic | 17 275 | **1er** | **2,54** | CRITIQUE |
| Flannel Shirt | — | — | 2,59 | CRITIQUE |
| Jacket | — | — | 2,64 | CRITIQUE |
| Leggings | — | — | 2,66 | CRITIQUE |
| Sunglasses | — | — | 2,67 | CRITIQUE |

**Lecture.** L'article qui pèse le plus lourd dans le revenu est celui que les clients notent le plus
mal. C'est le profil de risque classique d'un produit qui vend par assortiment ou par prix, pas par
satisfaction : le CA d'aujourd'hui finance l'attrition de demain. Action recommandée : audit qualité
et analyse des retours sur Tunic **avant** toute action d'acquisition.

*Réserve méthodologique :* 9,5 % des notes sont manquantes et la distribution n'a pas été testée
pour un biais de non-réponse. La hiérarchie des notes est indicative, pas conclusive.

---

## 5. Contrôles automatisés en place

| Test | Règle | Statut |
|---|---|---|
| `assert_transaction_unique` | `transaction_id` unique dans `fct_transactions` | ✅ |
| `assert_montant_positif` | `montant > 0` | ✅ |
| `assert_integrite_client` | tout `client_id` de la table de faits existe dans `dim_clients` | ✅ |
| `assert_coherence_ca` | `SUM(fct.montant)` = `SUM(dim.ca_client)` à 0,01 près | ✅ |
| `assert_grain_dim_clients` | `COUNT(*)` = `COUNT(DISTINCT client_id)` | ✅ |

Le test `assert_coherence_ca` est celui qui aurait détecté l'erreur de la v1. Il est désormais
exécuté à chaque build.

---

## 6. Limites assumées

- Données **synthétiques**, générées à des fins pédagogiques. Les montants n'ont pas de réalité
  commerciale et les conclusions ne sont pas transposables à un retailer réel.
- 166 clients seulement : les moyennes par segment reposent sur ~41 individus chacune. Aucun test
  de significativité n'a été mené.
- Une seule année de données : aucune saisonnalité ni tendance ne peut être établie.
- Les montants sont en **USD**. La v1 les libellait en euros : erreur d'unité, corrigée.
