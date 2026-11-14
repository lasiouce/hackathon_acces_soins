"""Lance Morris puis Sobol par profession ; écrit v2/sensibilite/out/*.csv et affiche k/N.

Run (racine) : PYTHONPATH=v2:. uv run python -m sensibilite.run [--n 2048] [--r 30] [--profs dentistes,...] [--pilot]
  famille « tout »        leviers compris : classe ce qui déplace Y
  famille « incertitude » leviers au tendanciel : donne la fourchette (a) à 2050
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from sensibilite.facteurs import PROFS, SEED, YEARS, Model
from sensibilite.methodes import bootstrap, morris_design, morris_effects, sobol_design, sobol_indices

OUT = Path("v2/sensibilite/out")


def progress(label, k, n, t0):
    if k % 200 == 0 or k == n:
        el = time.time() - t0
        print(f"{label} {k}/{n} {el:.0f}s reste ~{el / max(k, 1) * (n - k):.0f}s", flush=True)


def evaluate(model, X, label):
    flat = X.reshape(-1, X.shape[-1])
    Y, t0 = np.empty((len(flat), len(YEARS))), time.time()
    for j, u in enumerate(flat):
        Y[j] = model(u)
        progress(label, j + 1, len(flat), t0)
    return Y.reshape(*X.shape[:-1], len(YEARS))


def run_prof(prof, family, n, r, rng):
    m = Model(prof, levers=family == "tout")
    k, names = len(m.f), [f.name for f in m.f]
    ref = m(np.array([_default(f) for f in m.f]))
    # Morris
    des = morris_design(k, r, rng)
    Ym = evaluate(m, np.stack([d[0] for d in des]), f"{prof}/{family}/morris")
    EE = morris_effects(des, Ym)
    rows = []
    for yi, y in enumerate(YEARS):
        for i, nm in enumerate(names):
            e = EE[:, i, yi] / ref[yi] * 100
            rows.append(dict(profession=prof, famille=family, annee=y, facteur=nm, mu_star_pct=np.abs(e).mean(),
                             mu_pct=e.mean(), sigma_pct=e.std(ddof=1), y_ref=ref[yi]))
    morris = pd.DataFrame(rows)
    # Sobol
    X = sobol_design(k, n, rng)
    Y = evaluate(m, X, f"{prof}/{family}/sobol")
    rows, dist = [], []
    for yi, y in enumerate(YEARS):
        S1, ST = sobol_indices(Y[:, :, yi])
        c1, ct = bootstrap(Y[:, :, yi], rng)
        for i, nm in enumerate(names):
            rows.append(dict(profession=prof, famille=family, annee=y, facteur=nm, famille_facteur=m.f[i].family,
                             S1=S1[i], S1_lo=c1[0, i], S1_hi=c1[1, i], ST=ST[i], ST_lo=ct[0, i], ST_hi=ct[1, i]))
        ys = np.concatenate([Y[:, 0, yi], Y[:, 1, yi]])
        dist.append(dict(profession=prof, famille=family, annee=y, y_ref=ref[yi], p05=np.percentile(ys, 5),
                         p50=np.median(ys), p95=np.percentile(ys, 95), cv_pct=100 * ys.std() / ys.mean()))
    return morris, pd.DataFrame(rows), pd.DataFrame(dist), m.runs


def _default(f):
    """Point de référence : tendanciel par défaut (fenêtre 5, shrink 200, entrées plates, centrale, leviers neutres)."""
    d = {"fenetre": 5, "shrink": 200, "entrees": "plates", "filiere": False, "part_privee": "central",
         "fraction": 0.2, "decalage_retraite": 0.0, "cumul_multiplicateur": 1.0, "quotas": 1.0}
    v = d.get(f.name)
    if f.levels:
        return (f.levels.index(v) + 0.5) / len(f.levels)
    if v is None:                                   # part_cumul : valeur de la fiche, milieu géométrique de la plage
        v = (f.lo * f.hi) ** 0.5
    return (v - f.lo) / (f.hi - f.lo)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--n", type=int, default=2048)
    a.add_argument("--r", type=int, default=30)
    a.add_argument("--profs", default=",".join(PROFS))
    a.add_argument("--families", default="tout,incertitude")
    a.add_argument("--tag", default="")
    args = a.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    res = {"morris": [], "sobol": [], "dist": []}
    t0 = time.time()
    for prof in args.profs.split(","):
        for fam in args.families.split(","):
            mo, so, di, runs = run_prof(prof, fam, args.n, args.r, rng)
            res["morris"].append(mo)
            res["sobol"].append(so)
            res["dist"].append(di)
            print(f"FAIT {prof}/{fam} : {runs} runs, {time.time() - t0:.0f}s", flush=True)
    for k, v in res.items():
        pd.concat(v).to_csv(OUT / f"{k}{args.tag}.csv", index=False)
    print(f"TOTAL {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
