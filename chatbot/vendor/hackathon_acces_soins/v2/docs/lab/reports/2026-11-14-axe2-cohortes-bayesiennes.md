---
type: analysis
date: 2026-11-14
author: axe 2
question: Des cohortes par composantes en bayésien hiérarchique, entrées comprises, prévoient-elles mieux que le stock-flux à taux locaux, avec une bande calibrée ?
headline: "Cohortes bayésiennes (APC des sorties + entrées en niveau local × parts hiérarchiques) : MAPE dép. h=5 7,73 % contre 8,68 % (Δ −0,95 pt, IC 95 % [−1,51 ; −0,47]) ; bande à 80 % couvrant 77,6 % sur toutes les origines (73,5 % sur la cellule N6, juste sous [75 ; 85]) ; CRPS à égalité avec la naïve probabiliste ; propager θ (Laplace) n'apporte rien ; calibration par simulation : rétention 30/30, niveau national des entrées 0/10 (loi a posteriori trop étroite)"
status: fait (étape 2 du programme de l'axe 2), calibration par simulation comprise
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 2, étape 2
sources: [DREES RPPS 2012–2026 × secteur (axe 4, périmètre privé), data/processed/stock.parquet (2026-07-02)]
tags: [axe2, cohortes, bayésien, entrées, backtest, N1, N6, CRPS, PIT, SBC]
---

# Étape 2 : cohortes par composantes en bayésien hiérarchique, entrées comprises

> **Headline :**
> - **N1.** Le modèle des cohortes bayésien **bat le stock-flux à taux
>   locaux** en prévision ponctuelle : 7,73 % contre 8,68 % de MAPE
>   départementale à h = 5, Δ −0,95 pt, IC 95 % [−1,51 ; −0,47].
>   - Le modèle se compose de l'APC des sorties (étape 1), plus des entrées
>     en niveau local national × des parts départementales hiérarchiques.
>   - C'est le **premier gain de l'axe 2 qui dépasse 0,1 point**.
>   - Il tient sans les deux cellules vues par le pilote : 7,52 % contre
>     8,52 %.
> - **N6.** Sa bande à 80 % couvre **77,6 %** sur toutes les origines.
>   - Sur la seule cellule jugeable par N6 (origine 2021, SF, CD, PH), elle
>     couvre 73,5 %, juste sous [75 ; 85] %.
>   - Son CRPS est à **égalité** avec la meilleure naïve probabiliste.
> - **Propager θ** par Laplace ne change rien : 76,0 % contre 77,6 %.

## Question
Étape 2 du programme : à l'étape 1, la bande de l'APC couvrait 50 % au lieu
de 80 %, parce que les entrées étaient fixes. On rend les entrées
probabilistes et hiérarchiques ([dérivation](../derivations/2026-11-14-axe2-cohortes-bayesiennes.md)).

## Résultat

### N1, MAPE dép. h = 5, périmètre privé (inscrit à 04:41, avant le banc)
| Variante | MAPE | Δ vs A0 (IC 95 %) | Issue N1 (vs tendance) |
|---|---|---|---|
| A0 stock-flux taux locaux | 8,68 | — | gagne |
| APC seule (étape 1) | 8,74 | +0,07 [−0,03 ; +0,16] | gagne |
| **C1 cohortes, θ fixé** | **7,73** | **−0,95 [−1,51 ; −0,47]** | gagne |
| **C2 cohortes, θ propagé** | **7,73** | −0,95 [−1,51 ; −0,47] | gagne |
| tendance / persistance (naïves) | 9,30 / 9,92 | — | — |

- C1 et C2 ont la même moyenne a posteriori. Ils ne diffèrent que par la
  dispersion.

**Stabilité entre origines.** C1 bat A0 dans **17 cellules profession ×
origine sur 22**.

| Δ C1 − A0 (pts) | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|
| CD | −3,01 | −1,82 | −0,52 | −0,03 | −0,55 | +0,43 |
| IDE lib. | −0,71 | −0,80 | −1,38 | — | — | — |
| MK | — | — | — | — | — | +0,04 |
| PH | −1,00 | −0,74 | −0,67 | +0,19 | +0,47 | +1,24 |
| SF | −1,79 | −2,59 | −3,45 | −2,07 | −0,87 | −1,17 |

- ⚑ **Le gain décroît pour les origines récentes**, pour CD et PH.
- Le niveau local suit les entrées récentes. Il aide quand les entrées
  montent (SF, IDE) et coûte quand elles se retournent.

**Biais national moyen à h = 5 (%) :**

| | CD | IDE lib. | MK | PH | SF |
|---|---|---|---|---|---|
| A0 | −4,58 | +5,79 | −1,66 | −0,15 | **+7,64** |
| C1 | −5,06 | +4,69 | −1,72 | −0,39 | **+3,04** |

### N6, prévision probabiliste (protocole gelé)
- N6 exige au moins 20 erreurs passées pour construire la référence naïve.
  Seule l'**origine 2021** est donc jugeable à h = 5, pour **SF, CD et
  PH** : 279 départements.
- Les kinés et les infirmiers sont exclus.

| | CRPS (log N) | Δ vs persistance probabiliste (IC 95 %) | Couverture 80 % ([75 ; 85]) | Couverture 50 % ([44 ; 56]) |
|---|---|---|---|---|
| persistance probabiliste (meilleure naïve) | 0,0623 | — | — | — |
| A0 + erreurs passées | 0,0732 | +0,011 [+0,005 ; +0,016] : **perd** | 54,5 % ✗ | 30,5 % ✗ |
| APC (étape 1) | 0,0665 | +0,004 [+0,000 ; +0,009] : **perd** | 54,1 % ✗ | 32,3 % ✗ |
| **C1** | 0,0654 | +0,003 [−0,001 ; +0,007] : **égalité** | **73,5 %** ✗ (de 1,5 pt) | **45,9 %** ✓ |
| C2 | 0,0654 | +0,003 [−0,001 ; +0,007] : égalité | 71,7 % ✗ | 47,7 % ✓ |

**Hors protocole : toutes les origines (2 056 départements × origines).**
- C1 couvre **77,6 %** à 80 % et **50,0 %** à 50 % : les deux sont dans les
  bandes de N6.
- C2 couvre 76,0 % et 50,3 %.
- Le PIT de C1 (10 classes) vaut 171, 196, 207, 197, 226, 228, 197, 181,
  172, 281 : presque plat. Le PIT de l'APC seule était en U, avec 594 et
  395 aux extrêmes.

**Couverture à 80 % de C1 par profession (toutes origines) :**

| CD | IDE lib. | MK | PH | SF |
|---|---|---|---|---|
| 68,7 % | 81,0 % | 69,3 % | 86,8 % | 76,6 % |

- La bande est un peu trop étroite pour les dentistes et les kinés, et un
  peu trop large pour les pharmaciens.

### Verdict par profession (C1)
| Profession | N1 : MAPE vs A0 (IC 95 %) | N6 : CRPS vs naïve | Couverture 80 % (N6) |
|---|---|---|---|
| Dentistes | **bat**, −0,92 [−1,45 ; −0,44] | égale | 65 % |
| Infirmiers libéraux | **bat**, −0,96 [−1,48 ; −0,43] | non jugeable | — |
| Kinés | **égale**, +0,04 [−1,39 ; +1,19] (une seule origine) | non jugeable | — |
| Pharmaciens | **égale**, −0,09 [−0,38 ; +0,21] | **échoue** | 73 % |
| Sages-femmes | **bat**, −1,99 [−3,83 ; −0,45] | égale | 85 % |

### Propagation de θ (C2 contre C1)
- La couverture à 80 % passe de 77,6 % à 76,0 % sur toutes les origines,
  et de 73,5 % à 71,7 % sur la cellule N6. Le CRPS est identique.
- **Pas de gain.** La prédiction écrite (+0 à +5 points) est falsifiée.
- La dispersion vient des innovations futures (niveau national, bruit
  annuel), pas de l'incertitude sur θ. C2 coûte environ 2 fois plus cher
  à ajuster, donc **C1 est retenu**.

### Prédictions écrites avant le banc
| Prédiction | Observé | Tient ? |
|---|---|---|
| Couverture à 80 % de C1 entre 60 et 80 % | 77,6 % (toutes origines), 73,5 % (N6) | oui |
| C2 de 0 à 5 points au-dessus de C1 | −1,6 et −1,8 point | **non** |
| \|Δ MAPE(C, A0)\| < 0,3 pt | −0,95 | **non** (gain bien plus grand) |
| C bat la naïve probabiliste en CRPS chez ≥ 2 professions sur 3 | 0 sur 3 (2 égalités, 1 échec) | **non** |

### Calibration par simulation (5 professions × 2 sexes × 200 jeux, θ ré-estimé) {#mise-à-jour-sbc}
- **Plan.** On garde le plan d'observation réel (origine 2021), on tire les
  effets dans l'a priori(θ̂), on simule les données, on ré-estime θ, puis on
  relève le rang de la vérité parmi 99 tirages.
  - Critère N6 : χ² à 19 ddl, p ≥ 0,01/6 (Bonferroni).
  - 2 000 jeux, environ 3 h 30 machine.

| Quantité | Échecs (cellules profession × sexe) |
|---|---|
| π(≥ 60 ans, dernière année), APC | **0 / 10** |
| w (département médian), APC | **0 / 10** |
| η à h = 5, APC | **0 / 10** |
| ζ (part du département médian) | 1 / 10 (kinés H) |
| δ (écart régional de la part) | 3 / 10 (kinés H, pharmaciens H, SF H) |
| **L_T, niveau national des entrées** | **10 / 10**, rangs en U |

**Lecture.**
- **Les sorties (APC) sont correctement inférées**, même avec θ
  ré-estimé.
- **Le niveau national des entrées ne l'est pas.** Sa loi a posteriori,
  conditionnelle à σ̂_u et σ̂_v estimés sur une série de 9 à 14 points, est
  trop étroite.
  - Le test est plus dur que la production : une seule série au lieu de
    la mise en commun par profession. Le défaut est réel quand même.
- **Les écarts régionaux échouent dans les petites cellules** (hommes
  SF, MK, PH). Le Bayes empirique y estime τ_r ≈ 0 avec 13 régions, et la
  loi a posteriori s'effondre. C'est le défaut connu de l'estimation par
  maximum de vraisemblance des composantes de variance.
- **Conséquence.**
  - La bande départementale proche du nominal (77,6 %) ne vient pas d'une
    inférence correcte de chaque composante : le bruit annuel par
    département y domine.
  - **Une bande nationale de C1 n'est pas publiable** en l'état.
  - La règle pré-écrite s'applique (dérivation, « Ansätze ») : la
    calibration par simulation échoue, donc le **traitement bayésien
    complet de σ_u, σ_v et τ_r est rouvert**, avec des a priori
    demi-normaux écrits et un MCMC ou une intégration sur grille.
- Mondes N5 : non disponibles au moment du calcul.

## Ce qui produit le gain (dérivé, puis mesuré sur le biais)
1. **Le niveau national des entrées suit les années récentes** : niveau
   local, L_{T|T}. A0 prend la moyenne de toute la fenêtre.
   - Les SF ont des entrées en baisse depuis 2018 (année blanche).
   - Leur biais national passe de +7,6 à +3,0 %.
2. **Les entrées sont réparties au prorata du stock**, rétréci par région
   et par département (τ_d et τ_r estimés presque nuls pour les grandes
   tranches). A0 garde le flux de chaque département, qui est bruité.
   - C'est la conclusion de C5 (part du stock, r = 0,996) devenue modèle.

## How
- **Code.**
  - [`v2/methodes/cohortes.py`](../../../methodes/cohortes.py) : `Level`
    (niveau local, Kalman), `Shares` (parts hiérarchiques), `Cohortes`,
    module `cohortes`, `CohortesEstimator` (C1), `CohortesLaplace` (C2).
  - Composition : `methodes_vieillissement` + `cohortes`. Aucun fichier de
    `v2/jumeau/` n'est modifié.
- **Banc.** `PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.banc_cohortes`.
  - 126 ajustements, environ 65 min machine.
  - Sorties : `v2/methodes/out/coh_*`.
- **Calibration par simulation.** `… -m methodes.sbc2 200`, environ
  5 h 30 machine, en arrière-plan avec progression k/N.
- **Temps.** L'ajustement prend 6 à 20 s par profession (calibrage).
  Les 200 tirages à h = 5 prennent environ 0,4 s.

## ⚑ What could make it wrong
- **Pilote avant inscription.** Le pilote a vu les cibles 2026 (origine
  2021) des dentistes et des sages-femmes.
  - Sans ces deux cellules, le gain tient : 7,52 % contre 8,52 %.
- **Dépendance à l'origine.** Le gain diminue sur les origines récentes
  (CD, PH). Pour les entrées qui se retournent, le niveau local réagit
  avec retard.
- **N6 est très mince.** Une seule origine, trois professions. La
  couverture « toutes origines » est hors protocole.
- **Calibration par simulation.** Le niveau national des entrées échoue (10/10)
  et les écarts régionaux échouent dans 3 petites cellules. Seule la bande
  départementale est utilisable, avec sa couverture mesurée.
- **Corrélation entre origines.** Le bootstrap par département l'ignore :
  l'IC est probablement trop étroit (⚑ de N1).
- **Kinés.** Une seule origine, IC [−1,39 ; +1,19] : rien n'est établi.

## → What it changes
- **C1 devient la variante par défaut proposée pour la prévision** et pour
  les bandes. A0 reste la référence.
  - Le dépôt 2027–2030 (test hors échantillon propre) est la prochaine
    étape avant de l'annoncer.
- **Étape 3 (logit d'installation).** La répartition au prorata du stock
  est la base à battre. La régulation déplacera les parts.
- **Axe 5.** σ_u, σ_v (niveau des entrées) et τ_r, τ_d sont des facteurs à
  cribler.

## ? Next
| Item | Cost |
|---|---|
| ~~Dépôt de prévisions 2027–2030 de C1 et A0~~ fait (`v2/validation/depot/`, empreintes dans decisions.md) | — |
| Traitement bayésien complet de σ_u, σ_v, τ_r (a priori demi-normaux, grille ou MCMC) puis nouvelle calibration par simulation | ~2 h Claude + ~4 h machine |
| Niveau local amorti (tendance amortie) pour corriger le retard sur les entrées qui se retournent, à inscrire avant | ~1 h |
| Grain EPCI ou bassin de vie pour IDE, MK et PH, protocole N4 (π_commune dans le département) | ~3 h |
| Générateur N5 (axe 3) puis calibration par simulation sur les mondes M3 | ~1 h axe 3 + ~1 h |
