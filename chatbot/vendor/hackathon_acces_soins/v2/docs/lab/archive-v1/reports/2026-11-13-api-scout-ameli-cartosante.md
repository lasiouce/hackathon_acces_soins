---
type: analysis
date: 2026-11-13
author: Claude
question: Which ameli / CartoSanté / Atlasanté open datasets cover MMOPKSI, at what grain, and which can we query by API instead of bulk download?
headline: 37 MMOPKSI-relevant datasets, 30 confirmed usable via unauthenticated API (ameli 10/10, CartoSanté 19/25, Atlasanté 1/2); commune grain only via CartoSanté
status: draft
professions: [specialistes, sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: data survey (feeds the commune-level ARS decision)
sources: [data.ameli.fr Explore API v2.1, cartosante.atlasante.fr GC_tjs.php (OGC TJS), catalogue.atlasante.fr GeoNetwork + /api/data]
tags: [data, api, ameli, cartosante, atlasante, commune]
---

# API scout: data.ameli.fr, CartoSanté, Atlasanté

> **Headline:** 37 MMOPKSI-relevant datasets across the three portals; **30 are
> confirmed queryable by public, unauthenticated API** (measured: each was
> queried). ameli stops at **département**. **CartoSanté goes down to the
> commune** (and bassin de vie, EPCI, territoire de démocratie sanitaire,
> territoire de vie-santé) for liberal nurses, kinés, midwives and dentists,
> 2004/05–2025. **Neither portal counts pharmacists** (CartoSanté counts
> pharmacies).

## Question
Can we pull the liberal-sector stock and its context by territory from APIs
(cheap, filterable, vintage-stamped) instead of bulk files, and which source
is primary for each profession × grain? Feeds the open items "Commune data"
and "Which ARS groupings" in [open.md](../open.md) and the ARS commune
decision in [decisions.md](../decisions.md).

## Result

### 1. data.ameli.fr (Opendatasoft "Huwise", Explore API v2.1)
The page URL in the brief has a typo (`professionels` → 404). The real page
is <https://data.ameli.fr/pages/data-professionnels-sante-liberaux/>; it
embeds 6 datasets. The catalog (`/api/explore/v2.1/catalog/datasets`, 51
datasets) adds 4 more relevant ones. **All: département + région (code
`999` = regional/national aggregate rows), Licence ODbL, producer Cnam /
SNDS, vintage = `modified` date.** No commune grain, **no pharmacists**
(the "trentaine de professions" are doctors, dentists, midwives and
auxiliaires médicaux).

| Dataset id (on page?) | Rows | Years | Variables | Modified | MMOPKSI use |
|---|---|---|---|---|---|
| `demographie-effectifs-et-les-densites` (✔) | 3,694,080 | 2010–2025 | effectif, densité × 5-yr age band (<25…70+) × sex × profession (23 specialties, dentists omni/ODF, SF, IDE, MK) | 2026-10-28 | **stock by age × sex** (already loaded, `sante/ameli.py`) |
| `demographie-exercices-liberaux` | 142,080 | 2010–2025 | effectif × libéral exclusif / mixte | 2026-10-12 | split exclusive vs mixed → FTE proxy (lever L14) |
| `demographie-secteurs-conventionnels` (✔) | 190,680 | 2010–2025 | effectif × secteur 1 / 2-Optam / 2 / non conventionné | 2026-10-28 | specialists' sector mix |
| `demographie-ages-moyens-part-des-femmes-part-des-plus-de-60-ans` | 593 | 2010–2025 | mean age (F/M), % women, % 60+ — **national only** | 2026-10-20 | sanity check |
| `patientele` (✔) | 45,120 | 2016–2025 | patients uniques, patients médecin traitant | 2026-10-28 | activity per professional (need side) |
| `honoraires` (✔) | 71,040 | 2010–2025 | honoraires sans dépassement, dépassements (totaux, moyens), taux | 2026-10-28 | context |
| `honoraires-detailles` (✔) | 1,351,680 | 2010–2025 | honoraires by category levels 1–3 (actes cliniques/techniques, forfaits) | 2026-10-12 | activity mix, task-shifting baseline |
| `prescriptions` (✔) | 449,280 | 2010–2025 | montants by poste (médicaments, biologie, **kinésithérapie, soins infirmiers**, LPP, IJ, transports) | 2026-10-28 | doctor → kiné/IDE demand link |
| `medecins-optam-annuelle` | 30,240 | 2017– | Optam adhesion by specialty | 2025-01-28 | context |
| `file-active-medgen-annuelle` | 33,120 | 2016– | file active by specialty (despite the id) | 2025-01-28 | patients per specialist |

Not relevant: Risques professionnels (14), GP-only "Accès aux soins" sets
(primo-installés MG, zones sous-dotées MG, patientèle MT MG), Pathologies
(`effectifs` 5.8 M rows = patients by pathology × age × sex × dép — a
**need-side** input for K5, out of this survey's scope).

**API facts (measured 2026-11-13):** no key; headers say
`X-RateLimit-Limit: 10000000` per day (resets 00:00 UTC); CORS `*`.
`/records` returns ≤ 100 rows but supports server-side `group_by` and
aggregates; `/exports/csv|json|parquet` has no row cap.
Latencies: filtered export 0.18 s; national `group_by annee` 0.84 s;
all dép × age × sex for 5 professions, one year (21,684 rows, 1.3 MB) 1.23 s.

### 2. CartoSanté (Geoclip 4.26, ARS / Atlasanté)
A Geoclip app. Two public, unauthenticated endpoints:
- `GC_init.php?lang=fr&obs=main` — JSON config: 72 datasets, 22 territorial
  levels, indicator trees.
- **`GC_tjs.php` — an OGC Table Joining Service** (GetCapabilities,
  DescribeFrameworks, DescribeDatasets, DescribeData, GetData). Frameworks:
  `arm2026, arr2026, bv2012, com2026, cv2026, dep, epci2026, reg2016,
  ze2020`. 46 datasets at commune, 43 at département.
- `GC_listIndics.php?lang=fr&theme=<theme>&tree=A01` lists indicators with
  years, source and the levels each exists at. `GC_indic.php` returns
  metadata and distributions, **not** per-territory values (tested).

No licence statement found in the app's legal notices or the TJS
capabilities (`AccessConstraints: NONE`, `Fees: NONE`). Producer cited per
indicator: FNPS / SNDS (Cnam), DREES–IRDES (APL), INSEE, FINESS, ARS.

| CartoSanté dataset | Professions | Years | Variables | Levels | API |
|---|---|---|---|---|---|
| `infi_popage`, `kine_popage`, `sf_popage`, `dent_popage` (*correction 2026-11-13: `sf_popage` rows don't follow the year × age grid, unusable; see [loader report](2026-11-13-cartosante-commune-loader.md)*) | IDE, MK, SF, CD (liberal) | IDE 2004–25, MK 2005–25, SF 2012–25, CD 2006–25 | count by age band (Total, <40, 40–49, 50–54, 55–59, 60+), % per band, % women | commune → région, plus bv, epci, tds, tv, ze, canton | TJS ✔ |
| `*_popage_b` (×4) | same | same | **patients (bénéficiaires) by age band** | same | TJS ✔ |
| `*_datcom` (×4) | same | same | activity: acts by NGAP code, actifs all year, mean activity, intra-commune consumption share | same | TJS ✔ |
| `*_flux` (×4) | same | same | flows (installations / cessations: **assumed** from the name, not opened) | commune | **not in TJS**; GC_indic only (values not reached) |
| `demo_ps` | **specialists by specialty** (`pra_spe`) | 2020–2025 | denomb_ps, density /100k, 5-yr change | commune → région | TJS ✔ |
| `ps_age` | specialists × age | 2024–2025 | age | ? | not in TJS |
| `offre_ps` | all + **pharmacies** (count, density /10k), IPA libéraux, cabinets secondaires, SSIAD, centres | 2009–2025 | counts, densities, 5-yr change | commune → région | TJS ✔ |
| `apl_inf`, `apl_kine`, `apl_sf`, `apl_cd` | IDE, MK, SF, CD | 2021–2024 | APL (DREES–IRDES) | commune → région | TJS ✔ |
| `zonage_conv` | IDE, MK, SF, CD | current | ARS conventional zoning class per commune | commune | TJS ✔ |
| `z_phie` | pharmacies | current | ARS pharmacy zoning | commune | not in TJS |

Count: 25 relevant, 19 confirmed via TJS.

**Measured (2026-11-13):** département GetData for `kine_popage` 0.27 s,
12,732 rows, all 21 years × 6 age bands. Commune GetData for the same:
**21.9 s, 1.1 MB compressed, 4.39 M rows, 34,877 communes** — fine for a
one-time pull, too slow for live use.
**Quirk ⚑:** GetData rows carry only the territory key and value; year and
age are implicit by position. Order inferred as years ascending
(2005 → 2025) × age bands in DescribeData order. Checked against ameli: the
national ratio is stable unshifted (0.99 → 1.03) and drifts when shifted by a
year (0.88 → 1.00).
**Cross-check vs ameli, kinés, 2024, 100 départements:** CartoSanté 84,518
vs ameli 82,037. Median ratio 1.024 (range 0.989–1.134). From 2014 on,
CartoSanté runs 2–3 % above ameli. Both come from FNPS/SNDS, so the gap is a
counting rule (**assumed**, not checked).

### 3. Atlasanté (catalogue + data services)
- GeoNetwork catalogue `https://catalogue.atlasante.fr/geonetwork/srv/api/search/records/_search`
  (Elasticsearch JSON, POST, no auth) — 0.3 s. CSW endpoint also answers.
- **`https://catalogue.atlasante.fr/api/data/<uuid>?srs=EPSG:4326` returns
  GeoJSON**. Tested on *France – Zonages conventionnels des ARS : sages-femmes,
  infirmiers, dentistes et masseurs-kiné* (uuid `c987d0e2-…`): 36,700
  communes, fields `z_infi, z_kine, z_dent` (classes 1–5, 9; **no `z_sf`
  column**), 6.4 MB, 1.35 s. Use limitation: "Utilisation libre sous
  réserve de mentionner la source … et la date de sa dernière mise à jour".
  Metadata dated 2014 / 2019 → **vintage unclear ⚑**.
- Other catalog hits: *Métropole – Territoires de santé des ARS* (WFS listed,
  not tested), FINESS officines cat. 620, RPPS (ASIP), Insee projections,
  IGN EPCI/communes, ARS AURA "bassins de santé intermédiaires". WFS hosts:
  `carto.atlasante.fr/cgi-bin/mapservwfs`, `datacarto.atlasante.fr/wfs`.
  Count: 2 relevant (zonage, territoires de santé), 1 confirmed.

### 4. Source × profession × grain × access: what should be primary

| Profession | Dép × age × sex (projection base) | Commune / groups (ARS view, current state) | Access indicator | Zoning |
|---|---|---|---|---|
| Médecins spécialistes | **DREES RPPS** (all modes). ameli API for liberal, 23 specialties, 2010–25 | **CartoSanté `demo_ps`** (specialty × commune, 2020–25, no age) | none open (no specialist APL) | — |
| Sages-femmes | DREES RPPS; ameli liberal | **CartoSanté `sf_popage`** (age bands, 2012–25) | CartoSanté `apl_sf` = DREES APL | CartoSanté `zonage_conv` |
| Chirurgiens-dentistes | DREES RPPS; ameli liberal (omni / ODF) | **CartoSanté `dent_popage`** | `apl_cd` | Atlasanté GeoJSON / `zonage_conv` |
| Pharmaciens | **DREES RPPS only** (neither ameli nor CartoSanté counts pharmacists) | pharmacies only (CartoSanté `offre_ps.nb_phie`; FINESS cat. 620) → **gap** | — | `z_phie` |
| Masseurs-kinés | DREES RPPS (series break 2016→17); ameli liberal | **CartoSanté `kine_popage`** (2005–25) | `apl_kine` | GeoJSON / `zonage_conv` |
| Infirmiers | DREES RPPS + salaried raking; ameli liberal to 2025 | **CartoSanté `infi_popage`** (2004–25) | `apl_inf` | GeoJSON / `zonage_conv` |
| Population | Omphale (Insee) | CartoSanté `pop_sexe_age` (RP 1999–2023, commune) or Insee | — | — |

Example queries (all run 2026-11-13; samples in
`artifacts/ameli_api_scout/`):

```text
# ameli: kinés per département, 2024 (CSV, 0.18 s) → kines_dep_2024.csv
https://data.ameli.fr/api/explore/v2.1/catalog/datasets/demographie-effectifs-et-les-densites/exports/csv?select=departement,libelle_departement,effectif,densite&where=profession_sante='Masseurs-kinésithérapeutes' and annee=date'2024' and libelle_classe_age='Tout âge' and libelle_sexe='tout sexe'&order_by=departement

# ameli: national kiné series, aggregated server-side (0.84 s)
…/records?select=annee,sum(effectif) as n&where=profession_sante='Masseurs-kinésithérapeutes' and libelle_classe_age='Tout âge' and libelle_sexe='tout sexe' and departement!='999'&group_by=annee

# CartoSanté TJS: kinés by département × year × age band (0.27 s) → cartosante_kines_dep_2005_2025.csv
https://cartosante.atlasante.fr/GC_tjs.php?SERVICE=TJS&VERSION=1.0&REQUEST=GetData&FrameworkURI=http://insee.fr/cog/dep&DatasetURI=kine_popage&Attributes=eft
#   swap FrameworkURI for http://insee.fr/cog/com2026 | epci2026 | bv2012 | reg2016
#   list datasets: REQUEST=DescribeDatasets&FrameworkURI=…; columns: REQUEST=DescribeData&…&DatasetURI=…

# Atlasanté: conventional zoning by commune (GeoJSON, no geometry, 1.35 s)
https://catalogue.atlasante.fr/api/data/c987d0e2-e99c-4a11-a3a4-aa81de6aa416?srs=EPSG:4326
```

## How
- **Data:** data.ameli.fr catalog and dataset metadata (modified dates
  above). CartoSanté `GC_init.php` (header date 2026-11-05) and TJS.
  Atlasanté GeoNetwork.
- **Method:** found the endpoints from the catalog and the app's JS
  (`gc_core.js`). Ran one query per endpoint with `curl` and timed it.
  Cross-checked kinés between ameli and CartoSanté. No bulk download except
  the 6.4 MB zoning GeoJSON (kept in the scratchpad, not the repo).

## ⚑ What could make it wrong
- **The TJS row order is inferred**, not labelled. If Geoclip changes it, years
  and ages shift silently. Re-check with a known total on every pull (for
  example, 2025 France kinés).
- CartoSanté has **no stated licence**. Producers are cited per indicator, but
  reuse terms are unclear. Cite "CartoSanté (Atlasanté), source FNPS/SNDS,
  extracted 2026-11-13" until it is clarified.
- CartoSanté and ameli differ by 2–3 % for kinés. Do not mix them in one
  series without a ratio adjustment.
- Commune counts are small: the ±1/√N noise from the ARS decision applies.
- The zoning vintage is unknown, and the file has no `z_sf` column despite its
  title.
- `*_flux` datasets (installations/cessations?) were not reached; their content
  is **assumed** from the name.

## → What it changes
- **ARS commune decision / open.md "Commune data"**: the liberal stock for 4
  professions at commune level, with age bands, is available by API. Not
  needed: the RPPS directory, for those 4. Still needed: the directory (or
  DREES), for pharmacists and salaried staff.
- **open.md "Which ARS groupings"**: CartoSanté already serves bv, epci,
  territoire de démocratie sanitaire and territoire de vie-santé, and the
  ARS zoning per commune. The groups can be chosen from data we can fetch.
- **Need side (K5)**: `*_popage_b` (patients by age band, by commune) and
  ameli `patientele` are open use-rate inputs.
- **Recompute < 2 s**: APIs go in a one-time ETL to parquet, never in the
  recompute loop (commune TJS pull = 22 s).

## ? Next
| Item | Cost |
|---|---|
| Loader: CartoSanté TJS → `data/processed/stock_commune.parquet` (4 professions × age × year, + `demo_ps`), with the total check | ~1 h |
| Reach `*_flux` values (installations/cessations by commune) — would give entry/exit hazards directly | ~45 min |
| Clarify CartoSanté licence (contact / legal notice) | 15 min + wait |
| Pharmacists by commune: RPPS directory extract (size first) | ~1 h |
