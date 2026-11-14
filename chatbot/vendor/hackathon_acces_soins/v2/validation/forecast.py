"""Axe 3, niveau 1 : banc de prévision à origines glissantes (protocole N1, SHA-256 eb527ecb06a0…).

Tout estimateur à l'interface fit(t, fit_years, origin) / predict(target) -> Series (profession, territoire).
  design(t)                       la grille pré-enregistrée (origines, horizons) par profession
  bench(estimators, t, grid)      erreurs par territoire, une ligne par (estimateur, profession, origine, h, territoire)
  verdict(errors, candidate)      critère principal : MAPE dép. à h = 5, IC bootstrap de l'écart à la meilleure naïve
Rien n'est lancé ici : main() est volontairement absent tant que le jumeau et le périmètre « privé » ne sont pas figés.
"""
import numpy as np
import pandas as pd

HORIZONS = (1, 3, 5, 8, 10)
MIN_FIT, MIN_N, H_MAIN = 5, 30, 5
SEED, BOOT = 20261114, 2000
FIRST = {"kines": 2017}          # rupture de série RPPS 2016 -> 2017


def design(t: pd.DataFrame) -> list[tuple]:
    """(profession, (début, origine), origine, [cibles]) : fenêtre élargie ≥ MIN_FIT ans, cible ≤ dernière année."""
    grid = []
    for prof, yrs in t.groupby("profession").year:
        first, last = FIRST.get(prof, int(yrs.min())), int(yrs.max())
        for o in range(first + MIN_FIT - 1, last):
            targets = [o + h for h in HORIZONS if o + h <= last]
            if targets:
                grid.append((prof, (first, o), o, targets))
    return grid


def bench(estimators: dict, t: pd.DataFrame, grid: list, terr: str = "dep") -> pd.DataFrame:
    rows = []
    for prof, fit, origin, targets in grid:
        tp = t[t.profession == prof]
        tot = tp.groupby(["profession", terr, "year"]).n.sum().unstack("year")
        n0 = tot[origin]
        for name, E in estimators.items():
            est = E().fit(tp[tp.year <= origin], fit, origin)
            for target in targets:
                pred = est.predict(target).reindex(tot.index)
                rows.append(pd.DataFrame({"model": name, "origin": origin, "h": target - origin,
                                          "n_origin": n0, "actual": tot[target], "pred": pred}).reset_index())
    e = pd.concat(rows, ignore_index=True).rename(columns={terr: "territory"})
    e["ape"] = 100 * (e.pred - e.actual).abs() / e.actual
    return e


def _mape_by_cell(e: pd.DataFrame, deps=None) -> pd.Series:
    if deps is not None:
        e = e[e.territory.isin(deps)]
    return e.groupby(["model", "profession", "origin"]).ape.mean().groupby("model").mean()


def verdict(e: pd.DataFrame, candidate: str, naives=("naive_persistance", "naive_tendance")) -> dict:
    m = e[(e.h == H_MAIN) & (e.n_origin >= MIN_N)]
    pooled = _mape_by_cell(m)
    best = min(naives, key=lambda k: pooled[k])
    deps = m.territory.unique()
    rng = np.random.default_rng(SEED)
    # même tirage de départements pour toutes les cellules (corrélation conservée)
    boot = []
    for _ in range(BOOT):
        s = rng.choice(deps, len(deps))
        mm = m.set_index("territory").loc[s].reset_index()
        p = _mape_by_cell(mm)
        boot.append(p[candidate] - p[best])
    lo, hi = np.quantile(boot, [0.025, 0.975])
    nat = (m.groupby(["model", "profession", "origin"]).apply(lambda g: g.pred.sum() / g.actual.sum() - 1)
           .abs().groupby("model").mean())
    h1 = _mape_by_cell(e[(e.h == 1) & (e.n_origin >= MIN_N)])
    return {"best_naive": best, "mape": pooled.to_dict(), "delta": float(pooled[candidate] - pooled[best]),
            "ci": [float(lo), float(hi)], "issue": "gagne" if hi < 0 else ("perd" if lo > 0 else "égalité"),
            "precision_nationale": bool(nat[candidate] < min(nat[k] for k in naives)),
            "limite_h1_ok": bool(h1[candidate] <= h1["naive_persistance"] + 1)}
