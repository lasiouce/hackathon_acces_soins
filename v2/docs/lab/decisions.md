---
type: decisions
aliases: [Décisions v2]
---

# Décisions — v2 (jumeau numérique de l'offre de soins)

Chaque choix fait, inversé ou rejeté, avec son *pourquoi*. Format :
**Décision** / **Pourquoi** / **Ce qui le renverserait**. On remplace,
on n'efface jamais.

- Les entrées du 2026-11-14 ci-dessous sont copiées de la v1
  (`../../../docs/lab/decisions.md`), où elles restent aussi.
- Les décisions v1 antérieures restent valables tant qu'une entrée ici ne
  les remplace pas.

## 2026-11-14 — Recadrage en recherche : jumeau numérique des professions « libérales »

**Décision.**
- **Objectif.** Simuler des politiques publiques nationales, chacune
  exprimée comme un réglage d'hyperparamètres sourcés, et mesurer leur effet
  sur l'effectif « libéral » à une date future t.
  - Les hyperparamètres viennent d'Omphale, d'Hippocrate et du Dossier DREES
    n°76, plus des spécificités par profession : régulation de
    l'installation, filières en pharmacie, spécialisation en odontologie,
    abandon en études infirmières.
  - Les effectifs couvrent les sages-femmes, les chirurgiens-dentistes, les
    pharmaciens, les masseurs-kinésithérapeutes et les infirmiers.
- **Phase 2** : cardiologie, dermatologie, ophtalmologie (appui : rapport
  HCAAM sur les dépassements d'honoraires).
- **Démarche.** Mode de recherche quantitative : reproductible,
  falsifiable, interprétable, sans boîte noire. Code en briques (plug-ins
  par flux).
- **Feuille de route et axes de recherche** : [ROADMAP.md](../../ROADMAP.md).

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Ce qui le renverserait.** Un nouveau cadrage du jury ou de l'équipe.

## 2026-11-14 — « Libéral » = secteur privé, lucratif ou non (tout employeur public exclu)

**Décision.**
- Une personne compte comme « libérale » si elle n'exerce pas chez un
  employeur public.
  - **Inclus :** libéraux et mixtes, pharmaciens adjoints salariés
    d'officine, salariés de cliniques privées et d'établissements privés
    non lucratifs, industrie, laboratoires privés.
  - **Exclus :** hôpital public, PMI, Éducation nationale, EHPAD publics,
    centres de santé municipaux, et tout autre employeur public.
- Dans le code, le nom est explicite (`prive`, hors public). Dans les
  textes, on rappelle la définition, car les sources (RPPS, ameli)
  emploient « libéral » au sens d'exercice indépendant.

**Pourquoi.** L'utilisateur·rice, 2026-11-14. Le second point (autres
employeurs publics exclus, industrie incluse) a été choisi parmi des options
proposées.

**Conséquence mesurée.** Effectifs de la dernière année, ancienne
définition (libéral + mixte) → nouvelle. Le minimum compte zéro salarié
hospitalier privé ; le maximum les compte tous :
| Profession | Ancienne | Minimum | Maximum |
|---|---|---|---|
| Pharmaciens 2026 | 27 294 | 65 344 | 75 335 |
| Sages-femmes 2026 | 9 615 | 12 475 | 26 428 |
| Kinés 2026 | 92 836 | 98 348 | 111 237 |
| Dentistes 2026 | 40 083 | 48 143 | 48 690 |
- Le RPPS de la DREES ne sépare pas le public du privé dans « salarié
  hospitalier ».
- « Autre salarié » mélange aussi des employeurs publics (PMI…) et
  privés.

Il manque donc une donnée (voir le ledger). Les résultats K1 et
« entrées par la filière » sont **mesurés sur l'ancien périmètre**.

**Ce qui le renverserait.** Aucune source ouverte ne permettant de séparer
public et privé. Dans ce cas, la sortie serait donnée sous forme de
fourchette, ou la définition révisée.

## 2026-11-14 — Les modèles tournent à toutes les granularités, jusqu'à la commune ; horizon de référence 2050

**Décision.**
- **Granularité.** Les modèles s'appliquent à chaque niveau : commune,
  groupes de communes, département, région, national.
  - La régulation de l'installation est une **liste de géocodes** par
    profession : zones où l'installation est limitée au remplacement d'un
    départ, et zones où l'exercice est obligatoire.
  - Une même profession peut relever des deux statuts selon la zone
    (kinés).
  - Le DG de l'ARS doit avoir la visibilité maximale.
- **Horizon de référence : 2050.**

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Conséquences.**
- 2050 = 24 ans après 2026. Avec des données de 2012 à 2026, un backtest
  ne couvre qu'environ 10 ans, donc **aucune précision ne peut être annoncée
  à 2050**. On peut seulement reproduire le tendanciel de la DREES à 2050
  (Dossier n°76) et vérifier les cas limites.
- À 24 ans, l'horizon dépasse toutes les durées de formation : les quotas
  deviennent des leviers de premier ordre.
- À l'échelle de la commune, le bruit sur les petits effectifs (environ
  ±45 % pour N = 5, dérivé) se cumule sur l'horizon.

**Ferme** deux points de « En attente » : « Demo horizon » et « Projection
grain ».

## 2026-11-14 — Les nouveaux modèles ne sont pas tenus d'être des stock-flux

**Décision.**
- Le stock-flux (H1) est le **modèle de départ à battre**, pas la méthode
  imposée.
- Toute méthode peut entrer sur le banc si elle remplit trois conditions :
  - elle est interprétable, sans boîte noire ;
  - chaque levier y modifie un paramètre nommé et sourcé ;
  - elle respecte le contrat des modules.

  Par exemple : microsimulation, modèles bayésiens hiérarchiques ou
  espace-état, choix discret de l'installation, dynamique des systèmes,
  GAM, modèles spatiaux.
- C'est l'axe 2 de [ROADMAP.md](../../ROADMAP.md).

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Ce qui le renverserait.** Aucun.

## 2026-11-14 — L'axe 0 est le jumeau numérique de l'offre de soins en France

**Décision.**
- Le socle commun qui relie les axes de recherche est un **jumeau numérique
  de l'offre de soins**. Il comprend trois composants :
  1. un **état unique** : N[profession, secteur, âge, sexe, commune, t],
     plus le vivier en formation ;
  2. des **modules de flux** en plug-ins, chacun avec ses paramètres
     sourcés ;
  3. des **scénarios** : jeux d'hyperparamètres et d'événements datés. Une
     politique publique est un scénario.
- Les axes 1 à 5 s'y branchent.
- L'état comprend le **secteur public**. C'est dérivé : un entrant bloqué
  par la régulation, ou une transition privé ↔ public, doit avoir où aller
  pour que les effectifs se conservent. La sortie étudiée reste le
  « libéral » (privé).

**Pourquoi.** L'utilisateur·rice, 2026-11-14 : « le liant de l'axe 0 c'est
un jumeau numérique de l'offre de soins en France ».
**Ce qui le renverserait.** Le secteur public ne pouvant pas être estimé à
la commune. Dans ce cas, il serait tenu à une échelle plus grossière et
ventilé.

## 2026-11-14 — Axe 5 adopté ; ordre de travail et format des fiches

**Décision.**
- **L'axe 5 est adopté** : analyse de sensibilité (Morris, puis Sobol) et
  incertitude à 2050.
- **Ordre de travail.**
  - Les axes 0, 1, 3 et 4 démarrent tout de suite, en parallèle :
    - axe 0 : le jumeau, en code ;
    - axe 1 : fiches de paramètres ;
    - axe 3 : protocoles de validation ;
    - axe 4 : données, avec en tête la séparation public / privé.
  - Les axes 2 et 5 démarrent quand le contrat du jumeau (axe 0) tourne.
    Ils ont besoin de son interface.
- **Format commun des fiches** (axes 1 et 4) : `docs/lab/fiches/<id>.md`,
  avec un frontmatter qui contient :
  - `parametre`, `profession`, `module` (le flux du jumeau visé) ;
  - `valeur`, `unite`, `incertitude` ;
  - `source`, `millesime` ;
  - `statut` : mesuré / sourcé / supposé / non mesurable.
- **Règle de partage du dépôt.** Le dépôt n'a encore aucun commit, donc les
  sessions travaillent dans le même dossier. Chacune ne touche que ses
  fichiers et ne commite rien. Seule l'axe 0 modifie `sante/`. *(Remplacé le 2026-11-14 : voir « Dossier v2 » plus bas.)*

**Pourquoi.** L'utilisateur·rice valide l'axe 5 et l'ordre, 2026-11-14.
L'ordre « axe 0 d'abord, puis le reste » est affiné : les axes 1, 3 et 4
produisent des documents et des données, pas du code qui dépend du contrat.
Les attendre ferait perdre du temps de hackathon.
**Ce qui le renverserait.** Le contrat de l'axe 0 exigeant un format de
fiche différent. Dans ce cas, on convertit les fiches, qui sont du texte.

## 2026-11-14 — Dossier v2 : code et docs séparés, v1 figée

**Décision.**
- Tout le nouveau travail va dans `v2/` :
  - le code du jumeau, dans un paquet sous `v2/` ;
  - `v2/ROADMAP.md` ;
  - `v2/docs/lab/` : `decisions.md`, `open.md`, `reports/`, `fiches/`,
    `figures/`.
- La v1 est **figée** et sert de référence en lecture seule : `sante/`,
  `app/`, `docs/lab/` à la racine.
  - On peut importer `sante` et lire `data/processed/`.
  - Les données brutes et traitées restent dans `data/`, partagées.
- Ceci remplace « seule l'axe 0 modifie `sante/` » (entrée « Axe 5 adopté »
  plus haut).

**Pourquoi.** L'utilisateur·rice, 2026-11-14 : « crée même un dossier v2 ».
Choix « code + docs séparés » parmi les options proposées.
**Ce qui le renverserait.** Un besoin de corriger un bug de la v1 dont la
v2 dépend. On le corrigerait alors en v1 avec une entrée datée.

## 2026-11-14 — Contrat du jumeau (axe 0) : état à cellules, modules à flux typés, scénario à événements

*Complété le 2026-11-14 par « Corrections du contrat du jumeau après la revue adversariale », plus bas. Les critères « module factice », « levier » et « agrégation » mesurés ci-dessous étaient en partie vrais par construction : remplacés par les critères C1–C10.*

**Décision.** Le jumeau est le paquet `v2/jumeau/`.
- **État** (`state.py`) : N[cellule, âge], avec cellule = (profession,
  secteur, territoire, sexe), plus un vivier national (profession × année
  d'étude).
  - Le secteur est un axe de l'état, pas un filtre. `ensure_sector` crée
    une destination vide (ex. `public`).
  - `level` dit ce qu'est le territoire. `Geography` agrège commune →
    département → région → national, uniquement vers le haut.
- **Modules** (`module.py`) : `name`, `order`, des `params` (des `Param`
  avec valeur, unité, source, millésime et statut, dans le format des
  fiches), `fit(hist)` et `step(state, ctx)` → une liste de flux typés :
  Shift, Rate, Add, Move, Pool.
  - Le moteur applique les flux module par module (séparation
    d'opérateurs), puis un plancher à 0. Chaque flux est inscrit au
    registre, par cellule.
  - Un module s'enregistre par `@register`, dans `jumeau/modules/` ou dans
    un dossier passé à `discover()`.
  - Une méthode qui n'est pas un stock-flux est un module qui rend ses
    résultats sous forme de flux. Elle peut aussi remplacer la composition
    entière derrière `Estimator`.
- **Scénario** (`scenario.py`) : des surcharges « module.param » et des
  `Event(param, start, value, op, end, selector)`. C'est la forme retenue
  de `Perturbation(slot, selector, profile)` (v1, § Open) : le slot est le
  paramètre, le profil est start, end et op (set, mul, add), le sélecteur
  porte sur les axes de l'état. La composition (`modules`) fait partie du
  scénario.
- **Modules livrés :** `vieillissement`, `sorties` (rétention, plus les
  leviers retraite et cumul), `entrees` (flux, filière, multiplicateur de
  quotas), `regulation` (géocodes : remplacement seul, excédent déplacé
  vers `destination`), `formation` (vivier, abandon, capacité ; les
  diplômés ne sont pas encore injectés dans N).

**Challenge de l'incumbent (challenge-design).** Contraintes, en unités :
- écart à `predict` : 0 personne ;
- coût d'un nouveau mécanisme : 1 fichier, 0 édition ;
- recalcul : < 2 s (supposé) ;
- agrégation : 0 personne d'écart.

Verdict :
- `sante.estimators.Estimator` (`fit` / `predict` / `assumptions`)
  **survit** comme couche du banc. Le jumeau s'y branche par
  `jumeau.estimators.twin_of`.
- `sante.model.project` et la perturbation de `app/levers.py` sont
  **remplacés** pour le travail par scénario. Les mécanismes y étaient
  fusionnés et les leviers patchaient le tuple `rates` de l'extérieur :
  ajouter un mécanisme demandait d'éditer deux fichiers.
- L'ajustement `fit_rates` est **réutilisé tel quel** (`history.py`). La
  v1 reste l'oracle.

**Mesuré** (`PYTHONPATH=v2 uv run python -m jumeau.check`,
[rapport](reports/2026-11-14-jumeau-axe0.md)) :
- **Reproduction.** Écart 0,0 sur 140 comparaisons `predict` (5 variantes
  stock-flux × banc K1 + origine récente jusqu'en 2050). Écart 0,0 aussi
  par cellule × âge × année jusqu'en 2050, pour 7 professions.
- **Levier.** Retraite + 1 an : écart 0,0 avec la v1 en 2050.
- **Module factice.** Ajouté depuis un dossier temporaire ; empreinte de
  `v2/jumeau/` et de `sante/` inchangée.
- **Agrégation.** 13 147 communes → national : écart 0 à chaque niveau.
- **Temps.** 18 ms par scénario pour 7 professions au département
  jusqu'en 2050. 0,29 s pour une profession à la taille commune
  (35 047 territoires).

**Rejeté :**
- des modules qui rendent des deltas additifs seulement : le Rate
  multiplicatif est nécessaire pour reproduire `s · base` à l'identique ;
- un plug-in au niveau du modèle entier seulement (statu quo) : les
  leviers ne pourraient pas viser un mécanisme sans éditer le modèle.

**Ce qui le renverserait.**
- Un module de l'axe 2 qui ne s'exprime pas en flux par cellule. Par
  exemple, une microsimulation qui doit garder des individus entre deux
  années : il faudrait un état auxiliaire propre au module.
- Un recalcul à la commune pour 5 professions × 2 secteurs au-delà de
  2 s : ~0,3 s × 10 ≈ 3 s, extrapolé ; à mesurer quand l'état communal
  existera.
- Un ordre des modules qui change les résultats de plus que le bruit.
  L'ordre est fixé par `order` ; sa sensibilité n'est pas mesurée.

## 2026-11-14 — Qui possède quoi dans v2 (sessions en parallèle)

**Décision.** Les sessions de recherche travaillent dans le même dossier,
sans commit. Chacune ne modifie que ce qui lui appartient :

| Axe | Session | Possède |
|---|---|---|
| 0 | jumeau | `v2/jumeau/` |
| 1 | hyperparamètres | `v2/docs/lab/fiches/param-*.md` |
| 3 | validation | `v2/validation/` |
| 4 | données | `v2/data/`, `v2/docs/lab/fiches/data-*.md` |

- Toutes peuvent ajouter leurs rapports dans `v2/docs/lab/reports/`, et
  ajouter des lignes dans `decisions.md` et `open.md` sans réécrire celles
  des autres.
- La v1 se consulte en lecture seule.
- Les axes 2 et 5 démarreront quand le contrat de l'axe 0 tournera.

**Pourquoi.** Le lancement des axes 1, 3 et 4, décidé par
l'utilisateur·rice le 2026-11-14. Sans commit ni worktree, seule la
séparation des fichiers empêche que deux sessions s'écrasent.
**Ce qui le renverserait.** Un premier commit, qui permettrait des
worktrees par axe.

## 2026-11-14 — Axe 3 : protocoles de validation pré-enregistrés et gelés par empreinte

**Décision.**
- Chaque niveau de validation a un protocole écrit **avant** tout calcul :
  [plan](reports/2026-11-14-axe3-plan-validation.md),
  [N1](reports/2026-11-14-axe3-n1-prevision.md),
  [N2](reports/2026-11-14-axe3-n2-long-terme.md),
  [N3](reports/2026-11-14-axe3-n3-leviers-did.md),
  [N4](reports/2026-11-14-axe3-n4-echelle-fine.md).
- Gel à 02:54, copies immuables dans `v2/validation/preregistered/`,
  SHA-256 (12 premiers caractères) : plan `0108455d34aa`, N1 `eb527ecb06a0`,
  N2 `bc5df3083cc5`, N3 `c37e36457f12`, N4 `91f897cc5071`.
- Tout écart ultérieur au protocole est une nouvelle entrée datée, marquée
  « écart au protocole » ; une analyse hors protocole est *exploratoire*.
- Les protocoles s'appliquent à **tout estimateur** exposant `fit` /
  `predict` (et `trajectory` pour N2), pas seulement au jumeau.

**Pourquoi.** K1 v1 a choisi la meilleure de 3 variantes après avoir vu les
résultats (biais de sélection, rapport K1 § correction). La ROADMAP (axe 3)
exige un protocole fixé avant les résultats.
**Ce qui le renverserait.** Rien sur le principe ; un protocole peut être
remplacé avant son premier passage, jamais après.

## 2026-11-14 — Axe 3, N1 : grille, métrique, seuil et variante par défaut du backtest

**Décision.**
- Origines glissantes, fenêtre d'ajustement élargie depuis 2012 (kinés
  2017), ≥ 5 ans ; horizons h ∈ {1, 3, 5, 8, 10}.
- **Métrique principale unique : MAPE par département à h = 5**,
  départements à **N ≥ 30** à l'origine, moyenne à poids égal sur les
  cellules profession × origine. WAPE, biais national signé, h ≠ 5 :
  secondaires.
- **Critère :** borne haute de l'IC 95 % (bootstrap des départements,
  2 000 tirages, graine 20261114) de MAPE(candidat) − MAPE(meilleure
  naïve) < 0.
- **Variante par défaut, seule confirmatoire :** stock-flux à taux locaux
  (poids 200, entrées plates, rétention ≤ 1), sur le jumeau
  `twin_of(StockFlowLocal)`. Toute autre variante s'inscrit, datée, dans
  `v2/validation/registry.py` avant son premier passage.
- **Dépôt de prévisions** origine 2026 → 2027, 2028, 2030, avec empreinte,
  scoré à la publication du RPPS 2027 : seul test non contaminé par K1.

**Pourquoi.** MAPE : chaque département compte pour un DG d'ARS, et c'est
la métrique de K1. h = 5 : seul horizon commun aux 5 professions sur
plusieurs origines. Meilleure naïve après coup : choix défavorable au
candidat.
**Ce qui le renverserait.** Un classement instable entre origines, qui
rendrait la moyenne poolée trompeuse (rapporté, sans changer le critère).

## 2026-11-14 — Axe 3, N2 : validation à 2050 par reproduction DD76 (en ratios) et cas limites

**Décision.**
- Reproduction du tendanciel DREES n°76 (CD, SF, PH), origine 2020, en
  **ratios N(t)/N(2020)**, hypothèses DD76 imposées, sans réglage libre.
  **Tolérance choisie : ±2 % en 2030, ±3 % en 2040 et 2050**, plus la
  forme (creux PH, plateau SF).
- Cas limites : L1 h → 0 exact (1e-9) ; L2 N* = Q·C à 1 % à o + 200 ans,
  indépendant de l'état initial ; L3 aucun effet d'un quota avant t0 + L ;
  L4 conservation (axe 0).
- Un seul échec bloque tout chiffre 2050 pour la profession concernée.

**Pourquoi.** Ratios : notre périmètre 2020 dépasse DD76 de 0,8 à 2,5 %.
3 % : quatre fois moins que l'effet d'un quota ±20 % publié par la DREES
(±12–13 % en 2050), donc le levier reste lisible. C'est un choix, pas une
dérivation.
**Ce qui le renverserait.** L'axe 5 montrant une bande à 2050 bien plus
large que 3 %, qui rendrait la tolérance trop stricte pour être
informative.

## 2026-11-14 — Axe 3, N3 : différence de différences sur le zonage infirmier (expérience naturelle)

**Décision.**
- **Expérience principale E1 (IDE) :** zone `z_infi` = 5 (sur-dotée,
  conventionnement en remplacement seulement) vs 3 (intermédiaire), zonage
  Atlasanté uuid c987d0e2 (génération 2012). Cellule = département × zone,
  ≥ 10 infirmiers en 2008 dans chaque cellule. Avant 2004–2008 (référence
  2008), transition 2009–2011 exclue, après 2012–2019.
- Estimateur : D = log Y₅ − log Y₃ par département, moyenne non pondérée,
  grappes = départements, Student G − 1.
- Tests fixés : T1 tendances parallèles (Hotelling, p ≥ 0,10), T2 placebo
  de date 2006, T3 placebo dentistes, T4 placebo zone 4 vs 3, T5 effet.
- **Validation du module `regulation` de bout en bout :** θ = β_obs / β_mod,
  où β_mod est l'effet d'un plafond parfaitement contraignant. IC de θ
  contient 1 → le module survit ; IC dans ]0, 1[ → remplacé par un plafond
  qui fuit, de paramètre θ.
- **E2 (kinés), secondaire :** marche 2012–2014, arrêt après l'annulation
  par le Conseil d'État (17 mars 2014), jusqu'en 2017.

**Pourquoi.** Seul levier de la liste avec une date d'effet, un zonage
ouvert par commune et une série communale qui couvre l'avant (2004–2008).
L'agrégation département × zone retire le bruit de Poisson communal et suit
l'échelle de décision de l'ARS. 2009–2011 est exclu car régi par un zonage
de 1re génération qu'on n'a pas.
**Ce qui le renverserait.** La preuve que le jeu Atlasanté n'est pas le
zonage de 2012 (une révision construite sur des densités postérieures).

## 2026-11-14 — Axe 3, N4 : taille minimale d'affichage communal sans bande

**Décision.**
- Origines 2014, 2016, 2018, 2020 ; h = 5. Estimateur par défaut :
  projection départementale × part communale tenue (oracle départemental
  tant que N1 n'a pas tourné).
- Classes de taille {1–2, 3–5, 6–10, 11–20, 21–50, 51–100, 101–200, > 200}.
- **N_min** = plus petite classe à partir de laquelle **P80 |erreur| ≤ 25 %**,
  pour IDE, MK et CD, dans ≥ 3 origines sur 4. Sous N_min : bande
  empirique P10–P90 obligatoire, ou agrégation.
- Bande calibrée sur 2014–2018, testée sur 2020 : couverture 75–85 %.

**Pourquoi.** Le bruit de Poisson seul donne P80 ≤ 25 % pour N ≥ 26
(dérivé). 25 % est un choix : l'écart entre deux classes de densité
usuelles.
**Ce qui le renverserait.** Une erreur non monotone en N (la taille ne
serait pas le bon critère).

## 2026-11-14 — Axe 4 : public / privé lu dans le « secteur d'activité » des fichiers DREES, ambiguïtés réparties par FINESS

**Décision.**
- **Source principale : les fichiers DREES déjà sur disque** (`data/raw/drees/*_rpps_2012_2026.xlsx`,
  ADELI kinés 2012–2016). Ils croisent dép × **secteur d'activité** (9 à 12 modalités) × mode × âge × sexe ;
  le loader v1 gardait le secteur à « Ensemble ». Aucune extraction RPPS supplémentaire.
- **Infirmiers : BTS DREES/Insee** (secteur déjà public / privé, 6 modalités) + SNDS libéraux (tous privés).
- **Règle de classement** (`v2/data/build_secteur.py`, table `SECTEUR`) :
  - libéral et mixte → privé, quel que soit le secteur (cohérent avec la décision « libéral = privé ») ;
  - salarié : hôpital public → public ; ESPIC, privé lucratif, officine, laboratoire, médicament,
    cabinets → privé ;
  - salarié des secteurs mixtes (centres de santé, prévention, médico-social, « autre ») → **ambigu**,
    bornes 0 et 1, part privée centrale prise dans **FINESS** (statut juridique des établissements de la
    catégorie, extraction au 2026-05-04) ; « autre secteur » et, pour les pharmaciens, « prévention et
    établissement de santé » → 0,5 **supposé** (pas de source ouverte).
  - Statuts juridiques FINESS 40–46 (organismes de sécurité sociale, ex. centres de santé CPAM) comptés
    **publics** (administrations de sécurité sociale).
- La sortie « libéral » se donne en **trois valeurs** : minimum (ambigus publics), centrale, maximum.

**Pourquoi.** Mesuré : Σ des cellules détaillées = total France du fichier à 0 % près (SF, CD, PH, ADELI),
0,22 % pour les kinés RPPS (incohérence interne du fichier source en 2017–2018). La SAE et les rapports de
l'Ordre ne donnent pas dép × âge × sexe ; ce fichier si.

**Conséquence mesurée (2026, nouvelle fourchette « libéral » = privé) :**
| Profession | Ancienne fourchette | Min | Centrale | Max |
|---|---|---|---|---|
| Sages-femmes | 12 475 – 26 428 | 12 059 | 12 912 | 14 660 |
| Pharmaciens | 65 344 – 75 335 | 60 005 | 63 612 | 67 219 |
| Dentistes | 48 143 – 48 690 | 40 784 | 47 349 | 47 894 |
| Kinés | 98 348 – 111 237 | 98 828 | 101 951 | 103 986 |
| Infirmiers (2023) | — | 277 788 | 277 788 | 277 788 |
- Les anciennes bornes basses n'étaient pas des minima : elles comptaient tout « autre salarié » comme
  privé (PMI, centres de santé municipaux inclus).

**Rejeté :** extraction de l'annuaire santé (RPPS individuel) — inutile tant que le fichier DREES croise
déjà le secteur ; SAE — pas de libéraux, pas de dép × âge × sexe pour ces professions.

**Ce qui le renverserait.** Une source qui ventile « autre secteur » des pharmaciens (5 805 salariés en
2026, 7,7 % de l'effectif) ; un écart > 5 % entre la part FINESS (établissements) et une part en effectifs
salariés (SAE / DADS) pour les centres de santé ou le médico-social.

## 2026-11-14 — Axe 4 : zonage par commune = CartoSanté `zonage_conv` (actuel) + Atlasanté c987d0e2 (génération 2012)

**Décision.**
- **Millésime actuel :** service TJS CartoSanté `zonage_conv`, référentiel COG 2026, attributs `z_sf`,
  `z_dent`, `z_kine`, `z_infi` (sources CNAMTS – ARS). 34 877 communes par profession. La date des arrêtés
  n'est pas servie : millésime = date d'extraction (2026-11-14).
- **Historique :** jeu Atlasanté uuid c987d0e2 (`z_infi`, `z_kine`, `z_dent`, pas de SF), 36 700 communes,
  codes région d'avant 2016 → génération 2012, comme l'a lu l'axe 3 (entrée N3 ci-dessus). Pas d'autre
  millésime ouvert trouvé.
- **Statut lu par le modèle** (`v2/data/build_zonage.py`) :
  - `remplacement_seul` = « sur-dotée » (ancien zonage) ou « non prioritaire » (nouveau zonage kinés,
    dentistes) ;
  - `incitation` = très sous-dotée ou sous-dotée ;
  - `autre` = intermédiaire, très dotée, non renseigné.
  - Les deux régimes coexistent chez les kinés (2 800 communes « non prioritaires », 10 « sur-dotées »).
- **« Obligation d'exercice » n'est pas une classe de zonage** dans ces fichiers : elle n'est pas codée
  par commune (voir open.md).
- Paris, Lyon et Marseille sont zonés par arrondissement ; le référentiel `com2026` ne les porte pas
  (« non renseigné », 2,5 à 6,5 % de la population selon la profession).
  - **Remplacé le 2026-11-14 (même session) :** on lit le référentiel `arm2026` du même service, qui
    remplace les trois communes par leurs 45 arrondissements, zonés. Table : 34 919 géocodes par
    profession (colonne `niveau` = com / arm). Restent « non renseignés » : 2 à 26 communes des DROM
    selon la profession.

**Pourquoi.** Seules sources ouvertes par commune ; CartoSanté couvre aussi les DROM et les SF.
**Ce qui le renverserait.** Les arrêtés ARS datés (par région) montrant que le service CartoSanté mélange
des générations ; un référentiel arrondissement pour PLM.

## 2026-11-14 — Les axes 2 et 5 attendent la correction des défauts bloquants du jumeau

**Décision.**
- Les axes 2 et 5 ne démarrent pas avant que les 4 défauts bloquants de la
  [revue adversariale](reports/2026-11-14-revue-adversariale-axe0.md)
  soient corrigés :
  - modules du scénario ignorés par `twin_of` ;
  - secteur public sans sorties ;
  - dépendances entre modules non déclarées ;
  - scénario non validé et non sérialisable.
- Les critères d'acceptation de l'axe 0 sont réécrits pour pouvoir échouer.
- Les défauts sont transmis à la session de l'axe 0, qui possède
  `v2/jumeau/`.

**Pourquoi.** La revue a confirmé 6 défauts sur 6 soumis à réfutation
(mesuré). Plusieurs critères annoncés étaient vrais par construction.
**Ce qui le renverserait.** Une nouvelle revue qui ne trouve plus de
défaut bloquant.

## 2026-11-14 — Axe 3, N3 lancé : régulation IDE non validée (T1 échoue) ; prédiction kinés confirmée

**Décision.**
- **IDE : le levier « régulation en zone sur-dotée » n'est pas validé.**
  L'effet mesuré est −30 % [−34 ; −26] sur 2012–2019, et les trois placebos
  passent. Mais le test de tendances parallèles pré-enregistré échoue
  (p = 0,043 < 0,10). On applique le protocole tel quel, sans changer le
  seuil après coup.
- **Kinés : la prédiction marche / arrêt pré-enregistrée est confirmée**
  (écart des pentes +3,1 pts/an [1,1 ; 5,1], tendances parallèles
  p = 0,24). Ce n'est pas encore une validation du module, θ n'étant pas
  pré-enregistré pour E2.
- **θ ≈ 0,80 [0,74 ; 0,87]** (part contraignante du plafond, IDE) est
  **exploratoire** : à transmettre à l'axe 1 comme valeur *supposée*, pas
  mesurée. Il suggère un plafond qui fuit plutôt que le plafond strict du
  module `regulation`.
- Toute nouvelle analyse IDE (borne de Rambachan & Roth, contrôle
  synthétique) sera un **second test**, pré-enregistré avant passage.
- Rapport : [N3](reports/2026-11-14-axe3-n3-leviers-did.md), section
  Résultat.

**Pourquoi.** Pré-enregistrement (entrée « protocoles gelés » ci-dessus) :
relâcher un seuil après avoir vu p = 0,043 recréerait le biais de K1.
**Ce qui le renverserait.** Un second test pré-enregistré qui passe, ou la
preuve que le zonage Atlasanté n'est pas celui de 2012 (qui invaliderait
aussi E2).

## 2026-11-14 — Axe 1 : sources retenues pour les hyperparamètres par profession

**Décision.** Une source primaire par famille de paramètres. Fiches dans
`fiches/param-*.md`, synthèse dans
[le rapport axe 1](reports/2026-11-14-axe1-hyperparametres.md).

**Sources retenues.**
- **Régulation, règle.** Le texte conventionnel lui-même :
  - IDE : avenant 6 (JORF du 13/06/2019) ;
  - SF : avenant 4 (JORF du 10/08/2018), reconduit par l'avenant 7 (2023) ;
  - MK : avenant 7 (arrêté du 21/08/2023) ;
  - CD : convention du 21/07/2023 (arrêté du 23/08/2023), effet au
    01/01/2025.

  Les guides ARS et les syndicats ne servent qu'à confirmer.
- **Régulation, zonage de référence pour l'axe 1.** data.gouv « Zonages des
  professionnels de santé libéraux » (`t-zonages-com.csv`, avec la date des
  arrêtés). Il concorde avec la source CartoSanté de l'axe 4 (±10
  communes) : pas de conflit avec la décision « Axe 4 : zonage par
  commune ».
- **Régulation, effet.** IRDES QES n° 270 (seule estimation causale
  publiée). Il sert de **cible de validation**, pas de paramètre à ajouter
  au plafond. θ = 0,80 de l'axe 3 est classé *supposé*, comme l'axe 3 le
  demande.
- **Filières pharmacie.** Ordre national des pharmaciens, Panorama annuel :
  primo-inscrits par section. Pour la part privée de H, conflit avec la
  DREES (17 % contre 28,6 %) : **défaut proposé = DREES**, l'Ordre en borne
  haute. Choix final au ledger.
- **Odontologie.**
  - Postes de DES : arrêtés annuels du CNG au JORF, et statistiques du CNG
    pour 2008-2018.
  - Stocks par spécialité : rapports d'activité de l'Ordre (ONCD).
- **Abandon IFSI.** DREES, enquête Écoles, jeu 491 (« Séries longues
  1966-2025 »). Le modèle lit le **rendement ρ = diplômés(t+3) / inscrits en
  1re année(t)**, qui est *mesuré*, plutôt qu'un taux d'abandon.
- **Sorties.** DD76 et ER 1062, 1075 et 1319 pour les définitions ; CNOMK
  pour l'âge de retraite des MK ; COR 2016 pour le cumul emploi-retraite.
  La mortalité n'est pas séparée de la cessation.

**Rejeté.**
- « 30 % d'abandon par an » en IFSI : aucune source primaire (QO AN n° 101,
  2023, sans source) et incompatible avec la DREES.
- « Obligation de 2 ans pour les dentistes » : elle n'existe pas. Il s'agit
  des kinés (avenant 7, art. 4.1.1).

**Pourquoi.** Le principe « aucun nombre sans source primaire et millésime »
(ROADMAP § 1). Le rendement ρ_IDE est choisi parce qu'il est calculable
chaque année sur une donnée ouverte. Il englobe abandon, redoublement et
passerelles, ce qui le rend directement utilisable par le module
`formation`.

**Ce qui le renverserait.**
- Un bilan Cnam publié sur les avenants SF et MK.
- Un suivi individuel IFSI (cohortes).
- Une publication de l'Ordre ventilant les primo-inscrits H par
  public / privé.

## 2026-11-14 — Corrections du contrat du jumeau après la revue adversariale

**Décision.** Ces règles complètent le contrat (`v2/jumeau/`). Elles
corrigent les 6 défauts de la
[revue](reports/2026-11-14-revue-adversariale-axe0.md) et 2 des 3
constats non vérifiés.
1. **La composition fait partie du scénario.**
   `TwinEstimator.trajectory(until, scenario)` construit et calibre les
   modules du scénario passé, avec un cache par composition. Un paramètre
   d'un module absent de la composition est une erreur.
2. **Une cellule sans historique a une règle de repli explicite**
   (`supposé`).
   - Elle prend la rétention de la cellule de même (profession,
     territoire, sexe) dans le secteur `repli` (privé par défaut), avec
     I = 0.
   - Sans cellule de repli, c'est une erreur ; s = 1 n'est plus donné en
     silence.
   - Le secteur public a désormais un historique réel :
     `history.sector_table` lit `v2/data/processed/secteur_stock.parquet`
     (axe 4), où les salariés ambigus sont répartis par leur part privée,
     avec trois variantes (centrale, min, max).
3. **Les dépendances entre modules sont déclarées.** Chaque module a un
   `needs` (les flux de l'année qu'il lit via `ctx.delta`) et un
   `produces`.
   - `build()` refuse un besoin que ne produit aucun module placé avant,
     ainsi que deux producteurs du même flux.
   - `ctx.delta` refuse une lecture non déclarée, et `run()` refuse un flux
     rendu mais non déclaré.
   - La régulation refuse des zones qui ne touchent aucune cellule du
     secteur régulé.
4. **Le scénario est validé et sérialisable.** `Scenario.validate` refuse
   une clé, une opération, un axe de sélecteur ou une composition inconnus.
   `to_json` / `from_json` portent un `format` égal à 1 et une `seed`
   (`ctx.rng`).
5. **Convention des quotas = v1.** Les entrées × m s'appliquent à partir de
   origine + L_p + 1 (`entrees.evenement_quotas`). Cela suit
   `app/levers.project_flow`, où l'année origine + L_p reste au niveau de
   base.
6. **Les unités sont rattachées strictement.** `Geography.up` refuse une
   unité non rattachée ou rattachée deux fois. L'écart externe
   CartoSanté / RPPS est mesuré et publié ; il n'est pas corrigé.
7. **Vieillissement et reproductibilité.**
   - Le vieillissement accepte une fraction par tranche
     (`vieillissement.fractions`, pour les tranches CartoSanté).
   - Un module remet son état à zéro dans `begin()` à chaque run
     (formation).
   - `run(floor=False)` retire le plancher à 0 pour les tests de
     conservation.

**Critères d'acceptation réécrits pour pouvoir échouer** (C1–C10,
`PYTHONPATH=v2 uv run python -m jumeau.check`, code de sortie 1 en cas
d'échec). Chaque critère porte la valeur « avant » mesurée par la revue.
Deux mutations ont été vérifiées :
- remettre s = 1 au public fait échouer C4 (+838 personnes) ;
- avancer les quotas d'un an fait échouer C7 (écart de 15 par
  département).

**Pourquoi.** La revue adversariale a confirmé 6 défauts sur 6, mesurés.
Les critères d'origine passaient par construction.
**Rejeté :** mettre les dépendances dans l'ordre (`order`) seulement : un
module renommé ou absent fausserait le résultat sans erreur. Corriger la
convention des quotas côté v1 : la v1 est figée et sert d'oracle.
**Ce qui le renverserait.**
- Une nouvelle revue qui trouve un critère vrai par construction.
- Un module de l'axe 2 qui doit lire autre chose que des flux de l'année :
  il faudrait déclarer aussi les lectures d'état.

## 2026-11-14 — Axe 4 : registre d'événements `v2/data/events.csv` ; le saut d'inscrits 2025 est un artefact

**Décision.**
- Le registre est un CSV, une ligne par texte ou fait observé : `id, date_effet, profession, flux_touche,
  type, description, source, millesime, confiance`. 30 lignes (2009–2028), 23 `verifie`, 7 `partiel`.
  Chaque ligne a sa fiche `fiches/data-ev-*.md`.
- Sources : texte primaire quand il a pu être ouvert (Légifrance, ameli, Conseil d'État, DREES, ARS) ;
  sinon une source secondaire nommée (12 lignes), à remplacer.
- Date inconnue au jour près → rentrée (01/09) ou fin d'année universitaire, dit dans la description.
- **Le saut d'inscrits 2025-26 (odontologie 2e année : 2 083) est traité comme un artefact de fichier,
  pas comme une réforme** : Université Paris Cité vaut 683 contre 188–215 les années précédentes.
  Valeur à utiliser : 1 588 (fichier compilé « Base inscrits 2ème cycle MOP »), ou Paris Cité ≈ 190.
- Rejeté : un registre qui n'a que les réformes de la liste de départ. On y ajoute les ruptures de données
  (ADELI → RPPS 2017, artefact 2025), qui déplacent les séries autant qu'une réforme.

**Pourquoi.** Mesuré : l'année blanche MK 2018 se voit dans le RPPS (moins de 25 ans, 5 637 → 3 681 au
1er janvier 2019, −35 %) ; la part de population des zones dentaires non prioritaires (5 %, ARS PACA) se
retrouve dans la table de zonage (4,8 %).
**Ce qui le renverserait.** Une notice DREES expliquant la ligne Paris Cité comme un vrai changement de
périmètre (par exemple des entrants par une nouvelle voie) ; dans ce cas, l'événement devient une réforme.

## 2026-11-14 — Reprise de l'observatoire de l'équipe : 19 éléments adoptés, sous la ROADMAP

**Décision.**
- On reprend 19 éléments de l'observatoire (Pierreafeu181), détaillés dans
  [le rapport de reprise](reports/2026-11-14-reprise-observatoire.md) :
  - pour la validation : mondes simulés, backtest toutes origines, métrique
    de classement, ER1319 ;
  - pour le modèle : levier retraite corrigé (+n ans en 65+), année de
    décision et convention de date unique, shrinkage hiérarchique, levier
    incitatif à total constant, tests de propriétés ;
  - pour les données : zonage data.gouv en contrôle croisé, estimations de
    population 1975–2026, scénario « Population âgée », cellules masquées,
    règle sur les fichiers étudiants, correspondance université → ARS.
- **Pas repris :** sa définition de « libéral », son grain, son horizon, le
  modèle unique, le vieillissement uniforme, le seuil d'alerte relatif, les
  diplômés étrangers non sourcés.
- **Réservé** à la couche personas : son site, ses conventions
  d'affichage, la densité ajustée aux besoins.

**Pourquoi.** Demande de l'utilisateur·rice, 2026-11-14 : « rapport
exhaustif de ce qu'on reprend de son travail ». `v2/ROADMAP.md` prime.
**Ce qui le renverserait.** Un élément repris qui contredit un résultat du
banc ou un monde simulé.

## 2026-11-14 — Axes 2 et 5 lancés ; skills de design installés ; trois directions pour l'observatoire

**Décision.**
- **Axes 2 et 5 lancés**, à la demande de l'utilisateur·rice. Cela remplace
  « les axes 2 et 5 attendent la correction des défauts bloquants ».
  - La session de l'axe 0 dit avoir corrigé les 6 défauts. Ses 10 critères
    réécrits passent, et deux mutations échouent comme prévu.
  - Ces corrections n'ont **pas été revues de façon indépendante**. Une
    nouvelle revue adversariale reste à faire (ledger).
- **Skills installés** dans `.claude/skills/` :
  - `impeccable` 4.9.1 (pbakaus, Apache-2.0) ;
  - `design-taste-frontend` / taste-skill 2.5.1 (Leonxlnx, MIT).

  Le binaire que télécharge impeccable n'est **pas exécuté** : on suit ses
  consignes à la main. Aucun hook n'est installé. taste-skill vise les
  sites vitrines, pas les tableaux de bord, et pèse 39 Mo dans le dépôt.
- **Trois directions artistiques proposées** pour l'observatoire
  (`v2/docs/lab/design/2026-11-14-da-observatoire.html`) :
  - **A**, sémiologie graphique (Bertin), recommandée ;
  - **B**, gamme de signalisation ;
  - **C**, topographie en isolignes ;
  - l'option standard, le DSFR, est réservée aux services de l'État.

  Aucune n'est encore choisie. Ce travail d'interface relève de la couche
  personas et ne prend pas la place des axes de recherche.

**Pourquoi.** L'utilisateur·rice, 2026-11-14 : « lance les axes 2 et 5
après », « oui, les deux » pour les skills, et « le site fait trop
claude ».
**Ce qui le renverserait.** Une revue indépendante qui trouve un défaut
bloquant restant dans le jumeau. Dans ce cas, les axes 2 et 5 s'arrêtent
sur ce point.

## 2026-11-14 — Axe 5 : sortie, facteurs, plages, N et graine de l'analyse de sensibilité

**Décision.**
- **Sortie Y** : N « libéral » (secteur privé), total national, par
  profession, en 2030, 2040 et 2050. Le jumeau tourne au département, sur le
  privé seul : sans régulation ni transition, aucun flux ne relie le privé
  et le public.
- **Infirmiers** : `secteur_stock` n'a ni âge ni sexe. On utilise donc
  `infirmiers-liberaux` (v1, SNDS par âge, 2012–2023), soit 98 854 en 2023
  contre 277 788 dans tout le privé. C'est un écart de périmètre, signalé
  dans chaque sortie.
- **Facteurs et plages** (tirage uniforme ; les niveaux discrets sont
  équiprobables) :
  - E, fenêtre d'ajustement : {2, 3, 5, 8} ans ;
  - E, shrink : {20, 200, 2000, national} ;
  - E, entrées : {plates, récentes sur 2 ans} ;
  - E, filière : {non, oui}, pour CD et PH seulement ;
  - D, part privée des salariés ambigus : {min, centrale, max} (axe 4),
    sauf pour les IDE ;
  - P, `vieillissement.fraction` : [0,18 ; 0,22] (supposé, ±10 %) ;
  - P, `sorties.part_cumul` : valeur de la fiche cumul (SF 0,8 %, CD
    4,7 %, PH 1,8 %, MK et IDE 1,5 %) × [0,5 ; 2] (supposé autour d'un
    sourcé de 2015) ;
  - L, `decalage_retraite` : [0, 2] ans ;
  - L, `cumul_multiplicateur` : [1, 2] ;
  - L, quotas × [0,8 ; 1,2] après L_p (DD76 ±20 % ; L_p de la v1, supposé).
- **Deux familles** :
  - « tout » (leviers compris) classe ce qui déplace Y ;
  - « incertitude » (leviers au tendanciel) donne la fourchette (a).
- **Variante d'entrées « tendance » exclue du plan de Sobol.** Elle
  multiplie N(2050) par 2 à 10 (SF, fenêtre de 2 ans : 183 200 contre
  19 000, mesuré). Elle est rapportée à part, sur une grille.
- **Méthodes.**
  - Morris : r = 30 trajectoires, p = 4 niveaux, pas Δ = 2/3.
  - Sobol : estimateurs Saltelli 2010 (S1) et Jansen (ST), N = 2048,
    soit N(k + 2) runs.
  - Intervalles bootstrap à 95 %, 500 tirages.
  - Graine 20261114, celle du protocole N1.
  - Tout est implémenté en numpy (ni SALib ni scipy dans l'environnement).
- **Hors analyse par construction** : `formation.*` (le vivier n'alimente
  pas N), la régulation (zones communales, non activables au département)
  et les fiches sans point d'entrée dans le jumeau. Effet nul **par lecture
  du code**, non mesuré.

**Pourquoi.** La tâche de l'axe 5 (`v2/ROADMAP.md`) : mettre un prix sur
l'axe 1 et donner les fourchettes à 2050. Les leviers ne sont pas des
incertitudes : les mélanger à la fourchette la rendrait dépendante de la
politique choisie.
**Ce qui le renverserait.**
- Un indice ST dont l'intervalle bootstrap est plus large que l'indice
  lui-même : il faudrait augmenter N.
- Un module de l'axe 2 qui branche formation ou régulation : à refaire.

## 2026-11-14 — Dépôt git autonome, commits sans mention de Claude

**Décision.**
- Le projet est un dépôt git autonome, nommé `hackathon_acces_soins`,
  indépendant de sevel.
- Les commits sont découpés par thème.
- Les messages de commit ne mentionnent pas Claude (règle inscrite dans
  `CLAUDE.md`).
- Restent hors du dépôt : les données brutes et traitées, le mémoire
  EHESP (document tiers) et le skill taste-skill (39 Mo, réinstallable).

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Ce qui le renverserait.** Un besoin de versionner les données traitées.
Dans ce cas, on passerait par Git LFS ou un dépôt de données séparé.

## Open / not yet decided
- **Exigence d'interface (utilisateur·rice, 2026-11-14) : « très fluide
  visuellement, un véritable outil d'aide à la décision ».** Traduction
  proposée, en critères vérifiables :
  1. l'objet principal est l'**écart du scénario au tendanciel**, pas deux
     courbes de niveau ;
  2. chaque écart est **expliqué par flux** (entrées, sorties, régulation,
     transitions) ;
  3. le **délai d'effet** d'un levier est visible (quotas : rien avant la
     durée des études) ;
  4. réponse aux leviers en moins de **100 ms** perçus, avec des
     transitions animées entre échelles et entre états, et sans
     rechargement. Le jumeau met 17 ms au département, mais environ 3 s à
     la commune : il faudra précalculer ;
  5. l'incertitude est toujours affichée ;
  6. une fiche de synthèse par territoire, exportable.
- **La DA doit rester modifiable dans Figma** par les designers UX de
  l'équipe (demande de l'utilisateur·rice, 2026-11-14). Proposé, pas encore
  fait :
  - une source unique de tokens au format W3C Design Tokens (JSON) ;
  - les directions A, B et C deviennent trois *modes* d'une même collection
    de variables Figma ;
  - le site ne lit que des variables CSS générées depuis ce JSON ;
  - aller-retour avec Figma par le plugin Tokens Studio (synchronisé avec le
    dépôt) ou par le connecteur Figma MCP (lecture de `get_variable_defs`).
    L'import natif de variables JSON dans Figma reste à vérifier ;
  - règles d'encodage des données non modifiables dans Figma : une gamme par
    variable, pas de rouge/vert, hachures pour l'incertitude, lexique
    neutre.
- **Articulation avec l'observatoire de l'équipe** (dépôt
  Pierreafeu181/Hackathon-Evolution-soin, membre de l'équipe, présenté le
  2026-11-14). Il fournit déjà une interface Next.js, des leviers en
  direct et un « besoin » pondéré par âge, par département, jusqu'en 2040.
  - Proposé, pas encore décidé : la v2 est le **moteur de recherche** (le
    jumeau, la validation, les paramètres sourcés), et l'observatoire est
    la **future couche personas et restitution**.
  - **Précisé le 2026-11-14 par l'utilisateur·rice : `v2/ROADMAP.md`
    prime.** L'observatoire est une ressource de l'équipe, pas une
    contrainte : il n'impose ni la définition de « libéral », ni le grain,
    ni l'horizon, ni la méthode.
  - Une interface d'échange reste à définir (export de scénarios du jumeau
    vers ses JSON).
  - L'application Streamlit v1 ne serait alors plus reprise.
- Unité de l'offre : effectif ou équivalent temps plein (taux d'activité α).
  Question héritée de la v1.
- Quels « groupes de communes » utiliser : territoires de démocratie
  sanitaire, zonage ARS, bassins de vie ou EPCI. Question héritée de la v1.
- Mistral : le hackathon impose-t-il un modèle Mistral ? Question héritée
  de la v1.
- Ordre d'application des modules (séparation d'opérateurs) : fixé par
  `order` (formation 5, vieillissement 10, sorties 20, entrées 30,
  régulation 40). La sensibilité de N(2050) à cet ordre n'est pas mesurée
  (voir open.md).
- Part privée des pharmaciens hospitaliers (section H) : DREES 17 % ou Ordre
  28,6 % ? Défaut proposé : DREES (axe 1, 2026-11-14). Voir open.md.

## 2026-11-14 — Axe 2 : 5 variantes pré-inscrites au banc N1 avant tout passage ; périmètre confirmatoire = privé

**Décision.**
- Inscrites à 03:25 dans `v2/validation/registry.py`, **avant** tout
  passage sur le banc :
  - confirmatoires : `axe2_ages_interp` (A1a), `axe2_ages_simples` (A1b),
    `axe2_shrink_hier` (A2), `axe2_retention60` (A3), `axe2_combine`
    (A1a + A2 + A3) ;
  - diagnostic : `axe2_obs_r12` (B4).
- Dérivation et prédictions écrites avant le banc :
  [derivations/2026-11-14-axe2-methodes.md](derivations/2026-11-14-axe2-methodes.md),
  SHA-256 `1c324f5795b0`.
- **Périmètre confirmatoire : privé**, part centrale de l'axe 4.
  - N1 prévoyait l'ancien périmètre seulement « tant que la séparation
    n'existe pas ».
  - Infirmiers : libéraux du RPPS (l'âge des salariés privés manque).
  - L'ancien périmètre (libéral + mixte) est rapporté en secondaire, pour
    la comparaison avec K1.
- Code dans `v2/methodes/`, branché par le registre du jumeau (3 modules
  `methodes_*`). Aucun fichier de `v2/jumeau/` n'est modifié.
- **Contrôles** (`PYTHONPATH=v2 uv run python -m methodes.verif`) :
  - aux options v1, la composition reproduit `twin_of(StockFlowLocal)` à
    9e-13 personne près ;
  - le recalcul jusqu'en 2050 prend 14 à 40 ms (5 professions,
    département).
- **Écart de propriété signalé :** `registry.py` appartient à l'axe 3.
  - On n'y fait qu'un ajout en fin de fichier, parce que le protocole N1
    gelé impose d'y inscrire les variantes.
  - Les lignes existantes ne sont pas touchées.

**Pourquoi.** Le protocole N1 (SHA `eb527ecb06a0`, vérifié intact) rend
confirmatoire seulement une variante inscrite avant son premier passage.
**Rejeté :** régler k (shrinkage) ou la largeur des tranches ouvertes sur
le banc, parce que ce serait choisir après avoir vu.
**Ce qui le renverserait.** L'axe 3 qui refuse l'inscription hors de son
fichier. On déplacerait alors les entrées, avec leur heure.
