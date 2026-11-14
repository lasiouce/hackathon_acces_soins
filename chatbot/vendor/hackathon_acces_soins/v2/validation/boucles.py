"""Axe 3, N9 (SHA-256 96a39bc087bb…) : signe des boucles B2 (densité → installations nettes) et B1 (densité → départs
avant 60 ans).

Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.boucles -> v2/validation/out/boucles_results.json
MCO avec effets fixes en indicatrices, variance robuste par grappe = département (CR1), Student à G − 1 ddl.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"
B2P = {"ide": "infirmiers", "mk": "kines", "cd": "dentistes"}
B1P = ["sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers-liberaux"]


def ols_cr1(y, X, fe: pd.DataFrame, cl):
    """y ~ X (+ indicatrices des colonnes de fe) ; renvoie β, se, IC pour les colonnes de X."""
    D = [pd.get_dummies(fe[c].astype(str), prefix=c, drop_first=True, dtype=float) for c in fe]
    Z = pd.concat([X.reset_index(drop=True)] + [d.reset_index(drop=True) for d in D], axis=1)
    Z.insert(0, "const", 1.0)
    ok = np.isfinite(Z.to_numpy()).all(1) & np.isfinite(y)
    Z, yv, cl = Z[ok].to_numpy(float), np.asarray(y)[ok], np.asarray(cl)[ok]
    n, k = Z.shape
    ZtZi = np.linalg.pinv(Z.T @ Z)
    b = ZtZi @ Z.T @ yv
    u = yv - Z @ b
    S = pd.DataFrame(Z * u[:, None]).groupby(cl).sum().to_numpy()
    G = len(S)
    V = ZtZi @ (S.T @ S) @ ZtZi * G / (G - 1) * (n - 1) / (n - k)
    q = stats.t.ppf(0.975, G - 1)
    out = {}
    for j, c in enumerate(X.columns, start=1):
        se = float(np.sqrt(V[j, j]))
        out[c] = {"b": float(b[j]), "se": se, "lo": float(b[j] - q * se), "hi": float(b[j] + q * se),
                  "p": float(2 * stats.t.sf(abs(b[j]) / se, G - 1)), "n": int(n), "G": int(G)}
    return out


def verdict(r, expected_sign):
    if r["hi"] < 0:
        s = -1
    elif r["lo"] > 0:
        s = 1
    else:
        return "nul"
    return "confirmé" if s == expected_sign else "contraire"


def placebo_rule(v, main, pl):
    if v in ("confirmé", "contraire") and np.sign(pl["b"]) == np.sign(main["b"]) and abs(pl["b"]) >= 0.5 * abs(main["b"]):
        return "non attribuable"
    return v


# ---------------- B2 ----------------
def b2_panel():
    a = pd.read_parquet(ROOT / "v2/data/processed/commune_attributs.parquet")
    a = a[a.bv2022.notna()]
    for z in ("ide", "mk", "cd"):
        for v in ("2012", "actuel"):
            col = f"z_{z}_{v}"
            for st in ("incitation", "remplacement_seul"):
                a[f"{col}_{st}"] = (a[col] == st) * a.population
    a["p014"] = a.part_0_14 * a.population
    a["p65"] = a.part_65p * a.population
    num = [c for c in a.columns if c.startswith(("lib_", "inet_")) or c.endswith(("_incitation", "_remplacement_seul"))]
    g = a.groupby(["bv2022", "year"])[num + ["population", "p014", "p65"]].sum()
    g["dep"] = a.groupby(["bv2022", "year"]).dep.agg(lambda x: x.mode().iloc[0])
    return g.reset_index()


def b2():
    g = b2_panel().sort_values(["bv2022", "year"])
    res = {}
    for z, prof in B2P.items():
        d = g.copy()
        by = d.groupby("bv2022")
        others = [o for o in B2P if o != z]
        d["P1"] = by.population.shift(1)
        d["P2"] = by.population.shift(2)
        d["y"] = 1e5 * d[f"inet_{z}"] / d.P1
        d["logD2"] = np.log1p(1e5 * by[f"lib_{z}"].shift(2) / d.P2)
        d["logD1"] = np.log1p(1e5 * by[f"lib_{z}"].shift(1) / d.P1)
        d["logO2"] = np.log1p(1e5 * sum(by[f"lib_{o}"].shift(2) for o in others) / d.P2)
        d["logP1"] = np.log(d.P1)
        d["s014"], d["s65"] = d.p014 / d.population, d.p65 / d.population
        zc = []
        for v in ("2012", "actuel"):
            for st in ("incitation", "remplacement_seul"):
                c = f"z_{z}_{v}_{st}"
                d[c + "_s"] = d[c] / d.population
                zc.append(c + "_s")
        d = d[(d.year >= 2014) & (d.P1 >= 1000)]
        ctrl = ["logP1", "s014", "s65"]
        fe, cl = d[["dep", "year"]], d.dep
        main = ols_cr1(d.y.to_numpy(), d[["logD2"] + ctrl + zc], fe, cl)["logD2"]
        pl = ols_cr1(d.y.to_numpy(), d[["logO2"] + ctrl + zc], fe, cl)["logO2"]
        v = placebo_rule(verdict(main, -1), main, pl)
        res[prof] = {"principal": main, "placebo_autres": pl, "verdict": v,
                     "sans_zonage": ols_cr1(d.y.to_numpy(), d[["logD2"] + ctrl], fe, cl)["logD2"],
                     "decalage_1an": ols_cr1(d.y.to_numpy(), d[["logD1"] + ctrl + zc], fe, cl)["logD1"],
                     "propre_et_autres": ols_cr1(d.y.to_numpy(), d[["logD2", "logO2"] + ctrl + zc], fe, cl),
                     "y_moyen_pour_100k": float(d.y.mean()), "ecart_type_logD2": float(d.logD2.std()),
                     "n_bv": int(d.bv2022.nunique())}
    return res


# ---------------- B1 ----------------
def b1():
    s = pd.read_parquet(ROOT / "data/processed/stock.parquet")
    s = s[(s.mode3 == "liberal_mixte") & s.profession.isin(B1P) & ~s.dep.isin(["999", "20"])
          & ((s.profession != "kines") | (s.source == "RPPS"))]
    a = pd.read_parquet(ROOT / "v2/data/processed/commune_attributs.parquet")
    pop = a.groupby(["dep", "year"]).population.sum()
    reg = a.groupby("dep").reg.agg(lambda x: x.mode().iloc[0])
    tot = s.groupby(["profession", "dep", "year"]).n.sum().unstack("profession").fillna(0)
    res = {}
    for prof in B1P:
        sp = s[s.profession == prof]
        b4554 = sp[sp.age_lo.isin([45, 50])].groupby(["dep", "year"]).n.sum()
        b5059 = sp[sp.age_lo.isin([50, 55])].groupby(["dep", "year"]).n.sum()
        last = int(sp.year.max())
        rows = []
        for (dep, t), base in b4554.items():
            if t + 5 > last or base < 30 or (dep, t + 5) not in b5059.index or (dep, t) not in pop.index:
                continue
            P = pop[(dep, t)]
            others = tot.loc[(dep, t)].drop(prof).sum() if (dep, t) in tot.index else np.nan
            rows.append({"dep": dep, "year": t, "reg": reg.get(dep), "logR": np.log(b5059[(dep, t + 5)] / base),
                         "logD": np.log(1e5 * tot.loc[(dep, t), prof] / P), "logO": np.log(1e5 * others / P),
                         "logP": np.log(P), "logB": np.log(base)})
        d = pd.DataFrame(rows).dropna(subset=["reg"])
        fe, cl = d[["reg", "year"]], d.dep
        main = ols_cr1(d.logR.to_numpy(), d[["logD", "logP", "logB"]], fe, cl)["logD"]
        pl = ols_cr1(d.logR.to_numpy(), d[["logO", "logP", "logB"]], fe, cl)["logO"]
        res[prof] = {"principal": main, "placebo_autres": pl, "verdict": placebo_rule(verdict(main, 1), main, pl),
                     "annees": [int(d.year.min()), int(d.year.max())], "n_dep": int(d.dep.nunique()),
                     "R_moyen": float(np.exp(d.logR).mean())}
    return res


def main():
    OUT.mkdir(exist_ok=True)
    res = {"B2": b2(), "B1": b1()}
    (OUT / "boucles_results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for k in ("B2", "B1"):
        for p, r in res[k].items():
            m, pl = r["principal"], r["placebo_autres"]
            print(f"{k} {p:20s} β={m['b']:+.3f} [{m['lo']:+.3f};{m['hi']:+.3f}] n={m['n']} G={m['G']} | "
                  f"placebo {pl['b']:+.3f} [{pl['lo']:+.3f};{pl['hi']:+.3f}] -> {r['verdict']}")
    for p, r in res["B2"].items():
        print("B2", p, "sans zonage", round(r["sans_zonage"]["b"], 3), "D(t-1)", round(r["decalage_1an"]["b"], 3),
              "propre|autres", {c: round(v["b"], 3) for c, v in r["propre_et_autres"].items() if c in ("logD2", "logO2")},
              "y moyen", round(r["y_moyen_pour_100k"], 2))


if __name__ == "__main__":
    main()
