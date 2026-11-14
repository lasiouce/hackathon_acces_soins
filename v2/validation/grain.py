"""Axe 3, N10 (SHA-256 d86d27c7a750…) : grain le plus fin et couverture des bandes à 80 % (commune, BV, EPCI).

Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.grain -> v2/validation/out/grain_*
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from validation.fine_scale import BINS, LABELS, n_min, size_errors

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"
H, MIN_PAST, MIN_JUDGED = 5, 50, 30
JUDGED = range(2014, 2021)
PROFS = ("infirmiers", "kines", "dentistes")
GRAINS = ("commune", "bv2022", "epci")
ESTS = ("persistance", "tendance", "repartition_tendance", "repartition_oracle")


def trend(Y: np.ndarray, years, target):
    X = np.asarray(years, float)
    sl = ((X - X.mean()) * (Y - Y.mean(1, keepdims=True))).sum(1) / ((X - X.mean()) ** 2).sum()
    return np.maximum(Y.mean(1) + sl * (target - X.mean()), 0)


def records(prof: str) -> pd.DataFrame:
    s = pd.read_parquet(ROOT / "v2/data/processed/commune_stock.parquet", filters=[("profession", "==", prof)])
    W = s.groupby(["com", "year"]).n.sum().unstack("year").fillna(0)
    geo = pd.read_parquet(ROOT / "v2/data/processed/commune_geo.parquet").set_index("com")
    geo = geo.reindex(W.index)
    dep = geo.dep.fillna(s.groupby("com").dep.first().reindex(W.index))
    first, last = int(W.columns.min()), int(W.columns.max())
    rows = []
    for o in range(first + 5, last - H + 1):
        yrs = list(range(o - 5, o + 1))
        span = W[list(range(o - 5, o + H + 1))].to_numpy()
        jump = (np.abs(np.diff(span, axis=1)) > 3 * np.sqrt(np.maximum(span[:, :-1], 1))).any(1)
        dep_hist = W[yrs].groupby(dep).sum()
        dep_tr = pd.Series(trend(dep_hist.to_numpy(), yrs, o + H), index=dep_hist.index)
        dep_true = W[o + H].groupby(dep).sum()
        dep_o = W[o].groupby(dep).sum()
        for grain in GRAINS:
            if grain == "commune":
                key = pd.Series(W.index, index=W.index)
                Wg, keep = W, pd.Series(~jump, index=W.index)
            else:
                key = geo[grain].fillna("?" + W.index.to_series())
                Wg, keep = W.groupby(key).sum(), None
            gdep = dep.groupby(key).agg(lambda x: x.mode().iloc[0]) if grain != "commune" else dep
            gdep = gdep.reindex(Wg.index)
            n0, act = Wg[o], Wg[o + H]
            share = n0 / gdep.map(dep_o).replace(0, np.nan)
            P = {"persistance": n0, "tendance": pd.Series(trend(Wg[yrs].to_numpy(), yrs, o + H), index=Wg.index),
                 "repartition_tendance": share * gdep.map(dep_tr), "repartition_oracle": share * gdep.map(dep_true)}
            m = pd.Series(True, index=Wg.index) if keep is None else keep
            for e, p in P.items():
                rows.append(pd.DataFrame({"unit": Wg.index[m], "origin": o, "grain": grain, "est": e,
                                          "n0": n0[m].to_numpy(), "pred": p[m].to_numpy(), "actual": act[m].to_numpy()}))
    r = pd.concat(rows, ignore_index=True).assign(profession=prof)
    r["cls"] = pd.cut(r.n0, BINS, right=False, labels=LABELS)
    return r


def coverage(r: pd.DataFrame) -> pd.DataFrame:
    r = r[(r.n0 >= 1) & (r.pred > 0)].copy()
    r["ratio"] = r.actual / r.pred
    out = []
    for (g, e, c), d in r.groupby(["grain", "est", "cls"], observed=True):
        for o in JUDGED:
            past = d[d.origin + H <= o].ratio
            cur = d[d.origin == o]
            if len(cur) == 0:
                continue
            if len(past) < MIN_PAST:
                out.append({"grain": g, "est": e, "cls": c, "origin": o, "n": len(cur), "in": np.nan, "jugee": False})
                continue
            lo, hi = past.quantile([0.1, 0.9])
            inside = ((cur.ratio >= lo) & (cur.ratio <= hi)).sum()
            out.append({"grain": g, "est": e, "cls": c, "origin": o, "n": len(cur), "in": inside, "jugee": True,
                        "largeur_rel": float(hi - lo)})
    return pd.DataFrame(out)


def main():
    OUT.mkdir(exist_ok=True)
    allc, allp, verdict = [], [], {}
    for prof in PROFS:
        r = records(prof)
        cv = coverage(r).assign(profession=prof)
        allc.append(cv)
        j = cv[cv.jugee]
        agg = j.groupby(["grain", "est", "cls"], observed=True).agg(n=("n", "sum"), inn=("in", "sum"),
                                                                     largeur=("largeur_rel", "mean")).reset_index()
        agg["couv"] = agg.inn / agg.n
        byo = j.assign(c=j["in"] / j.n).groupby(["grain", "est", "cls"], observed=True).c.agg(["min", "max"]).reset_index()
        agg = agg.merge(byo, on=["grain", "est", "cls"])
        agg["profession"] = prof
        allp.append(agg)
        verdict[prof] = {}
        for g in GRAINS:
            a = agg[(agg.grain == g) & (agg.est == "repartition_tendance") & (agg.n >= MIN_JUDGED)]
            ok = bool(len(a) and a.couv.between(0.75, 0.85).all())
            ce = r[(r.grain == g) & r.origin.isin([2014, 2016, 2018, 2020])]
            nm = {}
            for e in ESTS:
                vals = []
                for o in (2014, 2016, 2018, 2020):
                    d = ce[(ce.est == e) & (ce.origin == o)]
                    tab = size_errors(d.pred.set_axis(d.unit), d.actual.set_axis(d.unit), d.n0.set_axis(d.unit))
                    vals.append(n_min(tab))
                nm[e] = next((b for b in BINS[:-1] if sum(v <= b for v in vals) >= 3), None)
            verdict[prof][g] = {"fiable": ok, "classes_jugees": int(len(a)),
                                "classes_hors_bande": a[~a.couv.between(0.75, 0.85)][["cls", "couv", "n"]]
                                .astype({"cls": str}).to_dict("records"),
                                "N_min": {k: (None if v is None or np.isinf(v) else float(v)) for k, v in nm.items()}}
        fine = next((g for g in GRAINS if verdict[prof][g]["fiable"]), None)
        verdict[prof]["grain_le_plus_fin_fiable"] = fine or "département (aucun grain fin calibré)"
    C = pd.concat(allp, ignore_index=True)
    C.to_csv(OUT / "grain_couverture.csv", index=False)
    pd.concat(allc).to_csv(OUT / "grain_couverture_par_origine.csv", index=False)
    (OUT / "grain_results.json").write_text(json.dumps(verdict, indent=1, ensure_ascii=False, default=float))
    with pd.option_context("display.width", 220, "display.max_rows", 400):
        print(C[C.est == "repartition_tendance"].pivot_table(index="cls", columns=["profession", "grain"],
                                                              values="couv", observed=False).round(3).to_string())
    print(json.dumps(verdict, indent=1, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
