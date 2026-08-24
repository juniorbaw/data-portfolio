# Le paysage data — savoir ce qu'un nom veut dire

Fiche de repérage. Objectif : devant n'importe quel nom d'outil dans une offre d'emploi, savoir en trois secondes de quelle famille il relève.

---

## Les trois familles, et une quatrième

| Famille | Rôle | Métaphore |
|---|---|---|
| **Langues** | ce que tu écris | les règles du jeu |
| **Moteurs** | ce qui exécute et détient les données | le stade |
| **Transformation / orchestration** | ce qui ordonne, teste, planifie | l'entraîneur |
| **Restitution (BI)** | ce qui montre le résultat | la retransmission télé |

Une offre d'emploi mélange toujours les quatre sans le dire. Savoir trier, c'est déjà comprendre le poste.

---

# 1. LES LANGUES

## SQL — la seule vraiment incontournable

Créée en 1974, toujours dominante. Aucun autre langage informatique n'a cette longévité.

**Ce qu'elle fait** : interroger et transformer des données organisées en tables.

**Ce qu'elle ne fait pas** : boucles, machine learning, appels réseau, graphiques.

**Les dialectes** — le noyau est identique partout, les fonctions avancées diffèrent :

| Dialecte | Moteur |
|---|---|
| ANSI SQL | le standard commun |
| T-SQL | SQL Server, Synapse |
| PL/SQL | Oracle |
| PostgreSQL | Postgres, Redshift, DuckDB (proche) |
| Snowflake SQL | Snowflake |
| GoogleSQL | BigQuery |
| SparkSQL | Databricks, Spark |

Passer d'un dialecte à l'autre coûte quelques jours, pas quelques mois. **C'est pour ça que le SQL est l'investissement le plus rentable du métier : il ne se périme pas et il est portable.**

## Python — le couteau suisse

Ce que SQL ne sait pas faire : boucles, machine learning, API, automatisation, parsing de formats exotiques.

Bibliothèques : `pandas` (tables en mémoire), `polars` (idem, plus rapide), `numpy`, `scikit-learn` (ML classique), `matplotlib` / `plotly` (graphiques), `requests`.

**Règle pratique** : si SQL peut le faire, fais-le en SQL — le moteur est optimisé pour ça et la requête est lisible par l'équipe. Python prend le relais quand SQL bloque.

## R

Statistiques et recherche. Fort en académique, pharma, biostatistique, économétrie. Rare en entreprise hors ces secteurs. Ne pas investir sauf si le secteur l'exige.

## DAX

Langage de calcul de **Power BI uniquement**. Sert à écrire les mesures d'un modèle. Ressemble à Excel en surface, fonctionne très différemment — la notion de contexte de filtre n'a pas d'équivalent ailleurs.

Non transférable : le DAX ne sert que dans Power BI.

## M / Power Query

Langage de préparation dans Power BI et Excel. Nettoyage, pivots, jointures avant le modèle. Se pratique surtout via une interface graphique.

## LookML

Langage de modélisation de **Looker uniquement**. Décrit une couche sémantique — les dimensions, les mesures, les jointures autorisées — que les utilisateurs interrogent ensuite sans écrire de SQL.

Concept important au-delà de Looker : **la couche sémantique**. C'est le vocabulaire métier posé au-dessus des tables. Elle apparaît dans l'offre Hermès.

## Scala / Java

Historiquement Spark. En recul : la plupart des équipes font du Spark en Python (`PySpark`).

## JavaScript

Visualisation web sur mesure : `D3.js`, `Observable Plot`. Utile pour un portfolio, rare dans une fiche de poste analyste.

---

# 2. LES MOTEURS

## La distinction fondamentale : OLTP contre OLAP

**OLTP** — bases transactionnelles. Optimisées pour écrire une ligne à la fois, très vite. Ce sont les bases qui font tourner les applications. Rangement **par ligne**.

**OLAP** — bases analytiques. Optimisées pour lire des millions de lignes et agréger. Rangement **par colonne** — si tu ne demandes que 3 colonnes sur 42, seules ces 3 sont lues. D'où la vitesse.

Ton métier vit sur l'OLAP. Comprendre cette distinction est une question d'entretien classique.

## Bases transactionnelles (OLTP)

| Nom | Remarque |
|---|---|
| **PostgreSQL** | open source, très répandu, excellent standard |
| **MySQL / MariaDB** | web historique |
| **SQL Server** | Microsoft, forte présence grands comptes |
| **Oracle** | banque, assurance, ERP historiques |
| **SQLite** | fichier unique, embarqué — **ta source du projet foot** |

## Entrepôts cloud (OLAP) — le cœur du métier aujourd'hui

| Nom | Remarque |
|---|---|
| **Snowflake** | leader du segment. Séparation stockage / calcul. **C'est la cible de la migration Hermès.** |
| **BigQuery** | Google. Facturation à la donnée scannée. Destination native de l'export GA4. |
| **Databricks** | né de Spark, orienté lakehouse et ML. `Databricks SQL` pour l'analytique. |
| **Amazon Redshift** | AWS, plus ancien, en perte de terrain |
| **Microsoft Fabric / Synapse** | offre Microsoft intégrée à Power BI |

## Moteurs embarqués

| Nom | Remarque |
|---|---|
| **DuckDB** | OLAP dans un fichier, sans serveur. **Le « SQLite de l'analytique ».** Ce que tu utilises. |
| **SQLite** | OLTP dans un fichier |

**Pourquoi DuckDB compte pour toi** : il te fait travailler en colonnes, avec une syntaxe proche de Postgres, sur ton portable, gratuitement. Tout ce que tu y apprends se transpose à Snowflake. C'est le meilleur terrain d'entraînement possible.

## Traitement distribué

| Nom | Remarque |
|---|---|
| **Apache Spark** | calcul réparti sur plusieurs machines. Gros volumes. |
| **Trino / Presto** | requêter plusieurs sources sans les déplacer |
| **Amazon Athena** | Trino géré par AWS, sur fichiers S3 |

## Temps réel

**ClickHouse**, **Apache Druid**, **Apache Pinot** — tableaux de bord à la seconde. Niche, mais recherchés.

## Formats de fichiers — à connaître de nom

| Format | Remarque |
|---|---|
| **CSV** | texte, sans types, lourd. Universel et médiocre. |
| **Parquet** | colonnaire, compressé, typé. **Le standard de l'analytique.** |
| **Delta Lake / Apache Iceberg** | Parquet plus un historique de versions et des transactions. Base du « lakehouse ». |

---

# 3. TRANSFORMATION ET ORCHESTRATION

## dbt — data build tool

**Ce que c'est** : un outil qui exécute tes `SELECT` dans le bon ordre, les teste et les documente.

**Concrètement, trois mécanismes :**

1. **Un modèle = un fichier `.sql` contenant un seul `SELECT`.** Le nom du fichier devient le nom de la table. Pas de `CREATE TABLE` à écrire.

2. **`{{ ref('autre_modele') }}` remplace le nom de table en dur.** dbt en déduit le graphe de dépendances et lance tout dans l'ordre. Modifier un modèle amont reconstruit automatiquement l'aval.

3. **Les tests vivent dans `schema.yml`**, à côté des modèles. `unique`, `not_null`, `accepted_values`, `relationships`, plus les tests écrits à la main. Rejoués à chaque exécution.

**Pourquoi c'est devenu un standard** : avant dbt, les transformations vivaient dans des interfaces graphiques propriétaires, non versionnables, non testables. dbt les a ramenées à des fichiers texte dans Git, avec des tests. Ça a rendu au SQL les pratiques du développement logiciel.

**Ce que dbt ne fait pas** : il n'extrait pas les données, ne les charge pas, ne les visualise pas. Il transforme, à l'intérieur de l'entrepôt. Le `T` de ELT.

**Core / Cloud** : `dbt Core` est gratuit et open source, en ligne de commande. `dbt Cloud` est l'offre payante avec interface, planification et gestion d'équipe.

**Pour toi** : dbt est **la compétence pivot entre Data Analyst et Analytics Engineer**. C'est le poste que tu vises à trois ans. En avoir un projet public te distingue immédiatement.

## Les alternatives à dbt

| Nom | Positionnement |
|---|---|
| **SQLMesh** | concurrent plus récent. Gère mieux les environnements et évite de tout reconstruire à chaque changement. Communauté plus petite. |
| **Dataform** | équivalent racheté par Google, intégré à BigQuery. Enfermé dans l'écosystème Google. |
| **Coalesce** | interface graphique, orienté grands comptes |

**Est-ce que dbt est le meilleur ?** Ce n'est pas le plus élégant techniquement — SQLMesh corrige plusieurs de ses défauts de conception. Mais c'est celui que les entreprises utilisent, celui qu'on demande dans les offres, et celui qui a la plus grande communauté. **En début de carrière, l'écosystème compte davantage que l'élégance.**

## Orchestrateurs — à ne pas confondre avec dbt

Un orchestrateur planifie et enchaîne **des tâches de toute nature** : extraire d'une API, lancer dbt, entraîner un modèle, envoyer un mail. dbt ne fait que le SQL.

| Nom | Remarque |
|---|---|
| **Apache Airflow** | le plus répandu. Créé chez Airbnb. Verbeux mais universel. |
| **Dagster** | plus moderne, raisonne en « actifs de données » plutôt qu'en tâches |
| **Prefect** | plus léger, syntaxe Python simple |

**Dans une équipe type** : Airflow déclenche dbt à 6 h. dbt transforme. Power BI rafraîchit à 8 h.

## Ingestion — le E et le L

Ces outils copient les données depuis les sources vers l'entrepôt. Ils ne transforment pas.

| Nom | Remarque |
|---|---|
| **Fivetran** | leader, payant, connecteurs clés en main |
| **Airbyte** | alternative open source |
| **Stitch**, **Meltano** | autres options |

## ETL classiques d'entreprise

**Talend**, **Informatica**, **SSIS**, **Alteryx** — génération précédente, interfaces graphiques. Encore massivement présents en banque, assurance, industrie. Une offre qui mentionne Talend ou Informatica décrit souvent un système d'information ancien.

## ETL contre ELT — la question d'entretien

**ETL** : Extract, Transform, Load. On transforme **avant** de charger, sur un serveur dédié. Le stockage coûtait cher, il fallait arriver propre.

**ELT** : Extract, Load, Transform. On charge brut, on transforme **dans** l'entrepôt. Le stockage cloud est bon marché et le calcul est élastique. C'est la logique moderne, et celle de dbt.

**Ta base DuckDB applique déjà ce principe** : `raw` en lecture seule contient la source intouchée, `main` contient tes transformations. C'est un ELT en miniature.

---

# 4. RESTITUTION (BI)

| Nom | Remarque |
|---|---|
| **Power BI** | Microsoft. Le plus répandu en Europe, surtout en France. Langage DAX. **Cité dans l'offre Hermès.** |
| **Tableau** | Salesforce. Fort en visualisation exploratoire. |
| **Looker** | Google. Couche sémantique en LookML. Cher, orienté grands comptes. |
| **Looker Studio** | ex-Data Studio. Gratuit. Fréquent en marketing digital. |
| **Qlik Sense** | historique, encore présent en industrie |
| **Metabase** | open source, simple, aimé des start-ups |
| **Apache Superset** | open source, plus technique |
| **Sigma** | interface tableur sur entrepôt cloud, en croissance |
| **Mode**, **Hex** | notebooks SQL + Python, orientés équipes data |

---

# 5. LES MÉTIERS — qui utilise quoi

Notation : ⬤⬤⬤ cœur du poste · ⬤⬤ fréquent · ⬤ occasionnel

## Data Analyst

SQL ⬤⬤⬤ · Outil BI ⬤⬤⬤ · Excel ⬤⬤ · Python ⬤ · dbt ⬤

Répond à des questions métier. Construit des tableaux de bord. **Le SQL et un outil BI font 80 % du poste.** dbt entre progressivement dans les descriptions.

## Analytics Engineer — ta cible à trois ans

SQL ⬤⬤⬤ · dbt ⬤⬤⬤ · Git ⬤⬤⬤ · Entrepôt ⬤⬤ · Python ⬤

Métier apparu vers 2019, créé par la diffusion de dbt. Construit les tables propres que les analystes consomment. Modélisation dimensionnelle, tests, documentation, couche sémantique.

**Pont entre Data Analyst et Data Engineer.** Moins d'infrastructure qu'un DE, plus de rigueur logicielle qu'un DA. **Ce que tu fais depuis deux jours est exactement ce métier.**

## Data Engineer

Python ⬤⬤⬤ · SQL ⬤⬤ · Airflow ⬤⬤ · Spark ⬤⬤ · Cloud ⬤⬤ · Docker ⬤

Construit et maintient les tuyaux. Ingestion, fiabilité, coût, temps réel. Plus proche du développement logiciel que de l'analyse.

## Data Scientist

Python ⬤⬤⬤ · SQL ⬤⬤ · scikit-learn ⬤⬤ · Statistiques ⬤⬤⬤ · R ⬤

Modélisation prédictive, expérimentation, statistiques. **Le SQL reste indispensable** — la plupart passent plus de temps à préparer les données qu'à modéliser.

## Machine Learning Engineer

Python ⬤⬤⬤ · Docker / Kubernetes ⬤⬤ · MLOps ⬤⬤ · SQL ⬤

Met les modèles en production et les surveille. Plus ingénierie que science.

## BI Analyst / BI Developer

SQL ⬤⬤⬤ · DAX ou LookML ⬤⬤⬤ · Modélisation ⬤⬤⬤ · Python ⬤

Spécialiste de la couche de restitution. Modèles sémantiques, mesures, performance des rapports. Très demandé en grande entreprise.

## Data Quality Analyst / Data Steward — le poste Hermès

SQL ⬤⬤⬤ · Profiling ⬤⬤⬤ · Documentation ⬤⬤⬤ · Catalogues ⬤⬤ · Python ⬤

Mesure et améliore la qualité d'un patrimoine de données. Règles de validation, indicateurs de qualité, rétro-documentation, gap analysis lors des migrations.

Outils spécifiques : **Collibra**, **Alation**, **Informatica Data Quality**, **Monte Carlo**, **Great Expectations**, et les tests dbt.

**C'est exactement la mission de l'offre Hermès**, et exactement ce que tu as produit avec `profiling.md`. Ce document est ton livrable type pour ce métier.

## Web Analyst / Digital Analyst

GA4 ⬤⬤⬤ · Google Tag Manager ⬤⬤⬤ · SQL ⬤⬤ · BigQuery ⬤⬤ · Looker Studio ⬤⬤ · Python ⬤

Mesure le comportement en ligne. Tunnels de conversion, attribution, plan de marquage.

**Le SQL y est devenu central** : GA4 exporte nativement vers BigQuery, et l'analyse fine passe obligatoirement par là. Un web analyst qui écrit du SQL vaut nettement plus qu'un qui reste dans l'interface.

Autres outils : Adobe Analytics, Matomo, Piano Analytics.

## Product Analyst

SQL ⬤⬤⬤ · Amplitude / Mixpanel ⬤⬤ · Tests A/B ⬤⬤ · Statistiques ⬤⬤ · Python ⬤

Analyse l'usage d'un produit numérique. Rétention, cohortes, expérimentation.

## Marketing Analyst / CRM Analyst

SQL ⬤⬤ · Excel ⬤⬤⬤ · BI ⬤⬤ · Outils CRM ⬤⬤ · Python ⬤

Segmentation, RFM, campagnes, valeur client. Outils : Salesforce, Braze, Klaviyo, Adobe Campaign.

**C'est le métier le plus proche de ton projet Fashion Retail.**

## Financial Analyst / FP&A

Excel ⬤⬤⬤ · Power BI ⬤⬤ · SQL ⬤ · Outils EPM ⬤

Budget, prévision, reporting financier. Excel reste roi. Le SQL est un différenciateur fort et rare.

## Business Analyst

SQL ⬤ · Excel ⬤⬤ · BI ⬤ · Spécifications ⬤⬤⬤

Traduit un besoin métier en spécifications. Moins technique. Attention : l'intitulé recouvre des réalités très différentes selon les entreprises.

## Data Architect

Modélisation ⬤⬤⬤ · Cloud ⬤⬤⬤ · Gouvernance ⬤⬤⬤ · SQL ⬤⬤

Conçoit la structure d'ensemble. Poste senior, rarement accessible avant dix ans.

---

# 6. CE QUI COMPTE POUR TOI

## L'ordre d'investissement

1. **SQL** — portable, durable, présent dans tous les métiers ci-dessus sans exception. C'est le meilleur rendement possible.
2. **Modélisation** — grain, clés, étoile, additivité. **Ce n'est pas un outil, c'est du raisonnement, et ça ne se périme jamais.** C'est ce que tu travailles depuis deux jours.
3. **dbt + Git** — le pivot vers Analytics Engineer.
4. **Un outil BI** — Power BI en priorité vu le marché français et l'offre Hermès.
5. **Python** — utile, mais après les quatre précédents pour ton profil.

## Ce qui est surestimé en début de carrière

Spark et le big data — la plupart des entreprises n'ont pas des volumes qui le justifient. Le machine learning — sans données propres, aucun modèle ne tient. La multiplication des outils BI — en maîtriser un vraiment vaut mieux qu'en survoler quatre.

## La phrase à retenir

**Les outils changent tous les cinq ans. Le grain, les clés, l'additivité et le contrôle ne changent jamais.**

Ton fan-out de Fashion Retail se serait produit à l'identique en Talend en 2005, en Spark en 2015, en dbt en 2026. C'est pour ça qu'il fait une bonne histoire d'entretien — il prouve un raisonnement, pas un outil.
