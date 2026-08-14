# Fashion Retail Analytics — segmentation client & qualité de données

**En une phrase :** 2 750 transactions transformées en un modèle de données testé, et une erreur de
modélisation trouvée et corrigée dans ma propre v1.

| | |
|---|---|
| **Stack** | SQL (approche dbt) · Python · Looker Studio |
| **Périmètre** | 2 750 transactions · 166 clients · 430 952 USD · oct. 2022 → oct. 2023 |
| **Données** | Synthétiques, à des fins pédagogiques |
| **Dashboard** | *(lien Looker Studio publié à insérer)* |

---

## Ce que le projet montre

**1. La valeur est concentrée, mais pas pour la raison attendue.**
Le quartile supérieur de clients (25,3 %) réalise **51,4 % du chiffre d'affaires**. En revanche, ces
clients font **777 achats, soit moins que les Fidèles (794)**. Leur surperformance ne vient pas de la
fréquence mais du panier : **304 USD contre 111 USD**, soit 2,7 fois plus par transaction. Le levier
sur ce segment est la montée en gamme, pas la relance.

**2. Le premier contributeur au CA est le produit le moins bien noté.**
`Tunic` pèse 17 275 USD (rang 1) pour une note moyenne de **2,54 / 5**. Quatre autres articles passent
sous 2,7. C'est le profil de risque d'un produit qui vend par prix ou par assortiment, pas par
satisfaction : le CA d'aujourd'hui finance l'attrition de demain.

**3. Le mode de paiement discrimine peu.**
Carte 160,4 USD de panier moyen contre 152,7 USD en espèces, soit +5 %. L'écart existe mais ne
justifie aucune action isolée — et surtout, il ne mesure pas un comportement, il mesure une
corrélation sur 2 750 lignes.

---

## Ce que le projet montre aussi : une erreur, et sa correction

La version 1 de ce dashboard affichait **7,6 M€ de chiffre d'affaires pour 2 750 transactions et un
panier moyen de 156,7 €**. Ces trois nombres sont incompatibles : 2 750 × 156,7 = 430 925.

La cause était une **erreur de grain**. Les colonnes `total_depense` et `nb_achats` sont des agrégats
client, et elles avaient été laissées dans la table de transactions, répétées sur chaque ligne du
client. L'outil de restitution les additionnait, comptant chaque client autant de fois qu'il avait
d'achats — 16,6 en moyenne. Le « 2 800 clients » était le même artefact : un décompte de lignes, pas
de clients distincts. Il y a 166 clients.

La correction est structurelle : deux tables, deux grains, et un test (`assert_coherence_ca`) qui
échoue si les deux ne se rejoignent pas.

👉 **[Rapport de qualité de données complet](docs/rapport_qualite_donnees.md)** — c'est la partie du
projet dont je suis le plus satisfait.

---

## Architecture

```
02-fashion-retail-analytics/
├── data/
│   ├── raw/        Fashion_Retail_Sales.csv          source brute, jamais modifiée
│   └── processed/  fct_transactions.csv              grain : 1 transaction
│                   dim_clients.csv                   grain : 1 client
│                   mart_segments.csv, mart_produits.csv
├── models/
│   ├── staging/    stg_transactions.sql, dim_clients.sql
│   ├── marts/      mart_kpi_global.sql, mart_segments.sql, mart_produits.sql
│   └── tests/      tests.sql                         7 assertions
├── docs/           rapport_qualite_donnees.md
│                   data_catalog.md
└── dashboard/      captures + lien Looker Studio
```

## Contrôles automatisés

Unicité du grain transaction · montants strictement positifs · intégrité référentielle client ·
unicité du grain client · **cohérence du CA entre les deux grains** · cohérence arithmétique des KPI
affichés · somme des parts de segments à 100 %.

Le cinquième test est celui qui aurait détecté l'erreur de la v1. Il tourne désormais à chaque build.

## Limites

Données synthétiques · 166 clients seulement, aucune significativité testée · une seule année, donc
aucune saisonnalité établie · 19,1 % des lignes sources sans montant, exclues du CA · 9,5 % de notes
manquantes, sans test de biais de non-réponse · montants en **USD**.

---

## Reproduire ce projet

```bash
# 1. Le pipeline dbt (DuckDB en local, aucun entrepôt cloud requis)
cd dbt
pip install dbt-duckdb
cp profiles.example.yml ~/.dbt/profiles.yml
dbt deps && dbt seed && dbt build      # 5 modèles, 4 tests singuliers, tests génériques

# 2. Les graphiques
python scripts/make_charts.py          # -> assets/*.png

# 3. La page de restitution
python scripts/make_page.py            # -> docs/index.html
```

Aucun chiffre n'est écrit en dur nulle part : graphiques et page sont recalculés depuis les
tables à chaque génération. Si une valeur change dans la source, elle change partout.

## Restitutions

| Surface | Lien |
|---|---|
| Page web | [`docs/index.html`](docs/index.html) — hébergeable sur GitHub Pages |
| Looker Studio | https://datastudio.google.com/s/r_MJe_bQizA |
| Power BI | `dashboard/powerbi/` |
| Graphiques | [`assets/`](assets/) — 5 PNG, régénérables par commande |

## Architecture

```
02-fashion-retail-analytics/
├── data/raw/          Fashion_Retail_Sales.csv        source, jamais modifiée
├── data/processed/    fct_transactions.csv (2 750)    grain : 1 transaction
│                      dim_clients.csv (166)           grain : 1 client
├── dbt/               projet dbt exécutable           5 modèles, schema.yml, 4 tests singuliers
├── scripts/           make_charts.py, make_page.py    tout est régénérable
├── assets/            5 graphiques PNG
├── docs/              index.html, rapport_qualite_donnees.md, data_catalog.md
└── dashboard/         captures et liens des restitutions
```
