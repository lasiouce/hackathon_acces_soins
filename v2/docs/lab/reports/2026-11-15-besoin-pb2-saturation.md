---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: Le recours standardisé plafonne-t-il quand l'accessibilité croît (saturation), ce qui identifierait le niveau du besoin (M2b) ?
headline: "P-B2 : M2b (saturation) tombe pour les 4 professions ; borne haute de l'IC à 98,75 % de δ ≥ 0 partout (IDE +1,63, MK +1,10, CD +0,37, SF +0,82) ; ΔAIC ≥ 2 pour les seuls kinés (23,1), mais pente du premier quintile non distinguable de 0 et placebo non attribuable"
status: passage fait ; M2b retiré du service
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B2 ; protocole gelé P-B2 (v2/validation/preregistered/2026-11-15-besoin-p-b2-saturation.md) et amendement A1
sources: [patientèle et démographie data.ameli.fr (ODbL), Omphale 2022 (Insee), poids APL DREES, effectifs du jumeau]
tags: [besoin, validation, P-B2]
---

# P-B2 — saturation du recours standardisé contre l'accessibilité (passage)

> **Headline :** aucun plateau du recours standardisé n'est établi. **M2b tombe pour les quatre professions**
> (IDE, MK, CD, SF) : l'IC à 98,75 % de `δ = β_Q5 − ½ β_Q1` contient 0 partout. Pour IDE, MK et SF, la pente du
> premier quintile n'est même pas distinguable de 0 (« pas de pente à saturer »). Pour MK et CD, le placebo
> (densité des trois autres professions) a une pente de même signe et au moins moitié aussi forte : la densité y
> mesure l'attractivité du territoire autant que l'accès. Conforme à l'a priori de la littérature.

## Écarts au protocole et à A1, écrits le 2026-11-15 avant tout calcul
Protocole gelé (RFC 3161, 02:17:19 UTC) ; amendement A1 gelé et commité sur `claude/besoin-derivation-4a2fe6`
(`f5267ad`), fusionné ici avant ce passage. Aucun seuil, aucune règle n'est touché.

1. **Population.** Le protocole veut les estimations Insee au 1ᵉʳ janvier par département, sexe et âge quinquennal.
   Elles ne sont pas sur disque ; on utilise **Omphale 2022, scénario central**, années 2023–2025 (projection
   depuis 2018, pas une estimation). Même source que M1 et P-B1.
2. **Offre des infirmiers.** La table de secteur du jumeau n'a les infirmiers que jusqu'en **2023** et sans Mayotte :
   `A` est la moyenne sur les années d'offre disponibles parmi 2023–2025 (IDE : 2023 seule) ; `R_std` garde les
   trois années.
3. **Stabilité « 2016–2018 » (non décisive).** Omphale commence en 2018 : année **2018 seule**.
4. **Descriptif de la patientèle.** Lecture tentée le 2026-11-15 (page « information » du jeu `patientele` sur
   data.ameli.fr) : la page ne donne que le titre (« Professionnels de santé libéraux : patientèle par territoire »),
   aucune définition du département ni de la file active. Le « département d'exercice » reste une **déduction**.
5. **Placebo.** « Densité standardisée des trois autres professions (somme de leurs effectifs) » : numérateur = somme
   des effectifs du jumeau des trois autres professions (moyenne des mêmes années), dénominateur = `B₁` de la
   profession testée, pour que seul le numérateur change.
6. **NLS.** `scipy.optimize.curve_fit`, `maxfev = 200` (200 évaluations de la fonction, la borne d'arrêt
   disponible) ; échec ⇒ ΔAIC = −∞, comme gelé.
7. **AIC.** `n · log(RSS/n) + 2k`, k = 2 pour les deux formes (la variance commune s'annule dans ΔAIC).
8. **Spline.** Base `1, x, (x − k_j)₊` (j = 1…4, nœuds aux quintiles 20/40/60/80 % de x) ; `β_Q1` = pente du
   premier segment, `β_Q5` = somme des pentes. Bootstrap : nœuds recalculés sur chaque tirage, IC percentile
   bilatéral à 98,75 % pour `δ` et `β_Q1`.
9. **Cellules masquées** (secret statistique) : un département sans file active une année sort de la jointure pour
   la profession (le nombre est rapporté).
10. **SFA (non décisive)** : vraisemblance demi-normale, Nelder–Mead, `E[u|ε]` de Jondrow et coll. (1982).
11. **Régions (non décisif)** : sommes de R, B₁ et N par région, mêmes formes concurrentes, ΔAIC seulement.

## Question
H-B2 ([dérivation §6, M2](../derivations/2026-11-15-besoin-derivation.md)) : le recours standardisé plafonne quand
l'accessibilité croît. Si oui, le plateau `ρ_max` identifie le niveau du besoin (M2b) et le besoin non satisfait.

## Result
Décisif (2023–2025, départements ; seuils gelés). Nombres **mesurés** ; seuils supposés au gel.

| Profession | n | β_Q1 [IC 98,75 %] | β_Q5 | δ [IC 98,75 %] | ΔAIC (log − sat) | placebo β_Q1 | Verdict |
|---|---:|---|---:|---|---:|---:|---|
| infirmiers | 100 | −0,60 [−1,67 ; 0,45] | −0,04 | 0,26 [−1,66 ; 1,63] | −0,06 | −0,05 | **tombe** (pas de pente à saturer) |
| kinés | 101 | 0,93 [−0,25 ; 1,97] | 0,83 | 0,36 [−0,33 ; 1,10] | **23,11** | 0,72 | **tombe** (pas de pente à saturer ; non attribuable) |
| dentistes | 101 | 1,09 [0,29 ; 1,50] | 0,26 | −0,29 [−0,55 ; 0,37] | 1,94 | 0,89 | **tombe** (non attribuable) |
| sages-femmes | 101 | 1,02 [−0,12 ; 1,59] | −0,06 | −0,57 [−1,48 ; 0,82] | 0,87 | 0,39 | **tombe** (pas de pente à saturer) |

Formes ajustées (point) : MK `ρ_max` = 5,99, K = 685 (le « plateau » est hors du nuage : la courbe est concave, pas
saturée) ; CD 2,07 / 68 ; SF 1,60 / 18 ; IDE : NLS « converge » sur K = −69, sans sens physique (sans effet : la
saturation y perd déjà).

**Lecture.** Les dentistes sont le seul cas qui ressemble à une saturation (pente forte au premier quintile, IC
au-dessus de 0, pente faible au dernier, ΔAIC = 1,94, à 0,06 du seuil). Mais l'IC de δ contient 0 et le placebo
reprend 82 % de la pente : la règle gelée tue M2b. Les kinés ont le ΔAIC le plus fort, mais par concavité, et le
recours suit la densité à tous les quintiles (β_Q5 = 0,83) : c'est la forme « sans plateau » de la dérivation
(demande induite ou rationnement partout).

Rapporté, non décisif :

| Profession | 2018 seule : δ / ΔAIC | hors 75, 92, 93, 94 : δ / ΔAIC | A ameli : β_Q1 / β_Q5 (biaisé vers 1) | 18 régions : ΔAIC | SFA : σ_u ; E[u] Q1 → Q5 |
|---|---|---|---|---:|---|
| infirmiers | 0,17 / −1,41 | −0,01 / −0,28 | 2,53 / −0,63 | 0,45 | 0,45 ; 0,22 → 0,49 |
| kinés | 0,51 / 22,56 | 0,37 / 22,20 | 1,39 / 0,71 | 7,30 | 0,18 ; 0,16 → 0,13 |
| dentistes | −0,26 / 1,39 | −0,14 / 5,87 | 0,99 / 0,37 | −0,12 | 0,23 ; 0,22 → 0,20 |
| sages-femmes | 0,46 / −0,55 | −0,65 / 1,09 | 1,01 / −0,08 | 0,36 | 0,29 ; 0,27 → 0,23 |

- La frontière stochastique ne montre pas d'inefficacité (`u`) qui décroît nettement avec l'accès, sauf faiblement
  pour MK et SF ; pour les IDE elle croît.
- « 18 régions » : 13 métropolitaines et 5 DROM, chacun sa région (le protocole disait « 13 » ; sans test).
- Dentistes hors Paris et petite couronne : ΔAIC = 5,87, δ = −0,14. C'est la menace de fuite de patientèle écrite au
  protocole ; non décisif.

## How
- **Données :** patientèle et démographie data.ameli.fr (ODbL, hors dépôt, `v2/data/odbl/besoin/`), 2023–2025 ;
  Omphale 2022 central ; poids APL (M1, P1) ; effectifs libéraux observés du jumeau (`jumeau.history.sector_table`,
  secteur privé ; IDE 2023 seule).
- **Méthode :** [`v2/besoin/validation/pb2.py`](../../../besoin/validation/pb2.py), lecteurs
  [`recours.py`](../../../besoin/estimateurs/recours.py). Commit du passage : `3ac2abd` (écarts commités avant).
  Commande : `PYTHONPATH=v2 uv run --with scipy python -m besoin.validation.pb2` → `v2/artifacts/besoin_pb2/`.
  Bootstrap B = 2 000, graine 20261115.
- **Reproduction :** relancé après déplacement de `table()` dans `recours.py` : sorties identiques.

## ⚑ What could make it wrong
- **Département de la patientèle** non documenté (écart 4) ; la fuite vers les départements bien dotés biaise la
  pente du quintile haut **vers le haut**, donc contre la saturation (protocole).
- **Patients uniques, pas actes** ; double compte entre professionnels (A1.1).
- **Offre IDE du jumeau** : le secteur privé inclut les salariés des cliniques (effectif ≈ 2,8 × l'effectif libéral
  ameli en 2023) ; la pente IDE négative peut venir de là.
- **Population projetée** (Omphale) au lieu des estimations Insee (écart 1).
- **101 points, 20 par quintile** : la charge de la preuve est sur la saturation ; un IC large la tue.

## → What it changes
- **M2b retiré du service** : `v2/besoin/estimateurs/m2b.py` garde le code et le verdict, la classe n'est plus
  enregistrée (aucun chemin de service ne la choisit).
- **M2a (AREA) reste** : il n'est pas jugé par P-B2 ; c'est le repli prévu. Le niveau absolu du besoin non
  satisfait (`B₂ − R`) n'est donc **pas identifié** par les données ouvertes.
- P-B3 (triangulation du niveau) compare M3 à M2a au lieu de M2.

## ? Next
| Item | Cost |
|---|---|
| Lire la page « Méthode » de la patientèle (département d'exercice ou de résidence) | ~10 min Claude |
| Offre IDE libérale seule (ameli) dans la spline, en sensibilité | ~10 min Claude |
