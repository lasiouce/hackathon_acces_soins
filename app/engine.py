"""Algorithm-agnostic estimation engine for the UI.

Takes any class registered in sante.estimators.ESTIMATORS (interface: name, assumptions, fit(t, fit_years, origin),
predict(target) -> headcount per (profession, dep)) and, for the user's selection:
  - builds the stock table (profession × dep × sex × age_lo × year -> n) with the UI's sector/specialty filters,
  - fits at the latest data year on the last `fit_len` years and predicts every year to the horizon,
  - computes an EMPIRICAL band by self-backtest: refit the same estimator h years earlier, predict the latest
    year, and take the 10–90 % range of relative error over départements. No estimator-specific code.
Adding an estimator to ESTIMATORS makes it appear here, with its band, without touching the app.
"""
import sys

import numpy as np
import pandas as pd

import data as D
import levers as LV

sys.path.insert(0, str(D.ROOT))
from sante.estimators import ESTIMATORS  # noqa: E402
from sante.model import KEYS  # noqa: E402

MIN_N = 30            # départements with fewer professionals at the backtest origin are left out of the band
MAX_BACKTEST_H = 8    # longest horizon measured by self-backtest; beyond, the band is extrapolated
DEFAULT = "StockFlowLocal"

# French UI labels; the library's own name/assumptions are the fallback, so new estimators show up untranslated.
LABELS_FR = {
    "StockFlowNational": ("Stock-flux, taux nationaux",
                          "Vieillissement par tranche d'âge de 5 ans ; un taux de maintien net par profession, sexe et "
                          "âge, commun à toute la France (plafonné à 1) ; entrées = flux annuel constant, égal à la "
                          "moyenne de la fenêtre d'ajustement."),
    "StockFlowLocal": ("Stock-flux, taux locaux",
                       "Comme « taux nationaux », mais chaque département a ses propres taux, rapprochés des taux "
                       "nationaux quand les effectifs sont faibles (poids a priori : 200 personnes). Entrées = flux "
                       "annuel constant."),
    "StockFlowLocalTrendEntries": ("Stock-flux, taux locaux, entrées tendancielles",
                                   "Comme « taux locaux », mais les entrées annuelles de chaque département "
                                   "prolongent leur tendance linéaire passée (ex. hausse des quotas)."),
    "NationalTimesTrendShares": ("Total national × parts tendancielles",
                                 "Total national issu du modèle stock-flux ; la part de chaque département est "
                                 "prolongée selon sa tendance linéaire passée."),
    "Persistence": ("Persistance", "Rien ne change : chaque territoire garde son dernier effectif observé."),
    "LinearTrend": ("Tendance linéaire", "L'effectif de chaque territoire prolonge sa tendance linéaire passée "
                                         "(fenêtre d'ajustement) ; pas d'âges, pas de leviers."),
}
REGISTRY = {E.__name__: E for E in ESTIMATORS}


def label(key):
    return LABELS_FR.get(key, (REGISTRY[key].name, ""))[0]


def assumptions(key):
    return LABELS_FR.get(key, ("", REGISTRY[key].assumptions))[1] or REGISTRY[key].assumptions


def table(stock_raw: pd.DataFrame, prof_key: str, sector: str, specialty: str | None) -> pd.DataFrame:
    """Stock table in the estimators' schema, filtered like the UI selection."""
    _, prof, spec_rule = D.PROFESSIONS[prof_key]
    s = stock_raw[stock_raw["profession"] == prof]
    if prof == "kines":
        s = s[s["source"] == "RPPS"]  # ADELI years break the series (same rule as sante.model.stock_table)
    if spec_rule == "non_mg":
        s = s[s["specialty"] != "Médecine générale"]
        if specialty:
            s = s[s["specialty"] == specialty]
    if sector == "liberal":
        s = s[s["mode3"] == "liberal_mixte"]
    s = s[~s["dep"].isin(["999", "20"])]
    return s.groupby(KEYS + ["age_lo", "year"], as_index=False)["n"].sum()


def _fit_window(t, origin, fit_len):
    return (max(int(t["year"].min()), origin - fit_len + 1), origin)


def run(key: str, t: pd.DataFrame, fit_len: int = 6, horizon: int = D.HORIZON, origin: int | None = None,
        prof_key: str = "", levers: dict | None = None):
    """-> (dep × year headcount table, observed through origin then predicted; origin; levers without effect).

    `levers` (see app/levers.py): flow levers need an estimator with fitted flow terms; output levers apply to all.
    """
    origin = origin or int(t["year"].max())
    est = REGISTRY[key]().fit(t[t["year"] <= origin], _fit_window(t, origin, fit_len), origin)
    obs = t.groupby(["dep", "year"])["n"].sum().unstack("year")
    obs = obs[[y for y in obs.columns if y <= origin]]
    act = LV.active(levers or {})
    flow = {k: v for k, v in act.items() if LV.BY_KEY[k].kind == "flow"}
    ignored = []
    if LV.has_flows(est):  # one multi-year projection; equals est.predict year by year (diff 0, 6x faster)
        fut = LV.project_flow(est, prof_key, horizon, flow)
    else:
        ignored = list(flow)
        fut = pd.DataFrame({y: est.predict(y).groupby(level="dep").sum() for y in range(origin + 1, horizon + 1)})
    fut = fut * act.get("activity", 1.0)
    return pd.concat([obs, fut], axis=1).fillna(0.0), origin, ignored


def band_table(key: str, t: pd.DataFrame, fit_len: int = 6, origin: int | None = None) -> pd.DataFrame:
    """Self-backtest: for each measurable horizon h, 10/50/90 % quantiles of pred/actual − 1 over départements."""
    origin = origin or int(t["year"].max())
    first = int(t["year"].min())
    actual = t[t["year"] == origin].groupby("dep")["n"].sum()
    rows = []
    for h in range(1, MAX_BACKTEST_H + 1):
        o = origin - h
        if o - first < 2:  # need at least 3 years to fit
            break
        est = REGISTRY[key]().fit(t[t["year"] <= o], _fit_window(t, o, fit_len), o)
        pred = est.predict(origin).groupby(level="dep").sum()
        base = t[t["year"] == o].groupby("dep")["n"].sum()
        keep = base.index[base >= MIN_N].intersection(actual.index)
        r = (pred.reindex(keep) / actual[keep] - 1).dropna()
        rows.append(dict(h=h, q10=r.quantile(0.1), q50=r.quantile(0.5), q90=r.quantile(0.9), n_dep=len(r),
                         backtest=f"{o}→{origin}"))
    return pd.DataFrame(rows).set_index("h")


def band_for(bt: pd.DataFrame, h: int) -> tuple[float, float, str]:
    """(q10, q90, provenance) for horizon h; linear extrapolation in h beyond the longest measured horizon."""
    if bt.empty:
        return np.nan, np.nan, "aucune mesure"
    if h in bt.index:
        r = bt.loc[h]
        return r.q10, r.q90, f"mesurée ({r.backtest}, {int(r.n_dep)} dép.)"
    hm = int(bt.index.max())
    k = h / hm
    return bt.loc[hm, "q10"] * k, bt.loc[hm, "q90"] * k, f"extrapolée depuis {hm} ans"


def interval(values: pd.DataFrame, origin: int, bt: pd.DataFrame):
    """Lower/upper bounds for projected columns: actual ∈ [pred/(1+q90), pred/(1+q10)]."""
    lo, hi = values.copy(), values.copy()
    for y in values.columns:
        if y > origin:
            q10, q90, _ = band_for(bt, y - origin)
            lo[y], hi[y] = values[y] / (1 + q90), values[y] / (1 + q10)
    return lo, hi
