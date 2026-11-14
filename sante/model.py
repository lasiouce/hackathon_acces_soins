"""Stock-flow projection (H1) and naive baselines (H0).

Annual cohort-component model on 5-year age bands, per profession x département x sex:
  N[a](t+1) = s[a] * ( (4/5) N[a](t) + (1/5) N[a-1](t) )     inner bands
  N[top](t+1) = s[top] * ( N[top](t) + (1/5) N[top-1](t) )    open top band
  + I[a]                                                      absolute yearly net inflow (entries)
s[a] <= 1 is an annual retention rate, estimated by least squares on the fit window. Where the raw
ratio exceeds 1 (the entry bands, mostly 25-39), s is capped at 1 and the excess becomes an absolute
inflow I = mean net inflow per year over the fit window, per cell. (Fix 2026-11-13: an uncapped ratio
> 1 made entries proportional to the stock, so they compounded: +3.5 %/yr vs +1.5 %/yr observed.) Pooled: one s per profession x sex x age (national), applied to each département's
pyramid. Local: one s per département, shrunk toward the national rate.
"""
import numpy as np
import pandas as pd

KEYS = ["profession", "dep", "sex"]


def stock_table(professions: list[str] | None = None) -> pd.DataFrame:
    """profession x dep x sex x age_lo x year -> n, with médecins split into specialistes (GPs excluded)."""
    s = pd.read_parquet("data/processed/stock.parquet")
    s = s[(s.profession != "kines") | (s.source == "RPPS")]           # ADELI years break the series
    med = s.profession == "medecins"
    s = s[~med | (s.specialty != "Médecine générale")].copy()
    s.loc[med, "profession"] = "specialistes"
    try:
        n = pd.read_parquet("data/processed/stock_nurses_salaried.parquet")
        s = pd.concat([s, n], ignore_index=True)
    except FileNotFoundError:
        pass
    s = s[~s.dep.isin(["999", "20"])]
    t = s.groupby(KEYS + ["age_lo", "year"], as_index=False)["n"].sum()
    return t if professions is None else t[t.profession.isin(professions)]


def _cube(t: pd.DataFrame):
    """-> array [cell, age, year], cell index frame, ages, years."""
    ages, years = np.sort(t.age_lo.unique()), np.sort(t.year.unique())
    wide = t.pivot_table(index=KEYS, columns=["age_lo", "year"], values="n", aggfunc="sum", fill_value=0)
    wide = wide.reindex(columns=pd.MultiIndex.from_product([ages, years]), fill_value=0)
    return wide.to_numpy().reshape(len(wide), len(ages), len(years)), wide.index.to_frame(index=False), ages, years


def _inflow(N):
    """Expected next-year stock before retention, per band: shape like N[..., :-1]."""
    cur, prev = N[:, :, :-1], np.roll(N[:, :, :-1], 1, axis=1)
    prev[:, 0] = 0
    base = 0.8 * cur + 0.2 * prev
    base[:, -1] = cur[:, -1] + 0.2 * N[:, -2, :-1]
    return base


def fit_rates(t: pd.DataFrame, fit_years: tuple[int, int], shrink: float | None = None, inflow_trend: bool = False,
              inflow_recent: int | None = None):
    """Net retention rates. shrink=None -> pooled national; shrink=k -> local, k = prior weight in persons."""
    N, cells, ages, years = _cube(t)
    yi = (years >= fit_years[0]) & (years <= fit_years[1])
    Nf = N[:, :, yi]
    base, nxt = _inflow(Nf), Nf[:, :, 1:]
    num, den = nxt.sum(axis=2), base.sum(axis=2)                       # [cell, age]
    grp = cells.groupby(["profession", "sex"]).ngroup().to_numpy()
    nat = np.zeros_like(num)
    for g in np.unique(grp):
        m = grp == g
        nat[m] = num[m].sum(0) / np.maximum(den[m].sum(0), 1e-9)
    r = nat if shrink is None else (num + shrink * nat) / (den + shrink)   # empirical-Bayes style shrinkage
    s = np.minimum(r, 1.0)
    e = nxt - s[:, :, None] * base                                       # yearly net inflow series [cell, age, t]
    inflow = np.where(r > 1.0, (e if inflow_recent is None else e[:, :, -inflow_recent:]).mean(axis=2), 0.0)
    slope = np.zeros_like(inflow)
    if inflow_trend:                                                     # entries keep their fit-window linear trend
        tt = np.arange(e.shape[2]) - (e.shape[2] - 1) / 2
        slope = np.where(r > 1.0, (e * tt).sum(axis=2) / (tt ** 2).sum(), 0.0)
        inflow = inflow + slope * (e.shape[2] - 1) / 2                   # level at the end of the fit window
    return s, inflow, slope


def project(t: pd.DataFrame, origin: int, horizon: int, rates, inflow_scale=None) -> pd.DataFrame:
    """rates = (s, inflow, slope) from fit_rates. inflow_scale: callable(cells frame, h) -> per-cell multiplier."""
    s, inflow, slope = rates
    N, cells, ages, years = _cube(t)
    x = N[:, :, list(years).index(origin)].copy()
    out = []
    for h in range(1, horizon + 1):
        prev = np.roll(x, 1, axis=1)
        prev[:, 0] = 0
        base = 0.8 * x + 0.2 * prev
        base[:, -1] = x[:, -1] + 0.2 * x[:, -2]
        k = 1.0 if inflow_scale is None else inflow_scale(cells, h)[:, None]
        x = np.maximum(s * base + k * (inflow + slope * h), 0)
        out.append(pd.DataFrame(x, columns=ages).assign(**cells, year=origin + h))
    return pd.concat(out).melt(id_vars=KEYS + ["year"], var_name="age_lo", value_name="n")


def baseline(totals: pd.DataFrame, origin: int, target: int, fit_years: tuple[int, int], kind: str) -> pd.Series:
    """totals: profession x dep -> year columns. persistence or linear trend on the fit window."""
    if kind == "persistence":
        return totals[origin]
    yrs = [y for y in totals.columns if fit_years[0] <= y <= fit_years[1]]
    X = np.array(yrs, float)
    Y = totals[yrs].to_numpy()
    slope = ((X - X.mean()) * (Y - Y.mean(1, keepdims=True))).sum(1) / ((X - X.mean()) ** 2).sum()
    return pd.Series(np.maximum(Y.mean(1) + slope * (target - X.mean()), 0), index=totals.index)
