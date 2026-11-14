"""Axe 3, niveau 4 : erreur selon la taille de la commune (protocole N4, SHA-256 91f897cc5071…).

  share_out(dep_total, shares_origin)       défaut : projection départementale × part communale tenue
  size_errors(pred, actual, n_origin)       métriques par classe de taille (P80 principal)
  n_min(table)                              plus petite classe à partir de laquelle P80 ≤ 25 % (classes au-dessus incluses)
"""
import numpy as np
import pandas as pd

BINS = [1, 3, 6, 11, 21, 51, 101, 201, np.inf]
LABELS = ["1–2", "3–5", "6–10", "11–20", "21–50", "51–100", "101–200", ">200"]
P80_MAX = 25.0


def share_out(dep_total: pd.Series, n_origin: pd.Series, dep_of: pd.Series) -> pd.Series:
    """dep_total : dep -> total projeté ; n_origin : com -> effectif à l'origine ; dep_of : com -> dep."""
    share = n_origin / n_origin.groupby(dep_of).transform("sum")
    return share * dep_of.map(dep_total)


def size_errors(pred: pd.Series, actual: pd.Series, n_origin: pd.Series) -> pd.DataFrame:
    d = pd.DataFrame({"pred": pred, "actual": actual, "n0": n_origin}).dropna()
    d = d[d.n0 >= 1]
    d["cls"] = pd.cut(d.n0, BINS, right=False, labels=LABELS)
    d["err"] = 100 * (d.pred - d.actual) / d.actual.where(d.actual > 0)
    g = d.groupby("cls", observed=False)
    return pd.DataFrame({
        "communes": g.size(),
        "P80_abs_%": g.err.apply(lambda x: x.abs().quantile(0.8)),
        "mediane_abs_%": g.err.apply(lambda x: x.abs().median()),
        "WAPE_%": g.apply(lambda x: 100 * (x.pred - x.actual).abs().sum() / x.actual.sum()),
        "biais_%": g.apply(lambda x: 100 * (x.pred.sum() / x.actual.sum() - 1)),
        "plancher_poisson_P80_%": [100 * 1.28 / np.sqrt(lo) for lo in BINS[:-1]],
    })


def n_min(tab: pd.DataFrame) -> float:
    ok = (tab["P80_abs_%"] <= P80_MAX).to_numpy()
    for i in range(len(ok)):
        if ok[i:].all():
            return BINS[i]
    return np.inf
