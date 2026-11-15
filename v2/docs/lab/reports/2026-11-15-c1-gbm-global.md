---
type: analysis
date: 2026-11-15
author: session c1-gbm
question: Un modèle d'apprentissage automatique global (GBM, MLP), entraîné sur toutes les séries à la fois, bat-il A2 en MAPE départementale à h = 5 ?
headline: "Rejeté : le GBM global fait 10,15 % de MAPE dép. à h = 5 contre 8,60 % pour A2 (Δ +1,55 pt, IC 95 % [+0,62 ; +2,75]) ; le MLP 20,52 % (Δ +11,92, [+10,54 ; +13,86]) ; aucune profession où l'un des deux gagne"
status: fait (banc N1, périmètre privé, test d'abandon inscrit avant)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: C1 — l'apprentissage automatique fait-il mieux que les méthodes interprétables ?
sources: [DREES RPPS × secteur (methodes.perimetres.prive, périmètre privé central), data/processed/stock.parquet, INSEE population par département (data/processed/population.parquet, scénario central, 2018+)]
tags: [c1, apprentissage-automatique, gbm, mlp, backtest, N1]
---

# C1-GBM : apprentissage automatique global contre A2

> **Headline :** les deux modèles sont **rejetés**.
> - **GBM global :** MAPE dép. à h = 5 de **10,15 %**, contre **8,60 %** pour A2.
>   Δ **+1,55 pt**, IC 95 % [+0,62 ; +2,75]. Il fait aussi moins bien que la
>   tendance naïve (9,32 %).
> - **MLP global :** **20,52 %**, Δ +11,92 pt, IC 95 % [+10,54 ; +13,86].
> - Aucune profession où l'un des deux bat A2. Le GBM est à égalité pour les
>   dentistes et les pharmaciens ; il perd ailleurs.

## Question
- Un modèle global appris sur toutes les séries (profession × département ×
  sexe × âge) prévoit-il mieux que le meilleur modèle interprétable (A2,
  shrinkage hiérarchique) ?
- Test d'abandon inscrit avant le banc :
  [dérivation](../derivations/2026-11-15-c1-gbm-global.md), SHA-256
  8e35043aecb2, commit 70f8bc9.
  - **Accepté** si la borne haute de l'IC bootstrap 95 % de MAPE(candidat) −
    MAPE(A2) à h = 5 est < 0.
  - **Sinon rejeté.**

## Résultat
MAPE dép. à h = 5 (%), mesurée. Δ par rapport à A2, avec IC bootstrap apparié
sur les départements (2 000 tirages, graine 20261114).

| Profession | Cellules | A2 | Tendance | GBM | Δ GBM [IC 95 %] | MLP | Δ MLP [IC 95 %] |
|---|---|---|---|---|---|---|---|
| **Total** | 22 | **8,60** | 9,32 | **10,15** | **+1,55 [+0,62 ; +2,75]** | 20,52 | +11,92 [+10,54 ; +13,86] |
| Dentistes | 6 | 8,66 | 8,70 | 8,45 | −0,21 [−0,85 ; +0,43] | 23,23 | +14,57 [+13,41 ; +15,75] |
| Infirmiers | 3 | 5,72 | 7,62 | 7,27 | +1,54 [+0,92 ; +2,18] | 14,34 | +8,62 [+7,73 ; +9,55] |
| Kinés | 1 | 6,62 | 9,12 | 11,37 | +4,75 [+1,13 ; +10,92] | 60,13 | +53,51 [+33,56 ; +88,54] |
| Pharmaciens | 6 | 5,06 | 5,85 | 6,00 | +0,94 [−0,48 ; +3,48] | 11,75 | +6,70 [+5,86 ; +7,59] |
| Sages-femmes | 6 | 13,87 | 14,29 | 17,25 | +3,38 [+1,86 ; +4,92] | 23,07 | +9,20 [+7,32 ; +11,14] |

- **Deux tests, deux verdicts.** Avec l'IC à 97,5 % (correction de
  Bonferroni), le GBM reste rejeté (Δ dans [+0,53 ; +2,91]), et le MLP aussi
  ([+10,43 ; +14,18]).
- **Selon l'horizon** (MAPE poolée, %) :

  | h | 1 | 3 | 5 | 8 | 10 |
  |---|---|---|---|---|---|
  | A2 | 2,73 | 5,59 | 8,60 | 14,33 | 17,59 |
  | GBM | 2,75 | 5,91 | 10,15 | 25,50 | 28,87 |
  | MLP | 3,70 | 9,77 | 20,52 | 23,33 | 51,15 |
  | Persistance | 3,12 | 6,85 | 9,94 | 13,56 | 16,06 |

  - Le GBM égale A2 à un an : 2,75 % contre 2,73 %.
  - L'erreur s'accumule ensuite par itération : à h = 10, le GBM est à
    28,9 % contre 17,6 % pour A2.
  - C'est la signature attendue d'un modèle à un pas sans structure
    démographique imposée.
- **Biais national à h = 5** (écart relatif de la somme France entière,
  moyenne des origines), en % :

  | Profession | GBM | A2 |
  |---|---|---|
  | Sages-femmes | +14,2 | +7,5 |
  | Infirmiers | +8,5 | +5,6 |
  | Dentistes | −7,7 | −5,0 |

  Le GBM amplifie les tendances récentes.

## Comment
- **Données.**
  - Panel privé central (`methodes.perimetres.prive`), 2012 → 2026.
    Infirmiers jusqu'en 2023, kinés depuis 2017.
  - Population INSEE par département, 2018+.
- **Méthode** ([`v2/methodes/gbm.py`](../../../methodes/gbm.py), banc
  [`v2/methodes/c1_gbm.py`](../../../methodes/c1_gbm.py)).
  - Modèle à un pas, itéré. La cible est la contribution de la cellule à la
    croissance relative du département : (n(a, t+1) − base vieillie) /
    N(dép, t).
  - Variables explicatives :
    - retards de la cible et des taux bruts ;
    - croissances du département à 1, 2 et 3 ans, croissance nationale ;
    - parts des 60 ans et plus et des moins de 35 ans ;
    - population, part des 60 ans et plus de la population, densité ;
    - effets fixes de région, de profession, de sexe et de tranche.
  - GBM : `HistGradientBoostingRegressor`, réglages fixés a priori ; MLP
    (32, 16).
  - **Aucun hyperparamètre réglé**, ni sur le banc, ni en validation
    imbriquée.
- **Banc.** `validation.forecast.design`, `bench` et le bootstrap apparié de
  `methodes.banc.boot`. Grille identique à celle de `tab:prive` : 42 origines
  au total, dont 22 cellules profession × origine à h = 5.
- **Contrôle de fuite, explicite.**
  1. Assertions : aucune donnée ni cible postérieure à l'origine dans
     l'entraînement.
  2. Test de perturbation : stock et population d'années > 2019 remplacés
     par du bruit uniforme. L'écart maximal des prédictions est de **0,0**
     pour les deux modèles (mesuré).
  3. La population est figée à l'origine pendant l'itération.
- **Lancer :** `OMP_NUM_THREADS=4 PYTHONPATH=v2 uv run --with scikit-learn==1.9.1 python -m methodes.c1_gbm`.
  - Durée du banc : 100 s (mesuré).
  - Sorties : `v2/methodes/out/c1_gbm_verdicts.json`, `c1_gbm_cellules.csv`
    et `c1_gbm.log`.

## Taille de l'échantillon (honnêtement)
- Lignes d'entraînement, selon l'origine (mesuré) : de **32 240 cellules** à
  l'origine 2016 à **80 620** en 2021.
- Ces lignes ne correspondent qu'à **1 612 à 4 031 départements × années**,
  issus de 4 à 9 transitions annuelles.
- Les séries réellement indépendantes sont environ 100 départements × 5
  professions, sur une seule histoire macro.
- Un MLP de ~1 500 poids sur quelques milliers de groupes corrélés est
  sous-déterminé. Son rejet ne dit rien de l'apprentissage profond à grande
  échelle ; il dit que ce volume de données ne le nourrit pas.

## ⚑ Ce qui pourrait le rendre faux
- **Pas de réglage.** Un GBM réglé en validation imbriquée pourrait réduire
  l'écart. C'est peu probable : l'écart de +1,55 pt vaut 14 fois le gain de
  A2 sur A0 (−0,11 pt), et il vient de la dérive à
  l'itération, pas de l'ajustement à un an (égalité à h = 1).
- **Écart de protocole.** Un essai de fumée a vu une cible de test (origine
  2021 → 2026) avant le banc. Aucun réglage n'en a été tiré : les réglages
  inscrits n'ont pas changé.
- **A2 vaut ici 8,60 %, contre 8,57 % dans `tab:prive`** (tendance 9,32 %
  contre 9,30 %). Les données du périmètre privé ont sans doute bougé depuis
  le banc de l'axe 2. La comparaison reste appariée, sur les mêmes données.
- **Un modèle direct à h = 5** n'était pas faisable sans fuite aux origines
  2016-2017. Un modèle direct sur les origines tardives seules reste non
  testé.
- **Kinés : une seule origine** à h = 5. L'IC par profession y est peu
  informatif.

## → Ce que ça change
- `v2/docs/lab/decisions.md` : C1-GBM est **rejeté** et reste au registre
  comme diagnostic (`c1_gbm_global`, `c1_mlp_global` dans
  `v2/validation/registry.py`).
- **A2 reste la meilleure méthode au total.** La réponse à « l'IA ferait-elle
  mieux ? » est mesurée : non, pas avec ces données.
- Tableau `tab:prive` du papier de l'axe 2 : on peut ajouter une ligne
  « GBM global 10,15 % » comme contrôle négatif. Cette mise à jour n'est pas
  faite ici.

## ? Suite
| Item | Coût |
|---|---|
| GBM direct à h = 5 sur les origines ≥ 2018 seulement (sans itération), avec validation imbriquée | ~20 min de Claude, ~5 min de machine |
| GBM sur les résidus de A2 (hybride interprétable + correction apprise), même test d'abandon | ~30 min de Claude |
| Ligne « contrôle négatif » dans `tab:prive` | ~5 min |
