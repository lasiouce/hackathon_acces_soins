---
type: exploration
date: 2026-11-13
author: Claude
status: done
headline: "DREES already projects 5 of our 6 professions (national, trend scenario). Nurses 2035 = 729 614 (DREES xlsx). None is below ex-region level and kinés have no projection since 2018. APL is commune-level but needs SNIIR-AM/DCIR activity data we don't have"
professions: [all]
tags: [incumbent, DREES, APL, backtest]
---

# Prior work: DREES projections, the APL indicator, other territorial tools

**Why:** the derivation ([workforce-projection-model](../derivations/workforce-projection-model.md)) was written before any literature was read. Nothing in it can be called novel until the incumbent is cited. Below: what exists, how it works, and which numbers we should be compared with.

**Provenance.** Every number is tagged *quoted* (read in the source text or spreadsheet this session), *derived* (computed by us from quoted numbers) or *not verified*. All documents below were downloaded and their text extracted locally; pages on `drees.solidarites-sante.gouv.fr/sources-outils-…` returned 403 to the fetcher, so those were not read.

## 1. DREES projections of health professionals

### 1.1 Médecins, chirurgiens-dentistes, sages-femmes, pharmaciens — Dossiers de la DREES n°76 (March 2021)

- **Source:** Anguis, Bergeat, Pisarik, Vergier, Chaput, *Quelle démographie récente et à venir pour les professions médicales et pharmaceutique ?*, Les Dossiers de la DREES n°76, March 2021. <https://drees.solidarites-sante.gouv.fr/sites/default/files/2021-03/DD76.pdf> (press page: <https://drees.solidarites-sante.gouv.fr/communique-de-presse/medecins-sages-femmes-chirurgiens-dentistes-et-pharmaciens-combien-de>). Read in full (74 pages, text extracted).
- **Scope and horizon:** professionals active, under 70, France entière. Projection 2021→2050, annual steps, results at 1 January. *Quoted.*
- **Data:** RPPS panel (chained vintages, 2016–2020 for rates; 2019 for médecins), SISE and ECN for médecins' studies. *Quoted.*
- **Method — a stock-flow, not one microsimulation.** *Quoted.*
  - Dentists, midwives, pharmacists: a **component model** (groups defined by age × sex × mode of practice; probabilities are applied as shares of the group). Midwives: no sex split in the rates (too few men).
  - **Médecins: the only microsimulation**, and only for 3rd cycle and active doctors. Cycles 1–2 are modelled as aggregates, with repeat/dropout rates by region and year of study.
  - **Flows per annual step** (the 6 numbered steps in the document): (1) stock of actives and "reserve" of inactives at 1 Jan; (2) per age × sex × practice-mode probabilities of *cessation*, *transition* of practice mode, *resumption* for inactives, plus inter-region move for médecins; ageing by one year; (3) inflow of **French graduates** = intake (numerus clausus/apertus) lagged by study length, minus attrition, spread over an installation delay of 0–4 years; (4) inflow of **foreign graduates**, entering at their first activity with the age/sex/practice profile of recent arrivals.
  - **No hard retirement age:** exit is an empirical age-specific cessation probability.
- **Scenarios:** one *tendanciel* scenario ("comportements et législation constants") plus variants on two levers only: intake ±20 % from the start, and foreign-graduate inflow. Variant results quoted: ±20 % intake moves midwives by ±12 % in 2050 and pharmacists by ±13 % in 2050. A médecin variant of +20 % intake shortens the trough by ~3 years. Everything else (retirement age, mobility, task-shifting) is not a lever.
- **Population side:** Insee population projections (2016 vintage), the low-fertility/low-life-expectancy/central-migration variant, because it tracked observed population best. Need is a **standardised population**: age-specific consumption weights from Assurance Maladie 2018, applied to the population. *Quoted.*
- **Territorial level:** the model carries médecins by **pre-2015 region** (CHU level), but the published results are **national**. Regional statements in the text are qualitative. *Quoted.* No département output.

| Profession | 2020/21 base | 2030 | 2040 | 2050 | Source quote |
|---|---|---|---|---|---|
| Médecins (all specialities, <70) | ≈215 000 stable since 2012 | back to 2020 level (low point 209 000 in 2024) | +18 % vs 2020 | **292 000** (+36 %) | DD76 p.46 |
| Médecins, other specialities than GP | — | — | — | +39 % vs 2021 | DD76 p.51 |
| Médecins, general practice (excluded from our scope) | 95 400 (2021) | — | — | +35 % vs 2021; low 92 300 in 2026 | DD76 p.51 |
| Médecins, standardised density | 2021 = 100 | low point −5 % in 2028; back to 2021 level 2035 | — | **+23 %** | DD76 synthèse |
| Chirurgiens-dentistes | 41 800 (2020) | 45 900 | 53 900 | 61 800 (+48 %) | DD76 p.46 |
| Pharmaciens (Ordre-registered) | 72 600 (2020) | — (low 71 000 in 2027) | 76 600 | **81 100** (+12 %) | DD76 p.46 |
| Sages-femmes | 23 000 (2020) | 26 200 | 28 600 | 29 300 | DD76 p.46 |

**No 2035 value is published for any profession in DD76.** A 2035 figure can only be interpolated (derived, linear between 2030 and 2040): dentists ≈ 49 900, sages-femmes ≈ 27 400, pharmaciens ≈ 73 800 (≈ mid-point of 71 000 trough/recovery, so weak).

**Earlier DD76 lineage (table 9 in DD76):** dentists 2017 (horizon 2040), pharmacists 2019 (2040), médecins 2017 (2040), sages-femmes 2011 (2030), **infirmiers 2018 (2040)** and **masseurs-kinésithérapeutes 2018 (2040)** — these two professions were *not* in the 2021 update. *Quoted.* DD76 says the DREES models exist "for six professions".

**2023 update of the médecins projection:** a search-engine summary reports a 2023 update with standardised density +31 % in 2050 and 309 → 372 per 100 000 (2022 → 2050). **Not verified** — I did not read a primary document for this. Treat as a lead, not a number.

### 1.2 Infirmiers — Études et Résultats n°1319 (December 2024)

- **Source:** C. Parent (DREES), *Le nombre d'infirmières augmenterait fortement d'ici à 2050, mais moins que les besoins en soins de la population vieillissante*, ER n°1319, 5 Dec 2024. <https://drees.solidarites-sante.gouv.fr/publications-communique-de-presse/241203_ER_Nombre-infirmieres>; PDF <https://drees.solidarites-sante.gouv.fr/sites/default/files/2024-12/ER1319_0.pdf>; data <https://drees.solidarites-sante.gouv.fr/sites/default/files/2024-12/ER1319.xlsx> (also on data.drees: `drees_projections_infirmieres_2024`, not opened). PDF and xlsx read.
- **Method:** **component model** (groups age × sex × practice mode: liberal, public hospital, private hospital, medico-social, other). Events: change of practice mode, cessation, resumption. Inflow from **quotas of training places × (1 − "taux de perte")**, no retirement age. Nurses *in employment* ≤ 70, France entière excl. Mayotte. Data: Insee BTS (salaried), SNDS (liberal), Insee "panel tous actifs" (salaried↔liberal transitions, ~10 000 nurses), DREES school surveys. Foreign nurses behave as new graduates. No cap on salaried posts. *Quoted.*
- **Horizon 2021→2050, national only.**
- **Headline (quoted, xlsx "Graphique Web", tendanciel):** 598 915 (2021) → 685 737 (2030) → **729 614 (2035)** → 766 871 (2040) → **821 003 (2050)**, +37 %. Standardised density per 100 000: 885.0 (2021) → 841.3 (2035) → 806.7 (2050). Simple density: 888.5 → 1 057.7 (2035). Need grows 50 % 2021–2050; 80 000 extra nurses needed in 2050 to hold coverage. 29 000 graduates/yr in the trend (quota 38 000 places, 20 % attrition) vs 32 900 needed. Liberal share 16 % → 21 % (2050).
- **Levers modelled:** training places (+14 %), attrition rate (halved), foreign nurses (table in xlsx). Variant "1a" 32 200 graduates/yr at 11 % attrition.

### 1.3 Masseurs-kinésithérapeutes

- Last DREES projection cited: **Millien 2018b, horizon 2040** (DD76 table 9). I did not find or read it, so no kiné projection number is available. **Not verified:** its title and numbers.
- The **only kiné figure found** is the stock: 111 400 in activity at 1 Jan 2026 (DREES, <https://drees.solidarites-sante.gouv.fr/communique-de-presse-jeux-de-donnees/jeux-de-donnees/260702-les-effectifs-des-professionnels-de-sant%C3%A9>, quoted by the subagent that read the page, not re-read by me).

### 1.4 Recent stocks to anchor a backtest (RPPS, DREES, 1 Jan 2026)

Same DREES page as above (published 2 Jul 2026): kinés **111 400**, pharmaciens **75 300**, chirurgiens-dentistes **48 700**, sages-femmes **26 400**, pédicures-podologues 14 600. *Quoted via subagent; the page does not say whether the scope is "<70" as in DD76.* Médecins and infirmiers are not on that page.

## 2. The APL indicator

- **What it is:** a commune-level indicator by DREES and IRDES (created 2012), "inspired by Radke & Mu 2000, Luo & Wang 2003, Luo & Qi 2009", i.e. the **floating-catchment-area family (2SFCA)**, and close to Mizrahi's "densité répartie". Supply from neighbouring communes is distance-weighted; demand is the age-standardised population; activity of each professional is bounded (min/max liberal activity). Source: DREES "APL_Lisez-moi.pdf" (read), <https://data.drees.solidarites-sante.gouv.fr/api/datasets/1.0/530_l-accessibilite-potentielle-localisee-apl/attachments/apl_lisez_moi_pdf>.
- **Professions with an APL file:** médecins généralistes, infirmiers, kinésithérapeutes, sages-femmes, chirurgiens-dentistes. **No pharmacist and no specialist APL** in the dataset's attachment list (dataset metadata, JSON API). Médecins généralistes' unit: consultations/visits per inhabitant per year; the others: FTE per 100 000. *Quoted.*
- **Vintages and files:** latest "root" files cover **2022, 2023, 2024**; older folders "Méthode initiale V0 2010/2013", "Méthode concertée V1 2015-16", "V2 2015–2022" (nurses/midwives/kiné 2016–19, 21, 22; dentists 2021–22; GPs 2015–19, 21, 22). One xlsx per profession, one row per **commune**, with the APL and the **standardised population** (to aggregate to any supra-commune level by population-weighted mean). Also an xlsx of "APL moyens par dixièmes de population". Licence Ouverte v2.0 (Etalab). Dataset: <https://data.drees.solidarites-sante.gouv.fr/explore/dataset/530_l-accessibilite-potentielle-localisee-apl/> (metadata read from its API; the xlsx files themselves not downloaded).
- **Inputs of the official computation:** **SNIIR-AM / SNDS** (Assurance Maladie activity of each liberal professional, including health-centre activity), **DCIR** age-specific care consumption for the population weights (EGB before), Insee census population by age. Distance: a travel-time matrix between communes (**Metric**, Insee) — mentioned in a search summary, **not verified in the text I read**. *Quoted for SNIIR-AM/DCIR/census.*
- **Built for the present, not for projection.** DREES's own caveat: because weights are fixed for a vintage, the APL cannot compare two vintages while accounting for the ageing of the population. It also says the more it is aggregated, the more it tends to a plain density. *Quoted.*
- **Can we reproduce it from our inputs? No, not faithfully.** RPPS gives headcount and location, not activity; the activity bounds, DCIR weights and the travel-time matrix are not in our data inventory. **Do not reproduce it; reuse it:** the published commune files are an open-data anchor (Licence Ouverte), and a simplified **age-standardised density** at département level (headcount ÷ Σ age-weights × Omphale population) is exactly what DREES does for its *standardised density* in DD76 and ER1319, and we can do that. Derived.
- **IRDES typology (May 2026):** Bonal et al., *Accessibilité des patients aux soins de premier recours en France : quelles configurations territoriales ?*, QES n°308. <https://www.irdes.fr/recherche/questions-d-economie-de-la-sante/308-accessibilite-des-patients-aux-soins-de-premier-recours-en-france.pdf>. A commune typology from 2023 data using APL for GPs, nurses, kinés and pharmacies. It states the GP APL fell over 2019–2022 and that a decline "should ease then reverse from 2030" citing the DREES projection. Read first pages only.

## 3. Other French territorial tools and reports

Searched less than the DREES material. What I verified:

| Item | What it is | Level | Horizon | Read? |
|---|---|---|---|---|
| **Insee + ARS Normandie**, Dossier Normandie n°25 (2 Jun 2026) and Analyses Normandie n°156 (27 May 2026) <https://www.insee.fr/fr/statistiques/8997728?sommaire=8997802>, <https://www.insee.fr/fr/statistiques/8995751> | Renewal needs of 22 salaried + 8 liberal professions. **Departures** by age from 2020–24 follow-up, retirement thresholds per profession; **demand** from Omphale 2022 (central/high) and SNDS use rates 2019–24 | Region, 5 départements, some bassins de vie | 2035 | yes (via subagent) |
| **ONDPS** (created 2003) | National observatory, assembles demographic knowledge | — | — | only a 2015 trade-press mention that its médecin and dentist projections "are obsolete" and that it needs finer entrant/exit flows. **No ONDPS projection tool found.** |
| **Cour des comptes**, Dec 2024, reform of health studies | Not read (PDF empty to my fetcher). Search summaries say it finds the rise in places unlinked to territorial need and wants ONDPS to plan HR. **Not verified** | — | — | no |
| **Ordre des pharmaciens**, *Projections démographiques 2050* | Search summary: 81 000 pharmacists in 2050, own model consistent with DREES. **Not verified**: page failed twice | national | 2050 | no |
| **ARS Nouvelle-Aquitaine / C@rtoSanté** | Mapping of current density and need zones, not projection | various | — | only a search snippet |

The Insee-ARS Normandie dossier is the **closest territorial incumbent** and uses the same ingredients as H1 (age-specific departure rates, Omphale 2022, use rates from SNDS). Verified figures: liberal replacement needs by 2035 in Normandy are ≈3 100 nurses, 1 400 GPs, 1 200 kinés (Insee Dossier n°25 panorama); trend installations ≈ 4 000 nurses, 1 800 GPs, 3 000 kinés would "globally compensate". It compares needs with trend installations rather than projecting a stock year by year (as read in the summary of the Analyses page, which was truncated). Normandy-only.

## Gaps I could not close

- DD76 and ER1319 give 2030/2040/2050 or yearly national totals, **never département**. Our département-level output has **no incumbent** found, and nothing here tells us DREES's own département projection error.
- Kiné projection (Millien 2018), Ordre des pharmaciens 2050, Cour des comptes 2024 and a possible 2023 médecin update are unread.
- APL's exact formula, decay function and Metric usage are in the "Méthode concertée" archives (.7z/.zip), not opened.

## What in our H1 derivation is a rediscovery

- **The whole stock-flow skeleton.** Age × sex × practice-mode cohorts; exits; entries = intake lagged by study length with an installation delay; foreign-graduate inflow; ageing step; Insee population as exogenous. DREES has used this since 2011 (Barlet & Cavillon for nurses, Cavillon for midwives) and it is the structure of DD76 and ER1319. This is not novel and the deck must not say so.
- **The pipeline lag result** (intake lever acts only after the study length). DD76 states it in the first paragraph: "cinq à dix ans (sages-femmes, médecins)". Our h < L_p lock is the same claim, not new.
- **Standardised need.** Our `need = Σ pop·u` with age-specific use rates u is DREES's *standardised population*, with Assurance Maladie consumption weights.
- **Constant-rate assumption (stationarity)** is DREES's *scénario tendanciel*, with rates averaged over 2016–2020.
- **Quota variants (±20 %)** and the near-nil short-run effect of intake: DREES shows them (midwives ±12 %, pharmacists ±13 % in 2050).
- **The "Q·C" limit N\*** (Little's law) is not stated by DREES. I found no statement of it. That is the one unmatched analytic result; treat as "unclaimed, small".

## What differs

- **Grain:** DREES publishes **national** series (médecins carry a pre-2015 region internally). H1 is **département × profession**. It also needs the territorial share π, which DREES does not publish; this is our extension and also our main unvalidated risk.
- **Levers:** DREES has two (intake, foreign graduates) plus attrition for nurses. H1's seven slots (retention, retirement age, installation, task shifting, need) are beyond it, but only with sourced mechanisms; DREES's two are the only ones with a published effect size.
- **Need side:** DREES stops at a standardised density. H1 adds task shifting τ between professions; no incumbent found for that.
- **Mode of exercise:** DREES models **liberal/mixed vs salaried** for three professions (and 5 modes for nurses) and projects liberal and salaried headcounts separately. The brief says the liberal sector comes first. H1 as written has no practice-mode state. **This is the biggest structural gap in H1**: add mode of practice, as DREES does, or the headline cannot be about the liberal sector. Recorded as a recommendation for `decisions.md`, not a decision.
- **Exit rule:** DREES uses empirical age-specific cessation probabilities, not a retirement age; ours has `x[p,a,s]`, the same thing. A "retirement age" lever has no DREES precedent and needs its own citation (COR, quoted as a footnote in ER1319 note 12: +2 yr of opening age → +6 months of average retirement age).
- **Inactive reserve:** DREES carries a pool of inactive professionals with a resumption probability. H1 has none.
- **Uncertainty band:** DREES publishes variants, not bands. We have an open choice here.

## Comparison numbers for our projection

**Reframed 2026-11-13 after the objective changed** (profile: the deliverable is a library of swappable estimators, compared by backtest, not one exact number). DREES's published numbers below are therefore **not ground truth to match**. They are the outputs of one more estimator, **E_DREES** (a frozen national trend), which belongs in our comparison as a reference. Ground truth is observed RPPS. Use rows 1–7 as (a) sanity checks on our estimators' shape and (b) a published-estimator column in the backtest table. Each is national; sum our départements to compare.

| # | Quantity | DREES value | Source | Use |
|---|---|---|---|---|
| 1 | **Infirmiers 2035**, en emploi, tendanciel | **729 614** (2030: 685 737; 2050: 821 003) | ER1319 xlsx, sheet "Graphique Web" | Forward check. Scope differs (nurses in employment from BTS/SNDS, not RPPS) so compare **growth 2021→2035 = +21.8 %** (derived: 729 614/598 915) |
| 2 | **Médecins 2050**, <70 | **292 000**, +18 % in 2040, low 209 000 in 2024 | DD76 p.46 | Total only; we exclude GPs. Use the non-GP growth, **+39 % 2021→2050** (DD76 p.51); and the **GP-excluded** 2035 level has no published value |
| 3 | **Pharmaciens 2030/2040/2050** | 71 000 low in 2027; 76 600 (2040); 81 100 (2050) | DD76 p.46 | Shape check: dip then growth. Tolerance: the dip's depth of ≈2 % |
| 4 | **Chirurgiens-dentistes 2030/2040** | 45 900 / 53 900 | DD76 p.46 | Our 2035 should lie between (derived midpoint ≈ 49 900) |
| 5 | **Sages-femmes 2030** | 26 200 (2040: 28 600; 2050: 29 300; max 29 400 in 2048) | DD76 p.46 | Also tests the flat-then-declining shape |
| 6 | **Standardised density médecins** | −5 % at 2028, back to 2021 level in 2035, **+23 %** in 2050 | DD76 synthèse and p.53 | Need-side check for H1 |
| 7 | **Intake sensitivity** | ±20 % intake → ±12 % midwives, ±13 % pharmacists at 2050 | DD76 synthèse | Falsifier for our quota lever (K2): the effect at **2035** must be much smaller than at 2050 |

**A backtest of DREES's own 2021 projection on later RPPS data** (derived; scope checked 2026-11-13).
- **Scope check.** The DREES 2026 page defines its count as "Professionnel de santé en activité au 1er janvier exerçant au moins une activité en France" (RPPS). It does **not** say "moins de 70 ans". Source: <https://drees.solidarites-sante.gouv.fr/communique-de-presse-jeux-de-donnees/jeux-de-donnees/260702-les-effectifs-des-professionnels-de-sant%C3%A9>. So the 2026 counts are *not* documented as under-70, while DD76's are.
- **Size of the gap.** Our own `data/processed/stock.parquet` (RPPS, same totals as the page: dentists 48 690, pharmacists 75 335, midwives 26 428 in 2026) has an open "65 ans et plus" band, so over-70s can't be isolated. Compare 2020 instead: ours vs DD76 is dentists 42 843 vs 41 800 (+2.5 %), pharmacists 73 788 vs 72 600 (+1.6 %), midwives 23 175 vs 23 000 (+0.8 %). That is an **upper bound** on the scope/vintage difference.
- **Result after scaling DD76 by those factors.** DD76 interpolated to 2026 (linear 2020→2030 for dentists and midwives, 2020→2027 trough for pharmacists), then scaled: dentists ≈45 400 vs **48 690** observed (+7 %); pharmacists ≈72 300 vs **75 335** (+4 %); midwives ≈25 100 vs **26 428** (+5 %). So the 2021 trend scenario **undercounted by ≈4–7 % over six years**, even after removing the largest plausible scope effect. Unscaled it was 6–10 %.
- **Reading.** Dentists and midwives grew faster than the DREES trend, which assumed foreign-graduate inflow and intake held at their 2016–20 values. Pharmacists did not fall to the projected trough; the stock kept rising. This is the first scored point for **E_DREES** in the estimator comparison: ≈4–7 % national error at 6 years for 3 professions. It is national, not by département, so it is a reference line, not the bar to clear.
- **Caveats.** Interpolation is linear between published points; a vintage revision and the scope effect are mixed in the scaling factor; médecins and nurses are not in this check (médecins: our <70 sum, 214 224 in 2021, matches DD76's ≈215 000).

## Verdict on the derivation

- **Fits the new objective.** DREES's models are a ready-made family of estimators (component model with flows; lag-only intake variants; standardised density). Wrap them as reference entries in the estimator library, next to H0 (persistence) and H1 (stock-flow), and score all by the same backtest.

- **H1 survives** as a model *form*, but as a **rediscovery**: no claim of novelty for the structure or for the lag limit.
- **What is ours:** département grain, the π territorial split, the lever taxonomy with a flow slot each, the live recompute, and neutral-lexicon personas. None of the above is shown to improve accuracy yet; K1 decides.
- **Concrete change to H1:** add a **practice-mode state** (liberal/mixed vs salaried), an **inactive reserve**, and take **cessation, transition and reprise rates** from the RPPS panel as DREES does. Cost, assumed: +10–20 person-hours.

## Next

| Question | Price |
|---|---|
| ~~Does the DREES RPPS 2026 count use the <70 scope of DD76?~~ Done 2026-11-13: not stated, gap ≤2.5 % in 2020, backtest holds at ≈4–7 % | done |
| Read Millien 2018b (kiné, horizon 2040) and DREES's 2023 médecin update | ~30 min |
| Open `Méthode concertée V2` archive: APL formula, decay, bounds | ~30 min |
| Read Cour des comptes Dec 2024 and the Ordre des pharmaciens 2050 page with a working PDF reader | ~30 min |
