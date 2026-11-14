---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: Un estimateur du jumeau prévoit-il l'effectif par département mieux que la persistance et la tendance, jusqu'à 10 ans ?
headline: "Protocole pré-enregistré, pas encore lancé : critère = MAPE dép. à h = 5 ans, borne haute de l'IC 95 % (bootstrap par département) de l'écart à la meilleure référence naïve < 0"
status: protocole gelé (non lancé)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 3 niveau 1
sources: [DREES démographie des PS 2012–2026 (data/processed/stock.parquet, millésime 2026-07-02)]
tags: [validation, axe3, backtest, pre-registration]
---

# Niveau 1 — prévision à horizon ≤ 10 ans (protocole pré-enregistré)

> **Headline:** protocole **gelé, non lancé**. Un estimateur ne peut
> annoncer de précision par département que si la borne haute de l'IC 95 %
> de *MAPE(candidat) − MAPE(meilleure référence naïve)*, à h = 5 ans, est
> **< 0**. Les prévisions 2027–2030 de la variante par défaut sont
> **déposées** avant la publication du RPPS 2027 : c'est le seul test hors
> échantillon non contaminé.

## Question
Le jumeau (axe 0) ou une méthode de l'axe 2 prévoit-il mieux que les
références naïves ? C'est le critère « Fait quand » de l'axe 2
([ROADMAP](../../ROADMAP.md)).

## Pourquoi un protocole gelé
K1 v1 a retenu, *après* avoir vu les résultats, la meilleure de trois
variantes H1, pour un écart de 0,1 point
([K1](../../../../docs/lab/reports/2026-11-13-k1-backtest.md), « What could
make it wrong »). Chaque degré de liberté ci-dessous est donc fixé avant
tout calcul. Tout ce qui n'est pas listé ici est **exploratoire** et ne
peut pas fonder d'affirmation de précision.

## Le protocole

### Données et périmètre
- `data/processed/stock.parquet` (RPPS DREES, millésime 2026-07-02),
  effectif par profession × département × sexe × âge × année.
- **Périmètre déclaré à chaque passage.** Le périmètre cible est le
  « libéral » = privé (décision 2026-11-14). Tant que la séparation
  public / privé (axe 4) n'existe pas, le banc tourne sur l'**ancien
  périmètre (libéral + mixte)** et le rapport le dit en tête. Un résultat
  ne se transporte pas d'un périmètre à l'autre.
- Département = 101 départements hors collectivités d'outre-mer ; les
  agrégats nationaux sont la somme des départements retenus.

### Fenêtres (origines glissantes, fenêtre d'ajustement élargie)
- Ajustement : de la première année disponible (2012 ; kinés : 2017, rupture
  de série 2016→17) jusqu'à l'origine *o* incluse, **au moins 5 années**.
- Origines : toutes les années *o* telles que la fenêtre fait ≥ 5 ans et
  *o* + h ≤ dernière année de la profession.
- Horizons : **h ∈ {1, 3, 5, 8, 10}**.
- Dernière année : 2026 (infirmiers libéraux : 2023).

| Profession | Origines | Horizons possibles |
|---|---|---|
| SF, CD, PH | 2016–2025 | h = 10 : origine 2016 seulement |
| Kinés | 2021–2025 | h ≤ 5 |
| Infirmiers libéraux | 2016–2022 | h ≤ 7 (donc 1, 3, 5) |

### Métriques
- **Principale (une seule) : MAPE par département à h = 5**, sur les
  départements avec **N ≥ 30 à l'origine**, moyennée d'abord par cellule
  (profession × origine), puis à poids égal sur les cellules.
  - Pourquoi la MAPE : chaque département pèse autant pour un DG d'ARS ;
    c'est aussi la métrique de K1, ce qui garde la comparaison.
  - Pourquoi h = 5 : seul horizon disponible pour les 5 professions, avec
    plusieurs origines.
- **Secondaires (rapportées, jamais décisives) :**
  - MAPE à h = 1, 3, 8, 10 ;
  - WAPE = Σ|erreur| / Σ effectif réel ;
  - **biais national signé** = Σ prédit / Σ réel − 1 ;
  - médiane et P80 de l'erreur absolue en %.

### Candidats et références
- **Références naïves** (fixes) : persistance et tendance linéaire, telles
  que `sante.estimators.Persistence` et `LinearTrend`.
- **Barre à franchir** : la référence naïve dont la MAPE principale est la
  plus basse sur les mêmes cellules. On prend la meilleure *après coup* :
  c'est un choix défavorable au candidat, donc sans biais en sa faveur.
- **Variante par défaut (seule confirmatoire) : stock-flux à taux locaux**
  (rétrécissement vers le national, poids 200 ; entrées plates à la moyenne
  de la fenêtre ; rétention plafonnée à 1). Sur le jumeau :
  `jumeau.estimators.twin_of(sante.estimators.StockFlowLocal)`. C'était le
  défaut fixé après K1.
- **Toute autre variante** (entrées par la filière, microsimulation,
  bayésien…) doit être **inscrite dans
  [`v2/validation/registry.py`](../../../validation/registry.py), datée,
  avant son premier passage**. Une variante inscrite après avoir vu ses
  résultats sur le banc est marquée *exploratoire*.

### Critère de décision
Soit Δ = MAPE(candidat) − MAPE(meilleure naïve), à h = 5, poolée.
- IC 95 % par **bootstrap des départements** : on tire les départements
  avec remise (les mêmes pour toutes les cellules, pour garder la
  corrélation), 2 000 tirages, graine 20261114.
- **Gagne** si la borne haute < 0 ; **perd** si la borne basse > 0 ;
  **égalité** sinon.
- **National** : le candidat peut annoncer une précision nationale si son
  |biais national| moyen à h = 5 est inférieur à celui des deux références.
- **Limite h → 0** : à h = 1, la MAPE du candidat ne doit pas dépasser
  celle de la persistance de plus de 1 point. Sinon le modèle a un défaut
  de démarrage (la prédiction ne colle pas à l'état observé), à corriger
  avant tout.

### Dépôt de prévisions (test hors échantillon réel)
- Toutes les origines ≤ 2026 ont été vues, au moins en partie, par K1. Le
  seul test vraiment hors échantillon est l'avenir.
- À chaque variante inscrite, on écrit les prévisions **origine 2026 → 2027,
  2028, 2030** par profession × département dans
  `v2/validation/depot/<variante>_<date>.parquet`, avec son SHA-256 dans
  decisions.md.
- Le score tombe à la publication du RPPS 2027 (vers juillet 2027), avec le
  même critère.

## Ce qui falsifierait le protocole lui-même
- Le classement change de signe entre origines (Δ < 0 pour la moitié des
  origines et > 0 pour l'autre) : la moyenne poolée masque une
  instabilité. On le rapporte ; l'affirmation devient « dépend de
  l'origine ».
- Une rupture de série (kinés 2016→17, inscrits 2025) fait exploser une
  seule cellule : on rapporte la MAPE avec et sans la cellule, mais **le
  critère reste celui du protocole**.

## How
- **Code :** [`v2/validation/forecast.py`](../../../validation/forecast.py)
  (`bench(estimators, table, design)` ; `design()` construit la grille
  ci-dessus) et [`registry.py`](../../../validation/registry.py).
- **Non lancé ici** : le jumeau est en construction, et le périmètre « privé »
  n'existe pas encore. Le code est vérifié sur données synthétiques
  seulement ([`selftest.py`](../../../validation/selftest.py)), pour ne pas
  voir de résultat avant le gel.

## ⚑ What could make it wrong
- **Contamination par K1.** Les cibles 2023 et 2026 ont déjà été vues pour
  les origines 2018 et 2021. Le banc rétrospectif reste donc *en partie*
  dans l'échantillon de conception ; seul le dépôt 2027 est propre.
- Les origines successives se recouvrent : les cellules ne sont pas
  indépendantes. Le bootstrap par département ne capte pas la corrélation
  entre origines ; l'IC est probablement trop étroit (**supposé**).
- N ≥ 30 à l'origine exclut les petits départements, où l'erreur est la
  plus forte : c'est le niveau 4 qui les couvre.

## → What it changes
- Axe 2 : aucune méthode ne peut se dire « meilleure » sans passer ce
  critère.
- Axe 0 : `TwinEstimator` doit garder `fit` / `predict` (c'est le cas).

## ? Next
| Item | Cost |
|---|---|
| Lancer le banc sur la variante par défaut du jumeau, ancien périmètre | ~10 min Claude + ~1 min machine |
| Écrire le premier dépôt 2027–2030 | ~5 min, dès que le jumeau est stable |
| Relancer sur le périmètre « privé » quand l'axe 4 livre la séparation | ~10 min |

---

## Passages (ajouté 2026-11-14)
- **Premier passage confirmatoire** : axe 2, périmètre privé ; défaut 8,68 %
  contre 9,30 % (tendance), Δ −0,63 [−0,97 ; −0,27], gagne
  ([rapport axe 2](2026-11-14-axe2-methodes.md)).
- **Stabilité par origine** ([N7](2026-11-14-axe3-n7-addendum.md) § B) : au
  privé, égalité en 2016 et 2018, victoire en 2021 seulement ; τ de Kendall
  entre classements ≤ 0,29. La clause « classement instable » s'applique.
