---
type: analysis
date: 2026-11-14
author: session axe 3
question: Pour chaque profession, quel est le grain le plus fin (commune, bassin de vie, EPCI) où une projection à 5 ans a une bande à 80 % calibrée dans chaque classe de taille ?
headline: "Protocole pré-enregistré, pas encore lancé : 3 grains × 3 professions × origines 2009–2020 ; bande P10–P90 empirique par grain × classe de taille, tirée des seules erreurs passées ; « fiable » = couverture dans [75 ; 85] % dans chaque classe d'au moins 30 unités ; plus P80 et N_min (règle N4) par grain"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes]
hypothesis: axe 3, N10 ; décision « Chantier projection communale fiable »
sources: [v2/data/processed/commune_stock.parquet (CartoSanté, axe 4, avec arrondissements de Marseille), v2/data/processed/commune_geo.parquet (EPCI, bassin de vie 2022)]
tags: [validation, axe3, commune, calibration, pre-registration]
---

# N10 — grain le plus fin et couverture des bandes (protocole pré-enregistré)

> **Headline:** protocole **gelé avant tout calcul**. Il étend N4 (gelé,
> déjà lancé à la commune avec un oracle départemental) à trois grains, à
> des projections **réelles** (sans oracle) et à un contrôle de couverture
> par classe de taille. N4 n'est pas modifié.

## Définition retenue (décision « Chantier projection communale fiable »)
**Fiable = calibrée** : la bande à 80 % contient la valeur observée dans
environ 80 % des cas au backtest. Une bande large mais calibrée passe ; une
bande étroite mais fausse échoue.

## Données et grains
- Effectifs libéraux au 31/12 par commune (CartoSanté, axe 4 : `commune_stock`),
  IDE 2004–2025, MK 2005–2025, CD 2006–2025.
- Grains : **commune** (COG 2026), **bassin de vie 2022**, **EPCI**
  (`commune_geo`). Ordre de finesse : commune < bassin de vie (1 707) <
  EPCI (1 255).
- Exclusion des sauts (> 3 écarts de Poisson d'une année sur l'autre,
  règle N4) **à la commune seulement**.

## Estimateurs (chacun projette l'unité u à h = 5)
1. **Persistance** : N_u,o.
2. **Tendance** linéaire de l'unité sur 6 ans (plancher 0).
3. **Répartition-tendance (principal)** : part de l'unité dans son
   département à l'origine × total départemental projeté par tendance
   linéaire sur 6 ans. Réel, sans oracle.
4. **Répartition-oracle** (borne, comme N4) : part × vrai total
   départemental de la cible. Non décisif.
5. Le modèle de l'axe 2, quand il sera soumis, avec ses propres bandes, et
   jugé sur les mêmes critères.

## Bande à 80 % (pour les estimateurs 1 à 3)
- r = réel / prédit, sur toutes les paires passées de **même** estimateur,
  profession, grain, classe de taille et h = 5, avec **cible ≤ origine
  courante** (aucune information future).
- Bande = prédit × [P10(r) ; P90(r)]. Au moins **50** erreurs passées dans
  la classe, sinon la cellule n'est pas jugée et elle est comptée.
- Classe de taille : celle de N4 ({1–2, 3–5, 6–10, 11–20, 21–50, 51–100,
  101–200, > 200}) selon N_u,o. Unités à 0 à l'origine : à part.

## Origines
- Prévision : toutes les origines o de 2009 à 2020 (h = 5, cibles
  2014–2025).
- **Origines jugées : 2014 à 2020** (les erreurs passées existent dès que
  o − 5 ≥ première année + 5).

## Critères
1. **Couverture** : par profession × grain × classe (≥ 30 unités jugées,
   toutes origines jugées confondues), couverture dans **[75 ; 85] %**.
2. **Grain fiable** pour une profession et l'estimateur principal : toutes
   ses classes jugées sont dans [75 ; 85] %.
3. **Livrable** : pour chaque profession, le grain le plus fin qui est
   fiable. Si aucun ne l'est : on le dit, et le département reste le grain
   d'affichage.
4. **Rapporté avec, non décisif** : P80 de |erreur| par classe, et N_min
   (règle N4 : P80 ≤ 25 % pour la classe et toutes celles au-dessus, ≥ 3
   origines sur 4 parmi 2014, 2016, 2018, 2020), par grain et estimateur.

## Ce qui falsifierait le protocole
- Couverture correcte en moyenne mais due à des compensations entre
  origines (trop large une année, trop étroite l'autre) : on rapporte la
  couverture par origine ; si elle sort de [65 ; 95] % pour une origine, on
  le signale, sans changer le verdict.

## How
- Code : `v2/validation/grain.py` ; sorties `v2/validation/out/grain_*`.
