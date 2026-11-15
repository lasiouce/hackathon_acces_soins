---
type: analysis
date: 2026-11-15
author: session besoin-derivation
question: "L'expérimentation de la vaccination antigrippale en officine (2017–2019) a-t-elle ajouté des vaccinations (m > 0) ou seulement déplacé des vaccinations existantes (m = 0) ? (P-B6, protocole gelé, amendement A1)"
headline: "(passage non encore lancé : écarts au protocole écrits avant calcul)"
status: draft
professions: [pharmaciens]
hypothesis: "H-BT (dérivation du besoin, §6) ; test P-B6"
sources: [Open Medic 2014–2018 ATC J07BB (Assurance maladie, LO 2.0), Insee populations municipales 2014–2018 (base-pop-historiques-1876-2023), IQVIA vaccination grippe 2021-22 → 2025-26 (data.gouv, LO 2.0)]
tags: [validation, besoin, transferts, vaccination, DiD, P-B6]
---

# P-B6 : vaccination antigrippale en officine, expérience naturelle

## Protocole appliqué
- Protocole gelé : `v2/validation/preregistered/2026-11-15-besoin-p-b6-grippe-officine.md`.
- Amendement A1, § A1.4, gelé et horodaté avant ce passage : `v2/validation/preregistered/2026-11-15-besoin-amendement-a1.md`.

## Écarts au protocole, écrits avant tout calcul (2026-11-15, vers 04:55)
Au moment d'écrire ces écarts, l'auteur avait vu :
- le total **national** des boîtes J07BB par année, 2014–2025, sans aucune ventilation régionale : 6,72 M en 2014,
  7,03 M en 2015, 7,70 M en 2016, 7,96 M en 2017, 8,57 M en 2018 (m) ;
- la liste des codes de région présents dans Open Medic ;
- les cinq premières lignes du fichier IQVIA.

Aucun volume régional n'avait été lu.

1. **Population.**
   - Le protocole prévoit les « estimations de population au 1ᵉʳ janvier » de l'Insee, qui ne sont pas sur disque. On
     utilise à la place les **populations municipales** des millésimes 2014 à 2018 (Insee, séries historiques,
     géographie au 1ᵉʳ janvier 2025), sommées par région.
   - L'écart à l'estimation au 1ᵉʳ janvier est de l'ordre de la croissance annuelle, < 1 % (d). Il est presque
     entièrement absorbé par les effets fixes de région.
2. **Zones.**
   - Les 12 zones métropolitaines sont celles d'Open Medic.
   - **93 = PACA**, la Corse n'ayant pas de code propre dans le fichier. La population de la zone 93 est celle de la
     PACA **plus** la Corse : on suppose que la Corse est rattachée à la PACA, comme dans DAMIR (supposé).
   - Les codes 0, 5 (DOM) et 99 sont exclus.
3. **Dénominateur du placebo** (0–19 ans) et de la tranche des 60 ans et plus : la **population totale**. La
   population régionale par âge 2014–2018 n'est pas sur disque.
   - Avec des effets fixes de région et d'année, seule compte la différence de croissance entre la tranche et le
     total, à l'intérieur d'une même région (d).
   - Le placebo reste donc un test de rupture sur les 0–19 ans.
4. **Construction de l'IC.**
   - Bootstrap sauvage par région, poids de Webb, B = 9 999, graine 20261115, sur le modèle **non contraint**.
   - IC « de base » : `[2·ATT − q₀,₉₇₅ ; 2·ATT − q₀,₀₂₅]`.
   - La valeur p bootstrap est calculée sous H₀ imposée (ATT = 0, modèle contraint), statistique |ATT|.
   - Le type d'intervalle n'était pas précisé dans le protocole.
5. **Sun et Abraham.**
   - La cohorte de contrôle est **g = 2019**, les 8 zones encore non traitées en 2018.
   - Interactions cohorte × temps relatif pour g = 2017 (e = −3, −2, 0, 1) et g = 2018 (e = −4, −3, −2, 0) ; e = −1 de
     référence.
   - ATT = moyenne simple des trois cellules post-traitement (g = 2017, e = 0 et 1 ; g = 2018, e = 0), chacune comptant
     2 régions × 1 an.
6. **Permutation.**
   - Les 2 970 affectations sont énumérées : 2 régions en 2017 et 2 en 2018, parmi 12.
   - La valeur p bilatérale est la part des |ATT| ≥ |ATT observé|, l'affectation réelle comprise.
7. **`m` en doses.**
   - `m = Σ_{cellules post} boîtes observées × (1 − e^{−ATT})`, soit l'observé moins le contrefactuel, sommé sur les
     trois cellules région-année, puis rapporté **par saison** (divisé par 2, les cellules post couvrant 2017 et 2018).
   - Ce n'était pas précisé dans le protocole.
8. **`s(t)`, descriptif (A1.4).**
   - Série nationale : actes VGP IQVIA de la campagne t/t+1 ÷ boîtes J07BB d'Open Medic de l'année t, pour 2021 à
     2025.
   - Ajustement `s(t) = s_∞(1 − e^{−(t−t₀)/τ})` avec **t₀ = 2019**, la généralisation, puisque la série est nationale.
   - IQVIA n'est pas régional au grain utile : il donne des actes pour 10 000 habitants, cumulés.
   - La campagne 2025-26 est **partielle** (arrêtée au 28 février) : elle est rapportée, mais exclue de l'ajustement.

## Résultat
*(à compléter après le passage)*
