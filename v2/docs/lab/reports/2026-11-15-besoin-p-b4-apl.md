---
type: analysis
date: 2026-11-15
author: session besoin-v2-m4
question: M4 (2SFCA aux paramètres DREES) reproduit-il l'APL DREES 2024 commune par commune pour IDE, MK, SF et CD, mieux que deux densités naïves ? (P-B4, protocole gelé)
headline: "(passage en attente : écarts au protocole écrits avant le passage)"
status: draft
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B4 ; test d'abandon P-B4
sources: [APL DREES 530 millésimes 2022–2024 (LO 2.0), CartoSanté FNPS/SNDS au 31/12/2020–2022, RPPS DREES par secteur (secteur_stock), SNDS infirmiers libéraux, data.ameli.fr honoraires 2020–2022 (ODbL), geo.api.gouv.fr centres de communes, BV2022 Insee]
tags: [validation, besoin, 2SFCA, APL, P-B4]
---

# P-B4 — reproduction de l'APL DREES 2024 par M4 (passage du protocole gelé)

Provenance des nombres : (m) mesuré, (s) sourcé, (d) dérivé, (h) supposé.

Protocole : [`2026-11-15-besoin-p-b4-apl.md`](../../../validation/preregistered/2026-11-15-besoin-p-b4-apl.md),
gelé et horodaté (jeton FreeTSA 02:17:19 UTC, 2026-11-15). Le passage est postérieur au jeton.

## Écarts au protocole (écrits le 2026-11-15 à 03:10 UTC, avant le passage)

Aucun seuil n'est changé. Chaque écart ci-dessous tranche une ambiguïté ou constate une donnée absente, et il est
écrit avant tout calcul de M4 contre l'APL. Les entrées ont été contrôlées seules (totaux, ETP), sans croisement avec
l'APL.

- **E1 — distancier : repli.** OSRM n'est pas installé (accord de l'utilisateur·rice requis pour l'extrait OSM de
  4,8 Go). Le temps vaut 1,3 × distance à vol d'oiseau / 50 km/h, comme le protocole (h). La table de l'axe 4 porte
  un temps à 60 km/h : il n'est pas utilisé ; seule sa colonne `d_km` l'est. **Le verdict porte la mention
  « repli » et ne vaut pas reproduction** (règle du protocole).
- **E2 — P^std : colonne `pop_std` du fichier APL du même millésime.** La population Insee commune × âge
  quinquennal 2022 n'est pas sur disque (le seul fichier communal par âge, `base_cc_evol_struct_pop_2023`, a des
  tranches non quinquennales). La DREES publie la population standardisée qu'elle utilise (population N−2 × ω de
  l'onglet « Paramètres ») : c'est l'entrée même du protocole, calculée par la DREES. Contrôle hors protocole,
  rapporté non décisif : P^std recalculée par la structure par âge du département (Omphale 2022, année 2022) × ω
  figés, au même total départemental.
- **E3 — 65 ans au plus.** Les tranches communales de CartoSanté s'arrêtent à « 60 ans et plus ». L'effectif des
  60 ans et plus est multiplié par la part des 60–64 ans dans les 60 ans et plus du département (RPPS libéral et
  mixte, `secteur_stock` ; SNDS libéraux pour les infirmiers), année N−2 (d). « 65 ans au plus » est lu « moins de
  65 ans » (tranches quinquennales). Les lignes communales sans tranche (arrondissements de Marseille à série
  partielle) sont multipliées par la part des moins de 65 ans du département.
- **E4 — effectifs des SF.** La table communale du jumeau (`commune_stock`) n'a pas les SF. Ils sont lus dans la même
  source (CartoSanté `sf_popage`, com2026, FNPS/SNDS). Ordre des lignes : 14 années croissantes × 7 tranches, total
  d'abord, vérifié par la somme des tranches (écart de 8 sur 4 297 sur 3 000 communes) (m). Paris, Lyon et Marseille
  n'y figurent qu'en commune : leur effectif est réparti sur les arrondissements au prorata de la population (h).
  Les SF salariées en centre de santé, comptées par la DREES, ne le sont pas ici.
- **E5 — ETP.** `ETP_dép = h̄_dép / médiane(h̄)`, avec h̄ = honoraires moyens par professionnel « Ensemble des
  honoraires » moins « Dépassements » (honoraires sans dépassement, comme la DREES), année N−2, médiane non pondérée
  des départements métropolitains (h). Département absent : 1.
- **E6 — « état historique du jumeau ».** Lu dans la table communale observée dont le jumeau part
  (`commune_stock.parquet`, CartoSanté au 31/12), sans lancer le moteur : pour une année passée, c'est la même
  quantité.
- **E7 — unités et champ.** M4, N1 et N2 sont exprimés comme l'APL : ETP pour 100 000 habitants standardisés
  (femmes standardisées pour les SF). Champ : communes métropolitaines de l'APL 2024 dont l'APL n'est pas manquante.
  Une offre située dans une commune hors de cette liste est hors champ ; son montant est rapporté.
- **E8 — bassin de vie.** `bv2022` de `commune_geo` (Insee, BV2022 au 01/01/2026). Commune sans bassin : elle forme
  son propre bassin.
- **E9 — variante secondaire.** Le scalaire de l'ETP est cherché sur une grille de 0,500 à 2,000 au pas de 0,001,
  minimisant EM sur l'APL 2022 (entrées 2020), puis appliqué à 2024. Le millésime 2023 est reproduit avec les
  entrées 2021 et les ω du fichier 2023 (`pop_std` de 2023).
- **E10 — Spearman.** Rangs moyens en cas d'égalité (nombreux zéros de N1) ; bootstrap : un département tiré deux
  fois apporte deux fois ses communes. IC percentile à 98,75 % (quantiles 0,625 % et 99,375 %).
- **E11 — communes absentes du distancier.** Elles gardent la paire (i, i) à 0 min (poids 1), sans voisin. Aucune
  commune de l'APL 2024 n'est concernée (contrôle de l'axe 4) ; quelques communes des millésimes 2022–2023,
  fusionnées depuis, le sont (rapporté seulement).

## Result
(à venir)
