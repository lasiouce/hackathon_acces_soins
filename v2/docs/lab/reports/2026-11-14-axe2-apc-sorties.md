---
type: analysis
date: 2026-11-14
author: Claude (session axe 2)
question: Un modèle âge-période-cohorte bayésien de la rétention nette prévoit-il mieux que le stock-flux à taux locaux, et sa prévision probabiliste est-elle calibrée ?
headline: "APC gaussien de la rétention nette : MAPE dép. h=5 8,74 % contre 8,68 % (A0), égalité (Δ +0,07 [−0,03 ; +0,16]) ; bat la rétention 60+ en tendance (9,00 %) ; CRPS relatif 6,82 % mais intervalles trop étroits (couverture 80 % : 50 %) ; calibration par simulation réussie"
status: fait (étape 1 du programme de l'axe 2)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 2, étape 1
sources: [DREES RPPS 2012–2026 × secteur (axe 4, périmètre privé), data/processed/stock.parquet (2026-07-02)]
tags: [axe2, APC, bayésien, backtest, N1, CRPS, PIT, SBC]
---

# Étape 1 : sorties en âge-période-cohorte bayésien

> **Headline :** l'APC gaussien de la rétention nette fait **jeu égal** avec
> le stock-flux à taux locaux.
> - MAPE dép. à h = 5 : 8,74 % contre 8,68 %, Δ +0,07 pt, IC 95 %
>   [−0,03 ; +0,16]. Il bat la tendance naïve (−0,56) et nettement A3, la
>   rétention des 60 ans et plus en tendance (9,00 %).
> - Sa prévision probabiliste a un **CRPS relatif de 6,82 %**, contre 8,68 %
>   pour la prévision ponctuelle de A0.
> - Mais elle est **trop étroite** : couverture de 50 % pour un intervalle
>   nominal à 80 %, PIT en U. Elle ne porte que l'incertitude des sorties,
>   pas celle des entrées.
> - La calibration par simulation réussit ; la couverture dans l'échantillon
>   est de 91 % pour 90 % nominal.

## Question
Étape 1 du programme de l'axe 2 (décision « Programme de l'axe 2 ») :
remplacer la rétention estimée à la main (moindres carrés, k = 200) par un
modèle statistique explicite, vérifiable, avec une incertitude propagée.

## Résultat

### Banc N1, périmètre privé (inscrit à 03:58, avant le passage)
| Variante | MAPE h=5 | Δ vs tendance (IC 95 %) | Issue N1 | Δ vs A0 (IC 95 %) |
|---|---|---|---|---|
| A0 stock-flux taux locaux | 8,68 | −0,63 [−0,97 ; −0,27] | gagne | — |
| **APC** | **8,74** | −0,56 [−0,91 ; −0,20] | gagne | **+0,07 [−0,03 ; +0,16] : égalité** |
| A3 rétention 60+ en tendance | 9,00 | −0,30 [−0,67 ; +0,08] | égalité | +0,33 [+0,23 ; +0,42] |
| tendance (naïve) | 9,30 | — | — | — |

- Limite h = 1 : réussie.
- Précision nationale : réussie.
- Le banc a été passé une seule fois.

### Prévision probabiliste à h = 5 (secondaire, 2 056 départements × origines)
| | CRPS relatif (%) |
|---|---|
| **APC, 100 tirages prédictifs** | **6,82** |
| A0 (ponctuelle : CRPS = \|erreur\|) | 8,68 |
| APC, moyenne a posteriori (ponctuelle) | 8,74 |
| tendance (ponctuelle) | 9,30 |

**Couverture et calibration :**
- Couverture des intervalles prédictifs : **50 %** pour 80 % nominal, **60 %**
  pour 90 % nominal.
- PIT, histogramme en 10 classes : 594, 154, 150, 107, 122, 128, 117, 109,
  159, 416. Il est en **U** : la prévision est **sous-dispersée**, et un peu
  plus souvent trop haute que trop basse (594 contre 416 aux extrêmes).

**Lecture.**
- Le CRPS plus bas vient de ce qu'une distribution, même trop étroite, est
  mieux notée qu'un point.
- Une comparaison juste demanderait une référence ponctuelle habillée
  d'une bande naïve, par exemple la pente d'erreur reprise de
  l'observatoire. Elle n'est pas faite ici.

### Contrôles du modèle
| Contrôle | Résultat | Critère pré-écrit | Tient ? |
|---|---|---|---|
| **Calibration par simulation, θ fixé (200 jeux)** | rangs uniformes, KS p = 0,56 · 0,20 · 0,45 · 0,30 (π 60+ en T, γ, w, η à h = 5) | KS p ≥ 0,01 | oui |
| **Calibration par simulation, θ ré-estimé (40 jeux)** | KS p = 0,78 · 0,40 · 0,23 · 0,80 | KS p ≥ 0,01 | oui |
| Contrôle prédictif dans l'échantillon, couverture à 90 % de y | 90,9 à 91,8 % selon la profession | entre 80 et 98 % | oui |
| Couverture à 80 % hors échantillon, dép. à h = 5 | **50 %** | entre 70 et 90 % | **non** |
| Prédiction : couverture à 80 % entre 55 et 80 % | 50 % | — | **non** (pire que prévu) |
| Prédiction : \|Δ(APC, A0)\| < 0,3 pt | +0,07 | — | oui |
| Prédiction : l'effet cohorte apprend peu (sd post / prior > 0,7) | 0,98 (médiane, dentistes 2021) | — | oui |

### Ce que le modèle apprend (dentistes, origine 2021, mesuré)
- σ_π, l'écart-type des incréments de période, vaut 0,0009 (femmes) et
  0,006 (hommes) en log par an. La période est presque plate : la
  rétention des dentistes ne dérive pas dans la fenêtre.
- σ_γ vaut 0,014 à 0,015 en log par an de cohorte ; c'est l'a priori qui le
  dicte, puisque le rapport sd post / prior est de 0,98.
- τ_rég = 0,035 et τ_dép = 0,008 à 0,013. L'écart entre régions domine
  l'écart entre départements d'une même région. Le shrinkage A2, qui est
  hiérarchique, avait donc raison de passer par la région.
- σ_e vaut 0,64 et 0,65 : le bruit d'échantillonnage est environ 4 fois le
  binomial pur, puisque √((1 − r)/r) ≈ 0,17 pour r = 0,97. Cela capte les
  déménagements et les changements de mode d'exercice.

## Pourquoi la prévision probabiliste est trop étroite (dérivé)
- **Les entrées sont fixes.** L'APC ne modélise que la rétention des
  tranches où elle est ≤ 1. Les entrées absolues I de A0 sont reprises sans
  incertitude, et ce sont elles qui dominent l'erreur départementale (K1,
  B4, ablation).
- **θ est fixé à θ̂** (Bayes empirique) : son incertitude n'est pas
  propagée.
- **σ_π est presque nul**, donc les innovations futures de période sont
  presque nulles. Une rupture comme le cumul emploi-retraite n'est pas
  anticipée.

**Conséquence pour le programme.** L'étape 2 doit porter l'incertitude des
entrées : cohortes par composantes bayésiennes, entrées comprises. Sans
cela, aucune bande ne sera calibrée.

## How
- **Modèle.**
  - Code : [`v2/methodes/apc.py`](../../../methodes/apc.py) (classes
    `Group` et `APC`, module `apc_sorties`, `APCEstimator`).
  - Composition : `methodes_vieillissement` + `apc_sorties` +
    `methodes_entrees`.
  - Aucun fichier de `v2/jumeau/` n'est modifié.
- **Inférence.**
  - La loi a posteriori est gaussienne, avec une matrice de précision de
    500 à 700 paramètres par profession × sexe. Elle se calcule par
    Cholesky dense.
  - θ est obtenu par L-BFGS-B sur la log-vraisemblance marginale exacte.
  - log|P| est calculé analytiquement : bloc i.i.d. −2n·log t, marche
    d'ordre 1 −2(n − 1)·log σ.
- **Commandes** (depuis la racine) :
  - `PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.banc_apc`
    (≈ 8 min machine) ;
  - `… -m methodes.sbc` (≈ 7 min).
  - Sorties : `v2/methodes/out/apc_*`. Graines : 20261114.
- **Temps.** 15 s d'ajustement par profession au département. La
  projection d'un tirage reste de l'ordre de la milliseconde.

## ⚑ What could make it wrong
- **CRPS et couverture.** Les cibles de l'origine 2021 (h = 5 → 2026)
  servent aussi à la ligne MAPE. Les 2 056 points ne sont pas
  indépendants : les origines se recouvrent.
- **Variance tirée vers le haut.** Le plafond s = min(1, e^η) appliqué aux
  tirages structurels biaise légèrement leur moyenne vers le bas : −0,55 %
  au national pour les dentistes, origine 2021 (mesuré).
- **SBC partielle.** Elle utilise un seul plan d'observation (dentistes,
  femmes, 2012–2021) et 40 jeux seulement pour θ ré-estimé.
- **Tranches non modélisées.** Les tranches où la rétention nationale
  dépasse 1 (les plus jeunes) gardent la rétention de A0, sans
  incertitude.

## → What it changes
- **Verdict.** L'APC **égale** la référence en prévision ponctuelle. Il
  est **adopté comme modèle des sorties quand on veut une incertitude** ;
  A0 reste le défaut ponctuel. Il **remplace A3**, avec un levier de
  période explicite au lieu d'une pente.
- **Étape 2.** Les entrées doivent entrer dans le modèle probabiliste :
  c'est la condition d'une bande calibrée.
- **Axe 3.** CRPS et PIT sont maintenant mesurés pour un modèle
  probabiliste ; il faudra une référence naïve probabiliste pour les
  comparer à armes égales.
- **Axe 5.** σ_π et le levier `apc_sorties.periode_60plus` sont des facteurs
  à cribler.

## ? Next
| Item | Cost |
|---|---|
| Étape 2 : cohortes par composantes bayésiennes, avec des entrées probabilistes (commune ⊂ dép ⊂ rég) | ~1 j Claude |
| Référence naïve probabiliste (pente d'erreur par horizon, reprise A3 de l'observatoire) pour comparer les CRPS | ~30 min |
| Propager l'incertitude de θ (Laplace sur log θ, ou quelques tirages) et mesurer le gain de couverture | ~45 min |
| Calibration par simulation sur les 5 professions × 2 sexes, 200 jeux, θ ré-estimé | ~40 min machine |
