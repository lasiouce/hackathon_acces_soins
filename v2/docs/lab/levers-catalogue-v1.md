---
type: registry
date: 2026-11-13
author: Claude
status: draft
headline: 32 levers over the 7 flow slots; 0 wired end to end yet; every effect size except the legal facts is `assumed`
tags: [levers, model, personas]
---

# Policy lever registry

Each lever is a perturbation of one flow slot of the stock-flow model in
[[workforce-projection-model]] (§ Structure): exits **x**, entries **E/Q**
(lag L_p), installation shares **π**, net moves and foreign diplomas **M**,
activity rate **α**, use rate **u**, task shifting **τ/ρ**.

How to read it:
- **Source** names the text that *creates or describes* the lever (a law, a
  decree, a convention, a DREES study). The **effect size** (how much the slot
  moves) is a separate claim. Where no source gives it, the cell says
  `effect: assumed`, and the ledger ([[open]]) holds the price of finding it.
- **Default** is the status quo, so that the default scenario equals the
  baseline projection. Multipliers default to 1; task-shifting shares τ are
  *increments over the 2025 base year* and default to 0, because measures
  already in force by 2025 are already in the RPPS/use-rate data.
- **Personas**: A = ARS/DG (regional view), X = Administration (every
  parameter), P = politician (plain mode, via the presets below). X sees all
  rows.
- **Wired** = none yet. Per [[CLAUDE]], a lever counts only once it is wired
  end to end; this file is the spec, not the count.
- Lags L_p for training levers come from the derivation and are still
  `assumed` there (ledger row "Training lags L_p").

## Registry

### Pipeline levers (entries E/Q, π through training)

| id | Nom (FR) | Personas | Slot | Mechanism | Default · range · unit | Source | Lag |
|---|---|---|---|---|---|---|---|
| L01 | Numerus apertus — médecine | X, P | E/Q (M) | Universities set admissions within national pluriannual objectives; entries to specialties follow ~L years later | 1.0 · 0.9–1.3 · × objectif 2026–2030 (≥ 61 230 médecins over 5 y, press figure) | Loi n° 2019-774 du 24 juillet 2019 (OTSS, end of numerus clausus); arrêté du 13 sept. 2021 (objectifs 2021–2025: 51 505 médecins ± 5 %); arrêté du 20 oct. 2026 (2026–2030, reported by L'Étudiant). Effect: identity (no assumption beyond L_p) | 9–12 y (specialists; assumed) |
| L02 | Numerus apertus — pharmacie | X, P | E/Q (P) | Same mechanism; the ONDPS 2021–2025 review reports pharmacy barely reached its lower bound, so filled places < objective | 1.0 · 0.8–1.3 · × objectif 2026–2030 (~18 670, press figure) | Arrêtés 2021 & 2026 as L01; ONDPS/DREES bilan formation 2021–2025 (19 déc. 2025) | ~6 y (assumed) |
| L03 | Numerus apertus — odontologie | X, P | E/Q (O) | Same mechanism | 1.0 · 0.9–1.3 · × objectif 2026–2030 (≥ 8 625, press figure) | Arrêtés 2021 & 2026 as L01 | ~6 y (assumed) |
| L04 | Numerus apertus — maïeutique | X, P | E/Q (M) | Same mechanism; maïeutique lost 80 places over 2021–2025 vs 2016–2020 | 1.0 · 0.8–1.3 · × objectif 2026–2030 (≥ 5 570, press figure) | Arrêtés 2021 & 2026 as L01; ONDPS bilan 2021–2025 | ~5 y (assumed) |
| L05 | Quotas d'entrée en IFMK (kiné) | X, P | E/Q (K) | Annual admission quotas into kiné training institutes | 1.0 · 0.9–1.3 · × quota 2025 | `assumed` — the quota mechanism is known, but the legal reference and series were not checked this session (ledger) | ~5 y (assumed) |
| L06 | Places en IFSI (infirmiers) | A, X, P | E/Q (I) | Regions set nursing-school capacity | 1.0 · 0.9–1.3 · × capacité 2025 | `assumed` — legal reference and series not checked (ledger). Context: DREES ER n° 1319 (déc. 2024) projects +37 % nurses 2021–2050 vs +50 % need at constant use | ~3 y (assumed) |
| L07 | Taux de remplissage et d'abandon en formation | X | E/Q (all) | Share of opened places that become graduates; separates *places opened* from *graduates* | 1.0 · 0.7–1.0 · graduates / places | ONDPS/DREES bilan 2021–2025 (pharmacy under-filled). Per-profession value: `effect: assumed` | = L_p |
| L08 | Postes d'internat par région et spécialité | A, X | π (specialists), E/Q | Regional allocation of internship posts shifts where new specialists settle (they tend to stay near where they trained) | 1.0 · 0.8–1.2 · × share of posts per region; national total 10 260 posts in 2026 (incl. GP) | Annual arrêté of internship posts; 2026 total via ministry communiqué 14 oct. 2026 (reported by santementale.fr). Stay-near-training elasticity: `effect: assumed` | 4–6 y (DES length) |

### Stock levers (exits x, moves M, activity α)

| id | Nom (FR) | Personas | Slot | Mechanism | Default · range · unit | Source | Lag |
|---|---|---|---|---|---|---|---|
| L09 | Âge légal de départ à la retraite | X, P | x | Shifts the exit hazard of the 60–67 ages by Δ years | 0 · −1 to +2 · years vs calendar in force | Loi n° 2023-270 du 14 avril 2023 (LFRSS, 62→64); LFSS pour 2026 suspends the increase until 1 Jan 2028 (1964 cohort: 62 y 9 m), effective 1 Sept 2026 (vie-publique.fr). Mapping legal age → liberal exit hazard: `effect: assumed` | immediate (by cohort) |
| L10 | Cumul emploi-retraite | A, X, P | x, α | Retired professionals keep a reduced activity; lowers the effective exit rate after the legal age | 1.0 · 0.5–2.0 · × 2018 share (≈ 10 % of liberal/mixed doctors, 3.5 % in 2011) | DREES Études et Résultats n° 1097 (déc. 2018). Other professions and activity level while in cumul: `effect: assumed` | < 1 y |
| L11 | Attrition en cours de carrière (sorties précoces) | X | x | Exits before retirement age (career change, leaving liberal practice) | 1.0 · 0.7–1.3 · × observed rate | Estimated from DREES RPPS 2012–2026 (data-inventory). Policy effect on it: `effect: assumed` | < 1 y |
| L12 | Procédure PADHUE (EVC) | X, P | M | Annual competitive exams set how many non-EU diploma holders can be authorised; laureates then do a consolidation period | 1.0 · 0.5–2.0 · × EVC posts 2024 (3 749 médecins, 96 pharmaciens, 125 dentistes, 30 sages-femmes) | Art. L.4111-2 CSP; arrêté EVC 2024 and arrêté du 27 juin 2025 (session 2025), via FHF. Success and retention rates: `effect: assumed` | ~2–3 y (exam + consolidation; assumed) |
| L13 | Diplômes de l'UE (reconnaissance automatique) | X | M | EU diploma holders enter the stock without exam; modelled as a flow per profession | 1.0 · 0.5–1.5 · × observed inflow | Directive 2005/36/CE. Inflow level: to estimate from RPPS diploma-country field, else `assumed` | < 1 y |
| L14 | Taux d'activité / temps partiel | A, X, P | α | Converts headcount to FTE; lower α = less care supplied per professional | 1.0 · 0.8–1.1 · × α by profession × age × sex | DREES Les Dossiers n° 76 (mars 2021) projects "à comportements constants" (the default here). α values themselves: `effect: assumed` (no open FTE series checked) | immediate |

### Installation levers (π, territorial)

| id | Nom (FR) | Personas | Slot | Mechanism | Default · range · unit | Source | Lag |
|---|---|---|---|---|---|---|---|
| L15 | Régulation de l'installation — kinés | A, X, P | π (K) | In "zones non prioritaires", a new conventionnement only replaces a departure ("1 départ pour 1 installation") | on · on/off · rule | Avenant n° 7 à la convention nationale des masseurs-kinésithérapeutes (signé 13 juil. 2023, approuvé arrêté du 21 août 2023). Size of redirected flow: `effect: assumed`; direction: DREES Les Dossiers n° 89 (regulation evens out distribution but does not remove local gaps) | ~1 y |
| L16 | Régulation de l'installation — infirmiers | A, X, P | π (I) | In "zones sur-dotées", conventionnement tied to a departure ("une arrivée pour un départ") | on · on/off · rule | Avenant n° 6 à la convention nationale des infirmiers (signé 29 mars 2019). Effect: `assumed`; direction: DREES DD89 | ~1 y |
| L17 | Régulation de l'installation — chirurgiens-dentistes | A, X, P | π (O) | Conventionnement can be refused in "zones non prioritaires" (≈ 5 % of the population) since 1 Jan 2025 | on · on/off · rule | Convention nationale des chirurgiens-dentistes 2023–2028 (signée 21 juil. 2023, JO 25 août 2023); zoning method arrêté du 20 mars 2024. Effect: `assumed` | ~1 y |
| L18 | Régulation de l'installation — sages-femmes | A, X | π (SF) | Zoning-based conventionnement rule, assumed analogous to L16 | on · on/off · rule | `assumed` — legal reference not checked this session (ledger) | ~1 y |
| L19 | Régulation de l'installation — médecins spécialistes (hypothèse) | A, X, P | π (specialists) | Hypothetical: a "1 départ pour 1 installation" rule for specialists in zones with density above average; **not in force** | off · off/on · rule | Mechanism by analogy with L15–L17. Expected direction: DREES Les Dossiers n° 89 (Polton, Chaput, Portela, déc. 2021). Size: `effect: assumed` | ~1 y |
| L20 | Création d'officines (seuils de population) | A, X | π (P) | Opening a pharmacy requires a commune population threshold; caps pharmacist installation where population is low | on · on/off · rule | Art. L.5125-11 CSP as amended by ordonnance n° 2018-3 du 3 janvier 2018; thresholds not re-checked this session (ledger) | ~1–2 y |
| L21 | Aides à l'installation (contrats incitatifs, zonage ARS) | A, X, P | π | Payments for installing or staying in zones the ARS classes as under-served; raises the share of entrants there | 1.0 · 1.0–1.3 · × entrant share in aided zones | Contrats incitatifs infirmiers (avenant 6), ARS zonages (art. L.1434-4 CSP). Evidence: DREES DD89 — incentives attract but retain poorly. Size: `effect: assumed` | ~1 y |
| L22 | Contrat d'engagement de service public (CESP) | A, X | π (specialists, O) | Allowance during studies in exchange for practising in a listed under-served zone for the same duration | 1.0 · 1.0–3.0 · × contracts signed | Art. L.632-6 code de l'éducation (mod. loi n° 2023-1268); décret n° 2020-268 du 17 mars 2020. Count and completion rate: `effect: assumed` | = remaining training (4–8 y) |

### Demand-side levers (u, τ/ρ)

| id | Nom (FR) | Personas | Slot | Mechanism | Default · range · unit | Source | Lag |
|---|---|---|---|---|---|---|---|
| L23 | Vaccination par les pharmaciens (prescription + administration) | X, P | τ (specialists → P), ρ | Vaccination acts move from doctors (paediatrics, gynaecology; GPs as context only) to pharmacists | 0 · 0–0.5 · share of the remaining doctor vaccination acts shifted, increment over 2025 | Décret n° 2023-736 du 8 août 2023 (in force 10 août 2023, so mostly in the 2025 base). Share and its weight in specialist need: `effect: assumed` | < 1 y |
| L24 | Antibiotiques après TROD (angine, cystite) en officine | X | τ (→ P) | Pharmacists dispense antibiotics after a positive rapid test; acts mostly on GP need (context), marginal on specialists | 0 · 0–0.5 · share shifted, increment over 2025 | Décret n° 2024-550 du 17 juin 2024 + arrêtés du 17 juin 2024 (in force 19 juin 2024). Size: `effect: assumed` | < 1 y |
| L25 | Infirmiers en pratique avancée — effectifs formés | X, P | E/Q (IPA ⊂ I), τ (specialists → I) | More IPA graduates take over follow-up of stable chronic patients from specialists | 1.0 · 1.0–2.0 · × 1 000 IPA formés/an (target 2 000/an from 2027) | Décret n° 2018-629 du 18 juillet 2018 (IPA); ministry communiqué 14 oct. 2026 (doubling, reported by L'Étudiant / infirmiers.com). Specialist need absorbed per IPA: `effect: assumed` | ~2 y (master) |
| L26 | Accès direct aux IPA | A, X, P | τ (→ I) | Patients see an IPA without a doctor's referral; currently a 5-year experiment in CPTS in 6 territories from 1 Dec 2026 | 0 · 0/6 dép./all · territories covered | Loi n° 2023-379 du 19 mai 2023 (loi Rist); décret du 23 oct. 2026 (Hérault, Loiret, Yonne, Val-d'Oise, Martinique, Mayotte; reported by santementale.fr / caducee.net). Size: `effect: assumed` | < 1 y |
| L27 | Accès direct aux masseurs-kinésithérapeutes | A, X, P | τ (→ K), u (K) | Patients see a kiné without prescription (in coordinated practice, limited sessions without prior diagnosis); raises kiné need, lowers referring-doctor need | 0 · 0–1 · share of territory covered beyond the experiment | Loi n° 2023-379 du 19 mai 2023 (loi Rist) and its experimentation decree. Size: `effect: assumed` | < 1 y |
| L28 | Compétences élargies des sages-femmes | X, P | τ (gynéco-obstétrique → SF) | Vaccination and instrumental abortion (IVG instrumentale) in hospitals move acts from gynaecologist-obstetricians to midwives | 0 · 0–0.3 · share shifted, increment over 2025 | Décret n° 2023-737 du 8 août 2023 (vaccination); décret n° 2023-1194 du 16 déc. 2023 mod. by décret n° 2024-367 du 23 avril 2024 (IVG instrumentale). Size: `effect: assumed` | < 1 y |
| L29 | Consultation et diagnostic infirmiers | X, P | τ (→ I), u (I) | Nurses run consultations within their own role (e.g. simple wounds) and prescribe some products | 0 · 0–0.3 · share shifted, increment over 2025 | Loi n° 2025-581 du 27 juin 2025 sur la profession d'infirmier; décret n° 2025-1306 du 24 déc. 2025. Size: `effect: assumed` | < 1 y |
| L30 | Téléconsultation (plafond d'activité à distance) | A, X, P | u (cross-territory), ρ | A share of need is served from another territory; the convention caps remote activity at 20 % per doctor | 0.20 · 0–0.40 · max share of a doctor's activity at distance | Avenant n° 9 à la convention médicale, arrêté du 22 sept. 2021 (20 % cap). Share of need actually served across départements: `effect: assumed` | < 1 y |
| L31 | Taux de recours par âge (tendance) | X | u | Drift in age-specific use rates on top of Omphale ageing (kill test K5) | 0 · −2 to +2 · %/year | `assumed` until K5 runs on open use-rate data | n/a |
| L32 | Scénario de population Insee | A, X | u (via pop) | Chooses the population projection that drives need | central · basse/central/haute · Omphale scenario | Insee Omphale 2022 (data-inventory) | n/a |

L32 is a model input rather than a policy, but it is the first thing an
expert changes, so it lives here.

## Profession map — which levers apply to which MMOPKSI profession

● = acts directly on that profession's supply or need. ○ = acts on it as the
*source* of shifted demand (its need goes down). GP effects are context only.

| Lever | Spécialistes | Sages-femmes | Dentistes | Pharmaciens | Kinés | Infirmiers |
|---|---|---|---|---|---|---|
| Training (L01–L07) | ● L01, L07 | ● L04, L07 | ● L03, L07 | ● L02, L07 | ● L05, L07 | ● L06, L07 |
| Internship posts L08 | ● | | | | | |
| Retirement L09, cumul L10, attrition L11 | ● | ● | ● | ● | ● | ● |
| PADHUE L12 | ● | ● | ● | ● | | |
| EU diplomas L13 | ● | ● | ● | ● | ● | ● |
| Activity α L14 | ● | ● | ● | ● | ● | ● |
| Installation regulation | ● L19 (hypothesis) | ● L18 | ● L17 | ● L20 | ● L15 | ● L16 |
| Incentives L21 | ● | ● | ● | | ● | ● |
| CESP L22 | ● | | ● | | | |
| Pharmacist vaccination L23 | ○ (paediatrics, gynaecology) | ○ | | ● | | |
| TROD antibiotics L24 | (○, marginal) | | | ● | | |
| IPA L25, L26 | ○ (chronic follow-up) | | | | | ● |
| Kiné direct access L27 | ○ (MPR, rheumatology, orthopaedics) | | | | ● | |
| Midwife competences L28 | ○ (gynéco-obstétrique) | ● | | | | |
| Nurse consultation L29 | ○ | | | | | ● |
| Telehealth L30 | ● | ● | | | ● (télésoin) | ● (télésoin) |
| Use-rate trend L31, population L32 | ● | ● | ● | ● | ● | ● |

Note for the brief's example (*specialists in Clermont-Ferrand in 2035 if
pharmacists can vaccinate*): L23 acts on specialists only through the small
share of vaccination acts done by paediatricians and gynaecologists, and
mostly on GP need, which is context. The projected specialist effect is
expected to be close to zero (derived from the profession map, not
measured). Stock and installation levers (L09–L10, L19, L21) move that
number more.

## Scenario presets — politician view

Wording follows [[lexicon]]: each scenario is a set of hypotheses, and the
UI reports what it *conduit à*, against the "Tendances actuelles" baseline
and the national average, for a named year.

| Preset | Levers set (all others at default) | What the UI says |
|---|---|---|
| **S0 · Tendances actuelles** | All defaults (rules in force on 1 Nov 2026, population central) | « Projection à règles et comportements constants. Les autres scénarios sont comparés à celle-ci. » |
| **S1 · Formation renforcée** | L01–L04 = 1.2; L05, L06 = 1.2; L25 = 2.0 | « Ce scénario conduit à +N professionnels en 2035 et +M en 2045 par rapport aux tendances actuelles. Pour les spécialistes, l'effet apparaît après la durée des études (environ 10 ans). » |
| **S2 · Partage des compétences** | L23, L24, L28, L29 = upper half of range; L26 = all départements; L27 = 1 | « Ce scénario conduit à un écart entre offre et besoins projetés de X % en 2035 pour les spécialistes, contre Y % dans les tendances actuelles. Hypothèses d'effet non sourcées : voir le détail. » |
| **S3 · Installation orientée** | L15–L18 on; L19 on; L21 = 1.2; L22 = 2.0; L08 reweighted toward régions with density below the national average | « Dans les territoires où la densité est inférieure à la moyenne nationale, la densité projetée en 2035 est de D pour 100 000 habitants, contre D₀ dans les tendances actuelles. » |
| **S4 · Activité prolongée** | L09 = +1 y; L10 = 1.5; L12 = 1.5 | « Ce scénario conduit à +N professionnels en 2030, effet qui diminue ensuite. La densité diminue de X % d'ici 2035 au lieu de Y %. » |

Every number in the UI text is computed by the model, shown with its range,
and the "Hypothèses" panel lists the `assumed` effect sizes the scenario
uses.
