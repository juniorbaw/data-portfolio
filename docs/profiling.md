# Profiling — European Soccer Database

**Source** : Kaggle `hugomathien/soccer`, fichier SQLite unique, 313 090 048 octets (313 Mo), extraction datée du 19 septembre 2019.
**Accès** : attaché dans DuckDB sous le catalogue `raw`, en `READ_ONLY`.
**Localisation** : `~/data/soccer/database.sqlite` — hors dépôt Git.
**Base de travail** : `~/data-portfolio/soccer.duckdb`, catalogue `main`.

Session : 19 août 2026.

---

## 0. Inventaire

8 tables présentes, dont **1 technique** :

| Table | Nature |
|---|---|
| `Country`, `League`, `Match`, `Player`, `Player_Attributes`, `Team`, `Team_Attributes` | métier |
| `sqlite_sequence` | **technique** — compteurs d'auto-incrément SQLite, à exclure de tout inventaire |

Méthode : `information_schema.tables` filtrée sur `table_catalog = 'raw'`, plutôt que `SHOW ALL TABLES` — le catalogue système est requêtable, filtrable et joignable, donc automatisable.

---

## 1. Player_Attributes

### Volumétrie

- **183 978 lignes** · **11 060 joueurs distincts** · **42 colonnes**
- **16,6 relevés par joueur** en moyenne — facteur de fan-out potentiel en cas de jointure sans réduction de grain

### Grain

**`(player_api_id, date)`**, valide **sous condition** `overall_rating IS NOT NULL`.

| Test | Résultat |
|---|---|
| `COUNT(*)` | 183 978 |
| `COUNT(DISTINCT (player_api_id, date))` | 183 142 |
| Écart | **836** |
| Idem après `WHERE overall_rating IS NOT NULL` | **0** |

`id` est une clé technique auto-incrémentée : unique par construction, elle ne prouve rien sur le grain métier et ne doit jamais servir de test.

### Défaut n°1 — lignes fantômes

**836 doublons sur le couple joueur-date, soit 0,454 %.**

Nature : à chaque date concernée, une ligne porte des valeurs, les autres sont **intégralement nulles**. Pas des versions contradictoires — des lignes créées et jamais renseignées.

Traitement : `WHERE overall_rating IS NOT NULL`. Aucune perte, aucun arbitrage.

| Date | Couples en doublon | Part |
|---|---|---|
| 2007-02-22 | 734 | 87,8 % |
| 2013-09-20 | 30 | 3,6 % |
| 43 autres dates | 72 | 8,6 % |

Le pic du 22/02/2007 est un incident de chargement, **antérieur au périmètre** (§2), donc neutralisé par filtrage temporel.

### Règle métier implicite n°1 — rythme des relevés

| Période | Rythme observé |
|---|---|
| 2007 → 2012 | **semestriel** — deux campagnes annuelles, ~22 février et ~30 août |
| 2013 → 2016 | **bimensuel**, à jour fixe dans la semaine |

**Contredit la documentation Kaggle**, qui annonce un rythme hebdomadaire sur toute la période.

Confirmation indépendante : la distribution des anciennetés de relevés (§4) ne contient que des **multiples de 7** — 1, 7, 14, 21, 28, 35… Les valeurs 107, 170, 172 cassent la série avec des effectifs négligeables : bruit, pas signal.

Les dates de doublons se concentrent sur ces jours de campagne, ce qui est cohérent : volume traité maximal, donc risque d'incident maximal.

**Conséquence analytique majeure** : la règle « dernier relevé avant le coup d'envoi » n'a pas la même précision selon l'année. Voir §4.

### Défaut n°2 — variations aberrantes (à instruire)

Joueur `32968` : `dribbling` fait **66 → 32 → 67** en trois relevés consécutifs. Une capacité technique ne s'effondre pas de moitié en six mois pour remonter aussitôt.

Statut : anomalie de saisie probable, **non quantifiée**. À mesurer avant toute analyse de progression.

---

## 2. Match

### Volumétrie et grain

- **25 979 lignes** · **`match_api_id` unique sans filtrage** (25 979 = 25 979)
- **8 saisons**, du **2008-07-18** au **2016-05-25**

**Cette table borne le périmètre du projet.** Tout relevé antérieur à juillet 2008 est hors sujet, ce qui neutralise 88 % du défaut n°1.

### Remplissage des compositions

22 colonnes de titulaires (`home_player_1..11`, `away_player_1..11`), format large non normalisé.

| Colonne | Renseignée | Taux |
|---|---|---|
| `home_player_1` | 24 755 | 95,3 % |
| `home_player_11` | 24 424 | **94,0 %** |
| `away_player_11` | 24 425 | 94,0 % |

**Le remplissage décroît de la position 1 à la position 11.** La source remplit dans l'ordre et s'interrompt parfois : un match peut compter 8 titulaires sur 11.

**Risque** : un comptage naïf sous-estimerait les joueurs en fin de liste. La position étant corrélée au poste, **le biais ne serait pas neutre entre postes**. À vérifier après dépivotage.

Symétrie domicile/extérieur : écart d'une ligne. Défaut structurel, non lié au côté.

### Couverture par saison

| Saison | Matchs | Avec compo | Taux | Manquants |
|---|---|---|---|---|
| 2008/2009 | 3 326 | 2 456 | **73,8 %** | 870 |
| 2009/2010 | 3 230 | 3 036 | 94,0 % | 194 |
| 2010/2011 | 3 260 | 3 087 | 94,7 % | 173 |
| 2011/2012 | 3 220 | 3 101 | 96,3 % | 119 |
| 2012/2013 | 3 260 | 3 171 | 97,3 % | 89 |
| 2013/2014 | 3 032 | 2 999 | 98,9 % | 33 |
| 2014/2015 | 3 325 | 3 277 | 98,6 % | 48 |
| 2015/2016 | 3 326 | 3 297 | 99,1 % | 29 |
| **Total** | **25 979** | **24 424** | **94,0 %** | **1 555** |

Progression monotone. Interprétation retenue : **amélioration de la collecte à la source**, les compositions n'étant pas systématiquement publiées en début de période. Cette base ne contient que des championnats nationaux — pas d'amicaux, pas de compétitions de jeunes.

### DÉCISION DE PÉRIMÈTRE

**La saison 2008/2009 est conservée.**

Critère : aucune saison exclue, l'écart de couverture étant traité par la méthode plutôt que par le filtrage.

Coût assumé : 73,8 % de couverture contre 94 à 99 % ensuite, soit **plus de 20 points d'écart**. Un joueur y paraîtra avoir moins joué alors que c'est la donnée qui manque.

**Parade obligatoire, structurante pour tout le projet** :

> Le temps de jeu ne se compte jamais en valeur absolue, mais en **part des matchs de son équipe dont la composition est connue**. Le dénominateur est la couverture réelle, jamais le calendrier théorique.

Un ratio est robuste à un taux de couverture variable ; un compte ne l'est pas.

**2008/2009 est la saison la plus fragile du périmètre — c'est la deuxième fois qu'elle se distingue (voir aussi §4, rétention à 41 %).** Toute comparaison inter-saisons doit le mentionner.

---

## 3. League — répartition et contrôle

| Championnat | Matchs | ÷ 8 | Clubs déduits |
|---|---|---|---|
| Spain LIGA BBVA | 3 040 | 380 | 20 |
| England Premier League | 3 040 | 380 | 20 |
| France Ligue 1 | 3 040 | 380 | 20 |
| Italy Serie A | 3 017 | 377,1 | **non entier — 23 matchs manquants vs 20 clubs** |
| Netherlands Eredivisie | 2 448 | 306 | 18 |
| Germany 1. Bundesliga | 2 448 | 306 | 18 |
| Portugal Liga ZON Sagres | 2 052 | 256,5 | **non entier — format variable** |
| Poland Ekstraklasa | 1 920 | 240 | 16 |
| Scotland Premier League | 1 824 | 228 | 12 (format avec split) |
| Belgium Jupiler League | 1 728 | 216 | format avec play-offs |
| Switzerland Super League | 1 422 | 177,75 | **non entier — format variable** |
| **Total** | **25 979** | | |

**Méthode de contrôle** : pour N clubs en aller-retour, N × (N − 1) matchs par saison. 18 × 17 = 306 pour la Bundesliga, 20 × 19 = 380 pour les trois grands. Le calcul tombe au match près, ce qui valide la volumétrie.

**Trois anomalies à instruire** : Italie, Portugal, Suisse donnent des moyennes non entières. Format changé en cours de période, ou matchs manquants. Non résolu.

---

## 4. Tables construites

### `main.stg_lineups` — compositions dépivotées

**Grain : une ligne = un joueur aligné dans un match.**

Construction : `UNPIVOT` des 22 colonnes de titulaires. Sélection des colonnes par expression régulière `'^(home|away)_player_[0-9]+$'` — le `$` final est indispensable : sans lui, le filtre attrape aussi les 44 colonnes `_X` et `_Y`, qui sont des **coordonnées de position sur le terrain**, pas des identifiants de joueurs.

| Contrôle | Attendu | Obtenu |
|---|---|---|
| Lignes | ≤ 25 979 × 22 = 571 538 | **542 281** |
| Matchs distincts | < 25 979 | **25 221** |
| Joueurs distincts | ≤ 11 060 | **11 060** |
| Doublons `(match_api_id, poste)` | 0 | **0** |

**`UNPIVOT` écarte les valeurs nulles** — comportement vérifié, non supposé : la somme des `count()` de 3 colonnes testées vaut exactement le nombre de lignes produites (74 117 = 74 117).

Conséquences :

- Une ligne = un joueur réellement aligné. Aucune ligne vide à nettoyer.
- **Le nombre de lignes par match est variable** (de 1 à 22). Le dénominateur n'est jamais 11 par équipe — confirmation directe de la parade §2.
- **758 matchs ont disparu** (25 979 − 25 221), ceux dont aucune position n'était renseignée. Tous concentrés sur 2008/2009 : 3 326 − 2 568 = 758. Les sept autres saisons n'ont perdu aucun match entier.

**Intégrité référentielle parfaite** : 11 060 joueurs distincts dans les compositions, exactement le total de `Player_Attributes`. Chaque joueur aligné existe dans la table des attributs, et réciproquement. La jointure principale ne perdra personne.

### Défaut n°3 — joueurs en double dans un même match

**14 cas sur 542 281 lignes, soit 0,0026 %.**

**11 des 14 partagent la signature `[home_player_1, away_player_11]`** — même couple de positions, 11 matchs et 11 joueurs différents. Un accident de saisie ne se répète pas 11 fois au même endroit : c'est un **défaut systématique de la chaîne d'alimentation**, la valeur de la première position domicile étant recopiée en dernière position adverse. `home_player_1` étant le gardien, cela produit 11 gardiens listés simultanément dans les deux équipes.

3 cas isolés sans motif : `[home_player_2, home_player_4]`, `[home_player_1, away_player_9]`, `[home_player_3, away_player_11]`. Le match `1043052` est doublement corrompu.

**Non corrigé.** Parade : compter `count(DISTINCT match_api_id)`, jamais `count(*)` — on compte des matchs, pas des lignes. Plus robuste en général, et rend le nettoyage inutile.

### `main.stg_saisons` — calendrier

**Grain : une ligne = une saison.**

| Saison | Début | Fin |
|---|---|---|
| 2008/2009 | 2008-07-18 | 2009-05-31 |
| 2009/2010 | 2009-07-11 | 2010-05-16 |
| 2010/2011 | 2010-07-17 | 2011-05-29 |
| 2011/2012 | 2011-07-16 | 2012-05-23 |
| 2012/2013 | 2012-07-13 | 2013-06-02 |
| 2013/2014 | 2013-07-13 | 2014-05-18 |
| 2014/2015 | 2014-07-18 | 2015-05-31 |
| 2015/2016 | 2015-07-17 | 2016-05-25 |

**Aucun chevauchement** : chaque fin précède le début suivant. La fenêtre « avant le coup d'envoi » est donc non ambiguë.

> **ERREUR DE CONSTRUCTION CORRIGÉE.** Première version bâtie sur `stg_lineups` : 2008/2009 démarrait au **2008-08-09**, soit **22 jours trop tard**, les matchs de juillet 2008 étant sans composition donc absents des lineups. Les sept autres saisons étaient justes, ce qui rendait l'anomalie discrète — sept juillets et un août.
>
> **Règle installée : une dimension se construit sur la source la plus complète, jamais sur une table déjà filtrée par un autre critère.** Le calendrier ne doit rien devoir à la qualité des compositions.
>
> Aucune erreur n'était levée ; le résultat était plausible. C'est ce qui rend ce type de faute dangereux.

### `main.stg_notes_avant_saison` — note du jeu avant le coup d'envoi

**Grain : une ligne = un joueur × une saison.** 51 996 lignes.

**Règle de sélection, définitive** :

> Dernier relevé `overall_rating` non nul, **strictement antérieur** au premier match de la saison **et daté de moins de 365 jours** avant celui-ci. Sans relevé dans cette fenêtre, le joueur est exclu de la saison.

Le second membre est aussi important que le premier : **une règle de sélection doit prévoir le cas où rien ne convient.**

**Justification du seuil de 365 jours** : c'est la seule valeur atteignable sur les huit saisons. Le rythme semestriel d'avant 2013 rend tout seuil inférieur structurellement impossible en 2008/2009 — le premier match est le 18/07/2008, le relevé de campagne précédent date du 30/08/2007, soit 323 jours plus tôt, sans rien entre les deux. Un seuil de 180 jours n'y retiendrait que **409 joueurs**, contre 3 299 à 6 910 les autres saisons : facteur 8 à 15. **Un seuil doit être atteignable dans toutes les périodes du périmètre, sinon il crée un biais de sélection** — on ne compare plus des saisons mais des régimes de collecte.

**Rétention par saison** :

| Saison | Retenus | Rétention |
|---|---|---|
| 2008/2009 | 4 495 | 41 % |
| 2009/2010 | 5 730 | 52 % |
| 2010/2011 | 6 235 | 56 % |
| 2011/2012 | 6 759 | 61 % |
| 2012/2013 | 6 953 | 63 % |
| 2013/2014 | 7 230 | 65 % |
| 2014/2015 | 7 328 | **66 %** |
| 2015/2016 | 7 266 | 66 % |
| **Total** | **51 996** | |

**À publier à côté de tout chiffre issu de cette table.** La rétention passe de 41 % à 66 % : les saisons ne sont pas équivalentes en couverture.

> **ERREUR DE CONSTRUCTION CORRIGÉE.** Première version sans borne d'ancienneté : **88 480 lignes, exactement 11 060 × 8**, le plafond théorique. Chaque joueur avait un relevé antérieur à chacune des huit saisons — y compris avant juillet 2008. Ancienneté moyenne de 429 à 654 jours, **maximum à 3 067 jours, soit 8 ans et demi** : des joueurs de 2015/2016 se voyaient attribuer une note de 2007.
>
> Cause : la jointure ne posait qu'une borne haute. Sans borne basse, `row_number()` retenait toujours quelque chose, même sans rien de pertinent. **La règle sélectionnait systématiquement, y compris quand la bonne réponse était « aucun ».**
>
> Signal manqué : la colonne d'effectifs affichait 11 060 sur les huit lignes. **Une série de chiffres identiques dans un agrégat est presque toujours un artefact, pas un fait.**

Distribution des anciennetés retenues, saison 2015/2016 — pic à **14 jours (930 joueurs)**, correspondant à la mise à jour de sortie du jeu, deux semaines avant la reprise. Décroissance ensuite, sans rupture nette : le seuil ne pouvait pas être lu sur la distribution seule, il a fallu mesurer son coût par saison.

---

## 5. Synthèse

| Objet | Statut |
|---|---|
| Grain `Player_Attributes` | **établi** — `(player_api_id, date)` sous condition de non-nullité |
| Grain `Match` | **établi** — `match_api_id` seul |
| Périmètre temporel | **borné** — 2008-07-18 → 2016-05-25, 8 saisons, toutes conservées |
| Faisabilité de l'indicateur temps de jeu | **confirmée** — 94,0 % de couverture, risque n°1 du projet levé |
| Règles métier implicites | **2 documentées** — rythme des relevés en deux régimes ; recopie `home_player_1` → `away_player_11` |
| Tables de staging | **3 construites et testées** |

## 6. Reste à faire

**Prochaine brique — la mesure du réel.** Le temps de jeu, c'est-à-dire le vote de l'entraîneur, n'est pas encore calculé. C'est la table qui fera exister l'écart entre note du jeu et réalité du terrain.

Puis :

- Table `Player` : grain, complétude des dates de naissance, jointure avec `Player_Attributes`
- Table `Team` : cohérence des identifiants entre `Match` et `Team_Attributes`
- Colonnes XML d'événements de `Match` : structure et taux de remplissage
- Quantification des variations aberrantes d'attributs (défaut n°2)
- Vérification du biais par position dans `stg_lineups` (§2)
- Résolution des trois anomalies de volumétrie par championnat (§3)

---

# Session 2 — 20 août 2026 : construction de l'écart

## 7. Tables construites (suite)

### `main.fct_temps_de_jeu` — le vote de l'entraîneur, par club

**Grain : une ligne = un joueur × une saison × un club.** 35 002 lignes.

| Contrôle | Attendu | Obtenu |
|---|---|---|
| Colonnes | 6 | **6** |
| `pct_titularisation` > 100 | 0 | **0** |
| Doublons de grain | 0 | **0** |
| `pct_max` | ≤ 100 | **100,0** |

Dénominateur = `matchs_connus`, nombre de matchs du club dont la composition est renseignée. Jamais le calendrier théorique — application directe de la parade §2.

Comptage en `count(DISTINCT match_api_id)`, jamais `count(*)` : neutralise le défaut n°3 sans nettoyage.

Contrôle de vraisemblance : `max(matchs_connus)` = **38** sur les huit saisons, jamais au-dessus. Conforme à un championnat à 20 clubs.

> **INCIDENT.** Première version livrée avec **5 colonnes au lieu de 6** — `titularisations` absente. **Les trois contrôles de valeurs sont passés malgré tout** : ils vérifiaient le nombre de lignes, les dépassements, le grain et le maximum, aucun ne vérifiait la présence des colonnes.
>
> **Règle installée : après un `CREATE TABLE`, vérifier la liste des colonnes AVANT les valeurs.** Une table peut être cohérente avec elle-même et ne pas contenir ce qu'on croit.

### `main.stg_matchs_par_equipe` — dénominateur

**Grain : une ligne = une équipe × une saison.** 174 à 188 clubs par saison.

> **À instruire** : 2013/2014 tombe à **174 clubs** contre 185-188 les autres saisons. C'est aussi la saison à 3 032 matchs au lieu de 3 220-3 326. Un championnat entier manque probablement. Non résolu.

### `main.fct_temps_de_jeu_joueur` — agrégé par joueur

**Grain : une ligne = un joueur × une saison.** 33 715 lignes.

Motif de la construction : les notes sont au grain `(saison, joueur)`, le temps de jeu au grain `(saison, joueur, club)`. **Joindre directement aurait recopié la note sur chaque ligne de club — le fan-out de Fashion Retail à l'identique.** L'agrégation précède donc la jointure.

Recalcul du pourcentage en **`SUM / SUM`**, jamais en moyenne de pourcentages. Règle d'additivité, deuxième application du dossier.

| `nb_clubs` | Joueurs |
|---|---|
| 1 | 32 430 |
| 2 | 1 283 |
| 3 | **2** |

> **Écart de 2 lignes expliqué.** Attendu 33 717 (35 002 − 1 285), obtenu 33 715. Deux joueurs ont trois clubs dans la même saison et perdent donc deux lignes chacun à l'agrégation : 1 283 × 1 + 2 × 2 = 1 287, et 35 002 − 1 287 = 33 715.
>
> Écart de 0,006 %, négligeable. **Mais un écart inexpliqué est un écart non compris.** Une requête suffisait à le lever.

### DÉFAUT DE CONCEPTION — dénominateur des joueurs transférés

Un joueur transféré en janvier voit ses deux `matchs_connus` **additionnés** : 38 + 38 = 76. Or ses deux clubs jouent en parallèle, pas l'un après l'autre. **Son plafond physique reste 38, donc il ne peut jamais dépasser 50 % dans la métrique.**

La règle `SUM/SUM` est arithmétiquement correcte ; c'est le dénominateur qui ne correspond pas à la réalité.

Impact mesuré : les multi-clubs représentent 3,8 % de la population mais **20 % du classement des « surnotés »** (4 sur 20).

Correction à trancher : `max()` des `matchs_connus` plutôt que `sum()`, ou exclusion des multi-clubs de cette analyse. **Non appliquée à ce jour.**

---

## 8. `main.fct_ecart` — la jointure des deux jugements

**Grain : une ligne = un joueur × une saison.** 28 751 lignes, **0 doublon**.

Jointure interne entre `stg_notes_avant_saison` (51 996) et `fct_temps_de_jeu_joueur` (33 715). Résultat sous le plus petit des deux : **aucun fan-out**.

### Perte à la jointure

**4 964 joueurs-saisons (14,7 %)** ont été titularisés sans note valide dans la fenêtre des 365 jours.

| Saison | Perdus | Temps de jeu moyen |
|---|---|---|
| 2008/2009 | 715 | 38,0 % |
| 2009/2010 | 537 | 34,8 % |
| 2010/2011 | 657 | 33,8 % |
| 2011/2012 | 623 | 33,5 % |
| 2012/2013 | 612 | 33,6 % |
| 2013/2014 | 581 | 33,3 % |
| 2014/2015 | 610 | 33,5 % |
| 2015/2016 | 629 | 31,7 % |

**Contre 48,0 % sur la population retenue.** La perte est stable dans le temps — donc structurelle, sans lien avec l'amélioration de la collecte — et concentrée sur les joueurs à faible temps de jeu. **Non neutre : à publier.**

Méthode : `LEFT JOIN` + `WHERE ... IS NULL`, motif standard pour mesurer ce qu'une jointure interne écarte. Directement transposable à une gap analysis source ↔ modèle cible.

---

## 9. Premier résultat — note du jeu contre temps de jeu

| Tranche | Joueurs | Moyenne | Médiane | Q1 | Q3 |
|---|---|---|---|---|---|
| 80+ | 2 348 | 59,9 % | 63,3 % | 39,5 % | 82,4 % |
| 75-79 | 5 162 | 52,8 % | 55,3 % | 28,1 % | 76,5 % |
| 70-74 | 7 614 | 48,5 % | 47,4 % | 23,3 % | 73,7 % |
| 65-69 | 6 849 | 46,1 % | 44,1 % | 20,0 % | 72,2 % |
| <65 | 6 778 | 41,4 % | 36,7 % | 13,3 % | 66,7 % |

**Lecture sur les moyennes seules** : relation monotone, croissante. 18,5 points d'écart entre le sommet et la base. Faible — un joueur d'élite ne joue qu'une fois et demie plus qu'un joueur médiocre.

**Lecture avec les quartiles — elle contredit la première** :

- Chez les 80+, l'intervalle interquartile couvre **43 points** (39,5 → 82,4). **Un quart des meilleurs joueurs du monde jouent moins de 40 % des matchs de leur club.**
- Le Q3 des joueurs notés sous 65 (**66,7 %**) dépasse la médiane des 80+ (**63,3 %**). **Un quart des plus mal notés jouent plus que la moitié des mieux notés.**
- La tranche `<65` est **bimodale** : moyenne 41,4, médiane 36,7, Q1 à 13,3 et Q3 à 66,7. Deux populations distinctes. **La moyenne ne décrit personne.**

**Titre-message retenu** : « La note du jeu explique à peine le temps de jeu ». Falsifiable, et vérifié.

Démonstration la plus nette du principe *une métrique ne se lit jamais seule* : trois minutes séparaient un tableau qui disait « la note prédit le temps de jeu » de sa réfutation.

---

## 10. LIMITE STRUCTURELLE — ce que l'indicateur mesure réellement

Extraction des joueurs notés 80+ à moins de 20 % de titularisation : Radamel Falcao (2014/2015, 19,7 %), Iker Casillas (2013/2014, 5,3 %), Franck Ribéry (2015/2016, 17,6 %), David Trezeguet, Robinho, Wesley Sneijder, Nemanja Vidić, Ruud van Nistelrooy, Petr Čech…

Vérification manuelle par recoupement externe : **blessures, suspensions, décisions d'entraîneur, fins de cycle.** Pas de la surnotation.

> **L'indicateur capte trois phénomènes que la base ne permet pas de séparer** : la surnotation réelle, l'indisponibilité (blessure, suspension), et la décision de l'entraîneur. Ni les blessures ni les suspensions ne figurent dans cette source.
>
> **Conséquence méthodologique : aucun classement individuel de « joueurs surnotés » n'est publiable.** La correction n'est pas technique — elle consiste à changer d'échelle.
>
> **Règle : quand un facteur non mesuré pollue l'analyse individuelle, monter d'un cran en agrégat.** Les blessures deviennent du bruit qui s'annule, au lieu de contre-exemples qui invalident chaque cas.

---

## 11. Défaut de source n°4 — typage dynamique SQLite

`raw.Player.height` est déclarée `INTEGER` mais contient des décimaux (`182.88`).

**SQLite ne contraint pas les types** : une colonne déclarée `INTEGER` accepte n'importe quoi. DuckDB, strictement typé, refuse la lecture avec `Mismatch Type Error`.

Ce n'est pas un bug de DuckDB — **c'est DuckDB qui révèle une incohérence que SQLite dissimulait.**

Contournement appliqué : `SET GLOBAL sqlite_all_varchar = true`, puis `DETACH` / `ATTACH`. Toutes les colonnes arrivent en `VARCHAR` ; les conversions deviennent explicites, ce qui est plus sûr.

**Point de vigilance majeur pour toute migration vers un moteur strictement typé — Snowflake compris.** Une déclaration de type dans la source ne garantit rien sur son contenu.

---

## 12. `main.stg_notes_fin_saison` et `main.fct_trajectoire`

### La question révisée

Le classement des surnotés étant impubliable (§10), la question devient : **le jeu anticipe-t-il les performances ou y réagit-il ?**

Elle porte sur le comportement du studio, pas sur les joueurs. L'indisponibilité cesse d'être un contre-exemple et devient du bruit agrégé.

### `stg_notes_fin_saison`

**Grain : une ligne = un joueur × une saison.** Dernier relevé compris entre le début et la fin de la saison.

`overall_rating` converti en `INTEGER` — nécessaire depuis l'activation de `sqlite_all_varchar`, sans quoi `variation_pendant` serait une soustraction de chaînes.

### `fct_trajectoire`

`variation_pendant = note_fin − note_avant`.

| Saison | Joueurs | Variation moyenne | Corrélation avec le temps de jeu |
|---|---|---|---|
| 2008/2009 | 3 009 | +1,01 | 0,105 |
| 2009/2010 | 3 420 | +1,81 | 0,071 |
| 2010/2011 | 3 513 | +1,03 | 0,080 |
| 2011/2012 | 3 639 | +1,12 | 0,175 |
| 2012/2013 | 3 679 | +0,95 | 0,183 |
| 2013/2014 | 3 554 | +0,49 | 0,174 |
| 2014/2015 | 3 845 | +0,82 | 0,198 |
| 2015/2016 | 3 931 | +2,08 | 0,193 |

### Résultat 1 — la thèse n'est pas confirmée

**Corrélations de 0,07 à 0,20.** Élevées au carré : le temps de jeu explique **0,5 % à 4 %** de la variation de note en cours de saison.

Le studio ajuste les notes, mais pas en fonction du temps de jeu. **Le temps de jeu s'avère être un mauvais indicateur de performance individuelle** — un joueur peut jouer tous les matchs et être mauvais.

C'est un résultat, pas un échec. Il invalide l'hypothèse de travail initiale.

### Résultat 2 — dérive haussière systématique

La variation moyenne est **positive sur les huit saisons**. Sur une population, les progressions devraient à peu près compenser les régressions.

Trois explications candidates, non départagées :
1. **Biais de sélection** — seuls les joueurs suivis activement par le jeu ont un relevé en cours de saison, donc plutôt ceux qui jouent et progressent ; les joueurs en déclin sortent du radar.
2. **Inflation des notes** — aucune contrainte de somme nulle, et un intérêt commercial à ce que les joueurs progressent.
3. **Artefact de fenêtre temporelle** — partiellement confirmé, voir §13.

---

## 13. PIÈGE DU RÉGIME DE COLLECTE — fenêtre à géométrie variable

2015/2016 sortait du lot sur **trois indicateurs simultanément** : variation moyenne la plus haute (+2,08), médiane à 2,0 alors que les autres sont à 0 ou 1, et rapport montent/descendent de **6,6 pour 1** contre 1,1 à 1,6 ailleurs.

*Trois signaux convergents sur la même ligne ne sont jamais une coïncidence.*

### Ce que le test a révélé

| Saison | Premier relevé | Dernier relevé | **Nb de dates** |
|---|---|---|---|
| 2008/2009 | 2008-08-30 | 2009-02-22 | **2** |
| 2009/2010 | 2009-08-30 | 2010-02-22 | **2** |
| 2010/2011 | 2010-08-30 | 2011-02-22 | **2** |
| 2011/2012 | 2011-08-30 | 2012-02-22 | **2** |
| 2012/2013 | 2012-08-31 | 2013-05-31 | 18 |
| 2013/2014 | 2013-07-19 | 2014-05-16 | 42 |
| 2014/2015 | 2014-07-18 | 2015-05-29 | 50 |
| 2015/2016 | 2015-07-24 | 2016-05-19 | 41 |

**De 2008 à 2012, il n'y a que deux relevés par saison.** La « note de fin de saison » y est en réalité une **note de février**, à trois mois de la fin. À partir de 2012/2013, c'est une vraie note de fin.

**`variation_pendant` couvre donc septembre-février sur la première moitié de la période, et juillet-mai sur la seconde.** Deux fenêtres de durées différentes, comparées comme si elles étaient équivalentes.

> **Ceci était déjà documenté au §1 depuis la veille — règle métier implicite n°1, rythme semestriel puis bimensuel. La règle était écrite ; elle n'a pas été appliquée à la construction de la table.**

### DÉCISION DE PÉRIMÈTRE — spécifique à cet indicateur

**Toute analyse de trajectoire intra-saison est restreinte à 2012/2013 → 2015/2016.**

Critère : régime de collecte homogène, au moins 18 relevés par saison.
Coût : la moitié de la période perdue, environ 15 000 joueurs-saisons retenus.

2008-2012 **reste utilisable** pour tout ce qui ne dépend pas de la trajectoire intra-saison : temps de jeu, note d'avant-saison, écart avec le terrain.

> **Règle installée : une règle de périmètre se déclare par indicateur, pas une fois pour toutes.**

### L'anomalie 2015/2016 persiste

Après restriction au régime homogène :

| Saison | Montent | Stables | Descendent | Rapport | Moyenne | Médiane |
|---|---|---|---|---|---|---|
| 2012/2013 | 1 803 | 732 | 1 144 | 1,6 | +0,95 | 0,0 |
| 2013/2014 | 1 434 | 999 | 1 121 | 1,3 | +0,49 | 0,0 |
| 2014/2015 | 1 697 | 1 093 | 1 055 | 1,6 | +0,82 | 0,0 |
| 2015/2016 | 2 931 | 557 | 443 | **6,6** | **+2,08** | **2,0** |

**Le régime de collecte n'explique pas l'anomalie.** 2015/2016 reste seule. Cause non identifiée — c'est le point ouvert n°1 de la suite.

---

## 14. Synthèse session 2

| Objet | Statut |
|---|---|
| `fct_temps_de_jeu` | construite, 6 colonnes, 35 002 lignes, contrôlée |
| `fct_temps_de_jeu_joueur` | construite, 33 715 lignes, écart de 2 expliqué |
| `fct_ecart` | construite, 28 751 lignes, sans fan-out |
| `stg_notes_fin_saison` | construite |
| `fct_trajectoire` | construite |
| Hypothèse « le jeu réagit au temps de jeu » | **non confirmée** — corrélation 0,07-0,20 |
| Classement individuel des surnotés | **impubliable** — trois causes non séparables |
| Défaut du dénominateur des transférés | **identifié, non corrigé** |
| Anomalie 2015/2016 | **non expliquée** |

## 15. Points ouverts, par priorité

1. **Expliquer l'anomalie 2015/2016** — rapport montent/descendent de 6,6 contre 1,3-1,6, à régime de collecte égal.
2. **Corriger le dénominateur des joueurs transférés** — `max()` au lieu de `sum()`, ou exclusion.
3. **Trouver une meilleure mesure du réel** que le temps de jeu — parsing des événements XML de `Match` pour buts et passes.
4. Instruire la chute à 174 clubs en 2013/2014.
5. Quantifier les variations aberrantes d'attributs (défaut n°2).
6. Vérifier le biais par position dans `stg_lineups`.
7. Résoudre les trois anomalies de volumétrie par championnat (§3).

---

# Session 3 — 21 août 2026 : la thèse démontrée

## 16. Correction du dénominateur des transférés — deux échecs, une exclusion

Le défaut identifié en session 2 : un joueur à 2 clubs a `matchs_connus` = 38 + 38 = 76, alors que ses clubs jouent **en parallèle**. Son plafond physique reste 38.

### Tentative 1 — `sum()`

Arithmétiquement définie, mais **plafonne mécaniquement tout joueur transféré à 50 %**. Les multi-clubs représentaient 3,8 % de la population et 20 % du classement des « surnotés ».

### Tentative 2 — `max()`

`max(matchs_connus)` au lieu de `sum()`. Résultat mesuré :

| Contrôle | Valeur |
|---|---|
| Lignes | 33 715 |
| `pct_titularisation` > 100 | **5** |
| Maximum | **109,1 %** |

**Échec.** Un joueur ayant disputé 20 matchs dans un club et 25 dans l'autre cumule 45 titularisations pour un dénominateur de 38.

### DÉCISION — exclusion

> **Aucun dénominateur correct n'existe pour un joueur transféré.** Les deux clubs jouent en parallèle, et la date du transfert n'est pas dans la source. Il faudrait découper la saison au transfert — information absente.
>
> **Les joueurs ayant évolué dans plus d'un club au cours d'une saison sont exclus de toute analyse de temps de jeu.**
>
> Deux approximations testées, deux échecs mesurés : `sum()` plafonne à 50 %, `max()` produit 5 valeurs au-dessus de 100 %.

```sql
GROUP BY 1, 2
HAVING count(DISTINCT team_api_id) = 1
```

**Coût de l'exclusion, propagé sur toute la chaîne** :

| Table | Avant | Après | Perte |
|---|---|---|---|
| `fct_temps_de_jeu_joueur` | 33 715 | **32 430** | 1 285 |
| `fct_ecart` | 28 751 | **27 535** | 1 216 |
| `fct_trajectoire` | 28 590 | **27 375** | 1 215 |

Contrôle de propagation : `max(nb_clubs)` = **1** sur les trois tables. Une reconstruction manquée aurait laissé un 2 quelque part.

---

## 17. L'anomalie 2015/2016 — quatre hypothèses, trois éliminées

Rappel : rapport montent/descendent de **6,6 pour 1** contre 1,3 à 1,6 les autres saisons, à régime de collecte homogène.

### Hypothèse A — sous-notation initiale, rattrapée en cours de saison. ÉLIMINÉE

| Saison | `note_avant` moy | `note_fin` moy |
|---|---|---|
| 2012/2013 | 69,8 | 70,8 |
| 2013/2014 | 69,9 | 70,4 |
| 2014/2015 | 69,5 | 70,4 |
| 2015/2016 | **69,4** | **71,5** |

Les notes de départ sont stables. C'est la note de fin qui décroche d'un point.

### Hypothèse B — recalibration ponctuelle sur une date. ÉLIMINÉE

Variation moyenne par date de relevé sur 2015/2016 : oscille entre 1,2 et 2,7 sur 38 dates, **sans pic isolé**. Aucune date ne porte la hausse.

### Hypothèse C — fenêtre d'observation plus longue. ÉLIMINÉE

| Saison | Jours moyens début → relevé de fin | Médiane |
|---|---|---|
| 2012/2013 | 266 | 280 |
| 2013/2014 | 233 | 258 |
| 2014/2015 | 219 | 238 |
| 2015/2016 | **224** | **244** |

2015/2016 se situe **entre** 2013/2014 et 2014/2015. Et 2012/2013, la fenêtre la plus longue, n'a qu'un rapport de 1,6. Aucun lien.

### Hypothèse D — glissement global du barème. CONFIRMÉE

Variation moyenne par tranche de note de départ :

| Saison | <65 | 65-74 | 75+ |
|---|---|---|---|
| 2012/2013 | +3,20 | +0,65 | −0,39 |
| 2013/2014 | +2,03 | +0,42 | −0,57 |
| 2014/2015 | +2,35 | +0,68 | −0,33 |
| 2015/2016 | **+3,71** | **+1,97** | **+0,70** |

**L'écart avec 2014/2015 est d'environ +1,3 point sur chacune des trois tranches.** Uniforme. Ce n'est pas une sous-population qui bouge, c'est tout le barème qui glisse.

> **CONCLUSION : une variation de note n'est pas comparable d'une édition du jeu à l'autre.** Toute analyse de trajectoire doit raisonner en **écart au médian de la saison et de la tranche**, jamais en points bruts.

---

## 18. RÉSULTAT — le retour vers la moyenne

Découvert en cherchant l'anomalie 2015/2016, et plus important qu'elle.

Sur les trois saisons non anormales, dans la **même colonne** verticale :

| Tranche de note de départ | Variation moyenne |
|---|---|
| < 65 | **+2,0 à +3,2** |
| 65-74 | +0,4 à +0,7 |
| 75+ | **−0,3 à −0,6** |

**Le jeu fait systématiquement monter les faibles et descendre les forts.** Quatre saisons, même sens, mêmes ordres de grandeur.

### Deux lectures, non départageables avec cette source

1. **Mécanique** — un joueur noté 85 dispose de peu d'amplitude à la hausse, un joueur noté 55 de peu à la baisse. Effet de bornes.
2. **Éditoriale** — le studio resserre volontairement sa distribution pour éviter que les écarts ne s'étendent d'année en année.

### La compression de l'échelle, mesurée

| Seuil | Observations | Part |
|---|---|---|
| Note ≥ 90 | **18** | 0,13 % |
| Note ≥ 85 | **199** | 1,4 % |
| Total | 14 338 | |

Maximum observé : **94**.

> L'échelle est compressée en haut — un ordre de grandeur en dessous d'autres simulations sportives qui atteignent 97-99. Cette compression **contribue mécaniquement** au retour vers la moyenne constaté sur les notes élevées.

### Conséquence méthodologique

Ce retour vers la moyenne est un **signal parasite qui domine celui recherché**. Sans le retirer, tout joueur mal noté paraîtrait « sous-évalué puis corrigé », alors que c'est la mécanique de l'échelle.

### `main.fct_trajectoire_norm` — la normalisation

```sql
variation_pendant - median(variation_pendant) OVER (
    PARTITION BY season, tranche
) AS variation_relative
```

Chaque joueur est comparé à la dérive médiane de **sa saison et de sa tranche de niveau**. Les deux effets parasites — glissement de barème, retour vers la moyenne — sont neutralisés d'un coup.

**Contrôle** : `median(variation_relative)` = **0,00** sur les 12 groupes. C'est la définition de l'opération ; une déviation signalerait une fenêtre mal partitionnée.

**Vérification indirecte** : après normalisation, les moyennes de 2015/2016 rejoignent celles des autres saisons. L'anomalie a disparu sans avoir été traitée pour elle-même.

Périmètre : 2012/2013 → 2015/2016, **14 338 observations**.

---

## 19. `main.dim_poste` — le poste par les coordonnées de terrain

### La bonne source

`raw.Match` contient `home_player_Y1..Y11` et `away_player_Y1..Y11` : la **coordonnée verticale** dans la formation. C'est la vraie donnée de position — bien meilleure que le numéro de colonne, qui ne dit rien de l'organisation tactique.

### Profiling de l'échelle avant tout codage

| Position | Distribution de Y |
|---|---|
| `home_player_Y1` | **1** dans 24 146 cas sur 24 158 (**99,95 %**) · 11 zéros · un 3 |
| `home_player_Y6` | réparti sur 5 (1 793), 6 (7 967), **7 (14 027)**, marges à 3, 8, 9 |
| `home_player_Y11` | **10** (13 567) et **11** (10 577) |

**Échelle : 1 à 11.** Gardien à 1, attaquant de pointe à 10-11. La dispersion en position 6 reflète les différentes formations — confirmation que Y mesure l'avancée sur le terrain.

Anomalies négligeables notées : 11 zéros et deux valeurs isolées.

### `main.stg_positions`

| Contrôle | `stg_lineups` | `stg_positions` | Écart |
|---|---|---|---|
| Lignes | 542 281 | **531 247** | −11 034 (2,0 %) |
| Matchs | 25 221 | **24 158** | −1 063 (4,2 %) |

Les coordonnées ne sont pas toujours renseignées quand le joueur l'est.

### `main.stg_lineups_pos` — la jointure à risque

Aucune clé commune directe : d'un côté `poste` = `home_player_3`, de l'autre `poste_y` = `home_player_Y3`. Rapprochement sur une **clé composite reconstruite** — `match_api_id` + numéro extrait par `regexp_extract(poste, '[0-9]+$')` + côté déduit.

| Contrôle | Attendu | Obtenu |
|---|---|---|
| Lignes | **exactement** 542 281 | **542 281** |
| Doublons `(match_api_id, poste)` | 0 | **0** |
| Avec position | ~531 000 | **527 618** (97,3 %) |

**Pas de fan-out.** Le `LEFT JOIN` préserve la gauche : toute augmentation aurait signalé une clé incomplète. C'était le risque n°1 de l'étape.

### `main.dim_poste`

Poste = **médiane** de Y sur la saison, jamais la moyenne : un joueur qui dépanne une fois en attaque ne change pas de poste.

| Seuil | Groupe |
|---|---|
| y ≤ 1 | Gardien |
| y ≤ 4 | Défenseur |
| y ≤ 8 | Milieu |
| sinon | Attaquant |

**Contrôle de vraisemblance** — une équipe aligne typiquement 1 gardien, 4 défenseurs, 4 milieux, 2 attaquants :

| Groupe | n | Observé | Attendu |
|---|---|---|---|
| Milieu | 12 628 | 38,6 % | 36 % |
| Défenseur | 10 978 | 33,5 % | 36 % |
| Attaquant | 6 336 | 19,4 % | 18 % |
| Gardien | 2 783 | **8,5 %** | 9 % |

Seuils validés sans recalage.

---

## 20. LA THÈSE — anticipation contre réaction

### Construction

`main.fct_variations` ajoute la **variation d'avant-saison** : `note_avant` de N moins `note_avant` de N−1, via `lag()`.

**Piège traité** : `lag()` compare 2012/2013 à 2014/2015 sans le signaler si le joueur a un trou. Les paires non consécutives sont supprimées par comparaison des années de départ.

Population finale : **6 940 observations** avec une variation d'avant-saison exploitable, sur 13 675 lignes.

### Le test central

| Mesure | Corrélation avec le temps de jeu |
|---|---|
| Variation **avant** la saison (anticipation) | **0,078** |
| Variation **pendant** la saison, normalisée (réaction) | **0,281** |

**Rapport de 3,6 pour 1.**

> **Le jeu réagit aux performances, il ne les anticipe pas.**

La note attribuée avant le coup d'envoi n'a quasiment aucun lien avec le temps de jeu qui suivra (0,078). La correction appliquée en cours de saison en a un, faible mais net (0,281).

Le 0,281 est obtenu sur `variation_relative`, donc **après** neutralisation du glissement de barème et du retour vers la moyenne. C'est un signal propre, pas un artefact — c'est précisément à quoi servait la normalisation du §18.

### LE GRADIENT PAR ÂGE — le résultat original

| Tranche d'âge | n | Anticipation | Réaction | Rapport |
|---|---|---|---|---|
| < 23 ans | 1 139 | **0,072** | **0,360** | **5,0** |
| 23-27 ans | 2 927 | 0,101 | 0,303 | 3,0 |
| 28-31 ans | 1 915 | 0,102 | 0,285 | 2,8 |
| 32 ans et + | 959 | **0,118** | **0,229** | **1,9** |

**Les deux colonnes évoluent en sens inverse, de façon monotone sur les quatre tranches.**

L'anticipation est la **plus faible** chez les jeunes (0,072) et croît avec l'âge (0,118). La réaction fait exactement l'inverse : 0,360 chez les moins de 23 ans, 0,229 chez les vétérans.

> **Le jeu réagit aux performances plutôt qu'il ne les anticipe, et ce comportement s'accentue à mesure que le joueur est jeune. Chez les moins de 23 ans, la corrélation entre correction en cours de saison et temps de jeu est cinq fois supérieure à celle de la note d'avant-saison. Chez les plus de 32 ans, le rapport tombe à moins de deux. Le studio prédit d'autant moins bien qu'il a moins d'historique.**

**Note** : l'hypothèse de travail initiale était l'inverse — le jeu anticiperait pour les jeunes, via le potentiel. Les données la réfutent. Le mécanisme retenu est qu'un jeune joueur, sans historique, est structurellement imprévisible : le studio attend et corrige plutôt que de parier.

### Limites à publier avec le résultat

1. Les corrélations restent **faibles en valeur absolue**. 0,360 au carré = 13 % de variance expliquée. Signal réel, pas loi.
2. Le temps de jeu confond toujours performance, blessure, suspension et choix d'entraîneur (§10). Le gradient étant monotone sur quatre tranches, il résiste probablement à ce bruit — **mais cela ne se démontre pas avec cette source**.

---

## 21. `main.fct_percentiles` — les axes du radar

**Règle** : un radar ne trace jamais de valeur brute, toujours le **percentile au sein du poste, sur la saison**.

Implémentation par `percent_rank()` avec une clause `WINDOW` nommée — définie une fois, réutilisée par les six axes. Sans elle, `PARTITION BY` serait répété six fois et une faute de frappe sur l'une passerait inaperçue.

**Ordre des axes, figé et documenté** — technique, physique, défensif :

`dribble` · `passe` · `finition` · `vitesse` · `force` · `interception`

> Un ordre arbitraire produit une forme arbitraire. L'ordre ne change jamais entre deux radars.

### DÉFAUT n°5 — le percentile ment sur une distribution concentrée

Contrôle de la médiane par groupe :

| Groupe | n | Médiane `pct_dribble` |
|---|---|---|
| Attaquant | 5 260 | 47 |
| Défenseur | 9 412 | 49 |
| Milieu | 10 956 | 48 |
| **Gardien** | 2 455 | **19** |

Une médiane de percentile doit tomber à 50 par construction. Cause identifiée :

| `dribbling` | Gardiens |
|---|---|
| **25** | **717** (29 %) |
| 21 | 244 |
| 22 | 195 |
| 13 | 159 |
| 12 | 140 |

**29 % des gardiens partagent exactement la même valeur.** `percent_rank()` attribue à tous le rang de la première occurrence, et la médiane s'effondre.

Le 25 est une **valeur par défaut** : le studio ne renseigne pas le dribble des gardiens, il pose une valeur générique.

> **RÈGLE GÉNÉRALE : un percentile n'a de sens que sur une distribution étalée. Sur une distribution à forte concentration, il ment.** À vérifier avant de publier tout percentile.

### Correction — deux radars distincts

Les six attributs de champ n'ont aucun sens pour un gardien. `main.fct_percentiles_gk` utilise **cinq axes propres** :

`gk_reflexes` · `gk_diving` · `gk_handling` · `gk_positioning` · `gk_kicking`

Cinq et non six : c'est ce que la donnée permet, on ne fabrique pas un sixième axe pour l'esthétique.

**Contrôle** : médiane `pct_reflexes` = **48**. Les gardiens sont retirés de `fct_percentiles` (contrôle : 0 ligne).

---

## 22. Inventaire des tables

| Table | Grain | Lignes |
|---|---|---|
| `stg_lineups` | joueur × match | 542 281 |
| `stg_positions` | position × match | 531 247 |
| `stg_lineups_pos` | joueur × match + coordonnée | 542 281 |
| `stg_saisons` | saison | 8 |
| `stg_notes_avant_saison` | joueur × saison | 51 996 |
| `stg_notes_fin_saison` | joueur × saison | — |
| `stg_matchs_par_equipe` | équipe × saison | — |
| `dim_poste` | joueur × saison | 32 725 |
| `dim_joueur` | joueur | — |
| `fct_temps_de_jeu` | joueur × saison × club | 35 002 |
| `fct_temps_de_jeu_joueur` | joueur × saison | 32 430 |
| `fct_ecart` | joueur × saison | 27 535 |
| `fct_trajectoire` | joueur × saison | 27 375 |
| `fct_trajectoire_norm` | joueur × saison | 14 338 |
| `fct_variations` | joueur × saison | 13 675 |
| `fct_percentiles` | joueur × saison, hors gardiens | 25 628 |
| `fct_percentiles_gk` | gardien × saison | 2 455 |

---

## 23. LIMITES À PUBLIER — version consolidée

À écrire **sur la page**, pas en annexe.

1. Les attributs proviennent de la série **FIFA d'EA Sports**, pas de PES. Aucune source ouverte n'existe pour PES. L'esthétique est un hommage à une ergonomie, pas une analyse de PES.
2. Le temps de jeu confond **surnotation, blessure, suspension et choix d'entraîneur**. La source ne contient ni blessures ni suspensions. **Aucun classement individuel de « surnotés » n'est publiable.**
3. Les joueurs **multi-clubs sont exclus** — aucun dénominateur correct n'existe pour eux. 3,8 % de la population.
4. **14,7 % des joueurs-saisons** sont écartés faute de note valide dans la fenêtre de 365 jours. Ils jouent 32-38 % contre 48 % pour les retenus.
5. Rétention de la note d'avant-saison : **41 % en 2008/2009 à 66 % en 2014/2015**. Les saisons ne sont pas équivalentes en couverture.
6. L'analyse de trajectoire est restreinte à **2012/2013-2015/2016** — régime de collecte homogène.
7. Les variations de note **ne sont pas comparables entre éditions du jeu**. Tout raisonnement se fait en écart au médian de la saison et de la tranche.
8. Les corrélations sont **faibles en valeur absolue** — la plus forte, 0,360, explique 13 % de la variance.
9. Le temps de jeu n'est pas corrigé de la profondeur d'effectif. Un remplaçant du Barça n'est pas un remplaçant de Wigan.
10. Les **radars gardiens et joueurs de champ ne sont pas comparables** : axes différents, cinq contre six.

---

## 24. Reste à faire

1. **Export JSON** pour la page — `COPY ... TO ... (FORMAT JSON)`.
2. **La page**, trois écrans : le onze du jeu contre le onze du terrain · anticipation ou réaction, avec le trait vertical au coup d'envoi · les cas, avec correction d'âge.
3. **Passage en dbt** — chaque `CREATE OR REPLACE TABLE` devient un `models/*.sql` contenant le seul `SELECT`, avec `{{ ref() }}` pour les dépendances. Tests `unique` sur chaque clé de grain, et un test singulier interdisant toute `date_releve` postérieure à `debut_saison` — **c'est celui qui empêche la fuite temporelle de revenir**.
4. Points ouverts non traités : chute à 174 clubs en 2013/2014 · anomalies de volumétrie Italie, Portugal, Suisse · quantification des variations aberrantes d'attributs · biais par position dans `stg_lineups`.
