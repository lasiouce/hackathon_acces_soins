"""K3 (inscrit avant passage) : part tenue × total départemental de K ; bande = erreur départementale commune
(un tirage par département) + erreur locale par classe de taille ; soumission N10 (commune, bv2022, epci).

Données de N10 : v2/data/processed/commune_stock.parquet (axe 4). Professions au nom de l'axe 4
(infirmiers, kines, dentistes). Sortie : v2/methodes/out/n10_soumission_k3.parquet
(profession, grain, unit, origin, h, pred, q10, q90).
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.communes_k3
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.communes import BANDS, WINDOW, K, exclusion
from validation.fine_scale import BINS

OUT = Path("v2/methodes/out")
H, S, LAGS, MIN_N = 5, 200, range(5), 20
PROFS = ("infirmiers", "kines", "dentistes")


def load_v2(prof):
    s = pd.read_parquet("v2/data/processed/commune_stock.parquet", filters=[("profession", "==", prof)])
    known = s[s.age_band.isin(BANDS)]
    w = known.pivot_table(index="com", columns=["age_band", "year"], values="n", aggfunc="sum", fill_value=0)
    years = np.sort(s.year.unique())
    coms = np.sort(s.com.unique())
    w = w.reindex(index=coms, columns=pd.MultiIndex.from_product([BANDS, years]), fill_value=0)
    N = w.to_numpy(float).reshape(len(coms), len(BANDS), len(years)).copy()
    extra = s[~s.age_band.isin(BANDS)].groupby(["com", "year"]).n.sum()      # lignes « Total (reste …) »
    for (c, y), v in extra.items():                                            # réparties au prorata (supposé)
        i, j = np.searchsorted(coms, c), list(years).index(y)
        prof_ = N[i, :, j]
        N[i, :, j] += v * (prof_ / prof_.sum() if prof_.sum() > 0 else np.full(len(BANDS), 1 / len(BANDS)))
    geo = pd.read_parquet("v2/data/processed/commune_geo.parquet", columns=["com", "dep", "epci", "reg", "bv2022"])
    g = pd.DataFrame({"com": coms}).merge(geo, on="com", how="left")
    g["dep"] = g.dep.fillna(s.groupby("com").dep.first().reindex(coms).reset_index(drop=True))
    for c in ("epci", "bv2022"):
        g[c] = g[c].fillna("?" + g.com)
    g["reg"] = g.reg.fillna("d" + g.dep)
    return N, years, g


def point(N, years, geo, o):
    tot = N.sum(1)
    n0 = tot[:, list(years).index(o)]
    m = K(N, years, geo[["com", "dep", "epci", "reg"]], o)
    D = np.bincount(m.dep_i, m.project(H)[-1].sum(1))
    D0 = np.bincount(m.dep_i, n0)
    share = np.where(D0[m.dep_i] > 0, n0 / np.maximum(D0[m.dep_i], 1e-9), 0.0)
    return share * D[m.dep_i], share, D, D0, m.dep_i


def errors(N, years, geo, o):
    tot = N.sum(1)
    e_dep, e_loc = [], {i: [] for i in range(len(BINS) - 1)}
    for lag in LAGS:
        o2 = o - H - lag
        if o2 - WINDOW + 1 < years[0]:
            continue
        p, share, D, D0, di = point(N, years, geo, o2)
        act = tot[:, list(years).index(o2 + H)]
        Dt = np.bincount(di, act)
        ok = (D > 0) & (Dt > 0)
        e_dep.extend(np.log(Dt[ok] / D[ok]))
        n0 = tot[:, list(years).index(o2)]
        keep = (n0 >= 1) & ~exclusion(tot, years, o2, H)
        orc = share * Dt[di]
        cls = np.digitize(n0, BINS[1:-1])
        for i in e_loc:
            sel = keep & (cls == i)
            e_loc[i].extend(np.log((act[sel] + 0.5) / (orc[sel] + 0.5)))
    pools = {}
    for i in e_loc:
        e, j = list(e_loc[i]), 1
        while len(e) < MIN_N and j < len(e_loc):
            e = e + list(e_loc.get(i - j, [])) + list(e_loc.get(i + j, []))
            j += 1
        pools[i] = np.array(e)
    return np.array(e_dep), pools


def main():
    t0, out, k = time.time(), [], 0
    for prof in PROFS:
        N, years, geo = load_v2(prof)
        tot = N.sum(1)
        for o in range(2014, 2021):
            if o + H > years[-1]:
                continue
            k += 1
            ed, pools = errors(N, years, geo, o)
            if len(ed) < MIN_N or any(len(v) < MIN_N for v in pools.values()):
                print(f"{k} · {prof} {o} · pas assez de pseudo-prévisions : pas de bande", flush=True)
                continue
            p, share, D, D0, di = point(N, years, geo, o)
            n0 = tot[:, list(years).index(o)]
            rng = np.random.default_rng(20261114 + o)
            cls = np.digitize(n0, BINS[1:-1])
            E_d = rng.choice(ed, size=(S, di.max() + 1))                     # une erreur par département et tirage
            E_l = np.empty((S, len(p)))
            for i, pool in pools.items():
                sel = cls == i
                E_l[:, sel] = rng.choice(pool, size=(S, sel.sum()))
            X = np.maximum((p + 0.5)[None, :] * np.exp(E_d[:, di] + E_l) - 0.5, 0.0)   # [S, commune]
            for grain in ("commune", "bv2022", "epci"):
                key = geo.com if grain == "commune" else geo[grain]
                codes, units = pd.factorize(key)
                Xg = np.zeros((S, len(units)))
                np.add.at(Xg.T, codes, X.T)
                pg = np.bincount(codes, p, minlength=len(units))
                out.append(pd.DataFrame({"profession": prof, "grain": grain, "unit": units, "origin": o, "h": H,
                                         "pred": pg, "q10": np.quantile(Xg, .1, axis=0),
                                         "q90": np.quantile(Xg, .9, axis=0)}))
            print(f"{k} · {prof} {o} · {len(ed)} erreurs dép. · {time.time() - t0:.0f} s", flush=True)
    d = pd.concat(out, ignore_index=True)
    d.to_parquet(OUT / "n10_soumission_k3.parquet", index=False)
    print(d.groupby(["profession", "grain"]).origin.agg(["min", "max", "size"]))


if __name__ == "__main__":
    main()
