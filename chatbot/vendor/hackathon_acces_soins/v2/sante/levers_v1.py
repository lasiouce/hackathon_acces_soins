"""Policy levers wired through the engine (ids follow docs/lab/levers.md).

Two kinds:
  flow    perturbs the fitted flow terms of estimators that expose them (`rates` = (s, inflow, slope) from
          sante.model.fit_rates: the stock-flow family). Entry levers act after the training lag L_p, by
          projecting in two segments. Estimators without these terms are reported as unaffected.
  output  scales the projected supply of any estimator (e.g. activity rate -> full-time equivalents).
Every lever is the identity at its default value, so the default scenario equals the baseline.
Effect sizes are `assumed` unless stated; the mechanism and its source come from the registry.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

# Training lag L_p in years (derivation workforce-projection-model.md, `assumed`, to verify)
LAG = {"specialistes": 10, "pharmaciens": 6, "dentistes": 6, "sages-femmes": 5, "kines": 5, "infirmiers": 3}
ENTRY_ID = {"specialistes": "L01", "pharmaciens": "L02", "dentistes": "L03", "sages-femmes": "L04",
            "kines": "L05", "infirmiers": "L06"}
CUMUL_SHARE = 0.10  # share of liberal/mixed doctors in cumul emploi-retraite, 2018 (DREES ER n° 1097); others assumed


@dataclass(frozen=True)
class Lever:
    key: str
    ids: str
    name: str
    kind: str          # "flow" or "output"
    default: float
    lo: float
    hi: float
    step: float
    unit: str
    mechanism: str
    source: str


LEVERS = [
    Lever("entries", "L01–L06", "Entrées en formation (numerus apertus, quotas)", "flow", 1.0, 0.7, 1.5, 0.05,
          "× niveau actuel",
          "Multiplie le flux annuel d'entrées à partir de l'origine + durée de formation L_p.",
          "Loi OTSS 2019 ; arrêtés d'objectifs 2021 et 2026. L_p : hypothèse."),
    Lever("retirement", "L09", "Âge de départ à la retraite", "flow", 0.0, -1.0, 2.0, 0.5, "années",
          "Décale les sorties des tranches 60–64 et 65–69 : sorties × (1 − Δ/5).",
          "Loi n° 2023-270 ; LFSS 2026. Passage âge légal → sorties libérales : hypothèse."),
    Lever("cumul", "L10", "Cumul emploi-retraite", "flow", 1.0, 0.5, 2.0, 0.1, "× part 2018",
          f"Sorties à 65 ans et plus × (1 − {CUMUL_SHARE:.0%} × (k − 1)).",
          "DREES ER n° 1097 (2018) pour les médecins ; autres professions : hypothèse."),
    Lever("activity", "L14", "Taux d'activité", "output", 1.0, 0.8, 1.1, 0.01, "× actuel",
          "Convertit les effectifs projetés en équivalents temps plein : offre × α.",
          "DREES Dossiers n° 76 (2021), « à comportements constants ». Valeur de α : hypothèse."),
]
BY_KEY = {lv.key: lv for lv in LEVERS}


def defaults():
    return {lv.key: lv.default for lv in LEVERS}


def active(values: dict) -> dict:
    return {k: v for k, v in values.items() if k in BY_KEY and v != BY_KEY[k].default}


def _band_mask(ages, lo, hi=None):
    a = np.asarray(ages)
    return (a >= lo) & (a <= (hi if hi is not None else a.max()))


def perturb_retention(s: np.ndarray, ages, values: dict) -> np.ndarray:
    """Retention s (≤ 1) per [cell, age] -> perturbed copy. Exit rate e = 1 − s."""
    e = 1.0 - s
    k = np.ones(len(ages))
    d = values.get("retirement", 0.0)
    if d:
        k[_band_mask(ages, 60, 65)] *= max(0.0, 1.0 - d / 5.0)
    c = values.get("cumul", 1.0)
    if c != 1.0:
        k[_band_mask(ages, 65)] *= max(0.0, 1.0 - CUMUL_SHARE * (c - 1.0))
    return 1.0 - e * k[None, :]


def has_flows(est) -> bool:
    return hasattr(est, "rates") and isinstance(est.rates, tuple) and len(est.rates) == 3


def project_flow(est, prof_key: str, horizon: int, values: dict) -> pd.Series:
    """Scenario projection for a stock-flow estimator: dep × year headcount for origin+1..horizon."""
    from sante.model import KEYS, _cube, project  # sante is on sys.path via engine

    s, inflow, slope = est.rates
    _, _, ages, _ = _cube(est.t[est.t.year == est.origin])
    s2 = perturb_retention(s, ages, values)
    m, lag, H = values.get("entries", 1.0), LAG.get(prof_key, 0), horizon - est.origin
    if m == 1.0 or lag >= H:
        segs = [(est.t, est.origin, H, (s2, inflow, slope))]
        out = [project(*seg) for seg in segs]
    else:
        out = []
        if lag > 0:
            first = project(est.t, est.origin, lag, (s2, inflow, slope))
            out.append(first)
            t2 = first[first.year == est.origin + lag].astype({"age_lo": int})
        else:
            t2 = est.t[est.t.year == est.origin]
        out.append(project(t2[KEYS + ["age_lo", "year", "n"]], est.origin + lag, H - lag,
                           (s2, (inflow + slope * lag) * m, slope * m)))
    p = pd.concat(out)
    return p.groupby(["dep", "year"])["n"].sum().unstack("year")
