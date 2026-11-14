---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: Comment montrer qu'un estimateur du jumeau et un levier sont justes, de 1 an à 2050 ?
headline: "4 protocoles pré-enregistrés (prévision, 2050, leviers, échelle fine) gelés par empreinte SHA-256 avant tout résultat ; le niveau 3 est lancé pour les IDE"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 3
sources: [RPPS DREES 2012–2026, CartoSanté infi/kine/dent_popage 2004–2025, Atlasanté zonages conventionnels ARS (uuid c987d0e2, génération 2012), DREES Dossier n°76]
tags: [validation, axe3, pre-registration, derive-ansatz]
---

# Axe 3 — plan de validation (derive-ansatz, court)

> **Headline:** quatre protocoles, un par niveau, écrits et gelés
> (empreinte SHA-256 dans [decisions.md](../decisions.md)) **avant** de lancer
> le moindre calcul de validation. Seul le niveau 3 (infirmiers) est lancé
> dans cette session.

ETA de la session : ~30 min Claude (20–45), calibré ×0,3 sur l'historique
`eta.py stats`.

## Contrainte, en unités
Ce que la validation doit garantir, et ce qu'elle coûte :

| Niveau | Grandeur décisionnelle | Unité | Ce qui la borne |
|---|---|---|---|
| 1. Prévision ≤ 10 ans | erreur par département à h = 5 ans | points de MAPE | 2012–2026 → au plus 10 ans de recul |
| 2. 2050 | écart à la DREES et aux limites analytiques | % de l'effectif 2050 | aucun backtest possible à 24 ans |
| 3. Leviers | effet causal d'un levier | % de l'effectif de la zone | une expérience naturelle datée et des zonages ouverts |
| 4. Échelle fine | erreur selon la taille de la commune | % (P80 de \|erreur\|) | bruit de Poisson ≈ 1/√N |

Le coût est du temps Claude et machine (minutes), pas d'argent.

## Structure du problème
- **La validation est un test d'hypothèse, pas une mesure.** Le risque
  principal est le *jardin des chemins qui bifurquent* : K1 v1 a choisi la
  meilleure de 3 variantes après avoir vu les résultats
  ([K1, section correction](../../../../docs/lab/reports/2026-11-13-k1-backtest.md)).
  D'où : une variante par défaut, une métrique principale, un horizon
  principal, un seuil, fixés ici et gelés par empreinte.
- **Ce qui est connu et ce qui est appris.** L'identité comptable et le
  vieillissement sont connus ; seuls les taux et la répartition sont appris.
  Les cas limites (h → 0, h → ∞) testent donc la partie connue sans
  données.
- **Un backtest ne valide pas un levier.** Le levier change un paramètre
  que l'historique n'a pas fait varier, sauf dans une expérience naturelle.

## Cas limites qui cadrent les protocoles
| Limite | Ce qui doit sortir | Niveau |
|---|---|---|
| h → 0 | persistance : prédiction(origine) = observé | 1 et 2 |
| h → ∞, scénario stationnaire | N* = Q · C, indépendant de l'état initial | 2 |
| h < durée des études L | un changement de quota ne bouge rien | 2 |
| N → 0 (petite commune) | l'erreur relative tend vers le bruit de Poisson 1/√N | 4 |
| régulation parfaitement contraignante | croissance nette de la zone ≤ 0 | 3 |

## Ansätze retenus (un par niveau) et leur test qui tue
| Niveau | Ansatz | Test qui le tue | Prix |
|---|---|---|---|
| 1 | origines glissantes, fenêtre élargie, MAPE dép. à h = 5, IC bootstrap par département ; + prévisions 2027–2030 **déposées** | le candidat ne bat pas la meilleure référence naïve (borne haute de l'IC ≥ 0) | ~5 min machine par passage |
| 2 | reproduction du tendanciel DD76 en ratios N(t)/N(2020) ; trois limites analytiques | écart > 3 % à 2050, ou une limite violée | ~1 h Claude une fois le jumeau prêt |
| 3 | différence de différences dép. × zone, étude d'événement, placebos | pré-tendances non nulles, placebo dentistes ou zone 4 du même ordre | ~20 min, **lancé** |
| 4 | erreur par classe de taille de commune, seuil P80 ≤ 25 % | erreur non monotone en N | ~30 min |

Ansatz écarté : un backtest « long » en raccordant RPPS et CartoSanté
2004–2025. Les deux séries n'ont pas la même règle de comptage (+2–3 %
CartoSanté) ; on n'en ferait qu'une validation à 20 ans pour 3 professions
sur le seul libéral. À rouvrir si le niveau 2 échoue (ledger).

## Les quatre protocoles
1. [Niveau 1 — prévision](2026-11-14-axe3-n1-prevision.md)
2. [Niveau 2 — long terme 2050](2026-11-14-axe3-n2-long-terme.md)
3. [Niveau 3 — effet des leviers (DiD)](2026-11-14-axe3-n3-leviers-did.md)
4. [Niveau 4 — échelle fine](2026-11-14-axe3-n4-echelle-fine.md)

## Interface attendue d'un estimateur
Celle de `sante/estimators.py`, reprise par `jumeau.estimators.TwinEstimator` :
- `fit(t, fit_years, origin)` ; `t` = table (profession, territoire, sexe,
  age_lo, year, n), années ≤ origine seulement ;
- `predict(target) -> Series` indexée par (profession, territoire) ;
- facultatif, pour le niveau 2 : `trajectory(until, scenario)`.

Le code de validation est dans [`v2/validation/`](../../../validation/) et ne
dépend pas de l'intérieur du jumeau.
