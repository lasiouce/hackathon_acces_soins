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
| Jumeau (axe 0) | ✅ `v2/jumeau/` : état à cellules (profession, secteur, territoire, sexe) × âge, modules plug-ins, scénarios datés ; stock-flux v1 reproduit à 0,0 ; critères C1–C10 corrigés après revue adversariale (tous OK) ; 17 ms par scénario (dép.). `PYTHONPATH=v2 uv run python -m jumeau.check`. [Rapport](v2/docs/lab/reports/2026-11-14-jumeau-axe0.md) |
| Données (axe 4) | ✅ public / privé séparé (`v2/data/build_secteur.py`) : « libéral » = privé 2026, SF 12 059 – 14 660, PH 60 005 – 67 219, CD 40 784 – 47 894, MK 98 828 – 103 986, IDE 2023 277 788 · zonage par commune × 4 professions (`build_zonage.py`) · registre d'événements `v2/data/events.csv` |
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
| 2026-11-14 | [Registre d'événements, axe 4](v2/docs/lab/reports/2026-11-14-axe4-registre-evenements.md) | 30 événements datés et sourcés (23 vérifiés) ; année blanche MK 2018 visible dans le RPPS (−35 % de moins de 25 ans) ; saut d'inscrits 2025 = artefact Paris Cité | Claude |
| 2026-11-14 | [Zonage par commune, axe 4](v2/docs/lab/reports/2026-11-14-axe4-zonage-commune.md) | 34 919 géocodes × 4 professions ; dentistes « remplacement seul » 97 géocodes, 4,8 % de la population (cité : 97, ≈ 5 %) | Claude |
| 2026-11-14 | [Public / privé, axe 4](v2/docs/lab/reports/2026-11-14-axe4-secteur-public-prive.md) | « libéral » = privé, SF 2026 : 12 059 – 14 660 (était 12 475 – 26 428, largeur −81 %) ; secteur lu dans les fichiers DREES, ambiguïtés par FINESS | Claude |
| 2026-11-14 | [Reprise de l'observatoire de l'équipe](v2/docs/lab/reports/2026-11-14-reprise-observatoire.md) | 31 éléments : 19 repris ou adaptés, 2 à vérifier, 7 non repris, 3 réservés aux personas ; plus utiles : mondes simulés, levier retraite +n ans, zonage data.gouv, ER1319 | Claude |
| 2026-11-14 | [Dépôt Evolution-soin, lecture critique](v2/docs/lab/reports/2026-11-14-depot-evolution-soin.md) | même famille de modèle que notre v1 ; mondes simulés : +8 à +19 % de seniors (âges uniformes par tranche) ; levier retraite à revoir chez nous | Claude |
| 2026-11-14 | [Revue adversariale, axe 0](v2/docs/lab/reports/2026-11-14-revue-adversariale-axe0.md) | 6 défauts confirmés sur 6 (4 bloquants) : plug-in ignoré par twin_of, public sans sorties (+822 kinés en 2050), dépendances implicites, scénario non validé ; axes 2 et 5 en attente | Claude |
| 2026-11-14 | [Jumeau numérique, axe 0 (v2, après revue)](v2/docs/lab/reports/2026-11-14-jumeau-axe0.md) | 10/10 critères capables d'échouer passent (C1–C10) ; stock-flux v1 reproduit à 0,0 ; régulation sans création (avant +822) ; 17 ms par scénario (dép.), ≈ 3 s extrapolé à la commune | Claude |
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
