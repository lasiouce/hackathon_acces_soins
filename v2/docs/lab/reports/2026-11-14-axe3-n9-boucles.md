---
type: analysis
date: 2026-11-14
author: session axe 3
question: Les deux boucles de rétroaction proposées ont-elles le signe attendu dans les données ? B2 (densité → installations nettes des moins de 40 ans) et B1 (densité → départs avant 60 ans)
headline: "Protocole pré-enregistré, pas encore lancé : B2 par bassin de vie × année (IDE, MK, CD, 2014–2025), B1 par département × année (5 professions, cohortes 45–54 → 50–59 à 5 ans) ; verdict par profession : signe confirmé, nul ou contraire, IC 95 % robuste par département ; placebo « densité des autres professions »"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: axe 3, N9 ; décision « Tests des boucles de rétroaction »
sources: [v2/data/processed/commune_attributs.parquet (axe 4 : population Insee, structure d'âge, zonages 2012 et actuel, libéraux CartoSanté, proxy d'installations nettes `inet_*`), data/processed/stock.parquet (RPPS 2012–2026)]
tags: [validation, axe3, retroaction, pre-registration]
---

# N9 — signe des boucles de rétroaction B1 et B2 (protocole pré-enregistré)

> **Headline:** protocole **gelé avant tout calcul** sur ces questions. Il ne
> dit pas *comment* modéliser une boucle ; il dit seulement si son **signe**
> se voit dans les données, et avec quelle incertitude.

## B2 — densité → installations nettes des moins de 40 ans

**Hypothèse (signe attendu).** Là où la densité est faible, les installations
nettes de jeunes libéraux **par habitant** sont plus fortes : β < 0.

**Données.** `commune_attributs.parquet` (axe 4) : `lib_*` (libéraux actifs
au 31/12, CartoSanté), `inet_*` (proxy d'installations nettes des moins de
40 ans, **solde**), `population` (Insee), `part_0_14`, `part_65p`, zonages
`z_*_2012` et `z_*_actuel` (statut : incitation, remplacement_seul, autre).

**Unité.** Bassin de vie 2022 × année (la commune est trop bruitée).
Agrégats : N_b,t = Σ lib, I_b,t = Σ inet, P_b,t = Σ population ; parts
d'âge pondérées par la population ; parts de population de chaque statut de
zonage (2012 et actuel).

**Variables.**
- Résultat : y_b,t = 100 000 · I_b,t / P_b,t−1 (installations nettes pour
  100 000 habitants).
- Densité : D_b,t−2 = 100 000 · N_b,t−2 / P_b,t−2 ; régresseur **log(1 + D)**.
  Décalage de **2 ans** pour casser le lien mécanique entre le bruit de
  N_t−1 et le solde de l'année t.
- Années t = 2014 à 2025.

**Modèle principal.** MCO : y = β · log(1 + D_t−2) + γ · contrôles + effets
fixes **département** et **année**. Contrôles : log P_t−1, part_0_14,
part_65p, parts de zonage 2012 « incitation » et « remplacement_seul », mêmes
parts pour le zonage actuel. Non pondéré (chaque BV × année pèse 1). BV avec
P ≥ 1 000.

**Inférence.** Variance robuste par grappe = département (CR1), Student à
G − 1 ddl, IC 95 %.

**Verdict par profession.** Signe **confirmé** si l'IC de β est entièrement
< 0 ; **contraire** s'il est entièrement > 0 ; **nul** sinon.

**Placebo (attractivité générale).** Même modèle, où log(1 + D) est remplacé
par la densité **des deux autres professions** (somme des libéraux des deux
autres, pour 100 000 habitants, t − 2). Si β_placebo a le même signe que β
et |β_placebo| ≥ ½ |β|, le verdict devient « **non attribuable** » : la
densité mesure alors l'attractivité générale du territoire, pas la
saturation propre à la profession.

**Rapporté, non décisif.** (a) Sans contrôles de zonage (le zonage est
lui-même fonction de la densité) ; (b) décalage d'un an (D_t−1) ; (c) densité
propre et densité des autres dans le même modèle.

## B1 — densité → départs avant 60 ans

**Hypothèse (signe attendu).** Là où la densité est faible, la rétention des
45–59 ans est plus faible : β > 0 (plus de densité, plus de rétention).

**Données.** RPPS `data/processed/stock.parquet`, mode `liberal_mixte`
(exercice libéral ou mixte), par département × tranche × année ; population
des départements = somme des communes (`commune_attributs`). Professions :
SF, CD, PH, MK (RPPS à partir de 2017), IDE libéraux (jusqu'en 2023).

**Variables.**
- Rétention de cohorte à 5 ans : R_d,t = N[50–59]_d,t+5 / N[45–54]_d,t.
  Elle mêle cessations, passages au salariat et migrations entre
  départements ; c'est un **solde**.
- Densité : D_d,t = 100 000 · N_tous âges,d,t / P_d,t ; régresseur log D.
- t de la première année disponible à la dernière telle que t + 5 ≤ fin de
  série (CD, SF, PH : 2012–2021 ; MK : 2017–2021 ; IDE : 2012–2018).

**Modèle principal.** MCO : log R = β · log D + γ · (log P_d,t, log
N[45–54]_d,t) + effets fixes **région** et **année**. Départements avec
N[45–54] ≥ 30. Variance robuste par département, Student à G − 1 ddl.

**Verdict.** **Confirmé** si l'IC est entièrement > 0 ; **contraire** s'il
est entièrement < 0 ; **nul** sinon.

**Placebo.** La même règle « densité des autres professions » que pour B2
(somme des quatre autres professions du RPPS, même mode). Même seuil.

## Limites annoncées d'avance
- **Endogénéité.** La densité résulte des installations passées : β n'est
  pas causal. Le test dit si le signe est compatible avec la boucle.
- **Solde, pas flux brut.** Un déménagement compte −1 ici et +1 là ; une
  cessation compensée par une installation ne se voit pas.
- **Écologie.** B1 est au département : une relation entre départements ne
  dit rien des individus.
- **Mécanique.** Le décalage de 2 ans (B2) réduit, sans l'annuler, le retour
  à la moyenne dû au bruit de N.

## How
- Code : `v2/validation/boucles.py` ; sorties `v2/validation/out/boucles_*`.

---

## Résultat (ajouté après calcul ; gel 08:10, SHA-256 `96a39bc087bb`)
`PYTHONPATH=v2 uv run --with scipy python -m validation.boucles` (~7 s) →
`v2/validation/out/boucles_results.json`.

### B2 — densité → installations nettes (BV × année, 20 460 obs., 96 départements)
β en installations nettes pour 100 000 habitants par unité de log(1 + D).

| Profession | β [IC 95 %] | Placebo (autres professions) | y moyen | Verdict |
|---|---|---|---|---|
| Infirmiers | −1,52 [−4,05 ; +1,01] | −1,72 [−3,82 ; +0,37] | 6,0 | **nul** |
| Kinés | −1,66 [−3,43 ; +0,11] | −2,76 [−5,07 ; −0,46] | 4,4 | **nul** |
| Dentistes | +0,17 [−0,05 ; +0,39] | −0,45 [−0,77 ; −0,13] | 1,7 | **nul** |

Rapporté (non décisif) : sans zonage −1,07 / −0,58 / +0,33 ; densité à t − 1
−2,27 / −2,73 / −0,10 ; densité propre et des autres ensemble : propre
−0,97 / −0,84 / +0,26, autres −1,38 / −2,31 / −0,56.

**Lecture.** Aucun signe établi. Pour IDE et MK, le point a le signe attendu,
mais la densité des **autres** professions pèse autant ou plus : on voit une
attractivité générale du territoire, pas une saturation propre. Le
décalage d'un an double l'effet : c'est le retour à la moyenne mécanique que
le décalage de deux ans écarte.

### B1 — densité → rétention des 45–54 ans à 5 ans (département × année)
β en log R par unité de log D.

| Profession | Années t | Obs. (G) | β [IC 95 %] | Placebo | Verdict |
|---|---|---|---|---|---|
| Sages-femmes | 2012–2021 | 122 (15) | −0,24 [−0,48 ; +0,01] | +0,02 | nul |
| Dentistes | 2012–2021 | 756 (89) | +0,04 [−0,03 ; +0,10] | +0,05 [+0,01 ; +0,09] | nul |
| Pharmaciens | 2012–2021 | 862 (92) | −0,01 [−0,14 ; +0,11] | +0,05 | nul |
| Kinés | 2017–2021 | 451 (92) | −0,02 [−0,08 ; +0,03] | +0,05 | nul |
| **Infirmiers libéraux** | 2012–2018 | 700 (100) | **+0,11 [+0,05 ; +0,18]** | −0,00 [−0,04 ; +0,03] | **confirmé** |

**Lecture.** Pour les infirmiers libéraux, une densité deux fois plus forte va
avec une rétention à 5 ans des 45–54 ans plus haute d'environ 8 % (dérivé :
2^0,113 − 1), et la densité des autres professions n'y est pour rien. Pour
les autres professions, aucun signe. Sages-femmes : 15 départements
seulement passent le seuil de 30.

## ⚑ What could make it wrong
- Endogénéité : la densité est le produit des installations passées.
- Soldes, pas flux bruts : une migration compte −1 ici et +1 là.
- Écologie (B1, département) ; régime de zonage qui change en cours de
  période (IDE 2019–2020, MK 2018), contrôlé seulement par des parts fixes.
- B2 sur CartoSanté (libéraux), B1 sur le RPPS libéral + mixte : deux sources.

## → What it changes
- **Axe 2** : B2 n'a pas de signe établi ; la densité n'entre pas comme
  covariable **confirmée** du logit d'installation (elle peut y entrer comme
  covariable à estimer, sans a priori de signe).
- **Jumeau / axe 5** : la boucle charge → départs reste un scénario de stress
  « supposé » ; seul le cas IDE a un signe mesuré, au département.
