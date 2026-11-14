"""Training pipeline -> national cohort index of yearly entries, per profession.

Source: team-provided DREES enrolment files (data/raw/990_drees_mmop2_f.xlsx sheet Feuil1, 2020-2024;
data/raw/990_drees_mmop2_2526.xlsx, 2025). Students counted by diploma x year of study x academic year.
A cohort in year of study k in academic year y is expected to start working in y + (last_k + 1 - k).
Each year-of-study series is divided by its own mean (removes attrition and DES-length level differences),
then the index for an entry year is the mean of the relative estimates available for it.

Clean cohorts only:
  specialistes : DES MEDECINE year 4 only (years 1-3 hold general practice; years 5-6 grow with the
                 2017 DES-length reform, not with cohort size)
  dentistes    : DE DOCTEUR EN CHIRURGIE DENTAIRE years 2-6
  pharmaciens  : DE DOCTEUR EN PHARMACIE years 2-6
Other professions have no pipeline data here: index = None.
"""
from functools import lru_cache

import pandas as pd

RAW = "data/raw"
SPEC = {  # profession -> (diploma, years of study used, last year of study)
    "specialistes": ("DES MEDECINE", [4], 5),          # year 4 only: DES lengths changed after 2017
    "dentistes": ("DE DOCTEUR EN CHIRURGIE DENTAIRE", [2, 3, 4, 5, 6], 6),
    "pharmaciens": ("DE DOCTEUR EN PHARMACIE", [2, 3, 4, 5, 6], 6),
}


@lru_cache
def enrolments() -> pd.DataFrame:
    a = pd.read_excel(f"{RAW}/990_drees_mmop2_f.xlsx", sheet_name="Feuil1", engine="calamine")
    b = pd.read_excel(f"{RAW}/990_drees_mmop2_2526.xlsx", sheet_name=0, engine="calamine")
    b = b[b.ANNEE.astype(str) != "Inscriptions"]
    df = pd.concat([a, b])[["ANNEE", "type_de_diplome", "année_dans_le_diplôme", "Inscriptions"]]
    df = df.assign(year=pd.to_numeric(df.ANNEE, errors="coerce"),
                   k=pd.to_numeric(df["année_dans_le_diplôme"], errors="coerce"),
                   n=pd.to_numeric(df.Inscriptions, errors="coerce"))      # "-" (suppressed) -> NaN
    return df.dropna(subset=["year", "k"]).groupby(["type_de_diplome", "k", "year"]).n.sum().reset_index()


@lru_cache
def cohort_index(profession: str) -> pd.Series | None:
    """entry year -> expected cohort size (students), or None if no pipeline data."""
    if profession not in SPEC:
        return None
    diploma, ks, last = SPEC[profession]
    e = enrolments()
    e = e[(e.type_de_diplome == diploma) & e.k.isin(ks) & (e.n > 0)]
    est = e.assign(entry=e.year + (last + 1 - e.k))
    est["rel"] = est.n / est.groupby("k").n.transform("mean")          # each year of study on its own scale
    return est.groupby("entry").rel.mean().rename("cohort")             # relative index (mean ~1)


def scale(profession: str, origin: int, horizon: int) -> list[float]:
    """Multiplier on yearly entries for origin+1..origin+horizon, relative to the origin's cohort.
    Reference = the origin cohort, or the first known cohort after it. Years past the last known cohort hold
    the last known ratio; no data -> 1.0."""
    c = cohort_index(profession)
    if c is None or c.index.max() <= origin:
        return [1.0] * horizon
    ref = c[origin] if origin in c.index else c[c.index > origin].iloc[0]   # first known cohort after origin
    out, last = [], 1.0
    for h in range(1, horizon + 1):
        y = origin + h
        last = c[y] / ref if y in c.index else last
        out.append(float(last))
    return out
