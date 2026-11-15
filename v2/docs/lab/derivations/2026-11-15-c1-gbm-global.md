---
type: derivation
date: 2026-11-15
author: session c1-gbm
question: Un modèle d'apprentissage automatique global (toutes séries à la fois) bat-il A2 en MAPE départementale à h = 5 ?
status: inscrit avant tout passage sur le banc
---

# C1-GBM : apprentissage automatique global contre A2 (inscription)

Écrit **avant** le premier passage sur le banc. Aucun réglage, aucun pilote
n'a vu une cible de test.

## Contrainte, en unité
- **Métrique :** MAPE départementale à h = 5 ans, protocole N1 (axe 3,
  `v2/validation/forecast.py`) : mêmes origines glissantes que `tab:prive`,
  mêmes cellules (n à l'origine ≥ 30), même périmètre privé central.
- **Incumbent :** A2 shrinkage hiérarchique (`axe2_shrink_hier`), 8,57 %
  (mesuré, banc axe 2).
- **Recalcul :** < 2 s par scénario dans l'outil ; non testé ici (le modèle
  n'est pas un levier, il ne peut pas en porter).

## Test d'abandon (écrit avant)
- Δ = MAPE(candidat) − MAPE(A2), poolée comme `verdict()` (moyenne des
  cellules profession × origine à poids égal).
- IC 95 % par bootstrap des départements : 2 000 tirages, graine 20261114,
  mêmes tirages pour les deux modèles (appariés), comme `methodes.banc.boot`.
- **Accepté** si la borne haute de l'IC est < 0. **Sinon rejeté.**
- Deux candidats inscrits : GBM et MLP. Chacun est jugé seul contre A2 ; on
  ne retient pas le meilleur des deux a posteriori sans le dire (deux tests :
  l'IC à 97,5 % Bonferroni est rapporté en plus).
- Par profession : Δ et IC rapportés, **à titre descriptif** ; le verdict est
  le total poolé.

## Pourquoi pas un modèle direct à h = 5
- Données : 2012 → 2026 (infirmiers 2023, kinés depuis 2017).
- Aux origines 2016 et 2017, aucune paire (origine′, origine′ + 5) n'est
  entièrement antérieure à l'origine : un modèle direct à h = 5 n'aurait
  aucune donnée d'entraînement sans fuite.
- **Choix :** modèle à un pas (h = 1), itéré jusqu'à la cible. C'est
  l'analogue appris du stock-flux.

## Modèle
- **Unité :** cellule profession × département × sexe × tranche d'âge
  (10 tranches), environ 10 000 cellules par année.
- **Base vieillie** (sans apprentissage) : b = 0,8 n(a) + 0,2 n(a − 1), la
  tranche ouverte 65+ garde tout son stock.
- **Cible :** croissance relative, pas niveau. y = (n(a, t+1) − b) / N(dép, t),
  la contribution de la cellule à la croissance du département. La somme des
  cellules donne la croissance relative du département.
- **Variables explicatives, toutes à l'année t ≤ origine :**
  - profession, sexe, tranche, région (catégorielles : effets fixes de région) ;
  - log N(dép, t), part de la cellule, part de la tranche voisine ;
  - retards de la cible (t − 1, t − 2) et taux bruts n(a, t)/b(t − 1) ;
  - croissance relative du département à 1, 2 et 3 ans ;
  - croissance nationale de la profession à 1 an ;
  - part des 60 ans et plus et des moins de 35 ans de l'effectif du département ;
  - population (log), part des 60 ans et plus de la population, densité pour
    100 000 habitants (INSEE, `data/processed/population.parquet`, 2018+ ;
    manquant avant 2018, traité nativement).
- **Itération :** après l'origine, l'état par âge est mis à jour par le modèle
  lui-même ; les variables de population restent **figées à l'origine**
  (pas de projection de population venue du futur).
- **GBM :** `HistGradientBoostingRegressor` (scikit-learn), réglages fixés a
  priori, **aucun réglage sur le banc** : 300 itérations, taux 0,05, 15
  feuilles, 50 observations par feuille au minimum, L2 = 1, sans arrêt
  précoce. Pondération : 1 par département × année (chaque cellule pèse
  1 / nombre de cellules du département), pour coller à la MAPE.
- **MLP (option) :** `MLPRegressor` (32, 16), ReLU, α = 1e-3, arrêt précoce
  sur 10 % des lignes d'entraînement (toutes antérieures à l'origine),
  variables standardisées, catégorielles en indicatrices, manquants à 0 avec
  indicatrice. Graine fixe.

## Contrôle de fuite (explicite, dans le code)
1. `fit` ne reçoit que `t[year ≤ origine]` (le banc filtre ; le code le
   vérifie par assertion).
2. Test de perturbation : on remplace toutes les données d'années > origine
   (stock et population) par du bruit ; les prédictions doivent être
   identiques au bit près.
3. Les lignes d'entraînement ont toutes une cible d'année ≤ origine (assertion).

## Prédiction (avant de lancer)
- Probable : **rejet**, égalité avec A2. Taille d'échantillon : ~10 000
  cellules × ≤ 13 années, mais seulement ~100 départements × 5 professions
  de séries indépendantes, et 2 à 3 « régimes » temporels par origine.
- Ce qui me surprendrait : Δ < −0,3 point (IC strictement négatif).
