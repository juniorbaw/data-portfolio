# Reprise du dashboard Looker Studio

## 1. Remplacer la source

Aujourd'hui la source est `fashion_looker.csv`, qui mélange deux grains. La remplacer par **deux**
sources distinctes :

| Source | Fichier | Sert à |
|---|---|---|
| Transactions | `data/processed/fct_transactions.csv` | KPI globaux, CA, panier moyen, top articles, paiement, séries temporelles |
| Clients | `data/processed/dim_clients.csv` | Tout ce qui est « par client » : segments, RFM, nombre de clients |

Ne jamais mélanger les deux dans un même graphique sans blend explicite sur `client_id`.

## 2. Corriger les KPI de la page 2

| Ancien | Nouveau |
|---|---|
| CA `7,6 M €` | **`430 952 $`** — source : transactions, `SUM(montant)` |
| `panier_moyen 156,7` | **`156,71 $`** — source : transactions, `AVG(montant)` — ajouter le symbole $ |
| Nombre de clients `2,8 k` | **`166`** — source : clients, `COUNT(client_id)` |
| Nombre de transactions `2 750` | inchangé ✅ |

Ajouter une ligne de contexte sous les KPI :
> *2 750 transactions retenues sur 3 400 — 19,1 % des lignes sources n'ont pas de montant. Données synthétiques, montants en USD.*

## 3. Corriger le TOP Catégorie

Les valeurs affichées (Shorts 218,1 k, Tank Top 217,3 k…) venaient de `SUM(total_depense)`, l'agrégat
client répété. Les vraies valeurs, sur `SUM(montant)` :

| Article | CA (USD) |
|---|---|
| Tunic | 17 275 |
| Jeans | 13 068 |
| Pajamas | 12 798 |
| Shorts | 12 702 |
| Handbag | 12 668 |

## 4. Corriger la page RFM

- Le camembert intitulé « Répartition des clients par statut » affiche en réalité la répartition du
  **CA**. Deux options : renommer en « Répartition du chiffre d'affaires par segment » avec les vraies
  valeurs **51,4 / 20,3 / 16,4 / 12,0**, ou le refaire sur le nombre de clients — ce sera alors
  quatre parts de ~25 %, ce qui est le message honnête.
- Le mieux : **deux camemberts côte à côte**, clients et CA. C'est le contraste 25 % → 51 % qui
  raconte l'histoire, pas un chiffre isolé.

## 5. Corriger la page comportementale

Le bubble chart affichait quatre bulles (les segments) avec un axe `nb_achats` de 500 à 800 : ce sont
des sommes par segment, pas des clients. Le refaire sur `dim_clients` : **166 points**, X = `ca_client`,
Y = `nb_achats`, couleur = `segment_valeur`, taille = `panier_moyen`.

C'est ce graphique qui montre le vrai message : les VIP ne sont pas plus à droite ET plus haut, ils
sont plus à droite **sans** être plus haut.

## 6. Refaire le texte de la page 5

Remplacer « les clients à forte valeur combinent nombre d'achats élevé et dépense totale importante »
— c'est faux — par :

> Les VIP réalisent 777 achats contre 794 pour les Fidèles : ils n'achètent pas plus souvent, ils
> achètent 2,7x plus cher (304 $ contre 111 $). Le levier n'est pas la fréquence, c'est la montée
> en gamme.

## 7. Publier

Fichier → Partager → **Gérer l'accès → Public sur le Web (lecture)**. Puis tester le lien en
navigation privée. Un lien en `/edit` n'est visible que de toi ; c'est actuellement le cas des deux
rapports.
