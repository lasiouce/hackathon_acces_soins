---
type: analysis
date: 2026-11-15
author: Claude (session c1-intervalles)
question: La prévision conforme ou la réconciliation hiérarchique donnent-elles à C1 des bandes calibrées qui battent la persistance probabiliste en CRPS ?
headline: "Non. À l'origine 2021 (test N6), aucun des 6 candidats ne bat la persistance (meilleur : C1-conf, +0,0043 [−0,0006 ; +0,0094] en CRPS sur log N), et tous sont moins bons que C1 brut (+0,0012 à +0,0098). Le conforme abaisse la couverture à 80 % de 73,5 % à 63–67 %. Cause mesurée : le biais de C1 à h = 5 change de signe entre les origines 2016 (z moyen −0,30) et 2021 (+0,59)."
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 2, point faible de C1 en N6 (hors protocole ; N6 gelé, non modifié)
sources: [Vovk et al. 2005 « Algorithmic learning in a random world » (prédiction conforme, cité de mémoire), Gibbs & Candès 2021 NeurIPS (conforme adaptatif, cité de mémoire), Wickramasuriya, Athanasopoulos & Hyndman 2019 JASA 114(526) (MinT, cité de mémoire), Panagiotelis et al. 2023 EJOR 306(2) (réconciliation probabiliste par projection des tirages, cité de mémoire)]
tags: [axe2, c1, crps, conforme, mint, n6]
---

# Intervalles de C1 : prévision conforme et réconciliation hiérarchique

> **Headline :** **non**. À l'origine 2021, sur les cellules N6 (sages-femmes, dentistes et pharmaciens, 279
> départements), **aucun candidat ne bat la persistance probabiliste**. Le meilleur, C1-conf, est à
> **+0,0043 [−0,0006 ; +0,0094]** (mesuré) en CRPS sur log N, et **tous font moins bien que C1 brut**. C1 lui-même
> reste à égalité avec la persistance : **+0,0031 [−0,0008 ; +0,0071]** (mesuré). Le recalage sur le passé échoue, parce
> que l'erreur de C1 à h = 5 **n'est pas stationnaire** d'une origine à l'autre.

## Question
N6 trouvait que C1 fait jeu égal avec la persistance probabiliste, avec une bande à 80 % qui couvre 73,5 % (cible
75–85). Peut-on recalibrer les tirages de C1, ou les réconcilier entre échelles, pour gagner en CRPS sans perdre la
calibration ? Test d'abandon écrit avant le lancement : un candidat est abandonné si son CRPS à l'origine 2021 n'est
pas inférieur à celui de C1. Il gagne si la borne haute de l'IC à 95 % de Δ contre la persistance est < 0.

## Result

**Test principal : origine 2021, h = 5, cellules N6**
- Cellules : SF, CD et PH, 279 couples département × profession (mesuré). Les autres cellules n'ont pas 20 erreurs
  passées au même horizon.
- Δ et IC : bootstrap des départements, 2 000 tirages, graine 20261114, cellules à poids égal.

| Candidat | CRPS log | Couv. 80 % | Couv. 50 % | Δ vs persistance [IC 95 %] | Δ vs C1 [IC 95 %] |
|---|---|---|---|---|---|
| persistance (N6, même h) | 0,0625 | 63,1 % | 33,3 % | — | — |
| **C1 (tirages bruts)** | 0,0656 | **73,5 %** | **45,9 %** | +0,0031 [−0,0008 ; +0,0071] égalité | — |
| (a) C1-conf (tous h′) | 0,0669 | 63,4 % | 36,6 % | +0,0043 [−0,0006 ; +0,0094] égalité | +0,0012 [−0,0014 ; +0,0040] |
| (a) C1-conf-hg (adaptatif en h, post hoc) | 0,0672 | 66,3 % | 40,9 % | +0,0046 [−0,0003 ; +0,0098] égalité | +0,0015 [−0,0013 ; +0,0044] |
| (a) C1-conf-h5 (même h, o′ = 2016) | 0,0755 | 65,6 % | 30,8 % | +0,0130 [+0,0060 ; +0,0202] perd | +0,0098 [+0,0043 ; +0,0154] |
| (b) C1-MinT | 0,0676 | 67,0 % | 39,8 % | +0,0051 [+0,0009 ; +0,0093] perd | +0,0019 [+0,0010 ; +0,0030] |
| (c) C1-MinT-conf | 0,0679 | 62,0 % | 38,4 % | +0,0054 [+0,0002 ; +0,0106] perd | +0,0022 [−0,0006 ; +0,0052] |
| (c) C1-MinT-conf-hg | 0,0681 | 67,0 % | 42,7 % | +0,0056 [+0,0004 ; +0,0108] perd | +0,0024 [−0,0004 ; +0,0054] |
| tendance (N6, même h) | 0,0665 | 67,4 % | 41,6 % | +0,0039 [−0,0014 ; +0,0095] égalité | — |

Toutes les valeurs sont mesurées. La reproduction de N6 n'est que partielle : C1 donne 0,0656 contre 0,0654 et la
persistance 0,0625 contre 0,0623. Les couvertures, elles, sont identiques à N6 (73,5 et 45,9 %).

**Toutes origines, hors protocole**
- Cellules : h = 5, origines 2017–2021, 1 581 couples, 17 cellules profession × origine (mesuré).
- Référence : la persistance passée au même conforme tous horizons (score e/√h′), c'est-à-dire à armes égales.

| Candidat | CRPS log | Couv. 80 % | Couv. 50 % | Δ vs persistance-conf [IC 95 %] |
|---|---|---|---|---|
| persistance-conf | 0,0582 | 59,3 % | 32,8 % | — |
| C1 | 0,0589 | 77,4 % | 48,9 % | +0,0007 [−0,0029 ; +0,0044] égalité |
| C1-conf | 0,0598 | 63,7 % | 38,1 % | +0,0016 [−0,0014 ; +0,0047] égalité |
| C1-MinT | 0,0595 | 73,6 % | 45,4 % | +0,0013 [−0,0022 ; +0,0047] égalité |
| C1-MinT-conf | 0,0606 | 62,5 % | 37,3 % | +0,0025 [−0,0008 ; +0,0057] égalité |

**Pourquoi le conforme échoue : deux mesures sur les scores normalisés z = (log y − m)/s de C1**

| | h′ = 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| écart-type de z | 0,80 | 0,89 | 0,96 | 1,04 | 1,12 |

| Origine (h = 5) | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|
| moyenne de z | −0,30 | −0,28 | −0,10 | +0,31 | +0,29 | **+0,59** |

1. La dispersion de C1 croît moins vite avec l'horizon que son erreur.
   - Le score n'est donc pas invariant en h, et les scores à court horizon donnent une bande trop étroite à h = 5.
   - La variante C1-conf-hg corrige la pente, mais pas le centre.
2. **Le biais change de signe.** Avant 2018, C1 sur-prédit ; à partir de 2019, il sous-prédit.
   - Au même horizon, la seule origine de calibrage pour 2021 est 2016, de signe opposé : C1-conf-h5 déplace la bande
     dans le mauvais sens.
   - Aucun calibrage qui n'utilise que des cibles ≤ 2021 ne peut voir ce changement. Le conforme adaptatif (Gibbs &
     Candès) a le même retard de 5 ans à h = 5.
3. Le PIT de C1 en 2021 est déporté à droite (67 valeurs sur 279 dans la dernière classe) : la réalité dépasse la
   prévision.
4. La couverture dépend de la taille du département : 91 % pour les petits, 74 % pour les moyens, 55 % pour les grands
   (C1, 2021).
   - La bande de C1 a la forme d'un bruit d'échantillonnage. Elle ne contient pas le choc commun, qui pèse le plus sur
     les grands départements.
5. MinT tire les départements vers les prévisions de C1 au niveau région et France, qui sont moins bonnes. Le CRPS
   augmente : +0,0019 [+0,0010 ; +0,0030] contre C1, seul écart significatif.

## How
- **Données :** table privée de `methodes.perimetres.prive()` (axe 4 et RPPS des infirmiers libéraux), grille N1
  (`validation.forecast.design`), origines ≤ 2021.
- **Méthode :** [`v2/methodes/c1_intervalles.py`](../../../methodes/c1_intervalles.py).
  - Tirages : C1 (θ fixé), 200 tirages, ajusté au niveau département, région et France pour 25 couples
    profession × origine. Durée machine : 6 min au département, 3 min à la région, 2 min à la France.
  - Prédictives : définies dans la docstring. Séparation temporelle : seuls entrent les scores dont la cible est
    ≤ l'origine (o′ + h′ ≤ o).
- **Lancer :**
  - `PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.c1_intervalles tirages --level dep` (puis `reg`,
    `nat`) ;
  - puis `… eval`.
  - Sorties : `out/c1i_scores.parquet`, `out/c1i_verdicts.json` et `out/c1i_eval.log`.
- **Écart à la consigne :** les candidats sont des post-traitements des tirages de C1 dans le banc, et non des
  classes `Estimator`.
  - Une classe devrait réajuster C1 aux origines passées à chaque `fit`, soit environ 5 fois le coût.
  - Les candidats étant abandonnés, l'emballage n'a pas été fait (voir `open.md`).

## ⚑ What could make it wrong
- **Une seule origine de test**, 2021, et donc un seul choc commun. L'IC ne bootstrape que les départements : il
  ignore l'incertitude sur l'origine et il est trop étroit pour une conclusion générale.
- Les références sont citées de mémoire, sans relecture.
- La variante C1-conf-hg a été écrite après avoir vu les premiers résultats (post hoc). Elle ne gagne pas, ce qui
  limite le risque.
- Pour MinT, la région et la France sont ajustées en relabellisant le département. Le rétrécissement régional de C1
  y devient un seul groupe (« ? »). Un meilleur modèle aux niveaux supérieurs pourrait rendre MinT utile.
- La réconciliation s'arrête au département : C1 n'existe pas à la commune.

## → What it changes
- **La bande affichée reste celle de C1 brut**, avec sa couverture mesurée (« bande couvrant 73 % des cas
  passés »), comme le prescrit N6. Aucun recalibrage n'est retenu.
- Le levier de gain probabiliste n'est **pas la largeur de la bande, mais son centre**, c'est-à-dire le biais de
  période.
  - Piste : un choc commun national à h = 5 dans C1, à l'image du niveau local des entrées, dont la SBC dit déjà que
    la loi a posteriori est trop étroite (`L_T`, 10/10).
  - Conséquence attendue : des bandes plus larges pour les grands départements.
- Article de l'axe 2, paragraphe N6 : on peut ajouter une phrase. Le recalibrage conforme et MinT ont été essayés ;
  ils dégradent le CRPS de 0,001 à 0,010 parce que le biais change de signe entre les origines.

## ? Next
| Item | Cost |
|---|---|
| Choc commun national dans C1 (variance de L_T estimée, ou rétrécissement bayésien complet de σ_u, σ_v) puis relance de ce banc | ~2 h Claude + ~10 min machine |
| Juger sur le dépôt 2027 (origine 2022, h = 5) : deuxième origine de test, sans nouveau code | ~10 min machine, en 2027 (temps du monde) |
| Conforme par tiers de taille (score normalisé séparé petits / grands) — post hoc, à pré-enregistrer avant | ~30 min Claude |
