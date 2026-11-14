---
type: analysis
date: 2026-11-14
author: axe 2
question: Peut-on projeter l'effectif libéral à la commune avec une bande à 80 % calibrée dans chaque classe de taille (protocole N4) ?
headline: "Pas encore. K (cohortes hiérarchiques commune ⊂ EPCI ⊂ dép ⊂ région) : bande trop large (couverture à 80 % de 90–100 % chez les IDE) et point moins bon que la part tenue sous 10 personnes ; repli K2 (part tenue × total de K, bande empirique par classe) : calibré pour les IDE de 1 à 50 professionnels (81–83 %), trop étroit au-dessus et pour les dentistes (68–73 %). Les deux sont rejetés selon leur critère pré-écrit"
status: fait (deux variantes inscrites avant passage, deux rejets)
professions: [infirmiers, kines, dentistes]
hypothesis: chantier « projection communale fiable »
sources: [CartoSanté *_popage (data/processed/stock_commune.parquet, protocole N4), v2/data/processed/commune_geo.parquet (axe 4, COG 2026)]
tags: [axe2, commune, N4, calibration, cohortes, hiérarchique]
---

# Projection communale calibrée : deux essais, deux rejets, une piste nette

> **Headline :** aucun des deux modèles ne passe le critère de calibration
> de N4 pour les trois professions.
> - **K**, les cohortes communales hiérarchiques, est **trop prudent** : sa
>   bande couvre de 90 à 100 % des cas pour une cible de 80 %.
> - **K2**, la part tenue × le total de K avec une bande empirique par
>   classe, est **calibré pour les infirmiers de 1 à 50 professionnels**
>   (81 à 83 %).
>   - Il est trop étroit pour les grandes communes (62 à 72 %).
>   - Il est trop étroit pour les dentistes (68 à 73 %), et irrégulier
>     pour les kinés.

**Ce que ça dit.** À la commune, la difficulté n'est pas le bruit des
petites communes : K2 le calibre bien. Elle vient de l'**erreur commune à
tout le département**. Elle est corrélée entre communes, et c'est elle qui
domine dans les grandes communes.

## Question
Chantier « projection communale fiable » (décision du 2026-11-14) :
- étendre le modèle de cohortes à commune ⊂ EPCI ⊂ département ⊂ région ;
- juger le modèle sur N4, avec pour critère une bande à 80 % qui couvre
  [75 ; 85] % des cas dans chaque classe de taille.

## Résultat

### K, inscrit avant le banc
Cohortes communales :
- rétention rétrécie nat → région → dép → EPCI → commune ;
- entrées en niveau local départemental × part communale hiérarchique ;
- variance α·μ + β·μ², mesurée sur des pseudo-prévisions dans la fenêtre.

[Dérivation](../derivations/2026-11-14-axe2-communes.md).

**Couverture de la bande à 80 %, toutes origines (2014–2020, h = 5) :**

| Classe | IDE | MK | CD |
|---|---|---|---|
| 1–2 | 90 % | 91 % | 95 % |
| 3–5 | 90 % | 88 % | 95 % |
| 6–10 | 91 % | **84 %** | 94 % |
| 11–20 | 93 % | **79 %** | 92 % |
| 21–50 | 96 % | **79 %** | 86 % |
| 51–100 | 98 % | **76 %** | **82 %** |
| 101–200 | 100 % | 71 % | 88 % |
| > 200 | 99 % | **75 %** | 71 % |

- Les valeurs en gras sont dans [75 ; 85] %.
- **Verdict : rejeté.** Les IDE échouent dans 8 classes sur 8 et les CD
  dans 7 sur 8.
- La variance mesurée en moments est dominée par quelques communes
  extrêmes. Elle atteint β = 1 chez les CD en 2018 et 2020, soit un
  écart-type égal à la moyenne.
- En 2014, aucune pseudo-origine n'existe pour les MK et les CD.

**P80 de |erreur| (%) contre la part tenue :**

| | 1–2 | 3–5 | 6–10 | 11–20 | 21–50 | 51–100 | 101–200 | > 200 |
|---|---|---|---|---|---|---|---|---|
| IDE, K | 83,9 | 66,8 | 49,0 | 38,9 | 30,5 | 26,6 | 19,2 | 20,1 |
| IDE, part tenue × total de K | 42,7 | 56,8 | 41,9 | 34,2 | 26,0 | 24,1 | 23,4 | 21,0 |
| IDE, part tenue × total réel (oracle N4) | 42,0 | 42,0 | 31,9 | 24,9 | 19,6 | 16,2 | 12,5 | 9,2 |
| CD, K | 70,7 | 63,9 | 46,5 | 37,9 | 28,3 | 19,0 | 13,3 | 11,7 |
| CD, part tenue × total de K | 47,3 | 54,2 | 40,0 | 33,3 | 27,2 | 17,3 | 13,2 | 13,1 |

- **Sous 10 personnes, la mécanique de cohortes à la commune ajoute du
  bruit.** L'âge et la part des entrées y sont estimés sur 1 à 10
  personnes.
- **Au-dessus de 100 personnes, elle aide légèrement** (IDE : 19,2 contre
  23,4).
- **L'écart à l'oracle est la part qui vient du total départemental.**
  - Biais signé moyen : +22 % chez les IDE pour K, +24 % pour la part
    tenue × total de K.
  - Le niveau local des entrées des IDE dans CartoSanté surestime : les
    entrées ralentissent après 2018.

### K2, inscrit après l'échec de K, avant son passage
Point : part tenue × total de K. Bande : quantiles empiriques de l'erreur
relative par classe, sur des pseudo-prévisions dans la fenêtre.

| Classe | IDE | MK | CD |
|---|---|---|---|
| 1–2 | **81,8 %** | **77,8 %** | 70,8 % |
| 3–5 | **81,5 %** | **76,3 %** | 73,4 % |
| 6–10 | **81,1 %** | 74,8 % | 72,9 % |
| 11–20 | **81,7 %** | **77,0 %** | 67,5 % |
| 21–50 | **83,4 %** | 71,9 % | 68,5 % |
| 51–100 | 71,8 % | 70,0 % | 72,4 % |
| 101–200 | 67,7 % | 47,2 % | **76,2 %** |
| > 200 | 62,0 % | 39,6 % | 38,1 % |

- **Verdict : rejeté.** Plus de 2 classes sur 7 échouent pour chaque
  profession.
- En 2014, MK et CD n'ont pas de bande : il n'y a pas de pseudo-origine.
- **Mais K2 calibre les IDE de 1 à 50 professionnels**, soit 43 370
  communes × origines.
- La bande se resserre avec la taille, plus vite que l'erreur réelle. Une
  grande commune porte presque toute l'erreur du total départemental,
  qu'aucune commune voisine ne compense. Or les quantiles par classe sont
  estimés sur 3 pseudo-origines, avec peu de grandes communes.

### Temps de calcul
- K s'ajuste en 0,6 s pour 11 525 communes (kinés). Sa projection sur
  40 ans prend 0,06 s.
- Il est compatible avec le budget de l'axe 0 : 1,02 s par scénario à la
  commune (C15).

## K3, inscrit avant passage et soumis au jugement N10 de l'axe 3
- **Modèle.** Point de K2. Bande = erreur du total départemental (un tirage
  par département, commun à ses communes) + erreur locale par classe de
  taille, sur 200 tirages. Les grains BV et EPCI s'obtiennent en sommant
  les tirages ([dérivation, § K3](../derivations/2026-11-14-axe2-communes.md)).
- **Soumission.** `v2/methodes/out/n10_soumission_k3.parquet` (profession,
  grain, unit, origin, h, pred, q10, q90).
  - Origines 2014–2020 pour les IDE, 2015–2020 pour les MK, 2016–2020 pour
    les CD. Avant, il n'y a pas de pseudo-prévision possible.
- **Contrôle rapide fait ici, non décisif.**
  - Il porte sur la couverture de la bande à 80 %.
  - Il ne retire pas les sauts communaux, contrairement à N10.
  - Il n'a servi à aucun réglage.

| Classe | IDE commune | IDE EPCI | MK commune | MK EPCI | CD commune | CD EPCI |
|---|---|---|---|---|---|---|
| 1–2 | 81,5 % | 61,1 % | 76,1 % | 73,0 % | 69,0 % | 61,6 % |
| 3–5 | 83,1 % | 82,3 % | 76,8 % | 77,7 % | 77,2 % | 75,3 % |
| 6–10 | 83,6 % | 84,1 % | 75,7 % | 77,0 % | 75,1 % | 75,5 % |
| 11–20 | 84,0 % | 87,4 % | 76,2 % | 78,3 % | 71,3 % | 78,8 % |
| 21–50 | 85,4 % | 87,4 % | 71,8 % | 77,2 % | 70,6 % | 83,7 % |
| 51–100 | 72,1 % | 83,9 % | 75,7 % | 80,2 % | 66,1 % | 72,9 % |
| 101–200 | 86,1 % | 82,3 % | 62,4 % | 76,4 % | 75,2 % | 73,2 % |
| > 200 | 79,1 % | 69,9 % | 57,1 % | 77,9 % | 85,4 % | 83,5 % |

**Lecture provisoire.**
- **Les grandes classes progressent nettement par rapport à K2**, comme
  prévu. IDE à la commune : de 67,7 à 86,1 % pour 101–200, de 62,0 à 79,1 %
  pour > 200.
- **Les kinés à l'EPCI sont presque calibrés** : 76 à 80 % dans 7 classes
  sur 8.
- **Plusieurs classes restent hors bande.** Pour les CD, les classes
  communales de 11 à 100 sont à 66–71 %. Pour les MK à la commune, les
  classes de plus de 100 sont à 57–62 %.
- Le verdict appartient à N10 (axe 3).

## K4 : inscrit avant passage, jugement et confirmation confiés à l'axe 3
- **N10 a jugé K3** (axe 3) : aucun grain ne passe.
  - Les IDE sont trop larges dans les classes moyennes (85–91 %).
  - Les CD sont trop étroits (69–73 %).
  - Les kinés à l'EPCI sont les plus proches : une seule classe hors bande
    (1–2 : 73,0 %).
- **K4 = K3 avec deux changements de mécanisme**, sans facteur réglé sur
  ce jugement :
  - les erreurs viennent des 2 pseudo-origines les plus récentes ;
  - l'erreur départementale et l'erreur locale sont tirées dans la même
    pseudo-origine.
  - Voir la [dérivation, § K4](../derivations/2026-11-14-axe2-communes.md).
- **Fichiers.**
  - `v2/methodes/out/n10_soumission_k4.parquet` : 2014–2020, h = 5.
  - `v2/methodes/out/n10_confirmation_k4_2021h4.parquet` : origine 2021,
    h = 4, réservée.
  - Code : `v2/methodes/communes_k4.py`, environ 1 min machine. Les
    parquets ne sont pas versionnés : ils se régénèrent.
- **L'axe 2 n'a regardé aucune des deux couvertures de K4.** Un passage sur
  2014–2020 ne vaudra que s'il est confirmé sur 2021, ou par le dépôt
  2027.

### Verdict de K4 (axe 3, N11, commit 1d9545c) : non confirmé
- **N10 (2014–2020, h = 5).** Échec à tous les grains, sans progrès sur
  K3. Couverture globale, commune / BV / EPCI :

| | Commune | BV | EPCI |
|---|---|---|---|
| CD | 72,5 % | 73,6 % | 73,5 % |
| IDE | 83,0 % | 85,1 % | 84,4 % |
| MK | 76,3 % | 76,8 % | 76,0 % |

  - Pour les kinés à l'EPCI, 3 classes sortent de la bande, contre une
    seule pour K3.
- **Confirmation 2021, h = 4.** Échec partout.
  - Les CD restent trop étroits dans les grandes classes : 51 % à l'EPCI
    pour 101–200.
  - Les IDE restent trop larges : 86 à 100 %.
  - Sur cette période, la tendance naïve calibre 8 classes sur 8 pour les
    kinés au BV, alors qu'elle échoue N10. 2021 est une période facile
    pour les kinés.
- **Prédictions de K4.** Fausses toutes les trois : les IDE ne descendent
  pas sous 85 %, et les CD ne montent pas au-dessus de 75 %.
- **Lecture (dérivé).**
  - Les deux changements (récence, tirage conjoint) déplacent peu la
    largeur.
  - L'écart vient d'un **niveau d'erreur propre à chaque profession**,
    qui ne se reproduit pas d'une période à l'autre. Les erreurs passées
    des pseudo-origines ne prédisent pas l'erreur future à la bonne
    échelle.
  - C'est l'hypothèse « l'erreur passée prédit l'erreur future » qui
    échoue, pas la structure départementale + locale.

## Ce que ça change (dérivé)
1. **La bande d'une commune a deux parties.**
   - Une partie **locale** : de type Poisson, indépendante entre communes.
     K2 la calibre.
   - Une partie **départementale** : erreur du total, commune à toutes les
     communes du département, proportionnelle à la taille.
   - Il faut les **séparer** : bande = locale ⊕ (part × incertitude du
     total départemental).
2. **Le total départemental doit venir de C1**, et non de K sur
   CartoSanté.
   - C1 a une bande départementale calibrée à 77,6 % sur le RPPS privé.
     K sur CartoSanté porte un biais de +22 % chez les IDE.
   - Il faut un passage RPPS privé → CartoSanté libéral (axe 4).
3. **La mécanique de cohortes à la commune n'aide qu'au-dessus de ~100
   personnes.** En dessous, on garde la part tenue, avec l'âge seulement
   à l'EPCI.

## Règle d'affichage, en attendant (décision « chantier communal »)
| Profession | Projection communale | Raison |
|---|---|---|
| IDE | communes de 1 à 50 professionnels avec la bande K2 ; au-dessus, l'EPCI ou le département | K2 calibré dans 5 classes |
| MK, CD | **pas de projection communale calibrée** : observé à la commune + projection du département | ni K ni K2 ne passent |

## How
- **Code.**
  - [`v2/methodes/communes.py`](../../../methodes/communes.py) : `K`,
    `variance`, `quantiles`, `k2_point`, `k2_band`, `k2_interval`.
  - [`banc_communes.py`](../../../methodes/banc_communes.py) et
    [`banc_communes_k2.py`](../../../methodes/banc_communes_k2.py) : environ
    25 s machine chacun.
  - Sorties : `v2/methodes/out/com_*`.
- **Protocole.** N4 (SHA-256 `91f897cc5071`), fonctions
  `validation.fine_scale` inchangées, même exclusion des sauts.
- **Inscriptions** : `decisions.md`, entrées « modèle K inscrit » et « K
  rejeté ; repli K2 inscrit ».
- **Branchement sur le jumeau.** **Non fait.** Brancher un modèle rejeté
  n'aurait pas de sens. L'axe 0 garde sa répartition communale (C15).

## ⚑ What could make it wrong
- **CartoSanté est un périmètre libéral au 31/12**, pas le privé RPPS.
  L'écart entre les deux est connu (axe 4 : −5,4 % pour les kinés en 2025).
- **Peu de pseudo-origines.** 3 au mieux, et aucune en 2014 pour MK et CD.
  Les quantiles des grandes classes reposent sur peu de communes.
- **La part des IDE de 1 à 50 qui passe** est mesurée sur les 4
  origines. Sur l'origine 2020 seule, la couverture vaut de 75,3 à 84,6 %
  dans ces classes, donc encore dans la bande, mais la classe 21–50 est à
  la limite (75,3 %).

## ? Next
| Item | Cost |
|---|---|
| K3 : bande = locale (K2) ⊕ part × tirages du total départemental de C1, avec un passage RPPS privé → CartoSanté libéral ; à inscrire avant | ~2 h Claude |
| Passage RPPS privé ↔ CartoSanté libéral par département et par année (axe 4) | ~1 h axe 4 |
| Même banc à l'EPCI et au bassin de vie (N4 le prévoit) | ~30 min |
| Historiques communaux PH et SF (axe 4), puis même banc | dépend de l'axe 4 |
