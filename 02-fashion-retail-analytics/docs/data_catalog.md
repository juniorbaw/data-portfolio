# Dictionnaire de données

## `fct_transactions` — grain : 1 ligne = 1 transaction (2 750 lignes)

| Colonne | Type | Description | Règle |
|---|---|---|---|
| `transaction_id` | string | Identifiant technique de la transaction | Unique (testé) |
| `client_id` | string | Référence client | Doit exister dans `dim_clients` (testé) |
| `article` | string | Article acheté | 50 valeurs distinctes |
| `montant` | float | Montant de la transaction, **en USD** | > 0 (testé) |
| `date` | date | Date d'achat | Entre 2022-10-02 et 2023-10-01 |
| `note` | float | Note client 1–5 | Nullable — 9,5 % manquantes |
| `paiement` | string | Credit Card / Cash | Aucune autre valeur admise |
| `mois` | string | `YYYY-MM`, dérivé de `date` | — |
| `jour_semaine` | string | Dérivé de `date` | — |

> ⚠️ Cette table ne doit **jamais** contenir de colonne agrégée au niveau client
> (`ca_client`, `nb_achats`). C'est ce qui a produit un CA de 7,6 M au lieu de 431 k en v1.

## `dim_clients` — grain : 1 ligne = 1 client (166 lignes)

| Colonne | Type | Description |
|---|---|---|
| `client_id` | string | Clé primaire, unique (testé) |
| `nb_achats` | int | Nombre de transactions du client (6 à 28, moyenne 16,6) |
| `ca_client` | float | Somme des montants du client, USD |
| `panier_moyen` | float | `ca_client / nb_achats` |
| `premier_achat`, `dernier_achat` | date | Bornes d'activité |
| `recence_jours` | int | Jours entre `dernier_achat` et la date de référence du jeu |
| `note_moyenne` | float | Moyenne des notes renseignées |
| `nb_categories` | int | Articles distincts achetés |
| `r_score`, `f_score`, `m_score` | int 1–4 | Quartiles Récence / Fréquence / Montant |
| `rfm` | string | Concaténation des trois scores |
| `segment_valeur` | string | Quartile de valeur : chaque segment ≈ **25 % des clients** |

> ⚠️ `segment_valeur` est un quartile. Les parts de clients par segment sont ~25 % chacune par
> construction. Ne jamais présenter les parts de CA (51,4 / 20,3 / 16,4 / 12,0) comme des parts
> de clients : c'est l'erreur de la v1.

## Glossaire métier

| Terme | Définition retenue |
|---|---|
| **Chiffre d'affaires** | `SUM(montant)` sur `fct_transactions`, périmètre = lignes avec montant renseigné (2 750 / 3 400) |
| **Panier moyen** | `AVG(montant)` par transaction — pas par client |
| **Panier moyen client** | `ca_client / nb_achats`, calculé dans `dim_clients` |
| **Client actif** | Client avec au moins une transaction sur la période |
| **Segment VIP** | 4ᵉ quartile de `ca_client` — 25 % des clients, pas 8,9 % |
| **Alerte satisfaction** | Note moyenne article < 2,70 (CRITIQUE) ou < 3,00 (VIGILANCE) |
| **Risque prioritaire** | Article simultanément dans le top 10 CA et en alerte CRITIQUE |
