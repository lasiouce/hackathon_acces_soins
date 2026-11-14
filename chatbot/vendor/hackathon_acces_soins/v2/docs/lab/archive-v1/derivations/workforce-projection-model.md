---
type: derivation
date: 2026-11-13
author: Claude
status: done
headline: stock-flow (H1) vs persistence (H0); quotas cannot move 2035 specialist count
professions: [all]
tags: [model, H1]
---

# What form should the MMOPKSI workforce projection model take?

**Derived:** 2026-11-13   **Time spent:** ~20 min (Claude time), one sitting, before any literature or data was read
**Status:** 2 promoted (H0, H1) / 1 parked (A2) / 1 killed (A3)

> Pre-literature derivation (anti-anchoring). DREES almost certainly has its
> own projection models for these professions, and an access indicator
> (APL). Nothing here is novel until `explore-and-report` has found and cited
> them.

## Problem (objective · constraint · free variables)

- **Objective.** Decision usefulness: a lever changes, and the effect on
  supply/need by profession × territory × year shows up with a band. The
  second part is **backtest MAPE** on headcount by profession × département
  at a 5–10 yr horizon (profile).
- **Binding constraint.** **480 person-hours**, or 48 h wall clock for 10
  people (sourced: user). The < 2 s recompute does **not** bind (derived
  below).
- **Free variables.** Model form · territorial grain · horizon · the lever
  set and each lever's mechanism · supply unit (headcount or FTE) · the need
  model.
- **Givens that are actually choices.** The demo horizon, e.g. 2035 (the
  team's choice). Grain (open in the ledger). Whether the hackathon
  ("Mistralverse") requires a Mistral model (unknown, organisers).

## Structure

**The core is an accounting identity, so it is *known*, not learned.**
For profession *p*, territory *d*, age *a*, sex *s* and year *t*:

```
N[p,d,a+1,s,t+1] = N[p,d,a,s,t] · (1 − x[p,a,s])        exits: retirement, attrition
                 + E[p,t] · π[p,d,t] · g[p,a,s]            entries: national flow × territorial share × age profile
                 + M[p,d,a,s,t]                            net inter-département moves + foreign diplomas
E[p,t] = Q[p, t − L_p]                                     entries = training quota L_p years earlier
supply FTE[p,d,t] = Σ_a,s N · α[p,a,s]                    α = activity rate
need[p,d,t] = Σ_a pop[d,a,t] · u[p,a] · (1 − Σ_q τ[p→q]) + Σ_q τ[q→p] · ρ[q→p] · need_q
ratio[p,d,t] = FTE / need                                  the access output
```

- **Symmetries.**
  - *Conservation* (Σ_d N = national stock, and no one appears from nowhere)
    is a **hard constraint**. It is enforced structurally by the stock-flow
    form for free; any model that violates it loses credibility in front of
    a policy jury.
  - *Permutation across professions*: one code path, six parameter sets.
    This is a cost saving, not just a symmetry.
  - *Time-shift invariance of the rates* x, π, u, α is an **assumption**
    (stationarity). The backtest K1 is exactly the test of it.
- **Timescales.**

  | Process | Timescale |
  |---|---|
  | Training lag L_p (assumed, to verify) | nurses ~3 y · kiné ~5 y · midwife ~5 y · pharma ~6 y · dentist ~6 y · specialist ~9–12 y |
  | Career length C | ~35–40 y (assumed) |
  | Installation / move decisions | ~1 y |
  | Task shifting (e.g. pharmacists vaccinating) | acts on need in < 1 y |

  The separation splits levers into three classes:
  - *pipeline* levers (quotas), which act only after L_p;
  - *stock* levers (retention, retirement age, foreign diplomas,
    installation rules), which act immediately;
  - *demand* levers (task shifting, prevention, telehealth), which also act
    immediately.
- **Known vs learned.**
  - *Known*: ageing, the identity, quotas already set, students already
    enrolled, INSEE population projections (exogenous).
  - *Estimated from open data*: x, π, α, u.
  - *Not estimable in 48 h*: policy effect sizes such as τ, ρ, or the
    elasticity of installation to incentives. These must be **parameters with
    a cited source or an explicit "assumed" tag**, never fitted.
- **Where the cost is.**
  - *Compute is negligible* (derived): 6 prof × 101 dép × ~45 ages × 2 sexes
    ≈ 5.5·10⁴ cells, × 15 yr ≈ 10⁶ multiply-adds, which is milliseconds even
    in browser JS. So the full model can be recomputed live on every slider
    move, and a precomputed scenario grid is unnecessary.
  - *The person-hours go to data*: ingesting, reshaping and harmonising
    département codes, profession labels and liberal/salaried status. A
    second sink is the UI. The model itself is ~1 file.

## Limiting cases

| Limit | What wins | Implication |
|---|---|---|
| horizon h → 0 | persistence N(t+h)=N(t) | A0 is unbeatable at short horizons. Any model must reduce to it |
| h → ∞ (≫ C) | the initial pyramid is forgotten. **N\* = Q · C** (Little's law, derived) | quotas set the long-run level. The long-run answer is analytic, no simulation needed |
| h < L_p (decision window) | **the supply of new graduates is already fixed**: ∂N(t+h)/∂Q = 0 | for specialists, 2026 → 2035 is h = 9 < L ≈ 10: **no quota lever can move the 2035 specialist count** (derived; see the note on internship posts below) |
| L_p < h ≪ C | a fractional quota change δ moves the stock by ≈ δ·(h − L_p)/C | nurses at 2035, with δ = +10 %, C = 35 assumed: ≈ 0.1·6/35 ≈ **+1.7 %** of stock. Quotas are a weak lever at decision horizons (derived) |
| grain → commune | Poisson noise, relative error ≈ 1/√N. N = 5 gives ~45 % | do not project at fine grain. Project at département (or coarser for rare specialties) and *display* access finer |
| grain → national | no territorial signal | defeats the brief |
| mobility → 0 | territories evolve independently | lower bound |
| mobility → ∞ | distribution relaxes to the attractiveness equilibrium | upper bound. Reality is near "incumbents stay, entrants choose", so π for entrants is the mobility channel |
| number of levers → ∞ | unvalidated, unusable demo | **exhaustiveness comes from the flow taxonomy, not enumeration**: every policy is a perturbation of one term (x, E/Q, π, M, α, u, τ). Seven slots cover the space |

Note on internship posts: the regional allocation of internship posts is
fixed ~4–6 years before installation. Specialists tend to settle near where
they trained (intuition). So this is the one *pipeline* lever with a lag
short enough to matter by 2035, and it acts through π, not through the
national stock.

## Isomorphism

**Cohort-component population projection** (the INSEE method):

| This | That | Label |
|---|---|---|
| entries from training | births | claim (same equation) |
| exit hazard x(a) | mortality q(a) | claim |
| entrant installation π | internal migration | intuition |
| quota Q | fertility | intuition |
| ratio FTE / need | dependency ratio | intuition |

**Where it breaks:**
- Entries are *policy-set* and arrive at age ~25–30, not 0.
- Exits are *behavioural* and respond to policy (retirement age, working
  while drawing a pension). Mortality does not.
- Activity rate α has no demographic analogue.
- The demand side (need) has no analogue at all.

**Pipeline inventory with lead time** (supply chains):

| This | That | Label |
|---|---|---|
| quota decision | purchase order | intuition |
| training lag L | lead time | claim |
| oscillating shortage and surplus | bullwhip effect | intuition (France cut quotas in the 1990s and has shortages now) |

**Where it breaks:** there is no "order cancellation"; students already
enrolled graduate. Inventory also does not choose where to live.

## Ansätze

**A0: persistence or linear trend per profession × département.**
- *Exploits*: nothing.
- *Limits*: right at h → 0, wrong at h → ∞ (a trend extrapolates without
  bound) and wrong at h < L (it ignores the known retirement wave).
- *Cost*: ~2 person-hours once the data is loaded. No levers.

**A1: cohort-component stock-flow (the equations above).**
- *Rates*: constant, estimated from the last ~3–5 years of open data.
- *Entrants*: allocated by historical shares π. Incumbents static apart
  from exits.
- *Need*: INSEE population × age-specific use rate u.
- *Levers*: one multiplier per flow slot (7 slots), each tagged
  source/assumed.
- *Exploits*: conservation, the permutation over professions, known
  ageing, the separation of timescales.
- *Limits*: right at all of them (it reduces to persistence at h → 0 and
  to Q·C at h → ∞, and it is locked at h < L).
- *Cost*: ~40–80 person-hours (assumed), mostly data. Compute ≈ 1 ms
  (derived).

**A2: A1 + behavioural installation.**
- *Form*: π[p,d] = softmax(β · features_d), with features such as current
  density, population growth, urban/rural, regulated zone, internship-post
  share.
- *Exploits*: it gives installation-regulation and incentive levers a
  mechanism instead of a bare multiplier.
- *Limits*: same as A1.
- *Cost*: +30–60 person-hours (assumed). β is weakly identified from a few
  years of data.

**A3: black-box forecaster or agent-based simulation.** The first variant
is an ML time-series model on headcount; the second simulates ~10⁶
professionals (order of magnitude, assumed) as individual agents.
- *ML*: violates conservation, has no lever mechanism, and gets
  h → ∞ wrong.
- *ABM*: the same aggregate as A1 at ~10× the calibration cost, with no
  extra limit right.

**Interface note, not an ansatz.**
- If Mistral use is expected, the LLM belongs in the *scenario compiler*.
  It turns "what if pharmacists vaccinate?" into a lever vector plus a
  cited mechanism, and the user confirms it before it applies.
- It never belongs in the forecaster: the forecaster's core is an exact
  identity and must not be learned.

## Kill tests

| Test | Discriminates | Result that kills | Price |
|---|---|---|---|
| **K1 backtest.** Fit on data up to year T₀ (≥ 8 yr back, if open series exist). Project to the latest year; MAPE per profession × département | A0 vs A1 (vs A2) | A1 MAPE not below A0 at the 8-yr horizon → A1 killed *as a forecaster* (it may survive as a scenario tool, but then it can't claim accuracy) | ~6–10 person-hours, mostly data, assumed. Blocked on the data survey |
| **K2 pipeline lock.** In A1, share of the 2035 stock variance explained by (current pyramid + enrolled students) vs quota levers | the "quotas matter by 2035" assumption | quota sensitivity > ~5 % of stock for specialists at 2035 → the h < L limit or the L_p values are wrong | ~1 h once A1 runs |
| **K3 installation.** Hold out the last 2–3 years of entrant locations; constant π vs logit π | A1 vs A2 | logit π not better on log-loss → A2 killed for the hackathon | ~4–6 person-hours |
| **K4 small counts.** Distribution of N per profession × département | grain choice | median N < ~30 for a profession (e.g. a specialty or midwives in small départements) → project that one at region level | ~30 min |
| **K5 need stationarity.** Drift in the age-specific use rate u over the available years | constant-u need model | drift > ~2 %/yr (assumed threshold) → need a trend term in u | ~2 h |

## Verdicts

- **A0: promoted as H0, the baseline.** It is required, and every claim is
  stated against it.
- **A1: promoted as H1.** It gets every limit right and conservation for
  free. Its cost sits in data, which any approach pays anyway.
- **A2: parked.** Un-park it if K3 shows constant π fails, or if the jury
  demo needs an installation-regulation lever with a real mechanism.
- **A3: killed.**
  - *ML forecaster*: violates conservation and the h → ∞ limit, and has no
    lever mechanism.
  - *ABM*: same aggregate as A1 at ~10× the calibration cost, with no
    limit gained.
  - Don't re-propose either without new data that A1 can't use.

## Hand-offs

- **explore-and-report**, in this order:
  1. Open data per profession: stock by age × sex × département × mode of
     practice, history depth for K1, quotas, enrolled students, use rates.
  2. DREES's own projection models and the APL indicator. These are the
     likely incumbent, to cite and to beat or reuse.
  3. INSEE département population projections.
- **record-decision (open).** Horizon and grain. Headcount vs FTE as the
  supply unit. Whether Mistral use is required.
- **Ledger.** K1–K5 with the prices above.
- **Implication for the demo.** For the Clermont-2035 example, lead with
  stock and demand levers (retention, installation, task shifting); quotas
  are the long-run lever. The demo should show the long-run lever
  separately as N\* = Q·C.
