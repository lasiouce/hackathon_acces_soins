---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: La pondération par l'âge (M1) change-t-elle l'indice de couverture de 2050 assez pour justifier son coût, par rapport à la population brute (M0) ?
headline: "Protocole pré-enregistré, gelé avant tout calcul : abandon de l'âge pour une profession si |C₁/C₀ − 1| < 2 % dans plus de 90 % des départements en 2050 et Spearman(C₁, C₀) ≥ 0,98, sous les deux profils d'âge ; seuils supposés"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B0 (dérivation du besoin, §6 M0) ; test d'abandon P-B1 (§8)
sources: [Omphale 2022 (Insee), poids de standardisation APL DREES 2024 (DCIR 2020–2022), Open DAMIR 2025 (Assurance maladie), projection C1 du jumeau]
tags: [validation, besoin, pre-registration, P-B1]
---

# P-B1 — M1 contre M0 sur l'indice de couverture 2050 (protocole pré-enregistré)

> **Headline :** gelé **avant tout calcul** de M1. Ce protocole ne croise
> aucune donnée de recours avec l'offre : il ne compare que deux
> dénominateurs.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Hypothèse
H-B0 : la structure par âge ne déplace pas l'indice de couverture indexé à
2026 de plus de 2 % (h) dans la plupart des départements, et ne change pas
leur classement. Si H-B0 tient pour une profession, M1 n'apporte rien au-delà
de M0 pour cette profession.

## Données (jeu, millésime, grain)
- **Population** : Omphale 2022 (Insee), scénario central, département ×
  sexe × âge, années 2026 et 2050 (déjà chargé par `v2/sante/load.py`).
- **Effectifs** `N(p,d,t)` : projection servie du jumeau (C1, médiane des
  tirages, scénario par défaut), département, 2026 et 2050. Le commit du
  jumeau utilisé est inscrit dans le rapport de passage.
- **Profils d'âge**, deux sources, toutes deux appliquées :
  - *(P1, principal)* poids de standardisation publiés dans les fichiers APL
    DREES 2024 (DCIR 2020–2022, 19 tranches quinquennales jusqu'à 90+) pour
    IDE, MK, CD, SF (SF : femmes seules) (s) ;
  - *(P2)* profil Open DAMIR 2025, national, tranches décennales fermées à
    80+, actes `PRS_NAT` par `PSE_ACT_SNDS` (19, 21, 24, 26, 50) (s). Seule
    source pour les **pharmaciens**, qui n'ont pas de poids APL.
- **Départements** : tous ceux où Omphale et le jumeau fournissent une
  valeur. La liste est fixée par la jointure, jamais par le résultat.

## Statistique
Pour la profession p et le département d :
- `B₀(p,d,t) = pop(d,t)` (le niveau `r̄_p` s'annule à l'indexation) ;
- `B₁(p,d,t) = Σ_{a,s} pop(d,t,a,s) · ω(p,a,s)` ;
- `C_k(p,d,2050) = [N(2050)/B_k(2050)] / [N(2026)/B_k(2026)]`.

Le rapport `C₁/C₀ = [B₀(2050)/B₀(2026)] / [B₁(2050)/B₁(2026)]` ne dépend pas
de N (d) : il mesure seulement l'effet de l'âge.
1. `S₁ = part des départements où |C₁/C₀ − 1| < 0,02` ;
2. `ρ = Spearman(C₁(p,·,2050), C₀(p,·,2050))` sur les départements (N
   intervient ici).

## Seuil de décision
L'âge est **abandonné** pour la profession p si `S₁ > 0,90` **et**
`ρ ≥ 0,98`, **sous P1 et sous P2** (les deux profils doivent conclure à
l'abandon). Sinon M1 est **retenu** pour p. Pour les pharmaciens, seul P2
existe : la décision repose sur P2 seul, et c'est écrit dans le verdict.

Pour les SF, M0 utilise la population totale et M1 les poids féminins : un
écart dû au sexe autant qu'à l'âge est compté comme un écart (c'est le
dénominateur servi).

## IC, référence naïve, placebo, multiplicité
- **Pas d'inférence.** Les deux statistiques sont des calculs déterministes
  sur des projections ; il n'y a pas d'échantillon à rééchantillonner. La
  sensibilité au profil (P1 contre P2) tient lieu d'incertitude.
- **Référence naïve** : M0 lui-même (c'est l'objet du test).
- **Placebo** : aucun.
- **Multiplicité** : Bonferroni sans objet (aucun test statistique). Les cinq
  verdicts sont rendus séparément ; aucun verdict poolé.

## Rapporté, non décisif
- `S₁` et `ρ` sous les scénarios Omphale bas et haut ;
- la distribution de `C₁/C₀ − 1` (min, quartiles, max) et les 5 départements
  les plus écartés ;
- les mêmes statistiques en 2035.

## ⚑ Menaces écrites
- **Seuils supposés.** 2 % et 0,98 sont des seuils de lecture (h), sans
  étalonnage externe. Ils sont figés ici et ne sont pas révisés après coup.
- **Poids datés.** Les poids P1 viennent de 2020–2022 et sont figés : la
  dérive du recours par âge (L31) est hors périmètre.
- **Écrasement du profil à 80+ en P2** (IDE : 4,50 à 80–84 ans contre 15,51
  à 90+ en P1 (s)). P2 sous-estime l'effet de l'âge : un abandon sous P2
  seul serait biaisé vers l'abandon ; c'est pourquoi les deux profils doivent
  conclure.
- **Circularité.** M1 hérite de la censure du recours (dérivation §2.3).
  P-B1 ne la teste pas ; P-B2 et P-B3 s'en chargent.

## Règles de gel
- Copie gelée, empreinte SHA-256 inscrite dans le rapport
  `v2/docs/lab/reports/2026-11-15-besoin-axe3-protocoles.md`.
- Le calcul n'est lancé qu'après l'horodatage externe de l'empreinte, ou, à
  défaut, après le commit poussé de la copie seule ; le rapport de passage
  cite l'heure du jeton ou dit qu'il n'y en a pas.
- Tout écart est un **amendement daté** dans le rapport de passage ; cette
  copie ne change plus.
