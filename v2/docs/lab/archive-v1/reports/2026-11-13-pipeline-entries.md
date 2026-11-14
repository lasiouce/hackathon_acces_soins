---
type: analysis
date: 2026-11-13
author: Claude
question: Does driving yearly entries by the student cohorts already in training remove the stock-flow model's national under-prediction?
headline: "Partly: specialists −6.5 % → −4.1 % and pharmacists −4.2 % → −3.3 % national error at 5 y; dentists no better. The remaining gap sits in two places: entries at 25–39 and professionals still working past 65"
status: done
professions: [specialistes, dentistes, pharmaciens, kines]
hypothesis: H1
sources: [team DREES enrolment files 990_drees_mmop2 (2020–2025), DREES RPPS 2012–2026]
tags: [model, pipeline, backtest]
---

# Pipeline entries: student cohorts drive yearly entries

> **Headline:** partly. National error at 5 years (origin 2021 → 2026):
> - specialists **−6.5 % → −4.1 %**;
> - pharmacists **−4.2 % → −3.3 %**;
> - dentists no better (−7.1 → −7.2 %).
>
> The rest of the gap is **young entrants (25–39) and professionals working
> past 65**, both rising over time (measured).

## Question
Can the flat-entries bias (−10 to −12 % at 8 years for specialists and
dentists, K1 correction) be fixed by taking entries from the student
cohorts already in training? These are known, not guessed.

## Result
Origin 2021, fit 2015–2021, target 2026 (h = 5), départements with ≥ 30
professionals. "Pipeline" is new; "recent" is the control: the same
recent-entry level, without cohort scaling.

**National error (%):**

| Profession | Trend | H1 local (flat entries) | H1 local, recent entries | **H1 local, pipeline entries** |
|---|---|---|---|---|
| Spécialistes | −5.32 | −6.49 | −5.27 | **−4.05** |
| Pharmaciens | −3.61 | −4.21 | −4.81 | **−3.28** |
| Dentistes | −8.63 | −7.11 | **−5.35** | −7.15 |
| Kinés (no pipeline data) | −4.85 | −2.15 | **−0.47** | −0.47 |

**Per-département MAPE (%):**

| Profession | Trend | H1 local (flat) | H1 local, recent | H1 local, pipeline |
|---|---|---|---|---|
| Spécialistes | **8.48** | 9.13 | 9.91 | 9.58 |
| Pharmaciens | 5.73 | **5.37** | 7.07 | 6.79 |
| Dentistes | 10.02 | **7.58** | 9.00 | 9.50 |
| Kinés | 10.60 | 7.06 | **6.91** | 6.91 |

**Where the remaining gap is.** Actual − predicted in 2026, persons, H1
local with recent entries:

| Profession | Total | Young (25–39) | Past 65 |
|---|---|---|---|
| Spécialistes | +7,442 | **+5,217 at 35–39** | **+3,901** |
| Dentistes | +2,580 | **+2,773** | +622 |
| Pharmaciens | +3,626 | **+2,437** | **+1,527** |

## How
- **Data.** Team DREES enrolment files, `990_drees_mmop2_f.xlsx` (Feuil1,
  2020–2024) and `990_drees_mmop2_2526.xlsx` (2025). Students by diploma ×
  year of study.
- **Cohort index** (`sante/pipeline.py`). A cohort in year of study k in
  year y enters the workforce in y + (last + 1 − k). Each year-of-study
  series is normalised by its own mean, then averaged.
  - Specialists use DES year 4 only: years 1–3 include GPs, and years 5–6
    grow with the 2017 DES-length reform, not with cohort size.
  - Dentists and pharmacists use DE years 2–6.
- **Estimator** (`sante/estimators.py`, `StockFlowLocalPipeline`).
  Entries = the last-2-years level × cohort(year) / cohort(reference).
  Beyond the last known cohort, the ratio is held. The model change is
  `project(..., inflow_scale=)` and `fit_rates(..., inflow_recent=)`.
- **Bench.** `uv run python -m sante.backtest`, now with origin-2021 rows.

## ⚑ What could make it wrong
- **One origin, one horizon (5 years).** The student data starts in 2020,
  so no 8-year pipeline test is possible.
- **Dentists:** domestic cohorts shrank slightly (index 0.92), yet the stock
  grew. The likely cause is **dentists trained abroad** (EU diplomas), who
  are not in the domestic pipeline. **Assumed**, not checked.
- **The 2025 enrolment sheet jumps** (e.g. dentistry year 2: 2,083 vs
  ~1,500). It drives entries for 2030+ only, and not the backtest. It is
  unexplained: a reform, a scope change, or a different file.
- **Per-département error is not better** with pipeline entries. The index
  is national, so it can't place entrants locally. Regional enrolments by
  ARS exist and are not used yet.
- **The specialist index is a single year of study**, so it is noisier.

## → What it changes
- **Registered two estimators**, both on the bench and in the app via
  `ESTIMATORS`:
  - *pipeline entries*: has a real mechanism, and is the natural carrier
    for the quota lever;
  - *recent entries*: the control.
- **Default stays H1 local rates (flat entries)**: best per département on
  average.
- **The national bias has two named causes, each a rate that is not
  stationary:**
  1. entries rising faster than domestic cohorts (foreign diplomas, the
     numerus apertus increase);
  2. **later exits**: people working past 65, which matches the lever
     "cumul emploi-retraite".

  That points to the next estimator, retention at 60+ trending (the F1
  retention loop, or a simple trend on 60+ rates). Not entries again.

## ? Next
| Item | Cost |
|---|---|
| 60+ retention trend estimator (later retirement), on the bench | ~1 h |
| Foreign-diploma inflow for dentists (DREES: place of diploma) | ~1 h |
| Regional pipeline: allocate entries by ARS of training (with the médecins diploma-region × practice-region matrix) | ~2 h |
| Explain the 2025 enrolment jump | ~20 min |
