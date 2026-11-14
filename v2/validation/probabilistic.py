"""Axe 3, N6 (SHA-256 d1cc665cb864…) et N7-C (06ba47b91647…) : prévision probabiliste sur log N.

Entrée : erreurs du banc N1 (validation.forecast.bench), toutes origines × horizons, périmètre privé, produites par
l'axe 2 avec le même banc (v2/methodes/out/erreurs_prive.parquet, apc_erreurs.parquet).
  N6     bande empirique au même horizon : log prédit + e, e parmi les erreurs log passées (même estimateur,
         profession, h ; cible ≤ origine), ≥ 20 erreurs ; CRPS par échantillon. Applicable à h = 5 : origine 2021.
  N7-C   bande « pente d'erreur » : log N ~ Normale(log prédit, (s·h)²), s = RMS(e/h') sur les paires passées
         (o' ≥ 2016, o' + h' ≤ o) ; CRPS gaussien en forme fermée. h = 5, origines 2017–2021.
  APC    tirages propres (N6, « estimateur qui rend des tirages ») : `--apc`, origine 2021, S = 200 (machine, long).
Critère : Δ CRPS vs meilleure naïve probabiliste, bootstrap des départements (2 000, graine 20261114).
Couverture des intervalles centraux à 50 et 80 % ; histogramme PIT en 10 classes (rapporté).
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.probabilistic [--apc]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"
SEED, BOOT, MIN_N, MIN_ERR, H = 20261114, 2000, 30, 20, 5
NAIVES = ("naive_persistance", "naive_tendance")


def load() -> pd.DataFrame:
    a = pd.read_parquet(ROOT / "v2/methodes/out/erreurs_prive.parquet")
    b = pd.read_parquet(ROOT / "v2/methodes/out/apc_erreurs.parquet")
    e = pd.concat([a, b[b.model == "axe2_apc"]], ignore_index=True)
    e = e[(e.actual > 0) & (e.pred > 0)].copy()
    e["e"] = np.log(e.actual / e.pred)
    return e


def crps_sample(x: np.ndarray, y: float) -> float:
    """E|X − y| − ½ E|X − X'| (forme par échantillon, Gneiting & Raftery 2007, éq. 21 au signe près)."""
    x = np.sort(x)
    n = len(x)
    i = np.arange(1, n + 1)
    return float(np.abs(x - y).mean() - (2 * i - n - 1) @ x / n ** 2)


def crps_gauss(mu, sig, y):
    z = (y - mu) / sig
    return sig * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))


def n6(e: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cur = e[(e.h == H) & (e.n_origin >= MIN_N)]
    for (m, p, o), g in cur.groupby(["model", "profession", "origin"]):
        past = e[(e.model == m) & (e.profession == p) & (e.h == H) & (e.origin + H <= o)].e.to_numpy()
        if len(past) < MIN_ERR:
            continue
        for r in g.itertuples():
            x = np.log(r.pred) + past
            y = np.log(r.actual)
            rows.append({"model": m, "profession": p, "origin": o, "territory": r.territory, "crps": crps_sample(x, y),
                         "pit": float((x < y).mean() + 0.5 * (x == y).mean()), "n_past": len(past)})
    return pd.DataFrame(rows)


def n7c(e: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cur = e[(e.h == H) & (e.n_origin >= MIN_N) & e.origin.between(2017, 2021)]
    for (m, p, o), g in cur.groupby(["model", "profession", "origin"]):
        past = e[(e.model == m) & (e.profession == p) & (e.origin >= 2016) & (e.origin + e.h <= o)]
        if len(past) < MIN_ERR:
            continue
        s = float(np.sqrt(((past.e / past.h) ** 2).mean()))
        mu, y, sig = np.log(g.pred.to_numpy()), np.log(g.actual.to_numpy()), s * H
        rows.append(pd.DataFrame({"model": m, "profession": p, "origin": o, "territory": g.territory.to_numpy(),
                                  "crps": crps_gauss(mu, sig, y), "pit": norm.cdf((y - mu) / sig), "s": s,
                                  "n_past": len(past)}))
    return pd.concat(rows, ignore_index=True)


def verdicts(sc: pd.DataFrame, label: str) -> pd.DataFrame:
    """Δ CRPS poolé (cellules profession × origine à poids égal) vs meilleure naïve, IC bootstrap des départements."""
    rng = np.random.default_rng(SEED)
    deps = np.sort(sc.territory.unique())
    di = {d: i for i, d in enumerate(deps)}
    cells = sorted(set(map(tuple, sc[["profession", "origin"]].drop_duplicates().to_numpy())))
    W = rng.multinomial(len(deps), np.full(len(deps), 1 / len(deps)), size=BOOT).astype(float)
    mats, point = {}, {}
    for m, g in sc.groupby("model"):
        M = np.full((len(cells), len(deps)), np.nan)
        gi = g.set_index(["profession", "origin"])
        for j, c in enumerate(cells):
            if c in gi.index:
                gc = gi.loc[[c]]
                M[j, [di[d] for d in gc.territory]] = gc.crps.to_numpy()
        mats[m] = M
        point[m] = np.nanmean(np.nanmean(M, 1))

    def boot(M):
        ok = ~np.isnan(M)
        num, den = W @ np.where(ok, M, 0).T, W @ ok.T.astype(float)
        return np.nanmean(num / np.where(den > 0, den, np.nan), 1)
    naives = [k for k in NAIVES if k in mats]
    best = min(naives, key=lambda k: point[k])
    bb = boot(mats[best])
    rows = []
    for m in mats:
        cov = sc[sc.model == m].pit
        row = {"bande": label, "model": m, "crps_log": point[m], "best_naive": best,
               "couv50": float(((cov > 0.25) & (cov < 0.75)).mean()), "couv80": float(((cov > 0.1) & (cov < 0.9)).mean()),
               "n": int(len(cov)), "pit10": np.histogram(cov, bins=10, range=(0, 1))[0].tolist()}
        if m != best:
            d = boot(mats[m]) - bb
            lo, hi = np.nanquantile(d, [0.025, 0.975])
            row.update(delta=point[m] - point[best], lo=lo, hi=hi,
                       issue="gagne" if hi < 0 else ("perd" if lo > 0 else "égalité"))
        row["calibre"] = bool(0.75 <= row["couv80"] <= 0.85 and 0.44 <= row["couv50"] <= 0.56)
        rows.append(row)
    return pd.DataFrame(rows)


def apc_draws(S: int = 100) -> pd.DataFrame:
    """N6 pour l'APC avec ses propres tirages : origine 2021, cible 2026 (h = 5)."""
    from methodes.apc import APCEstimator
    from methodes.perimetres import prive
    t = prive()
    rows, t0 = [], time.time()
    profs = [p for p in sorted(t.profession.unique()) if t[t.profession == p].year.max() >= 2026]
    for k, p in enumerate(profs, 1):
        tp = t[t.profession == p]
        first = 2017 if p == "kines" else 2012
        est = APCEstimator().fit(tp[tp.year <= 2021], (first, 2021), 2021)
        smp = est.sample(2026, S)
        smp.index = smp.index.set_names(["profession", "territory"]) if smp.index.nlevels == 2 else smp.index
        act = tp[tp.year == 2026].groupby("dep").n.sum()
        n0 = tp[tp.year == 2021].groupby("dep").n.sum()
        for idx, x in smp.iterrows():
            d = idx[-1] if isinstance(idx, tuple) else idx
            if d not in act.index or n0.get(d, 0) < MIN_N or act[d] <= 0:
                continue
            lx, y = np.log(np.maximum(x.to_numpy(float), 1e-9)), np.log(act[d])
            rows.append({"model": "axe2_apc (tirages)", "profession": p, "origin": 2021, "territory": d,
                         "crps": crps_sample(lx, y), "pit": float((lx < y).mean())})
        print(f"{k}/{len(profs)} APC {p} {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(rows)


def main(argv):
    OUT.mkdir(exist_ok=True)
    e = load()
    a, b = n6(e), n7c(e)
    if "--apc" in argv:
        d = apc_draws()
        d.to_parquet(OUT / "prob_apc_tirages.parquet")
        a = pd.concat([a, d], ignore_index=True)
    a.to_parquet(OUT / "prob_n6_scores.parquet")
    b.to_parquet(OUT / "prob_n7c_scores.parquet")
    v = pd.concat([verdicts(a, "N6 empirique même h"), verdicts(b, "N7-C pente d'erreur")], ignore_index=True)
    v.to_csv(OUT / "prob_verdicts.csv", index=False)
    cells = {"N6": a.groupby(["profession", "origin"]).size().reset_index().values.tolist(),
             "N7C": b.groupby(["profession", "origin"]).size().reset_index().values.tolist()}
    (OUT / "prob_cells.json").write_text(json.dumps(cells, default=int))
    with pd.option_context("display.width", 250, "display.max_columns", 20):
        print(v.drop(columns="pit10").round(4).to_string())
        print(v[["bande", "model", "pit10"]].to_string())
    print(json.dumps(cells, default=int)[:600])


if __name__ == "__main__":
    main(sys.argv[1:])
