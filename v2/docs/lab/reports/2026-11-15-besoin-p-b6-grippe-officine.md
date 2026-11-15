---
type: analysis
date: 2026-11-15
author: session besoin-derivation
question: "L'expérimentation de la vaccination antigrippale en officine (2017–2019) a-t-elle ajouté des vaccinations (m > 0) ou seulement déplacé des vaccinations existantes (m = 0) ? (P-B6, protocole gelé, amendement A1)"
headline: "P-B6 : m = 0 retenu, ATT +0,73 % [−0,12 ; +1,58] (IC 95 % bootstrap sauvage), permutation p = 0,15 sur 2 970 ; mais placebo 0–19 ans +4,7 % [+1,2 ; +8,2] → non attribuable : m reste supposé à 0, cohérent avec la littérature. s(t) national : 0,44 (2021-22) → 0,67 (2024-25), s∞ = 0,74 ± 0,07, τ = 2,4 ± 0,5 ans"
status: done
professions: [pharmaciens]
hypothesis: "H-BT (dérivation du besoin, §6) ; test P-B6"
sources: [Open Medic 2014–2018 ATC J07BB (Assurance maladie, LO 2.0), Insee populations municipales 2014–2018 (base-pop-historiques-1876-2023), IQVIA vaccination grippe 2021-22 → 2025-26 (data.gouv, LO 2.0)]
tags: [validation, besoin, transferts, vaccination, DiD, P-B6]
---

# P-B6 : vaccination antigrippale en officine, expérience naturelle

## Protocole appliqué
- Protocole gelé : `v2/validation/preregistered/2026-11-15-besoin-p-b6-grippe-officine.md`.
- Amendement A1, § A1.4, gelé et horodaté avant ce passage : `v2/validation/preregistered/2026-11-15-besoin-amendement-a1.md`.

## Écarts au protocole, écrits avant tout calcul (commit 2d20495, 2026-11-15 04:45:57 +0100)
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
Commande : `uv run --with scipy --with python-calamine --with pyarrow python v2/besoin/validation/pb6.py --raw <v2/data/raw/insee>`.
Sortie complète : `v2/besoin/validation/out/pb6.json`. Graine 20261115, B = 9 999. Le passage prend environ 40 s.

> **Headline :** l'autorisation de vacciner en officine n'a **pas** augmenté de façon détectable le nombre de doses
> antigrippales délivrées. Le placebo échoue pourtant : le dispositif ne permet pas d'attribuer cette absence d'effet
> à la mesure. `m` reste « supposé » à 0. La part des officines dans les vaccinations antigrippales monte
> d'environ 0,44 à 0,67 entre 2021-22 et 2024-25.

### `m` (test décisif)
| Quantité | Valeur |
|---|---|
| Panel | 12 zones × 2014–2018 = 60 cellules (m) |
| ATT (log des boîtes J07BB pour 1 000 hab.) | **+0,0073** (m) |
| IC 95 %, bootstrap sauvage de base | **[−0,0012 ; +0,0158]** (m) |
| Valeur p bootstrap (H₀ imposée) | 0,198 (m) |
| Valeur p de permutation exacte (2 970 affectations) | 0,153 (m) |
| `m` en doses par saison (estimation ponctuelle, non significative) | ≈ 19 500 (d) |
| Avant traitement, g = 2017, e = −3 | −0,019 [−0,080 ; +0,042] (m) |
| Avant traitement, g = 2017, e = −2 | +0,004 [−0,040 ; +0,049] (m) |
| **Placebo, 0–19 ans** | **+0,047 [+0,012 ; +0,082]** : l'IC exclut 0 (m) |

**Verdict selon les règles gelées :**
- **`m = 0` retenu**, puisque l'IC 95 % contient 0 et que les tendances avant traitement ne sont pas rejetées.
- Le **placebo dont l'IC exclut 0** fait passer le verdict en **« non attribuable »**.
- **`m` reste donc « supposé » à 0.**

C'est la valeur par défaut, et elle est cohérente avec les a priori publiés : 46,1 % contre 46,0 % la première année
selon la HAS, via Liard et coll. 2022 ; rapport de prévalence de 1,05 au Canada, Buchan et coll. 2017.

Le placebo n'est pas une simple formalité. Les pharmaciens ne vaccinaient pas les mineurs, et pourtant les boîtes
délivrées aux 0–19 ans augmentent dans les régions traitées. Deux lectures sont possibles :
- un effet régional non lié à la mesure, par exemple les campagnes des ARS pilotes ou l'intensité épidémique ;
- un artefact du dénominateur (écart 3 : population totale au lieu des 0–19 ans).

Son propre coefficient avant traitement (e = −3, −0,046 [−0,088 ; −0,003]) montre déjà une tendance différente avant
2017. Avec 12 grappes dont 4 traitées, la puissance est faible : `m = 0` est une **absence d'effet détectable**, pas une
preuve d'absence.

### Secondaires (non décisifs)
| Variante | ATT [IC 95 %] |
|---|---|
| 60 ans et plus | +0,0038 [−0,0029 ; +0,0105] (m) |
| Montants remboursés au lieu des boîtes | +0,0066 [−0,0021 ; +0,0153] (m) |
| Sans la cohorte g = 2018 | +0,0092, estimation ponctuelle seulement (m) |

### `s(t)` (descriptif, A1.4)
Part officinale nationale = actes VGP IQVIA de la campagne ÷ boîtes J07BB d'Open Medic de l'année de début :

| Campagne | Actes VGP (IQVIA) | Boîtes J07BB | s |
|---|---|---|---|
| 2021-22 | 4 475 890 | 10 255 940 | 0,436 |
| 2022-23 | 5 373 898 | 10 306 357 | 0,521 |
| 2023-24 | 5 645 127 | 9 903 344 | 0,570 |
| 2024-25 | 6 629 119 | 9 899 944 | 0,670 |
| 2025-26 | 8 020 525 | 11 675 815 | 0,687 |

- **Ajustement selon l'écart 8** (t₀ = 2019, sur les 4 premières campagnes) : **s∞ = 0,736 ± 0,071, τ = 2,37 ± 0,53 ans**
  (m ; erreurs types asymptotiques sur 4 points, indicatives).
- **Recoupement externe :** la Cour des comptes donne « près de deux sur trois » en 2024-25 (s). La série donne 0,67.
- **Correction de l'écart 8.** La campagne 2025-26 n'est **pas** partielle : elle est arrêtée au 28 février, comme les
  autres. La campagne partielle est 2026-27 (au 11 novembre 2026), qui n'a pas de boîtes Open Medic. Ajustement de
  sensibilité, 2025-26 incluse : s∞ = 0,747 ± 0,042, τ = 2,44 ± 0,35 (m). Le résultat est le même.

## Comment
- **Données :** Open Medic 2014–2018, J07BB, région de résidence (LO 2.0) ; Insee, populations municipales
  2014–2018 ; IQVIA 2021-22 à 2025-26 (LO 2.0, panel extrapolé).
- **Méthode :** Sun et Abraham à adoption échelonnée, avec effets fixes de région et d'année. Bootstrap sauvage par
  région (poids de Webb) et permutation exacte. Script : `v2/besoin/validation/pb6.py`.

## ⚑ Ce qui pourrait rendre ceci faux
- **Le placebo échoue.** Les régions traitées ont une dynamique propre, que la mesure n'explique pas.
- **Doses délivrées et non administrées.** Open Medic compte les boîtes, et une dose délivrée peut ne pas être faite.
- **Année civile contre campagne.** La saison t/t+1 est attribuée à l'année t (supposé).
- **Corse rattachée à la PACA** dans la population (supposé).
- **12 grappes.** La puissance est faible.
- **`s(t)`** repose sur un panel IQVIA extrapolé (environ 60 % des officines) et sur 4 ou 5 points. τ est mal
  déterminé.

## → Ce que ça change
- **Transferts (L23) :** `m = 0`, étiqueté « supposé ». P-B6 ne le contredit pas, mais ne le prouve pas non plus.
- **Montée en charge :** `s(t)` de L23 vaut s∞ ≈ 0,74, τ ≈ 2,4 ans, t₀ = 2019 (mesuré sur la série nationale), à la
  place de la forme supposée par l'axe 1.
- **Fiche L23** (`v2/docs/lab/fiches/`) : à mettre à jour avec ces valeurs.

## ? Suite
| Point | Coût |
|---|---|
| Placebo avec le vrai dénominateur 0–19 ans (Insee, population régionale par âge 2014–2018, à télécharger) | ~20 min |
| `s(t)` régional, si DAMIR 2015–2020 est un jour lu (codes 3360 VGP par région) | ~2 h 30 machine + 30 min |
| Mettre à jour la fiche L23 (s∞, τ, t₀ ; `m` supposé, avec la référence à P-B6) | ~10 min |
