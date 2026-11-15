---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: La morbidité (M3, prévalence × soins par cas) change-t-elle l'indice 2050 au-delà de l'âge (M1), et explique-t-elle le recours standardisé hors échantillon ?
headline: "P-B3 : (A) M3 retenu pour l'indice des seuls infirmiers (S₃ = 83 %, ρ = 0,992) ; réduit au recoupement pour MK, CD, SF, PH (S₃ 95–100 %, ρ ≥ 0,998, aux 3 imputations) ; (B) H-B3 rejetée pour les 4 professions : ΔR² hors échantillon de −0,03 à +0,01, contre 0,10 exigé"
status: passage fait
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B3 ; protocole gelé P-B3 (v2/validation/preregistered/2026-11-15-besoin-p-b3-pathologies.md) et amendement A1.2
sources: [cartographie des pathologies 2024 (effectifs, dépenses ; data.ameli.fr, ODbL), Open DAMIR 2025 (9 mois), Omphale 2022, poids APL, patientèle ameli, projection C1 du jumeau]
tags: [besoin, validation, P-B3]
---

# P-B3 — M3 contre M1 sur l'indice ; morbidité et recours hors échantillon (passage)

> **Headline :** la morbidité départementale ne change presque pas l'indice 2050 une fois l'âge pris en compte,
> sauf pour les **infirmiers** (17 % des départements s'écartent de plus de 2 %, jusqu'à +5 % à La Réunion) :
> **M3 est retenu pour l'indice IDE**, et **réduit au recoupement** pour MK, CD, SF et PH. Et la morbidité
> n'explique pas le recours standardisé hors échantillon : **H-B3 est rejetée** pour les quatre professions testées
> (ΔR² ≤ 0,01, seuil 0,10).

## Écarts au protocole et à A1, écrits le 2026-11-15 avant tout calcul de C₃ et de ΔR²
Avant ces écarts, seul un contrôle de construction de M3 a été regardé : total national de B₃ 2024 contre la
dépense nationale du poste / prix (rapport 1,001–1,008), part négative du résidu `r₀`. Aucun indice, aucun
rapport C₃/C₁, aucun R² n'a été calculé.

1. **Groupes g.** Les 16 groupes de **niveau 1** de la cartographie qui ont des effectifs (dont « pas de pathologie
   repérée ») ; la dépense de niveau 1 est une partition (Σ groupes + soins courants = total, mesuré à 10⁻⁹). Les
   « soins courants », sans effectif, vont dans `r₀`.
2. **`n(p,g)`** = dépense remboursée nationale du poste attribuée au groupe / effectif national du groupe (€ par
   patient), divisée par le prix moyen : **montant remboursé / quantité**, Open DAMIR flux 2025-01 à 2025-09
   (A1.2), secteur privé (`PRS_PPU_SEC = 2`), national. Le prix ne fixe que le niveau (il s'annule dans C et dans
   log(B₃/B₁) à une constante près).
3. **`r₀` non borné.** Résidu national par âge et sexe tel que gelé (profil total de M1 moins la part des groupes).
   Il est négatif à certains âges (dépense par cas sans âge) : part négative rapportée, de 4 % (MK) à 25 % (IDE) du
   total. Aucune cellule département × âge × sexe n'a un besoin par habitant négatif (mesuré).
4. **Profil total.** M1 servi : P1 (APL) pour IDE, MK, CD, SF ; P2 (DAMIR) pour PH.
5. **Effectifs (A).** Comme P-B1 : trajectoire C1 servie, déterministe.
6. **Validation croisée (B).** « Régions 2016 » : les 13 régions métropolitaines **et** les 5 DROM, chacun sa région
   (18 plis). Le protocole dit « 13 plis » ; il ne dit pas où vont les DROM ; la règle « une région laissée de côté »
   est appliquée à la partition régionale telle qu'elle est.
7. **(B) `R_std`** de P-B2 (A1.2) ; `log(B₃/B₁)` à 2024, Omphale central, `B₁` = population standardisée APL.
8. **Triangulation** : **sans objet**, M2b n'a pas survécu à P-B2 (le protocole ne la prévoit que dans ce cas).
   Le rapport P-B2 disait « P-B3 compare M3 à M2a » : c'est corrigé ici, la comparaison à M2a n'est pas au protocole
   et n'est pas faite.
9. **Imputations des cellules masquées** : 1, 5, 10 patients ; (A) doit conclure « réduit » aux trois pour réduire M3 ;
   (B) est calculé à l'imputation centrale 5 (le protocole n'exige les trois que pour (A)).
10. **Voie (ii) SF** (norme réglementaire) : non rapportée ; la fiche `n_grossesse` existe, mais le décompte
    « actes par grossesse » n'est pas branché dans M3 avant ce passage.

## Question
P-B3 ([protocole](../../../validation/preregistered/2026-11-15-besoin-p-b3-pathologies.md)) : (A) M3 déplace-t-il
l'indice 2050 au-delà de M1 ? (B) H-B3 : la morbidité explique-t-elle, hors échantillon, une part du recours
standardisé que l'âge n'explique pas ([dérivation §6, M3](../derivations/2026-11-15-besoin-derivation.md)) ?

## Result
**(A) Indice 2050**, Omphale central, effectifs C1 servis. Nombres **mesurés** ; seuils supposés au gel.

| Profession | S₃ (imput. 1 / 5 / 10) | ρ (imput. 5) | C₃/C₁ − 1 : min · médiane · max | Verdict |
|---|---|---:|---|---|
| infirmiers | 0,830 / 0,830 / 0,830 | 0,9917 | −3,6 % · +0,1 % · +5,0 % | **M3 retenu pour l'indice** |
| kinés | 1,000 / 1,000 / 0,990 | 0,9991 | −1,9 % · +0,1 % · +1,4 % | réduit au recoupement |
| dentistes | 0,990 / 0,990 / 0,990 | 0,9997 | −0,5 % · 0,0 % · +2,9 % | réduit au recoupement |
| sages-femmes | 0,970 / 0,970 / 0,950 | 0,9986 | −3,1 % · −0,1 % · +2,5 % | réduit au recoupement |
| pharmaciens | 0,990 / 0,980 / 0,980 | 0,9985 | −2,2 % · 0,0 % · +2,9 % | réduit au recoupement |

IDE, départements les plus écartés : 974 (+5,0 %), 62 (+3,7 %), 74 (−3,6 %), 971 (+3,5 %), 08 (+3,1 %).

**(B) H-B3**, `y = log R_std` (2023–2025) sur `log(B₃/B₁)` 2024, 18 plis régionaux, IC à 98,75 %.

| Profession | n | ΔR² hors échantillon [IC] | placebo (profession) : ΔR² | Verdict |
|---|---:|---|---|---|
| infirmiers | 100 | 0,005 [−0,117 ; 0,114] | kinés : 0,128 | **rejetée** ; non spécifique |
| kinés | 101 | −0,033 [−0,166 ; 0,082] | dentistes : 0,046 | **rejetée** |
| dentistes | 101 | −0,003 [−0,109 ; 0,086] | sages-femmes : 0,401 | **rejetée** |
| sages-femmes | 100 | 0,010 [−0,206 ; 0,146] | infirmiers : 0,042 | **rejetée** ; non spécifique |

Lecture : le placebo dépasse le propre dans 4 cas sur 4, nettement pour les dentistes (0,40) : la morbidité « propre »
de la profession n'apporte rien, mais un indice de morbidité générale corrèle au recours (comme γ de M2a, qui
utilise une autre mesure de morbidité). Ce n'est pas décisif (le placebo ne sert qu'à qualifier).

Contrôles de construction (avant passage) : total national B₃ 2024 / (dépense du poste / prix) = 1,001–1,008 ;
part négative du résidu `r₀` : IDE 24,6 %, SF 17,8 %, CD 8,5 %, PH 5,0 %, MK 4,3 % du total.

## How
- **Données :** cartographie des pathologies 2024, effectifs et dépenses (data.ameli.fr, ODbL, hors dépôt) ; prix
  moyen Open DAMIR 2025 (9 mois, A1.2) ; Omphale 2022 ; poids APL et profil DAMIR (M1) ; patientèle (P-B2) ;
  trajectoire C1 servie.
- **Méthode :** [`pb3.py`](../../../besoin/validation/pb3.py), estimateur [`m3.py`](../../../besoin/estimateurs/m3.py).
  Commit du passage : `3bf9b5d` (écarts commités dans le même commit, avant le lancement).
  Commande : `PYTHONPATH=v2 uv run python -m besoin.validation.pb3` → `v2/artifacts/besoin_pb3/results.json`.
  Bootstrap B = 2 000, graine 20261115.

## ⚑ What could make it wrong
- **Construction maison** (dépense par cas sans âge, prix moyen national) : le résidu `r₀` absorbe jusqu'à un quart
  de la dépense IDE avec un signe négatif aux âges où les groupes surattribuent. M3 n'est pas plus fin que M1 pour
  cette raison : la variation départementale n'entre que par la prévalence.
- **Prévalence = recours** : la cartographie repère les pathologies par la consommation ; circularité diluée, pas
  levée.
- **Prévalences figées à 2024** ; la dérive épidémiologique n'est pas projetée.
- **Patientèle** (B) : mêmes menaces que P-B2.
- Le verdict IDE (83 % contre 90 %) dépend en partie des DROM (974, 971 en tête).

## → What it changes
- **Indice IDE** : M3 est un second estimateur servi à côté de M1 (« fourchette entre ansätze », axe 5).
- **MK, CD, SF, PH** : M3 n'est pas servi pour l'indice (constante `m3.INDICE`) ; il reste calculable comme
  recoupement du niveau.
- **H-B3 rejetée** : la morbidité, telle que mesurée en données ouvertes, n'améliore pas la prédiction du recours
  au-delà de l'âge. M1 reste le socle.
- Triangulation du niveau M3 / M2 : sans objet (M2b tué).

## ? Next
| Item | Cost |
|---|---|
| Dépense par cas par âge (si le jeu `depenses` existait par âge) pour réduire `r₀` négatif | non disponible en données ouvertes |
| Voie (ii) SF : actes réglementaires par grossesse × naissances Omphale | ~30 min Claude |
