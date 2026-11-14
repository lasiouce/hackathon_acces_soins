---
type: derivation
date: 2026-11-14
author: axe 2
question: Comment projeter l'effectif libéral à la commune avec une bande à 80 % qui couvre environ 80 % des cas, dans chaque classe de taille ?
status: 1 promue (K, cohortes hiérarchiques + variance prédictive estimée dans la fenêtre) · 1 en attente (arbre gaussien complet) · 1 tuée (C1 tel quel à la commune)
---

# Projection communale calibrée : commune ⊂ EPCI ⊂ département ⊂ région

**Dérivé :** 2026-11-14, environ 15 minutes. Chantier « projection communale
fiable » (decisions.md).

## Problème
- **Objectif.** Une bande à 80 % qui couvre entre 75 et 85 % des cas, **dans
  chaque classe de taille** du protocole N4 (classes 3–5 et au-dessus), à
  h = 5.
  - On ne cherche pas l'étroitesse : le bruit de Poisson est irréductible.
  - En second, le P80 de |erreur| par classe, et N_min, contre le défaut
    de N4 : total départemental × part tenue, avec l'oracle du total
    départemental réel.
- **Contraintes.**
  - Recalcul compatible avec l'axe 0 : 1,02 s par scénario à la commune
    (C15).
  - Boîte blanche ; données ≤ origine.
- **Données.** CartoSanté (libéraux, au 31/12) : 16 078 communes, 5 tranches
  (< 40, 40–49, 50–54, 55–59, 60+), sans sexe.
  - IDE de 2004 à 2025, MK de 2005 à 2025, CD de 2006 à 2025.
  - C'est le fichier du protocole N4 (`data/processed/stock_commune.parquet`).
  - Table de passage commune → EPCI → département → région :
    `v2/data/processed/commune_geo.parquet` (axe 4).

## Structure
- **Une commune de N professionnels a un bruit annuel de l'ordre de √N.**
  À N = 5, l'écart-type relatif vaut ±45 % (dérivé).
  - La bande d'une petite commune est donc dominée par ce bruit, pas par
    l'incertitude des paramètres.
  - **La calibration est d'abord un problème de variance** : la moyenne
    compte peu sous N ≈ 20.
- **L'âge compte à la commune.** Une commune de 3 infirmiers de plus de
  60 ans les perd en 5 ans. Une part tenue (défaut N4) ne le voit pas ; un
  modèle de cohortes le voit.
- **Rétrécissement.** Une commune a trop peu de personnes pour estimer ses
  propres taux.
  - Sa rétention et sa part des entrées sont rétrécies vers l'EPCI, puis
    le département, la région et le national : moyenne a posteriori sous
    un a priori en pseudo-effectifs.
- **La variance prédictive a deux parties.**
  - Une part de Poisson, en αμ.
  - Une part de surdispersion, en βμ² : déménagements, chocs locaux,
    erreur du total départemental.
  - α et β se mesurent **dans la fenêtre** : on ajuste le même modèle à une
    origine o − h, on projette jusqu'à o, et l'on régresse le carré du
    résidu sur μ et μ². Aucune donnée postérieure à l'origine n'entre.

## Modèle K (une page)
Pour chaque profession, et pour chaque commune c, tranche a et année τ :

- **Vieillissement.**
  B(a, τ) = (1 − f_a)·N(a, τ−1) + f_{a−1}·N(a−1, τ−1).
  - f = (1/15, 1/10, 1/5, 1/5, 0) : la tranche « < 40 » est traitée comme
    25–39 ans, supposé.
- **Rétention.** r_{c,a} = Σ_τ N(a, τ) / Σ_τ B(a, τ), sur la fenêtre de
  6 ans.
  - Elle est rétrécie à chaque niveau ℓ : r_ℓ = (num_ℓ + k·r_parent) /
    (den_ℓ + k), avec k = 200 (comme A2), dans l'ordre région ← national,
    département ← région, EPCI ← département, commune ← EPCI.
  - s = min(1, r).
- **Flux net.** e_{c,a,τ} = N(a, τ) − s_{c,a}·B(a, τ). Au département,
  E_{d,a}(τ) = Σ_c e : on prend son niveau local (filtre de Kalman, comme
  C1), prolongé à plat.
- **Part de la commune dans les entrées du département.**
  - q_e = (S_e + k_q·π_e) / (S_d + k_q), puis
    q_c = (S_c + k_q·q_e·π_{c|e}) / (S_e + k_q·q_e) × q_e.
  - S est la somme du flux net sur la fenêtre ; π est la part du stock de
    la tranche à l'origine. On prend k_q = 20 personnes, supposé.
  - Les parts somment à 1 dans le département. Si S_d ≤ 0 : parts au
    prorata du stock.
- **Projection.** N(a, τ) = s·B(a, τ) + q_{c,a}·L_{d,a}, avec un plancher à
  0. On obtient μ_c(o + h).
- **Distribution prédictive.**
  - Var = α_h·μ + β_h·μ², mesurés dans la fenêtre.
  - Loi binomiale négative si Var > μ, Poisson sinon. Bande de P10 à P90.
- **Paramètres qu'un levier modifie.**
  - Le multiplicateur des entrées, appliqué à L_d.
  - La rétention des 60 ans et plus.
  - La régulation, qui fermera des communes dans le logit de l'étape 3.

## Ansätze
- **K : promue.** C'est le modèle ci-dessus.
- **Arbre gaussien complet (en attente).** Mêmes niveaux, mais τ_ℓ par
  vraisemblance marginale exacte (propagation sur l'arbre) et une loi a
  posteriori par commune.
  - On n'y passe que si K échoue à calibrer **à cause des moyennes**,
    c'est-à-dire si la couverture est correcte dans les grandes classes et
    biaisée dans les petites.
- **C1 tel quel à la commune (tuée).**
  - Pas de sexe, et des tranches inégales dans CartoSanté.
  - Une loi a posteriori par commune ferait des centaines de milliers de
    paramètres en factorisation dense.
  - Et la calibration par simulation de l'étape 2 met déjà en défaut ses
    variances.

## Kill tests (pré-écrits)
| Test | Résultat qui tue | Prix |
|---|---|---|
| Couverture de la bande à 80 % par classe (≥ 3–5), origines 2014 à 2020, h = 5 | hors de [75 ; 85] % dans plus de 2 classes sur 7 pour une profession | ~5 min machine |
| P80 de \|erreur\| par classe, contre le défaut de N4 sans oracle | pire dans toutes les classes ≥ 11 | inclus |
| Temps de projection à la commune (une profession, jusqu'en 2050) | > 1 s | ~1 min |

## Prédictions écrites avant le banc (supposées)
- **Couverture à 80 %** entre 75 et 85 % dans au moins 5 classes sur 7,
  pour chaque profession. Le risque est dans les grandes classes (> 100),
  où la part d'erreur du total départemental domine et où peu de communes
  servent à estimer β.
- **P80 de K** au plus égal à celui du défaut sans oracle dans les classes
  ≥ 11. Grâce à l'âge, il passe sous le défaut avec oracle dans au moins
  une classe.
