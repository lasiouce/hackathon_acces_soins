---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: Projeter le recours 2016 → 2025 par la seule structure d'âge (M1) bat-il la persistance du recours par habitant, et un GBM sur covariables ouvertes bat-il M1 ?
headline: "Protocole pré-enregistré, gelé avant tout calcul : MAPE départementale de la patientèle 2025 depuis l'origine 2016 (h = 9), Δ = MAPE(M1) − MAPE(persistance), IC 98,75 % par bootstrap des départements ; H-B1 retenue si M1 gagne pour ≥ 3 professions sur 4 (pharmaciens absents du jeu) ; le GBM n'entre que si la borne haute de l'IC de Δ(GBM − M1) est < 0"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B1 (dérivation du besoin, §6 M1) ; test P-B5 (§8) ; candidat ML (décision « passe de littérature ; ML seulement comme candidat au backtest »)
sources: [patientèle des PS libéraux (CNAM, data.ameli.fr, ODbL) 2016–2025, Insee estimations de population 2016 et 2025, poids APL DREES 2024, Open DAMIR 2016]
tags: [validation, besoin, backtest, GBM, pre-registration, P-B5]
---

# P-B5 — backtest du recours par la structure d'âge (protocole pré-enregistré)

> **Headline :** gelé avant tout calcul. La référence naïve est la
> persistance du recours par habitant. Le GBM est jugé par la même règle que
> C1-GBM : il doit battre M1 avec un IC qui exclut 0.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Hypothèse
H-B1 : projeter le recours de 2016 à 2025 par la seule structure d'âge bat
la persistance du recours par habitant (MAPE départementale), pour au moins 3
professions.

**Écart à la dérivation, déclaré ici.** La dérivation dit « 3 sur 5 ». La
patientèle, seule série départementale vérifiée, n'a pas de pharmaciens (s).
Le test porte donc sur **4** professions (IDE, MK, CD, SF), et la barre reste
**3**. Aucune série d'actes départementale n'existe en données ouvertes
(exploration §1) : la mention « actes si disponibles » est sans objet.

## Données (jeu, millésime, grain)
- **Recours** `R(p,d,t)` : patientèle (patients uniques), département,
  **2016** (origine), **2021** et **2025** (cibles) (s).
- **Population** `pop(d,t,a,s)` : Insee, estimations de population au
  1ᵉʳ janvier, département × sexe × âge quinquennal, 2016, 2021 et 2025
  (millésime le plus récent à la date du passage, inscrit au rapport). Le
  backtest est **conditionnel à la population observée**, comme la
  projection l'est à Omphale.
- **Profil d'âge** : P1 (poids APL DREES 2024, DCIR 2020–2022) pour le
  passage principal. P2 (Open DAMIR **2016**, national, décennal) en
  sensibilité, sans regard en avant.

## Prédicteurs (cible 2025 depuis 2016, h = 9)
- **Persistance** (référence naïve) :
  `R̂_pers(d,2025) = R(d,2016) · pop(d,2025) / pop(d,2016)`.
- **M1** : `R̂_M1(d,2025) = R(d,2016) · B₁(d,2025) / B₁(d,2016)`, avec
  `B₁ = Σ pop · ω`.
- **GBM (candidat ML)** : il prédit `log[R(d,2025)/R̂_M1(d,2025)]`, une
  correction de M1 ; la prédiction est `R̂_GBM = R̂_M1 · exp(ŷ)`.
  - Covariables ouvertes, toutes mesurées en 2016 ou dérivées de la
    population, figées ici :
    - log du recours par habitant ;
    - parts des 0–14, 15–59, 60–74 et 75 ans et plus ;
    - `log B₁(2025)/B₁(2016)` ;
    - log de la densité libérale de la profession ;
    - log de la densité des trois autres ;
    - part de la population en communes denses ou intermédiaires (grille
      de densité Insee 2016) ;
    - indicatrice DROM.
  - Apprentissage et évaluation en validation croisée « une région laissée
    de côté » (13 plis). Chaque département est prédit par un modèle qui ne
    l'a pas vu, ni aucun département de sa région.
  - Hyperparamètres **fixés, non réglés** : `HistGradientBoostingRegressor`
    (scikit-learn), `max_iter=200`, `learning_rate=0.05`, `max_depth=3`,
    `min_samples_leaf=10`, `random_state=20261115`. Un GBM par profession.

## Statistique
`MAPE_k(p) = moyenne_d |R̂_k(d,2025) − R(d,2025)| / R(d,2025)`, en points.
- `Δ₁(p) = MAPE_M1 − MAPE_pers` ;
- `Δ_GBM(p) = MAPE_GBM − MAPE_M1`.

## IC
Bootstrap des départements : on tire des départements entiers avec remise,
puis on recalcule les MAPE sur les prédictions déjà faites (le GBM n'est pas
réentraîné). B = 2 000, graine 20261115, IC percentile.

## Multiplicité
Bonferroni sur les **4 professions** : IC à **98,75 %**, pour `Δ₁` comme
pour `Δ_GBM`.

## Seuils de décision
- **Par profession** : M1 **gagne** si la borne haute de l'IC de `Δ₁` est
  < 0 ; il **perd** si `Δ₁ ≥ 0` (valeur ponctuelle) ; sinon **égalité**.
- **H-B1 retenue** si M1 gagne pour ≥ 3 professions sur 4 ; **rejetée** si
  M1 perd pour ≥ 2 professions sur 4 ; sinon « non tranchée ».
- **GBM** : il **entre** pour la profession seulement si la borne haute de
  l'IC de `Δ_GBM` est < 0. Sinon il reste un diagnostic au registre, jamais
  un estimateur servi. C'est la règle de C1-GBM.

## Limite h → 0 (contrôle)
Cible 2021 depuis 2016 (h = 5) : on calcule les mêmes statistiques. Elles
sont rapportées et ne décident pas. Si M1 perd à h = 5 et gagne à h = 9, le
verdict le dit.

## Placebo
Aucun.

## Rapporté, non décisif
- sensibilité au profil P2 (DAMIR 2016) ;
- MAPE pondérée par la population ;
- exclusion des départements 75, 92, 93, 94.

## ⚑ Menaces écrites
- **Regard en avant dans le profil.** Les poids P1 sont estimés sur
  2020–2022, à l'intérieur de la fenêtre 2016 → 2025. P2 (DAMIR 2016) est la
  sensibilité sans fuite. Si les deux verdicts diffèrent, H-B1 est déclarée
  « dépendante du profil ».
- **Profil d'actes, recours en patients.** Les poids sont des consommations
  (actes ou montants). La cible compte des patients uniques : l'effet de
  l'âge sur le nombre de patients est plus faible que sur les actes, ce qui
  défavorise M1.
- **Département d'exercice ou de résidence** : voir P-B2. Le descriptif est
  lu avant le passage ; le protocole ne change pas selon la réponse.
- **Révisions de la patientèle.** Le millésime téléchargé est inscrit au
  passage. Une révision ultérieure ne relance pas le test.
- **COVID.** 2020–2021 perturbent le recours ; la cible principale, 2025, est
  postérieure, mais pas la cible de contrôle, 2021.
- **101 départements.** La validation croisée du GBM n'a que ~93 points
  d'apprentissage par pli : l'a priori est défavorable au GBM (comme pour
  C1-GBM).

## Règles de gel
Mêmes règles que P-B1.
