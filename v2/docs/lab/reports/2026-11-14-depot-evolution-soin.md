---
type: analysis
date: 2026-11-14
author: Claude
question: Que vaut le dépôt « Hackathon-Evolution-soin » (Pierreafeu181), et qu'en reprendre pour la v2 ?
headline: "Même famille de modèle que notre v1 (cohortes par tranches de 5 ans, taux de maintien). Plus avancé sur la démo et sur la validation (mondes simulés, backtest à 3–10 ans). Leur levier retraite avait un bug qui touche aussi le nôtre"
status: done
professions: [all]
hypothesis: axe 2, axe 3
sources: [github.com/Pierreafeu181/Hackathon-Evolution-soin (dépôt privé, lu le 2026-11-14 : README, docs/AUDIT_PROJECTIONS.md, pipeline/assumptions.json)]
tags: [prior-art, validation, levier, confidentiel]
---

# Dépôt « Hackathon-Evolution-soin » : lecture critique

> **Dépôt privé.** Il contient des données d'organisateurs sous accord de
> confidentialité (`web/public/data/students.json`). Rien de ce dépôt n'est
> copié ici. Seuls les constats de méthode sont repris, avec leur source.

## Ce que c'est
- Un observatoire Next.js statique : carte, fiche territoire, vivier
  étudiant, page Projections avec curseurs en direct et lien
  partageable.
- Un pipeline Python ; le moteur est porté en TypeScript et testé contre
  la référence Python.
- Le périmètre : SF, CD, PH, MK, IDE, en libéral + mixte (notre ancienne
  définition), par département, jusqu'en 2040. Il inclut un « besoin »
  pondéré par l'âge (Open DAMIR, un mois).
- Le modèle : cohortes en tranches de 5 ans, 1/5 qui vieillit par an, un
  taux de maintien par département × âge avec shrinkage, des entrées égales
  à la moyenne des 5 dernières années. C'est **la même famille que notre
  stock-flux v1**.

## Ce qui est meilleur que chez nous
1. **Validation par mondes simulés, où la vérité est connue**
   (`docs/AUDIT_PROJECTIONS.md`, § 2.2). Leurs résultats :
   - **+8 à +19 % de seniors** : le modèle suppose que les âges sont
     répartis uniformément dans chaque tranche ;
   - **−12 % en 15 ans** quand les entrées augmentent de 3 % par an ;
   - **20 à 25 % d'erreur** sous 100 professionnels par département, même
     dans un monde parfait.

   Notre code a les mêmes hypothèses et doit donc avoir les mêmes biais
   (non vérifié chez nous).
2. **Backtest sur toutes les origines, aux horizons 3, 5, 7 et 10 ans.**
   L'erreur croît à peu près linéairement avec l'horizon. Leur
   extrapolation à 2040 donne des fourchettes nationales de ±5 %
   (pharmaciens) à ±60 % (sages-femmes).
3. **Année de décision.** Aucun levier n'agit avant l'année en cours, et
   non l'année des dernières données. C'est pertinent pour les infirmiers,
   dont les données s'arrêtent en 2023.
4. **Une source qui nous manquait :** DREES, *Études et Résultats*
   n°1319 (déc. 2024), projections des infirmières 2021–2050, avec une
   ligne « libéral » disponible par API. C'est un point de comparaison à
   2050 pour notre axe 3, niveau 2. Il s'ajoute au Dossier n°76 (CD, SF,
   PH).

## ⚑ Ce qui concerne directement notre code
- **Levier retraite.** Leur audit (§ 3.1) montre qu'un multiplicateur
  permanent sur les sorties de la tranche ouverte 65+ allonge le séjour
  moyen bien au-delà du report annoncé : « +3 ans » ajoute en réalité 4 à
  7 ans.
  - Notre v1 (`app/levers.py:75`) et le jumeau
    (`v2/jumeau/modules/sorties.py`) appliquent `× (1 − Δ/5)` aux tranches
    60-64 **et 65+**, de façon permanente. C'est la même structure.
  - Leur correctif pour la tranche ouverte : `sortie' = sortie / (1 + n ×
    sortie)`. Il allonge le séjour moyen d'exactement n ans, avec une
    montée en charge progressive.
  - Notre contrôle « retraite +1 an → +1,1 % » (v1) est donc **à
    revérifier**.
- **Le saut des dentistes en 2025–2026** (+1 480 puis +950 par an, contre
  environ +100 auparavant). Ils le constatent aussi, sans l'expliquer.
  C'est cohérent avec notre hypothèse des diplômés à l'étranger.
- **Diplômés à l'étranger par an**, dans leur `assumptions.json` :
  dentistes 665, pharmaciens 160, SF 70, IDE 400, kinés 0 (non
  documenté). Les sources ne sont pas détaillées par valeur : **à ne pas
  reprendre sans source primaire** (axe 1).

## Ce qui ne correspond pas à notre objectif
- Une seule méthode, sans protocole pré-enregistré. Leviers nationaux
  seulement. Pas d'échelle communale : le zonage y est une part de
  population.
- Définition de « libéral » = libéral + mixte. Leurs effectifs de
  référence tous modes (48 690 CD, 75 335 PH, 26 428 SF) sont nos bornes
  hautes.
- Le moteur existe en double (Python et TypeScript). C'est utile pour un
  site statique, mais c'est un coût de maintenance. Ce type d'interface
  relève chez nous de la future couche personas.

## → Ce que ça change
- **Axe 3 :** ajouter le niveau « mondes simulés » (vérité connue) au
  protocole ; ajouter ER1319 comme comparaison à 2050.
- **Axe 0 :** revoir le levier retraite (tranche ouverte) dans
  `sorties.py`.
- **Axe 2 :** les âges en années simples ou un vieillissement intra-tranche
  non uniforme deviennent une piste prioritaire (biais sur les seniors).

## ? Pour la suite
| Point | Coût |
|---|---|
| Vérifier le biais du levier retraite sur le jumeau (+1 et +3 ans, séjour moyen en 65+) | ~15 min |
| Mondes simulés dans le protocole de l'axe 3 | ~1 h |
| Récupérer ER1319 et sa série API | ~20 min |
