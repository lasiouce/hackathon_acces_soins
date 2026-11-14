---
type: analysis
date: 2026-11-14
author: axe 4 (données)
question: Quelles données communales ouvertes peuvent alimenter le modèle de choix d'installation (axe 2) : flux, ouvertures d'officines, attributs des communes ?
headline: "Proxy d'installations nettes par commune 2012–2025 (IDE, MK, CD ; Σ communes = département à ≤ 0,34 % pour MK et CD) mais il ne voit pas toute l'année blanche kinés 2018 (0,90, seuil 0,8 : échec) ; 20 083 officines en 2025 (Ordre 1/1/2025 : 20 242, +0,4 % fin 2024) avec 251 fermetures pour 10 ouvertures ; table d'attributs 35 011 géocodes × 14 ans"
status: done
professions: [infirmiers, kines, dentistes, pharmaciens]
hypothesis: variable dépendante et covariables du logit d'installation (axe 2, § 3.4)
sources: [CartoSanté *_popage, DREES RPPS / SNDS, FINESS historique 2004–2025, Insee séries de population, RP 2012/2017/2023, grille de densité 2015–2024, AAV2020, BV2022, COG 2026 (événements), geo.api.gouv.fr, Annuaire Santé 2026-11-13]
tags: [data, axe4, flux, commune, logit]
---

# Axe 4 — Flux communaux pour le modèle de choix d'installation

> **Headline :**
> - **Proxy d'installations nettes, 2012–2025.** On a un solde par commune et par an pour IDE, MK et CD,
>   cohérent avec le département. Il ne voit qu'une fraction de l'année blanche des kinés : le test
>   pré-enregistré **échoue**. Il sert donc à **répartir** les installations entre communes, pas à mesurer
>   leur niveau national.
> - **Officines, 2004–2025.** Le stock et les flux par commune tombent à 0,4 % du total de l'Ordre.
> - **Attributs des communes.** La table commune × année est prête pour le logit.
> - **Annuaire Santé.** Le premier instantané est archivé, ce qui est la seule voie ouverte vers des flux bruts.

## Question
Le logit d'installation de l'axe 2 ([état de l'art](../explorations/2026-11-14-etat-de-lart-methodes.md), § 3.4)
demande deux choses par commune et par an : une variable dépendante (où s'installe-t-on ?) et des covariables
(population, âge, densité, distance aux pôles, zonage, offre en place). Le rapport sur le
[grain communal](2026-11-14-axe4-grain-communal.md) a montré qu'aucune source ouverte ne donne de flux
d'installation par commune.

## Result

### 1. Proxy d'installations nettes (IDE, MK, CD) — `flux_installations_commune.parquet`
I_net(c, t) = ΔN_<40(c, t) + a_dep(t−1) · N_<40(c, t−1). Ici, a_dep est la part des moins de 40 ans qui passent
40 ans dans l'année, tirée de la pyramide du département (RPPS libéral + mixte ; SNDS pour les IDE).

| Test, posé avant de lancer | Résultat (mesuré) | Verdict |
|---|---|---|
| T1 : Σ communes = même formule sur le pull départemental | 2012–2025 : ≤ 0,28 % (CD), ≤ 0,34 % (MK), ≤ 1,69 % (IDE). 2006–2011 : jusqu'à 63 % (MK) et 201 % (CD) | **passe à partir de 2012** |
| T2 : MK, année blanche 2018 (DREES ER 1159) → I_net national 2018 < 0,8 × moyenne 2016–17 et 2019–20 | 2 604 contre 2 877, soit **0,90** ; minimum 0,87 en 2019 | **échoue** |

I_net national (somme des communes) :

| | 2014 | 2016 | 2018 | 2020 | 2022 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Kinés | 4 590 | 2 571 | 2 604 | 3 520 | 3 970 | 4 444 | 3 399 |
| Infirmiers | 4 624 | 3 970 | 4 071 | 3 535 | 2 980 | 2 278 | 2 590 |
| Dentistes | 1 538 | 1 106 | 1 176 | 1 275 | 1 640 | 2 078 | 2 075 |

- **Ce que mesure le proxy :** un **solde**, entrées moins sorties avant 40 ans. Un déménagement compte −1
  dans la commune de départ et +1 dans celle d'arrivée. Le salariat n'est pas vu. Les entrées brutes sont
  donc sous-estimées.
- **Pourquoi T2 échoue (supposé, non mesuré) :** 32,5 % des kinés actifs ont un diplôme UE (rapport grain
  communal), et les primo-installés commencent souvent comme remplaçants ou assistants.
- **Usage retenu :** la part de chaque commune dans les installations nettes de son département, à partir
  de 2012 (variable dépendante en parts).

### 2. Officines, maisons et centres de santé — `finess_commune_annee.parquet`, `officines_flux_commune.parquet`
| | 2004 | 2012 | 2018 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| Officines (31/12) | 23 241 | 22 855 | 21 669 | 20 543 | 20 324 | 20 083 |
| Ouvertures | — | 6 | 7 | 12 | 3 | 10 |
| Fermetures | — | 79 | 219 | 310 | 222 | 251 |
| Maisons de santé (603) | — | 175 | 1 263 | 2 595 | 2 827 | 3 045 |
| Centres de santé (124) | — | — | 2 154 | 3 316 | 3 413 | 3 379 |

- **Identité comptable :** Δstock = ouvertures − fermetures, à 0 près chaque année.
- **Total connu :** 20 324 officines fin 2024 contre **20 242** au 1/1/2025 selon l'Ordre (+0,4 %) ; 20 543 fin
  2023 contre 20 502 (19 887 + 615) au 1/1/2024 (+0,2 %).
- **Codes communes :** les codes anciens sont ramenés au COG 2026 (événements Insee depuis 1943), et les DROM
  convertis (9A…9F → 97…). **99,9 %** des officines sont rattachées chaque année, contre 96–97 % sans
  conversion.
- **Limites :** les catégories 603 et 124 n'existent qu'à partir de 2012 et 2014. Une officine transférée sous
  un nouveau numéro FINESS compte comme fermeture + ouverture.

### 3. Attributs des communes — `commune_attributs.parquet` (490 154 lignes = 35 011 géocodes × 2012–2025)
| Colonne | Source | Couverture |
|---|---|---|
| population | Insee, séries historiques (pop. municipale) ; 2024–25 = 2023 reportée | 99,7 % ; Σ 2023 = **68 094 280 = population légale geo.api** (hors Mayotte et COM) ✔ |
| part_0_14, part_65p, part_80p | Insee RP 2012 / 2017 / 2023, interpolé | 99,7 % |
| dens7 | grille de densité 7 niveaux 2015–2024 | 99,7 % |
| aav2020, aav_cat, dist_pole_km | AAV 2020 ; distance au centre de la commune-centre la plus proche | 99,7 % ; 100 % |
| n_officines, n_maisons_sante, n_centres_sante | FINESS historique | 99,9 % des officines |
| z_<prof>_actuel, z_<prof>_2012 | zonage CartoSanté / Atlasanté | 99,7 % |
| lib_<prof>, inet_<prof> | CartoSanté + proxy ci-dessus | MK 2025 : 86 832, contre 87 076 au pull dép. (−0,3 %) |

- **Paris, Lyon et Marseille** sont par arrondissement, comme dans `zonage_commune` et `annuaire_commune`.
- La table v1 portait Paris et Lyon en commune. Contrôle : la nouvelle table égale la v1 plus exactement
  l'écart du dép. 13 (2025 : CD +780, MK +1 886, IDE +2 695).

### 4. Archivage de l'Annuaire Santé — `v2/data/archive_annuaire.py`
- **Premier instantané :** 2026-11-13, avec 813 557 activités de soin et 752 993 personnes pour les
  5 professions. Il est réduit, sans nom.
- **Calcul des flux :** vérifié sur un cas synthétique (entrée, sortie, arrivée, départ, stable). Il n'a
  pas encore tourné sur deux instantanés réels : la ressource data.gouv n'a pas été republiée le 14/11.
- **Aucune tâche planifiée créée** : la fréquence est à décider par l'équipe (open.md).

### 5. Trous restants
- **Infirmiers, secteur × âge :** pas de nouvelle source. La SAE donne des personnels par statut
  d'établissement, sans âge croisé dans les bordereaux ouverts lus par l'axe 1. H_ind reste non testée sur
  l'âge.
- **Sages-femmes, historique communal :** le texte d'un signalement à Atlasanté est prêt en annexe. Il n'est
  **pas envoyé** : c'est à l'utilisateur·rice de le faire.
- **Signaux de l'axe 1, appliqués à la séparation public / privé** (voir decisions.md) :
  - SF « Prévention » → public. La fourchette SF 2026 devient **12 059 – 13 331** (centrale 12 819).
  - Pharmaciens hospitaliers : variante SAE à **+1 116** privés.

## How
- **Scripts et ordre d'exécution** (chacun ≤ 1 min) :
  1. `build_secteur.py`
  2. `build_annuaire.py`
  3. `build_commune.py`
  4. `build_zonage.py`
  5. `build_finess_histo.py`
  6. `build_flux.py`
  7. `build_attributs.py`

  `archive_annuaire.py [--local]` tourne à part.
- **Téléchargements**, taille notée :
  - FINESS historique : 196 Mo ;
  - Insee RP 2023 : 66 Mo ;
  - grilles de densité : 2,2 à 12 Mo ;
  - AAV : 1,1 Mo ;
  - séries de population : 7 Mo ;
  - événements COG : 2 Mo ;
  - centres geo.api : 3,3 Mo.

  Tous sont sous 500 Mo, rangés dans `v2/data/raw/` (non versionné).

## ⚑ What could make it wrong
- **I_net est un solde.** Son niveau national ne suit pas les promotions (T2). Comme variable dépendante du
  logit, il suppose que la mobilité entre communes et les sorties précoces se répartissent comme les entrées.
- Le vieillissement hors de la classe des moins de 40 ans est estimé au niveau du département, pas de la
  commune.
- La population 2024–2025 est celle de 2023 reportée. L'âge est interpolé entre trois recensements.
- La distance au pôle est à vol d'oiseau, entre centres de communes.
- Le zonage n'a que deux générations, sans date d'effet par région : il ne peut pas encore varier par année.

## → What it changes
- **Axe 2, logit :**
  - variable dépendante : parts communales de I_net, 2012–2025 ;
  - covariables : `commune_attributs.parquet` ;
  - ensemble de choix : restreint par `z_<prof>_actuel == 'remplacement_seul'`.
  - Pharmaciens : le flux le plus proche est l'ouverture ou la fermeture d'officines.
- **Axe 0 :** `commune_stock` inclut maintenant Paris, Lyon et Marseille par arrondissement.
- **Axe 5 :** la variante SAE des pharmaciens (+1 116) donne la taille du premier facteur d'incertitude.

## ? Next
| Item | Cost |
|---|---|
| Deuxième instantané de l'Annuaire (dès republication) pour valider `diff` en réel | 2 min + temps du monde |
| Comparer I_net aux entrées brutes de l'Annuaire après un an d'archivage | ~1 h, dans un an |
| Dater le zonage par région pour le faire varier par année dans les attributs | ~1 h |
| Réconcilier RPPS / SAE / Ordre pour les pharmaciens hospitaliers | ~1 h |

## Annexe — texte prêt pour un signalement à Atlasanté (non envoyé)
> Objet : CartoSanté, jeu `sf_popage` (effectifs des sages-femmes libérales) : métadonnées de la dimension d'âge
>
> Bonjour,
>
> En interrogeant le service TJS de CartoSanté (`GC_tjs.php`, DescribeData puis GetData, jeu `sf_popage`,
> attribut `eft`, référentiels `dep` et `com2026`), nous constatons deux choses :
> - les modalités de la colonne `age_sf` sont libellées en années (« 2025 » … « 2012 ») et non en tranches
>   d'âge ;
> - l'ordre des lignes de GetData ne suit pas la grille année × tranche : pour Paris, aucune lecture ne
>   reproduit le total par les tranches.
>
> Les jeux équivalents (`kine_popage`, `infi_popage`, `dent_popage`) se lisent correctement. Pourriez-vous
> vérifier les métadonnées et l'ordre des lignes de `sf_popage`, ou indiquer comment obtenir les effectifs
> communaux de sages-femmes libérales par tranche d'âge et par année ?
>
> Merci, l'équipe hackathon-santé.
