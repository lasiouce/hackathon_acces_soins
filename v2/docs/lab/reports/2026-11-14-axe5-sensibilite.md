---
type: analysis
date: 2026-11-14
author: Claude (session axe 5)
question: "Quels hyperparamètres déplacent vraiment l'effectif « libéral » (privé) en 2030, 2040 et 2050, de combien, et avec quelle fourchette ?"
headline: "Partie 2 : en 2050, la décision pèse plus que l'ignorance pour les IDE (0,88 contre 0,12) et les kinés (0,71 contre 0,15), pas pour SF ni CD (0,41 contre 0,57–0,59) ; au département, le modèle n'est assez sûr pour décider que pour 57 dép. IDE et 26 MK. Partie 1 : à 2050, la variance de N privé vient de 3 sources : part privée des salariés ambigus (ST 0,91 SF, 0,48 PH), lien formation → entrées (filière CD 0,55, PH 0,32 ; quotas 0,2–0,6 en levier) et fenêtre d'ajustement (MK 0,53, IDE 0,53). Le cumul emploi-retraite ne bouge rien (μ* ≤ 0,25 %). Fourchette 2050 : propagation −17 à +34 %, backtest extrapolé ±9 à ±66 %"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "Une poignée de paramètres porte l'essentiel de la variance de N(2050) ; la plupart des fiches de l'axe 1 ne la déplacent pas"
sources: [jumeau v2 (axe 0, code du 2026-11-14 03:36), axe 4 secteur_stock (DREES RPPS × secteur, FINESS), v1 stock (SNDS infirmiers libéraux), fiches axe 1, banc N1 (axe 3)]
tags: [axe5, sensibilite, morris, sobol, incertitude, 2050]
---

# Axe 5 — sensibilité et fourchettes à 2050

> **Headline.**
> - **À 2050, trois sources portent la variance de N « libéral »** :
>   - la part privée des salariés ambigus : ST 0,91 pour les SF, 0,48 pour
>     les PH ;
>   - le lien entre formation et entrées : filière ST 0,55 pour les CD et
>     0,32 pour les PH ; en levier, les quotas pèsent ST 0,19 à 0,61 ;
>   - la fenêtre d'ajustement : ST 0,53 pour les MK et les IDE.
> - **Le cumul emploi-retraite ne déplace rien** : μ* ≤ 0,25 % de N à 2050,
>   pour la part comme pour le multiplicateur.
> - **Fourchette à 2050**, en deux composantes séparées :
>   - (a) propagation des incertitudes : de −17 % à +34 % autour du
>     tendanciel selon la profession ;
>   - (b) erreur de backtest extrapolée : de ±9 % (PH) à ±66 % (SF).
> - **Aucun backtest n'existe à 2050** : le plus long horizon observé est
>   de 10 ans, et de 5 ans pour les MK et les IDE.

Toutes les valeurs sont **mesurées** sur le jumeau, sauf mention contraire.
Les plages des facteurs, elles, sont **supposées** ou **sourcées**, comme
l'indique le tableau 1.

## Question
Mettre un prix sur l'axe 1 : inutile de sourcer finement un paramètre qui ne
bouge pas la sortie. Donner aussi les fourchettes à 2050, faute de backtest
à cet horizon ([ROADMAP](../../../ROADMAP.md), axe 5 ; [décision axe 5](../decisions.md)).

## Ce qui a été fait

### Sortie, échelle et facteurs
- **Y** = N privé, total national, par profession, en 2030, 2040 et 2050.
  - Le jumeau tourne au département, sur le secteur privé seul. Sans
    régulation ni transition, aucun flux ne relie le privé et le public.
  - Origine 2026, sauf IDE : 2023.
- **Périmètre infirmier.** `secteur_stock` n'a ni âge ni sexe pour les IDE.
  On prend donc les **libéraux** v1 (SNDS), soit 98 854 en 2023 contre
  277 788 dans tout le privé. Les chiffres IDE couvrent environ 36 % du
  privé.

**Tableau 1 — facteurs.** Familles : E = choix d'estimation, D = données,
P = paramètre, L = levier. Chaque plage indique son statut.

| Facteur | Famille | Plage | Statut de la plage |
|---|---|---|---|
| `fenetre` | E | {2, 3, 5, 8} ans | choix ; observatoire A5 |
| `shrink` | E | {20, 200, 2000, national} | choix ; N1 défaut 200 |
| `entrees` | E | {plates, récentes 2 ans} | choix ; « tendance » exclue (voir plus bas) |
| `filiere` | E | {non, oui} (CD, PH) | choix ; inscrits DREES 2020–2025 |
| `part_privee` | D | {min, centrale, max} (sauf IDE) | mesuré, bornes axe 4 |
| `vieillissement.fraction` | P | [0,18 ; 0,22] | supposé (±10 % autour d'âges uniformes) |
| `sorties.part_cumul` | P | fiche × [0,5 ; 2] : SF 0,8 %, CD 4,7 %, PH 1,8 %, MK et IDE 1,5 % | sourcé (COR 2016, données 2015) × supposé |
| `sorties.decalage_retraite` | L | [0, 2] ans | levier |
| `sorties.cumul_multiplicateur` | L | [1, 2] | levier |
| quotas (`entrees.multiplicateur`, après L_p) | L | [0,8 ; 1,2] | levier ; DD76 ±20 %, L_p v1 supposé |

- **Deux familles d'analyse :**
  - « tout » (leviers compris) classe ce qui déplace Y ;
  - « incertitude » (leviers au tendanciel) donne la fourchette (a).
- **Méthodes :**
  - Morris : r = 30 trajectoires, p = 4 niveaux, pas Δ = 2/3 de la plage.
  - Sobol : N = 2048, S1 par Saltelli 2010 sur Y centré, ST par Jansen.
  - Intervalles bootstrap à 95 % sur 500 tirages, graine 20261114.
  - 201 276 runs du jumeau en 1 187 s sur une machine chargée (2,7 à
    4,2 ms par run au repos, une fois les ajustements en cache ; mesuré).
  - **Instantané figé du jumeau** : empreinte `c2dc760126b34239` (`.py`
    triés), critères C1–C14 au vert. Le premier passage, sur le code de
    03:45, donne des ST identiques (écart max 0,000).
- Code : [`v2/sensibilite/`](../../../sensibilite/). Commandes dans
  « Reproduire ».

### Facteurs sans prise dans le jumeau (effet nul par construction, pas mesuré)
- `formation.abandon` et `formation.capacite` : le vivier n'alimente pas N
  (open.md, axe 2).
- La régulation : les zones sont communales, donc non activables au
  département ; le module n'est par ailleurs pas conservatif selon la
  seconde revue.
- Une vingtaine de fiches de l'axe 1 n'ont pas de point d'entrée :
  - régulation SF, CD, MK, IDE et θ ;
  - rendement et abandon IFSI ;
  - filières et internat PH, évaporation PH ;
  - DES dentaires, âge d'entrée, obligation MK, mortalité, cessation par
    âge.

  Leur sensibilité est **indécidable** tant que l'axe 2 ne les branche pas.
  Ce n'est pas un zéro.

## Résultats

### 1. Classement (indice total ST, IC 95 % bootstrap)
Seuls les facteurs dont ST ≥ 0,05 au moins une fois sont listés. Tous les
tableaux complets, y compris S1 et Morris, sont dans
[`out/resume.md`](../../../sensibilite/out/resume.md) et
[`out/classement.csv`](../../../sensibilite/out/classement.csv).

**Famille « incertitude » (leviers au tendanciel).**

| Profession | Facteur | 2030 | 2040 | 2050 |
|---|---|---|---|---|
| sages-femmes | part_privee | 1,01 [0,97–1,05] | 0,95 [0,91–1,00] | 0,91 [0,87–0,95] |
| dentistes | part_privee | 0,89 [0,84–0,93] | 0,40 [0,37–0,42] | 0,26 [0,24–0,27] |
| dentistes | filiere | 0,03 [0,02–0,03] | 0,41 [0,38–0,43] | 0,55 [0,52–0,58] |
| dentistes | fenetre | 0,06 | 0,14 | 0,13 [0,12–0,15] |
| dentistes | entrees | 0,03 | 0,09 | 0,10 [0,09–0,11] |
| pharmaciens | part_privee | 0,93 [0,90–0,98] | 0,63 [0,59–0,66] | 0,48 [0,45–0,50] |
| pharmaciens | filiere | 0,00 | 0,19 | 0,32 [0,30–0,34] |
| pharmaciens | fenetre | 0,04 | 0,14 | 0,15 [0,13–0,16] |
| kines | fenetre | 0,23 [0,21–0,24] | 0,52 [0,49–0,56] | 0,53 [0,49–0,57] |
| kines | part_privee | 0,69 [0,65–0,73] | 0,29 | 0,18 [0,17–0,19] |
| kines | entrees | 0,05 | 0,14 | 0,17 [0,15–0,19] |
| kines | shrink | 0,06 | 0,14 | 0,17 [0,16–0,18] |
| kines | fraction | 0,00 | 0,04 | 0,12 [0,11–0,12] |
| infirmiers | fenetre | 0,65 [0,60–0,70] | 0,58 | 0,53 [0,49–0,57] |
| infirmiers | entrees | 0,52 [0,48–0,57] | 0,51 | 0,49 [0,44–0,53] |
| infirmiers | fraction | 0,06 | 0,15 | 0,20 [0,19–0,22] |

**Famille « tout » (leviers compris), 2050.**

| Profession | Facteur, ST 2050 [IC 95 %] (dans l'ordre) |
|---|---|
| sages-femmes | part_privee 0,66 [0,62–0,69] · quotas 0,24 [0,23–0,26] |
| dentistes | filiere 0,44 · part_privee 0,21 · quotas 0,19 · fenetre 0,10 · entrees 0,08 |
| pharmaciens | part_privee 0,37 · quotas 0,25 · filiere 0,23 · fenetre 0,10 · entrees 0,06 |
| kines | quotas 0,61 [0,58–0,64] · fenetre 0,21 · part_privee 0,07 · shrink 0,07 · entrees 0,06 |
| infirmiers | quotas 0,53 [0,50–0,57] · entrees 0,27 · fenetre 0,25 · fraction 0,09 · decalage_retraite 0,03 |

Les intervalles bootstrap restent tous plus étroits que l'indice dès que
ST ≥ 0,05 : le critère « N trop petit » n'est pas déclenché.

**Premier ordre S1 et interactions.** S1 est calculé sur Y centré ; brut,
l'estimateur sortait de [0, 1] (−0,34 à 1,78). Centré, il reste dans
[−0,001 ; 1,008]. L'écart ST − S1 mesure les interactions :
- elles sont fortes pour les IDE, entre la fenêtre (S1 0,28, ST 0,53) et
  les entrées (S1 0,24, ST 0,49) ;
- elles sont fortes pour les MK, entre la fenêtre (S1 0,35, ST 0,53) et
  les entrées (S1 0,01, ST 0,17) ;
- ailleurs, S1 ≈ ST.

Le choix de la fenêtre et celui des entrées doivent donc être faits
ensemble.

**Morris, ordre de grandeur en % de Y.** μ* mesure l'effet d'un pas de 2/3
de la plage, en % de N tendanciel à 2050.
- Quotas : 15 à 19 %.
- Filière : CD 24 %, PH 15 %.
- Part privée : SF 23 %, PH 16 %, CD 9 %, MK 4 %.
- Fenêtre : 4 à 8 %.
- Fraction de vieillissement : 4 à 8 %.
- Décalage retraite (levier corrigé) : 2 à 4 %.
- Cumul : `part_cumul` ≤ 0,16 % et `cumul_multiplicateur` ≤ 0,25 %.

### 2. Ce qui ne déplace pas la sortie
- **`part_cumul` et `cumul_multiplicateur`** : μ* ≤ 0,25 % de N à 2050,
  ST < 0,01, pour toutes les professions (mesuré). Les parts sourcées (0,8 à 4,7 %)
  sont trop petites pour peser.
- **`decalage_retraite`** (corrigé) : ST ≥ 0,05 seulement pour les IDE en
  2030 (0,14) ; ailleurs, ST ≤ 0,02.
- **`shrink`** : ST ≤ 0,17 (MK) ; ailleurs, < 0,05.

### 3. Fourchettes (deux composantes, jamais additionnées)

**Aucun backtest n'existe au-delà de h = 10 ans (MK et IDE : h = 5).** Les
deux composantes sont des extrapolations.

| Profession | N tendanciel 2050 | (a) propagation P5–P95 | (b) backtest extrapolé ± | Biais signé h = 5 |
|---|---|---|---|---|
| sages-femmes | 19 124 | 16 001 – 22 982 (−16 / +20 %) | ±65,6 % (6 573 – 31 675) | +7,8 % |
| dentistes | 76 397 | 64 816 – 102 482 (−15 / +34 %) | ±34,6 % | −4,6 % |
| pharmaciens | 72 309 | 65 561 – 96 092 (−9 / +33 %) | ±8,7 % | −0,2 % |
| kines | 160 783 | 146 683 – 176 233 (−9 / +10 %) | ±16,4 % (h_max 5) | −1,7 % |
| infirmiers (libéraux) | 115 323 | 95 647 – 125 972 (−17 / +9 %) | ±49,3 % (h_max 5) | +5,8 % |

- **(a)** P5–P95 de Y sur les 2 × 2048 tirages de la famille
  « incertitude ». Les choix discrets sont équiprobables, ce qui est
  **supposé**.
- **(b)** Méthode A3 de l'observatoire : pente a de |erreur nationale| ∝ h
  sur le banc N1 (défaut `twin_of(StockFlowLocal)`, privé central), puis
  ± 1,6 · a · h.
  - Le facteur 1,6 est **cité** (observatoire), non reproduit.
  - Les années intermédiaires sont dans
    [`out/fourchettes.csv`](../../../sensibilite/out/fourchettes.csv).
- **Biais SF.** L'erreur SF n'est pas du bruit mais un biais qui croît :
  +1,5 % à h = 1, +7,8 % à h = 5, +18,8 % à h = 10 (mesuré). La moitié
  haute de la bande (b) SF est donc peu informative : le modèle surestime.
- **Lien avec la tolérance N2.** Les deux composantes dépassent largement
  la tolérance de ±3 % fixée par N2 pour la reproduction DD76. C'est le cas
  « ce qui le renverserait » de la décision N2 : voir open.md.

### 4. Variante d'entrées « tendance » (hors Sobol)
La pente des entrées nettes, prolongée sur 24 ans, multiplie N(2050) :
- par 1,6 à 1,9 avec une fenêtre de 8 ans ;
- par 4 à 10 avec une fenêtre de 2 ans (SF : 183 200 contre 19 000).

Elle n'est pas utilisable à long terme ; c'est pourquoi elle est exclue du
plan.

### 5. Levier retraite
- **Avant le correctif de l'axe 0 (03:35).** Le levier du jumeau donnait
  0,7 à 1,85 fois l'effet de B1 (`e/(1+Δe)` sur 65+) : dentistes 1,10× à
  Δ = 1, 1,39× à Δ = 2 et 1,85× à Δ = 3. C'est concordant avec la seconde
  revue (+12 % et +41 %). Fichier :
  [`out/retraite_avant_correctif.csv`](../../../sensibilite/out/retraite_avant_correctif.csv).
- **Après le correctif.** Il reste 1,05 à 1,16 fois B1, et l'écart
  s'explique par le demi-effet sur 55–59 ans que le jumeau ajoute. La
  troisième revue ne trouve plus de défaut bloquant : **le facteur n'est
  plus marqué « biaisé »**. Tous les indices ci-dessus sont calculés sur le
  code corrigé.

## Conclusion pour l'axe 1 : liste priorisée

| Rang | Recherche | Pourquoi (mesuré) | Fiches concernées | Prix |
|---|---|---|---|---|
| 1 | **Part privée des salariés ambigus** (SF surtout, puis PH, CD, MK) : réduire l'écart min–max de l'axe 4 | ST 0,91 SF, 0,48 PH, 0,26 CD à 2050 ; μ* 23 % SF | data-secteur-sf/ph/cd/mk, param-ph-part-privee-biologie, param-ph-part-privee-etablissements, data-finess-parts-privees | ~1–2 h |
| 2 | **Transmission formation → entrées** : rendement, abandon, évaporation, délai L_p. Elle fixe l'effet des quotas et de la filière, premier levier partout | quotas ST 0,19–0,61 ; filière ST 0,55 CD, 0,32 PH | param-ide-rendement-diplomes, ide-abandon-1a, ide-abandon-promotion, ph-taux-inscription-diplomes (millésime 2015 à rafraîchir), ph-internat-postes, cd-specialisation-des, age-entree-exercice | ~2 h, **utile seulement quand l'axe 2 branche formation → N** |
| 3 | **Âges fins dans les tranches** (âge détaillé RPPS, ou au moins la forme intra-tranche) | fraction ST 0,20 IDE, 0,12 MK ; μ* 4–8 % | (pas de fiche : à créer) | ~45 min |
| 4 | Âge et cessation de retraite | decalage_retraite ST ≤ 0,04 sauf IDE 2030 (0,14) | param-mk-age-retraite, param-cessation-par-age | ~30 min, faible priorité |
| — | **Ne bouge pas la sortie : ne pas approfondir** | cumul μ* ≤ 0,25 %, ST < 0,01 | param-cumul-emploi-retraite (l'item open.md « cumul par caisse, millésime récent » peut être fermé) | 0 |
| — | **Indécidable aujourd'hui** (pas de point d'entrée dans le jumeau) | — | régulation (×8 fiches), θ, report des entrants, obligation MK, mortalité | après l'axe 2 |

Ce n'est **pas** une question pour l'axe 1 : la fenêtre et la variante
d'entrées (ST 0,5 pour MK et IDE) sont des choix d'estimation. Le banc
de l'axe 3 doit les trancher sur l'erreur hors échantillon, pas une source.

## Partie 2 — leviers branchés : le choix du décideur pèse-t-il plus que notre ignorance ?

**Code.** [`leviers.py`](../../../sensibilite/leviers.py) et
[`priorites.py`](../../../sensibilite/priorites.py).
- Composition `LEVIERS` du jumeau, instantané `git archive` (`v2/jumeau`
  au commit 4721268, empreinte `a8cb2750`).
- N = 512 par profession, plans par facteur et par groupe : 8 693 à
  11 253 runs par profession.
- 0,12 à 0,7 s par run selon la charge (mesuré).
- 5 processus en parallèle, de 56 à 115 min chacun.
- Décisions du 2026-11-14 : « Axe 5, partie 2 » et « fourchettes
  départementales ».

**Groupes.**
- **Décision** : quotas, capacité de formation, report de la retraite,
  cumul emploi-retraite, départs précoces, abandon IFSI (IDE), diplômés
  étrangers (SF, CD, MK) et part des zones régulées.
- **Connaissance** :
  - les choix d'estimation ;
  - la part privée des salariés ambigus ;
  - la fraction de vieillissement et la part en cumul ;
  - θ, la destination des entrants bloqués et la part exemptée.
- **Infirmiers** : on passe au **privé complet** (table axe 4, hypothèse
  H_ind), soit 301 681 en 2030 au tendanciel, contre les libéraux seuls
  de la partie 1.

### Part de la variance de N privé en 2050 (Sobol par groupe, IC 95 % bootstrap, mesuré)

| Profession | Décision S1 | Connaissance S1 | Interaction | Qui pèse le plus en 2050 ? | 2030 (décision / connaissance) |
|---|---|---|---|---|---|
| Infirmiers (privé complet) | **0,88** [0,77–0,99] | 0,12 [0,08–0,15] | 0,01 | la décision | 0,81 / 0,14 |
| Kinés | **0,71** [0,60–0,82] | 0,15 [0,10–0,20] | 0,14 | la décision | 0,41 / 0,64 |
| Pharmaciens | 0,48 [0,39–0,57] | 0,52 [0,44–0,61] | 0,00 | à égalité (IC chevauchants) | 0,04 / 0,91 |
| Sages-femmes | 0,41 [0,33–0,48] | **0,57** [0,49–0,63] | 0,02 | la connaissance | 0,03 / 1,04 |
| Dentistes | 0,41 [0,33–0,50] | **0,59** [0,50–0,67] | 0,00 | la connaissance | 0,09 / 0,88 |

**Message pour le décideur.**
- **En 2030, l'ignorance l'emporte presque partout.** La connaissance
  pèse de 0,64 à 1,04 ; la seule exception est celle des IDE, où les
  leviers rapides (capacité IFSI en 3 ans, abandon) agissent déjà.
- **En 2050, le choix pèse plus que l'ignorance pour les IDE et les
  kinés.** Pour les pharmaciens, les deux sont à égalité.
- **Pour les sages-femmes et les dentistes**, notre incertitude reste plus
  grande que l'effet du choix. Pour eux, réduire l'incertitude (part
  privée, filière) vaut autant que choisir.

**Leviers, ST à 2050 (mesuré).**
- Les **quotas** (0,14–0,39) et la **capacité de formation** (0,08–0,36)
  dominent partout. Ce sont deux mécanismes d'une même politique : leur
  somme approche la part « décision ».
- Diplômés étrangers : 0,27 pour les MK, 0,17 pour les CD, 0,04 pour les
  SF.
- Départs précoces : ≤ 0,08. Abandon IFSI : 0,07 (IDE).
- Report de la retraite (≤ 0,01), cumul (0,00) et part des zones régulées
  (≤ 0,01) **ne déplacent pas le total national**. La régulation
  redistribue les effectifs entre territoires, sans changer le total ;
  θ, la destination et la part exemptée ont un ST ≤ 0,011.

### Fourchettes 2050 par département
Figure : [`figures/2026-11-14-axe5-fourchettes-dep.svg`](../figures/2026-11-14-axe5-fourchettes-dep.svg).
Table : [`out/fourchettes_dep.csv`](../../../sensibilite/out/fourchettes_dep.csv).

- **(a) Largeur P5–P95** sur 500 tirages de la connaissance seule, en %
  du tendanciel départemental. Mesuré.
- **Seuil « assez sûr pour décider »** = 2 × l'effet national de quotas
  × 1,2 à 2050, soit 22,6 à 27,4 % selon la profession (dérivé).

| Profession | Effet quotas × 1,2 (2050) | Largeur (a), médiane [P10–P90] des départements | Départements « assez sûrs » | (b) backtest extrapolé, médiane (demi-largeur) |
|---|---|---|---|---|
| Sages-femmes | +12,3 % | 66 % [36–146] | 0 / 101 | ±77 % |
| Dentistes | +11,9 % | 69 % [48–114] | 0 / 101 | ±56 % |
| Pharmaciens | +11,3 % | 55 % [41–95] | 0 / 101 | ±32 % |
| Kinés | +11,9 % | 34 % [19–53] | 26 / 101 | ±46 % |
| Infirmiers (privé complet) | +13,7 % | 26 % [16–47] | 57 / 100 | ±460 % ⚠ |

- **Au département, le modèle n'est assez sûr pour décider que pour les
  IDE (57 départements) et les MK (26).** Pour les SF, CD et PH, la bande
  de connaissance dépasse partout deux fois l'effet du levier le plus
  fort.
- **Aucun backtest n'existe à 2050.** La composante (b) prolonge
  linéairement des erreurs observées jusqu'à h ≤ 10.
- **⚠ IDE, composante (b).** La pente d'erreur départementale médiane est
  de 10,4 %/an, alors que la série privée nationale est lisse (2013–2023,
  mesuré). La ventilation départementale sous H_ind (axe 4) est suspecte.
  Cette (b) n'est pas utilisable en l'état (open.md).

### Convergence (N suffisant ?)
Fichier : [`out/convergence.csv`](../../../sensibilite/out/convergence.csv).
On recalcule les indices sur les N premières lignes, avec 300 tirages
bootstrap.

- **Partie 1** (N = 2048) : la largeur max de l'IC de ST, pour les
  facteurs de ST ≥ 0,05 à 2050, passe de 0,19–0,41 à N = 128 à
  0,05–0,09 à N = 2048. L'écart à la valeur finale est ≤ 0,021 dès
  N = 1024.
- **Partie 2** (N = 512) :
  - largeur max de l'IC : 0,12–0,17 ;
  - l'écart entre N = 256 et N = 512 reste ≤ 0,05 ;
  - pour les 61 facteurs de ST ≥ 0,05, aucun IC n'est plus large que
    l'indice ;
  - les IC des parts « décision » et « connaissance » se séparent pour
    les IDE, les MK, les SF et les CD, et se chevauchent pour les PH.
- **Verdict** : N = 512 suffit pour le classement et pour les parts par
  groupe, pas pour départager des facteurs à ±0,08 près. Prolonger le
  plan coûte environ 1 h 30 de machine par doublement.

### Où mettre l'effort de recherche
Le gain attendu vaut ST × la fraction réductible (dérivé, voir
`priorites.py`) :
- 1 pour un choix d'estimation que le banc tranche ;
- 0,75 pour une plage divisée par deux ;
- 0,5 pour un encadrement de donnée resserré.

Les prix sont des estimations de temps (supposées).

| Rang | Source d'incertitude | ST 2050 (partie 2) | Moyen | Axe | Prix | Gain attendu |
|---|---|---|---|---|---|---|
| 1 | **Filière** (le vivier suit-il les entrées ?) | CD 0,33 · PH 0,17 | relier le vivier aux entrées (`lien_formation`) et le valider au banc N1 | 2 | ~1 h | CD 0,33 · PH 0,17 |
| 2 | **Part privée des salariés ambigus** | SF 0,50 · PH 0,26 · CD 0,14 · MK 0,03 | secteur par personne (Annuaire Santé), FINESS, SAE | 4 | ~1–2 h | SF 0,25 · PH 0,13 · CD 0,07 |
| 3 | **Fenêtre et entrées, ensemble** (interaction) | MK 0,09+0,03 · PH 0,07+0,04 · CD 0,06+0,05 | les trancher au banc N1, sur l'erreur hors échantillon | 2/3 | ~30 min machine | 0,05–0,12 par profession |
| 4 | Âges fins dans les tranches | IDE 0,05 · SF 0,02 | A1b (axe 2, adopté) à brancher dans le jumeau | 2 | ~45 min | IDE 0,04 |
| 5 | Ventilation départementale des IDE privés (H_ind) | ne pèse pas au national ; casse (b) au département | revoir le ratissage BTS × âge × sexe | 4 | ~1 h | (b) IDE utilisable |
| — | **Inutile d'approfondir** : cumul emploi-retraite, θ, destination des bloqués, part exemptée | ≤ 0,011 | — | 1 | 0 | ≈ 0 |

**Ce que le tableau ne mesure pas.** Les facteurs ont une prise sur le
total national ou départemental. La régulation, θ et la destination
agissent sur la **répartition entre communes**, que cette analyse ne
regarde pas. Leur ST nul ne dit rien de l'effet local.

## ⚑ Ce qui pourrait rendre ce résultat faux
- **Les plages font les indices.**
  - Les niveaux discrets sont équiprobables : une fenêtre de 2 ans pèse
    autant qu'une de 5 ans, ce qui est supposé.
  - Resserrer `fenetre` à {5, 8} ferait chuter son ST.
- **Le périmètre IDE couvre les libéraux seuls** (≈ 36 % du privé). Les
  salariés privés, sans âge dans les données, ne sont pas projetés.
- **Le modèle reste le stock-flux v1 réécrit.** Une méthode de l'axe 2
  (diplômés → entrées, régulation communale) peut changer le classement.
  C'est d'ailleurs le but.
- **La bande (b) est une extrapolation linéaire** de h ≤ 10 (MK et IDE :
  h ≤ 5) à h = 24–27, avec un facteur 1,6 cité et non reproduit. Pour les
  SF, c'est un biais qui croît, pas une dispersion.
- **La sortie est nationale.** Au département, le classement peut changer
  (`shrink` y pèserait plus) : pas mesuré. La partie 2 donne les
  fourchettes départementales, mais pas les indices par département.
- **Partie 2.**
  - Les IDE n'ont aucun facteur « données » : l'hypothèse H_ind n'est pas
    variée. Leur part « connaissance » est donc sous-estimée.
  - Les parts par groupe dépendent des amplitudes jouables choisies
    (quotas ±20 % ; l'interface va de 0,7 à 1,5).
  - Quotas et capacité, deux mécanismes d'une même politique, sont
    comptés tous les deux.
- **Le jumeau a changé plusieurs fois pendant l'analyse.** Le calcul
  final tourne sur un instantané figé (empreinte `c2dc7601`, 04:14). Les
  leviers branchés ensuite par l'axe 0 (commit 063c192) font l'objet de la
  partie 2.

## → Ce que ça change
- **Axe 1 :** ordre de recherche ci-dessus ; la question du cumul se
  ferme.
- **Axe 4 :** l'ambiguïté public / privé est la première source
  d'incertitude pour les SF et les PH, et non un détail de données.
- **Axe 2 :** brancher formation → N rend décidable la moitié des fiches
  et conditionne le premier levier (quotas).
- **Axe 3 :**
  - la tolérance N2 de ±3 % est bien plus étroite que les deux bandes ;
  - la fenêtre et les entrées doivent être choisies par le banc ;
  - le biais SF croît avec h.
- **Couche personas :** toute valeur affichée pour 2050 porte les deux
  bandes et la mention « aucun backtest à cet horizon ».

## Reproduire
Depuis la racine :

```
# instantané du jumeau (empreinte c2dc760126b34239) en tête de PYTHONPATH : PYTHONPATH=<snap>:v2:.
PYTHONPATH=v2:. uv run python -m sensibilite.run --n 2048 --r 30   # ≈ 20 min, Morris + Sobol, graine 20261114
PYTHONPATH=v2:. uv run python -m sensibilite.backtest                # banc N1 privé, pente A3
PYTHONPATH=v2:. uv run python -m sensibilite.tendance                # grille « tendance »
PYTHONPATH=v2:. uv run python -m sensibilite.retraite_b1             # levier retraite contre B1
PYTHONPATH=v2:. uv run python -m sensibilite.resume                  # tableaux -> out/resume.md
# partie 2 (instantané git archive de v2/jumeau au commit 4721268 en tête de PYTHONPATH)
PYTHONPATH=<snap2>:v2:. uv run python -m sensibilite.leviers --n 512 --mc 500 --profs <p> --tag _<p>   # une par profession
PYTHONPATH=<snap2>:v2:. uv run python -m sensibilite.carte backtest && ... carte
PYTHONPATH=<snap2>:v2:. uv run python -m sensibilite.convergence
PYTHONPATH=v2:. uv run python -m sensibilite.priorites
```

## ? Pour la suite
| Item | Prix |
|---|---|
| Refaire l'analyse au département (classement local, poids de `shrink`) | ~20 min machine |
| Ajouter la régulation (θ, zones) quand l'axe 2 la rend conservative et communale | ~30 min |
| Brancher formation → N (axe 2), puis relancer pour rendre décidables les fiches formation | 815 s machine après l'axe 2 |
| Plages pondérées (fenêtre, entrées) par l'erreur du banc N1 au lieu de l'équiprobabilité | ~30 min |
| Reproduire le facteur 1,6 de la méthode A3 sur notre banc (couverture observée à h ≤ 10) | ~20 min |
| Indices de Sobol par département (régulation, `shrink`, part privée locales) | ~2 h machine |
| Varier H_ind (ventilation IDE) comme facteur « données » | ~30 min + 1 h machine |
| Doubler N de la partie 2 (512 → 1024) pour départager les leviers à ±0,05 | ~1 h 30 machine |
| Vectoriser le vivier du module `formation` (axe 0) : ×10 sur le coût d'un run | ~1 h (axe 0) |
