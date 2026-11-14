---
title: Réconciliation de l'effectif des chirurgiens-dentistes
date: 2026-11-14
headline: "Socle 2026 dentistes privé = 47 347 (≤ 48 690 tous modes, RPPS 2026) ; 76 397 est la projection 2050, pas le socle"
tags: [axe4, jumeau, verification]
---

# Réconciliation dentistes : 76 000 contre 62 000

## Constat
L'écart signalé ne vient pas d'un double comptage. Le chiffre de 76 000 est la valeur **2050** de la
projection de référence. Le socle 2026 du jumeau vaut **47 347** dentistes dans le secteur privé.
Ce socle est inférieur au total tous modes de la source, **48 690**. Aucun correctif de code n'est nécessaire.

## Preuves

| Grandeur | Valeur | Statut |
|---|---|---|
| Total dentistes tous modes 2026, `secteur_stock.parquet` (DREES RPPS 2012–2026) | 48 690 | mesuré |
| dont dép. 999 (exclu) | 2 | mesuré |
| Répartition par mode 2026 : libéral 36 259 · mixte 3 824 · autre salarié 8 060 · salarié hospitalier 547 | somme 48 690 | mesuré |
| Effectif privé 2026 (Σ n × p_central, hors 999/20), `history.sector_table` | 47 347,5 | dérivé |
| API `/api/scenario?prof=dentistes&terr=FR` : `base[2026]` / `obs[2026]` | 47 347,5 | mesuré |
| API : `base[2050]` | 76 397 | mesuré (projection) |

Contrôles de double comptage sur l'année 2026 (dentistes, 13 909 lignes) :
- aucune ligne « Ensemble » en âge ou en sexe (le filtre de `sector_table` est donc sans effet ici) ;
- 0 clé dupliquée sur (dép., mode, secteur, âge, sexe) ;
- DROM présents une seule fois (971 à 976) ; dép. 999 exclu.
- La série est régulière : 40 488 (2012) puis 48 690 (2026), sans saut de niveau.

## Le chiffre de 62 000
Aucune publication DREES consultée dans le dépôt ne donne 62 000 dentistes. Le fichier RPPS DREES
vendorisé (`data/raw/drees/chirurgiens_dentistes_rpps_2012_2026.xlsx`) totalise 48 690 au 1er janvier 2026.
La source de ce chiffre reste à identifier (**supposé** : confusion avec une autre profession ou avec une
valeur projetée). Le fichier brut n'a pas été relu directement (openpyxl absent de l'environnement).
Le contrôle repose sur le parquet dérivé.

## Autres professions (socle 2026 de l'API = effectif privé de la source)

| Profession | Privé 2026 (API) | Tous modes source | 2050 (API) |
|---|---|---|---|
| Sages-femmes | 12 817 | 26 428 | 18 991 |
| Pharmaciens | 63 612 | 75 335 | 72 309 |
| Kinés (RPPS) | 101 946 | 111 141 | 160 783 |
| Infirmiers (dernier observé 2023) | 277 788 | 607 644 (privé + public, axe 4) | 336 422 |

Tous les chiffres sont mesurés. Le socle privé de chaque profession est inférieur à son total. Aucune n'est
touchée par un double comptage.

## Correctif
Aucun dans le code. Côté interface, il faut vérifier que la valeur affichée sous le libellé « 2026 » est bien
`base[0]` et non `base[-1]`, si c'est l'affichage qui a produit la lecture « 76 000 en 2026 » (non vérifié).

## Confiance
Élevée sur l'absence de double comptage. Le parquet, `sector_table` et l'API donnent le même chiffre.
La confiance est moyenne sur l'origine du chiffre de 62 000, faute de source citée.
