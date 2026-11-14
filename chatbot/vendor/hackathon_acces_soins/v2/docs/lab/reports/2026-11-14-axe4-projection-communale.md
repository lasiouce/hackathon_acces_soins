---
type: analysis
date: 2026-11-14
author: axe 4 (données)
question: Quelles données l'axe 2 peut-il utiliser pour une projection communale fiable : pharmaciens par commune et par an, historique des sages-femmes, tables de passage, petits effectifs ?
headline: "Pharmaciens par commune 2012–2026 reconstitués (Σ = DREES dép. ; erreur médiane 16 % à la commune, 10,7 % à l'EPCI contre l'Annuaire : test échoué de peu) ; sages-femmes : historique communal non disponible (5 routes testées) ; passage COG 2026 pour 39 227 codes ; médiane privée par EPCI : SF 2,5 · CD 8 · PH 16,5 · MK 23,5 · IDE 53"
status: done
professions: [pharmaciens, sages-femmes, dentistes, kines, infirmiers]
hypothesis: chantier « projection communale fiable » (decisions.md) ; modèle hiérarchique de l'axe 2 ; N4 de l'axe 3
sources: [FINESS historique 2004–2025, DREES RPPS 2026-07-02, Annuaire Santé 2026-11-13, CartoSanté TJS, data.ameli.fr, Insee COG 2026 (événements), BV2022, geo.api.gouv.fr]
tags: [data, axe4, commune, pharmaciens, sages-femmes, passage]
---

# Axe 4 — Données pour la projection communale

> **Headline :**
> - **Pharmaciens :** une série par commune et par an (2012–2026), calée sur la DREES par département.
>   Contre l'Annuaire 2026, l'erreur médiane est de **16 % à la commune et 10,7 % à l'EPCI**. Le test fixé avant
>   le calcul demandait ≤ 10 % à l'EPCI : il **échoue de peu**.
> - **Sages-femmes :** pas d'historique communal en données ouvertes.
> - **Tables de passage et distributions de petits effectifs :** prêtes pour l'axe 2 et pour N4 (axe 3).

## Question
Le chantier « projection communale fiable » (decisions.md) demande quatre choses à l'axe 4 :
- les pharmaciens par commune et par an ;
- un historique communal des sages-femmes ;
- des tables de passage au COG 2026 ;
- la distribution des petits effectifs.

## Result

### 1. Pharmaciens par commune et par an — `pharmaciens_commune_annee.parquet`
- **Composante officine.** Officines FINESS au 31/12/t−1 × r(dép., t), avec r = pharmaciens du secteur
  « Pharmacie » (DREES, 1/1/t) / officines du dép. La somme des communes égale la DREES par département, par
  construction.
- **Hors officine** (laboratoires, industrie, établissements, autres). Total DREES du dép. par statut (prive /
  public / ambigu), réparti selon les parts communales de l'Annuaire du 13/11/2026, **tenues fixes dans le
  temps** (supposé). Quand un statut manque dans un dép., on prend les parts tous statuts.

| Contrôle (mesuré) | Valeur |
|---|---|
| Σ communes − DREES dép., 1 530 dép.-années | 0 % sauf Mayotte 2012–13 (−62 à −71 % : pas d'officines FINESS avant 2014) |
| Officine 2026 reconstituée / Annuaire (pharmaciens en SA33) | 50 196 / 50 664 (−0,9 %) ; corrélation par commune 0,98 |
| Erreur absolue relative, communes ≥ 5 pharmaciens d'officine (2 381) | médiane **16,1 %**, p90 45,5 % — seuil 25 % : passe |
| Idem, EPCI ≥ 5 (1 145) | médiane **10,7 %**, p90 32,7 % — seuil 10 % : **échoue** |

**Série nationale :**
- officine : 50 665 (2012) → 50 196 (2026) ;
- privé, centrale : 63 892 → 63 608 ;
- hors officine public : 6 161 → 8 116.

**Lecture :** le ratio départemental pharmaciens / officine ne tient qu'en moyenne. Les grandes officines des
pôles urbains ont plus d'adjoints. Usage : une bande de ±11 % (médiane) à 33 % (p90) à l'EPCI.

### 2. Sages-femmes : historique communal — **non disponible**
| Route | Résultat | Coût |
|---|---|---|
| CartoSanté `sf_popage` (stock × âge) | modalités d'âge libellées en années, grille cassée après 10 ans | rapport grain communal |
| CartoSanté `sf_datcom.actifs` (actives toute l'année, 2017–2025) | 9 lignes par territoire, mais leurs sommes par position (6 896–7 549) ne sont aucune permutation de la série ameli (5 773 → 8 490) | ~15 min |
| CartoSanté `offre_ps.dens_sf` (densité, 17 ans) | valeurs sans ordre, -9999 fréquents ; même défaut pour `densite_kine` | ~10 min |
| data.ameli.fr | département seulement | rapport API |
| Annuaire Santé | instantané du 13/11/2026 seul | — |

- **Repli :** parts communales de l'Annuaire 2026 × série départementale (ameli, DREES). C'est **modélisé, non
  observé** : le passé communal est supposé distribué comme en 2026.
- **Seule voie vers une vraie série :** l'archivage de l'Annuaire (`archive_annuaire.py`), qui ne vaut que
  pour l'avenir.
- **Coût total de la recherche :** environ 40 min.

### 3. Tables de passage — `passage_commune.parquet`
- **Ce qu'elle couvre :** 39 227 codes sources, soit 34 966 communes 2026, 45 arrondissements, 4 213 anciens
  codes et 3 communes PLM agrégées. Chacun mène à un géocode du jumeau, puis à la commune parente, l'EPCI (2026),
  le bassin de vie 2022, le département et la région.
- **Fusions :** les anciens codes sont ramenés au COG 2026 par le fichier Insee des événements depuis 1943,
  appliqué transitivement.
- **Trous :** sans EPCI, seulement des collectivités d'outre-mer hors champ (975, 977, 978, 984, 986–989) et
  4 communes insulaires sans EPCI (dans les dép. 22, 29, 85). Sans bassin de vie, seulement les collectivités
  d'outre-mer.

### 4. Petits effectifs — `petits_effectifs.parquet`, `petits_effectifs_classes.csv`
Ces tables donnent, pour trois mesures, l'effectif par unité : commune (34 917), EPCI (1 255), bassin de vie
(1 707) et département. Les trois mesures sont :
- les privés de l'Annuaire 2026 ;
- les libéraux CartoSanté 2025 ;
- les pharmaciens reconstitués 2026.

Médianes à l'EPCI (privés, Annuaire) :
| Profession | Commune 0 / 1–4 / 5–29 / 30–99 / ≥ 100 | EPCI : médiane | EPCI < 5 | Pros dans une EPCI < 30 |
|---|---|---|---|---|
| Infirmiers | 22 647 / 6 252 / 4 868 / 768 / 382 | 53,2 | 5 | 2,6 % |
| Kinés | 25 262 / 5 862 / 3 237 / 436 / 120 | 23,5 | 71 | 10,3 % |
| Pharmaciens | 26 694 / 5 663 / 2 216 / 273 / 71 | 16,5 | 105 | 18,5 % |
| Dentistes | 29 529 / 3 746 / 1 378 / 216 / 48 | 8 | 427 | 19,9 % |
| Sages-femmes | 31 939 / 2 601 / 319 / 49 / 9 | 2,5 | 878 | 40,0 % |

## How
- **Scripts :**
  - [`build_pharmaciens.py`](../../../data/build_pharmaciens.py) (≈ 5 s) ;
  - [`build_passage.py`](../../../data/build_passage.py) (≈ 10 s).

  Tous deux s'exécutent après `build_secteur`, `build_annuaire`, `build_commune` et `build_finess_histo`.
- **Téléchargements :** aucun nouveau, hors les sondes CartoSanté au département (quelques ko chacune).

## ⚑ What could make it wrong
- **Parts hors officine fixes :** 2026 est projeté sur 2012. Les déplacements de laboratoires et d'industrie
  ne sont pas vus.
- **Ratio pharmaciens / officine uniforme dans le département :** c'est la source de l'échec à l'EPCI.
- **Statut « ambigu » (activité sans FINESS juridique, hors libéral) :** compté à 0,5 dans la centrale.
- **Petits effectifs :** les trois mesures n'ont pas la même définition (privé large, libéral FNPS,
  reconstitué). Ne pas les mélanger dans un même seuil.

## → What it changes
- **Axe 2 :**
  - pharmaciens : une série communale existe, avec sa bande ;
  - sages-femmes : rester au département, avec répartition 2026 ;
  - tables de passage pour toute agrégation.
- **Axe 3, N4 :** `petits_effectifs_classes.csv` donne les classes par unité et profession.

## ? Next
| Item | Cost |
|---|---|
| Ratio pharmaciens / officine par taille (pôle urbain vs rural) pour passer le seuil à l'EPCI | ~1 h |
| Repli SF : parts communales Annuaire × série ameli dép., avec une bande | ~20 min |
| Deuxième instantané de l'Annuaire dès republication | 2 min + temps du monde |
