---
type: analysis
date: 2026-11-15
author: session besoin-v2-m4
question: M4 (2SFCA aux paramètres DREES) reproduit-il l'APL DREES 2024 commune par commune pour IDE, MK, SF et CD, mieux que deux densités naïves ? (P-B4, protocole gelé)
headline: "P-B4 échoue sur OSRM (voie principale) pour les 4 professions : Spearman M4–APL 2024 de 0,71 (SF) à 0,76 (MK), sous 0,90 ; erreur médiane 23 à 33 %, au-dessus de 15 % ; gain sur la meilleure densité naïve +0,15 à +0,35, IC 98,75 % > 0. Le temps routier ne change presque rien au repli ; accord départemental ρ = 0,98 (MK). M4 reste un indice maison"
status: done
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

## Amendement A1 — passage 2 sur OSRM (écrit le 2026-11-15 à 03:25 UTC, avant tout temps OSRM calculé)

L'utilisateur·rice a accepté le téléchargement de l'extrait OSM et l'installation d'OSRM (2026-11-15, « Yes,
OSRM »). Le passage 2 suit la voie **principale** du protocole (OSRM sur OSM, voiture, centres de communes). Son
verdict est le verdict de P-B4 ; le passage 1 (repli) reste rapporté. Aucun seuil ni aucune statistique ne change.

- **Distancier.** OSRM 26.11.0 (Homebrew), profil `car.lua` par défaut, algorithme MLD, sans trafic. Extrait
  `france-latest.osm.pbf` du miroir **download.openstreetmap.fr** (5 895 464 862 octets, modifié le 2026-11-15 à
  01:12 UTC), et non Geofabrik (1,1 Mo/s mesuré, ≈ 70 min) : même donnée OSM, découpe différente, DOM compris puis
  hors champ. Filtré par osmium aux voies (`highway`), bacs (`route=ferry`) et interdictions de tourner. Script :
  `v2/besoin/donnees/distancier_osrm.py`.
- **Paires.** Pour chaque commune i, appel `table` de i vers les communes à moins de 60 km à vol d'oiseau ; on garde
  t_ij ≤ 30 min, plus (i, i) à 0. Le temps est orienté : t_ij va de la commune de résidence i au point d'offre j
  (la conservation tient quelle que soit l'asymétrie). Une paire non routable compte comme hors d'atteinte.
- **Centres.** Ceux de geo.api.gouv.fr, comme le repli (pas la mairie du distancier Metric), accrochés par OSRM à la
  route la plus proche.
- **Complément du 2026-11-15 à 04:42 UTC, avant tout temps OSRM calculé.** Le premier graphe (toutes voies `highway`,
  DOM compris) saturait la mémoire (`osrm-extract` arrêté après 48 min, 21 Go d'échange). Le graphe retenu est
  restreint à la métropole et à la Corse (boîte −5,4 / 41,2 / 9,8 / 51,2, `osmium extract`, voies complètes) et aux
  voies carrossables : `motorway`, `trunk`, `primary`, `secondary`, `tertiary` (et leurs bretelles),
  `unclassified`, `residential`, `living_street`, `road`, plus les bacs et les interdictions de tourner. Les voies
  `service` et `track` sont exclues (h) : un centre de commune s'accroche alors à la voie carrossable la plus proche.
- **Complément du 2026-11-15 à 04:47 UTC, avant la table complète et avant tout calcul de M4 sur OSRM.** Pour
  accélérer (pilote MLD : 240 s pour 1 000 communes, ≈ 2,3 h pour toutes, mesuré) : algorithme **CH** au lieu de
  MLD (`osrm-contract` ; même graphe, mêmes poids : les deux donnent le plus court chemin exact) et rayon de
  recherche **50 km** au lieu de 60. Sur le pilote de 300 communes, la plus grande distance à vol d'oiseau d'une
  paire à 30 min au plus vaut 46,1 km (99,9ᵉ centile 31,4 km) (m). Risque résiduel : une paire au-delà de 50 km et
  sous 30 min serait perdue (aucune sur le pilote). Le pilote n'a servi qu'à ces deux choix ; aucune APL lue.
- **Le reste est inchangé** : écarts E2 à E11 du passage 1, mêmes entrées, même bootstrap, même graine.
- **Table dérivée d'OSM, donc ODbL** : `v2/data/odbl/besoin/distancier_osrm.parquet`, non commitée (règle d'attente
  du 2026-11-15).


> **Headline :** P-B4 **échoue** pour IDE, MK, SF et CD, sur OSRM (voie principale, passage 2) comme en repli
> (passage 1). M4 classe les communes bien mieux que les deux densités naïves (+0,15 à +0,35 de Spearman, IC > 0),
> mais ne reproduit pas l'APL : ρ de 0,71 à 0,76 contre 0,90 requis, erreur médiane de 23 à 33 % contre 15 %.
> Les temps routiers ne changent ρ que de −0,01 à +0,05 : **le distancier n'est pas la cause principale**. M4 est un
> **indice maison**, jamais présenté comme l'APL.

## Question
H-B4 ([dérivation](../derivations/2026-11-15-besoin-derivation.md), §6 M4) : M4, avec les seuls paramètres publiés,
reproduit-il l'APL 2024 au grain communal ? Décide si M4 peut être appelé « la méthode de l'APL »
(registre, [entrée du 2026-11-15](../decisions.md)).

## Result
APL 2024, entrées 2022, 34 778 communes métropolitaines (m). IC à 98,75 % (bootstrap de 96 départements,
B = 2 000, graine 20261115).

### Passage 2 — OSRM (amendement A1) : verdict de P-B4

| Profession | ρ_M4 [IC] | EM [IC] | ρ_N1 | ρ_N2 | G [IC] | ρ ≥ 0,90 | EM ≤ 15 % | G ≥ 0,05, IC > 0 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Infirmiers | 0,717 [0,670 ; 0,760] | 22,7 % [21,4 ; 24,3] | 0,333 | 0,570 | +0,147 [0,103 ; 0,204] | non | non | oui | indice maison |
| Kinés | 0,756 [0,720 ; 0,788] | 27,5 % [26,1 ; 29,0] | 0,381 | 0,565 | +0,191 [0,142 ; 0,252] | non | non | oui | indice maison |
| Sages-femmes | 0,713 [0,683 ; 0,743] | 26,5 % [24,7 ; 28,6] | 0,224 | 0,359 | +0,354 [0,318 ; 0,392] | non | non | oui | indice maison |
| Dentistes | 0,725 [0,701 ; 0,750] | 32,8 % [31,1 ; 34,6] | 0,333 | 0,425 | +0,299 [0,254 ; 0,345] | non | non | oui | indice maison |

**Contrôle bloquant :** conservation `Σ P·A = Σ S` à 2,1 × 10⁻¹⁶ au pire (m) ; aucune offre perdue.
**Distancier** (m) : 34 881 communes, 2 997 245 paires à 30 min au plus, 0,004 % de paires non routables,
asymétrie médiane 0,16 min, toutes les communes APL 2024 métropolitaines présentes ; 327 s de calcul.

### Passage 1 — repli à vol d'oiseau (rapporté)

| Profession | ρ_M4 [IC] | EM [IC] | G [IC] | Verdict |
|---|---|---|---|---|
| Infirmiers | 0,718 [0,659 ; 0,767] | 21,2 % [19,9 ; 23,0] | +0,148 [0,118 ; 0,185] | indice maison (repli) |
| Kinés | 0,766 [0,726 ; 0,803] | 23,5 % [22,3 ; 24,9] | +0,201 [0,167 ; 0,244] | indice maison (repli) |
| Sages-femmes | 0,662 [0,627 ; 0,695] | 26,9 % [25,1 ; 28,9] | +0,302 [0,271 ; 0,339] | indice maison (repli) |
| Dentistes | 0,736 [0,711 ; 0,760] | 29,4 % [27,7 ; 31,1] | +0,310 [0,271 ; 0,351] | indice maison (repli) |

### Rapporté, non décisif (passage 2)
| Profession | ρ < 1 000 hab. | ρ 1 000–10 000 | ρ > 10 000 | ρ 2023 (entrées 2021) | κ (APL 2022) | EM 2024 × κ | ρ, P^std Omphale (E2) | moyenne M4 / APL |
|---|---|---|---|---|---|---|---|---|
| Infirmiers | 0,668 | 0,793 | 0,876 | 0,717 | 0,988 | 22,5 % | 0,686 | 153 / 150 |
| Kinés | 0,694 | 0,800 | 0,858 | 0,751 | 1,160 | 24,9 % | 0,747 | 105 / 121 |
| Sages-femmes | 0,683 | 0,701 | 0,740 | 0,689 | 1,085 | 26,0 % | 0,719 | 21,5 / 21,9 |
| Dentistes | 0,681 | 0,687 | 0,611 | 0,721 | 1,126 | 30,8 % | 0,723 | 47,1 / 61,5 |

- **Communes les plus écartées** (`v2/artifacts/besoin_pb4_osrm/ecarts_*.csv`, non commités) : la Corse reste en
  tête pour les IDE (13 sur 20) et les MK (8), moins qu'en repli ; Ariège, Isère et Puy-de-Dôme ensuite.
- **Diagnostic (d, hors protocole, passage 2, MK) :**
  - ρ = 0,77 hors de 14 départements de montagne et de Corse, 0,69 dedans ;
  - ρ = 0,75 sur les seules communes où l'APL est positive (2 % ont une APL nulle, 3 % un M4 nul) ;
  - **ρ = 0,98 au département** (Σ P·A / Σ P contre Σ P·APL / Σ P).
  Le niveau départemental est donc reproduit ; c'est la répartition **entre communes d'un même département** qui
  diverge.
- **Variante κ** (un scalaire sur l'ETP calé sur 2022) : EM gagne au plus 2,6 points. Le niveau n'est pas la cause.

## How
- **Données :** APL DREES 530 (2022–2024, LO 2.0) ; CartoSanté FNPS/SNDS au 31/12 (IDE, MK, CD : `commune_stock` ;
  SF : `sf_popage`) ; RPPS et SNDS par âge (part des moins de 65 ans) ; data.ameli.fr honoraires 2020–2022 (ODbL,
  non commités) ; OpenStreetMap (miroir openstreetmap.fr, 2026-11-15 01:12 UTC) et OSRM 26.11.0 (CH, profil
  voiture) ; geo.api.gouv.fr (centres de communes) ; BV2022 (Insee).
- **Méthode :** [`v2/besoin/estimateurs/m4.py`](../../../besoin/estimateurs/m4.py) (2SFCA, paliers DREES),
  [`v2/besoin/donnees/distancier_osrm.py`](../../../besoin/donnees/distancier_osrm.py),
  [`v2/besoin/validation/pb4.py`](../../../besoin/validation/pb4.py). Commandes :
  `uv run python v2/besoin/donnees/distancier_osrm.py` (serveur lancé ; préparation dans l'en-tête),
  `PYTHONPATH=v2 uv run python -m besoin.validation.pb4 [--osrm]` (≈ 4 min machine chacun, mesuré). Critères
  M4a–M4d dans `besoin.tests` (11/11) ; `jumeau.check` vert.
- **Antériorité :** écarts E1–E11 commités en `76c04d5` avant le passage 1 ; amendement A1 et ses deux compléments
  en `761c190`, `822c2f8` et `faac106`, avant la table OSRM complète. Deux corrections de la seule sensibilité
  Omphale (`2e8fa79`) et un découpage par tuiles des appels OSRM (même plus court chemin, 12× plus rapide) ne
  touchent pas les statistiques décisives.
- **Coût machine (m) :** téléchargement 5 min, filtrages 3 min, `osrm-extract` 17 min (pic 19 Go), partition et
  personnalisation 3 min, `osrm-contract` 14 min, table 5,5 min. Un premier graphe complet (DOM, toutes voies) a été
  arrêté après 48 min de mémoire saturée.

## ⚑ What could make it wrong
- **Offre communale (cause principale probable).** M4 reproduit l'APL au département (ρ = 0,98) mais pas entre
  communes d'un même département. Ce qui varie à ce grain : l'ETP individuel borné de la DREES (nous : une moyenne
  départementale, (h)) et la commune d'exercice (CartoSanté FNPS contre adresses SNIIR-AM). Ni l'un ni l'autre n'est
  ouvert au grain individuel.
- **Distancier.** OSRM sur OSM n'est pas Metric (centres geo.api et non mairies, profil OSRM par défaut, voies
  `service` exclues). Son effet mesuré est faible (−0,01 à +0,05 de ρ contre le repli) : il ne peut pas expliquer
  à lui seul 0,15 de ρ manquant.
- **Champ des effectifs.** Part des moins de 65 ans départementale (E3), SF des centres de santé absentes (E4), PLM
  ventilés à la population. Les CD sont 23 % sous l'APL en moyenne.
- **Seuils supposés** (0,90 ; 15 %) : aucune reproduction ouverte de l'APL pour les étalonner.

## → What it changes
- **M4 est un indice maison**, sur les deux distanciers : la sortie et la carte ne l'appellent jamais « APL » ;
  libellé « accessibilité (2SFCA, paliers DREES, indice maison) ». Registre : entrées P-B4 du 2026-11-15.
- M4 bat les densités naïves de loin et reproduit l'ordre des départements : il reste l'indice spatial du module de
  besoin, descriptif, à agréger au département pour toute comparaison avec l'APL.
- **Ledger :** lignes P-B4 et P-B4 bis fermées ; une ligne ouverte sur l'offre communale.
- Le distancier OSRM (table ODbL, non commitée) sert désormais à M4 par défaut dans P-B4 (`--osrm`).

## ? Next
| Item | Cost |
|---|---|
| Décomposer l'écart communal : remplacer S_j par une offre tirée de l'APL publiée elle-même (inversion à P connu) et mesurer ρ avec nos temps ; dit quelle part vient de l'offre et quelle part du distancier | ~45 min Claude |
| Comparer le champ des CD (CartoSanté contre APL) pour l'écart de niveau de 23 % | ~20 min Claude |
| Centres de communes à la mairie (chef-lieu) plutôt que geo.api, pour rapprocher le distancier de Metric | ~30 min Claude + 6 min machine |
