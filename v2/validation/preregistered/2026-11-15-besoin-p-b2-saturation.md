---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: Le recours standardisé par l'âge atteint-il un plateau quand l'accessibilité augmente (M2b, saturation), ou suit-il l'offre sans plateau ?
headline: "Protocole pré-enregistré, gelé avant tout croisement recours × offre : spline linéaire de log R_std sur log densité aux quintiles (départements, patientèle 2023–2025) ; M2b vit si β_Q5 < ½ β_Q1 (IC 98,75 %, bootstrap des départements) et si la saturation gagne de ΔAIC ≥ 2 ; placebo densité des autres professions"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B2 (dérivation du besoin, §6 M2b) ; test d'abandon P-B2 (§8)
sources: [patientèle des PS libéraux (CNAM, data.ameli.fr, ODbL) 2016–2025, effectifs libéraux du jumeau, Insee estimations de population, poids APL DREES 2024]
tags: [validation, besoin, saturation, pre-registration, P-B2]
---

# P-B2 — forme du recours standardisé contre l'accessibilité (protocole pré-enregistré)

> **Headline :** gelé **avant** que le recours ne soit croisé avec l'offre.
> A priori défavorable (passe de littérature) : on s'attend à ce que P-B2 tue
> M2b. M2a (AREA) n'est pas jugé ici.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Hypothèse
H-B2 : il existe un plateau. L'élasticité du recours standardisé à
l'accessibilité dans le quintile le mieux doté est inférieure à la moitié de
celle du quintile le moins doté.

## Données (jeu, millésime, grain)
- **Recours** `R(p,d,t)` : patientèle des professionnels de santé libéraux
  (CNAM, data.ameli.fr, ODbL), **patients uniques** par profession et
  département, années **2023, 2024, 2025** (s). Professions : IDE, MK, CD,
  SF. **Pas de pharmaciens** (absents du jeu, (s)) : M2 ne s'applique pas à
  eux (dérivation §6).
- **Population** `pop(d,t,a,s)` : Insee, estimations de population au
  1ᵉʳ janvier par département, sexe et âge quinquennal, mêmes années
  (millésime le plus récent à la date du passage, inscrit au rapport).
- **Besoin M1** `B₁(p,d,t)` : population pondérée par les poids APL DREES
  2024 (P1 de P-B1).
- **Offre** `N(p,d,t)` : effectifs libéraux observés du jumeau (état
  historique, pas une projection), même profession, mêmes années.
- **Départements** : métropole et DROM où les trois sources existent ; la
  liste est fixée par la jointure.

## Variables
- `R_std(p,d) = moyenne_{t∈2023–2025} [R(p,d,t) / B₁(p,d,t)]`, normalisé à 1
  sur la France entière ; variable `y = log R_std`.
- Accessibilité : `A(p,d) = moyenne_t [100 000 · N(p,d,t) / B₁(p,d,t)]`
  (densité standardisée) ; variable `x = log A`.
- Moyenne sur trois ans pour réduire le bruit de comptage ; aucune autre
  covariable dans le modèle principal (l'âge est déjà dans `B₁`).

## Statistiques
1. **Spline linéaire** de `y` sur `x`, nœuds aux quintiles empiriques de `x`
   (5 segments), MCO non pondéré. `β_Q1` et `β_Q5` sont les pentes du premier
   et du dernier segment (élasticités).
   Statistique : `δ = β_Q5 − 0,5 · β_Q1`.
2. **Formes concurrentes**, ajustées sur `R_std` :
   - saturation (Michaelis–Menten) : `R_std = ρ_max · A / (A + K)`, moindres
     carrés non linéaires, départ `ρ_max = max R_std`, `K = médiane A` ;
   - sans plateau : `R_std = α + β · log A`, MCO.
   Statistique : `ΔAIC = AIC_log − AIC_sat` (erreurs gaussiennes, même n).

## Seuil de décision (par profession)
- **M2b vit** si les deux conditions tiennent :
  - la borne haute de l'IC à 98,75 % de `δ` est < 0 ;
  - `ΔAIC ≥ 2` (la saturation gagne).
- **M2b tombe** sinon :
  - `δ` non distinguable de 0 ou positif, ou `ΔAIC < 2` ;
  - le plafond `ρ_max` n'est alors pas identifié pour la profession.
- **Cas dégénéré** : si l'IC de `β_Q1` contient 0 ou est négatif, le recours
  ne suit pas l'offre en bas de distribution. Il n'y a pas de rationnement
  mesurable : M2b tombe, avec la mention « pas de pente à saturer ».
- Le NLS qui ne converge pas en 200 itérations compte comme une défaite de la
  saturation (`ΔAIC` = −∞), pas comme une donnée manquante.

## IC
Bootstrap non paramétrique **des départements** (tirage avec remise de
départements entiers ; nœuds de la spline recalculés à chaque tirage),
B = 2 000, graine 20261115, IC percentile.

## Multiplicité
Bonferroni sur les **4 professions** de ce protocole : α = 0,05 / 4, soit des
IC à **98,75 %**. Le critère AIC n'est pas un test et n'est pas corrigé.

## Référence naïve
La forme sans plateau (`α + β log A`) est la référence : la saturation doit
la battre.

## Placebo (attractivité générale)
Même spline où `x` est remplacé par le log de la densité standardisée des
**trois autres** professions de la patientèle (somme de leurs effectifs).
Si `β_Q1,placebo` a le même signe que `β_Q1` et `|β_Q1,placebo| ≥ ½ |β_Q1|`,
le verdict reçoit la mention « **non attribuable** » : la densité mesure
alors l'attractivité du territoire, pas l'accès à la profession (comme en
N9). Un M2b « vivant » mais non attribuable n'entre pas en service.

## Rapporté, non décisif
- années 2016–2018 seules (stabilité) ;
- variante frontière (SFA demi-normale sur `y`), `u` moyen par quintile ;
- exclusion de Paris et de la petite couronne (75, 92, 93, 94), où la fuite
  de patientèle est la plus probable ;
- agrégation aux 13 régions (sans test : 13 points).

## ⚑ Menaces écrites
- **Département d'exercice ou de résidence.** Le département de la
  patientèle est supposé être celui **d'exercice** ; le descriptif du jeu n'a
  pas été lu (ledger). S'il s'agit du département d'exercice, des patients
  d'un département peu doté soignés dans un voisin bien doté gonflent le
  recours du voisin : la pente est biaisée **vers le haut** dans le quintile
  supérieur, donc contre la saturation. Le descriptif est lu **avant** le
  passage ; quelle que soit la réponse, le protocole s'applique tel quel, et
  la réponse est écrite dans le verdict.
- **Marge extensive.** Des patients uniques, pas des actes : un plateau en
  patients peut cacher une croissance en actes par patient.
- **Double compte.** Un patient vu dans deux départements compte deux fois.
- **Causalité inverse.** Les professionnels s'installent là où le recours est
  fort (R1 non garantie, dérivation §2.2). Le test décrit une forme, il
  n'identifie pas un effet causal.
- **101 points, 20 par quintile.** Les pentes extrêmes sont imprécises ;
  l'IC le dit, et un IC large tue M2b (la charge de la preuve est sur la
  saturation).

## Règles de gel
Mêmes règles que P-B1 : copie figée, empreinte au rapport
`2026-11-15-besoin-axe3-protocoles`, calcul après le jeton, écarts en
amendement daté.
