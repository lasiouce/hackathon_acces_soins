---
type: analysis
date: 2026-11-15
author: session besoin-derivation (3 lecteurs en lecture seule, contrôle par échantillon)
question: "Quelles lignes « open » du ledger v2 sont déjà faites, dépassées ou en double ?"
headline: "Sur 167 lignes « open » hors module de besoin : 43 déjà faites, 6 dépassées, 7 incertaines, 111 réellement ouvertes ; 5 doublons ; le tableau des questions ouvertes du rapport technique reprend au moins 12 lignes faites"
status: final
professions: [all]
tags: [ledger, perime, stale]
---

# Ledger v2 : lignes périmées

> **Headline :** sur 167 lignes « open » de `v2/docs/lab/open.md`, hors module de besoin, on compte :
> - **43 déjà faites** ;
> - **6 dépassées** par une décision ultérieure ;
> - **7 incertaines** ;
> - **111 réellement ouvertes**, dont 5 doublons.
>
> **Appliqué le 2026-11-15** (accord de l'utilisateur·rice) : 43 lignes passées en « fait », 6 en « dépassé », avec
> leur preuve ; 4 doublons marqués « en double de » (la paire 143/170 est fermée). Les 7 incertaines restent ouvertes.

## Comment
Trois lecteurs en lecture seule se sont partagé les lignes, par tranches de 56. Ils ont confronté chacune au registre
(`decisions.md`), aux rapports, au code et au tableau du rapport technique (`ch-ouvertes.tex`).

La session a contrôlé 6 preuves par échantillon (decisions.md:855, 2705, 2869, 3158, 4448 ; open.md:48) : toutes
concordent. Les 43 autres verdicts « fait » n'ont pas été recontrôlés un par un.

## Déjà faites (43) : à passer en « fait », avec la preuve
| Ligne | Objet | Preuve |
|---|---|---|
| 16 | reproduction DD76 2050 | N2 (`axe3-n2-long-terme`, verdict N2-A) ; decisions:1846 |
| 23 | défauts bloquants 1–4 du jumeau | decisions:588, :1027 |
| 25 | second test IDE de N3 | N7-A, decisions:1798–1828 (échec) |
| 29 | banc N1 + premier dépôt | open:139 ; decisions:1964 |
| 30 | N2 L1–L3 + partie A | open:129 ; decisions:1916 |
| 31 | N4 avec oracle | `axe3-n4-echelle-fine` ; decisions:1924 |
| 36 | secteur_stock dans l'état | `jumeau/history.py:97` ; decisions:608 |
| 49 | biais du multiplicateur retraite 65+ | decisions:1224, :1241 |
| 50 | mondes simulés | N5, decisions:1002 |
| 51 | comparaison ER1319 2050 | N7-D, decisions:1807, :1846 |
| 57 | nouvelle revue adversariale | revues v2 et v3 ; decisions:1027 |
| 59 | observatoire → axe 3 | decisions:1002, :1798 |
| 65 | dépôt 2027–30 | decisions:2869 (A0 + C1) |
| 76 | seconde revue, défauts 1–4 | decisions:855 |
| 80 | troisième revue | decisions:1027 |
| 87 | IDE dans le jumeau (H_ind) | decisions:2100 |
| 88 | corrections de la troisième revue | decisions:1224 |
| 91 | rejeu UAT par persona | `uat-carte-v2`:19 |
| 93 | sélecteur d'horizon | decisions:3458 |
| 94 | fiche exportable avec sources | decisions:3183 |
| 95 | densité pour 100 000 | decisions:3317 |
| 97 | retours sur la carte (zoom, DROM, palette) | decisions:961–979 |
| 101 | N6 `probabilistic.py` | `v2/validation/probabilistic.py` ; decisions:1835 |
| 102 | SBC de N6 | decisions:1837 |
| 103 | kinés +20 % : rapport mis à jour | `prototype-decision`:15–20 |
| 104 | cohortes bayésiennes C1 | decisions:2834 |
| 105 | référence naïve probabiliste | N7-C, `axe3-n7-addendum`:80 |
| 106 | propagation de θ (Laplace) | decisions:2834 (C2 rejeté) |
| 107 | calibrage APC 5×2×200 | decisions:2894 |
| 109 | installations nettes < 40 ans par commune | decisions:1505 ; `build_flux.py` |
| 110 | officines par commune (FINESS) | decisions:2196 ; `build_pharmaciens.py` |
| 113 | flux des diplômés étrangers | decisions:1882 |
| 115 | vivier réel (DREES 491) | decisions:1671 ; `jumeau/vivier.py` |
| 116 | âge d'entrée des étrangers à 28 ans | decisions:1671 (l'âge par profession reste ouvert) |
| 121 | SF « Prévention » classée publique | decisions:1980 |
| 132 | dépôt C1/A0 2027–30 | decisions:2869 |
| 138 | N4 avec projection réelle | N10, `axe3-n10-grain-couverture`:18 |
| 143 | ±460 % IDE, H_ind | decisions:2238, :2419 (cause : 2012, axe 5) |
| 149 | clore « cumul emploi-retraite » | open:48 (déjà fermé, ligne en double) |
| 162 | inscrire K3 avant le banc | decisions:3020 |
| 164 | banc EPCI et bassin de vie | N10:29–31 |
| 166 | juger K3 avec N10 | decisions:2279, :2324 |
| 170 | ±460 % venait de l'axe 5 | decisions:2419 (ferme 143) |

## Dépassées (6) : à marquer « dépassé », avec la décision qui les remplace
| Ligne | Objet | Dépassée par |
|---|---|---|
| 71 | coût communal de A1a | decisions:2705 (A1b retenu) |
| 134 | grain EPCI / bassin de vie sous N4 | decisions:2279, :3158 (affichage au département) |
| 157 | modèle à agents à règles logit par commune | decisions:4473 (pas de modèle à agents ; test de covariables d'abord) |
| 160 | pharmaciens communaux, 10,7 % d'erreur à l'EPCI | decisions:3158 (fin des variantes K) |
| 163 | table de passage RPPS privé ↔ CartoSanté pour K3 | decisions:3158 ; K3 jugé |
| 190 | emballer un intervalle comme `Estimator` | decisions:4448 (aucun candidat ne bat C1, la condition est tombée) |

## Incertaines (7) : à trancher
| Ligne | Objet | Pourquoi incertaine |
|---|---|---|
| 14 | relancer K1 + filière sur le privé | N1 confirmatoire sur le privé fait (`axe3-n1-prevision`:161) ; variante filière peut-être jamais relancée |
| 17 | injecter le vivier | injection construite (decisions:1671) ; comparaison au banc non faite |
| 22 | recalcul communal 5 × 2 | mesuré de 2,0 à 4,6 s sur un état synthétique, « C15 échoue sous charge » (decisions:1564) ; état réel non mesuré |
| 24 | 3 constats non réfutés | 2 sur 3 vérifiés (decisions:588) ; « entrées ≤ sorties » non vérifié (decisions:1036) |
| 58 | observatoire → axe 0 (B1, B2, B6, A6) | B1 fait ; aucune trace pour B2, B6, A6 |
| 61 | borne r ≤ 1,2 contre l'emballement de K1 | répondu au banc (decisions:2745) ; test en mondes simulés non fait |
| 120 | part privée des pharmaciens hospitaliers : choix de la source | RPPS central, SAE en variante (decisions:1980) ; écart non réconcilié |

## Doublons (5 paires)
- **137 = 141** : flux des diplômés étrangers.
- **108 = 131** : archive de l'Annuaire santé.
- **145 ⊃ 171** : axe 5, doubler N.
- **155 ≈ 187** : σ bayésien complet, choc national de C1.
- **143 fermée par 170.**

## Réellement ouvertes (111)
Les lignes non citées ci-dessus, et les 18 lignes « Besoin » de ce jour.

Les lecteurs ont signalé quatre groupes :
- **attendent le monde** : 188, intervalles sur l'origine 2027 ; 47, kinés « 2 ans », pas mesurable avant 2028 ;
- **demandent du temps humain** : 46, 167, 168, 85, 86 ;
- **dépendent de l'archive de l'Annuaire** : 154, 158, 161, 193 ;
- **en partie sans objet** depuis que l'affichage reste au département : 19, 79, 119.

## ⚑ Ce qui pourrait rendre ceci faux
- Les verdicts « fait » viennent de lecteurs, avec un contrôle par échantillon de 6 preuves sur 49.
- Une ligne peut être « faite » au sens de sa première moitié seulement. C'est la raison des 7 incertaines ; il peut
  en manquer.

## → Ce que ça change
- **`open.md`** : 49 statuts à corriger, et 5 doublons à marquer « en double de ».
- **Le rapport technique**, chapitre `ch-ouvertes.tex` (tableau des questions ouvertes), présente comme ouvertes au
  moins 12 lignes faites (25, 36, 95, 97, 103, 109, 110, 121, 138, 160, 163…). Il faut un erratum ou une mise à jour.
- **Le compte de lignes ouvertes** passe de 185 à environ 130 (111 hors module de besoin + 18 du module).

## ? Suite
| Point | Coût |
|---|---|
| Passer les 49 statuts (fait / dépassé, avec la preuve) et marquer les doublons dans `open.md` | ~10 min |
| Trancher les 7 incertaines (couper chaque ligne en sa partie faite et sa partie ouverte) | ~15 min |
| Mettre à jour le tableau de `ch-ouvertes.tex` et recompiler le rapport technique | ~20 min + compilation |
| Ajouter des champs de provenance (`status`, `superseded_by`) aux lignes du ledger, pour rendre ce contrôle mécanique (signal : 49 sur 167 périmées, soit 29 %) | ~30 min |
