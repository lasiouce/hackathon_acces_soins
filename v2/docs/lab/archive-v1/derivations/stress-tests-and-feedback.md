---
type: derivation
date: 2026-11-13
author: Claude
status: done
headline: "Shocks and levers are the same object (a time-profiled perturbation of one flow term). Feedback on installation can redistribute at most ≈ 1/C ≈ 3 % of stock per year, so a 20 % density gap needs ≥ ~7 years even with perfect incentives (derived)"
professions: [all]
hypothesis: H2, H3
tags: [model, crisis, feedback, engine]
---

# How should crisis shocks and endogenous feedback enter the estimator library?

**Derived:** 2026-11-13   **Time spent:** ~20 min (Claude time), one sitting, before any literature
**Status:** 3 promoted (S1 → H2, F1 → H3, S0 as baseline) / 1 parked (F2) / 1 killed (A-struct)

## Problem (objective · constraint · free variables)

- **Objective.** Decision usefulness: a user applies a shock or a feedback
  setting and reads **resilience indicators** per territory. The
  indicators must be computable for **any estimator** in the library (the
  engine is algorithm-agnostic).
  1. *Depth* `D` (%): max over years of (1 − ratio_shock / ratio_reference).
  2. *Recovery time* `T_r` (years) until the trajectory is back within
     2 % of the reference.
  3. *Lost professional-years* `A` = Σ_t max(0, N_ref − N_shock).
  4. Number of territories below a threshold.
- **Binding constraint.** Remaining person-hours (from the 480 budget), and
  recompute < 2 s. Compute will not bind: H1 runs in ~1 ms (derived
  earlier), and feedback adds one coupling per step.
- **Free variables.** How a shock is represented. The functional form and
  gain of each feedback loop. **The engine interface**: this is a given that
  is really a choice, being designed by another session.

## Structure

- **Shocks and levers are the same object (claim).**
  - A **lever** is a policy-chosen perturbation of one flow term (x, E/Q,
    π, M, α, u, τ), usually persistent. A **shock** is an exogenous
    perturbation of one of the *same* terms, usually transient.
  - So one `Perturbation(slot, selector, profile m(t))` covers both:
    - `selector` = profession × territory × age;
    - `profile` = a multiplier per year: a step (lever), a pulse (shock) or
      a ramp.
  - Examples:
    - epidemic demand surge = pulse on u;
    - early-retirement wave = pulse on x for age 55+;
    - burnout exits = pulse on x for all ages;
    - quota cut = step on Q, felt after L_p.
- **Estimator-agnostic means capabilities, not uniformity.**
  - Black-box estimators (persistence, trend) have no slots. Only two
    perturbations apply to *every* estimator:
    - a multiplier on the **output** N;
    - a multiplier on **need** u, which sits outside the supply estimator.
  - Slot perturbations need a structural estimator. → The engine needs
    each estimator to declare `supports = {slots}`. For an unsupported
    slot, fall back to an output multiplier and **say so in the UI**.
- **Indicators need trajectories, not one target year.** The current
  `predict(target)` gives one year; `T_r` and `A` need every year. →
  Interface change: `predict(years) → N[profession, territory, year]`
  (decision-in-waiting).
- **Timescales.**

  | Process | Timescale |
  |---|---|
  | Demand surge (epidemic) | months – 2 y |
  | Burnout exits | 1–3 y |
  | Retirement wave | 1–5 y |
  | Quota cut | acts after L_p = 3–12 y, lasts ~C = 35 y (assumed) |
  | Feedback: activity / hours | months |
  | Feedback: retirement timing | ~1 y |
  | Feedback: where new graduates settle | 1–3 y |

  The annual step is coarse for demand surges under a year. That's
  acceptable for a demo; flag it in the UI.
- **Known vs learned.**
  - *Known*: shock profiles are scenario *inputs*. They are assumed or
    sourced, e.g. from COVID-era DREES/ameli figures; never fitted.
  - *Mostly not estimable from 15 yearly points*: feedback gains. They are
    levers with ranges.
  - *Partly estimable*: one gain, the sign and rough size of
    installation-vs-density, from ameli 2010–2025 (K3 below).

## Limiting cases

| Limit | What wins | Implication |
|---|---|---|
| Feedback gain g → 0 | frozen H1 | F1 must reduce *exactly* to H1 (test) |
| **Installation gain g_π → ∞** | new graduates all go to the most under-served territories. **Incumbents don't move**, so the reallocation per year is bounded by the entrant flow, E/N ≈ 1/C ≈ **3 %/yr** (derived, C = 35 y assumed) | **A 20 % density gap needs ≥ ~7 years to close even with perfect incentives** (derived). This is a strong, honest demo message and a hard sanity bound for F1 |
| Retention gain → ∞ (delaying exits at 60+) | stock can't exceed today's 60+ share kept a few more years | a faster but bounded lever: the 60+ share of stock caps it (to be measured, e.g. from the age bands) |
| Number of territories → 1 | installation feedback has nowhere to move people | **Installation feedback is zero-sum**: the national total must equal H1's exactly (conservation test) |
| Shock size → 0 | linear response, indicators ∝ size | the impulse-response limit. S0 is exact here |
| Shock size → large | floors at 0, thresholds, nonlinear | S0 (linear output multiplier) breaks. S1 needed |
| Shock duration → 0 (demand pulse) | no lasting supply effect | **unless** burnout feedback converts demand into exits. That's the one coupling worth showing in a crisis |
| Shock duration → ∞ | new equilibrium, N\* = Q·C | the long-run lever result from the first derivation |
| **Quota feedback with delay τ = L_p** | delayed negative feedback, x' = −g·x(t − τ), oscillates when **g·τ > π/2** (derived, first-order delay equation) | for specialists (τ ≈ 10 y), any reaction gain above ~0.16/yr makes quotas swing boom-bust: the **cobweb** cycle. This explains the 1990s cut → today's shortage as *policy reacting with a lag*, not bad luck |

## Isomorphism

| This | That | Label |
|---|---|---|
| Shock scenario × workforce → density trajectory → threshold | **Bank stress test**: adverse scenario × balance sheet → capital-ratio path → hurdle rate | claim (same pipeline, and a jury knows the vocabulary) |
| Quota policy reacting to observed shortage after L_p years | **Delayed negative feedback** (control theory) / **cobweb model** (economics) | claim (the stability condition g·τ < π/2) |
| Installation responding to density gaps | **Spatial labour-market matching**: workers flow toward the vacancies | intuition |
| Shocks = levers on the same 7 slots | the lever registry (`docs/lab/levers.md`) | claim: one data structure for both |

**Where it breaks:**
- Banks have a regulator-set hurdle; **we have no agreed threshold**
  (decision-in-waiting, and it must be worded neutrally).
- A bank's balance sheet reacts mechanically; ours reacts through
  behaviour with unknown gains.
- Quota policy is discrete (decided yearly, by decree) and capped by
  training capacity, so oscillation is damped in reality.
- Matching models assume mobile incumbents; ours mostly aren't.

## Ansätze

- **S0, output-multiplier shocks (baseline).**
  - *Form*: N_shock(t) = N_ref(t) · m(t), and/or need × m(t).
  - *Exploits*: works on every estimator.
  - *Limits*: exact for small shocks; misses recovery dynamics and age
    structure.
  - *Cost*: ~30 min.
- **S1, slot-perturbation stress tests.**
  - *Form*: a `Perturbation(slot, selector, m(t))` applied inside
    structural estimators, with x, E/Q, π, α, u, τ time-varying. The
    resilience indicators D, T_r, A and #below-threshold come from the
    trajectories.
  - *Exploits*: shocks = levers; known ageing.
  - *Limits*: correct at both shock-size limits and both duration limits.
  - *Cost*: ~2 h. It needs `predict(years)`.
- **F1, feedback stock-flow** (system dynamics; a new estimator class).
  - *Installation*: π_d(t) ∝ π_d⁰ · exp(g_π · gap_d(t−1)), renormalised to
    sum to 1 (zero-sum).
  - *Retention*: x_a,d(t) = x_a⁰ · (1 − g_x · gap_d(t−1)) for ages 60+.
  - *Activity*: α_d(t) = α⁰ · (1 + g_α · gap_d(t−1)), capped.
  - gap = (national density − local density) / national density.
  - All gains default to 0, which reproduces H1, and are exposed as levers.
  - *Exploits*: conservation; the entrant bound.
  - *Limits*: g → 0 and g → ∞ (bounded by E/N).
  - *Cost*: ~2–3 h.
- **F2, quota feedback loop.**
  - *Form*: Q(t) = Q⁰ · (1 + g_Q · gap_nat(t)), felt after L_p.
  - *Exploits*: the delay.
  - *Limits*: reproduces the oscillation limit.
  - *Cost*: ~1 h. Mainly an explanatory demo of why reacting late swings.
- **A-struct, a fully estimated structural/econometric model** (all gains
  fitted jointly): see Verdicts.

## Kill tests

| Test | Kills | Result that kills | Price |
|---|---|---|---|
| **K-cons**: F1 national total vs H1, all gains > 0 | F1 implementation | any difference > 1e-6 relative | 10 min |
| **K-bound**: F1 with g_π = 10⁶; yearly gap closure vs E/N | F1 form | closure faster than the entrant flow allows | 15 min |
| **K3, empirical sign**: ameli 2010–2025, regress the growth of the under-35 bands by département on the lagged density gap | F1 as a *description* (not as a lever) | coefficient ≤ 0, or not distinguishable from 0 → default g_π = 0, and F1 is presented as a policy lever only | ~1 h |
| **K-bench**: F1 with the K3-estimated g_π vs H1, on the bench (2018 → 2026) | F1 as a better forecaster | no MAPE gain → kept as a scenario tool only (fine under "algorithms, not exact numbers") | ~30 min after K3 |
| **K-S0vsS1**: same 3 crisis scenarios through S0 and S1 | S1's extra value | all indicators within 5 % → S1 adds nothing over S0 | ~30 min after S1 |
| **K-osc**: F2 sweep of g_Q × τ | the stability claim | oscillation onset far from g·τ ≈ π/2 → the derivation is wrong | 20 min |

## Verdicts

- **S0: promoted as the baseline** for crisis scenarios. It is the
  universal fallback for any estimator.
- **S1: promoted as H2.** Stress tests as slot perturbations, measured by
  D / T_r / A / #below-threshold, give different and more correct answers
  than S0 for large or long shocks. Falsified by K-S0vsS1.
- **F1: promoted as H3.** A feedback stock-flow with zero-sum installation
  feedback. It reduces to H1 at g = 0 and is bounded by E/N. Whether it
  *describes* reality is decided by K3; it is a valid *lever* regardless.
- **F2: parked.** An explanatory demo of the cobweb (boom-bust) cycle. Un-park
  it if the pitch needs the "why we have shortages today" story, at ~1 h.
- **A-struct: killed.** 15 yearly points can't identify several behavioural
  gains jointly, and its h → ∞ behaviour is no better than F1 with gains as
  levers. Don't re-propose it without micro-data on individual moves.

## Hand-offs

- **To the engine session** (decisions-in-waiting, `decisions.md` Open):
  1. `predict(years)`, i.e. trajectories, not one target year;
  2. each estimator declares the slots it `supports`;
  3. one `Perturbation(slot, selector, profile)` type shared by levers and
     shocks, with an output-multiplier fallback that is flagged in the UI;
  4. resilience indicators computed by the engine, not by estimators.
- **record-decision (open):** the threshold for "#territories below
  threshold", worded neutrally (e.g. "densité inférieure à X % de la
  moyenne nationale").
- **explore-and-report:** COVID-era figures for realistic shock profiles
  (demand surge size, early retirements, nurse departures); the
  system-dynamics workforce-planning literature (incumbent check).
- **Ledger:** K-cons, K-bound, K3, K-bench, K-S0vsS1, K-osc with the prices
  above.
