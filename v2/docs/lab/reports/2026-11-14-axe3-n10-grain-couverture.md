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

---

## Résultat (ajouté après calcul ; gel 08:31, SHA-256 `d86d27c7a750`)
`PYTHONPATH=v2 uv run --with scipy python -m validation.grain` (~12 s) →
`v2/validation/out/grain_couverture.csv`, `grain_couverture_par_origine.csv`,
`grain_results.json`.

**Livrable : aucun grain fin n'est fiable, pour aucune des trois
professions.** Avec l'estimateur principal (répartition-tendance), aucun
grain n'a toutes ses classes de taille dans [75 ; 85] %. **Le grain
d'affichage reste le département** (où la bande en √h de N8 est calibrée).

Couverture de la bande à 80 %, estimateur principal, origines 2014–2020
regroupées (classes d'au moins 30 unités) :

| Classe | CD commune | CD BV | CD EPCI | IDE commune | IDE BV | IDE EPCI | MK commune | MK BV | MK EPCI |
|---|---|---|---|---|---|---|---|---|---|
| 1–2 | 83,5 | 70,2 | 68,5 | **94,0** | 82,4 | — | **92,2** | 78,6 | 69,5 |
| 3–5 | 72,6 | 73,7 | 70,5 | 80,9 | 72,8 | 67,1 | 76,5 | 77,4 | 84,3 |
| 6–10 | 74,5 | 70,7 | 69,1 | 80,4 | 74,7 | 71,9 | 74,8 | 77,8 | 77,3 |
| 11–20 | 67,7 | 71,9 | 69,8 | 82,3 | 78,1 | 78,0 | 75,1 | 74,1 | 76,6 |
| 21–50 | 65,0 | 73,3 | 72,7 | 84,9 | 74,8 | 70,8 | 70,5 | 74,4 | 75,2 |
| 51–100 | 50,7 | 56,3 | 57,3 | 70,5 | 63,9 | 70,3 | 73,2 | 79,0 | 74,8 |
| 101–200 | 33,9 | 48,7 | 51,0 | 91,9 | 58,4 | 51,4 | 49,5 | 73,1 | 69,6 |
| > 200 | — | 22,2 | 27,5 | 55,2 | 59,4 | 59,1 | 46,3 | 54,1 | 62,9 |

**Lecture.**
- **En moyenne, la bande est presque calibrée** (couverture regroupée :
  IDE 81–84 %, MK 80–81 %, CD 72–79 % selon l'origine). **Par classe de
  taille, non** : elle est trop large pour les très petites communes
  (94 % pour les IDE à 1–2) et **trop étroite pour les grandes unités**
  (22 à 59 % au-delà de 100 professionnels). La moyenne est portée par la
  masse des petites communes.
- Cause probable : les erreurs passées des grandes unités sont plus petites
  que les erreurs récentes (croissance qui s'accélère après 2015, surtout
  chez les dentistes) ; une bande tirée du passé est trop étroite.
- **Aucun autre estimateur ne passe non plus** (persistance, tendance,
  oracle) : au mieux 6 classes sur 7 (IDE, oracle, BV et EPCI).

**N_min (règle N4) par grain, estimateur principal** : CD 21 / 21 / 21
(commune / BV / EPCI) ; IDE 51 / 11 / — ; MK 21 / 21 / 21. Avec l'oracle :
CD 21 / 11 / 11 ; IDE 21 / 11 / 11 ; MK 51 / 21 / 21.

## ⚑ What could make it wrong
- Le critère « toutes les classes » est strict : une seule classe hors bande
  suffit à faire échouer un grain. C'est le choix fixé d'avance.
- Les bandes sont empiriques par classe ; une bande modélisée (√h, ou
  Poisson + dérive) pourrait passer : c'est ce que le modèle de l'axe 2 doit
  montrer, sur le même protocole.
- Le département n'est pas testé dans N10 ; son calibrage vient de N8 (autre
  construction, autre source).

## → What it changes
- **Carte** : pour IDE, MK et CD, la projection affichée reste au
  département ; à la commune, l'observé seulement, avec la projection de
  l'échelon supérieur, et la carte le dit.
- **Axe 2** : son modèle commune ⊂ EPCI ⊂ département doit faire mieux que
  ces bandes empiriques, surtout pour les unités de plus de 50
  professionnels.

---

## Jugement du modèle K3 de l'axe 2 (même protocole, sans modification)
Soumission : `v2/methodes/out/n10_soumission_k3.parquet` (commit a042415 ;
K3 inscrit à 08:41 avant passage). Jugement :
`PYTHONPATH=v2 uv run --with scipy python -c "from validation.grain import judge; judge('v2/methodes/out/n10_soumission_k3.parquet','axe2_k3')"`
→ `out/grain_axe2_k3_couverture.csv`, `grain_axe2_k3_results.json`.
Mêmes valeurs observées, même exclusion des sauts à la commune, unités à 0 à
l'origine écartées ; appariées : CD 44 928 / 51 455, IDE 98 435 / 120 575,
MK 68 491 / 87 156 (l'écart : unités exclues pour saut ou à 0 à l'origine).

**Verdict : K3 ne passe N10 à aucun grain, mais il en approche.**

| Profession | Grain | Couverture globale | Classes hors [75 ; 85] % |
|---|---|---|---|
| Dentistes | commune | 72,2 % | 5 sur 8 (1–2 : 69 % ; 11–100 : 69–73 % ; > 200 : 85,4 %) |
| | BV | 75,1 % | 3 (1–2 : 67 % ; 51–200 : 70–73 %) |
| | EPCI | 75,5 % | 3 (1–2 : 62 % ; 51–200 : 73 %) |
| Infirmiers | commune | 83,2 % | 3 (11–50 : 85–89 % ; 101–200 : 91 %) — **trop larges** |
| | BV | 85,3 % | 5 (6–50 : 86–88 % ; 1–2 : 71 % ; > 200 : 71 %) |
| | EPCI | 84,8 % | 3 (11–50 : 87 % ; > 200 : 70 %) |
| Kinés | commune | 76,4 % | 3 (21–50 : 74 % ; > 100 : 61–66 %) |
| | BV | 78,1 % | 2 (1–2 : 73,7 % ; 3–5 : 74,6 %) |
| | **EPCI** | 77,6 % | **1 seule** (1–2 : 73,0 %, 259 EPCI) |

**Lecture.**
- Par rapport aux estimateurs de référence (22 à 59 % au-delà de 100
  professionnels), **K3 corrige l'essentiel de la sous-couverture des
  grandes unités** : l'erreur départementale commune aux communes était bien
  la pièce manquante.
- Il reste deux défauts de forme : **IDE trop larges** dans les classes
  moyennes (85–91 %), **dentistes trop étroits** presque partout (69–73 %).
- **Kinés à l'EPCI** : une seule classe hors bande, de 2 points, sur 259
  EPCI. Au sens du protocole, c'est un échec ; c'est le cas le plus proche
  d'un passage.

**Conséquence.** L'affichage reste au département pour IDE, MK et CD. Une
version K4 qui corrige la largeur par profession (IDE plus étroit, CD plus
large) devra être inscrite **avant** son passage ; ce jugement montre la
cible, ce qui l'expose au risque de sur-ajustement : un passage serait à
confirmer sur les origines 2021 et suivantes, ou sur le dépôt 2027.
