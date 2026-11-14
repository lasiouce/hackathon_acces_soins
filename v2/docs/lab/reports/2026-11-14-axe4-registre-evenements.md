---
type: analysis
date: 2026-11-14
author: Claude (session axe 4)
question: Quels événements datés et sourcés expliquent les ruptures des flux (formation, diplômés, installation) pour SF, CD, PH, MK, IDE ?
headline: "30 événements datés 2009–2028 dans v2/data/events.csv (23 vérifiés, 7 partiels) ; l'année blanche MK 2018 se voit dans le RPPS (moins de 25 ans : 5 637 → 3 681, −35 %) ; le saut d'inscrits 2025 en odontologie est un artefact de fichier (Paris Cité 683 au lieu de ~190)"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: scénario du jumeau = hyperparamètres + événements datés (contrat axe 0)
sources: [Légifrance, ameli.fr (avenants), Conseil d'État, DREES ER 1159, ARS PACA, Ordre des pharmaciens, fichiers d'inscrits DREES de l'équipe]
tags: [data, axe4, evenements, reformes]
---

# Axe 4 — Registre d'événements daté et sourcé

> **Headline :** `v2/data/events.csv` liste **30 événements** (2009–2028), chacun avec sa date d'effet, la
> profession, le flux touché, le type, la source ouverte et son millésime. 23 sont lus tels quels sur la
> source, 7 sont partiels (date ou chiffre en partie déduits). Le « saut d'inscrits 2025 » n'est pas une
> réforme : c'est **un artefact du fichier 2025-26** (une ligne, Université Paris Cité).

## Question
Le scénario du jumeau lit des événements datés (`Event(param, start, …)`, décision « contrat du jumeau »).
Il faut savoir quelles ruptures des séries sont des réformes, avec leur date d'effet.

## Result

| Flux touché | N | Événements clés (date d'effet) |
|---|---|---|
| Régulation de l'installation | 11 | IDE 18/04/2009, 27/05/2012, 13/06/2019, 06/05/2026 · MK 14/01/2012, annulé CE 17/03/2014, 01/07/2018, avenant 7 25/08/2023 (effet par ARS) · SF 15/09/2012, 11/09/2015 · CD 01/01/2025 |
| Capacité de formation | 7 | numerus apertus rentrée 2020 ; objectifs 2021–2025 (81 055, dont PH 17 065, CD 7 265, SF 5 220) ; 8 sites d'odontologie rentrée 2022 ; plafonds supprimés 07/05/2026 ; objectifs 2026–2030 minimaux (94 095, dont PH 18 670, CD 8 625, SF 5 570) ; IFSI via Parcoursup 2019 ; nouveau référentiel IDE 2026, durée inchangée, sans année blanche |
| Durée des études | 4 | IDE LMD 2009 · MK 3 → 4 ans en IFMK, rentrée 2015 · SF 6 ans : loi 25/01/2023, décret 2024 (entrée en 2e année à la rentrée 2024) |
| Diplômés | 2 | **MK : année blanche 2018** (2 820 diplômés en 2017) · **SF : (quasi) aucune diplômée en 2027-28** (déduit) |
| Compétences | 3 | IPA 2018 · vaccination antigrippale en officine 2019, tous vaccins 11 ans et plus 2023 |
| Installation (officines) | 1 | ordonnance 2018-3, seuils de population |
| Données | 2 | rupture ADELI → RPPS (MK, 2017) · artefact d'inscrits 2025-26 |

**Contrôles contre des totaux connus** (mesurés) :
- **Année blanche MK 2018 → stock RPPS au 1er janvier 2019** : kinés de moins de 25 ans, 5 637 (2018) puis
  **3 681 (2019), −35 %**, puis remontée à 5 126 en 2026 ✔.
- **Saut d'inscrits 2025** : la 2e année d'odontologie vaut 2 083 dans `990_drees_mmop2_2526.xlsx`, dont
  **683 à l'Université Paris Cité** (188 à 215 en 2020–2024, 193 en 3e année) ✔ (recompté par cette session).
  Le fichier compilé `Base inscrits 2ème cycle MOP.xlsx` donne 1 588 au national, dans la tendance
  (1 546 en 2024). Même gonflement à Paris Cité en médecine (2 113) et en pharmacie (747), selon la recherche
  (non recompté ici).
- **CD, zones non prioritaires = 5 % de la population** (ARS PACA) : la table de zonage donne 4,8 %
  ([rapport zonage](2026-11-14-axe4-zonage-commune.md)) ✔.

## How
- **Data :** sources ouvertes, chaque URL ouverte et le fait lu sur la page ou dans le PDF (sous-agent de
  recherche, 96 appels, 2026-11-14). Colonnes : `id, date_effet, profession, flux_touche, type, description,
  source, millesime, confiance`.
- **Method :** une ligne par texte ou par fait observé. Quand seule l'année est connue, la date est la
  rentrée (01/09) ou la fin d'année universitaire, et la description le dit.
- Fiches : `v2/docs/lab/fiches/data-ev-*.md`, une par événement (30).

## ⚑ What could make it wrong
- **7 lignes partielles**, dont deux qui comptent pour les flux :
  - l'année sans diplômées SF 2027-28 est **déduite** du calendrier, pas écrite par la source ;
  - l'avenant 7 kinés prend effet **à des dates différentes selon les ARS** : la date du JO n'est qu'une borne.
- Les bornes min / max des objectifs 2021–2025 n'ont pas été lues (site ONDPS inaccessible) ; les chiffres
  plus bas de L'Etudiant semblent être les bornes basses.
- Les sources secondaires (presse spécialisée, FHF, Ordre) portent 12 lignes ; le texte primaire (Légifrance)
  reste à ouvrir pour ces lignes.
- La cause de l'artefact Paris Cité est inconnue (étudiants PASS/LAS codés en 2e année : supposé).

## → What it changes
- **Pipeline (`sante/pipeline.py`, v1) et module `formation` (axe 0) :** utiliser 1 588 (fichier compilé),
  ou la ligne Paris Cité remplacée par ~190, pour la 2e année d'odontologie 2025-26. Le saut ne doit pas
  passer dans les entrées 2030+.
- **Scénario du jumeau :** les événements « durée des études » et « diplômés » (MK 2018, SF 2028) sont des
  `Event` sur le flux de diplômés ; les avenants donnent les dates d'activation du module `regulation`.
- **Axe 3 :** E2 (kinés) a sa date d'annulation sourcée (CE n° 357594, 17/03/2014).
- **Banc :** la rupture ADELI → RPPS (MK, 2017) et l'année blanche 2018 expliquent une partie de l'erreur
  kinés autour de 2018–2019.

## ? Next
| Item | Cost |
|---|---|
| Ouvrir les textes primaires (Légifrance) des 12 lignes à source secondaire | ~45 min |
| Dates d'effet de l'avenant 7 kinés par ARS (17 arrêtés de zonage) — même travail que la datation du zonage | ~1 h |
| Bornes min / max des objectifs 2021–2025 et bilan ONDPS (places SF perdues, pharmacie au plancher) | ~30 min, site ONDPS à réessayer |
| Expliquer l'artefact Paris Cité (contact DREES ou notice du fichier) | 15 min + attente |
