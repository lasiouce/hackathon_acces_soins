---
type: ledger
aliases: [Open questions]
---

# Open questions ledger

| Item | Price | Raised by | Date | Status |
|---|---|---|---|---|
| Expand "MMOPKSI": which professions are in scope? | 5 min, user | lab:init | 2026-11-13 | closed 2026-11-13: Médecine (specialists), Maïeutique, Odontologie, Pharmacie, Kiné, Soins infirmiers |
| GP exclusion vs the "doctors in Clermont" example | 5 min | lab:init | 2026-11-13 | closed 2026-11-13: specialists projected; GPs only as context |
| Which open datasets exist per profession | ~1 h | lab:init | 2026-11-13 | partly closed 2026-11-13: entries for M/O/P are covered (explorations/data-inventory.md); the stock, specialty split, S/K/I entries, projections and use rates are missing |
| Territorial grain: département vs bassin de vie | 30 min, after the data survey | lab:init | 2026-11-13 | closed 2026-11-14: all levels down to commune (decisions.md) |
| Jury rubric and demo length | 10 min, ask the organisers | lab:init | 2026-11-13 | open |
| Naive baseline MAPE (flat or linear trend) that the model must beat | ~1 h once data is loaded | lab:init | 2026-11-13 | open |
| K1 backtest: H1 vs H0 MAPE at 8-yr horizon, profession × département | ~6–10 person-hours (assumed); blocked on data survey | derive-ansatz | 2026-11-13 | open |
| K2 pipeline lock: quota sensitivity of the 2035 stock (specialists should be ≈ 0) | ~1 h once A1 runs | derive-ansatz | 2026-11-13 | open |
| K3 installation: constant vs logit entrant shares, held-out years (decides A2) | ~4–6 person-hours | derive-ansatz | 2026-11-13 | open |
| K4 small counts: median N per profession × département (decides grain) | ~30 min | derive-ansatz | 2026-11-13 | open |
| K5 need stationarity: drift of age-specific use rates | ~2 h | derive-ansatz | 2026-11-13 | open |
| Training lags L_p and career length C (assumed in derivation) | ~30 min, explore-and-report | derive-ansatz | 2026-11-13 | open |
| Does "Mistralverse" require using a Mistral model? | 5 min, ask organisers | derive-ansatz | 2026-11-13 | open |
| DREES projection models + APL indicator: incumbent to cite/reuse | ~1 h, explore-and-report | derive-ansatz | 2026-11-13 | open |
| Get the workforce stock (DREES, by profession × age × sex × département, max years) — blocks H1 and K1 | ~1 h | data-inventory | 2026-11-13 | closed 2026-11-13: DREES RPPS 2012–2026, dép × age × sex × mode (data-inventory update) |
| Separate specialists from GPs in DES MEDECINE (internship posts by specialty) | ~30 min | data-inventory | 2026-11-13 | closed 2026-11-13: `specialites_agregees` in Médecins RPPS |
| Meaning of année_dans_le_diplôme = 13 | 10 min, DREES dictionary | data-inventory | 2026-11-13 | open |

| What exactly Hippocrate (DREES) gives: professions, age × sex × territory grain, years available (decides H1 vs H0 and K1) | ~30 min, read its doc / the URL in the source list | team input | 2026-11-13 | closed 2026-11-13: assumed = DREES RPPS series; 15 years → K1 possible |
| Omphale: which scenario(s), horizon, grain (département × age × sex?) | ~30 min | team input | 2026-11-13 | closed 2026-11-13: Central + Pop basse/haute, 101 dép × sex × 5-yr age, 2018–2070 |
| Sub-départemental grain for the ARS view (regional capital): which zoning, and how to disaggregate without small-count noise | ~1 h, after K4 | personas | 2026-11-13 | superseded 2026-11-13: ARS zooms from commune (decisions.md) |
| Lexicon review by someone who knows the political register | 20 min, team | personas | 2026-11-13 | open |
| Salaried nurses: estimate dép × age × sex from marginals (raking) | ~1 h | data-inventory | 2026-11-13 | open |
| Kiné series break 2016→2017 (ADELI→RPPS): size it before using pre-2017 years | ~30 min | data-inventory | 2026-11-13 | open |
| Levers: task-shifting effect sizes τ/ρ (L23–L29) — share of specialist acts shifted per measure; look in DREES, IRDES, HAS evaluations | ~2 h, explore-and-report | levers registry | 2026-11-13 | open |
| Levers: installation response to regulation and incentives (L15–L22) — size of redirected entrant flow; IRDES/DREES evaluations of avenant 6 IDE and avenant 7 MK | ~1.5 h, explore-and-report | levers registry | 2026-11-13 | open |
| Levers: map legal retirement age → liberal exit hazard (L09), and cumul share for non-doctors (L10) | ~1 h, RPPS 60+ age pyramid | levers registry | 2026-11-13 | open |
| Levers: activity rate α by profession × age × sex (L14) — any open FTE series? | ~1 h | levers registry | 2026-11-13 | open |
| Levers: legal reference and series for IFMK quotas (L05) and IFSI capacity (L06) | ~30 min | levers registry | 2026-11-13 | open |
| Levers: midwife installation regulation — which avenant, which zones (L18) | ~15 min | levers registry | 2026-11-13 | open |
| Levers: pharmacy opening thresholds in art. L.5125-11 CSP (L20) — re-check on Légifrance | ~10 min | levers registry | 2026-11-13 | open |
| Levers: PADHUE success, consolidation length and retention (L12); EU-diploma inflow from RPPS (L13) | ~45 min | levers registry | 2026-11-13 | open |
| Levers: telehealth — share of need served across départements (L30) | ~1 h | levers registry | 2026-11-13 | open |
| Levers: confirm press-reported figures in the JO (2026–2030 objectives, 10 260 internship posts 2026, IPA 2 000/an, décret 23 oct. 2026 IPA access) | ~20 min | levers registry | 2026-11-13 | open |
| Commune data: professionals by commune (public professionals directory, practice address) + Insee commune population; sizes shown before download | ~1 h | ARS commune decision | 2026-11-13 | partly closed 2026-11-13: CartoSanté TJS gives liberal IDE/MK/SF/CD by commune × age, specialists by specialty (api-scout report); pharmacists + salaried still need RPPS |
| Which ARS groupings of communes (health territories, ZIP/ZAC shortage zoning, bassins de vie, EPCI) and where to get them | ~30 min | ARS commune decision | 2026-11-13 | partly closed 2026-11-13: CartoSanté serves bv, EPCI, territoire de démocratie sanitaire, territoire de vie-santé + ARS zoning per commune (api-scout report); the choice itself is open |
| Share-out rule: département projection → communes by current shares, with a widened band; check that levels add up | ~1 h | ARS commune decision | 2026-11-13 | open |
| App: ARS zoom levels commune → group → dép → région | ~1–2 h | ARS commune decision | 2026-11-13 | open |
| Infrastructure mapping (FINESS establishments) from the design brief: in scope? when? | 10 min, team; ~1 h data if yes | design brief | 2026-11-13 | open |
| CartoSanté TJS loader → stock_commune.parquet (IDE/MK/SF/CD × age band × year + demo_ps), with a known-total check on the inferred row order | ~1 h | API scout | 2026-11-13 | closed 2026-11-13: nurses/kinés/dentists loaded, checks pass except Marseille; midwives excluded (reports/2026-11-13-cartosante-commune-loader.md) |
| CartoSanté `*_flux` (installations/cessations by commune?): find an endpoint that returns values (not in TJS) | ~45 min | API scout | 2026-11-13 | open |
| CartoSanté reuse licence: none stated; ask Atlasanté or find the legal notice | 15 min + wait | API scout | 2026-11-13 | open |
| Pharmacists below département: no ameli/CartoSanté count; size an RPPS directory extract | ~1 h | API scout | 2026-11-13 | open |
| ARS conventional zoning file: vintage unknown (metadata 2014/2019) and no z_sf column; find the current per-profession zoning | ~30 min | API scout | 2026-11-13 | open |
| K-cons: feedback estimator keeps the national total vs H1 | 10 min | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| K-bound: feedback gap closure ≤ entrant flow E/N | 15 min | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| K3-feedback: sign of installation vs density gap from ameli 2010–2025 | ~1 h | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| K-bench: feedback estimator vs H1 on the bench | ~30 min after K3 | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| K-S0vsS1: same 3 crisis scenarios via output multiplier vs slot perturbation | ~30 min after S1 | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| K-osc: quota feedback oscillation onset vs g·τ ≈ π/2 | 20 min | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| COVID-era figures for realistic shock profiles (demand surge, early retirements, nurse departures) | ~1 h, explore-and-report | derive-ansatz (stress/feedback) | 2026-11-13 | open |
| Marseille (13055) missing from stock_commune: pull CartoSanté arm2026 (arrondissements) and sum | ~20 min + 1.5 min machine | cartosante loader | 2026-11-13 | open |
| Midwives by commune: sf_popage row order unreadable; try another CartoSanté route or RPPS directory | ~30 min | cartosante loader | 2026-11-13 | open |
| Load CartoSanté demo_ps (specialists by specialty × commune, 2020–2025) with the same checks | ~45 min | cartosante loader | 2026-11-13 | open |
| Entries from the known pipeline (enrolled students M/O/P, quotas) instead of flat inflow; fixes the −10 to −12 % national bias at 8 y | ~2 h | K1 correction | 2026-11-13 | closed 2026-11-13: partly fixes specialists/pharmacists (report pipeline-entries) |
| 60+ retention trend estimator (later retirement), on the bench | ~1 h | pipeline-entries | 2026-11-13 | open |
| Foreign-diploma inflow for dentists (DREES place of diploma) | ~1 h | pipeline-entries | 2026-11-13 | open |
| Explain the 2025 enrolment jump (e.g. dentistry year 2: 2,083 vs ~1,500) | ~20 min | pipeline-entries | 2026-11-13 | open |
| Séparer public / privé dans « salarié hospitalier » et « autre salarié » (RPPS détaillé par secteur d'activité, SAE, BTS pour les infirmiers) ; sans ça, la sortie « libéral » des SF va de 12 475 à 26 428 | ~1 h, explore-and-report | recadrage « libéral » | 2026-11-14 | déplacée vers v2/docs/lab/open.md |
| Relancer le banc (K1 + filière) sur le nouveau périmètre « libéral » (privé) | ~20 min après la séparation public/privé | recadrage « libéral » | 2026-11-14 | déplacée vers v2/docs/lab/open.md |
| Zonage conventionnel par commune × profession en géocodes (statut remplacement seul / obligation d'exercice), millésime actuel | ~30 min | recadrage granularité | 2026-11-14 | déplacée vers v2/docs/lab/open.md |
| Validation à 2050 : reproduire le tendanciel DREES n°76 (CD, SF, PH) avec leurs hypothèses, écart en % | ~2 h | horizon 2050 | 2026-11-14 | déplacée vers v2/docs/lab/open.md |
