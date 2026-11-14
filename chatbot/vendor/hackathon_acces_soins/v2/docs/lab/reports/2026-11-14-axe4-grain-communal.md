---
type: analysis
date: 2026-11-14
author: axe 4 (données)
question: Quel est, par profession, le grain le plus fin qu'on peut observer, et le plus fin qu'on peut projeter honnêtement, en « libéral » (= privé) ?
headline: "Observable à la commune pour les 5 professions (Annuaire Santé, nov. 2026 ; historique 2004–2025 pour IDE, MK, CD). Projetable : bassin de vie / EPCI pour les infirmiers (médiane 35–53 privés par unité), EPCI en hiérarchique pour kinés et pharmaciens, département pour dentistes et sages-femmes. 24 % des dentistes et 32 % des kinés actifs n'ont pas de diplôme d'État français"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: grain de l'état du jumeau ; modèle hiérarchique commune ⊂ dép ⊂ région (axe 2, § 3.2) ; logit d'installation (§ 3.4)
sources: [Annuaire Santé ANS extraction libre accès 2026-11-13, CartoSanté TJS *_popage com2026 et arm2026, Insee BV2022 au 01/01/2026, geo.api.gouv.fr, FINESS 2026-05-04, DREES RPPS 2026-07-02, BTS / SNDS]
tags: [data, axe4, commune, grain, petits-effectifs]
---

# Axe 4 — Le grain communal en détail

> **Headline :** on **observe** les 5 professions à la commune : l'Annuaire Santé donne un instantané
> (nov. 2026), et CartoSanté une histoire 2004–2025 pour IDE, MK et CD. Pour **projeter** honnêtement :
> - bassin de vie ou EPCI pour les infirmiers ;
> - EPCI avec un modèle hiérarchique pour les kinés et les pharmaciens ;
> - département pour les dentistes et les sages-femmes.
>
> La commune reste un grain d'observation et de répartition. En chemin, une mesure nouvelle : **24,4 % des
> dentistes et 32,5 % des kinés actifs n'ont pas de diplôme d'État français**, surtout des diplômes UE.

## Question
Demande de l'utilisateur·rice, relayée par la session v2 : regarder en détail les données communales, pour
fixer la granularité la plus précise. Elle alimente le modèle hiérarchique commune ⊂ dép ⊂ région et le logit
d'installation de l'axe 2 ([état de l'art](../explorations/2026-11-14-etat-de-lart-methodes.md), § 3.2 et 3.4).

## Result

### 1. Inventaire des sources ouvertes à la commune

| Source | Professions | Grain | Années | Âge | Sexe | Secteur / mode | Taille | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Annuaire Santé** (ANS, extraction libre accès, data.gouv) | les 5, dont **PH** et **SF** | commune de chaque activité (arrondissements PLM) | instantané du 2026-11-13, **pas d'archive trouvée** | non | civilité | mode L / S, secteur RPPS, FINESS site et juridique, section de l'Ordre (PH) ; origine du diplôme | zip 228 Mo (832 + 280 + 56 Mo) | **retenu** : instantané communal, public / privé, diplômés étrangers |
| **CartoSanté `*_popage`** (FNPS/SNDS, actifs au 31/12) | IDE, MK, CD (libéraux) | commune COG 2026 ; arm2026 | IDE 2004–25, MK 2005–25, CD 2006–25 | 5 tranches | non (part de femmes seule) | libéral seul | ≈ 1,1 Mo compressé par pull | **retenu** : histoire communale |
| CartoSanté `sf_popage` | SF | commune | 2012–25 | 6–7 tranches | non | libéral | idem | **rejeté** : modalités `age_sf` libellées en années, grille cassée après 10 ans |
| CartoSanté `*_flux` | 9 professions | commune | 2005–25 | — | — | — | — | **ce ne sont pas des installations** : « pôles d'attraction » des patients |
| CartoSanté `offre_ps` | officines (pas les pharmaciens) | commune | 2009–25 | — | — | — | petit | contexte PH (non chargé) |
| CartoSanté `demo_ps` | spécialistes (phase 2) | commune | 2020–25 | non | non | libéral | petit | phase 2 |
| FINESS établissements (+ historique 2004–2025, 195 Mo) | structures (officines cat. 620, centres, EHPAD) | commune | 2026 (historique non chargé) | — | — | statut juridique | 36 + 12 Mo | retenu pour le statut juridique |
| data.ameli.fr | libéraux (pas PH) | **département** | 2010–25 | 5 ans | oui | libéral | API | pas de commune |
| Insee BV2022, geo.api | — | commune → bassin de vie, EPCI, population légale | géographie 2026 | — | — | — | 1 + 4 Mo | retenu (regroupements) |
| DREES RPPS / BTS / SNDS | les 5 | **département** | 2012–26 | oui | oui | secteur | déjà sur disque | référence des contrôles |

### 2. Trous comblés

| Trou | Solution | Contrôle (mesuré) |
|---|---|---|
| **Marseille** absente de la table v1 | 16 arrondissements via `arm2026`, séries 2010–2025 en ordre croissant ; avant 2010, total du reste du dép. 13 | Σ arrondissements = écart du dép. 13 **à 0 près chaque année pour les IDE** ; MK et CD : un arrondissement à série partielle (13203, 13216) reçoit le reste (23–72 kinés, 12–21 dentistes) |
| **Sages-femmes** illisibles dans CartoSanté | instantané communal par l'Annuaire (25 788 actives, dont 11 612 privées) ; pas d'histoire communale | cf. contrôle 3 |
| **Pharmaciens** absents de CartoSanté | instantané communal par l'Annuaire (72 264 actifs, dont 61 882 privés ; 90 % des activités ont un FINESS juridique) | privé Annuaire 61 882 dans la fourchette DREES 2026 (60 005 – 67 219) |
| **Infirmiers** sans âge ni sexe par secteur | `infirmiers_secteur_age_sexe.parquet` : BTS dép × secteur ⊗ salariés dép × âge × sexe sous H_ind, + libéraux SNDS | marges reproduites (≤ 1,5 personne) ; **H_ind non rejetée** sur le sexe : part de femmes privé − public, médiane 2,1 points par dép. (seuil 3 fixé avant), 88,7 % vs 87,2 % au national |

### 3. Contrôles de cohérence : Σ communes contre le département

**CartoSanté (libéraux) contre RPPS libéral + mixte (MK, CD) et SNDS (IDE)**, France, écart en % :

| Profession | Année | Même année Y | 31/12/Y vs 1/1/Y+1 |
|---|---|---|---|
| Kinés | 2022 · 2023 · 2024 · 2025 | −3,7 · −3,1 · −2,5 · −3,2 | −7,2 · −6,6 · −6,0 · −6,4 |
| Dentistes | 2022 · 2023 · 2024 · 2025 | −3,3 · −2,7 · +0,3 · −0,8 | −4,4 · −2,8 · −3,5 · −3,2 |
| Infirmiers | 2020 · 2021 · 2022 · 2023 | +3,9 · +3,5 · +4,0 · +4,7 | +2,6 · +3,0 · +4,4 · — |

- L'écart kinés connu (−5,4 % en 2025) se situe entre nos deux alignements de date : il dépend de la date de
  référence du RPPS. CartoSanté compte des libéraux actifs au 31/12 (FNPS) ; le RPPS, des inscrits avec une
  activité libérale ou mixte au 1/1.
- Écarts par département : `v2/data/processed/commune_checks.csv`.

**Annuaire (privé, nov. 2026) contre la centrale DREES 2026 par département** — écart médian (déciles 1 et 9) :
PH −3,2 % (−9,2 ; −0,3) · MK −5,5 % (−9,3 ; −0,7) · CD −10,8 % (−16,5 ; −5,5) · SF −10,8 % (−22,3 ; −1,8) ·
IDE −14,6 % (−22,8 ; −7,8).
- Les dentistes perdent 11,5 % de leurs activités sans commune dans l'Annuaire (cabinets sans adresse
  structurée) : leur total national est **+3 %** au-dessus de la DREES, mais ces activités manquent au
  niveau du département.
- Les infirmiers sont comparés au BTS 2023 + SNDS, qui double-comptent les mixtes, et l'Annuaire a 3 ans
  d'écart.

### 4. Petits effectifs : combien d'unités sous 5, 30, 100 professionnels privés (Annuaire, nov. 2026)

| Profession | Unité | Unités | 0 | 1–4 | 5–29 | 30–99 | ≥ 100 | Médiane | Pros dans une unité < 30 |
|---|---|---|---|---|---|---|---|---|---|
| Infirmiers | commune | 34 917 | 22 657 | 6 249 | 4 864 | 766 | 381 | 0 | 30,6 % |
| | bassin de vie | 1 707 | 0 | 15 | 717 | 662 | 313 | 35,5 | 5,8 % |
| | EPCI | 1 255 | 0 | 6 | 313 | 556 | 380 | 53 | 2,6 % |
| Kinés | commune | 34 917 | 25 296 | 5 855 | 3 210 | 437 | 119 | 0 | 49,8 % |
| | bassin de vie | 1 707 | 6 | 175 | 1 028 | 366 | 132 | 17 | 16,3 % |
| | EPCI | 1 255 | 4 | 69 | 648 | 362 | 172 | 23 | 10,5 % |
| Pharmaciens | commune | 34 917 | 26 704 | 5 657 | 2 213 | 272 | 71 | 0 | 57,5 % |
| | EPCI | 1 255 | 0 | 106 | 781 | 261 | 107 | 16,5 | 18,4 % |
| Dentistes | commune | 34 917 | 29 538 | 3 739 | 1 377 | 215 | 48 | 0 | 53,4 % |
| | EPCI | 1 255 | 56 | 373 | 589 | 172 | 65 | 8 | 20,0 % |
| Sages-femmes | commune | 34 917 | 31 951 | 2 592 | 316 | 49 | 9 | 0 | 69,8 % |
| | EPCI | 1 255 | 242 | 639 | 307 | 54 | 13 | 2,5 | 39,9 % |
| | département | 101 | 0 | 1 | 23 | 39 | 38 | 78 | 4,0 % |

- Tableau complet, avec les bassins de vie : `grain_petits_effectifs.csv`.
- **Bruit observé d'une année sur l'autre** (CartoSanté, |Δlog N| médian 2024 → 2025) : il dépasse le bruit de
  Poisson, puisque les stocks sont persistants, mais il décroît avec la taille. Classe 5–29 : 5 à 7 % par an.
  Classe ≥ 100 : 1,5 à 3 % (`grain_bruit.csv`). Le bruit à 25 ans est celui des **flux** : environ 5 à 10 % du
  stock par an, donc moins d'une installation par an dans la plupart des communes de 5–29 (dérivé).

### 5. Recommandation de grain

Règle : médiane ≥ 30 privés par unité, soit un bruit de Poisson ≤ 18 % (dérivé de 1/√30).

| Profession | Observable | Projetable seul | Projetable avec emprunt de force (axe 2) | Commune |
|---|---|---|---|---|
| Infirmiers | commune, 2004–2025, âge | **bassin de vie / EPCI** | EPCI | répartition |
| Kinés | commune, 2005–2025, âge | département | **EPCI** | répartition |
| Pharmaciens | commune, 2026 seul, sans âge | département | EPCI | répartition |
| Dentistes | commune, 2006–2025, âge | **département** | EPCI à tester | répartition |
| Sages-femmes | commune, 2026 seul, sans âge | **département** | — | répartition |

- **Logit d'installation (axe 2, § 3.4) :** aucune source ouverte de flux d'installation par commune.
  - Les `*_flux` de CartoSanté sont des pôles d'attraction des patients.
  - L'Annuaire n'a pas d'archive.
  - **Proxy disponible :** la variation annuelle du stock communal des moins de 40 ans (CartoSanté, IDE, MK, CD,
    2004–2025), qui donne des installations nettes.
  - **Source exacte :** archiver nous-mêmes l'Annuaire chaque mois, à partir de maintenant.

## How
- **Scripts :**
  - [`build_annuaire.py`](../../../data/build_annuaire.py) (≈ 15 s) ;
  - [`build_commune.py`](../../../data/build_commune.py) (≈ 3 s, lit le cache v1 `data/raw/cartosante/` sans
    l'écrire) ;
  - [`build_infirmiers.py`](../../../data/build_infirmiers.py) (≈ 2 s).
  - Ordre : `build_secteur.py` → `build_annuaire.py` → `build_commune.py` → `build_infirmiers.py`.
- **Sorties** (`v2/data/processed/`, non versionnées) :
  - `annuaire_commune.parquet`, `annuaire_checks.csv`, `annuaire_checks_dep.csv` ;
  - `commune_stock.parquet`, `commune_geo.parquet`, `commune_checks.csv` ;
  - `grain_petits_effectifs.csv`, `grain_bruit.csv` ;
  - `infirmiers_secteur_age_sexe.parquet`, `infirmiers_test_hind.csv`.
- **Téléchargements**, avec leur taille annoncée avant :
  - Annuaire, 228 Mo ;
  - Insee BV2022, 1 Mo ;
  - geo.api, 4 Mo ;
  - CartoSanté `arm2026` × 3, environ 1,1 Mo compressé chacun (130–143 Mo de XML).
- **Données personnelles :** l'Annuaire contient des noms. Aucune sortie ne garde de nom ni d'identifiant :
  seulement des comptes.

## ⚑ What could make it wrong
- **L'Annuaire est un instantané** (13/11/2026) ; DREES compte au 1/1. Les écarts par département mêlent date,
  règle de comptage et adresses manquantes (11,5 % des activités dentaires sans commune).
- **Statut par personne :** une activité libérale suffit pour être compté privé, conformément à la décision.
  Avec la répartition 1/k par activité, une même personne peut compter privée dans plusieurs communes, pour
  une fraction chacune.
- **H_ind (infirmiers)** n'est testée que sur le sexe, pas sur l'âge. Les jeunes infirmiers pourraient être plus
  souvent à l'hôpital public (non mesuré).
- **Sexe = civilité** déclarée, pas le sexe à l'état civil.
- **« Pas de DE français » ≠ formé à l'étranger** pour certains cas (autorisations, diplômes anciens). La part
  reste un ordre de grandeur, mesuré sur les actifs de nov. 2026.
- Le seuil « médiane ≥ 30 » est une convention (bruit ≤ 18 %), pas une validation. Seul le banc (axe 3, N4)
  peut fixer la taille minimale d'affichage.

## → What it changes
- **Jumeau (axe 0) :**
  - les infirmiers peuvent entrer dans l'état (dép × secteur × âge × sexe) ;
  - les pharmaciens et les sages-femmes ont un état communal 2026 ;
  - Marseille est dans la table communale.
- **Axe 2 :**
  - grain du hiérarchique : EPCI ou bassin de vie pour IDE et MK, département pour SF et CD ;
  - le logit d'installation n'a qu'un proxy (installations nettes des moins de 40 ans).
- **Diplômés étrangers :** 24,4 % (CD) et 32,5 % (MK) des actifs sans DE français. Le flux d'entrée « diplômés
  étrangers » de la filière (ROADMAP § 2) a maintenant un ordre de grandeur. L'hypothèse « dentistes formés à
  l'étranger » (rapport filière v1) n'est plus seulement supposée.
- **Axe 3 (N4) :** la distribution des petits effectifs est prête pour fixer la taille minimale d'affichage.

## ? Next
| Item | Cost |
|---|---|
| Archiver l'Annuaire chaque mois (script + tâche planifiée) : seule voie vers des flux d'installation individuels | ~30 min + temps du monde |
| Installations nettes des moins de 40 ans par commune (CartoSanté), comme proxy du logit | ~45 min |
| Pharmacies par commune 2004–2025 (FINESS historique, 195 Mo ; cat. 620) : flux d'ouvertures et fermetures d'officines | ~1 h |
| Grille de densité communale Insee (rural / urbain) comme covariable du hiérarchique | ~20 min |
| Tester H_ind sur l'âge : le BTS ne croise pas le secteur avec l'âge, même au national ; chercher une autre source (SAE par âge ?) | ~45 min, issue incertaine |
