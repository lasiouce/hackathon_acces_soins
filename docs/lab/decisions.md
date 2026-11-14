---
type: decisions
aliases: [Decisions]
---

# Decisions — hackathon-sante

Each choice made, reversed, or rejected, with its *why*, so the team doesn't
re-argue it at 3 a.m. Format: **Decision** / **Why** / **What would reverse it**.
Every choice is provisional; a challenged-and-kept choice is recorded too.

## 2026-11-13 — Scope is MMOPKSI, with specialists only for Médecine

> **Remplacé le 2026-11-14** par « Recadrage en recherche » (plus bas) : phase 1 = SF, CD, PH, MK, IDE en « libéral » ; spécialistes en phase 2 (cardiologie, dermatologie, ophtalmologie).

**Decision.** The model projects six professions: médecins spécialistes,
sages-femmes, chirurgiens-dentistes, pharmaciens, masseurs-kinésithérapeutes
and infirmiers. It starts with the liberal sector. Médecins généralistes are
not projected and appear only as context, for example when demand shifts from
GPs to pharmacists.
**Why.** The brief says "hors médecine générale", and the team named the
MMOPKSI families.
**What would reverse it.** The organisers saying GPs are allowed, or open data
for one of the six being too thin to project at département level.

## 2026-11-13 — Three user personas, each with its own view of the same model

> **Reporté le 2026-11-14** : les personas deviennent une couche ultérieure (sélection des paramètres, aide à la décision), après le travail de recherche quantitative. Le besoin de l'ARS/DG (visibilité maximale, jusqu'à la commune) reste une exigence sur le *modèle*.

**Decision.** The tool serves three personas. They share one model and get
different interfaces.

| Persona | Needs | Interface consequence |
|---|---|---|
| **ARS / DG** (regional health agency, central directorate) | Everything happening in *their* region, with scaling: the regional capital matters a lot regionally and less nationally | ~~Multi-scale view: national → region → département → sub-départemental zones~~ *superseded 2026-11-13, see the ARS zoom-levels entry below.* The weight of a place depends on the zoom level. Default entry is "my region" |
| **Administration** (technical expert) | Tweak **every** parameter | Expert mode: the full lever registry (all 7 flow terms), with each value's source and vintage visible |
| **Politician** (occasional use, doesn't know the parameters) | Understand a situation and a scenario in words | Plain mode: a few named scenarios, outputs phrased with the **neutral lexicon** (`docs/lab/lexicon.md`). No value judgements: "l'accès aux soins est moindre", never "médiocre" |

**Why.** Team input, 2026-11-13.
**What would reverse it.** The jury rubric naming a single target user.

## 2026-11-13 — First stage: demographic projections from Omphale (Insee) and Hippocrate (DREES)

> **Corrigé le 2026-11-14** : Hippocrate est le *modèle* de projection de la DREES (pour les médecins), pas une source de données. Nos données de stock restent la série RPPS de la DREES. On reprend les hyperparamètres d'Omphale et d'Hippocrate (voir « Recadrage en recherche »).

**Decision.** Stage 1 builds the demographic core only:
- supply: professionals by profession × age × sex × territory, projected with
  the stock-flow model (H1), starting from **Hippocrate** (DREES);
- population: by age × sex × territory from **Omphale** (Insee);
- output: densities (professionals per 100,000 inhabitants) and their
  trajectory.

Need, use rates, task shifting and the access indicator come after stage 1.
**Why.** Team input. It is also the part every persona needs first, and it
is the input to everything else.
**What would reverse it.** Hippocrate not giving age × sex × territory, or
not giving enough years for the backtest. In that case the model falls back
to H0 and the K1 backtest is impossible.

## 2026-11-13 — ARS zoom levels go down to the commune

**Decision.** The ARS view starts at the **commune**, its finest level, and
zooms out:
**commune → groups of communes (the ARS's own subdivisions, where it has
them) → département → région**.
This supersedes "sub-départemental zones" in the personas entry above.
**Why.** Team input, 2026-11-13: the ARS looks at commune-level detail.
**Consequences.**
- *Data.* DREES stock and Omphale population stop at département, so
  commune level needs new sources:
  - today's professionals by commune (the public professionals directory,
    by practice address);
  - commune population (Insee census);
  - the ARS groupings.
- *Accuracy.* Measured département error is 8.6 % MAPE at 5–8 years (K1).
  At commune level, small counts add noise of about 1/√N (derived): ±45 % for
  N = 5.
**What would reverse it.** The jury or the ARS persona only needing
département level for projections.

## 2026-11-13 — The product is a library of estimation algorithms, not an exact estimate

**Decision.**
- The deliverable is a set of **swappable estimators behind one
  interface**: `fit` on past years, `predict` to future years, at
  profession × département × sex × age. Each carries its assumptions in
  plain words.
- The first ones are persistence, linear trend, stock-flow with national
  rates, stock-flow with local rates, and stock-flow national total ×
  trend shares. Every lever acts through an estimator.
- The backtest becomes a **comparison bench**: same windows, same metric,
  every estimator.
- The UI lets the user pick or compare estimators.
- MAPE stops being a headline claim and becomes the comparison metric.

**Supersedes** the "forecast accuracy" headline in `profile.md`. The K1
report stays valid as the first run of the bench.
**Why.** User, 2026-11-13: "notre objectif n'est pas de chercher
l'estimation exacte, mais de créer des algorithmes d'estimation". It also
matches K1: no single model wins everywhere.
**What would reverse it.** The jury asking for one official projection
number.

## 2026-11-13 — The UX design brief is accepted as input; personas reconciled

**Decision.**
- The designer's brief (`docs/lab/inputs/2026-11-13-brief-design-ux.md`)
  matches the three personas.
- It adds use frequencies: national policy occasional, ministry daily, ARS
  weekly (still a "?" in the brief).
- It sets the national persona's register to "professionnel". That is
  compatible with the neutral lexicon, but it is **not** plain popular
  language.

**Why.** The brief is team input. The reconciliation table is in that
note.

## 2026-11-13 — Primary source per profession × grain; APIs feed an ETL, never the recompute

**Decision.**
- **Projection base (dép × age × sex):** DREES RPPS stays primary for all six
  professions. ameli (`demographie-effectifs-et-les-densites`, Explore API,
  ODbL) is the liberal series: 23 specialties, 2010–2025.
- **Commune level and groups of communes, current state:** CartoSanté's
  public OGC TJS API (`cartosante.atlasante.fr/GC_tjs.php`) is primary for
  liberal infirmiers, kinés, sages-femmes and dentistes (counts × age band,
  2004/05–2025). It also covers specialists by specialty (`demo_ps`,
  2020–2025, no age).
- **Pharmacists:** neither ameli nor CartoSanté counts them, so DREES RPPS is
  the only source. Commune level is a gap; pharmacies (offices) are context
  only.
- **Access:** every API is pulled once into parquet with its extraction date.
  No API call happens at scenario recompute time (commune pull = 22 s,
  measured).
- **No mixing:** CartoSanté and ameli series are never mixed without a ratio
  adjustment. CartoSanté is 2–3 % above ameli for kinés (measured).

**Why.** [API scout report](reports/2026-11-13-api-scout-ameli-cartosante.md):
ameli stops at département. CartoSanté is the only open, queryable source
found at commune grain. The < 2 s recompute budget.
**What would reverse it.** CartoSanté's licence turning out to forbid reuse.
The TJS row order (inferred) failing the total check. A commune-level RPPS
extract proving cheaper and covering all six professions.

## 2026-11-13 — Demo UI: Streamlit + Plotly, four pages, an algorithm-agnostic engine

> **Gelé le 2026-11-14** : l'application reste en l'état ; elle revient avec la couche personas.

**Decision.**
- **Framework:** Streamlit + Plotly in `app/`, which calls `sante/` directly.
  The rejected alternative was a static page (Plotly.js/D3) with pre-baked
  JSON: it is instant, but every lever change would need an export step.
- **Pages:** Vue régionale (ARS/DG), En bref (politician), Tous les
  paramètres (Administration) and Méthode. The layout follows data.ameli.fr's
  patterns (chart cards, a breadcrumb, Année/Évolution tabs, an
  effectif/densité switch, a source line on every chart) but uses our own
  name, colours and no logo.
- **Engine (`app/engine.py`):** it runs any class in
  `sante.estimators.ESTIMATORS` with no estimator-specific code.
  - It fits at the latest data year on the last 6 years and predicts to
    2040.
  - The **band is an empirical self-backtest**, recomputed live: refit the
    same estimator h = 1…8 years earlier, then take the 10–90 % relative
    error over départements with ≥ 30 professionals. Beyond 8 years it is
    extrapolated linearly in h, and the UI says so. A new estimator gets a
    band for free; the band does not use `artifacts/s01_backtest`.
- **Default estimator:** "stock-flux, taux locaux". It has the lowest mean
  MAPE per département in the bench: 8.08 % vs 8.68 % for the linear trend,
  after the entry fix (it was 8.57 % before the fix). The politician view
  shows only the default.
- **Bias is shown, not hidden.** With flat entries, the stock-flow models
  under-predict specialists and dentists by about 10–12 % at 8 years. The
  self-backtest bands are therefore asymmetric (specialists at 8 years:
  −25 % / +11 %), and the app displays them as computed.
- **Region bands:** département bounds are summed, which assumes fully
  correlated errors (conservative).

**Why.** Requests from the user and the main session, 2026-11-13. Measured
speed: worst first-time page load 0.97 s; one estimator plus its band
≈ 0.36 s; comparing 3 estimators 0.4–0.5 s. All are within the < 2 s budget.
**What would reverse it.** A recompute above 2 s once levers are wired. The
jury wanting a single number, which would mean hiding the comparison. The
bench naming a clear winner, which would change the default.

## 2026-11-13 — CartoSanté commune loader: midwives and partial series excluded

**Decision.** `sante/cartosante.py` loads liberal nurses, kinés and dentists by
commune × age band. Territories whose series is incomplete are dropped
(30 communes, **including Marseille 13055**), never guessed. Midwives
(`sf_popage`) are excluded, because their rows don't follow the year × age
grid. This narrows the 2026-11-13 "primary source" entry: midwives at commune
level are **not** from CartoSanté until this is fixed.
**Why.** [Loader report](reports/2026-11-13-cartosante-commune-loader.md):
- with the inferred order, communes add up to the département pull in every
  département-year except dép 13;
- for midwives, no ordering reproduces the totals.

**What would reverse it.**
- Marseille: recovered via the `arm2026` framework.
- Midwives: a labelled endpoint for `sf_popage`.

## 2026-11-13 — Levers act through the engine: flow terms with training lags, plus output levers

**Decision.** `app/levers.py` + `app/engine.py` wire the first levers end to
end:
- L01–L06 (entries × m, after the training lag L_p);
- L09 (retirement age: exits at 60–69 × (1 − Δ/5));
- L10 (cumul emploi-retraite: exits at 65+ × (1 − 10 %·(k − 1)));
- L14 (activity rate α → full-time-equivalent supply).

L32, the population variant, was already wired. Mechanisms come from
`levers.md`. Effect sizes and L_p are `assumed`, and the UI says so.
- **Flow levers** perturb the fitted flow terms (`rates` = s, inflow, slope)
  of estimators that have them. A lag is handled by projecting in two
  segments (baseline until origin + L_p, perturbed after). Estimators
  without flow terms report the lever as "sans effet", with no silent
  fallback.
- **Output levers** (α) apply to every estimator.
- **Band under a scenario:** the baseline estimator's self-backtest band
  is reused, assuming the levers don't change the error distribution.
- **Speed:** the two-segment projection, run without levers, reproduces
  `predict` exactly (difference 0) and is 6× faster. The engine uses it for
  the stock-flow family: 36 ms per run, 68 ms per page update with a lever
  (measured).

**Rejected:** applying every lever as a multiplier on the final headcount.
It is the cheapest option and works for any estimator, but it ignores ageing
and lags. It would let quotas move the 2035 specialist count, which the
derivation rules out (h = 9 < L ≈ 10).

**Checks (measured, specialists libéraux unless noted):**
1. All levers at default = baseline (difference 0).
2. Quotas +20 % → 2035 change 0.00 % (lag respected).
3. Nurses +10 % → +3.3 % at 2035, origin 2023. The derivation predicts
   ≈ +2.6 % (δ·(h − L)/C, C = 35). We are 27 % above it: either the
   effective career is ≈ 27 years, or the fitted inflow also carries
   non-training entries. Kinés +10 % → +1.7 %.
4. Retirement +1 y → +1.1 %; −1 y → −1.05 %; cumul ×2 → +1.1 %.

**Relation to the open "engine interface" proposal (below).** This is a
first, narrower version of it. Slots are detected rather than declared.
There is one step time profile (the lag) and no territorial selector yet.
Flow levers have no output-multiplier fallback. Moving to
`Perturbation(slot, selector, profile)` stays open.
**What would reverse it.**
- K2 (pipeline lock) contradicting check 2.
- A sourced L_p or career length that moves check 3 by more than a factor 2.
- A lever whose effect needs time-varying rates beyond one step.

## 2026-11-14 — Recadrage en recherche : jumeau numérique des professions « libérales »

**Décision.**
- **Objectif.** Simuler des politiques publiques nationales, chacune
  exprimée comme un réglage d'hyperparamètres sourcés, et mesurer leur effet
  sur l'effectif « libéral » à une date future t.
  - Les hyperparamètres viennent d'Omphale, d'Hippocrate et du Dossier DREES
    n°76, plus des spécificités par profession : régulation de
    l'installation, filières en pharmacie, spécialisation en odontologie,
    abandon en études infirmières.
  - Les effectifs couvrent les sages-femmes, les chirurgiens-dentistes, les
    pharmaciens, les masseurs-kinésithérapeutes et les infirmiers.
- **Phase 2** : cardiologie, dermatologie, ophtalmologie (appui : rapport
  HCAAM sur les dépassements d'honoraires).
- **Démarche.** Mode de recherche quantitative : reproductible,
  falsifiable, interprétable, sans boîte noire. Code en briques (plug-ins
  par flux).
- **Feuille de route et axes de recherche** : [ROADMAP.md](../../ROADMAP.md).

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Ce qui le renverserait.** Un nouveau cadrage du jury ou de l'équipe.

## 2026-11-14 — « Libéral » = secteur privé, lucratif ou non (tout employeur public exclu)

**Décision.**
- Une personne compte comme « libérale » si elle n'exerce pas chez un
  employeur public.
  - **Inclus :** libéraux et mixtes, pharmaciens adjoints salariés
    d'officine, salariés de cliniques privées et d'établissements privés
    non lucratifs, industrie, laboratoires privés.
  - **Exclus :** hôpital public, PMI, Éducation nationale, EHPAD publics,
    centres de santé municipaux, et tout autre employeur public.
- Dans le code, le nom est explicite (`prive`, hors public). Dans les
  textes, on rappelle la définition, car les sources (RPPS, ameli)
  emploient « libéral » au sens d'exercice indépendant.

**Pourquoi.** L'utilisateur·rice, 2026-11-14. Le second point (autres
employeurs publics exclus, industrie incluse) a été choisi parmi des options
proposées.

**Conséquence mesurée.** Effectifs de la dernière année, ancienne
définition (libéral + mixte) → nouvelle. Le minimum compte zéro salarié
hospitalier privé ; le maximum les compte tous :
| Profession | Ancienne | Minimum | Maximum |
|---|---|---|---|
| Pharmaciens 2026 | 27 294 | 65 344 | 75 335 |
| Sages-femmes 2026 | 9 615 | 12 475 | 26 428 |
| Kinés 2026 | 92 836 | 98 348 | 111 237 |
| Dentistes 2026 | 40 083 | 48 143 | 48 690 |
- Le RPPS de la DREES ne sépare pas le public du privé dans « salarié
  hospitalier ».
- « Autre salarié » mélange aussi des employeurs publics (PMI…) et
  privés.

Il manque donc une donnée (voir le ledger). Les résultats K1 et
« entrées par la filière » sont **mesurés sur l'ancien périmètre**.

**Ce qui le renverserait.** Aucune source ouverte ne permettant de séparer
public et privé. Dans ce cas, la sortie serait donnée sous forme de
fourchette, ou la définition révisée.

## 2026-11-14 — Les modèles tournent à toutes les granularités, jusqu'à la commune ; horizon de référence 2050

**Décision.**
- **Granularité.** Les modèles s'appliquent à chaque niveau : commune,
  groupes de communes, département, région, national.
  - La régulation de l'installation est une **liste de géocodes** par
    profession : zones où l'installation est limitée au remplacement d'un
    départ, et zones où l'exercice est obligatoire.
  - Une même profession peut relever des deux statuts selon la zone
    (kinés).
  - Le DG de l'ARS doit avoir la visibilité maximale.
- **Horizon de référence : 2050.**

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Conséquences.**
- 2050 = 24 ans après 2026. Avec des données de 2012 à 2026, un backtest
  ne couvre qu'environ 10 ans, donc **aucune précision ne peut être annoncée
  à 2050**. On peut seulement reproduire le tendanciel de la DREES à 2050
  (Dossier n°76) et vérifier les cas limites.
- À 24 ans, l'horizon dépasse toutes les durées de formation : les quotas
  deviennent des leviers de premier ordre.
- À l'échelle de la commune, le bruit sur les petits effectifs (environ
  ±45 % pour N = 5, dérivé) se cumule sur l'horizon.

**Ferme** deux points de « En attente » : « Demo horizon » et « Projection
grain ».

## 2026-11-14 — Les nouveaux modèles ne sont pas tenus d'être des stock-flux

**Décision.**
- Le stock-flux (H1) est le **modèle de départ à battre**, pas la méthode
  imposée.
- Toute méthode peut entrer sur le banc si elle remplit trois conditions :
  - elle est interprétable, sans boîte noire ;
  - chaque levier y modifie un paramètre nommé et sourcé ;
  - elle respecte le contrat des modules.

  Par exemple : microsimulation, modèles bayésiens hiérarchiques ou
  espace-état, choix discret de l'installation, dynamique des systèmes,
  GAM, modèles spatiaux.
- C'est l'axe 2 de [ROADMAP.md](../../ROADMAP.md).

**Pourquoi.** L'utilisateur·rice, 2026-11-14.
**Ce qui le renverserait.** Aucun.

## 2026-11-14 — L'axe 0 est le jumeau numérique de l'offre de soins en France

**Décision.**
- Le socle commun qui relie les axes de recherche est un **jumeau numérique
  de l'offre de soins**. Il comprend trois composants :
  1. un **état unique** : N[profession, secteur, âge, sexe, commune, t],
     plus le vivier en formation ;
  2. des **modules de flux** en plug-ins, chacun avec ses paramètres
     sourcés ;
  3. des **scénarios** : jeux d'hyperparamètres et d'événements datés. Une
     politique publique est un scénario.
- Les axes 1 à 5 s'y branchent.
- L'état comprend le **secteur public**. C'est dérivé : un entrant bloqué
  par la régulation, ou une transition privé ↔ public, doit avoir où aller
  pour que les effectifs se conservent. La sortie étudiée reste le
  « libéral » (privé).

**Pourquoi.** L'utilisateur·rice, 2026-11-14 : « le liant de l'axe 0 c'est
un jumeau numérique de l'offre de soins en France ».
**Ce qui le renverserait.** Le secteur public ne pouvant pas être estimé à
la commune. Dans ce cas, il serait tenu à une échelle plus grossière et
ventilé.

## 2026-11-14 — Axe 5 adopté ; ordre de travail et format des fiches

**Décision.**
- **L'axe 5 est adopté** : analyse de sensibilité (Morris, puis Sobol) et
  incertitude à 2050.
- **Ordre de travail.**
  - Les axes 0, 1, 3 et 4 démarrent tout de suite, en parallèle :
    - axe 0 : le jumeau, en code ;
    - axe 1 : fiches de paramètres ;
    - axe 3 : protocoles de validation ;
    - axe 4 : données, avec en tête la séparation public / privé.
  - Les axes 2 et 5 démarrent quand le contrat du jumeau (axe 0) tourne.
    Ils ont besoin de son interface.
- **Format commun des fiches** (axes 1 et 4) : `docs/lab/fiches/<id>.md`,
  avec un frontmatter qui contient :
  - `parametre`, `profession`, `module` (le flux du jumeau visé) ;
  - `valeur`, `unite`, `incertitude` ;
  - `source`, `millesime` ;
  - `statut` : mesuré / sourcé / supposé / non mesurable.
- **Règle de partage du dépôt.** Le dépôt n'a encore aucun commit, donc les
  sessions travaillent dans le même dossier. Chacune ne touche que ses
  fichiers et ne commite rien. Seule l'axe 0 modifie `sante/`.

**Pourquoi.** L'utilisateur·rice valide l'axe 5 et l'ordre, 2026-11-14.
L'ordre « axe 0 d'abord, puis le reste » est affiné : les axes 1, 3 et 4
produisent des documents et des données, pas du code qui dépend du contrat.
Les attendre ferait perdre du temps de hackathon.
**Ce qui le renverserait.** Le contrat de l'axe 0 exigeant un format de
fiche différent. Dans ce cas, on convertit les fiches, qui sont du texte.

## 2026-11-14 — La suite est dans v2

**Décision.** Les décisions à partir de maintenant vont dans
[v2/docs/lab/decisions.md](../../v2/docs/lab/decisions.md). Ce journal (v1)
est figé. Les entrées du 2026-11-14 ci-dessus y sont recopiées.

## Open / not yet decided

**Live hypotheses** (from [derivations/workforce-projection-model.md](derivations/workforce-projection-model.md)):
- **H0, baseline.** Persistence or a linear trend per profession × département.
  Every accuracy claim is stated against it.
- **H1.** A cohort-component stock-flow model (exits by age, lagged entries
  from quotas, constant installation shares, need = INSEE population ×
  age-specific use rate) beats H0 on backtest MAPE at an 8-year horizon. It
  also reproduces the two limits: persistence at h → 0 and N* = Q·C at
  h → ∞. Falsified by K1.
  - **K1 result (2026-11-13,
    [report](reports/2026-11-13-k1-backtest.md)):** it survives in a
    narrower form. Nationally, mean |error| is 2.5 %, vs 4.6 % for the trend
    and 7.8 % for persistence. Per département it only ties the trend: MAPE
    8.57 % vs 8.68 %. So there is no département accuracy claim beyond
    "on par with the trend". H1 stays the scenario engine because it is the
    only candidate with ages and levers. Default variant from now on:
    local rates, chosen before the next test.
  - **Correction (2026-11-13):** entries were double-counted (retention
    above 1 in the entry bands made entries compound). After the fix,
    H1 local rates is best per département (8.08 % vs 8.68 % for the
    trend). The national claim is **withdrawn**: 4.1 % mean error, and
    specialists and dentists −10 to −12 % at 8 years because flat entries
    miss the 2012–2026 rise. Next: entries from the known student
    pipeline. Details in the K1 report, correction section.
  - **Pipeline entries (2026-11-13,
    [report](reports/2026-11-13-pipeline-entries.md)):** at 5 years they
    cut the national bias for specialists (−6.5 → −4.1 %) and pharmacists
    (−4.2 → −3.3 %), but not for dentists. The rest of the gap is rising
    entries at 25–39 and later exits past 65. Registered as an estimator;
    the default stays local rates (flat entries), which is best per
    département.

**Decisions waiting to be made:**
- ~~**Demo horizon**, e.g. 2035.~~ *Fermé le 2026-11-14 : 2050.* Note the derived result: quotas cannot move
  the 2035 specialist count.
- ~~**Projection grain.** Département by default; region for small counts
  (K4).~~ *Fermé le 2026-11-14 : tous les niveaux, jusqu'à la commune.*
- **Supply unit.** Headcount or FTE (activity rate α).
- **Mistral.** Whether the hackathon ("Mistralverse") requires a Mistral
  model. If yes, it goes in the scenario compiler, never in the forecaster.
- **What a commune-level *projection* means.** Proposed, not yet agreed:
  - **current state** is measured at commune level;
  - **projections** are made per département (where K1 measured them) and
    shared out to communes and groups by current shares, labelled
    "estimation" with a wider band;
  - all levels **add up exactly** (commune → group → département → région).
- **Which "groups of communes".** Options: ARS health territories
  (territoires de démocratie sanitaire), the ARS shortage zoning per
  profession (ZIP/ZAC), Insee bassins de vie, or EPCI. It probably depends
  on the ARS.
- **Infrastructure mapping** (from the design brief: "cartographier la
  présence d'infrastructures"). Health establishments, e.g. the FINESS
  register, are not in stage 1. Decide whether they are in scope and when.
- **Live hypotheses H2, H3** (from
  [derivations/stress-tests-and-feedback.md](derivations/stress-tests-and-feedback.md)):
  - **H2.** Stress tests as time-profiled perturbations of the flow terms
    (the same object as levers), scored by depth D, recovery time T_r,
    lost professional-years A and #territories below a threshold. For
    large or long shocks they give answers that differ by more than 5 %
    from the output-multiplier baseline S0. Falsified by K-S0vsS1.
  - **H3.** A feedback stock-flow estimator (installation zero-sum,
    retention at 60+, activity) reduces to H1 at gain 0. It keeps the
    national total. It can't close a density gap faster than the entrant
    flow (≈ 1/C ≈ 3 %/yr, derived). Whether it describes reality is
    decided by K3 (ameli 2010–2025).
- **Engine interface** (for the algorithm-agnostic engine being designed
  in another session). Proposed:
  1. `predict(years)` returns trajectories;
  2. each estimator declares the flow slots it supports;
  3. one `Perturbation(slot, selector, time profile)` type for levers and
     shocks, with an output-multiplier fallback flagged in the UI;
  4. resilience indicators computed by the engine.
- **Stress-test threshold:** what counts as "below threshold", worded
  neutrally (e.g. "densité inférieure à X % de la moyenne nationale").

