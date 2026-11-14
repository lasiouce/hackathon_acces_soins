"""Axe 3, N7-A : différence de différences dans les bassins de vie 2022 (protocole N7, SHA-256 06ba47b91647…).

Run (racine du dépôt) : PYTHONPATH=v2 uv run --with scipy python -m validation.did_commune -> v2/validation/out/didc_*

Cellule = BV × classe de zone (zonage 2012, Atlasanté) ; Y = somme des communes (CartoSanté, axe 4).
D[b, t] = log Y[b, traitée, t] − log Y[b, témoin, t] ; moyennes non pondérées sur les BV, variance robuste par
grappe = département (CR1), Student à G − 1 ddl ; tendances : Wald robuste -> F(q, G − q).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "v2/data/processed"
OUT = Path(__file__).parent / "out"
SEED, BOOT, MIN_Y = 20261114, 2000, 5
PROF = {"infirmiers": "infirmiers", "kines": "kines", "dentistes": "dentistes"}


def cells(prof: str, zprof: str, zones: tuple, ref: int):
    s = pd.read_parquet(DATA / "commune_stock.parquet", filters=[("profession", "==", prof)])
    s = s.groupby(["com", "year"], as_index=False).n.sum()
    z = pd.read_parquet(DATA / "zonage_commune.parquet")
    z = z[z.millesime.str.startswith("2012") & (z.profession == zprof)]
    z = z.assign(zone=z.classe.str[0])[["com", "zone"]]
    g = pd.read_parquet(DATA / "commune_geo.parquet")[["com", "dep", "bv2022"]]
    m = s.merge(z, on="com", how="left").merge(g, on="com", how="left")
    r = m[m.year == ref]
    bilan = {"profession": prof, "ref": ref, "communes": int(r.com.nunique()), "effectif": float(r.n.sum()),
             "sans_zone": float(r.loc[r.zone.isna(), "n"].sum()), "sans_bv": float(r.loc[r.bv2022.isna(), "n"].sum())}
    m = m[m.zone.isin(zones) & m.bv2022.notna()]
    Y = m.groupby(["bv2022", "zone", "year"]).n.sum().unstack("year").fillna(0)
    dep = m.groupby("bv2022").dep.agg(lambda x: x.mode().iloc[0])
    return Y, dep, bilan


def diff(Y, dep, a, b, ref):
    A, B = Y.xs(a, level="zone"), Y.xs(b, level="zone")
    bv = A.index.intersection(B.index)
    A, B = A.loc[bv], B.loc[bv]
    keep = (A[ref] >= MIN_Y) & (B[ref] >= MIN_Y)
    A, B = A[keep], B[keep]
    with np.errstate(divide="ignore"):
        D = (np.log(A) - np.log(B)).replace([np.inf, -np.inf], np.nan)
    return D, dep.loc[D.index]


def cr1_mean(x: np.ndarray, cl: np.ndarray) -> dict:
    ok = ~np.isnan(x)
    x, cl = x[ok], cl[ok]
    n, est = len(x), x.mean()
    s = pd.Series(x - est).groupby(cl).sum().to_numpy()
    G = len(s)
    se = float(np.sqrt(G / (G - 1) * (s ** 2).sum()) / n)
    q = stats.t.ppf(0.975, G - 1)
    return {"est": float(est), "se": se, "lo": float(est - q * se), "hi": float(est + q * se),
            "p": float(2 * stats.t.sf(abs(est) / se, G - 1)), "G": int(G), "n_bv": int(n)}


def wald(X: np.ndarray, cl: np.ndarray) -> dict:
    ok = ~np.isnan(X).any(1)
    X, cl = X[ok], cl[ok]
    n, q = X.shape
    m = X.mean(0)
    S = pd.DataFrame(X - m).groupby(cl).sum().to_numpy()
    G = len(S)
    V = G / (G - 1) * S.T @ S / n ** 2
    W = float(m @ np.linalg.solve(V, m))
    F = W * (G - q) / (q * (G - 1))
    return {"W": W, "F": F, "df": [q, G - q], "p": float(stats.f.sf(F, q, G - q)), "G": int(G), "n_bv": int(n)}


def did(D, cl, pre, post):
    return cr1_mean((D[post].mean(1) - D[pre].mean(1)).to_numpy(), cl.to_numpy())


def event(D, cl, ref):
    return pd.DataFrame([{"year": k, **cr1_mean((D[k] - D[ref]).to_numpy(), cl.to_numpy())}
                         for k in D.columns if k != ref]).set_index("year")


def slopes(D, years):
    X = np.array(years, float) - np.mean(years)
    return (D[years].to_numpy() * X).sum(1) / (X ** 2).sum()


def theta(Y, D, cl, post, ref):
    c = Y.xs("3", level="zone").loc[D.index]
    with np.errstate(divide="ignore"):
        g3 = np.log(c[post]).sub(np.log(c[ref]), axis=0).replace([np.inf, -np.inf], np.nan)
    mod = np.minimum(0, -g3).mean(1).to_numpy()
    obs = D[post].sub(D[ref], axis=0).mean(1).to_numpy()
    ok = ~(np.isnan(mod) | np.isnan(obs))
    mod, obs, cl = mod[ok], obs[ok], cl.to_numpy()[ok]
    rng = np.random.default_rng(SEED)
    groups = pd.Series(np.arange(len(obs))).groupby(cl).apply(list).tolist()
    boot = []
    for _ in range(BOOT):           # bootstrap par grappe (département)
        idx = np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])
        boot.append(obs[idx].mean() / mod[idx].mean())
    return {"beta_obs": float(obs.mean()), "beta_mod": float(mod.mean()), "theta": float(obs.mean() / mod.mean()),
            "lo": float(np.nanquantile(boot, 0.025)), "hi": float(np.nanquantile(boot, 0.975))}


def verdict_pl(pl, main):
    return "échoue" if np.sign(pl["est"]) == np.sign(main["est"]) and abs(pl["est"]) >= 0.5 * abs(main["est"]) else "passe"


def e1c():
    pre, post, ref, yrs = list(range(2004, 2009)), list(range(2012, 2020)), 2008, list(range(2004, 2020))
    Y, dep, bilan = cells("infirmiers", "infirmiers", ("1", "3", "4", "5"), ref)
    D, cl = diff(Y, dep, "5", "3", ref)
    D = D[yrs]
    main = did(D, cl, pre, post)
    r = {"bilan": bilan, "T1": wald((D[[2004, 2005, 2006, 2007]].sub(D[ref], axis=0)).to_numpy(), cl.to_numpy()),
         "T2": did(D, cl, [2004, 2005], [2006, 2007, 2008]), "T5": main,
         "transition_2009_2011": did(D, cl, pre, [2009, 2010, 2011])}
    Yd, depd, bd = cells("dentistes", "infirmiers", ("3", "5"), ref)
    Dd, cld = diff(Yd, depd, "5", "3", ref)
    r["T3_dentistes"] = {**did(Dd, cld, [2006, 2007, 2008], post), "bilan": bd}
    r["T3_verdict"] = verdict_pl(r["T3_dentistes"], main)
    D4, cl4 = diff(Y, dep, "4", "3", ref)
    r["T4_zone4"] = did(D4[yrs], cl4, pre, post)
    r["T4_verdict"] = verdict_pl(r["T4_zone4"], main)
    D1, cl1 = diff(Y, dep, "1", "3", ref)
    r["zone1_incitations"] = did(D1[yrs], cl1, pre, post)
    r["theta"] = theta(Y, D, cl, post, ref)
    r["T2_passe"] = bool(r["T2"]["lo"] <= 0 <= r["T2"]["hi"])
    r["design_valide"] = bool(r["T1"]["p"] >= 0.10 and r["T2_passe"] and r["T3_verdict"] == "passe"
                              and r["T4_verdict"] == "passe")
    return r, event(D, cl, ref), event(D4[yrs], cl4, ref), event(Dd, cld, ref)


def e2c():
    ref = 2011
    Y, dep, bilan = cells("kines", "kines", ("3", "5"), ref)
    D, cl = diff(Y, dep, "5", "3", ref)
    D = D[list(range(2005, 2018))]
    on, off = [2011, 2012, 2013, 2014], [2014, 2015, 2016, 2017]
    Dn = D.sub(D[ref], axis=0)
    r = {"bilan": bilan,
         "tendances": wald(Dn[list(range(2005, 2011))].to_numpy(), cl.to_numpy()),
         "pente_marche": cr1_mean(slopes(Dn, on), cl.to_numpy()),
         "pente_arret": cr1_mean(slopes(Dn, off), cl.to_numpy()),
         "ecart_pentes": cr1_mean(slopes(Dn, off) - slopes(Dn, on), cl.to_numpy())}
    return r, event(D, cl, ref)


def main():
    OUT.mkdir(exist_ok=True)
    r1, es, es4, esd = e1c()
    r2, esk = e2c()
    es.to_csv(OUT / "didc_e1_event.csv"); es4.to_csv(OUT / "didc_e1_event_zone4.csv")
    esd.to_csv(OUT / "didc_e1_event_dentistes.csv"); esk.to_csv(OUT / "didc_e2_event_kines.csv")
    res = {"E1c_infirmiers": r1, "E2c_kines": r2}
    (OUT / "didc_results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps(res, indent=1, ensure_ascii=False))
    print(es[["est", "lo", "hi", "n_bv"]].round(4).to_string())


if __name__ == "__main__":
    main()
