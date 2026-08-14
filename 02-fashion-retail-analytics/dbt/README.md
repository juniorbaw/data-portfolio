# Projet dbt — Fashion Retail Analytics

Projet dbt réel, exécutable en local avec **DuckDB**. Aucun entrepôt cloud requis :
n'importe qui peut cloner et rejouer l'ensemble en trois commandes.

## Lancer

```bash
pip install dbt-duckdb
cp profiles.example.yml ~/.dbt/profiles.yml
dbt deps && dbt seed && dbt build
```

`dbt build` charge la source, construit les cinq modèles et exécute l'ensemble des tests.

## Modèles

| Modèle | Grain | Matérialisation | Lignes attendues |
|---|---|---|---|
| `stg_transactions` | 1 transaction | view | **2 750** |
| `dim_clients` | 1 client | view | **166** |
| `mart_kpi_global` | 1 ligne | table | 1 |
| `mart_segments` | 1 segment | table | 4 |
| `mart_produits` | 1 article | table | 50 |

Staging en `view` — léger et toujours frais. Marts en `table` — interrogés souvent par la
restitution. Se tromper de matérialisation est ce qui fait exploser la facture d'un entrepôt
facturé à la seconde de calcul.

## Tests

Tests génériques déclarés dans `models/schema.yml` : unicité et non-nullité des clés,
intégrité référentielle entre les deux grains, bornes de valeurs, valeurs autorisées.

Quatre tests singuliers dans `tests/` :

| Test | Ce qu'il vérifie |
|---|---|
| **`assert_coherence_ca`** | `SUM(stg_transactions.montant)` = `SUM(dim_clients.ca_client)`. **C'est le test qui aurait détecté l'erreur de grain de la v1.** |
| `assert_kpi_arithmetique` | `nb_transactions × panier_moyen = ca_total` |
| `assert_parts_segments` | Les parts de clients et de CA somment chacune à 100 % |
| `assert_perimetre_transactions` | Le périmètre reste à 2 750 transactions |

Le dernier test est une sentinelle : si le périmètre change, tous les documents qui publient
« 2 750 » deviennent faux. Le test le signale avant qu'un lecteur ne le découvre.

## Documentation et lignage

```bash
dbt docs generate && dbt docs serve
```

Chaque colonne est décrite dans `schema.yml`, y compris les pièges de définition —
notamment le fait que `panier_moyen_usd` est une moyenne **par transaction** (156,71) et non
la moyenne des paniers moyens par client (156,54).
