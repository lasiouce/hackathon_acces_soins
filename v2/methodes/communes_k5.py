"""K5 (inscrit avant passage) : largeur par loi explicite, paramètres mis en commun entre professions.

log((n + ½)/(p + ½)) = b_p + σ_D,p z_d + √(φ_p/(n0 + ½) + κ_p) z_c ; z_d commun au département.
b, σ_D : médiane et écart-type robuste (1,4826 × MAD) des erreurs départementales des pseudo-origines (ℓ = 0..4) ;
φ, κ : maximum de vraisemblance gaussien sur les erreurs locales écrêtées aux centiles 1 et 99 ;
log σ_D, log φ, log κ rétrécis de moitié vers leur moyenne sur les trois professions (même origine).
Sorties (format N10) :
  v2/methodes/out/n10_soumission_k5.parquet           origines 2014–2020, h = 5
  v2/methodes/out/n10_reservee_k5_2022h3.parquet      origine 2022, h = 3 (réservée, jugée par l'axe 3 seul)
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.communes_k5
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from methodes import communes_k4 as K4
from methodes.communes_k3 import PROFS, load_v2
from validation.fine_scale import BINS

OUT = Path("v2/methodes/out")
S, POOL = 200, 0.5
K4.LAGS = (0, 1, 2, 3, 4)                      # toutes les pseudo-origines disponibles


def local_fit(el, n0):
    lo, hi = np.quantile(el, [0.01, 0.99])
    e = np.clip(el, lo, hi)
    x = 1 / (n0 + 0.5)

    def nll(z):
        v = np.exp(z[0]) * x + np.exp(z[1])
        return 0.5 * (np.log(v) + e * e / v).sum()
    z = minimize(nll, [0.0, np.log(0.01)], method="L-BFGS-B").x
    return np.exp(z)                                                   # φ, κ


def fit_params(N, years, geo, o, h):
    """(b, σ_D, φ, κ) ou None. Erreurs locales avec leur n0 : on relance errors_by_lag en gardant n0."""
    errs = K4.errors_by_lag(N, years, geo, o, h)
    if not errs:
        return None
    ed = np.concatenate([errs[l][0] for l in errs])
    tot = N.sum(1)
    el, n0s = [], []
    for l in errs:
        o2 = o - h - l
        n0 = tot[:, list(years).index(o2)]
        keep = (n0 >= 1) & ~K4.exclusion(tot, years, o2, h)
        cls = np.digitize(n0, BINS[1:-1])
        for i, v in errs[l][1].items():                               # même ordre que errors_by_lag
            el.append(v)
            n0s.append(n0[keep & (cls == i)])
    el, n0s = np.concatenate(el), np.concatenate(n0s)
    phi, kap = local_fit(el, n0s)
    med = float(np.median(ed))
    sD = 1.4826 * float(np.median(np.abs(ed - med)))                  # écart-type robuste (écart avant passage)
    return {"b": med, "sD": sD, "phi": float(phi), "kap": float(kap)}


def run(origins, h, path):
    t0, out, data = time.time(), [], {p: load_v2(p) for p in PROFS}
    for o in origins:
        par = {}
        for p in PROFS:
            N, years, geo = data[p]
            if o + h <= years[-1] and (pp := fit_params(N, years, geo, o, h)):
                par[p] = pp
        if not par:
            continue
        for k in ("sD", "phi", "kap"):                                # mise en commun de moitié (échelle log)
            m = np.mean([np.log(v[k]) for v in par.values()])
            for v in par.values():
                v[k + "_brut"] = v[k]
                v[k] = float(np.exp((1 - POOL) * np.log(v[k]) + POOL * m))
        for p, pp in par.items():
            N, years, geo = data[p]
            pt, share, D, di = K4.point(N, years, geo, o, h)
            n0 = N.sum(1)[:, list(years).index(o)]
            rng = np.random.default_rng(20261114 + o + 1000 * h)
            zd = rng.standard_normal((S, di.max() + 1))
            zc = rng.standard_normal((S, len(pt)))
            sl = np.sqrt(pp["phi"] / (n0 + 0.5) + pp["kap"])
            X = np.maximum((pt + 0.5)[None, :] * np.exp(pp["b"] + pp["sD"] * zd[:, di] + sl[None, :] * zc) - 0.5, 0.0)
            for grain in ("commune", "bv2022", "epci"):
                key = geo.com if grain == "commune" else geo[grain]
                codes, units = pd.factorize(key)
                Xg = np.zeros((S, len(units)))
                np.add.at(Xg.T, codes, X.T)
                out.append(pd.DataFrame({"profession": p, "grain": grain, "unit": units, "origin": o, "h": h,
                                         "pred": np.bincount(codes, pt, minlength=len(units)),
                                         "q10": np.quantile(Xg, .1, axis=0), "q90": np.quantile(Xg, .9, axis=0)}))
            print(f"{p} {o} h={h} · " + " ".join(f"{k}={v:.4f}" for k, v in pp.items()) + f" · {time.time() - t0:.0f} s",
                  flush=True)
    d = pd.concat(out, ignore_index=True)
    d.to_parquet(path, index=False)
    print(path, d.groupby(["profession", "grain"]).origin.agg(["min", "max", "size"]).to_string(), flush=True)


if __name__ == "__main__":
    run(range(2014, 2021), 5, OUT / "n10_soumission_k5.parquet")
    run([2022], 3, OUT / "n10_reservee_k5_2022h3.parquet")
