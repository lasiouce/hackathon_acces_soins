---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: La morbidité (M3, prévalence × soins par cas) change-t-elle l'indice 2050 au-delà de l'âge (M1), et explique-t-elle le recours standardisé hors échantillon ?
headline: "(passage non lancé : écarts au protocole écrits avant calcul)"
status: draft
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B3 ; protocole gelé P-B3 (v2/validation/preregistered/2026-11-15-besoin-p-b3-pathologies.md) et amendement A1.2
sources: [cartographie des pathologies 2024 (effectifs, dépenses ; data.ameli.fr, ODbL), Open DAMIR 2025 (9 mois), Omphale 2022, poids APL, patientèle ameli, projection C1 du jumeau]
tags: [besoin, validation, P-B3]
---

# P-B3 — M3 contre M1 sur l'indice ; morbidité et recours hors échantillon (passage)

> **Headline :** (à remplir après le passage)

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
