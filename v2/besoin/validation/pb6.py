"""P-B6 : la vaccination antigrippale en officine a-t-elle ajouté des vaccinations (m > 0) ?

Protocole gelé : v2/validation/preregistered/2026-11-15-besoin-p-b6-grippe-officine.md, amendement A1 (§ A1.4) ;
écarts écrits avant calcul dans v2/docs/lab/reports/2026-11-15-besoin-p-b6-grippe-officine.md (commit 2d20495).

Run (racine du dépôt) : uv run python v2/besoin/validation/pb6.py [--raw <dossier insee>]
Sortie : v2/besoin/validation/out/pb6.json

Différence de différences à adoption échelonnée (Sun et Abraham 2021), 12 zones métropolitaines d'Open Medic,
années civiles 2014–2018, y = log(boîtes J07BB pour 1 000 habitants). Cohortes : g = 2017 (ARA 84, NA 75),
g = 2018 (HdF 32, Occitanie 76), contrôle g = 2019 (les 8 autres zones).
"""
from __future__ import annotations

import functools
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "v2" / "data" / "processed" / "besoin"
OUT = Path(__file__).resolve().parent / "out"
SEED = 20261115
B = 9_999
ANNEES = list(range(2014, 2019))
ZONES = [11, 24, 27, 28, 32, 44, 52, 53, 75, 76, 84, 93]
COHORTE = {84: 2017, 75: 2017, 32: 2018, 76: 2018}  # le reste : 2019 (généralisation)
CELLULES = [(2017, -3), (2017, -2), (2017, 0), (2017, 1), (2018, -4), (2018, -3), (2018, -2), (2018, 0)]
POST = [(2017, 0), (2017, 1), (2018, 0)]


@functools.lru_cache
def population(raw: Path) -> pd.Series:
    x = pd.read_excel(raw / "base-pop-historiques-1876-2023.xlsx", sheet_name=0, header=5, engine="calamine")
    cols = [f"PMUN{a}" for a in ANNEES]
    x["REG"] = pd.to_numeric(x["REG"], errors="coerce")
    x.loc[x["REG"] == 94, "REG"] = 93  # Corse rattachée à PACA (écart 2, supposé)
    p = x.groupby("REG")[cols].sum().loc[ZONES]
    p.columns = ANNEES
    s = p.stack().rename("pop")
    s.index.names = ["reg", "annee"]
    return s


def panel(age: int | None, mesure: str = "boites", raw: Path | None = None) -> pd.DataFrame:
    m = pd.read_parquet(PROC / "medic_vaccins.parquet")
    m = m[(m.atc4 == "J07BB") & m.annee.isin(ANNEES) & m.ben_reg.isin(ZONES)]
    if age is not None:
        m = m[m.age == age]
    d = m.groupby(["ben_reg", "annee"])[mesure].sum().rename("doses").to_frame()
    d.index.names = ["reg", "annee"]
    d = d.join(population(raw))
    d["y"] = np.log(d["doses"] / d["pop"] * 1000)
    return d.reset_index()


def design(d: pd.DataFrame, cohorte: dict[int, int]) -> tuple[np.ndarray, list[str]]:
    regs, ans = sorted(d.reg.unique()), sorted(d.annee.unique())
    cols, X = [], []
    X.append(np.ones(len(d))); cols.append("const")
    for r in regs[1:]:
        X.append((d.reg == r).astype(float).values); cols.append(f"reg{r}")
    for a in ans[1:]:
        X.append((d.annee == a).astype(float).values); cols.append(f"an{a}")
    g = d.reg.map(lambda r: cohorte.get(r, 2019)).values
    e = d.annee.values - g
    for (gg, ee) in CELLULES:
        X.append(((g == gg) & (e == ee)).astype(float)); cols.append(f"g{gg}e{ee}")
    return np.column_stack(X), cols


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def att(beta, cols):
    return float(np.mean([beta[cols.index(f"g{g}e{e}")] for g, e in POST]))


def wild(d, cohorte, b=B, imposer=False, rng=None):
    """Bootstrap sauvage par région (poids de Webb). Renvoie les tirages de l'ATT (et des coefficients avant)."""
    X, cols = design(d, cohorte)
    y = d.y.values
    if imposer:  # H0 : ATT = 0 imposée par la contrainte Σ post = 0 (reparamétrage)
        idx = [cols.index(f"g{g}e{e}") for g, e in POST]
        Xr = X.copy()
        for k in idx[1:]:
            Xr[:, k] = X[:, k] - X[:, idx[0]]
        Xr = np.delete(Xr, idx[0], axis=1)
        br = ols(Xr, y)
        fit = Xr @ br
    else:
        fit = X @ ols(X, y)
    res = y - fit
    regs = d.reg.values
    uniq = np.unique(regs)
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5), np.sqrt(0.5), 1, np.sqrt(1.5)])
    out_att, out_pre = [], []
    for _ in range(b):
        v = dict(zip(uniq, rng.choice(webb, size=len(uniq))))
        ys = fit + res * np.array([v[r] for r in regs])
        bs = ols(X, ys)
        out_att.append(att(bs, cols))
        out_pre.append([bs[cols.index("g2017e-3")], bs[cols.index("g2017e-2")]])
    return np.array(out_att), np.array(out_pre)


def estimer(d, cohorte, rng, avec_p=True):
    X, cols = design(d, cohorte)
    beta = ols(X, d.y.values)
    a = att(beta, cols)
    sa, spre = wild(d, cohorte, rng=rng)
    ic = [2 * a - float(np.quantile(sa, 0.975)), 2 * a - float(np.quantile(sa, 0.025))]
    r = {"att": a, "ic95": ic,
         "pre": {f"g2017e{e}": {"coef": float(beta[cols.index(f'g2017e{e}')]),
                                "ic95": [2 * beta[cols.index(f'g2017e{e}')] - float(np.quantile(spre[:, i], 0.975)),
                                         2 * beta[cols.index(f'g2017e{e}')] - float(np.quantile(spre[:, i], 0.025))]}
                 for i, e in enumerate([-3, -2])}}
    if avec_p:
        s0, _ = wild(d, cohorte, imposer=True, rng=rng)
        r["p_boot"] = float((np.abs(s0) >= abs(a)).mean())
    return r, beta, cols


def permutation(d) -> tuple[float, int]:
    a_obs = None
    vals = []
    for g17 in itertools.combinations(ZONES, 2):
        reste = [z for z in ZONES if z not in g17]
        for g18 in itertools.combinations(reste, 2):
            coh = {z: 2017 for z in g17} | {z: 2018 for z in g18}
            X, cols = design(d, coh)
            vals.append(att(ols(X, d.y.values), cols))
    X, cols = design(d, COHORTE)
    a_obs = att(ols(X, d.y.values), cols)
    vals = np.array(vals)
    return float((np.abs(vals) >= abs(a_obs) - 1e-12).mean()), len(vals)


def s_de_t() -> dict:
    iq = pd.read_parquet(PROC / "iqvia_campagne.parquet")
    iq = iq[iq.variable == "ACTE(VGP)"][["campagne", "date", "valeur"]].copy()
    iq["annee"] = iq.campagne.str.slice(0, 4).astype(int)
    m = pd.read_parquet(PROC / "medic_vaccins.parquet")
    j = m[(m.atc4 == "J07BB")].groupby("annee").boites.sum()
    iq["boites_J07BB"] = iq.annee.map(j)
    iq["s"] = iq.valeur / iq.boites_J07BB
    iq["partielle"] = iq.date.astype(str).str.startswith("2026")  # campagne 2025-26 arrêtée au 28/02/2026
    fit = iq[~iq.partielle]
    out = {"serie": iq[["campagne", "valeur", "boites_J07BB", "s", "partielle"]].to_dict("records")}
    if len(fit) >= 3:
        f = lambda t, s_inf, tau: s_inf * (1 - np.exp(-(t - 2019) / tau))  # noqa: E731
        try:
            (s_inf, tau), cov = curve_fit(f, fit.annee.values.astype(float), fit.s.values, p0=[0.8, 3.0], maxfev=20000)
            out["ajustement"] = {"t0": 2019, "s_inf": float(s_inf), "tau": float(tau),
                                 "se": [float(np.sqrt(cov[0, 0])), float(np.sqrt(cov[1, 1]))], "n": int(len(fit))}
        except RuntimeError as e:
            out["ajustement"] = {"echec": str(e)}
    return out


def main() -> None:
    raw = Path(sys.argv[sys.argv.index("--raw") + 1]) if "--raw" in sys.argv else ROOT / "v2" / "data" / "raw" / "insee"
    rng = np.random.default_rng(SEED)
    d = panel(None, raw=raw)
    assert d.shape[0] == 60 and d.doses.notna().all() and d["pop"].notna().all(), "panel incomplet : non faisable"
    principal, beta, cols = estimer(d, COHORTE, rng)
    p_perm, n_perm = permutation(d)
    post = d.assign(g=d.reg.map(lambda r: COHORTE.get(r, 2019)))
    post = post[[(g, a - g) in POST for g, a in zip(post.g, post.annee)]]
    m_doses = float((post.doses * (1 - np.exp(-principal["att"]))).sum() / 2)
    pre_rejet = any(not (lo <= 0 <= hi) for lo, hi in (v["ic95"] for v in principal["pre"].values()))
    ic = principal["ic95"]
    if pre_rejet:
        verdict = "tendances parallèles rejetées : m reste supposé (0)"
    elif ic[0] <= 0 <= ic[1]:
        verdict = "m = 0 retenu (IC 95 % contient 0)"
    elif ic[0] > 0 and p_perm < 0.05:
        verdict = "m > 0 retenu"
    elif ic[1] < 0:
        verdict = "m < 0 : inattendu, m reste supposé (0)"
    else:
        verdict = "non tranché : m reste supposé (0)"
    placebo, _, _ = estimer(panel(0, raw=raw), COHORTE, rng, avec_p=False)
    if not (placebo["ic95"][0] <= 0 <= placebo["ic95"][1]):
        verdict += " ; placebo 0–19 ans dont l'IC exclut 0 : non attribuable"
    sec = {
        "60_plus": estimer(panel(60, raw=raw), COHORTE, rng, avec_p=False)[0],
        "sans_g2018": None,
        "montants": estimer(panel(None, mesure="rem", raw=raw), COHORTE, rng, avec_p=False)[0],
    }
    d2 = d[~d.reg.isin([32, 76])]
    X2, c2 = design(d2, {84: 2017, 75: 2017})
    sec["sans_g2018"] = {"att_g2017": float(np.mean([ols(X2, d2.y.values)[c2.index(f"g2017e{e}")] for e in (0, 1)]))}
    res = {"protocole": "P-B6", "amendement": "A1 §A1.4", "graine": SEED, "B": B,
           "panel": {"zones": ZONES, "annees": ANNEES, "n": int(d.shape[0])},
           "principal": principal, "permutation": {"p": p_perm, "n": n_perm},
           "m_doses_par_saison": m_doses, "verdict": verdict, "placebo_0_19": placebo,
           "secondaires": sec, "s_t": s_de_t(),
           "doses_regions": {str(int(r)): {str(int(a)): int(v) for a, v in row.items()} for r, row in d.pivot(index="reg", columns="annee", values="doses").iterrows()}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pb6.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float))
    print(json.dumps({k: res[k] for k in ["principal", "permutation", "m_doses_par_saison", "verdict"]},
                     indent=1, ensure_ascii=False, default=float))
    print("placebo", json.dumps(placebo, default=float))
    print("secondaires", json.dumps(sec, default=float))
    print("s(t)", json.dumps(res["s_t"], default=float, ensure_ascii=False))


if __name__ == "__main__":
    main()
