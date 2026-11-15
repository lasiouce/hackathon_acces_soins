---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: Le recours standardisé plafonne-t-il quand l'accessibilité croît (saturation), ce qui identifierait le niveau du besoin (M2b) ?
headline: "(passage non lancé : écarts au protocole écrits avant calcul)"
status: draft
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B2 ; protocole gelé P-B2 (v2/validation/preregistered/2026-11-15-besoin-p-b2-saturation.md) et amendement A1
sources: [patientèle et démographie data.ameli.fr (ODbL), Omphale 2022 (Insee), poids APL DREES, effectifs du jumeau]
tags: [besoin, validation, P-B2]
---

# P-B2 — saturation du recours standardisé contre l'accessibilité (passage)

> **Headline :** (à remplir après le passage)

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
