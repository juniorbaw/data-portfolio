# Carnet d'erreurs

Une entrée par erreur réellement commise. Format : ce qui s'est passé, pourquoi, le contrôle qui l'aurait évitée.

---

## Session du 19 août 2026 — profiling European Soccer Database

### 1. `ATTACH` sans `READ_ONLY` crée une base vide, sans erreur

**Fait** : `ATTACH 'database.sqlite' AS soccer (TYPE sqlite)` lancé depuis un dossier où le fichier n'existait pas. Aucune erreur. `SHOW ALL TABLES` a renvoyé 0 ligne.

**Cause** : l'extension SQLite s'ouvre en écriture par défaut. Fichier absent → elle le crée, vide.

**Contrôle** : toujours `READ_ONLY` sur une source. En lecture seule, un fichier absent lève une **vraie** erreur.

**Principe général** : *l'absence d'erreur n'est pas la preuve d'un succès.* Même famille que le fan-out de Fashion Retail — `SUM(total_depense)` ne plantait pas non plus, il renvoyait 7 585 581.

---

### 2. Le prompt disait `memory`, je ne l'ai pas lu

**Fait** : session DuckDB lancée sans fichier de travail. Tout se serait perdu à la fermeture.

**Contrôle** : le prompt affiche le catalogue courant. `memory D` = base en RAM. Lire son prompt avant de travailler.

---

### 3. `kagglehub` avec l'adaptateur PANDAS sur une base SQLite

**Fait** : snippet copié avec `file_path = ""` et `KaggleDatasetAdapter.PANDAS`.

**Cause** : deux erreurs cumulées — chemin vide, et un DataFrame pandas ne lit pas une base SQLite comme un fichier plat.

**Contrôle** : avant de copier un snippet, identifier le **format réel** de la source.

---

### 4. Dépôt Git à la racine du répertoire personnel

**Fait** : `/Users/souleyjr` était un dépôt Git (prompt `git:(master) ✗`), remote pointant vers un exercice Le Wagon. Un seul fichier suivi (`package-lock.json`), donc aucune fuite — mais `git add .` depuis n'importe quel sous-dossier aurait ajouté `Library`, `node_modules`, les PDF.

**Traitement** : `.git` renommé en `.git-home-desactive-20260819` — désactivation réversible plutôt que suppression.

**Contrôle** : `git status` doit **échouer** dans `~`. L'échec est le succès.

**Dette restante** : `~/.ssh/config` ne contient qu'un bloc `Host`, pour `juniorndiaye28`. Le compte `juniorbaw` passe probablement en HTTPS via `.git-credentials`. Deux mécanismes pour deux comptes, sans règle explicite — origine probable des « Repository not found ». À traiter avant publication.

---

### 5. Collision de noms de catalogues

**Fait** : `duckdb soccer.duckdb` attache automatiquement un catalogue nommé `soccer`. Un `ATTACH ... AS soccer` ensuite → `database with name "soccer" already exists`.

**Correction** : nommer le catalogue source `raw`. Le nom dit le rôle.

**Concept** : un catalogue est un espace de noms. Adressage complet `catalogue.schéma.table`. Avec plusieurs catalogues attachés, **toujours qualifier explicitement** — l'implicite finit par trahir.

---

### 6. `SELECT` confondu avec une recherche

**Fait** : `SELECT Player_Attributes FROM information_schema.columns WHERE table catalog =`

**Cause** : `SELECT` répond à « quelles colonnes afficher ? », pas à « quoi chercher ». La recherche appartient à `WHERE`.

**Méthode** : formuler en français dans l'ordre d'exécution du moteur — **d'où** (`FROM`), **quelles lignes** (`WHERE`), **quelles colonnes** (`SELECT`).

---

### 7. Valeur seule dans un `WHERE`

**Fait** : `WHERE player_Attributes table_catalog=raw`

**Règle** : une condition a toujours **trois** morceaux — colonne, opérateur, valeur. Une valeur seule n'est pas une condition. Conditions multiples reliées par `AND` / `OR`.

---

### 8. Chaîne de caractères sans guillemets simples

**Fait** : `table_catalog=raw` au lieu de `table_catalog='raw'`.

**Règle** : guillemets **simples** pour les chaînes, guillemets **doubles** pour les identifiants. L'inverse de l'intuition héritée de Python.

---

### 9. Noms de colonnes inventés

**Fait** : `SELECT name, type` alors que les colonnes s'appellent `column_name` et `data_type` — visibles dans la sortie précédente.

**Contrôle** : `SELECT * FROM table LIMIT 1` pour lire les noms réels avant d'écrire la requête.

---

### 10. Fautes de frappe et de ponctuation

- `informatio_schema` — un `n` manquant
- virgule manquante entre deux expressions du `SELECT`
- parenthèse non fermée sur `count(DISTINCT ...`

**Contrôle** : le parser donne le **numéro de ligne**, le **mot fautif** et une **flèche**. Lire le message avant de deviner. *(Corrigé seul aux 2e et 3e occurrences — réflexe en cours d'installation.)*

---

### 11. `COUNT(DISTINCT id)` pour compter des entités

**Fait** : `COUNT(DISTINCT id) AS joueurs_distincts`.

**Cause** : `id` est une clé technique auto-incrémentée. Unique par construction → renvoie toujours `COUNT(*)`. Elle ne prouve rien sur le grain métier.

**Règle** : pour compter des entités, utiliser la colonne qui **porte l'identité de l'entité** (`player_api_id`), jamais la clé technique.

---

### 12. Division entière

**Piège** : `836 / 183978` en arithmétique entière renvoie 0.

**Parade** : forcer un décimal — `100.0 * ...`.

---

### 13. Copier une valeur de la sortie précédente au lieu de la consigne

**Fait** : filtre sur `'sqlite_sequence'` alors que la consigne portait sur `'Player_Attributes'`.

**Cause** : recopie de ce qui traînait à l'écran. Même réflexe que les DAX tronqués collés sans relecture.

---

### 14. Expliquer une anomalie sans vérifier le contenu de la table

**Fait** : les compositions manquantes attribuées à des « matchs amicaux avec des jeunes du centre de formation ».

**Réalité** : la base ne contient que des championnats nationaux. Volume stable de 3 032 à 3 326 matchs par saison — signature d'un calendrier de championnat.

**Règle** : *avant d'expliquer une anomalie, vérifier ce que la table contient réellement.* Une hypothèse s'énonce, puis se teste. Fait correctement ensuite sur la Bundesliga : hypothèse « moins de clubs » → vérifiée par 2 448 ÷ 8 = 306 = 18 × 17.

---

### 15. Écarter une saison implicitement

**Fait** : « la saison 2008/2009 a 26 % de compositions manquantes, tant mieux car on ne la prend pas en compte » — alors qu'aucune décision de périmètre n'avait été prise.

**Règle** : *un périmètre se déclare, il ne se subit pas.* Toute exclusion doit avoir un critère écrit et un coût énoncé. Décision finalement retenue : saison conservée, écart traité par ratio plutôt que par filtrage.

---

### 16. Énoncer un résultat sans le formuler

**Fait** : « 0 c'est good » au lieu de « après filtrage sur `overall_rating IS NOT NULL`, aucun couple joueur-date n'est en doublon — grain validé sur l'intégralité de la table ».

**Enjeu** : en entretien, on ne demande pas de lancer une requête mais d'**énoncer ce qui a été vérifié et sur quoi**. La phrase complète est la compétence ; le chiffre seul ne l'est pas.

---

## Session du 19 août 2026 — suite : transformation

### 17. Filtre `LIKE` trop large sur les noms de colonnes

**Fait** : `column_name LIKE '%player_%'` sur la table `Match` → **66 colonnes** au lieu de 22. Les `_X` et `_Y` sont des **coordonnées de position sur le terrain**, pas des identifiants de joueurs.

**Évité de justesse** : la liste a été lue avant d'être collée dans l'`UNPIVOT`. Sans cela, des coordonnées auraient été empilées avec des identifiants dans la même colonne.

**Correction** : expression régulière `'^(home|away)_player_[0-9]+$'`. Le `$` final est ce qui exclut les `X` et `Y` — il exige que la chaîne s'arrête après les chiffres.

**Règle** : *toujours lire une liste générée avant de l'utiliser.* Même famille que `sqlite_sequence` compté comme table métier.

---

### 18. `GROUP BY 1,` — virgule finale tolérée

**Fait** : `GROUP BY 1,` avec une virgule orpheline. DuckDB l'accepte.

**Risque** : un autre moteur la rejettera. Ne jamais compter sur la tolérance d'un parser.

---

### 19. Construire une dimension sur une table déjà filtrée

**Fait** : `stg_saisons` bâtie sur `stg_lineups`. Résultat : 2008/2009 démarrait au **2008-08-09** au lieu du **2008-07-18**, soit **22 jours d'écart**. Les matchs de juillet 2008 existent mais sont sans composition, donc absents des lineups, donc invisibles au `min()`.

**Ce qui rend la faute dangereuse** : aucune erreur, et un résultat plausible — août est une date crédible pour une reprise européenne. Sept saisons sur huit étaient justes.

**Signal manqué** : sept juillets et un août dans une série régulière. *Regarder l'exception avant de valider la règle.* Réponse donnée sur le moment : « tout est cohérent au niveau des dates ».

**Règle installée** : *une dimension se construit sur la source la plus complète, jamais sur une table déjà filtrée par un autre critère.*

---

### 20. `PARTITION BY` ne reproduisant pas le grain de sortie

**Fait** : `row_number() OVER (PARTITION BY player_api_id ...)` alors que le grain visé était `(player_api_id, season)`.

**Conséquence** : le rang 1 aurait désigné le relevé le plus récent **toutes saisons confondues** — une ligne par joueur au lieu d'une par joueur et par saison.

**Règle** : *le `PARTITION BY` d'une fonction de fenêtre doit reproduire exactement le grain de la table de sortie.* Si les deux divergent, la numérotation ne dit pas ce qu'on croit.

---

### 21. Règle de sélection sans cas « aucun » — la plus grave de la session

**Fait** : `stg_notes_avant_saison` construite avec une seule borne — « relevé antérieur au début de la saison ». Résultat : **88 480 lignes, exactement 11 060 × 8**, le plafond théorique.

**Diagnostic** : ancienneté moyenne de 429 à 654 jours, **maximum à 3 067 jours (8 ans et demi)**. Des joueurs de 2015/2016 recevaient une note datant de 2007.

**Cause** : sans borne inférieure, `row_number()` retient toujours quelque chose. **La règle sélectionnait systématiquement, y compris quand la bonne réponse était « aucun ».**

**Signal manqué** : la colonne d'effectifs affichait 11 060 sur les huit lignes. *Une série de chiffres identiques dans un agrégat est presque toujours un artefact, pas un fait.* Un résultat qui atteint pile son maximum théorique est un signal, pas une réussite.

**Correction** : seconde borne à 365 jours, et formulation explicite du cas d'exclusion.

---

### 22. Choisir un seuil sans mesurer son coût

**Tentation** : retenir 180 jours, plus proche du pic de la distribution (14 jours, 930 joueurs).

**Mesure** : à 180 jours, la saison 2008/2009 ne retient que **409 joueurs**, contre 3 299 à 6 910 pour les autres. Facteur 8 à 15. Le rythme semestriel d'avant 2013 rend ce seuil structurellement impossible : premier match le 18/07/2008, relevé précédent le 30/08/2007, rien entre les deux.

**Règle** : *un seuil ne se choisit pas dans l'absolu mais contre son coût, et il doit être atteignable dans toutes les périodes du périmètre.* Sinon il crée un biais de sélection : on ne compare plus des saisons mais des régimes de collecte.

---

### 23. Valider trop vite

**Fait** : « tout est cohérent au niveau des dates » sur une sortie contenant trois anomalies — le décalage de 2008/2009, un compte de matchs modifié sans être signalé, et une valeur hors série.

**Règle** : *quand un compte connu réapparaît transformé, le rapprocher de sa valeur d'origine avant de continuer.* C'est ce qui manquait sur Fashion Retail.

---

## Session du 20 août 2026 — construction de l'écart

### 24. Un nom de colonne retapé au lieu d'être recopié

**Fait** : `match_connus` au lieu de `matchs_connus`. Puis `informatio_schema`. Puis `fct_temps_de_joueur` au lieu de `fct_temps_de_jeu_joueur`.

**Cause commune** : retaper de mémoire au lieu de copier.

**Règle** : *un identifiant se copie, il ne se retape jamais.* DuckDB propose souvent le bon nom sous « Candidate bindings » — le lire avant de deviner.

---

### 25. Contrôles qui passent sur une table incomplète

**Fait** : `fct_temps_de_jeu` créée avec **5 colonnes au lieu de 6**. Les trois contrôles de valeurs sont passés — nombre de lignes, dépassements, grain, maximum.

**Cause** : aucun contrôle ne vérifiait la **liste des colonnes**.

**Règle** : *après un `CREATE TABLE`, vérifier les colonnes AVANT les valeurs.* Une table peut être cohérente avec elle-même et ne pas contenir ce qu'on croit.

---

### 26. Un contrôle lancé dont le résultat ne change rien à la suite

**Fait** : `SELECT typeof(overall_rating)` renvoie `VARCHAR`. La requête suivante est écrite comme si de rien n'était, sans `CAST`. `variation_pendant` aurait été une soustraction de chaînes.

**Précédent identique la veille** : sept juillets et un août dans `stg_saisons`, vus puis validés d'un « tout est cohérent ».

**Règle** : *un contrôle n'a de valeur que si son résultat modifie la suite.* Sinon c'est un rituel.

---

### 27. `WHERE` contenant un agrégat

**Fait** : `WHERE overall_rating >= 80 AND round(avg(pct_titularisation),1) < 20.0` → `WHERE clause cannot contain aggregates!`

**Cause** : `avg()` écrit là où la valeur de la ligne suffisait. Chaque ligne portait déjà son `pct_titularisation`.

**Symétrique de l'erreur n°… de la veille** : `HAVING` sans agrégat.

**Règle** : *`WHERE` filtre ligne par ligne, avant tout regroupement. `HAVING` filtre après.* Un agrégat n'existe pas encore au moment du `WHERE`.

---

### 28. Deux niveaux d'agrégation dans une seule passe

**Fait** : `max(team_api_id, count(DISTINCT match_api_id))` — parenthèse jamais fermée et agrégats emboîtés.

**Cause** : vouloir compter par équipe **et** prendre le maximum de ces comptes en une requête.

**Règle** : *deux niveaux d'agrégation demandent deux passes.* Table intermédiaire, sous-requête, ou CTE. C'est un des points de blocage les plus longs en SQL — le repérer, c'est déjà l'avoir résolu.

---

### 29. `PARTITION BY` incomplet — récidive

**Fait** : `PARTITION BY pa.player_api_id` sur `stg_notes_fin_saison`, alors que le grain de sortie est `(season, player_api_id)`.

**Statut** : **répétition exacte de l'erreur n°20**, deux jours après, sur une table de même structure.

**Signal** : l'avertissement venait d'être donné dans le message précédent.

---

### 30. `SELECT` choisi sans rapport avec la question posée

**Fait** : trois fois dans la session — `SELECT season` seul (20 fois la même valeur), `SELECT player_api_id` seul (une colonne d'identifiants illisible), `SELECT *` là où quatre colonnes suffisaient.

**Règle** : *le `SELECT` se choisit en fonction de la question posée.* « Qui sont les surnotés » demande nom, note, temps de jeu, saison.

---

### 31. Une règle documentée mais non appliquée — la plus coûteuse

**Fait** : `stg_notes_fin_saison` construite sans tenir compte du rythme de collecte, alors que la règle métier n°1 était écrite dans `profiling.md` depuis la veille : **semestriel jusqu'en 2012, bimensuel ensuite**.

**Conséquence** : `variation_pendant` couvrait septembre-février sur la première moitié de la période et juillet-mai sur la seconde. Deux fenêtres de durées différentes comparées comme équivalentes. Toute l'analyse de trajectoire était faussée.

**Détection** : 2015/2016 sortait du lot sur **trois indicateurs simultanément**. *Trois signaux convergents sur la même ligne ne sont jamais une coïncidence.*

**Règle** : *avant de construire une table, relire ce qui a déjà été documenté sur les tables sources.* Le profiling ne sert à rien s'il n'est pas consulté au moment de transformer.

---

### 32. Interpréter un classement individuel sans facteur de confusion

**Fait** : classement des joueurs notés 80+ à faible temps de jeu, lu comme une liste de « surnotés ». Vérification externe : Falcao (rupture des ligaments croisés), Casillas (écarté par son entraîneur), Ribéry (saison blanche sur blessure), Trezeguet, Sneijder, Vidić — blessures, suspensions, fins de cycle.

**Cause** : l'indicateur capte **trois phénomènes** que la base ne sépare pas — surnotation, indisponibilité, décision d'entraîneur. Ni blessures ni suspensions ne figurent dans la source.

**Règle** : *quand un facteur non mesuré pollue l'analyse individuelle, monter d'un cran en agrégat.* Le bruit s'y annule au lieu d'invalider chaque cas.

**Point positif** : la vérification externe a été faite spontanément. Tester la vraisemblance d'un résultat contre le monde réel, et pas seulement contre une autre requête, est le bon réflexe.

---

## Session du 21 août 2026 — la thèse

### 33. Trois `CREATE TABLE` enchaînés sans un seul contrôle

**Fait** : `fct_temps_de_jeu_joueur`, `fct_ecart`, `fct_trajectoire` créées à la suite, aucune vérifiée. Troisième occurrence en trois jours.

**Ce qui manquait** : pas la connaissance — la règle est écrite au carnet depuis deux jours — mais **le moment de rappel**.

**Correctif** : bloc PROTOCOLE en tête de `gabarits.sql`, à l'endroit déjà consulté au moment d'écrire. Six questions, trente secondes.

---

### 34. Confondre « ce que j'ai mesuré » et « ce que je crois »

**Fait** : « les devs ajustent plus qu'ils n'anticipent », énoncé alors que la seule mesure disponible était une corrélation de 0,07-0,20 — c'est-à-dire quasiment rien. La thèse n'était pas démontrée à ce moment-là ; elle l'a été deux heures plus tard.

**Règle** : *distinguer explicitement le mesuré du supposé.* En entretien, confondre les deux se paie cher. Formuler « je suppose X, voici le test qui le trancherait ».

---

### 35. Une hypothèse plausible réfutée par les données — le bon usage

**Hypothèse posée** : le jeu anticipe pour les jeunes, via le potentiel.
**Mesure** : anticipation la plus **faible** chez les moins de 23 ans (0,072), croissante avec l'âge (0,118). L'inverse exact.

**Ce n'est pas une erreur** — c'est le fonctionnement normal d'une hypothèse. Consigné ici parce que le réflexe à installer est de **noter l'hypothèse avant le test**, pour que la réfutation soit visible et devienne un résultat au lieu d'être discrètement oubliée.

Quatre hypothèses ont été testées sur l'anomalie 2015/2016, trois éliminées. C'est la séquence à savoir raconter : *j'ai observé X, formulé quatre explications, testé chacune, voici celle qui tient et pourquoi les autres tombent.*

---

### 36. Un percentile sur une distribution concentrée

**Fait** : médiane de `pct_dribble` à **19** chez les gardiens, alors qu'un percentile doit donner 50 par construction.

**Cause** : 717 gardiens sur 2 455 (**29 %**) partagent exactement la valeur 25 — une valeur par défaut du jeu. `percent_rank()` leur attribue à tous le rang de la première occurrence.

**Ce n'était pas un bug de la requête** mais une propriété de la fonction face à des valeurs massivement dupliquées.

**Règle** : *un percentile n'a de sens que sur une distribution étalée.* Vérifier la concentration avant de publier tout percentile.

**Correction** : deux radars distincts, cinq axes propres aux gardiens. **Cinq et non six — on ne fabrique pas un axe pour l'esthétique.**

---

### 37. Deux approximations testées, deux échecs, une exclusion

**Fait** : dénominateur des joueurs transférés. `sum()` plafonne mécaniquement le joueur à 50 %. `max()` produit 5 valeurs au-dessus de 100 %, maximum 109,1 %.

**Conclusion** : aucun dénominateur correct n'existe — les clubs jouent en parallèle et la date du transfert est absente de la source. Exclusion des multi-clubs.

**Règle** : *quand deux corrections échouent pour la même raison de fond, le problème n'est pas la correction — c'est que la métrique n'a pas de sens sur cette population.* Exclure et documenter vaut mieux qu'une troisième approximation.

**Point positif** : les deux échecs sont **chiffrés**. Une exclusion motivée par deux mesures est plus solide qu'une correction qui aurait l'air de marcher.

---

## Principes transverses accumulés

1. **L'absence d'erreur n'est pas la preuve d'un succès.** Après chaque opération : « qu'est-ce qui pourrait être faux sans qu'aucune erreur ne s'affiche ? », puis lancer la commande qui répond.
2. **Une erreur bavarde est un cadeau, un silence est un piège.**
3. **Chercher la concentration.** Toute anomalie : diffuse, ou concentrée sur une date, un pays, une position, une plage d'identifiants ? La réponse change le traitement.
4. **Agrégat pour détecter, cas individuel pour comprendre, agrégat pour confirmer.**
5. **La documentation d'une source décrit ce que l'auteur croit avoir produit ; le profiling décrit ce qu'il a produit.**
6. **Un effectif accompagne toujours un chiffre.**
7. **Une clé technique ne prouve jamais un grain métier.**
8. **Écrire le nombre de lignes attendu AVANT toute transformation.** Sans ce chiffre posé d'avance, aucun moyen de savoir si la transformation est juste. C'est exactement ce qui manquait sur Fashion Retail : 2 750 en entrée, 2 750 attendues en sortie, et le 7 585 581 aurait sauté aux yeux.
9. **Une série de chiffres identiques dans un agrégat est presque toujours un artefact.**
10. **Un résultat qui atteint pile son maximum théorique est un signal, pas une réussite.**
11. **Regarder l'exception avant de valider la règle.**
12. **Le code qui tourne n'est pas le code qui est juste**, et l'écart entre les deux ne se voit qu'en mesurant.
13. **Une règle de sélection doit prévoir le cas où rien ne convient.**
14. **Compter la bonne entité, pas les lignes qui la portent** — `count(DISTINCT match_api_id)`, jamais `count(*)`.
15. **Un identifiant se copie, il ne se retape jamais.**
16. **Après un `CREATE TABLE`, vérifier les colonnes avant les valeurs.**
17. **Un contrôle n'a de valeur que si son résultat modifie la suite.** Sinon c'est un rituel.
18. **Deux niveaux d'agrégation demandent deux passes.**
19. **Avant de construire une table, relire ce qui a été documenté sur ses sources.**
20. **Quand un facteur non mesuré pollue l'analyse individuelle, monter d'un cran en agrégat.**
21. **Trois signaux convergents sur la même ligne ne sont jamais une coïncidence.**
22. **Une règle de périmètre se déclare par indicateur, pas une fois pour toutes.**
23. **Distinguer explicitement le mesuré du supposé.**
24. **Noter l'hypothèse avant le test**, pour que sa réfutation devienne un résultat.
25. **Un percentile n'a de sens que sur une distribution étalée.**
26. **Quand deux corrections échouent pour la même raison de fond, la métrique n'a pas de sens sur cette population** — exclure et documenter.
27. **Un signal parasite peut dominer le signal cherché.** Le retour vers la moyenne masquait entièrement la réaction du studio. Le neutraliser était la condition du résultat.
28. **Une clé composite reconstruite est le premier risque de fan-out.** Contrôler que le `LEFT JOIN` laisse le nombre de lignes strictement inchangé.
