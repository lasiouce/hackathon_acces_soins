---
type: analysis
date: 2026-11-13
author: Claude
question: Can the salaried-nurse stock (BTS marginals only) be put on the same dép × age × sex grid as the other professions?
headline: 508,790 salaried nurses in 2023 on dép × 10 age bands × sex; raked cells hit both marginals to 1e-7 %, ≤ 2 persons off the raw published cells
status: done
professions: [infirmiers]
hypothesis: H1
sources: [DREES infirmières salariées BTS 2013-2023 (2026-07-02), DREES infirmières libérales SNDS 2012-2023]
tags: [data, nurses, ipf]
---

# Salaried nurses: dép × age × sex by raking

> **Headline:** 508,790 salaried nurses in France (hors Mayotte) in 2023, now on dép × 10 age bands × sex for 2013–2023. The raked cells reproduce the age and sex marginals to 1e-7 %. Against the raw published cells they are at most 0.30 %, or 2 persons, off, because the source's own marginals disagree by that much.

## Question
The stock-flow model (H1) needs dép × age × sex for every profession. For salaried nurses, the largest group, the DREES/BTS file only gives marginals.

## Result
| Check | Value |
|---|---|
| Rows | 22,000 = 100 dép × 11 years × 10 ages × 2 sexes |
| Max error vs harmonised marginals | 1.0e-7 % (tolerance 0.1 %) ✅ |
| Max error vs raw published marginal cells | 0.30 % (≤ 2 persons, small départements such as 23, 2B, 90) |
| Source inconsistency, Σ age vs Σ sex | ≤ 0.21 % (±2 persons) |
| Σ dép vs national file total | ≤ 6 persons per year (2023: 508,790 = 508,790) |
| Distance to the naive independence product | mean 3.3 % of persons reallocated (weighted), max 11.8 % (Aisne, 2015) |
| Distance to the national-salaried-seed variant | mean 3.2 %, max 12.1 % |
| National backtest: liberal seed vs true national sex × age | 0.5–1.2 % of persons misallocated, vs 0.5–0.9 % for independence |

What the file holds was checked first. Every département row details at most one of sector, specialty, sex or age, and the others are "Ensemble". Only France entière crosses sex × age (20 rows), and that cross is the national backtest.

## How
- **Data:** `data/raw/drees/infirmieres_salariees_bts_2013_2023.xlsx` (DREES / Insee BTS, published 2025-03-25, updated 2026-07-02). Seed: `infirmieres_liberales_snds_2012_2023.xlsx` (dép × sex × age, missing rows read as 0).
- **Method:** [`sante/nurses.py`](../../../sante/nurses.py). Both marginals are scaled to the file's dép total. The 10 × 2 table is then fitted by IPF, seeded with the liberal nurses' age × sex in the same dép and year. A 1e-3 blend of the national salaried joint keeps the empty seed cells reachable. Output: `data/processed/stock_nurses_salaried.parquet`, with `mode3='salarie'`.
- **Run:** `uv run python -m sante.nurses` (≈ 3 s; it asserts the 0.1 % check).

## ⚑ What could make it wrong
- **The seed adds nothing measurable nationally.** In the national backtest the liberal seed does no better than independence: it is worse in 2013–2017 and slightly better in 2019 and 2022–2023. Its dép-level sex × age pattern is not validated. The interaction is weak anyway: the true national joint is only 0.5–0.9 % from independence. The national-salaried seed differs from the delivered result by 3.2 % on average.
- **Sector is not allocated.** It is not crossed with age or sex, so `mode3` is `'salarie'`, not split into `salarie_hosp` / `autre_salarie`.
- **There is a series break in 2022.** DREES flags BTS 2022–2023 as not back-cast, so 2021→2022 flows are not comparable.
- **Ages before and after 2021 are measured differently.** Up to 2020 age is taken directly from the BTS. From 2021 it is computed from the birth year.

## → What it changes
- The H1 stock can now include salaried nurses. Downstream, concatenate them with `stock.parquet` (profession `infirmiers-salaries`). Doing that is the loader owner's call: `sante/load.py` was not touched.
- Salaried and liberal nurses carry different `mode3` labels (`salarie` vs `liberal_mixte`). Levers keyed on `salarie_hosp` will not see nurses until sector is allocated.

## ? Next
| Item | Cost |
|---|---|
| Switch the default seed to the national salaried joint, given the backtest | 5 min |
| Allocate sector (hospital vs other) with a 3-way rake, sector ⟂ age·sex as the assumption | 20 min |
| Bridge the 2021→2022 series break before fitting flows | 30 min |
