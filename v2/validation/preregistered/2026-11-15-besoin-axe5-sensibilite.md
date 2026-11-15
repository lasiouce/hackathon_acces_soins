---
type: analysis
date: 2026-11-15
author: session besoin-axe5-sensibilite
question: "L'effet d'une politique sur l'indice de couverture C(p, T, 2050) se distingue-t-il de la dispersion due au choix du modèle de besoin ?"
headline: "Protocole pré-enregistré, gelé avant tout calcul de C : ratio R = |Δ log C| de la politique / étendue de log C entre estimateurs survivants ; R < 1 ⇒ « non distinguable » ; politique décisive quotas × 1,2 (DD76) ; décomposition de la variance de log C sur 4 sources (politique, estimateur, Omphale, tirages C1) + transfert L23 pour les pharmaciens"
status: protocole gelé (non lancé)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "H-S5 : pour au moins une profession, le choix du modèle de besoin déplace C(2050) plus que la politique de référence (R < 1)"
sources: [plan du besoin (axe 5), rapport axe 5 de l'offre (2026-11-14), rapport d'étape du besoin (2026-11-15), P-B6 (s∞, τ), fiche param-besoin-l23-vaccination]
tags: [besoin, axe5, sensibilite, pre-registration]
---

# Axe 5 du besoin — sensibilité de C(p, T, 2050) (protocole pré-enregistré)

Provenance des nombres : (m) mesuré, (s) sourcé, (d) dérivé, (h) supposé.

## Ce qui a été fait avant le gel
- **Pilote de faisabilité** (pharmaciens seulement, 2026-11-15 vers 06:30) : temps de calcul et effet **sur l'offre**
  seule de quotas × 1,2 (offre privée nationale 2050 / statu quo = 1,115 (m)) ; 200 tirages de C1 à 2050.
- **Aucun besoin B ni indice C** n'a été calculé dans cette session avant le gel. Les verdicts P-B1 à P-B6 sont
  connus (rapports publiés) ; ils fixent l'ensemble des estimateurs, pas les seuils ci-dessous.

## Sortie jugée
- `Y(p, T) = log C(p, T, 2050)`, logarithme naturel. C est un indice (rapport), sa dispersion se lit en log.
- C = `[S/B'](T, 2050) / [S₀/B₀](T, 2026)` (`besoin.couverture`, convention de l'axe 0 : base = statu quo sans
  transfert, même estimateur, même scénario Omphale, même tirage d'offre).
- **T** : 101 départements (niveau des états du jumeau) et **France** (C agrégé par sommes de S et de B, jamais une
  moyenne de C). Région : rapportée, non décisive.
- Horizon décisif **2050** ; 2035 rapporté.
- Professions : SF, CD, PH, MK, IDE. Aucun indice pour la médecine générale ni les spécialistes (O2) ; la MG
  n'apparaît que comme source de L23.

## Sources de variation
1. **Politique π** (offre), appliquée à partir de 2026 par `prototype.server.Model.scenario` (modèle servi, C1) :
   statu quo ; quotas × 0,8 et × 1,2 ; report de la retraite + 2 ans ; cumul emploi-retraite × 0,5 et × 2 ;
   départs précoces × 0,5 et × 1,5 ; diplômés étrangers × 0,5 et × 2 ; régulation à l'installation (part des zones
   = 1, entrants bloqués vers une zone voisine) pour les professions qui ont des zones. Amplitudes « dd76 » de l'axe
   5 de l'offre (référence retenue le 2026-11-14).
   **Plus L23** (pharmaciens) : vaccination antigrippale en officine, `besoin.transferts.l23` avec t₀ = 2019,
   s∞ = 0,74, τ = 2,4 ans (P-B6, (m)/(d)), a = 0,01 (h), k = 0,625 (milieu de [0,25 ; 1], (h)), μ = 0 (h).
   Lu contre la base sans transfert (convention de l'axe 0).
2. **Estimateur e** (besoin), parmi ceux qui survivent (rapport d'étape) :
   - IDE : M0, M1, M2a, M3 ;
   - MK, CD, SF : M0, M1, M2a ;
   - PH : M0, M1 (M2a non applicable).
   Profil de M1 : celui servi (`profil="apl"` : poids APL pour IDE, MK, CD, SF ; DAMIR pour PH).
   **M4 à part** : `M4.predict` rend le besoin d'entrée inchangé, donc C(M4∘M1) ≡ C(M1) par construction ; son
   indice d'accessibilité n'est pas C et n'entre pas dans la décomposition.
3. **Scénario Omphale ω** : central, pop_basse, pop_haute (Insee, Omphale 2022).
4. **Offre, tirages k** : K = 100 tirages de C1 (`validation.registry` « axe2_cohortes_c1 », `sample`), privé, par
   département. Appliqués à chaque trajectoire de politique comme écart relatif
   `ρ_k(T, t) = tirage_k(T, t) / moyenne(T, t)` (ρ = 1 pour t ≤ origine) : **séparabilité supposée (h)** entre
   l'incertitude de l'offre et l'effet du levier.
5. **Transfert j** (pharmaciens, dans la cellule π = L23 seulement) : J = 40 tirages uniformes indépendants,
   s∞ ∈ [0,67 ; 0,81] et τ ∈ [1,9 ; 2,9] ans (± 1 écart-type de P-B6, (d)), k ∈ [0,25 ; 1] (h, fiche),
   μ ∈ [0 ; 0,05] (h, fiche), a ∈ [0,005 ; 0,02] (h : placeholder 0,01 du module × [0,5 ; 2]).

Graine : 20261115.

## Statistiques
**Point de référence** : π = statu quo, e = estimateur servi (M1 ; M3 pour les IDE), ω = central, offre = moyenne
de C1 (sans tirage), transfert central.

- **Effet de la politique** `E_π(p, T) = |Y(π) − Y(statu quo)|`, autres facteurs au point de référence.
- **Dispersion due au choix du modèle de besoin** `D(p, T) = max_e Y(e) − min_e Y(e)`, au statu quo, autres
  facteurs au point de référence.
- **Ratio** `R_π(p, T) = E_π(p, T) / D(p, T)` ; D = 0 ⇒ R = +∞ (rapporté).
- **Politique décisive** : **quotas × 1,2**, celle qui sert de seuil à l'axe 5 de l'offre (« effet quotas × 1,2 »).
  Rapportées : chaque autre politique, le levier de plus grand E national par profession, et L23 pour les PH.
- **Décomposition de la variance** de Y sur la grille factorielle complète π × e × ω × k (× j pour PH), chaque
  niveau équiprobable : parts des effets principaux `S_X = Var(E[Y|X]) / Var(Y)` pour X ∈ {π, e, ω, k, j} et
  reste = interactions. Par profession, au national et par département (médiane et P10–P90 des départements).
- Échelles de comparaison rapportées à côté de D : étendue de Y entre scénarios Omphale ; P5–P95 de Y entre
  tirages d'offre ; P5–P95 de Y entre tirages de transfert (PH, L23).

## Seuil de lecture (gelé)
- **R < 1 ⇒ « non distinguable du choix du modèle de besoin »** ; R ≥ 1 ⇒ « distinguable ».
- Verdict national par profession sur la politique décisive ; part des départements où R ≥ 1 rapportée.
- **Règle d'affichage déclenchée** pour une profession si, au national et en 2050, R(quotas × 1,2) < 1 **ou**
  S_e > S_π. Elle s'écrit alors au registre : C affiché en **fourchette entre estimateurs** (min–max des
  estimateurs survivants), jamais un seul chiffre.
- Aucune inférence (pas d'IC) : la grille est déterministe à graine fixée ; R n'a pas de loi d'échantillonnage.

## Écarts au plan, déclarés avant calcul
1. **Capacité de formation et abandon IFSI** (leviers de l'axe 5 de l'offre) absents du modèle servi
   (`prototype.server.Model.scenario`) : non joués. Les quotas portent le levier de formation.
2. **Tirages de C1** : pris sur l'estimateur de méthodes (C1 privé, origine = dernière année observée), pas sur le
   jumeau servi, qui ne sert que la moyenne a posteriori ; d'où la séparabilité (h) du §4.
3. **IDE** : périmètre du modèle servi (`sector_table`), le même que P-B1.
4. **`a` de L23** en temps de MG : partiel dans la fiche ; plage supposée.
5. Le choix du profil de M1 (P1 / P2) n'est pas une source de variation décisive ; il est rapporté en variante,
   avec l'ensemble d'estimateurs sans M0 et avec M3 en recoupement (MK, CD, SF, PH).

## Ce qui renverserait la lecture
- Une dispersion D portée par un seul département atypique (Corse, DROM) : rapportée par la distribution, pas
  retirée.
- Un écart de séparabilité de l'offre : un tirage de C1 rejoué avec le levier dans la méthode, s'il change R de plus
  de 0,1, invalide le §4.
