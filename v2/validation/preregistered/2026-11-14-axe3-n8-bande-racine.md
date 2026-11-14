---
type: analysis
date: 2026-11-14
author: session axe 3
question: Une bande dont la largeur croît comme √h est-elle calibrée, là où la bande linéaire en h (N7-C) est trop large et la bande empirique au même h (N6) trop étroite ?
headline: "Protocole pré-enregistré, pas encore lancé : log N ~ Normale(log prédit, s²·h), s² = moyenne de e²/h′ sur les paires passées ; mêmes origines, critère CRPS et seuils de couverture que N7-C et N6"
status: protocole gelé (non lancé)
professions: [sages-femmes, dentistes, pharmaciens, infirmiers]
hypothesis: axe 3, N8 (ajout daté ; ne modifie ni N6 ni N7)
sources: [v2/docs/lab/reports/2026-11-14-axe3-n7-addendum.md § C (résultat), v2/docs/lab/reports/2026-11-14-axe3-n6-probabiliste.md]
tags: [validation, axe3, crps, calibration, pre-registration]
---

# N8 — bande en √h (protocole pré-enregistré)

> **Headline:** protocole **gelé, non lancé**. Il est écrit **après** avoir vu
> N7-C (bande linéaire en h trop large : « 80 % » couvre ~96 %) : c'est donc
> une hypothèse **suggérée par les données**, testée sur les **mêmes**
> origines. Un succès ici reste à confirmer sur le dépôt 2027.

## Forme
- Erreurs log passées e = log(réel / prédit), mêmes paires que N7-C
  (o′ ≥ 2016, o′ + h′ ≤ o, même estimateur et même profession, ≥ 20 erreurs).
- s² = moyenne de e² / h′ ; distribution prédictive
  log N ~ Normale(log prédit, s² · h). C'est la forme d'une marche aléatoire
  de l'erreur : variance proportionnelle à l'horizon.

## Critères (inchangés par rapport à N6 et N7-C)
- h = 5, origines 2017–2021, N ≥ 30 ; CRPS gaussien sur log N ; Δ vs
  meilleure naïve probabiliste (persistance et tendance, même bande),
  bootstrap des départements (2 000, graine 20261114).
- **Calibrée** si la couverture à 80 % est dans [75 ; 85] % **et** celle à
  50 % dans [44 ; 56] %, pour l'estimateur considéré.

## Ce qui falsifie
- Couverture hors bandes pour la variante par défaut → la forme √h ne suffit
  pas ; la bande n'est toujours pas publiable sous son niveau nominal.

## How
- `v2/validation/probabilistic.py`, fonction `n8` ; sorties
  `out/prob_n8_*`.
