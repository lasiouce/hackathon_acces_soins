---
type: analysis
date: 2026-11-13
author: Claude
question: Can we load the liberal stock by commune × age band from CartoSanté's TJS API and trust the implicit row order?
headline: 1,240,401 rows (nurses, kinés, dentists × 34,847 communes × age band, 2004–2025); communes sum to département exactly in 99.2 % of dép-years, the only misses are dép 13 (Marseille dropped); midwives excluded (row order unreadable)
status: draft
professions: [infirmiers, kines, dentistes]
hypothesis: data loader for the ARS commune view
sources: [CartoSanté OGC TJS (cartosante.atlasante.fr/GC_tjs.php), datasets infi/kine/dent_popage, producer FNPS/SNDS, extracted 2026-11-13]
tags: [data, loader, commune, cartosante]
---

# CartoSanté commune loader

> **Headline:** `data/processed/stock_commune.parquet`: 1,240,401 rows,
> 2.4 MB. It covers liberal nurses (2004–2025), kinés (2005–2025) and dentists
> (2006–2025), for 34,847 communes and 5 age bands. Communes add up to the
> département pull exactly (|gap| ≤ 1) in every département-year except
> dép 13. **Midwives are excluded.**

## Question
Does CartoSanté's TJS API give a usable commune-level stock for the ARS view
([decisions.md](../decisions.md), "Primary source per profession × grain")?
Its rows carry no year or age label, so does the inferred order hold?

## Result
| Check | Nurses | Kinés | Dentists |
|---|---|---|---|
| Communes kept / dropped (partial series) | 34,847 / 30 | 34,847 / 30 | 34,847 / 30 |
| Commune-year cells where the age bands ≠ the total | 92 of 766,634 (max 19) | max 47 | max 14 |
| Département-years where Σ communes ≠ the dép pull (\|gap\| > 1) | 16 of 2,200, all dép 13 | 16 of 2,100, all dép 13 | 16 of 2,000, all dép 13 |
| France 2025 (dép pull) | 104,074 | 87,076 | 38,938 |

Example: Clermont-Ferrand (63113), 2025: 177 nurses, 179 kinés, 112 dentists.

**Dropped:**
- **Marseille (13055)** has 16 of 22 years, which can't be placed by position.
  That is the whole dép-13 gap: 2,695 nurses, 1,886 kinés and 774 dentists in
  2025.
- 29 other communes, mostly created or merged (14666, 15031, …). Codes are in
  the log.
- Mayotte and the overseas collectivities (976, 977, 978) at département level.

**Midwives (`sf_popage`)** have 7 age bands. Their rows don't follow the
year × age grid: in Paris, no reading makes the bands add up to the total, and
both orderings give a jagged national series (1,445 → 2,338) against ameli's
3,842 → 8,490. **Excluded.**

## How
- **Data:** CartoSanté TJS `GetData`, frameworks `com2026` and `dep`,
  attribute `eft` (liberal professionals active at 31/12, FNPS/SNDS),
  extracted 2026-11-13. Raw XML (~420 MB) is cached in `data/raw/cartosante/`
  (gitignored).
- **Method:** [sante/cartosante.py](../../../sante/cartosante.py). Year and
  band come from row position, with years ascending × bands in DescribeData
  order. Age bounds are parsed from the band titles. Two checks:
  - the bands add up to the total in each cell;
  - the communes add up to the separate département pull.

  Log: `artifacts/ameli_api_scout/cartosante_loader.log`.
  Run: `uv run python -m sante.cartosante`; it takes ~2 min machine time on
  first fetch, seconds from cache.

## ⚑ What could make it wrong
- The order is still inferred. The checks catch a shuffle, but only because
  both pulls would have to be wrong in the same way to pass. The midwife case
  shows the order can break per dataset.
- 92 cells where the bands ≠ the total (max 47): **assumed** to be
  CartoSanté's masking or rounding.
- There is no sex split. Commune counts are small, so the ±1/√N noise applies.
- CartoSanté reports about 2–3 % more than ameli (kinés). Don't splice the two.

## → What it changes
- ARS commune view: the current state at commune level is ready for 3 of 6
  professions. Missing: Marseille, midwives, specialists (`demo_ps`, not
  loaded yet) and pharmacists (RPPS only).
- The share-out rule (dép projection → communes) can use these shares
  directly.

## ? Next
| Item | Cost |
|---|---|
| Marseille: pull the `arm2026` framework (arrondissements 13201–13216) and sum them | ~20 min Claude + ~1.5 min machine |
| Midwives at commune: try `sf_popage` `tx_sf_age` / `GC_indic`, or use the RPPS directory | ~30 min |
| Load `demo_ps` (specialists by specialty × commune, 2020–2025), with the same checks | ~45 min |
