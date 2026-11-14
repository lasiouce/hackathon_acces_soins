"""K4 (inscrit avant passage) : K3 avec erreurs des 2 pseudo-origines les plus récentes, tirées conjointement.

Point : part tenue × total départemental de K (comme K3). Pour chaque tirage, une pseudo-origine ℓ ∈ {0, 1} ;
erreur départementale (un tirage par département) et erreur locale (par classe de taille) prises dans ℓ.
Sorties (format N10) :
  v2/methodes/out/n10_soumission_k4.parquet          origines 2014–2020, h = 5
  v2/methodes/out/n10_confirmation_k4_2021h4.parquet origine 2021, h = 4 (réservée, jugée par l'axe 3 seul)
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.communes_k4
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.communes import WINDOW, K, exclusion
from methodes.communes_k3 import PROFS, load_v2
from validation.fine_scale import BINS

OUT = Path("v2/methodes/out")
S, LAGS, MIN_N = 200, (0, 1), 50


def point(N, years, geo, o, h):
    tot = N.sum(1)
    n0 = tot[:, list(years).index(o)]
    m = K(N, years, geo[["com", "dep", "epci", "reg"]], o)
    D = np.bincount(m.dep_i, m.project(h)[-1].sum(1))
    D0 = np.bincount(m.dep_i, n0)
    share = np.where(D0[m.dep_i] > 0, n0 / np.maximum(D0[m.dep_i], 1e-9), 0.0)
    return share * D[m.dep_i], share, D, m.dep_i


def errors_by_lag(N, years, geo, o, h):
    """{ℓ : (erreurs départementales, {classe : erreurs locales})} pour les pseudo-origines o − h − ℓ."""
    tot = N.sum(1)
    out = {}
    for lag in LAGS:
        o2 = o - h - lag
        if o2 - WINDOW + 1 < years[0]:
            continue
        p, share, D, di = point(N, years, geo, o2, h)
        act = tot[:, list(years).index(o2 + h)]
        Dt = np.bincount(di, act)
        ok = (D > 0) & (Dt > 0)
        n0 = tot[:, list(years).index(o2)]
        keep = (n0 >= 1) & ~exclusion(tot, years, o2, h)
        cls = np.digitize(n0, BINS[1:-1])
        el = np.log((act + 0.5) / (share * Dt[di] + 0.5))
        out[lag] = (np.log(Dt[ok] / D[ok]), {i: el[keep & (cls == i)] for i in range(len(BINS) - 1)})
    return out


def pool(errs, lag, i):
    """Erreurs locales de la classe i dans ℓ ; sous MIN_N, classes voisines de ℓ, puis toutes les ℓ."""
    e, j = list(errs[lag][1][i]), 1
    while len(e) < MIN_N and j < len(BINS) - 1:
        e += list(errs[lag][1].get(i - j, [])) + list(errs[lag][1].get(i + j, []))
        j += 1
    if len(e) < MIN_N:
        e = [x for l2 in errs for x in errs[l2][1][i]]
    return np.array(e)


def run(origins, h, path, future=False):
    t0, out = time.time(), []
    for prof in PROFS:
        N, years, geo = load_v2(prof)
        tot = N.sum(1)
        for o in origins:
            if o + h > years[-1] and not future:
                continue
            errs = errors_by_lag(N, years, geo, o, h)
            if not errs:
                print(f"{prof} {o} h={h} : pas de pseudo-origine, pas de bande", flush=True)
                continue
            p, share, D, di = point(N, years, geo, o, h)
            n0 = tot[:, list(years).index(o)]
            cls = np.digitize(n0, BINS[1:-1])
            rng = np.random.default_rng(20261114 + o + 100 * h)
            lags = np.array(sorted(errs))
            pick = rng.choice(lags, size=S)
            X = np.empty((S, len(p)))
            pools = {(l, i): pool(errs, l, i) for l in lags for i in range(len(BINS) - 1)}
            for s in range(S):
                l = pick[s]
                ed = rng.choice(errs[l][0], size=di.max() + 1)
                el = np.empty(len(p))
                for i in range(len(BINS) - 1):
                    sel = cls == i
                    el[sel] = rng.choice(pools[(l, i)], size=sel.sum())
                X[s] = np.maximum((p + 0.5) * np.exp(ed[di] + el) - 0.5, 0.0)
            for grain in ("commune", "bv2022", "epci"):
                key = geo.com if grain == "commune" else geo[grain]
                codes, units = pd.factorize(key)
                Xg = np.zeros((S, len(units)))
                np.add.at(Xg.T, codes, X.T)
                out.append(pd.DataFrame({"profession": prof, "grain": grain, "unit": units, "origin": o, "h": h,
                                         "pred": np.bincount(codes, p, minlength=len(units)),
                                         "q10": np.quantile(Xg, .1, axis=0), "q90": np.quantile(Xg, .9, axis=0)}))
            print(f"{prof} {o} h={h} · pseudo-origines {list(lags)} · {time.time() - t0:.0f} s", flush=True)
    d = pd.concat(out, ignore_index=True)
    d.to_parquet(path, index=False)
    print(path, d.groupby(["profession", "grain"]).origin.agg(["min", "max", "size"]).to_string(), flush=True)


if __name__ == "__main__":
    run(range(2014, 2021), 5, OUT / "n10_soumission_k4.parquet")
    run([2021], 4, OUT / "n10_confirmation_k4_2021h4.parquet")
    sys.exit(0)


def depot():
    """Dépôt communal de K4 (règle N11) : origine = dernière année observée (2025), cibles 2027 et 2028."""
    import hashlib
    path = Path("v2/validation/depot/k4_communes_2026-11-14.parquet")
    parts = []
    for h in (2, 3):
        tmp = OUT / f"_depot_k4_h{h}.parquet"
        run([2025], h, tmp, future=True)
        parts.append(pd.read_parquet(tmp).assign(cible=2025 + h))
        tmp.unlink()
    d = pd.concat(parts, ignore_index=True)
    d.to_parquet(path, index=False)
    print(path, len(d), hashlib.sha256(path.read_bytes()).hexdigest()[:12], flush=True)
