---
type: profile
aliases: [Lab profile]
---

# Lab profile — hackathon-sante

> Read by every `lab:` skill. Keep it under ~60 lines. Written by `/lab:init`
> on 2026-11-13; edit freely.

## Recadrage du 2026-11-14 (prime sur les sections ci-dessous quand elles divergent)
- **2026-11-14, après-midi :** l'agent conversationnel devient l'**interface principale**
  avec l'utilisateur·rice (plus une couche ultérieure). Mise en page en attente des
  propositions UX de l'équipe ; d'ici là, squelette fonctionnel (panneau « Questions »).
- **Projet de recherche quantitative.** Un jumeau numérique : des politiques
  nationales, exprimées comme des hyperparamètres sourcés (Omphale,
  Hippocrate, DREES n°76, plus des spécificités par profession), et leur
  effet sur l'effectif « libéral » de SF, CD, PH, MK et IDE.
  - **« Libéral »** = secteur privé, lucratif ou non. Tout employeur public
    est exclu.
  - ~~Spécialistes en phase 2 (cardiologie, dermatologie, ophtalmologie).~~ Remplacé le 2026-11-15 : amélioration
    possible, hors plan ; source de transferts seulement (O2).
- **Indicateur principal :**
  1. précision des prévisions contre des références naïves, au backtest
     (environ 10 ans au plus) ;
  2. reproduction des modèles de référence, avec le tendanciel DREES 2050 ;
  3. validité des leviers par expérience naturelle.

  La démo en direct n'est plus l'indicateur ; les personas sont une couche
  ultérieure.
- **Horizon de référence 2050.** Granularité : tous les niveaux, jusqu'à la
  commune.
- Feuille de route : [v2/ROADMAP.md](../../v2/ROADMAP.md). Décisions du
  2026-11-14 dans [v2/docs/lab/decisions.md](../../v2/docs/lab/decisions.md).

## What this project is for
A 48 h hackathon tool, built on French open data, that projects how many health
professionals there will be, by profession and territory (the brief excludes
general practice), and shows how public-health policies change that. It
covers the liberal (private-practice) sector first. Scope is **MMOPKSI**:
Médecine (specialists only, since the brief excludes general practice),
Maïeutique (midwives), Odontologie (dentists), Pharmacie, Kinésithérapie,
Soins Infirmiers (nurses). Example question: *how many specialists in
Clermont-Ferrand in 2035 if pharmacists can vaccinate?*

## Headline metric — the outcome, not the proxy
Two parts, both required (user, 2026-11-13):
- **Users:** three personas: ARS/DG (zoom commune → groups of communes →
  département → région), Administration
  (every parameter, daily), politician (national, occasional; professional and
  neutral register). See decisions.md.
- **Stage 1 scope:** demographic projections only. Supply from Hippocrate
  (DREES), population from Omphale (Insee), output = density per 100k.
- ~~superseded 2026-11-14, see Recadrage~~ **Decision usefulness:** in the live demo, a decision-maker changes a
  policy lever and reads the effect on headcount and access by territory,
  with an uncertainty band.
- **The deliverable is estimation algorithms, not one exact estimate**
  (user, 2026-11-13). It is a library of swappable estimators behind one
  interface, each with explicit assumptions. The backtest **compares**
  them; it does not crown a single number. ~~Forecast accuracy as a
  headline~~ superseded 2026-11-13: MAPE is now the comparison metric
  between algorithms.
- **Proxies that must never be the headline:** how many parameters exist
  (a lever only counts when it is wired end to end and its effect has a
  sourced mechanism), visual polish, model fit on the data it was trained
  on, and the count of datasets ingested.

## Currencies — the units that bind here
| Unit | Where it binds | Budget / ceiling (provenance) |
|---|---|---|
| person-hours | the whole build | **480 h** = 48 h × 10 people (sourced: user). Real coding time is probably ~60 % of that (**assumed**) |
| backtest MAPE (%) | headcount by profession × département at a 5–10 yr horizon | **not established**. A naive baseline sets the bar |
| levers wired end to end (count) | the "exhaustive parameters" goal | target **not established** |
| scenario recompute (s) | live demo interactivity | **< 2 s** (**assumed**) |
| territorial grain | département (101) vs bassin de vie / commune | ~~toutes les échelles jusqu'à la commune (user, 2026-11-14)~~ **département, région, national ; pas de commune** (user, 2026-11-15) |
| horizon | projection | **2050** (user, 2026-11-14); backtestable ≈ 10 y max (derived: data 2012–2026) |
| jury minutes | the pitch and demo | **not established**. Ask the organisers |

## Paths
| Record | Path |
|---|---|
| Layout | single-track |
| Derivations | `v2/docs/lab/derivations/` + `README.md` |
| Explorations | `v2/docs/lab/explorations/` + `README.md` (open-data sources go here) |
| Decisions | `v2/docs/lab/decisions.md` |
| Stage reports | `v2/docs/lab/reports/`; raw outputs in each axis `out/` folder |
| Open-questions ledger | `v2/docs/lab/open.md` |
| Live hypotheses | `v2/docs/lab/decisions.md` § Open |

## Upstream
None. This is separate from SEVEL LABS.

## House rules — hard constraints
- **Open data only**, as the brief requires. Every input names its dataset and
  vintage.
- **General practice is out of scope** (brief). GPs may appear only as
  context, for example when demand shifts from GPs to pharmacists. They are
  never a projected output.
- The submission deadline is fixed, so anything not demoable by H-6 is cut.

## How things are run
Not set yet. Default: Python + `uv` (`uv run python -m <pkg>.<mod>`).
