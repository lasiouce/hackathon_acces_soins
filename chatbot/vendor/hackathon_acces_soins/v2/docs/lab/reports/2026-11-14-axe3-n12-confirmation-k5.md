---
type: analysis
date: 2026-11-14
author: session axe 3
question: K5 (axe 2) passe-t-il N10 et une origine réservée, et sur quelle origine ?
headline: "Protocole pré-enregistré, gelé avant tout jugement de K5 : même règle que N11 ; origine réservée 2022, h = 3 (cible 2025), proposée par l'axe 2, acceptée comme confirmation partielle ; références jugées sur la même origine"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes]
hypothesis: axe 3, N12 ; reprend N11 (SHA-256 4bf54ad0587a) pour K5
sources: [protocole N10 (d86d27c7a750), protocole N11 (4bf54ad0587a), inscription K5 (axe 2, decisions.md « K5 inscrit »)]
tags: [validation, axe3, commune, calibration, pre-registration]
---

# N12 — confirmation de K5 (protocole pré-enregistré)

> **Headline:** gelé avant d'ouvrir les deux fichiers de K5. Les règles sont
> celles de N11 ; seule l'origine réservée change.

## Règles
1. **Étape 1** : N10 tel quel (2014–2020, h = 5), `validation.grain.judge`.
2. **Étape 2** : origine réservée **2022, h = 3** (cible 2025), mêmes
   unités, exclusion des sauts sur la fenêtre 2017–2025, classes et seuils
   de N10 ; **références** recalculées à h = 3 sur la même origine (bandes
   tirées des erreurs à h = 3 dont la cible ≤ 2022).
3. **Confirmé** à un grain si les étapes 1 et 2 passent toutes deux à ce
   grain.
4. **Dépôt communal** de K5 : accepté sous le nom
   `axe2_k5_communes_2026-11-14.parquet`, origine 2025, cibles 2027 et 2028,
   avec empreinte ; il est écrit **quel que soit** le verdict, avant que je
   ne rende le jugement, pour qu'il ne dépende pas du résultat.

## Limites annoncées
- La cible 2025 a déjà été vue (N10, N11). L'origine 2022 n'a servi à rien
  encore, mais elle partage 3 années sur 3 avec les fenêtres 2020 → 2025 et
  2021 → 2025 : confirmation **partielle**.
- 2021 → 2025 était une période facile pour les kinés (N11) ; 2022 → 2025
  peut l'être aussi. Les références sur la même origine le diront.
- L'écart d'avant passage déclaré par l'axe 2 (σ_D robuste, décidé sur un
  diagnostic de paramètres) est accepté ; il est rappelé dans le verdict.

---

## Résultat (gel 09:05, SHA-256 `ad08357a48fe` ; calculé après le gel)
Soumissions : `n10_soumission_k5.parquet` (09:04:47) et
`n10_reservee_k5_2022h3.parquet` (09:05:00). Sorties :
`out/grain_axe2_k5_*`, `out/grain_axe2_k5_2022h3_*`,
`out/grain_ref_2022h3_couverture.csv`.

**Verdict : K5 n'est confirmé à aucun grain** ; il échoue aux deux étapes
pour les trois professions. **L'affichage reste au département.**

### Étape 1 — N10 (2014–2020, h = 5)
| Profession | Commune | BV | EPCI |
|---|---|---|---|
| Dentistes | 75,0 % ; 7 classes hors bande sur 8 | 74,5 % ; 5 | 73,0 % ; 4 |
| Infirmiers | 79,7 % ; 3 | **65,9 %** ; 7 | **59,1 %** ; 6 |
| Kinés | 73,6 % ; 7 | 69,9 % ; 6 | 67,3 % ; 6 |

K5 est **moins bien calibré que K3 et K4** : ses bandes sont devenues trop
étroites, en particulier pour les infirmiers aux grains agrégés (33 à 61 %
au-delà de 20 professionnels).

### Étape 2 — origine réservée 2022, h = 3
| Profession | Commune | BV | EPCI |
|---|---|---|---|
| Dentistes | 76,1 % ; 4 sur 6 | 77,2 % ; 3 sur 6 | 76,9 % ; 3 sur 7 |
| Infirmiers | 83,9 % ; 3 sur 8 | 79,9 % ; 5 sur 7 | 77,8 % ; 4 sur 6 |
| Kinés | 78,3 % ; 3 sur 7 | 79,2 % ; **1 sur 8** (1–2 : 71,2 %, 66 BV) | 79,5 % ; 2 sur 8 |

### Références sur 2022, h = 3
La **tendance** naïve des unités calibre **8 classes sur 8 pour les
infirmiers à la commune** et 7 sur 8 pour les kinés au BV ; la
persistance, 7 sur 8 pour les kinés au BV. **2022 → 2025 est une période
facile**, comme 2021 → 2025 : l'étape 2 seule ne prouverait rien.

**Rappel.** L'écart d'avant passage déclaré par l'axe 2 (σ_D robuste) est
accepté ; il ne change pas le verdict.

### Dépôt communal de K5
`v2/validation/depot/axe2_k5_communes_2026-11-14.parquet` (09:06:20, SHA-256
`0169b97d4fac`), écrit par l'axe 2 **avant** que le verdict lui soit rendu, comme le
prévoit N12. Origine 2025, cibles 2027 et 2028. Il mesurera la couverture hors
échantillon ; il ne peut plus confirmer K5.
