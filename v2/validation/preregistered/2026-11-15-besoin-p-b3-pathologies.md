---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: La morbidité (M3, prévalence × actes par cas) change-t-elle l'indice de couverture et explique-t-elle le recours au-delà de l'âge (M1) ?
headline: "Protocole pré-enregistré, gelé avant tout calcul de M3 : même règle que P-B1 sur C₃/C₁ (2 %, 90 %, ρ ≥ 0,98) ; H-B3 retenue si le R² hors échantillon (validation croisée par région) gagne ≥ 0,10, IC 98,75 % (bootstrap des départements) au-dessus de 0 ; triangulation M3/M2 rapportée, non optimisée"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B3 (dérivation du besoin, §6 M3) ; test d'abandon P-B3 (§8)
sources: [cartographie des pathologies (CNAM, data.ameli.fr, ODbL) jeux effectifs et dépenses, Open DAMIR 2025, Omphale 2022, patientèle 2023–2025]
tags: [validation, besoin, pathologies, pre-registration, P-B3]
---

# P-B3 — M3 contre M1 sur l'indice ; triangulation du niveau M3 / M2 (protocole pré-enregistré)

> **Headline :** deux tests indépendants. (A) l'indice 2050, même règle que
> P-B1 ; (B) le pouvoir explicatif de la morbidité sur le recours observé, hors
> échantillon. Gelé avant toute construction de M3.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Hypothèses
- **(A)** M3 déplace l'indice de couverture 2050 au-delà de M1.
- **(B) H-B3** : la composante pathologie explique une part de la variation
  départementale du recours standardisé que l'âge seul n'explique pas :
  R² additionnel ≥ 0,10 (h) hors échantillon.

## Données (jeu, millésime, grain)
- **Prévalences** `prev(g,d,a,s)` : jeu `effectifs` de la cartographie des
  pathologies (CNAM, data.ameli.fr, ODbL), département × tranche
  quinquennale jusqu'à 95+ × sexe × groupes fins, **année 2024** (dernière de
  la série 2015–2024 (s)). Cellules < 11 patients masquées (s) : imputées à 5
  (milieu de 1–10) ; sensibilité à 1 et à 10.
- **Actes par cas** `n(p,g)`, voie (i) observée : jeu `depenses` (national,
  par pathologie et par poste : soins infirmiers, kinésithérapie,
  sages-femmes, dentaires, médicaments) (s), montant divisé par le prix moyen
  de l'acte d'Open DAMIR 2025 (montant / quantité, national). C'est la voie
  principale. La voie (ii), norme réglementaire, n'est rapportée que pour les
  SF et seulement si le texte est lu avant le passage.
- **Terme hors pathologie** `r₀(p,a,s)` : résidu national, recours total par
  âge et sexe (profil P1 ou P2 de P-B1) moins la part attribuée aux groupes.
- **Projection** : Omphale 2022 central, 2026 et 2050 ; prévalences par âge
  et sexe **constantes** au niveau départemental de 2024 (h).
- **Recours observé (test B)** : `R_std` de P-B2 (patientèle 2023–2025), donc
  4 professions ; les pharmaciens n'entrent que dans (A).
- **Effectifs** : comme P-B1.

## Statistiques et seuils
**(A) Indice.**
- `C₃/C₁` en 2050, par département ; `S₃ = part des départements où
  |C₃/C₁ − 1| < 0,02` ; `ρ = Spearman(C₃, C₁)`.
- **M3 est réduit au recoupement** pour la profession si `S₃ > 0,90` **et**
  `ρ ≥ 0,98`, avec les seuils supposés de P-B1. Sinon M3 est retenu comme
  estimateur de l'indice.
- Pas d'inférence (calcul déterministe), donc pas de correction de
  multiplicité. La sensibilité aux cellules masquées (1, 5, 10) tient lieu
  d'incertitude ; la règle doit conclure aux trois imputations pour réduire
  M3.

**(B) H-B3.**
- Variable expliquée : `y = log R_std(p,d)`, déjà standardisé par l'âge.
- **Modèle âge seul** : `ŷ = constante` (R² nul par construction, c'est la
  référence naïve).
- **Modèle morbidité** : `y = α + γ · log(B₃/B₁)(p,d,2024)`, MCO.
- **R² hors échantillon** par validation croisée « une région laissée de
  côté » (13 plis, régions 2016). Chaque pli prédit les départements de la
  région exclue avec α et γ appris sur les autres :
  `R²_oos = 1 − Σ(y − ŷ)² / Σ(y − ȳ_train)²`.
- `ΔR² = R²_oos(morbidité) − R²_oos(âge seul)`.
- **H-B3 retenue** si `ΔR² ≥ 0,10` **et** si la borne basse de l'IC à
  98,75 % de `ΔR²` est > 0. **Rejetée** si `ΔR² < 0,10`. Sinon, la mention
  est « non tranchée ».

## IC
Bootstrap des départements pour (B) : on tire des départements entiers avec
remise, puis on refait la validation croisée par région sur chaque tirage.
B = 2 000, graine 20261115, IC percentile.

## Multiplicité
Bonferroni sur les **4 professions** du test (B) : IC à **98,75 %**.
Le test (A) n'est pas inférentiel.

## Triangulation (rapportée, jamais optimisée)
Si M2b survit à P-B2, on rapporte `|B₃/B₂ − 1|` par profession et par
département (médiane, quartiles). Aucun paramètre de M3 n'est ajusté pour
réduire cet écart.

## Placebo
Pour (B) : on remplace `log(B₃/B₁)` par la même quantité calculée pour une
**autre** profession, tirée d'avance dans l'ordre cyclique IDE → MK → CD →
SF → IDE. Si le `ΔR²` placebo est ≥ ½ du `ΔR²` propre, le verdict reçoit la
mention « non spécifique » : la morbidité générale du territoire explique
alors le recours, pas la morbidité propre à la profession.

## ⚑ Menaces écrites
- **Censure héritée.** La voie (i) mesure `n(p,g)` sur des actes remboursés.
  Elle hérite de la censure, mais nationalement, ce qui la dilue (dérivation
  §6 M3).
- **Construction maison.** Le passage montant → actes par un prix moyen
  national n'est pas une méthode publiée (exploration §2).
- **Prévalence = recours.** La cartographie repère les pathologies par la
  consommation de soins. Un département peu doté peut sous-déclarer sa
  morbidité : on retrouve la circularité dans `prev`.
- **Patientèle** : mêmes menaces qu'en P-B2 (département d'exercice ou de
  résidence, marge extensive).
- **Seuils supposés** : 2 %, 0,98 et 0,10 sont supposés (h).

## Règles de gel
Mêmes règles que P-B1.
