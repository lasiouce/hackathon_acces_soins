---
type: exploration
date: 2026-11-15
author: session besoin-derivation (3 lecteurs web, vérification par la session)
question: "Quelles données ouvertes permettent d'estimer le besoin de soins (M0–M4) et les transferts de tâches, à quel grain et sous quelle licence ?"
headline: "Aucun jeu ouvert ne compte des actes par profession et par département : Open DAMIR s'arrête à 13 zones régionales (2009–déc. 2025, ~0,95 Go par mois) ; le département n'existe qu'en patients uniques (patientèle, sans pharmaciens) et en prévalences (pathologies) ; l'APL DREES 2022–2024 publie ses poids et ses paliers, pas de pharmaciens ; pas de distancier ouvert ; les jeux data.ameli.fr sont en ODbL"
status: final
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
sources:
  - https://www.data.gouv.fr/api/1/datasets/open-damir-base-complete-sur-les-depenses-dassurance-maladie-interregimes/
  - https://assurance-maladie.ameli.fr/content/descriptif-des-variables-de-la-serie-open-damir-base-complete
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/effectifs
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/depenses
  - https://data.ameli.fr/explore/dataset/patientele/
  - https://data.drees.solidarites-sante.gouv.fr/api/datasets/1.0/530_l-accessibilite-potentielle-localisee-apl/
  - https://www.data.gouv.fr/datasets/vaccination-grippe-2024-2025
  - https://www.ccomptes.fr/fr/publications/la-politique-de-vaccination-depuis-2018
  - https://drees.solidarites-sante.gouv.fr/publications-communique-de-presse/etudes-et-resultats/260826-temps-travail-medecins-generalistes-liberaux
  - https://metric-osrm.pages.lab.sspcloud.fr/metric-osrm-package/
  - https://download.geofabrik.de/europe/france.html
tags: [besoin, open-damir, pathologies, apl, distancier, vaccination, licences]
---

# Données ouvertes pour le module de besoin

> **Headline :** aucun jeu ouvert ne compte des actes par profession et par département. Le recours par âge n'existe
> qu'à la région (Open DAMIR, 13 zones) ; au département, on a des patients uniques (patientèle) et des prévalences
> (pathologies). L'APL DREES publie tout son paramétrage sauf l'activité individuelle. Aucun distancier communal n'est
> publié. Les jeux data.ameli.fr sont sous **ODbL**, pas sous Licence Ouverte.

## Question
Quelles données permettent d'estimer chaque ansatz de la
[dérivation du besoin](../derivations/2026-11-15-besoin-derivation.md) (M0–M4, transferts), à quel grain, et sous
quelle licence ? Vérifié en ligne le 2026-11-15 (pages, API et fichiers ouverts), pas de mémoire. Les fichiers lus
sont dans le dossier temporaire de la session, rien n'est commité.

## Résultat : tableau des jeux

| Jeu | Producteur | Grain géographique | Années (dernier millésime vu) | Variables utiles | Licence | Ansatz |
|---|---|---|---|---|---|---|
| **Open DAMIR** (base complète) | Assurance maladie, inter-régimes | **région seulement** : 13 zones depuis 2015 (DROM regroupés en 5, PACA + Corse en 93), 9 ZEAT de 2009 à 2014 ; région du bénéficiaire (`BEN_RES_REG`) **et** de l'exécutant (`EXE_INS_REG`) | mensuel, **2009-01 → 2025-12** ; ~0,92–0,96 Go compressé par mois (en-tête HTTP lu), ~11 Go par an | `PSE_ACT_SNDS` (19 dentaire, 21 SF, 24 IDE, 26 MK, 50 pharmacie) ; `PSE_STJ_SNDS` libéral/salarié ; `PRS_PPU_SEC` public/privé ; âge en **tranches décennales, 0–19 … 80+** ; sexe ; ALD ; `PRS_NAT` ~1 570 codes (3111 AMI, 3112 AIS, 3122 AMK, 1911 SF, 3360 VGP, 3415 RVA, 1959 VAX…) ; quantités et montants | Licence Ouverte | M1 (niveau, PH), prix moyen par acte (M3), `s(t)` (P-B6) |
| **Pathologies : effectifs** | CNAM, cartographie | **département** (102) et région | annuel, **2015–2024** | 17 / 48 / **61 groupes** ; âge quinquennal 0–4 … 95+ ; sexe ; patients, population, prévalence | **ODbL** | M3 (prévalence) |
| **Pathologies : dépenses** | CNAM, cartographie | **national seulement** | annuel, 2015–2024 | par pathologie × 31 postes (soins infirmiers, kinésithérapie, SF, dentaires, médicaments) : montant, recourants au poste, montant moyen ; ni âge ni sexe ; **pas d'actes** | **ODbL** | M3 (`n(p,g)`, voie observée) |
| **PS libéraux : patientèle** (déjà dans `v2/data/raw/patientele.xlsx`) | CNAM, data.ameli.fr | département, région | annuel, **2016–2025** | patients uniques par profession (38 valeurs : IDE, MK, SF, dentistes ; **pas de pharmaciens**) | **ODbL** | M2 (P-B2), backtest P-B5 |
| **PS libéraux : honoraires détaillés** | CNAM | département, région | annuel, 2010–2025 | montants par type d'honoraire ; **pas de nombre d'actes** | **ODbL** | `S_j` de M4 (ETP approché) |
| **Open Medic** | Assurance maladie | région du bénéficiaire (déduit d'un avis d'anomalie, descriptif non lu) | annuel, 2014–2025 | médicaments par ATC (dont vaccins antigrippaux J07BB), boîtes, montants, âge, sexe | Licence Ouverte | P-B6 (total des vaccinations) |
| Open PHMEV, Open Bio, Open LPP | Assurance maladie | PHMEV : établissement prescripteur ; Bio et LPP : **non vérifié** | 2014–2024/2025 | — | LO / non précisé | aucun |
| **APL DREES** (jeu 530) | DREES | **commune** (France hors Mayotte) | **2022, 2023, 2024** à la racine ; archives V0 2010/2013, V1 2015–16, V2 2015–2022 | APL en ETP pour 100 000 habitants standardisés ; population standardisée ; onglet « Paramètres » : paliers de distance, bornes d'activité, **poids d'âge DCIR (19 tranches)** | Licence Ouverte 2.0 | M4 (cible P-B4), poids `ω_a` de M1 |
| APL cardiologie | IRDES (data.gouv) | commune | SNDS et RP 2019 | contacts disponibles par habitant | Licence Ouverte 2.0 | phase 2 (spécialistes) |
| **Distancier Metric-OSRM** | Insee | toute paire, voiture | serveur OSRM 6.0, OSM du 15/10/2025 | **outil, pas de matrice publiée** ; serveur expérimental (SSPCloud) | paquet MIT ; données OSM ODbL | M4, à éviter comme dépendance |
| Localisation et accès aux équipements | Insee (data.gouv) | carreau 200 m → équipement **le plus proche** | BPE 2024, 2025 ; 28,7 Go | distance, durée | Licence Ouverte 2.0 + mention OSM/OSRM | M4 : référence « plus proche » seulement, pas un 2SFCA |
| **OpenStreetMap France + OSRM auto-hébergé** | OSM, Geofabrik | toute paire | `france-latest.osm.pbf`, 4,8 Go, métropole seule (DOM à part) | temps de trajet par `table` OSRM | **ODbL** | M4 (voie retenue) |
| Centres des communes (déjà sur disque) | geo.api.gouv.fr | commune | 2026 | coordonnées | Licence Ouverte | M4, repli vol d'oiseau |
| **Vaccination grippe en officine** | IQVIA-Pharmastat (data.gouv) | national quotidien ; régional cumulé pour 10 000 hab. | saisons 2024-25, 2025-26 (le jeu 2023-24 donne aussi le total) | actes VGP, doses J07E1, 65 ans et plus / moins de 65 ans ; panel ~60 % des officines extrapolé | Licence Ouverte 2.0 | `s(t)` de L23 |
| Cour des comptes, « La politique de vaccination depuis 2018 » (2026-09) | Cour des comptes | national | 2018–2024 | parts des vaccinations antigrippales par vaccinateur (SNDS) ; tarifs des actes ; expérimentation dans ~5 000 officines de six régions dès 2017 | rapport public | `a` de L23 ; P-B6 |
| DREES ER 1381 (2026-08) | DREES | national | panel 2025-26, déclaratif | durée moyenne de consultation de MG en cabinet : **19 min** | publication | `k` (côté MG) |
| Dépistage du diabète, tension, IPA, accès direct MK | presse, textes | — | 2024–2026 | cadres juridiques seulement ; **aucun volume ouvert** | — | aucun (levier « supposé » ou « non mesurable ») |

## Ce qui compte pour la dérivation

1. **Grain.** Open DAMIR, seule source d'actes par profession et par âge, s'arrête à la région. Au département, on a :
   - des **patients uniques** (patientèle), qui donnent une marge extensive et ne couvrent pas les pharmaciens ;
   - des **montants** (honoraires) ;
   - des **prévalences** (pathologies).

   Conséquences :
   - le profil `r(p, âge)` de M1 est national ou régional ;
   - P-B2 (saturation) et P-B5 (backtest) se font sur la patientèle départementale ;
   - à la commune, aucun recours n'est observé : M1 à la commune = population communale × profil national.
2. **Tranches d'âge.** DAMIR ferme à **80+**. Les poids APL (DCIR, quinquennaux jusqu'à 90+) montrent que c'est là
   que tout se joue pour les IDE (s) :
   - 80–84 ans : 4,50 ;
   - 90 ans et plus : 15,51.

   La **forme** du profil vient donc des poids APL (IDE, MK, CD, SF), le **niveau** de DAMIR. Pour les pharmaciens,
   on n'a que DAMIR (80+).
3. **L'APL est reproductible, sauf l'activité.** Paramètres publiés (s, onglet « Paramètres » 2024) :
   - paliers de décroissance : 1 / 2⁄3 / 1⁄3 sur 0–10 / 10–15 / 15–20 min pour CD, MK, IDE ; sur 0–10 / 10–20 /
     20–30 min pour les SF ;
   - professionnels de 65 ans au plus ;
   - 1 ETP = activité libérale médiane ;
   - bornes au 5ᵉ centile (SF) ou à 10 000 € (CD, IDE, équivalent en actes pour les MK), et au 90ᵉ centile ;
   - population N−2.

   L'activité individuelle (SNIIR-AM) n'est pas ouverte : c'est l'écart attendu principal. Il n'y a **pas d'APL des
   pharmaciens**. La méthode V0 couvrait « 10 professions », pharmaciens peut-être compris ; l'archive 7z n'a pas
   été ouverte (non vérifié).
4. **Distancier.**
   - Aucune matrice commune × commune ouverte n'a été trouvée sur data.gouv.fr.
   - Metric-OSRM est un outil qui interroge un serveur expérimental.
   - Voie robuste : OSRM auto-hébergé sur l'extrait OSM France (4,8 Go, métropole). Temps machine non mesuré.
   - Repli immédiat : vol d'oiseau entre centres de communes, × facteur de détour (supposé).
5. **Vaccination en officine : le seul transfert mesurable.**
   - Volumes : actes VGP **5 645 127** (2023-24), **6 629 119** (2024-25), **8 020 525** (2025-26 au 28/02) (IQVIA,
     extrapolé d'un panel, mesuré).
   - Parts par vaccinateur (Cour des comptes, SNDS) : pharmaciens d'un peu moins d'un tiers (2019-20) à près de deux
     tiers (2024-25) ; médecins d'une sur deux à moins d'une sur quatre ; IDE d'une sur cinq à environ une sur dix.
   - Total des injections : +3,3 M entre 2018 et 2024. C'est un indice direct d'expansion (`m > 0`), à confirmer par
     P-B6.
   - Les médecins et les SF n'ont pas d'acte de vaccination propre dans la facturation (Cour des comptes) : leur part
     ne s'isole pas dans DAMIR. Elle vient du rapport.
6. **Temps par acte (`k`).**
   - Aucune durée officielle pour une vaccination.
   - Consultation de MG : 19 min (DREES 2025, déclaratif).
   - Rapport des tarifs 9,61 € / 30 € ≈ 0,32 (d) : mauvais substitut, gardé comme borne.
7. **Licences.** Les jeux data.ameli.fr (pathologies, patientèle, honoraires) sont sous **ODbL** : une base dérivée
   redistribuée doit rester sous ODbL (partage à l'identique). Le dépôt commite les données traitées
   (`v2/data/processed/`, décision du 2026-11-14) : toute table dérivée de ces jeux doit porter l'ODbL et la mention
   des sources, ou rester hors du dépôt. Même règle pour une matrice de temps OSM. La Licence Ouverte 2.0 (DAMIR,
   Medic, APL, IQVIA) n'impose que la mention de la source.
8. **Masquage.** Pathologies : cellules de moins de 11 patients masquées (« NS ») ; effectifs apparemment arrondis à la
   dizaine (observé, non documenté). Au département, les petites pathologies × âge sont souvent masquées.

## Comment
- **Lecteurs :** trois agents web en parallèle (DAMIR et pathologies ; APL et distancier ; vaccination et transferts).
  Chacun a cité les URL ouvertes et marqué « non vérifié » ce qu'il n'a pas pu ouvrir.
- **Fichiers téléchargés et lus :**
  - descriptif DAMIR (xlsx) ;
  - fichiers APL 2024 des quatre professions et le Lisez-moi ;
  - CSV IQVIA ;
  - rapport de la Cour des comptes (texte extrait).
- **Vérification par la session :** la patientèle locale (2016–2025, 102 départements, 38 professions, sans
  pharmaciens), et la mention « six régions à partir de 2017 » dans le texte de la Cour des comptes.

## ⚑ Ce qui pourrait rendre ceci faux
- **Département de la patientèle.** Il est supposé être celui d'exercice. Le descriptif n'a pas été lu : s'il
  s'agit de la résidence du patient, P-B2 devient plus propre.
- **Région d'Open Medic.** Elle est déduite d'un avis d'anomalie, pas du descriptif.
- **Volumes IQVIA.** Ils sont extrapolés d'un panel (~60 % des officines) : ce n'est pas un recensement.
- **Recherche du distancier.** Elle n'a porté que sur data.gouv.fr. Odomatrix (INRAE) n'a pas été trouvé en
  téléchargement ouvert.
- **Méthode V0 de l'APL.** Elle pourrait contenir une APL des pharmaciens. L'archive n'a pas été ouverte.

## → Ce que ça change
- **Dérivation :**
  - M1 prend sa forme dans les poids APL et son niveau dans DAMIR ;
  - M2 est testé sur la patientèle et ne s'applique pas aux pharmaciens ;
  - M3 combine les prévalences départementales et les dépenses nationales ;
  - M4 reprend les paramètres publiés ;
  - L23 est le seul transfert mesuré.
- **Registre :**
  - question ouverte sur la licence ODbL des tables dérivées ;
  - question de périmètre sur la médecine générale.
- **Plan de construction :** l'axe 4 commence par un filtrage en flux de DAMIR. On ne garde que les agrégats, jamais commités.
  Fenêtre réduite le 2026-11-15 à ~37–49 fichiers (~35–47 Go, dérivé) au lieu de ~190 Go pour 2009–2025.
- **Pas d'API de requête pour Open DAMIR** (vérifié le 2026-11-15) : un CSV compressé par mois, lien à jeton sur la
  page `download.php` ; l'API de data.gouv.fr ne donne que les métadonnées ; DAMIR n'est pas dans le catalogue
  Opendatasoft de data.ameli.fr.

## ? Suite
| Point | Coût |
|---|---|
| Lire le descriptif de la patientèle : département d'exercice ou de résidence ? | ~5 min |
| Ouvrir l'archive APL V0 2010/2013 : y a-t-il des pharmaciens ? | ~15 min |
| Sourcer la liste et les dates des régions de l'expérimentation 2017–2019 (arrêtés) | ~15 min |
| Mesurer le temps machine d'OSRM `table` sur 35 000 communes à 30 min | ~30 min Claude + machine inconnue |
| Lire le descriptif d'Open Medic (grain, J07BB) | ~10 min |
| Vérifier `depenses-par-poste` et `demographie-effectifs-et-les-densites` (data.ameli.fr, API) : grain départemental ? | ~5 min |
