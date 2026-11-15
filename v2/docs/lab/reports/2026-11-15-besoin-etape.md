---
type: analysis
date: 2026-11-15
author: session besoin-etape (rédaction seule, aucun calcul)
question: Après le passage des protocoles gelés P-B1 à P-B6, quels estimateurs de besoin survivent, profession par profession, et que reste-t-il à établir ?
headline: "Étape du module de besoin : 6 protocoles sur 7 passés ; M1 (âge) retenu pour les 5 professions (IDE S₁ = 0 %, dentistes de justesse S₁ = 87,1 % sous P2) ; M2b tué partout ; M3 retenu pour l'indice des seuls IDE (S₃ = 83 %) ; H-B1 retenue (IDE −8,1 pts de MAPE) ; M4 indice maison en repli (ρ 0,66–0,77 < 0,90), passage OSRM à compléter ; m = 0 supposé (P-B6 non attribuable) ; k supposé [0,25 ; 1]"
status: draft — section P-B4 OSRM à compléter
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B0, H-B1, H-B2, H-B3, H-B4, H-BT (dérivation du besoin, §6)
sources: [rapports P-B1, P-B2, P-B3, P-B5 (branche claude/besoin-v2-m1-m3-4a490a), P-B4 (claude/besoin-v2-m4-ceebf5), P-B6 et P-B4-PH (claude/besoin-derivation-4a2fe6, claude/besoin-cible-pharmaciens-5c1cbe), decisions.md des mêmes branches]
tags: [besoin, étape, synthèse]
---

# Module de besoin : rapport d'étape (2026-11-15)

> **Headline :** sur les sept protocoles gelés, six ont été passés. L'âge (**M1**) est retenu pour les cinq
> professions. La saturation (**M2b**) tombe partout : le besoin non satisfait n'est pas identifié en données
> ouvertes au département. La morbidité (**M3**) ne sert l'indice que pour les **infirmiers**. Le backtest
> retient **H-B1** (l'âge bat la persistance pour 3 professions sur 4). **M4** reste un indice maison : il échoue en
> repli vol d'oiseau, et le passage OSRM n'est pas encore fait. Pour les transferts, **`m` et `k` restent supposés**.

Rédaction seule : chaque nombre est repris du rapport de passage cité, avec son étiquette d'origine
((m) mesuré, (s) sourcé, (d) dérivé, (h) supposé). Aucun calcul n'a été refait ici.

## Question
Quels estimateurs du besoin survivent aux tests d'abandon gelés de la
[dérivation](../derivations/2026-11-15-besoin-derivation.md) (§6) et du
[plan](../derivations/2026-11-15-besoin-plan.md), et qu'est-ce que l'indice de couverture servi peut affirmer ?

## Result

### Ce qui survit, par profession

| Profession | M0 (population) | M1 (âge) | M2a (AREA) | M2b (saturation) | M3 (morbidité) | M4 (2SFCA) | GBM (P-B5) |
|---|---|---|---|---|---|---|---|
| infirmiers | cas limite | **retenu** | repli construit | tué | **retenu pour l'indice** | indice maison (repli) | recours seulement |
| kinés | cas limite | **retenu** | repli construit | tué | recoupement | indice maison (repli) | n'entre pas |
| dentistes | cas limite | **retenu de justesse** | repli construit | tué | recoupement | indice maison (repli) | recours seulement |
| sages-femmes | cas limite | **retenu** | repli construit | tué | recoupement | indice maison (repli) | recours seulement |
| pharmaciens | cas limite | **retenu** (P2 seul) | — | sans objet | recoupement | P-B4-PH gelé, non passé | non testé |

« Recoupement » : M3 est calculé et rapporté à côté de M1, mais ne remplace pas M1 dans l'indice servi.
« Recours seulement » : le GBM prédit le recours, jamais le besoin (décision du 2026-11-15, option (a)).

### Les verdicts, avec leur chiffre et leur provenance

| Protocole | Question | Verdict | Chiffre clé | Source |
|---|---|---|---|---|
| **P-B1** | L'âge (M1) déplace-t-il l'indice 2050 par rapport à M0 ? (abandon si S₁ > 0,90 et ρ ≥ 0,98, sous P1 **et** P2) | M1 retenu pour les 5 professions | IDE S₁ = 0 % (m), ρ = 0,835 (P1) / 0,860 (P2) (m) ; MK S₁ = 0 %, ρ = 0,984 (m) ; SF S₁ = 1 % (m) ; PH (P2 seul) S₁ = 0 %, ρ = 0,987 (m) ; CD : P1 abandon (S₁ = 93,1 %, ρ = 0,998), P2 maintien (S₁ = 87,1 %, ρ = 0,999) (m) | [`2026-11-15-besoin-pb1-age.md`](2026-11-15-besoin-pb1-age.md), branche `claude/besoin-v2-m1-m3-4a490a` |
| **P-B2** | Le recours standardisé plafonne-t-il avec l'accessibilité (M2b) ? | M2b tué (IDE, MK, CD, SF) ; retiré du service | borne haute de l'IC 98,75 % de δ ≥ 0 partout : IDE +1,63, MK +1,10, CD +0,37, SF +0,82 (m) ; ΔAIC ≥ 2 pour les seuls MK (23,1 (m)), mais pente du premier quintile non distinguable de 0 et placebo non attribuable | [`2026-11-15-besoin-pb2-saturation.md`](2026-11-15-besoin-pb2-saturation.md), même branche |
| **P-B3** | (A) M3 déplace-t-il l'indice au-delà de M1 ? (B) H-B3 : la morbidité explique-t-elle le recours hors échantillon ? | (A) M3 retenu pour les IDE, réduit au recoupement ailleurs ; (B) H-B3 rejetée | (A) IDE S₃ = 83 %, ρ = 0,992 (m), écart max +5,0 % (974) (m) ; MK, CD, SF, PH S₃ de 95 à 100 %, ρ ≥ 0,998 aux 3 imputations (m). (B) ΔR² hors échantillon de −0,03 à +0,01 (m), contre 0,10 exigé (h, gel) | [`2026-11-15-besoin-pb3-pathologies.md`](2026-11-15-besoin-pb3-pathologies.md), même branche |
| **P-B4** | M4 reproduit-il l'APL DREES 2024 à la commune ? (ρ ≥ 0,90, erreur médiane ≤ 15 %) | **Échec en repli vol d'oiseau** ; M4 reste un indice maison | ρ M4–APL : IDE 0,72, MK 0,77, SF 0,66, CD 0,74 (m) ; erreur médiane 21 à 29 % (m) ; gain sur la meilleure densité naïve +0,15 à +0,31, IC 98,75 % > 0 (m) | [`2026-11-15-besoin-p-b4-apl.md`](2026-11-15-besoin-p-b4-apl.md), branche `claude/besoin-v2-m4-ceebf5` |
| **P-B5** | L'âge (M1) bat-il la persistance du recours 2016 → 2025 (h = 9) ? Un GBM bat-il M1 ? | H-B1 retenue (3 sur 4), même verdict sous P2 ; GBM qualifie pour IDE, CD, SF | Δ MAPE M1 − persistance : IDE −8,07, MK −3,32, CD −0,99, SF +1,57 pt (m) ; Δ GBM − M1 : IDE −1,91, CD −3,19, SF −45,84, MK −0,95 [IC contenant 0] (m) | [`2026-11-15-besoin-pb5-backtest.md`](2026-11-15-besoin-pb5-backtest.md), même branche |
| **P-B6** | La vaccination antigrippale en officine (2017–2019) a-t-elle ajouté des vaccinations (m > 0) ? | `m = 0` retenu par la règle, mais **non attribuable** (placebo en échec) : `m` reste supposé à 0 | ATT +0,73 % [−0,12 ; +1,58] (m, IC 95 % bootstrap sauvage) ; permutation p = 0,15 (m) ; placebo 0–19 ans +4,7 % [+1,2 ; +8,2] (m) ; s(t) national 0,44 (2021-22) → 0,67 (2024-25) (m), s∞ = 0,74 ± 0,07, τ = 2,4 ± 0,5 ans (d, ajustement) | [`2026-11-15-besoin-p-b6-grippe-officine.md`](2026-11-15-besoin-p-b6-grippe-officine.md), branche `claude/besoin-derivation-4a2fe6` |
| **P-B4-PH** | M4 pharmaciens reproduit-il l'APL DREES V0 aux pharmacies (2013) ? | **Gelé, non passé** | gel : SHA-256 `f96520f9…549d83`, RFC 3161 FreeTSA 04:09:44 UTC et DigiCert 04:09:45 UTC | décision du 2026-11-15, branche `claude/besoin-cible-pharmaciens-5c1cbe` |

### Ce qui est supposé

- **`k`** (rapport des durées de l'acte chez la profession cible et chez la source, dérivation §5) : **supposé**,
  plage [0,25 ; 1] pour L23 (fiches de l'axe 1, `decisions.md`). Aucun protocole ne le mesure. Pour L27 (accès
  direct au kiné), `k = 0` par construction.
- **`m`** (expansion du recours) : **supposé à 0**, plage [0 ; +5 %]. P-B6 ne rejette pas `m = 0`, mais son placebo
  échoue : le résultat est cohérent avec la littérature (RP 1,05 au Canada ; 46,1 % contre 46,0 % en France), sans
  la mesurer.
- **`a`** pour L23 : sourcé (parts des injections en 2018, Cour des comptes). **`s(t)`** : mesuré au national par
  P-B6 (s∞ = 0,74, τ = 2,4 ans), proche des valeurs dérivées de l'axe 1 (0,70 ; 2,8 ans) ; sa transposition à
  d'autres actes reste supposée.
- Les seuils des protocoles sont supposés au gel ; aucun n'a été changé au passage (écarts écrits avant calcul dans
  chaque rapport).
- M2a fige l'indice de morbidité M à 2024 (h) ; P-B1 et P-B3 prennent les effectifs de la trajectoire centrale C1,
  pas une médiane de tirages.

### P-B4, passage OSRM — **à compléter**

> **À compléter** par la session `besoin-v2-m4` quand le passage OSRM sera fait. L'amendement A1 (passage OSRM) est
> écrit avant calcul (branche `claude/besoin-v2-m4-ceebf5`, commit `761c190`) ; le distancier
> `v2/besoin/donnees/distancier_osrm.py` existe. Reporter ici : ρ M4–APL et erreur médiane par profession, gain sur
> la densité naïve, verdict (reproduction ou indice maison), et l'éventuel changement de libellé.

Tant que cette section est vide, la règle tient : **M4 n'est jamais appelé « APL »** dans la sortie, la carte ou un
rapport.

## How
- **Data :** rapports de passage et entrées de `decisions.md` des branches citées, lus par `git show` sans fusion.
- **Method :** reprise des headlines et des tableaux de résultats ; aucun nombre recalculé.

## ⚑ What could make it wrong
- **Dentistes, M1 de justesse** : P1 conclut à l'abandon, P2 au maintien (S₁ = 87,1 % pour un seuil de 90 %) ;
  sous les scénarios Omphale bas et haut, S₁ tombe à 55–58 %. Le verdict tient à la règle « P1 **et** P2 ».
- **M4 en repli** : l'échec peut tenir au distancier (Corse et montagne en tête des écarts ; ρ MK 0,78 hors
  montagne, 0,66 dedans, d'après le rapport P-B4). Le passage OSRM peut le renverser.
- **Le GBM suit l'offre** (corrélation 0,54 à 0,71 avec la croissance de l'effectif 2016 → 2025, diagnostic a
  posteriori) : c'est pourquoi il n'est servi que comme prédicteur du recours.
- **SF** : M1 perd contre la persistance au backtest (+1,57 pt), le recours y a crû avec l'offre (+54 % d'effectif
  libéral en médiane départementale). L'indice SF repose sur M1 retenu par P-B1, pas par P-B5.
- **P-B6** : deux saisons seulement avant 2017 ; tendances parallèles peu testables ; placebo en échec.
- Populations : Omphale 2022 au lieu des estimations Insee dans P-B2 et P-B3 ; 2025 extrapolée dans P-B5.
- Agrégats départementaux : rien ici ne valide l'indice à la commune, sauf la comparaison M4–APL.

## → What it changes
- **Indice de couverture servi** : dénominateur M1 pour les cinq professions ; M3 pour les infirmiers.
- **M2b** est retiré du service (`v2/besoin/estimateurs/m2b.py` garde le code) ; le besoin non satisfait n'est pas
  affiché comme un niveau.
- **M4** reste libellé « indice d'accessibilité maison » tant que P-B4 OSRM n'est pas passé.
- **Levier L23** (vaccination en officine) : branchable avec `a` sourcé, `s(t)` mesuré, `m = 0` et `k` supposés,
  chacun étiqueté.
- [`Home.md`](../../../../Home.md) (journal, Status), [`README.md`](../../../../README.md) (section du module) et le
  rapport technique (`v2/papers/rapport-technique/ch-ouvertes.tex`) sont mis à jour dans le même commit.

## ? Next
| Item | Cost |
|---|---|
| Passage OSRM de P-B4 et remplissage de la section « à compléter » | en cours (session besoin-v2-m4) ; machine occupée |
| Passage de P-B4-PH (APL V0 2013, pharmaciens) | ~1 h (h) |
| Mesurer `k` pour L23 (durées d'acte en officine et en cabinet) | non chiffré ; aucune source ouverte identifiée |
| Fusionner les branches de passage dans la branche du module | ~15 min (h), sur accord |
