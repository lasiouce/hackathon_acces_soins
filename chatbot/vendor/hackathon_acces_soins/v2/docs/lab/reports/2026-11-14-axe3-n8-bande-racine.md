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

---

## Résultat (ajouté le 2026-11-14 ; gel 08:06, SHA-256 `97ef367fd221`)
`PYTHONPATH=v2 uv run --with scipy python -m validation.probabilistic` →
`out/prob_n8_scores.parquet`, `prob_verdicts.csv`. 1 581 cellules par
estimateur (SF, CD, PH, IDE ; origines 2017–2021).

| Estimateur | CRPS log | Δ vs tendance [IC 95 %] | Couv. 50 % | Couv. 80 % | Calibrée |
|---|---|---|---|---|---|
| **jumeau_taux_locaux** | 0,0616 | −0,0045 [−0,0070 ; −0,0020] gagne | **49,2 %** | **75,9 %** | **oui** |
| axe2_shrink_hier | 0,0611 | −0,0050 gagne | 48,0 % | 76,0 % | oui |
| axe2_apc | 0,0623 | −0,0038 gagne | 48,4 % | 75,3 % | oui |
| axe2_obs_r12 (diagnostic) | 0,0606 | −0,0056 gagne | 47,8 % | 73,3 % | non |
| naive_tendance | 0,0661 | — | 49,5 % | 74,5 % | non (de peu) |
| naive_persistance | 0,0701 | +0,0040 égalité | 40,7 % | 71,3 % | non |

**Verdict : la bande en √h est calibrée pour la variante par défaut** (et
pour A2, l'APC, les âges fins, la rétention 60+, la combinaison), tout en
battant la naïve. La bande linéaire (N7-C) était trop large, la bande
empirique au même h (N6) trop étroite.

⚑ **Ce qui pourrait le rendre faux.**
- Forme suggérée par N7-C et testée sur les **mêmes** origines : succès à
  confirmer hors échantillon (dépôt 2027).
- La couverture à 80 % est à la limite basse (75,9 %), et le PIT a trop de
  valeurs en première classe (276 contre ~158 attendues) : la queue basse
  (réel sous la bande) est sous-estimée.
- Couverture moyenne : par profession ou par taille, elle peut varier.
