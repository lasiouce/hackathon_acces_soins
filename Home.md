---
type: home
aliases: [Home, Index]
---

# hackathon-sante: Home

Project health workforce numbers (MMOPKSI, excluding general practice) by
territory, to 2035+, and simulate policy levers. Open data only.
[Project brief](CLAUDE.md) · [Lab profile](docs/lab/profile.md)

> **Recadrage 2026-11-14 :** projet de recherche. Jumeau numérique des
> effectifs « libéraux » (secteur privé) SF, CD, PH, MK et IDE, à toutes les
> échelles jusqu'à la commune, horizon 2050. → **[v2/](v2/README.md)** · [feuille de route](v2/ROADMAP.md) · [décisions v2](v2/docs/lab/decisions.md). Tout ce qui suit est la v1, figée.

## Status (update when something moves)

| | |
|---|---|
| Model | **H1 cohort-component stock-flow**, promoted, not built. [Derivation](docs/lab/derivations/workforce-projection-model.md) |
| Data | Stock ✅ DREES RPPS 2012–2026, dép × age × sex × mode (nurses partial) · population ✅ Omphale 2018–2070, 3 scenarios · pipeline M/O/P ✅. [Inventory](docs/lab/explorations/data-inventory.md) |
| Users | ARS/DG (commune → groups of communes → dép → région) · Administration (all parameters) · politician (plain words, [lexicon](docs/lab/lexicon.md)) |
| Product | **library of estimation algorithms** behind one interface; backtest = comparison bench ([decision](docs/lab/decisions.md)) |
| Stage 1 | demographic projections: Hippocrate (DREES) supply + Omphale (Insee) population → density per 100k |
| Loaders | ✅ `uv run python -m sante.load` → `data/processed/` (stock, population, checks). Max gap vs totals 0.13 %. [Report](docs/lab/reports/2026-11-13-loaders.md) |
| Backtest K1 | ⚠️ corrected 2026-11-13: entry double-count fixed. H1 local rates is best per département (8.1 % vs 8.7 % trend); the national claim is withdrawn (−10 to −12 % at 8 y for specialists and dentists). [Report](docs/lab/reports/2026-11-13-k1-backtest.md) |
| App | ✅ `uv run --directory app streamlit run main.py`: 4 pages, any estimator + live self-backtest band, compare up to 3; **levers wired: L01–L06, L09, L10, L14, L32** (68 ms per lever change, measured). [Decision](docs/lab/decisions.md) |
| Jumeau (axe 0) | ✅ `v2/jumeau/` : état à cellules (profession, secteur, territoire, sexe) × âge, modules plug-ins, scénarios datés ; stock-flux v1 reproduit à 0,0 ; critères C1–C11 après 2 revues adversariales (tous OK, mutations rejouées) ; 21 ms par scénario (dép.). `PYTHONPATH=v2 uv run python -m jumeau.check`. [Rapport](v2/docs/lab/reports/2026-11-14-jumeau-axe0.md) |
| Données (axe 4) | ✅ public / privé séparé (`v2/data/build_secteur.py`) : « libéral » = privé 2026, SF 12 059 – 14 660, PH 60 005 – 67 219, CD 40 784 – 47 894, MK 98 828 – 103 986, IDE 2023 277 788 · zonage par commune × 4 professions (`build_zonage.py`) · registre d'événements `v2/data/events.csv` · grain communal : 5 professions observables à la commune (Annuaire nov. 2026), projetable BV/EPCI (IDE), EPCI hiérarchique (MK, PH), dép. (CD, SF) |
| Méthodes (axe 2) | ✅ `v2/methodes/` : banc N1 lancé (privé). Stock-flux taux locaux 8,68 % bat la tendance 9,30 % ; **shrinkage hiérarchique 8,57 %** bat la référence (−0,11 pt [−0,21 ; −0,02]) ; âges simples à égalité ; rétention 60+ en tendance pire. `PYTHONPATH=v2 uv run python -m methodes.banc`. [Rapport](v2/docs/lab/reports/2026-11-14-axe2-methodes.md) |
| Next | voir [v2/ROADMAP.md](v2/ROADMAP.md), axe 0 d'abord (contrat des modules) · *(avant le 2026-11-14 :* check stock-flow growth (specialists libéraux +36 % by 2035) · second backtest origin · private-practice nurse slowdown · wire levers into estimators*)* |

## Present
- [One-page TL;DR (PDF), 2026-11-13](docs/lab/presentations/2026-11-13-tldr.pdf). Rebuild it with `uv run --with reportlab python scripts/tldr_pdf.py`
- [Status deck, 2026-11-13](docs/lab/presentations/2026-11-13-status.md). Open it and use *Start presentation* from the command palette.

## Records
| What | Where | Add one with |
|---|---|---|
| **Analyses** (each result, with its number) | [reports/](docs/lab/reports/) | template `analysis` |
| Decisions and live hypotheses | [decisions.md](docs/lab/decisions.md) | `/record-decision` |
| Open questions, each with a price | [open.md](docs/lab/open.md) | any skill |
| Derivations (model form, from first principles) | [derivations index](docs/lab/derivations/README.md) | `/derive-ansatz` |
| Explorations (data, literature) | [explorations index](docs/lab/explorations/README.md) | `/explore-and-report` |
| Decks for colleagues | [presentations/](docs/lab/presentations/) | template `deck` |

## Browse and filter
![[Records.base]]

Switch views with the menu at the top left of the table: All records · Analyses · Drafts to finish · Model & data · Decks. *Filter* adds a condition on author, status, profession, tag or type. *Sort* reorders.
`professions` takes these values: `specialistes`, `sages-femmes`, `dentistes`, `pharmaciens`, `kines`, `infirmiers`, `all`.

## Analyses log (newest first)
| Date | Analysis | Headline | Author |
|---|---|---|---|
| 2026-11-14 | [Projection communale, axe 2](v2/docs/lab/reports/2026-11-14-axe2-communes.md) | K (cohortes commune ⊂ EPCI ⊂ dép ⊂ région) et K2 (part tenue + bande empirique) rejetés au banc N4 ; K2 calibré pour les IDE de 1 à 50 (81–83 %) ; l'erreur du total départemental domine les grandes communes | équipe |
| 2026-11-14 | [Projection communale : données, axe 4](v2/docs/lab/reports/2026-11-14-axe4-projection-communale.md) | pharmaciens par commune 2012–2026 (erreur médiane 16 % commune, 10,7 % EPCI : test échoué de peu) ; SF : historique communal non disponible ; passage COG 2026 ; petits effectifs pour N4 | axe 4 |
| 2026-11-14 | [Flux communaux, axe 4](v2/docs/lab/reports/2026-11-14-axe4-flux-communaux.md) | installations nettes par commune 2012–2025 (test année blanche MK échoué : 0,90) ; officines 2004–2025, 20 083 en 2025 (Ordre +0,4 %) ; attributs 35 011 géocodes × 14 ans ; SF « libéral » 2026 : 12 059 – 13 331 | axe 4 |
| 2026-11-14 | [Sensibilité et fourchettes 2050, axe 5](v2/docs/lab/reports/2026-11-14-axe5-sensibilite.md) | En 2050, la décision pèse plus que l'ignorance pour les IDE (0,88 contre 0,12) et les MK (0,71 contre 0,15), pas pour SF ni CD (0,41 contre 0,57–0,59) ; part privée, filière et fenêtre portent l'incertitude ; cumul sans effet ; assez sûr pour décider dans 57 dép. IDE, 26 MK, 0 ailleurs ; fourchette nationale −17 à +34 % (propagation), ±9 à ±66 % (backtest extrapolé) | équipe |
| 2026-11-14 | [Cohortes bayésiennes, axe 2 étape 2](v2/docs/lab/reports/2026-11-14-axe2-cohortes-bayesiennes.md) | MAPE dép. h=5 7,73 % contre 8,68 % (stock-flux), Δ −0,95 [−1,51 ; −0,47] ; bande à 80 % couvrant 77,6 % (toutes origines) ; CRPS à égalité avec la naïve probabiliste | équipe |
| 2026-11-14 | [Grain communal, axe 4](v2/docs/lab/reports/2026-11-14-axe4-grain-communal.md) | 5 professions observables à la commune (Annuaire nov. 2026) ; projetable : BV / EPCI (IDE), EPCI hiérarchique (MK, PH), dép. (CD, SF) ; 24 % des dentistes et 32 % des kinés sans DE français | axe 4 |
| 2026-11-14 | [APC des sorties, axe 2 étape 1](v2/docs/lab/reports/2026-11-14-axe2-apc-sorties.md) | APC gaussien de la rétention nette : MAPE dép. h=5 8,74 % contre 8,68 % (égalité) ; CRPS relatif 6,82 % mais couverture 80 % = 50 % (entrées sans incertitude) ; calibration par simulation réussie | Claude |
| 2026-11-14 | [Accueil de la carte V2 : challenge par personas](v2/docs/lab/reports/2026-11-14-accueil-personas.md) | 3/3 personas refusent l'accueil actuel ; 3/3 veulent un chiffre-phrase sans clic et les leviers repliés ; désaccord sur l'entrée (territoire contre national) | Claude |
| 2026-11-14 | [UAT de l'écran de décision, V1 et V2](v2/docs/lab/reports/2026-11-14-uat-interface.md) | V1 11/22 tâches réussies, 38/40 constats confirmés ; V2 carte recommandée pour la démo sous P1 (horizon, libellés, erreurs réseau) ; recette V2 à rejouer (onglet partagé) | Claude |
| 2026-11-14 | [Écran de décision V2 : carte plein écran](v2/docs/lab/reports/2026-11-14-prototype-carte.md) | levier → carte des 101 dép. + fiche recalculées en 53 ms p50, 66 ms p95 (n = 35, cible < 150 ms) ; recherche, survol, fiche, comparer, lien, export | Claude |
| 2026-11-14 | [Produit : défenseur contre acheteur public](v2/docs/lab/reports/2026-11-14-produit.md) | pas achetable en l'état : 8 conditions de signature, 0 remplie complètement ; voie = commun libre porté par une institution + prestation < 60 k€ HT par ARS ; [pitch 3 min](v2/docs/lab/presentations/2026-11-14-pitch.md) | Claude |
| 2026-11-14 | [Méthodes de prévision, axe 2](v2/docs/lab/reports/2026-11-14-axe2-methodes.md) | Shrinkage hiérarchique dép → rég → nat : MAPE dép. h=5 8,57 % contre 8,68 % (stock-flux taux locaux), Δ −0,11 pt [−0,21 ; −0,02], reproduit sur l'ancien périmètre ; âges fins à égalité (mais erreur 60+ ÷ 3 sur monde simulé) ; rétention 60+ en tendance pire | Claude |
| 2026-11-14 | [Registre d'événements, axe 4](v2/docs/lab/reports/2026-11-14-axe4-registre-evenements.md) | 30 événements datés et sourcés (23 vérifiés) ; année blanche MK 2018 visible dans le RPPS (−35 % de moins de 25 ans) ; saut d'inscrits 2025 = artefact Paris Cité | Claude |
| 2026-11-14 | [Zonage par commune, axe 4](v2/docs/lab/reports/2026-11-14-axe4-zonage-commune.md) | 34 919 géocodes × 4 professions ; dentistes « remplacement seul » 97 géocodes, 4,8 % de la population (cité : 97, ≈ 5 %) | Claude |
| 2026-11-14 | [Public / privé, axe 4](v2/docs/lab/reports/2026-11-14-axe4-secteur-public-prive.md) | « libéral » = privé, SF 2026 : 12 059 – 14 660 (était 12 475 – 26 428, largeur −81 %) ; secteur lu dans les fichiers DREES, ambiguïtés par FINESS | Claude |
| 2026-11-14 | [État de l'art : modèles en boîte blanche](v2/docs/lab/explorations/2026-11-14-etat-de-lart-methodes.md) | d'abord de meilleurs modèles sur la même structure (cohortes bayésiennes, APC, logit d'installation, MinT), puis des données de flux ; très peu de nouveaux hyperparamètres | Claude |
| 2026-11-14 | [Troisième revue adversariale, axe 0](v2/docs/lab/reports/2026-11-14-revue-adversariale-axe0-v3.md) | aucun défaut bloquant restant dans le jumeau ; conservation ≤ 0,5 personne ; 5 défauts importants ; leviers du prototype réactivés | Claude |
| 2026-11-14 | [Seconde revue adversariale, axe 0](v2/docs/lab/reports/2026-11-14-revue-adversariale-axe0-v2.md) | 6 constats sur 6 confirmés, soit 4 défauts bloquants : retraite 65+ (+41 % à Δ = 2), régulation non conservative (+254 CD), trajectory() écrase le scénario de base (−15 %), valeurs non validées | Claude |
| 2026-11-14 | [UAT agentique de la carte](v2/docs/lab/reports/2026-11-14-uat-agentique-carte.md) | 5 tâches réussies sur 21 (14 partielles) ; 37 constats confirmés sur 41 ; 3 P0 (fiche d'une autre profession, sélecteur hors écran sur mobile, export sans sources) et 9 P1 | Claude |
| 2026-11-14 | [UAT agentique de la carte V2](v2/docs/lab/reports/2026-11-14-uat-carte-v2.md) | 4 tâches réussies sur 19 ; 30 constats confirmés sur 39 ; 1 P0 (profession hors écran sur mobile), 6 P1 | Claude |
| 2026-11-14 | [Tests des boucles de rétroaction (N9)](v2/docs/lab/reports/2026-11-14-axe3-n9-boucles.md) | densité → installations : nul (IDE, MK, CD) ; densité → rétention 45-54 ans : confirmé pour les IDE seuls (+0,11 [+0,05 ; +0,18]) | Claude |
| 2026-11-14 | [Prétirage de synthèse](v2/papers/synthese/main.tex) | feuille de route + 6 axes + interface et UAT + suite ; régénéré par build.py, compile sans référence indéfinie | Claude |
| 2026-11-14 | [Prototype de l'écran de décision](v2/docs/lab/reports/2026-11-14-prototype-decision.md) | branché sur le jumeau : 3–32 ms (jumeau), 50–120 ms aller-retour ; écart décomposé exactement par flux ; kinés, quotas +20 % et régulation → +8 645 en 2050 (+5,4 %) | Claude |
| 2026-11-14 | [Reprise de l'observatoire de l'équipe](v2/docs/lab/reports/2026-11-14-reprise-observatoire.md) | 31 éléments : 19 repris ou adaptés, 2 à vérifier, 7 non repris, 3 réservés aux personas ; plus utiles : mondes simulés, levier retraite +n ans, zonage data.gouv, ER1319 | Claude |
| 2026-11-14 | [Dépôt Evolution-soin, lecture critique](v2/docs/lab/reports/2026-11-14-depot-evolution-soin.md) | même famille de modèle que notre v1 ; mondes simulés : +8 à +19 % de seniors (âges uniformes par tranche) ; levier retraite à revoir chez nous | Claude |
| 2026-11-14 | [Revue adversariale, axe 0](v2/docs/lab/reports/2026-11-14-revue-adversariale-axe0.md) | 6 défauts confirmés sur 6 (4 bloquants) : plug-in ignoré par twin_of, public sans sorties (+822 kinés en 2050), dépendances implicites, scénario non validé ; axes 2 et 5 en attente | Claude |
| 2026-11-14 | [Jumeau numérique, axe 0 (v3, après 2 revues)](v2/docs/lab/reports/2026-11-14-jumeau-axe0.md) | 11/11 critères passent, chacun échoue sur le code d'avant ; retraite B1 : séjour 65+ = +Δ ans exact ; régulation conservative (Δ total ≈ 0) ; v1 reproduite à 0,0 ; 21 ms par scénario (dép.) | Claude |
| 2026-11-13 | [Pipeline entries](docs/lab/reports/2026-11-13-pipeline-entries.md) | student cohorts cut national bias for specialists (−6.5 → −4.1 %) and pharmacists; the rest of the gap = young entrants + working past 65 | Claude |
| 2026-11-13 | [CartoSanté commune loader](docs/lab/reports/2026-11-13-cartosante-commune-loader.md) | 1.24 M rows, 3 professions × 34,847 communes × age, 2004–2025; communes = dép totals except dép 13 (Marseille dropped); midwives excluded | Claude |
| 2026-11-13 | [Stress tests and feedback](docs/lab/derivations/stress-tests-and-feedback.md) | shocks = levers (same object); feedback can reallocate ≤ ~3 %/yr of stock, so a 20 % gap needs ≥ ~7 y | Claude |
| 2026-11-13 | [API scout: ameli, CartoSanté, Atlasanté](docs/lab/reports/2026-11-13-api-scout-ameli-cartosante.md) | 37 relevant datasets, 30 by public API; commune grain only via CartoSanté (4 professions); no pharmacist counts in either | Claude |
| 2026-11-13 | [Data inventory, ameli](docs/lab/explorations/data-inventory.md) | ameli private practice 2010–2025, 23 specialties; agrees with DREES within 0–13 % by profession | Claude |
| 2026-11-13 | [K1 backtest](docs/lab/reports/2026-11-13-k1-backtest.md) | H1 national error 2.5 % vs 4.6 % trend; per département ties trend (8.6 vs 8.7 % MAPE) | Claude |
| 2026-11-13 | [Salaried nurses raked to dép × age × sex](docs/lab/reports/2026-11-13-nurses-salaried-raking.md) | 508,790 salaried nurses (2023); marginals hit to 1e-7 %, ≤ 2 persons off the raw cells | Claude |
| 2026-11-13 | [Loaders](docs/lab/reports/2026-11-13-loaders.md) | tidy stock + population; detailed cells match totals within 0.13 % | Claude |
| 2026-11-13 | [Data inventory, update](docs/lab/explorations/data-inventory.md) | stock + population in: 15 years of dép × age × sex for 5/6 professions; K1 unblocked | Claude |
| 2026-11-13 | [Data inventory](docs/lab/explorations/data-inventory.md) | 8 files = student pipeline only. The stock is missing | Claude |
| 2026-11-13 | [Projection model form](docs/lab/derivations/workforce-projection-model.md) | stock-flow model. Quotas can't move the 2035 specialist count (h < training lag) | Claude |

## Conventions
- One note per analysis, from the template. The **headline carries a number**.
  Every input names its dataset and vintage.
- Figures go in `docs/lab/figures/`. Diagrams are Mermaid.
- Add a row to the log above when an analysis lands. That table is what we
  present from.
