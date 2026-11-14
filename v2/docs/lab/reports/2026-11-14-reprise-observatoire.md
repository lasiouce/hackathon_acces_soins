---
type: analysis
date: 2026-11-14
author: Claude
question: Que reprend la v2 de l'observatoire de l'équipe (Pierreafeu181/Hackathon-Evolution-soin), où et à quel coût ?
headline: "31 éléments passés en revue : 19 repris ou adaptés, 2 à vérifier, 7 non repris, 3 réservés à la couche personas. Les 3 plus utiles : la validation par mondes simulés, le levier retraite corrigé (+n ans exactement en 65+) et deux sources de données (zonage data.gouv 2026-10-30, projections DREES des infirmières à 2050)"
status: done
professions: [all]
hypothesis: axes 0, 2, 3, 4, 5
sources: [github.com/Pierreafeu181/Hackathon-Evolution-soin, dépôt privé de l'équipe, commit du 2026-11-14 01:04 — README.md, docs/AUDIT_PROJECTIONS.md, pipeline/*.py, pipeline/tests, web/lib/projection.test.ts, pipeline/assumptions.json]
tags: [reprise, équipe, validation, levier, données]
---

# Ce que la v2 reprend de l'observatoire de l'équipe

> **Headline :** sur 31 éléments passés en revue, 19 sont repris ou
> adaptés, 2 sont à vérifier (B4, C7), 7 ne sont pas repris (E1–E6, C8) et
> 3 attendent la couche personas (D1–D3).
> **[`v2/ROADMAP.md`](../../ROADMAP.md) prime** (décision du
> 2026-11-14) : on reprend ce qui sert nos axes, on n'adopte ni sa
> définition de « libéral », ni son grain, ni son horizon.

**Provenance.**
- *Cité* : lu dans son dépôt, README, audit ou code.
- *Mesuré* : chiffré par nous.
- *Non vérifié* : ni l'un ni l'autre.

Son code tourne en local (site sur `localhost:3000`, copie dans le
scratchpad de cette session). Il n'est pas copié dans notre dépôt.

**Confidentialité.**
- Son dépôt est privé et versionne `web/public/data/students.json`, dérivé
  de fichiers d'organisateurs sous accord de confidentialité.
- Nous reprenons des **méthodes, des formules et des URL de sources
  ouvertes**, pas ses fichiers.

## Ce qu'est son outil, en une ligne
Un observatoire Next.js statique (carte, fiche territoire, vivier étudiant,
leviers en direct). Le modèle par cohortes est de **la même famille que notre
v1** :
- tranches de 5 ans, 1/5 qui vieillit par an ;
- taux de maintien par département × âge, avec shrinkage ;
- entrées égales aux résidus moyens des 5 dernières années ;
- libéral + mixte, par département, jusqu'en 2040.

Le moteur existe en Python et en TypeScript, avec un test qui vérifie
qu'ils donnent les mêmes chiffres.

## A. Validation (→ axe 3)

| # | Élément | Chez lui | Décision | Où chez nous | Coût |
|---|---|---|---|---|---|
| A1 | **Mondes simulés, vérité connue.** 30 départements de 30 à 4 000 professionnels simulés âge par âge, agrégés comme le RPPS, estimés sur 12 ans, projetés à 15 ans. 7 mondes : équilibre ; pyramide non stationnaire ; bruit ; cohorte nombreuse de 55-60 ans ; entrées +3 %/an ; saut des entrées de +40 % ; report de l'âge de départ pendant l'historique | `docs/AUDIT_PROJECTIONS.md` § 2.2 (scripts hors dépôt) | **repris** : nouveau niveau du protocole, appliqué à chaque estimateur du jumeau | axe 3 (`v2/validation/`) | ~1 h |
| A2 | **Ses résultats sur ces mondes** (cités) : +8 à +19 % de seniors (âges supposés uniformes dans la tranche) ; −12,4 % en 15 ans si les entrées croissent de 3 %/an ; 20–25 % d'erreur sous 100 professionnels par département, même sans bruit | idem | **repris comme prédiction à tester** sur notre stock-flux, qui a les mêmes hypothèses. Non vérifié chez nous | axe 3, puis axe 2 | inclus dans A1 |
| A3 | **Backtest sur toutes les origines × tous les horizons**, erreur ∝ horizon, pente × 1,6 pour viser environ 8 cas sur 10 | `projection.py::uncertainty` | **adapté** : sert de fourchette de référence naïve jusqu'en 2050, explicitement marquée « extrapolée ». Notre protocole N1 pré-enregistré reste l'étalon | axe 3, niveaux 1–2 | ~30 min |
| A4 | **Robustesse du classement** : le top 10 des départements les plus fragiles en 2040 garde 6 à 9 départements communs quand la fenêtre d'entrées varie | audit § 1 | **repris** comme métrique : le classement est plus robuste que les niveaux | axe 3, niveau 4 | ~20 min |
| A5 | **Sensibilité aux choix d'estimation** (fenêtre d'entrées de 2, 3, 5 ou 8 ans) : 13 % d'écart en 2040 pour les dentistes (cité) | audit § 2.3 | **repris** : les choix d'estimation entrent comme facteurs de l'analyse de sensibilité, à côté des hyperparamètres | axe 5 | ~15 min |
| A6 | **Tests de propriétés du modèle** : leviers neutres = observé ; plus de formation ne diminue jamais l'effectif ; la redistribution ne crée personne ; report retraite = +n ans exactement en 65+ ; les tranches à solde positif ne sont pas touchées ; aucun levier n'agit avant l'année de décision ; paramètres bornés ; fourchettes croissantes avec l'horizon | `pipeline/tests/test_projection.py`, `web/lib/projection.test.ts` | **repris** : à ajouter aux critères de `v2/jumeau/check.py` | axe 0 | ~45 min |
| A7 | **Calibrage DREES pour les infirmières libérales** : API `drees_projections_infirmieres_2024`, scénario tendanciel, ligne « Libéral », jusqu'en 2050 (DREES *Études et Résultats* n°1319, déc. 2024). URL d'export CSV dans `pipeline/download.py` | `calibrate.py` | **repris** : 2ᵉ point de comparaison à 2050, après le Dossier DREES n°76 | axe 3, niveau 2 | ~20 min |
| A8 | **Tableau croissance observée sur 5 ans / modèle / DREES**, avec une explication par profession | `calibrate.py`, `assumptions.json` | **repris** comme format de restitution du niveau 2 | axe 3 | inclus dans A7 |

## B. Mécanismes du modèle (→ axes 0 et 2)

| # | Élément | Chez lui | Décision | Où chez nous | Coût |
|---|---|---|---|---|---|
| B1 | **Levier retraite corrigé.** Sur la tranche ouverte 65+, la durée moyenne de séjour 1/e devient 1/e + n (au moins 1 an). Sur 55-59 et 60-64, les sorties baissent de 20 % par an de report (demi-effet sur 55-59). Les tranches à solde net positif ne sont pas touchées. Montée en charge de 3 mois par an | `projection.py::retirement_rates`, `RETRAITE_PAS` | **repris** : notre `sorties.py` applique `× (1 − Δ/5)` en permanence à 60-64 **et 65+**, ce qui reproduit le bug de son audit (« +3 ans » ajoute 4 à 7 ans) | axe 0 (`modules/sorties.py`) | ~30 min |
| B2 | **Année de décision.** Aucun levier n'agit avant l'année en cours (pas l'année des données). Les entrées en formation montent sur 3 promotions après le délai d'études | `project()` : `decision`, `ramp` | **repris**. On fixe **une seule convention de date** pour tous les leviers à délai : la revue a trouvé un décalage d'un an sur les quotas entre le jumeau et la v1 | axe 0 (`scenario.py`, `entrees.py`) | ~20 min |
| B3 | **Shrinkage hiérarchique** département → région → national, poids 200 (le nôtre : département → national, même poids) | `estimate()` | **adapté** : variante à mettre sur le banc, prolongée commune → département → région → national | axe 2 | ~30 min |
| B4 | **Taux de maintien bornés à [0,5 ; 1,2]**, r = 1 dans les tranches d'entrée, entrées = résidus moyens | `estimate()` | **à vérifier, pas repris tel quel**. Notre K1 a montré qu'une rétention > 1 fait croître les entrées avec le stock, ce qui les fait s'emballer. Sa borne 1,2 sur les 55+ peut reproduire ce piège. À tester sur un monde simulé (A1) | axe 2 | ~20 min |
| B5 | **Levier « attractivité »** : une part des entrants des départements à forte part de zones dotées est redirigée vers ceux à forte population en zone sous-dotée, à total constant (testé) | `project()` | **adapté** comme variante *incitative*, distincte de notre régulation par géocodes. L'ampleur de l'effet doit venir d'une source : la Cour des comptes 2024 juge les aides à l'installation « décevantes » (cité par le mémoire EHESP) | axe 1 (fiche), puis axe 0 (module) | ~45 min |
| B6 | **Pièges qu'il a relevés lui-même** : le levier formation multiplie aussi la part « diplômés à l'étranger » des entrées (double compte) ; un multiplicateur national rend plus négatives des entrées nettes déjà négatives | audit § 3.7 | **repris comme tests** : le module `entrees` sépare le flux national et le flux étranger, et une entrée nette négative n'est jamais multipliée | axe 0 | ~20 min |

## C. Données (→ axe 4)

| # | Élément | Chez lui | Décision | Où chez nous | Coût |
|---|---|---|---|---|---|
| C1 | **Zonages ARS par commune, data.gouv** (`zonages-des-professionnels-de-sante-liberaux`, `t-zonages-com.csv`, ressource du 2026-10-30). Niveaux 1–5 par profession (`zide`, `zmk`, `zsf`, `zdent`), arrondissements PLM | `download.py`, `parse_zonage.py` | **repris comme contrôle croisé** de notre table `zonage_commune.parquet` (CartoSanté arm2026) | axe 4 | ~15 min |
| C2 | **Estimations de population Insee** par dép × sexe × âge quinquennal, 1975–2026 (`estim-pop-dep-sexe-aq-1975-2026.xlsx`) ; Omphale recalé sur ces estimations | `download.py`, `parse_population.py` | **repris**. Il remplace « Omphale 2018 tenu constant avant 2018 » (hypothèse v1) pour les densités passées | axe 4 | ~20 min |
| C3 | **Scénario Omphale « Population âgée »** (en plus de Central et Pop basse) | `download.py` | **repris** : à ajouter à nos 3 scénarios (Central, Pop basse, Pop haute) | axe 4 | ~5 min |
| C4 | **Fiabilité des fichiers étudiants** : seules les feuilles annuelles DREES (`990_drees_mmop2_*`) sont sources ; les autres fichiers organisateurs en sont des copies manuelles avec erreurs (ARS inversées, coordonnées décalées) | `parse_students.py` | **repris comme règle**, cohérente avec notre usage. Notre axe 4 a trouvé en plus un artefact en 2025 (odontologie Paris Cité 683 au lieu de ~190, mesuré) : à lui signaler | axe 4 | — |
| C5 | **Correspondance université → ARS**, dont les codes nouveaux en 2025 (`UNIV_OVERRIDES`) | `parse_students.py` | **repris** pour répartir les entrées par région de formation (ledger v1 « Regional pipeline », ~2 h) | axe 2 | inclus |
| C6 | **Secret statistique** : les cellules < 5 sont masquées par la DREES ; il compte les cellules masquées au lieu de les ignorer | README | **repris** : nos chargeurs doivent compter et afficher les cellules masquées. Non vérifié chez nous | axe 4 | ~15 min |
| C7 | **Délais de formation** : pharmacie 6, odontologie 6, SF 5, kinés 4, IDE 3 ans | `assumptions.json` | **à croiser** avec les fiches de l'axe 1 et le registre d'événements de l'axe 4 (allongement de la maïeutique ; entrée en kiné après une 1re année de licence) | axe 1 | ~10 min |
| C8 | **Diplômés à l'étranger par an** : dentistes 665, pharmaciens 160, SF 70, IDE 400, kinés 0 | `assumptions.json` | **pas repris sans source primaire**. Les valeurs ne citent pas de tableau précis ; kinés = 0 est reconnu faux par son propre audit | axe 1 | ~1 h (déjà au ledger) |

## D. Produit (→ couche personas, plus tard, selon la ROADMAP)

| # | Élément | Décision |
|---|---|---|
| D1 | Site statique Next.js + MapLibre + ECharts, scénario encodé dans l'URL, vues nationale et ARS, fiche territoire | **réservé à la couche personas.** Quand elle viendra, le jumeau exportera des scénarios dans un format que son site lit. Un portage TypeScript du jumeau n'est pas réaliste à la commune : on prévoit une grille de scénarios précalculée |
| D2 | Badge de fiabilité par profession, effectifs arrondis à 3 chiffres (« ≈ 51 500 »), fourchette ombrée | **réservé**, bonne pratique |
| D3 | Densité ajustée aux besoins (poids d'âge Open DAMIR, un mois) | **réservé comme contexte.** Nos sorties sont des effectifs. Ses propres limites : un seul mois, des actes hétérogènes, une consommation freinée là où l'offre manque |

## E. Écarté

| # | Élément | Pourquoi |
|---|---|---|
| E1 | « Libéral » = libéral + mixte | Notre définition (secteur privé, tout employeur public exclu) prime. Pour les pharmaciens, 27 294 contre 60 005–67 219 en 2026 (mesuré, axe 4) |
| E2 | Grain département seulement, horizon 2040 | La ROADMAP impose la commune et 2050 |
| E3 | Un seul modèle, leviers nationaux seulement | La ROADMAP impose plusieurs estimateurs comparés et des leviers par territoire |
| E4 | Vieillissement uniforme 1/5 par an | C'est son propre biais mesuré (A2). Piste axe 2 : âges en années simples ou vieillissement non uniforme |
| E5 | Seuil d'alerte relatif (< 80 % de la moyenne nationale) | Il le critique lui-même : un seuil relatif ne se déclenche jamais si tout le pays se dégrade. Ses libellés (« alerte », « défavorable ») sont à revoir selon notre lexique neutre |
| E6 | Moteur dupliqué Python + TypeScript | Coût de maintenance ; un seul moteur chez nous (le jumeau) |

## F. Ce que nous pouvons lui apporter
- **Entrées tirées des étudiants en formation** (rapport v1
  `docs/lab/reports/2026-11-13-pipeline-entries.md`). Son audit le note
  comme à faire (§ 3.3). Mesuré : l'écart national passe de −6,5 à −4,1 %
  pour les spécialistes, et de −4,2 à −3,3 % pour les pharmaciens.
- **Le piège du double comptage des entrées** (correction K1) : il touche
  sa borne r ≤ 1,2.
- **Séparation public / privé** (axe 4) et **zonage par commune en
  géocodes**.
- **Registre de 30 événements datés**, dont l'année blanche MK 2018 et
  l'artefact du fichier d'inscrits 2025.
- **La convention de date des leviers à délai** (B2), relevée par notre
  revue.

## ⚑ Ce qui pourrait rendre ce rapport faux
- Lecture d'un seul commit (2026-11-14 01:04). Son dépôt évolue.
- Ses chiffres d'audit (A2, A4, A5) sont cités, pas reproduits : ses
  scripts d'audit sont hors dépôt.
- Les coûts sont estimés (temps Claude), pas mesurés.

## → Ce que ça change
- **Axe 0** : B1, B2, B6 et les tests A6, à transmettre à la session de
  l'axe 0. B1 et B2 recoupent la revue adversariale.
- **Axe 3** : niveau « mondes simulés » (A1) ; ER1319 (A7) ; métrique de
  classement (A4).
- **Axe 4** : contrôle croisé du zonage (C1), estimations de population
  (C2), scénario « Population âgée » (C3), cellules masquées (C6).
- **Axe 2** (quand il démarrera) : B3, B4, C5, E4.
- **Axe 5** : choix d'estimation comme facteurs (A5).

## ? Pour la suite
| Point | Coût |
|---|---|
| Transmettre B1, B2, B6 et A6 à l'axe 0 | 2 min |
| Transmettre A1, A3, A4, A7 à l'axe 3 | 2 min |
| Transmettre C1, C2, C3 et C6 à l'axe 4 | 2 min |
| Partager la section F avec lui (sans données sous accord de confidentialité) | 10 min, temps humain |
