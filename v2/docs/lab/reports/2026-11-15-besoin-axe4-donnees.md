---
type: analysis
date: 2026-11-15
author: session besoin-axe4-donnees
question: "Les sources du module de besoin sont-elles ingérées, au bon grain, sous leur licence, avec des totaux nationaux reconstruits égaux aux totaux publiés à 0,5 % près ?"
headline: "6 sources ingérées en 15 tables ; 1 247 contrôles réussis sur 1 276. Les 29 échecs sont expliqués : secret statistique, bénéficiaires non localisés. Le contrôle DAMIR à 0,5 % est irréalisable : aucun total publié tous régimes au même périmètre. DAMIR arrêté à 9 mois sur 49 (2025-01 à 2025-09), faute de temps : 213 s par mois à 1 flux (4,6 Mo/s), 4 flux refusés par le serveur, puis IP bloquée"
status: final
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "critères de l'axe 4 du plan de besoin"
sources:
  - https://data.drees.solidarites-sante.gouv.fr/api/datasets/1.0/530_l-accessibilite-potentielle-localisee-apl/
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/effectifs
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/depenses
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/patientele
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/honoraires-detailles
  - https://data.ameli.fr/api/explore/v2.1/catalog/datasets/demographie-effectifs-et-les-densites
  - https://www.data.gouv.fr/datasets/open-medic-base-complete-sur-les-depenses-de-medicaments-interregimes
  - https://www.data.gouv.fr/datasets/vaccination-grippe-2025-2026
  - https://www.data.gouv.fr/datasets/open-damir-base-complete-sur-les-depenses-dassurance-maladie-interregimes
  - https://www.assurance-maladie.ameli.fr/content/descriptif-des-variables-de-la-serie-open-damir-base-complete
  - https://www.assurance-maladie.ameli.fr/etudes-et-donnees/depenses-risque-statistique-mensuelle
tags: [besoin, axe4, donnees, open-damir, apl, data-ameli, open-medic, iqvia, distancier, licences]
---

# Module de besoin, axe 4 : ingestion des données

> **Headline :** 6 sources ingérées en 15 tables, une commande de reconstruction par source ; 1 247 contrôles de
> totaux réussis sur 1 276 (mesuré). Les 29 échecs sont tous expliqués par la source : secret statistique, ou
> bénéficiaires sans département. Le critère « DAMIR contre le total inter-régimes publié à 0,5 % » n'est **pas
> réalisable** : aucun total publié tous régimes au même périmètre n'a été trouvé. Le pilote DAMIR à 1 flux prend
> 213 s par mois (0,97 Go, 36,6 M lignes, 4,6 Mo/s). Avec 4 flux, le serveur a refusé les connexions, puis a bloqué
> la machine. **Limités par le temps du hackathon, nous avons arrêté DAMIR à 9 mois sur 49** (2025-01 à 2025-09) :
> ils suffisent pour M1 et M3. P-B6 passe sur Open Medic (voir plus bas).

## Question
Critères de l'axe 4 du [plan de besoin](../derivations/2026-11-15-besoin-plan.md) :
- totaux nationaux reconstruits égaux aux publiés à 0,5 % près, par profession et par année ;
- licence inscrite par table ;
- DOM déclarés.

**Contrainte d'ordre respectée :** aucune relation recours ~ offre n'a été calculée. Les protocoles de l'axe 3 ne
sont pas gelés.

## Résultat

| Source | Module | Tables | Licence → dossier | Contrôle | Réussis |
|---|---|---|---|---|---|
| APL DREES 2022–2024 (4 professions) | `apl.py` | `apl_commune`, `apl_parametres` | LO 2.0, commitée | moyenne Σ APL·pop. std / Σ pop. std = « APL moyen France hors Mayotte » publié | 12 / 12 (écart max 0,17 %) |
| data.ameli.fr : démographie | `ameli.py` | `ameli_demographie` | ODbL, hors dépôt | Σ dép. = France | 80 / 80 (0 %) |
| data.ameli.fr : patientèle | `ameli.py` | `ameli_patientele` | ODbL, hors dépôt | moyenne pondérée par les effectifs = France | 50 / 50 (max 0,27 %) |
| data.ameli.fr : honoraires | `ameli.py` | `ameli_honoraires` | ODbL, hors dépôt | Σ dép. = France | 74 / 80 |
| data.ameli.fr : pathologies, effectifs | `ameli.py` | `ameli_pathologies_effectifs` | ODbL, hors dépôt | Σ dép. = Σ régions ; Σ dép. = France | 110 / 110 ; 87 / 110 |
| data.ameli.fr : pathologies, dépenses (national) | `ameli.py` | `ameli_pathologies_depenses` | ODbL, hors dépôt | Σ postes = total par pathologie | 795 / 795 |
| Open Medic ATC4 J07 (2014–2025) | `medic.py` | `medic_vaccins` | LO 2.0, commitée | Σ régions × âges × sexes = national, J07BB | 24 / 24 (0 %) |
| IQVIA vaccination grippe (2020-21 à 2026-27) | `iqvia.py` | `iqvia_campagne`, `iqvia_quotidien`, `iqvia_regional` | LO 2.0, commitée | Σ quotidien = total de campagne | 12 / 12 (< 10⁻⁵) |
| Open DAMIR (fenêtre décidée) | `damir.py` | agrégats mensuels ; `damir_profils`, `damir_vaccination` | LO 2.0 ; agrégats bruts hors dépôt (~0,7 Go) | **aucun total publié au même périmètre** ; rapport DAMIR / régime général publié à titre d'information | — |
| Distancier à vol d'oiseau | `distancier.py` | `distancier_vol_oiseau` (9,8 M paires ≤ 35 km) | LO 2.0, hors dépôt (100 Mo, ~10 s) | symétrie ; communes de l'APL 2024 couvertes | 2 / 2 (100 %) |

Le détail est dans le [manifeste](../../../besoin/donnees/MANIFEST.md) et `v2/besoin/donnees/controles.csv` (une ligne
par contrôle).

**Échecs, tous expliqués à la source (mesuré) :**
- **Honoraires SF 2010–2015 (6), écart de 0,8 à 2,3 %.** Entre 5 et 13 départements sont masqués (secret
  statistique : moins de 5 professionnels). L'écart disparaît dès 2016 et la fenêtre du besoin commence en 2015.
- **Pathologies, Σ dép. contre France (23), écart de 0,50 à 2,9 % en 2015–2022.** Σ départements = Σ régions à
  0,04 % près (110 sur 110). La ligne France compte en plus des bénéficiaires sans région attribuée : 1,40 % de la
  population de la cartographie en 2015, 0,34 % en 2024. C'est un écart de champ, pas de lecture.

**Constats de lecture (descriptifs lus) :**
- **Patientèle :** c'est le **nombre moyen** de patients uniques par professionnel (file active moyenne), pas un
  total. Le département est celui des professionnels, déduit du libellé (la page « Méthode » n'a pas été lue). Il
  n'y a pas de pharmaciens. Pour P-B2 et P-B5, total ≈ moyenne × effectif.
- **Codes data.ameli.fr :** le département « 999 » est le total de la région de la ligne ; la France entière est en
  région « 99 ». Les compter ensemble double le total (observé, puis corrigé).
- **Open Medic :** `BEN_REG` est la région de **résidence** du bénéficiaire (confirmé). L'âge ne compte que 3
  tranches (0–19, 20–59, 60+), sur l'année civile.
- **`depenses-par-poste`** est le jeu « risques professionnels » (AT/MP du régime général), écarté.
  `demographie-effectifs-et-les-densites` est bien au grain départemental, par âge et sexe.
- **APL :** l'onglet « APL 2023 » porte « Millésime : 2024 » et une population 2022, comme l'onglet 2024. C'est une
  anomalie de libellé à la source. Les paliers sont confirmés : 1 / ⅔ / ⅓ sur 10 / 15 / 20 min pour CD, MK et IDE,
  et sur 10 / 20 / 30 min pour les SF. Les poids d'âge DCIR couvrent 19 tranches × 3 millésimes.
- **Open DAMIR :** le filtre `PRS_REM_TYP = 0` est imposé par le descriptif (sinon doublons), et les actes se
  comptent en quantité. Les dentistes sont la nature 19, 53, 54 ou la spécialité 36. `PSE_STJ_SNDS` n'est renseigné
  que pour le régime général et les régimes infogérés.

**Open DAMIR, débit :**
- **1 flux (pilote, mesuré) :** 202501, 0,97 Go compressés, 36,6 M lignes en 213 s, soit 4,6 Mo/s. Sur les
  9 premiers mois (2025-01 à 2025-09), de 3,4 à 4,6 Mo/s, médiane 3,8 Mo/s, soit 214 à 274 s par mois.
- **Goulot :** le filtre Python (~93 % d'un cœur), pas le réseau (curl à ~4 %). Le filtre a été porté de pandas à
  Arrow (multi-cœur). Il est identique sur un test de synthèse de 200 000 lignes (écart max 7·10⁻¹⁵).
- **4 flux (demande de l'utilisateur·rice) :** refusés. Le serveur renvoie une page HTML « Téléchargement refusé :
  limite de téléchargements atteinte ou délai de connexion dépassé » au lieu du fichier. Ensuite, même un seul flux
  a été refusé pendant plus de 6 min (jeton changé entre-temps). On revient à 1 flux, avec une nouvelle tentative
  toutes les 60 s.
- **Blocage :** le refus a duré au moins de 03:53 à 04:06 et touchait toute la machine : curl avec une session
  neuve, le navigateur intégré, et même Open Medic sur le même serveur. Il n'y a pas de cookie, et le jeton est
  commun à tous : la limite est très probablement liée à l'adresse IP (déduit, non documenté).

**Open DAMIR, fenêtre arrêtée à 9 mois (décision de l'utilisateur·rice, 2026-11-15, faute de temps) :**
- **Lu :** 2025-01 à 2025-09, soit 8,2 Go et ~310 M lignes. Les 3 mois de 2025 restants, les 12 mois de 2024 et
  les 25 mois de campagne 2015-16 à 2019-20 ne sont **pas lus**.
- **Ce qui suffit :**
  - **M1** : l'indice est rapporté à 2026, donc le niveau absolu s'annule. La forme par âge vient des poids APL
    pour SF, CD, MK et IDE, et de DAMIR pour les PH (tranches de 10 ans).
  - **M3** : le prix moyen par acte (ratio montant / quantité) se calcule sur 9 mois.
- **Ce qui manque :**
  - octobre–décembre 2025 : biais saisonnier possible sur les profils, surtout la vaccination ;
  - le contrôle de stabilité 2024 ;
  - **s(t) régional pour P-B6** (actes VGP 3360 par région, 2015–2020).
- **Repli pour P-B6 :**
  - **m** (expansion du total des vaccinations) se mesure sur Open Medic : boîtes J07BB par région de résidence et
    par an, 2014–2025, contrôles 24 / 24. C'est une différence de différences annuelle, moins fine que par mois de
    soins.
  - **s(t)** prend la part nationale publiée par la Cour des comptes, sans détail régional.
  - Ce changement de protocole revient à l'axe 3, avant le gel.
- **Reprendre plus tard :** `uv run python v2/besoin/donnees/damir.py --fenetre` saute les mois déjà lus. Compter
  ~40 × 220 s ≈ 2 h 30 de machine sur une connexion non bloquée, à 1 flux seulement.

## How
- **Données :** sources et millésimes dans le tableau et le manifeste. Brut sous `v2/data/raw/besoin/`, ignoré par
  git.
- **Méthode :** un module par source dans `v2/besoin/donnees/`. `_commun.ecrire` écrit chaque table dans le dossier
  de sa licence, avec une fiche `.meta.json` (source, millésime, licence, DOM, contrôles). `manifest.py` les
  rassemble.
- **DAMIR :** `curl | gunzip | pyarrow`, aucun CSV écrit ; un agrégat par mois de flux.

## ⚑ What could make it wrong
- **DAMIR n'est contrôlé contre aucun total externe.** La Statistique mensuelle est en régime général + SLM (PDF de
  champ lu), et DAMIR n'a pas de variable de régime. Une erreur de filtre qui garderait les proportions passerait
  inaperçue.
- **Le département de la patientèle** est déduit, pas lu.
- **Le distancier :** détour 1,3 et 60 km/h sont **supposés**. Le centre geo.api n'est ni la mairie ni le
  barycentre de population. P-B4 comparera M4 à l'APL, qui utilise des temps routiers.
- **IQVIA** est extrapolé d'un panel (60 à 90 % des officines), pas un recensement.
- **Profils DAMIR sur 9 mois seulement** (janvier–septembre 2025) : octobre–décembre manque. **Biais mesuré,
  jugé acceptable :**
  - la distance en variation totale entre les répartitions par âge de la dépense en hiver (mois de flux 1–3) et en
    été (6–8) vaut 0,6 % pour IDE, 0,8 % pour MK, 0,9 % pour CD, 1,1 % pour SF et 1,3 % pour PH, et 3,2 % pour MG
    (source seulement) ;
  - le trimestre manquant est intermédiaire, donc l'erreur du profil sur 9 mois est de quelques dixièmes de point
    (dérivé) ;
  - la vaccination ne pèse que 0,14 % de la dépense PH (mesuré) ;
  - la forme du profil de SF, CD, MK et IDE vient des poids APL, calculés sur l'année entière.
  Une tentative de lecture d'octobre à décembre par partage de connexion mobile (2026-11-15, 04:13) a été
  abandonnée : environ 75 Ko/s, soit ~10 h pour 3 mois.

## → What it changes
- **Axe 2 (M1–M4) :** les entrées sont prêtes. DAMIR couvre 9 mois de 2025 (`damir_profils`, `damir_vaccination`).
  M4 part sur le distancier de repli.
- **Axe 3, P-B6 :** m passe sur Open Medic, s(t) sur la part nationale de la Cour des comptes. Le protocole est à
  réécrire avant le gel.
- **Axe 3 :** la patientèle est une moyenne par professionnel (P-B2, P-B5). DOM et Corse sont fusionnés dans
  DAMIR et Open Medic (P-B6 : pas de DiD par DOM). L'onglet APL 2023 est mal libellé (P-B4).
- **Licence (registre § Open) :** les tables ODbL sont hors dépôt. Si la décision les autorise sous ODbL, il suffit
  de déplacer `v2/data/odbl/besoin/` et de l'ajouter.

## ? Next
| Item | Cost |
|---|---|
| Total inter-régimes publié par profession (comptes de la santé DREES, rapport charges et produits) pour contrôler DAMIR à 0,5 % | ~30 min, peut-être non mesurable |
| Lire les 40 mois DAMIR restants (s(t) régional pour P-B6, profils complets 2024–2025), à 1 flux, sur une connexion non bloquée | ~2 h 30 machine + ~37 Go de transfert ; reporté faute de temps |
| Page « Méthode » de data.ameli.fr : département de la patientèle | ~5 min |
| Caler le détour et la vitesse sur 100 temps routiers (Metric-OSRM) | ~30 min + accès SSPCloud |
| OSRM sur l'extrait OSM France (4,8 Go) : accord de l'utilisateur·rice nécessaire | ~30 min Claude + machine non mesurée |
