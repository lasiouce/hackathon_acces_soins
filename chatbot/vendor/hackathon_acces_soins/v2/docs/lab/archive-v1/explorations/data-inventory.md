---
type: exploration
date: 2026-11-13
author: Claude
status: done
headline: 8 files = M/O/P student pipeline 2020-2025; workforce stock missing
professions: [all]
tags: [data]
---

# Data inventory: the 8 files received, against what the stock-flow model (H1) needs

**Filed:** 2026-11-13 · **Source:** `artifacts/schema_report.txt`, a schema-only
report from `scripts/schema_report.R`. No rows were read.
**Status:** the inventory is done. The workforce stock is **missing**, which
blocks H1 and K1.

## What each file is

| File | What it is (from schema) | Grain | Years | Professions |
|---|---|---|---|---|
| `2026 - Données Modèles Démo Medicale Junior.xlsx` | **Source list, not data**: 4 sources (3 Insee, 1 DREES), each with its URL and the use it was put to. Includes "Professionnels de santé au 1er Jan 2022" (DREES) and the 2022 population on COG 2023 geography (Insee) | 1 row per source | 2022 | — |
| `990_drees_mmop2_f.xlsx` · `Feuil1` | Enrolments, long format (**the cleanest table**): diploma × year of study × teaching site (8-char code) × ARS region × attached establishment → `Inscriptions` (numeric) | site × diploma × year of study | 2020–2024 (5) | DE + DES in médecine, pharmacie, odontologie |
| `990_drees_mmop2_f.xlsx` · per-year sheets, `990_drees_mmop2_2526.xlsx` | The same table, one sheet per academic year. `Inscriptions` is stored as **text** (contains "-"), and each sheet has one stray header row | as above | 2020–2025 (6) | as above |
| `990_drees_mmop2_f.xlsx` · `Feuil2` | Pivot by region, 26 columns, no headers | region | ? | ? |
| `Base inscrits 2ème cycle MOP.xlsx` | Enrolments by academic year × cycle × year of study (2–6, plus thesis) × M/O/P × UFR × city × ARS, **plus a lookup table: training cities with lon/lat** | UFR × year of study | 2020-21 → 2025-26 (6) | M, O, P (the maïeutique column exists but holds no midwifery rows) |
| `Données médecine 1er_2ème_3ème cycle.xlsx` | Wide pivots, ARS × UFR. Years of study are repeated in one block per academic year. Count rows and **% variation rows are mixed in the same columns**. Sheets: 1er cycle, 2e cycle (FASM1–3), internat years 1–6 + thesis | UFR | ~6 years | médecine |
| `Données odontologie 2ème et 3ème cycle.xlsx`, `Données pharma 2ème et 3ème cycle.xlsx` | Same wide layout: 2e cycle and internat | UFR | ~6 years | odonto, pharma |
| `nf-sies-2025-31-…xlsx` | SIES publication (2025) on entry into health studies: numerus apertus, PASS/L.AS pass rates, the path of 100 new baccalaureate holders (e.g. "29 admitted into MMOPK year 2", "5 into IFSI"), the MMOPK split by L.AS discipline, social and sex profile | national | 2020–2024 cohorts | MMOPK, incl. kiné and maïeutique *shares* |

## Coverage against the model (derivation `workforce-projection-model.md`)

| Model input | Status | Comment |
|---|---|---|
| **Stock N[p, d, age, sex]** | ❌ **missing** | Only a pointer: the DREES "Professionnels de santé au 1er janvier 2022" source in the source list. **Blocks H1.** |
| **Stock history ≥ 8 years** (backtest K1) | ❌ missing | Blocks K1. Without it there is no accuracy claim |
| Exits x[p, age, sex] | ❌ missing | Derivable from two or more years of stock by age |
| **Entries pipeline E (M, O, P)** | ✅ have | Students by year of study × site × region, 2020–2025. This **fixes entries up to ~2031+ for M/O/P**: K2's pipeline lock can use real numbers |
| Entries: maïeutique, kiné, infirmiers | ⚠️ national shares only | SIES gives shares into MMOPK and IFSI, but there are no IFMK/IFSI/midwifery-school enrolments by region |
| **Specialist vs GP split** | ❌ missing | `DES MEDECINE` aggregates every specialty, **including médecine générale**, which the brief excludes. Needs the internship-post allocation by specialty |
| Installation shares π (where graduates settle) | ❌ missing | Only the training location is known (region/city). Training region can serve as a *proxy* (intuition), which is what the internship-post lever acts on |
| Population and projections | ⚠️ pointer only | 2022 population on COG 2023 (Insee) in the source list. The Omphale 2070 projections are not here |
| Need: use rates u[p, age] | ❌ missing | e.g. ameli data on consumption of care |
| Activity rate α | ❌ missing | |

## Cleaning notes (for whoever writes the loaders)

- Use the **8-char site/establishment codes**, not the labels. Labels are cut
  at 30 characters and their case varies.
- Region names differ between files ("Haut de France" vs "Hauts-de-France").
  Map them once to official codes.
- In the wide pivots, rows whose labels contain "Pourcentage de variation"
  are % variation, not counts. Drop them before any sum.
- In the per-year mmop2 sheets: parse `Inscriptions` as text → number, and
  treat "-" as suppressed small counts. Treat as NA, not 0. Drop the row
  where `ANNEE` = "Inscriptions".
- `année_dans_le_diplôme` = `13` is undocumented. It probably means a thesis
  or extra year (assumed). Check against the DREES dictionary.

## What to experiment with next

1. Get the stock: DREES series of health professionals by profession × age ×
   sex × département. It is public (the RPPS/ADELI-based demography), and
   its URL is already in the source list. Get as many years as exist.
2. Get the specialty split for internship posts (the EDN/ECN allocations, by
   specialty and subdivision), to separate specialists from GPs.
3. Get IFSI/IFMK/midwifery-school enrolments by region (DREES survey of
   health-training schools).
4. Get Insee Omphale population projections by département × age.

---

## Update 2026-11-13: public stock and population downloaded

These are 12 public files, downloaded with the user's approval into
`data/raw/drees/`, `data/raw/omphale/` and `data/raw/docs/`.
- **DREES**, "La démographie des professionnels de santé depuis 2012",
  data.drees, attachments last updated 2026-07-02.
- **Insee**, "Projections de population 2018-2070, tableaux détaillés
  départements" (Omphale 2022, page 7747107).

The structure below is from the schema report. Totals are the max of the
"Ensemble" rows (measured).

| File | Breakdown (all crossed unless noted) | Years | France total, last year |
|---|---|---|---|
| Médecins RPPS | dép × **specialty (15 groups + GP flag)** × mode (libéral / mixte / salarié hosp. / autre salarié) × 5-yr age (to 75+) × sex. Extra sheets: 92 detailed specialties (national), **region of diploma × region of practice**, number of activities | 2012–2026 | 242,185 (all doctors incl. GPs) |
| Dentistes, Pharmaciens, Sages-femmes RPPS | dép × activity sector × mode × 5-yr age (to 65+) × sex. Plus mean ages and density sheets | 2012–2026 | 48,690 · 75,335 · 26,428 |
| Kinés RPPS / ADELI | same structure. ADELI has 13 sectors vs 10 and 18 % NA. **Series break in 2017** | 2017–2026 / 2012–2016 | 111,384 |
| Infirmières libérales SNDS | dép × sex × 5-yr age | 2012–2023 | 98,854 |
| Infirmières salariées BTS | dép × sector / specialty / sex / age as **marginals only** (not crossed) | 2013–2023 | 508,790 |
| Omphale 2022 Central / Pop basse / Pop haute | 101 départements × sex × 20 five-year age bands. A Documentation sheet describes the scenarios | 2018–2070 | 68.09 M in 2026 (Central) |

**What changes:**
- **The stock is no longer missing.** For 5 of 6 professions it is
  dép × age × sex × mode, every year 2012–2026. That is **15 years**, so the
  K1 backtest is possible: fit on 2012–2018, project 2018 → 2026.
- **The specialist/GP split is solved**: `specialites_agregees` gives
  "1-Médecine générale" vs "2-Autres spécialités".
- **Region of diploma × region of practice** is the empirical installation
  matrix π for doctors. This feeds the internship-location lever.
- **Nurses are partial.** Private practice is fully crossed (to 2023).
  Salaried nurses come as marginals, so age × sex by dép has to be
  *estimated*, e.g. by raking the marginals.
- The age bands are 5-year, not single years. Use the standard
  cohort-component form, where 1/5 of a band moves up each year. Exits are
  estimated by comparing bands 5 years apart.

**Loader traps:**
- Every dimension has an aggregate "Ensemble" / "00-" level. Filter all
  dimensions to a consistent level before summing, or totals double-count.
- Codes are prefixed in labels ("84-Auvergne Rhône-Alpes"). The separator
  format varies: "76 - Occitanie" in SNDS vs "76-Occitanie" in RPPS.
- Age ranges also vary: the top band is 75+ for doctors and 65+ for the
  others.
- "Hippocrate": the team's source list (`data-sources-hippoc`) points at this
  DREES series. **Assumed** to be what the team means by Hippocrate.

## Update 2026-11-13 (2): ameli private-practice demography

- **Source:** data.ameli.fr, `demographie-effectifs-et-les-densites`
  ("Professionnels de santé libéraux : effectif et densité par tranche d'âge,
  sexe et territoire"). Modified 2026-10-28. Export filtered to
  `effectif > 0`: 1,523,922 rows, 6.1 MB parquet, in
  `data/raw/ameli/` (user-approved).
- **Loader:** `uv run python -m sante.ameli` →
  `data/processed/stock_ameli.parquet`. 380,979 detailed rows, 2010–2025,
  101 départements, **23 specialties**, dentists split into omnipraticien vs
  ODF. GPs, orthophonistes, orthoptistes and podologues are excluded.
  **No pharmaciens.**
- **Agreement with DREES private practice (libéral + mixte), measured:**

  | Profession | ameli / DREES |
  |---|---|
  | Dentistes | 1.00–1.03 |
  | Infirmiers | 1.00–1.01 |
  | Kinés | 0.93–0.94 |
  | Specialists | 0.88–0.90 |
  | Sages-femmes | 0.87–0.92 |

  ameli counts professionals billing Assurance Maladie, which is narrower
  than RPPS libéral + mixte (**assumed** cause, not checked).
- **What it adds:**
  - private-practice nurses to **2025** (DREES stops at 2023);
  - 23 specialties;
  - 16 years, so a second backtest start year becomes possible;
  - ameli's own density, as a cross-check.
