"""Data layer for the demo UI: aggregates, geometry, population and densities.

Reads data/processed/{stock,population}.parquet (written by sante/load.py) and
app/assets/departements-avec-outre-mer.geojson (gregoiredavid/france-geojson,
derived from IGN Admin Express). Aggregates are cached in app/cache/.

Projections come from app/engine.py (any estimator in sante.estimators).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
ASSETS = Path(__file__).resolve().parent / "assets"
CACHE = Path(__file__).resolve().parent / "cache"

HORIZON = 2040
POP_FIRST_YEAR = 2018  # Omphale 2022 starts in 2018; earlier years reuse 2018 (assumed)

SOURCES = {
    "stock": "DREES, « La démographie des professionnels de santé depuis 2012 » (RPPS / ADELI / SNDS), millésime 2026-07-02",
    "population": "Insee, Omphale 2022, projections départementales (scénarios central, haut, bas)",
    "geometry": "france-geojson (G. David), d'après IGN Admin Express — départements avec outre-mer",
}

# UI key -> (label, stock profession, specialty filter)
PROFESSIONS = {
    "specialistes": ("Médecins spécialistes (hors médecine générale)", "medecins", "non_mg"),
    "sages-femmes": ("Sages-femmes", "sages-femmes", None),
    "dentistes": ("Chirurgiens-dentistes", "dentistes", None),
    "pharmaciens": ("Pharmaciens", "pharmaciens", None),
    "kines": ("Masseurs-kinésithérapeutes", "kines", None),
    "infirmiers": ("Infirmiers (libéraux seulement, SNDS)", "infirmiers-liberaux", None),
}
SPECIALTIES = ["Anesthésie-Réanimation", "Cardiologie", "Chirurgie", "Dermatologie", "Gastro-entérologie",
               "Gynécologie", "Ophtalmologie", "Oto-rhino-laryngologie", "Pédiatrie", "Plateaux techniques",
               "Pneumologie", "Psychiatrie", "Autre spécialité"]
SECTORS = {"liberal": "Libéral et mixte", "tous": "Tous modes d'exercice"}

REGIONS = {
    "01": "Guadeloupe", "02": "Martinique", "03": "Guyane", "04": "La Réunion", "06": "Mayotte",
    "11": "Île-de-France", "24": "Centre-Val de Loire", "27": "Bourgogne-Franche-Comté", "28": "Normandie",
    "32": "Hauts-de-France", "44": "Grand Est", "52": "Pays de la Loire", "53": "Bretagne",
    "75": "Nouvelle-Aquitaine", "76": "Occitanie", "84": "Auvergne-Rhône-Alpes", "93": "Provence-Alpes-Côte d'Azur",
    "94": "Corse",
}



def _agg_stock() -> pd.DataFrame:
    """profession × specialty × sector × dep × year -> n. Cached."""
    f = CACHE / "stock_agg.parquet"
    src = PROCESSED / "stock.parquet"
    if f.exists() and f.stat().st_mtime > src.stat().st_mtime:
        return pd.read_parquet(f)
    s = pd.read_parquet(src, columns=["profession", "specialty", "mode3", "dep", "dep_name", "region", "year", "n"])
    s = s[~s["dep"].isin(["999", "20"])]  # abroad / unsplit Corsica code
    s["sector"] = np.where(s["mode3"] == "liberal_mixte", "liberal", "autre")
    agg = s.groupby(["profession", "specialty", "sector", "dep", "year"], as_index=False)["n"].sum()
    CACHE.mkdir(exist_ok=True)
    agg.to_parquet(f, index=False)
    return agg


def _agg_pop() -> pd.DataFrame:
    f = CACHE / "pop_agg.parquet"
    src = PROCESSED / "population.parquet"
    if f.exists() and f.stat().st_mtime > src.stat().st_mtime:
        return pd.read_parquet(f)
    p = pd.read_parquet(src, columns=["scenario", "year", "dep", "pop"])
    agg = p.groupby(["scenario", "dep", "year"], as_index=False)["pop"].sum()
    agg.to_parquet(f, index=False)
    return agg


def load_all() -> dict:
    stock = _agg_stock()
    pop = _agg_pop() if (PROCESSED / "population.parquet").exists() else None
    s = pd.read_parquet(PROCESSED / "stock.parquet", columns=["profession", "dep", "dep_name", "region"])
    deps = (s[s.profession != "medecins"].drop_duplicates("dep").set_index("dep")[["dep_name", "region"]])
    deps = deps.drop(index=[d for d in ["999", "20"] if d in deps.index])
    return {"stock": stock, "pop": pop, "deps": deps}


def geometry() -> dict:
    """Département GeoJSON with coordinates rounded to ~1 km to lighten each map redraw."""
    f = CACHE / "deps_light.geojson"
    if f.exists():
        return json.loads(f.read_text())
    g = json.loads((ASSETS / "departements-avec-outre-mer.geojson").read_text())

    def thin(ring):
        out = []
        for x, y in ring:
            p = [round(x, 2), round(y, 2)]
            if not out or p != out[-1]:
                out.append(p)
        return out if len(out) >= 4 else ring

    for feat in g["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            geom["coordinates"] = [thin(r) for r in geom["coordinates"]]
        else:
            geom["coordinates"] = [[thin(r) for r in poly] for poly in geom["coordinates"]]
    CACHE.mkdir(exist_ok=True)
    f.write_text(json.dumps(g, separators=(",", ":")))
    return g






def population(pop: pd.DataFrame, scenario: str, horizon: int = HORIZON) -> pd.DataFrame:
    """dep × year population, 2012..horizon; years before 2018 reuse 2018 (assumed)."""
    p = pop[pop["scenario"] == scenario].pivot(index="dep", columns="year", values="pop")
    for y in range(2012, POP_FIRST_YEAR):
        p[y] = p[POP_FIRST_YEAR]
    return p[sorted(c for c in p.columns if c <= horizon)]


def density(n: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    """Professionals per 100,000 inhabitants, dep × year."""
    years = [y for y in n.columns if y in pop.columns]
    idx = n.index.intersection(pop.index)
    return n.loc[idx, years] / pop.loc[idx, years] * 1e5


def national_density(n: pd.DataFrame, pop: pd.DataFrame, deps: list | None = None) -> pd.Series:
    years = [y for y in n.columns if y in pop.columns]
    idx = n.index.intersection(pop.index)
    if deps is not None:
        idx = idx.intersection(deps)
    return n.loc[idx, years].sum() / pop.loc[idx, years].sum() * 1e5
