# Le jeu anticipait-il, ou reagissait-il ?

Analyse des notes d'un jeu video de football compare au temps de jeu reel,
sur 8 saisons de championnats europeens (2008-2016).

## La question

Le jeu attribue une note a chaque joueur avant la saison. La saison a lieu.
Le jeu corrige la note en cours de route.
Laquelle des deux colle le mieux a ce qui s'est passe sur le terrain ?

## Le resultat

**Le jeu reagit, il n'anticipe pas. Et il reagit d'autant plus fort que le
joueur est jeune.**

| Age | Anticipation | Reaction | Rapport |
|---|---|---|---|
| moins de 23 ans | 0,072 | 0,360 | 5,0 |
| 23 a 27 ans | 0,101 | 0,303 | 3,0 |
| 28 a 31 ans | 0,102 | 0,285 | 2,8 |
| 32 ans et plus | 0,118 | 0,229 | 1,9 |

Monotone sur les quatre tranches, dans les deux colonnes, sur 6 940 observations.
Sans historique, le studio ne parie pas : il attend et corrige.

L'hypothese de depart etait l'inverse. Les donnees l'ont refutee.

## Les pages

- `ecran1-onze.html` — le onze du jeu contre le onze du terrain
- `ecran2-gradient.html` — le resultat
- `ecran3-cas.html` — les desaccords extremes

Trois generations d'interface commutables (2006, 2010, 2015), avec la formation
reellement dominante de chaque epoque : 4-4-2 a 58,9 % en 2008/2009,
4-5-1 a 41,0 % en 2015/2016.

## Les limites, publiees a cote des chiffres

1. Attributs issus de la serie FIFA d'EA Sports. Aucune source ouverte n'existe
   pour PES ; l'esthetique est un hommage a une ergonomie.
2. Le temps de jeu confond performance, blessure, suspension et choix
   d'entraineur. La source n'en contient aucun. **Aucun classement individuel de
   joueurs surnotes n'est publiable.**
3. 14,7 % des joueurs-saisons ecartes faute de note valide dans la fenetre de
   365 jours. Joueurs multi-clubs exclus : aucun denominateur correct n'existe.
4. Analyse de trajectoire restreinte a 2012/2013-2015/2016, regime de collecte
   homogene. Les variations de note ne sont pas comparables entre editions.
5. Correlations faibles en valeur absolue : la plus forte explique 13 % de la
   variance.

## La methode

`docs/profiling.md` — 24 sections. 5 defauts de source documentes avec leur
mecanisme, 2 regles metier implicites decouvertes, 4 decisions de perimetre
motivees et chiffrees, 3 erreurs de conception corrigees avec la trace de ce
qui a echoue.

C'est le livrable principal de ce projet.

## Stack

DuckDB (extension SQLite, lecture seule sur la source) · SQL · HTML, CSS et SVG
ecrits a la main, sans dependance.

## Source

Kaggle `hugomathien/soccer` — European Soccer Database. SQLite, 313 Mo,
extraction du 19 septembre 2019. 25 979 matchs, 11 060 joueurs, 11 championnats.
La base n'est pas versionnee dans ce depot.
