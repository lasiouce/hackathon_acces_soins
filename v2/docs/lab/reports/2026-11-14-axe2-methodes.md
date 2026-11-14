---
type: analysis
date: 2026-11-14
author: Claude (session axe 2)
question: Une méthode interprétable prévoit-elle l'effectif « libéral » par département mieux que le stock-flux à taux locaux (protocole N1) ?
headline: "Shrinkage hiérarchique dép → région → national : MAPE dép. h=5 8,57 % contre 8,68 % pour le stock-flux à taux locaux (Δ −0,11 pt, IC 95 % [−0,21 ; −0,02], périmètre privé ; −0,10 sur l'ancien) ; âges fins à égalité ; rétention 60+ en tendance pire (+0,33 pt)"
status: fait (banc N1 lancé, 5 variantes confirmatoires)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 2
sources: [DREES RPPS 2012–2026 × secteur (v2/data/processed/secteur_stock.parquet, axe 4), data/processed/stock.parquet (millésime 2026-07-02), DREES 990_drees_mmop2_f.xlsx (inscrits 2020–2024)]
tags: [axe2, methodes, backtest, N1]
---

# Axe 2 : méthodes de prévision interprétables contre le stock-flux à taux locaux

> **Headline :** sur le périmètre **privé**, une seule méthode bat la
> référence : le **shrinkage hiérarchique** dép → région → national (A2).
> - A2 : MAPE dép. à h = 5 de **8,57 %**, contre 8,68 % pour le stock-flux
>   à taux locaux. Δ −0,11 pt, IC 95 % [−0,21 ; −0,02].
> - Âges fins (A1a, A1b) et combinaison : **égalité**.
> - Rétention des 60 ans et plus en tendance (A3) : **échoue** (+0,33 pt).
> - Toutes les variantes, la référence comprise, battent la meilleure
>   naïve (la tendance, 9,30 %), sauf A3, à égalité.
> - A2 est le seul gain qui se reproduit sur l'ancien périmètre
>   (−0,10 pt).
> - Le schéma de l'observatoire (B4, diagnostic non candidat) fait
>   8,32 % au privé, mais se renverse sur l'ancien périmètre (+0,53 pt
>   par rapport à A0).

**Le stock-flux à taux locaux gagne contre la meilleure naïve.** C'est
le **premier passage confirmatoire de N1** sur le jumeau, au périmètre
privé : Δ −0,63 pt, IC 95 % [−0,97 ; −0,27], contre 9,30 % pour la
tendance.

## Question
L'axe 2 ([ROADMAP](../../ROADMAP.md)) cherche une méthode qui prévoit
mieux que le stock-flux, sans boîte noire. Les règles :
- chaque méthode est un module branché sur le jumeau ;
- elle nomme le paramètre qu'un levier modifie ;
- elle passe le protocole N1, gelé avant les résultats.

## Résultat

### Banc N1, périmètre privé (confirmatoire)
La MAPE est mesurée par département à h = 5 (N ≥ 30 à l'origine), en
moyenne à poids égal sur 22 cellules profession × origine. Les IC à
95 % viennent d'un bootstrap des départements : 2 000 tirages, graine
20261114. Le bootstrap vectorisé reproduit `verdict()` à l'identique.

| Variante | MAPE h=5 | Δ vs tendance (IC 95 %) | Issue N1 | Δ vs A0 (IC 95 %) | Verdict vs référence |
|---|---|---|---|---|---|
| A0 stock-flux taux locaux (`jumeau_taux_locaux`) | 8,68 | −0,63 [−0,97 ; −0,27] | gagne | — | référence |
| **A2 shrinkage hiérarchique** | **8,57** | −0,74 [−1,07 ; −0,40] | gagne | **−0,11 [−0,21 ; −0,02]** | **bat** |
| A1b âges simples | 8,70 | −0,60 [−0,96 ; −0,24] | gagne | +0,03 [−0,07 ; +0,11] | égale |
| A123 combinaison (A1a + A2 + A3) | 8,74 | −0,56 [−0,92 ; −0,21] | gagne | +0,06 [−0,07 ; +0,18] | égale |
| A1a âges interpolés | 8,77 | −0,53 [−0,89 ; −0,17] | gagne | +0,09 [+0,01 ; +0,18] | échoue (de peu) |
| A3 rétention 60+ en tendance | 9,00 | −0,30 [−0,67 ; +0,08] | égalité | +0,33 [+0,23 ; +0,42] | échoue |
| *B4 observatoire, r ∈ [0,5 ; 1,2] (diagnostic)* | *8,32* | *−0,98 [−1,37 ; −0,59]* | *gagne* | *−0,35 [−0,65 ; −0,08]* | *non candidat* |
| tendance linéaire (naïve) | 9,30 | — | — | — | — |
| persistance (naïve) | 9,92 | — | — | — | — |

**Critères et contrôles du protocole :**
- **Bonferroni.** À l'IC 99 % (5 variantes), toutes les victoires contre
  la naïve tiennent. Pour A2, l'écart à A0 est une comparaison
  *exploratoire*, inscrite comme telle dans la dérivation, et n'est pas
  corrigé.
- **Limite h = 1 et précision nationale.** Tout passe : à h = 1, aucune
  variante n'est à plus de 1 point de la persistance.

**MAPE h = 5 par profession (%) :**

| | CD | IDE lib. | MK | PH | SF |
|---|---|---|---|---|---|
| A0 | 8,95 | 5,89 | 6,47 | 4,99 | 13,85 |
| A2 | 8,66 | 5,72 | 6,62 | 5,06 | 13,73 |
| A1b | 9,05 | 5,84 | 6,46 | 4,95 | 13,91 |
| A3 | 8,92 | 7,27 | 7,09 | 5,83 | 13,44 |
| B4 (diag.) | 8,00 | 7,54 | 7,50 | 4,68 | 12,82 |
| tendance | 8,70 | 7,62 | 9,12 | 5,85 | 14,23 |

**Stabilité entre origines.** Une origine est « gagnée » quand la
méthode bat la naïve sur cette origine.
- Les dentistes ne gagnent que 3 origines sur 6 (A0 : 2 sur 6) : l'avantage
  des dentistes dépend de l'origine.
- Les autres professions gagnent de 4 sur 6 à 3 sur 3.
- Le banc de ce périmètre a pris 18,7 s (machine).

### Ancien périmètre, libéral + mixte (secondaire, pour K1)
Le banc a pris 23,5 s.

| Variante | MAPE h=5 | Δ vs tendance (IC 95 %) | Δ vs A0 (IC 95 %) |
|---|---|---|---|
| A0 | 8,21 | −0,93 [−1,30 ; −0,56] | — |
| **A2** | **8,10** | −1,04 [−1,39 ; −0,69] | **−0,10 [−0,21 ; −0,002]** |
| A1b | 8,18 | −0,96 [−1,31 ; −0,61] | −0,03 [−0,15 ; +0,08] |
| A1a | 8,26 | −0,88 [−1,23 ; −0,53] | +0,05 [−0,06 ; +0,16] |
| A123 | 8,71 | −0,43 [−0,78 ; −0,09] | +0,50 [+0,35 ; +0,64] |
| A3 | 8,97 | −0,17 [−0,58 ; +0,25] (égalité) | +0,76 [+0,61 ; +0,91] |
| *B4 (diag.)* | *8,74* | *−0,40 [−0,83 ; −0,02]* | ***+0,53 [+0,15 ; +0,88]*** |
| tendance | 9,14 | — | — |

**Ce que l'ancien périmètre confirme et ce qu'il renverse :**
- **A2 est le seul gain qui se reproduit sur les deux périmètres**
  (−0,11 et −0,10 pt). Sur l'ancien périmètre, sa borne haute frôle 0.
- **B4 se renverse.** Il est le meilleur au privé (−0,35 pt) et pire
  qu'A0 sur l'ancien périmètre (+0,53 pt). Son avantage dépend du
  périmètre. C'est une raison de plus de ne pas l'adopter.
- A0 sur l'ancien périmètre mesure 8,21 %, contre **8,08 % dans K1** (v1).
  La grille diffère : origines glissantes contre 2 origines. L'ordre de
  grandeur est le même.

### Ce que disent les prédictions écrites avant le banc
Les prédictions étaient dans la [dérivation](../derivations/2026-11-14-axe2-methodes.md),
SHA `1c324f5795b0`.

| Prédiction | Observé | Tient ? |
|---|---|---|
| \|Δ(A1, A0)\| < 0,3 pt | +0,09 (A1a), +0,03 (A1b) | oui |
| A2 améliore A0 de 0 à 0,3 pt | −0,11 | oui |
| A3 réduit le \|biais national\| pour PH et CD | PH : −0,15 → +2,28 % (pire) ; CD : −4,58 → −4,10 % | **non** |

### Monde simulé à âges connus (kill test de A1)
18 mondes : pic de génération 0, 60 ou 120, centré à 40, 50 ou 55 ans ;
entrées constantes ou en hausse de 2 %/an. On observe des tranches, on
ajuste sur 10 ans et on projette.

| Méthode | \|erreur\| 60+ h=5, moyenne (max) | \|erreur\| 60+ h=10 | \|erreur\| total h=5 |
|---|---|---|---|
| uniforme (A0) | 7,0 % (18,9 %) | 5,2 % (12,0 %) | 3,9 % |
| A1a interp | 5,3 % (13,5 %) | 4,5 % (9,7 %) | 3,0 % |
| **A1b âges simples** | **2,1 % (5,9 %)** | **1,8 % (2,9 %)** | 3,8 % |

- Le vieillissement uniforme biaise la part des seniors **jusqu'à 19 %**
  (mesuré). C'est l'ordre de grandeur cité par l'observatoire, +8 à
  +19 %.
- Les âges simples le divisent par 3.
- Le biais n'a pas de signe fixe : sa moyenne est de −1 %, il dépend de
  la position du pic de génération.
- Il ne se voit **pas** sur le total à h = 5, qui est dominé par les
  entrées (dérivé : la rétention s absorbe l'erreur d'âge dans la
  fenêtre).
- Cela explique l'égalité au banc. A1 survit pour la **structure par âge**
  et pour les leviers retraite ; il n'apporte pas de gain sur le total.

### B4 : la borne r ≤ 1,2 de l'observatoire fait-elle s'emballer les entrées ?
Croissance nationale projetée de 2026 à 2050, sur le périmètre privé,
origine 2026 :

| | observée (10 ans, %/an) | A0 (%/an) | B4 r ≤ 1,2 (%/an) | 2050/2026 A0 → B4 | cellules ≥ 35 ans avec r > 1 |
|---|---|---|---|---|---|
| CD | 1,60 | 1,13 | 2,00 | 1,31 → 1,61 | 30 % |
| MK | 3,29 | 1,68 | 1,93 | 1,49 → 1,58 | 29 % |
| PH | −0,16 | 0,10 | 0,24 | 1,03 → 1,06 | 27 % |
| SF | 2,79 | 1,70 | 1,79 | 1,50 → 1,53 | 43 % |
| IDE lib. | 2,35 | 0,97 | 1,24 | 1,30 → 1,40 (2023 →) | 47 % |

**Verdict B4 : le piège est partiellement reproduit.**
- De 27 à 47 % des cellules hors entrées ont r > 1. Leur croissance est
  donc proportionnelle au stock et se compose.
- L'écart à A0 est de **+0,1 à +0,9 pt/an**. Pour les dentistes, cela
  fait **+23 % d'effectif en 2050** (1,61 contre 1,31).
- Ce n'est pas l'emballement de K1 (+3,5 %/an), et à h ≤ 10 c'est même un
  **avantage** au banc (MAPE 8,32 %).
- Le risque se concentre au-delà de l'horizon backtestable. C'est
  exactement là où N1 ne voit rien et où N2 (DREES n°76 à 2050) doit
  trancher.

**Ablation exploratoire** (inscrite après avoir vu le banc) : l'avantage
de B4 ne vient ni des entrées récentes, ni de la hiérarchie.
- A0 avec les entrées récentes sur 5 ans : 8,75 %.
- B4 sans hiérarchie : 8,34 %.
- Il vient donc de la **croissance proportionnelle au stock dans les
  tranches de 35 ans et plus** : son biais national à h = 5 est de
  +0,92 %, contre +1,50 % pour A0.

### C5 : la région de formation prédit-elle la région d'installation ? (exploratoire)
On compare deux prédicteurs de la part régionale des entrées nettes
(calibrées sur 2019–2026, 12 régions) :

| | r (part étudiante, DE années 2–6, 2020–2024) | r (part du stock 2026) | erreur moyenne, part étudiante | erreur moyenne, part du stock |
|---|---|---|---|---|
| CD | 0,64 | 0,996 | 3,2 pts | 0,4 pt |
| PH | 0,94 | 0,996 | 1,2 pt | 0,3 pt |

- En **niveau**, la part du stock prédit les entrées bien mieux que la
  région de formation. Répartir les entrées par région de formation
  dégraderait la prévision à structure inchangée.
- C5 garde sa valeur comme **mécanisme de levier** (numerus apertus
  régional, nouvelles antennes). Il faut pour cela une série d'inscrits
  par université avant 2020, pour tester les *variations*.

### Verdict par candidat
| Candidat | Méthode | Verdict | Paramètre que touche un levier |
|---|---|---|---|
| 1. Âges plus fins | A1a (désagrégé chaque année), A1b (âges simples) | **égale** au banc ; **adoptée pour la structure par âge** (monde simulé : erreur 60+ divisée par 3) | aucun nouveau. Les leviers `decalage_retraite` et `cumul_multiplicateur` agissent par tranche, avec un effet plus juste sur les âges |
| 2. Shrinkage hiérarchique | A2 | **bat** la référence (−0,11 pt) ; **adoptée** | k (poids 200, `shrink`) : un réglage d'estimation, pas un levier politique. Les leviers restent ceux de `sorties` et `entrees` |
| 3a. Rétention 60+ en tendance | A3 | **échoue** (+0,33 pt). Gardée seulement comme levier, avec λ = 0 par défaut | `methodes_sorties.tendance_60plus` (λ) |
| 3b. Diplômés étrangers (CD) | — | **non testé** : aucune série ouverte par lieu de diplôme dans nos données (C8 de la reprise, sans source primaire) | serait `entrees.flux_etranger` |
| 4. Choix discret de l'installation | A4 (logit) | **non testé, en attente** : avec effets fixes, il égale les parts observées par construction ; il faut un attribut daté par département | serait β(zonage) dans l'utilité, levier régulation |
| 5. Bayésien hiérarchique / espace-état | A5 | **non testé, en attente** : au département avec N ≥ 30, sa moyenne a posteriori ≈ A2 ; son gain relève de N4 (commune) | — |
| 6. Microsimulation | A6 | **tuée pour N1** : même espérance que A0 par linéarité | — |
| B4 (borne 1,2) | diagnostic | piège partiel (+0,1 à +0,9 pt/an à 2050) ; meilleur au privé, pire sur l'ancien périmètre ; **non adopté** | — |
| C5 (université → ARS) | diagnostic | **non adopté pour la prévision** (part du stock r = 0,996 contre 0,64–0,94) | serait la capacité de formation régionale |

## How
- **Données.**
  - Périmètre privé : `jumeau.history.sector_table(…, "central")`, axe 4.
  - Infirmiers : libéraux du RPPS (`data/processed/stock.parquet`).
  - Ancien périmètre : `mode3 == "liberal_mixte"`.
  - Le tout est construit dans `v2/methodes/perimetres.py`.
- **Méthode.**
  - [`v2/methodes/calibrage.py`](../../../methodes/calibrage.py) généralise
    `fit_rates` : opérateur de vieillissement, hiérarchie, tendance des 60
    ans et plus, schéma de l'observatoire.
  - [`modules.py`](../../../methodes/modules.py) : trois modules
    `methodes_*` enregistrés dans le registre du jumeau. Ils produisent
    les flux `vieillissement`, `sorties` et `entrees`.
  - [`estimators.py`](../../../methodes/estimators.py) : les variantes
    derrière `TwinEstimator`.
  - Inscription : `v2/validation/registry.py`, 03:25, avant tout
    passage.
- **Commandes** (depuis la racine) :
  - `PYTHONPATH=v2 uv run python -m methodes.verif` : V1–V5, aucune cible
    regardée ;
  - `… -m methodes.banc` : N1, environ 19 s de banc et quelques minutes
    de bootstrap ;
  - `… -m methodes.monde`, `… -m methodes.b4`, `… -m methodes.c5`,
    `… -m methodes.ablation`.
  - Sorties : `v2/methodes/out/`.
- **Contrôles mesurés.**
  - Aux options v1, la composition `methodes` égale
    `twin_of(StockFlowLocal)` à 9e-13 personne près.
  - La désagrégation conserve la masse (5e-13).
  - Le levier λ = 0 égale la variante sans tendance.
  - λ = 1 ajoute +1 553 pharmaciens en 2026 (origine 2021). C'est l'ordre
    de grandeur des +1 527 pharmaciens de plus de 65 ans mesurés en v1.

## ⚑ What could make it wrong
- **Petite marge pour A2.** −0,11 pt, avec une borne haute de −0,02.
  - Le bootstrap par département ignore la corrélation entre origines
    (⚑ du protocole N1) : l'IC est probablement trop étroit (supposé).
  - L'écart à A0 n'est pas le critère du protocole, qui se mesure contre
    la meilleure naïve : c'est une comparaison déclarée exploratoire.
- **Contamination.** Les cibles 2023 et 2026 ont déjà été vues par K1. Le
  seul test propre sera le dépôt 2027 (non écrit ici, voir Next).
- **Sages-femmes privées.** MAPE de 13 à 14 %, et la cellule pèse
  lourd. Leur série libérale a été multipliée par 1,8 entre 2012 et 2026.
  - Une partie de l'écart peut venir de la répartition public / privé de
    l'axe 4, qui change dans le temps (variante centrale seulement ;
    min / max non passés).
- **B4 a été choisi par l'observatoire après ses propres essais.**
  - Son avantage au privé est un résultat de diagnostic, pas une
    victoire pré-inscrite.
  - Il se renverse sur l'ancien périmètre (+0,53 pt).
- **Hypothèses des âges fins** (supposé) : tranche « moins de 25 » = 20–24
  ans ; tranche 65+ de largeur 10 ; entrées réparties uniformément dans
  la tranche.

### Défauts du contrat signalés (non corrigés)
- **Seconde revue du jumeau** (`revue-adversariale-axe0-v2`), effets
  sur ce banc :
  - **Aucun effet sur les résultats.** Le banc appelle `predict` avec le
    scénario par défaut de chaque variante, et ce scénario n'a aucun
    paramètre de base. Les options des méthodes passent par
    `hist.options`, pas par le scénario.
  - **Aucun levier ni sélecteur** n'a servi à départager les méthodes.
  - **Biais hérité.** `methodes_sorties.decalage_retraite` recopie le
    mécanisme de `sorties`, donc il hérite du biais de la tranche 65+.
    Il faudra le réaligner quand l'axe 0 aura corrigé.
- **Vieillissement par cellule.** `Shift` n'accepte qu'une fraction par
  tranche, pas par cellule. Un vieillissement non uniforme par cellule
  (A1a) passe donc par un `Add` à somme nulle, et son compte au registre
  est `vieillissement`, pas `interne`.
- **Calibrage non injectable.** `stock_flow_rates` est une fonction, avec
  un cache privé sur `History`. Une méthode qui change le calibrage doit
  donc remplacer les trois modules : les leviers changent de nom
  (`methodes_sorties.*` au lieu de `sorties.*`), et le mécanisme des
  leviers retraite est recopié.
- **Échelle commune.**
  - A1a à la commune coûte **+1,23 s** par profession jusqu'en 2050
    (70 094 cellules, mesuré). Cinq professions dépasseraient le budget de
    2 s.
  - Ne pas l'utiliser à la commune sans optimisation.
  - Les tranches CartoSanté (< 40, 40–49…) cassent l'hypothèse de largeur
    5 de la tranche du bas.

## → What it changes
- **Variante par défaut proposée pour la prévision :** A2 + A1b.
  - A2 parce qu'il bat la référence.
  - A1b parce qu'il est à égalité sur le total et plus juste sur les âges.
  - Ce n'est **pas** encore confirmatoire : A2 + A1b n'a pas été
    pré-inscrite. Il faut l'inscrire, puis la passer, avant de l'annoncer.
- **Axe 3 (N2).** B4 et A0 divergent de +23 % pour les dentistes en 2050.
  Seule la reproduction DD76 peut trancher.
- **Axe 0.** Les deux défauts du contrat sont à arbitrer par l'axe 0.
- **Axe 5.** k (shrinkage) et λ (tendance des 60 ans et plus) sont deux
  facteurs d'estimation à ajouter au criblage.

## ? Next
| Item | Cost |
|---|---|
| Inscrire puis passer A2 + A1b (et A2 + B4 si N2 le permet) | ~5 min Claude + ~3 min machine |
| Dépôt de prévisions 2027–2030 de A0 et A2 (seul test hors échantillon propre) | ~10 min |
| N2 : A0 contre B4 contre DD76 à 2050 (dentistes en priorité) | ~30 min |
| Passer le banc avec les variantes min / max du privé (sensibilité de SF) | ~5 min |
| A4 logit avec un attribut daté (population Insee 1975–2026, C2) | ~1 h |
| A5 à la commune, protocole N4 | ~2 h |
| Optimiser A1a à la commune (float32, sans `where`) ou réserver A1b | ~30 min |
| Série d'inscrits par université avant 2020 pour tester C5 en variation | ~1 h de recherche de données |
