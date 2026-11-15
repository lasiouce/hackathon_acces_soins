"""P-B2 : forme du recours standardisé contre l'accessibilité (protocole gelé v2/validation/preregistered/
2026-11-15-besoin-p-b2-saturation.md, amendement A1 ; écarts dans v2/docs/lab/reports/2026-11-15-besoin-pb2-saturation.md).

Run (racine du dépôt) : PYTHONPATH=v2 uv run --with scipy python -m besoin.validation.pb2
                         -> v2/artifacts/besoin_pb2/results.json

  y = log R_std, R_std = moyenne_t R/B₁ normalisée à 1 (France) ; x = log A, A = moyenne_t 100 000 · N/B₁
  spline linéaire, nœuds aux quintiles de x : δ = β_Q5 − ½ β_Q1, IC bootstrap 98,75 % (B = 2 000, départements)
  ΔAIC = AIC_log − AIC_sat ; M2b vit si borne haute IC(δ) < 0 et ΔAIC ≥ 2 ; dégénéré si IC(β_Q1) ∌ (0, +∞)
  placebo : x = log densité standardisée des trois autres professions ; « non attribuable » si même signe et ≥ ½
"""
import json
import subprocess
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from besoin.cube import Population, mapping
from besoin.estimateurs.recours import PROF_AMELI, effectif_ameli, offre_obs, pstd, recours

OUT = Path("v2/artifacts/besoin_pb2")
YEARS, STAB = (2023, 2024, 2025), (2018,)
B, SEED, NIV = 2000, 20261115, 1 - 0.05 / 4                  # gelés : Bonferroni sur 4 professions
IDF = {"75", "92", "93", "94"}


def table(prof, pop, years, offre="jumeau"):
    """DataFrame [département] : R_std, A, et les sommes utiles (R, B₁, N) ; jointure des trois sources."""
    yrs = [y for y in years if y in offre_obs(prof, years).dropna(axis=1, how="all").columns] if offre == "jumeau" \
        else list(years)
    R = recours(prof, years)[list(years)]
    Bs = pstd(prof, pop, years)
    N = offre_obs(prof, yrs) if offre == "jumeau" else effectif_ameli(prof, yrs)
    d = sorted(set(R.dropna().index) & set(Bs.index) & set(N.dropna().index))
    r = (R.loc[d] / Bs.loc[d, list(years)]).mean(axis=1)
    nat = (R.loc[d].sum() / Bs.loc[d, list(years)].sum()).mean()
    A = (1e5 * N.loc[d, yrs] / Bs.loc[d, yrs]).mean(axis=1)
    return pd.DataFrame({"R_std": r / nat, "A": A, "R": R.loc[d].mean(axis=1), "B1": Bs.loc[d, list(years)].mean(axis=1),
                         "N": N.loc[d, yrs].mean(axis=1)}), yrs


def spline(x, y, knots=None):
    """(β_Q1, β_Q5, coef) d'une spline linéaire à nœuds aux quintiles de x."""
    k = np.quantile(x, [.2, .4, .6, .8]) if knots is None else knots
    X = np.column_stack([np.ones_like(x), x] + [np.maximum(x - kk, 0) for kk in k])
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return c[1], c[1:].sum(), c


def aic(rss, n, k):
    return n * np.log(rss / n) + 2 * k


def formes(A, R):
    """ΔAIC = AIC_log − AIC_sat ; NLS saturé non convergé en 200 itérations ⇒ ΔAIC = −∞."""
    from scipy.optimize import curve_fit
    n = len(A)
    X = np.column_stack([np.ones(n), np.log(A)])
    c, *_ = np.linalg.lstsq(X, R, rcond=None)
    rss_log = float(((R - X @ c) ** 2).sum())
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            (rmax, K), _ = curve_fit(lambda a, rm, k: rm * a / (a + k), A, R, p0=[R.max(), np.median(A)], maxfev=200)
        rss_sat = float(((R - rmax * A / (A + K)) ** 2).sum())
        sat = dict(rho_max=float(rmax), K=float(K), converge=True, aic=aic(rss_sat, n, 2))
    except RuntimeError:
        sat = dict(converge=False, aic=float("inf"))
    lg = dict(alpha=float(c[0]), beta=float(c[1]), aic=aic(rss_log, n, 2))
    return dict(sat=sat, log=lg, dAIC=float(lg["aic"] - sat["aic"]))


def sfa(x, y):
    """Frontière stochastique demi-normale y = a + b x + v − u (MV) ; E[u|ε] (Jondrow et coll. 1982)."""
    from scipy.optimize import minimize
    from scipy.stats import norm

    def nll(t):
        a, b, ls_v, ls_u = t
        sv, su = np.exp(ls_v), np.exp(ls_u)
        s, lam = np.hypot(sv, su), su / sv
        e = y - a - b * x
        return -(np.log(2 / s) + norm.logpdf(e / s) + norm.logcdf(-e * lam / s)).sum()

    b0 = np.polyfit(x, y, 1)
    r = minimize(nll, [b0[1], b0[0], np.log(y.std()), np.log(y.std())], method="Nelder-Mead",
                 options=dict(maxiter=5000, xatol=1e-8, fatol=1e-10))
    a, b, ls_v, ls_u = r.x
    sv, su = np.exp(ls_v), np.exp(ls_u)
    e = y - a - b * x
    s2 = sv ** 2 + su ** 2
    mu, ss = -e * su ** 2 / s2, su * sv / np.sqrt(s2)
    u = mu + ss * norm.pdf(mu / ss) / norm.cdf(mu / ss)
    return dict(b=float(b), sigma_u=float(su), sigma_v=float(sv), u=u, converge=bool(r.success))


def passage(prof, pop, years=YEARS, placebo_n=None, excl=(), boot=True):
    t, yrs = table(prof, pop, years)
    t = t.drop(index=[d for d in excl if d in t.index])
    x, y = np.log(t.A.to_numpy()), np.log(t.R_std.to_numpy())
    b1, b5, _ = spline(x, y)
    out = dict(n=len(t), annees_offre=yrs, beta_Q1=float(b1), beta_Q5=float(b5), delta=float(b5 - 0.5 * b1),
               formes=formes(t.A.to_numpy(), t.R_std.to_numpy()))
    if boot:
        rng = np.random.default_rng(SEED)
        bs = np.empty((B, 3))
        for i in range(B):
            j = rng.integers(0, len(x), len(x))
            q1, q5, _ = spline(x[j], y[j])
            bs[i] = q1, q5, q5 - 0.5 * q1
        lo, hi = (1 - NIV) / 2, 1 - (1 - NIV) / 2
        out["IC_delta"] = [float(np.quantile(bs[:, 2], lo)), float(np.quantile(bs[:, 2], hi))]
        out["IC_beta_Q1"] = [float(np.quantile(bs[:, 0], lo)), float(np.quantile(bs[:, 0], hi))]
    return out, t


def verdict(r, plac):
    degen = r["IC_beta_Q1"][0] <= 0
    vit = (r["IC_delta"][1] < 0) and (r["formes"]["dAIC"] >= 2) and not degen
    same = np.sign(plac["beta_Q1"]) == np.sign(r["beta_Q1"]) and abs(plac["beta_Q1"]) >= 0.5 * abs(r["beta_Q1"])
    v = "M2b vit" if vit else "M2b tombe"
    if degen:
        v += " (pas de pente à saturer : IC de β_Q1 contient 0 ou est négatif)"
    if same:
        v += " ; non attribuable (placebo)"
    return v, bool(vit and not same), bool(same)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pop = Population.load()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    res = dict(commit=commit, B=B, seed=SEED, niveau=NIV, professions={})
    tables = {p: table(p, pop, YEARS)[0] for p in PROF_AMELI}
    for p in PROF_AMELI:
        r, t = passage(p, pop)
        # placebo : densité standardisée des trois autres professions (somme de leurs effectifs) sur B₁ de p
        autres = sum(tables[q].N.reindex(t.index) for q in PROF_AMELI if q != p)
        ok = autres.notna()
        xp = np.log((1e5 * autres[ok] / t.B1[ok]).to_numpy())
        b1p, b5p, _ = spline(xp, np.log(t.R_std[ok].to_numpy()))
        plac = dict(n=int(ok.sum()), beta_Q1=float(b1p), beta_Q5=float(b5p))
        v, servi, na = verdict(r, plac)
        # rapporté, non décisif
        stab, _ = passage(p, pop, STAB, boot=False)
        idf, _ = passage(p, pop, excl=IDF, boot=False)
        ta, _ = table(p, pop, YEARS, offre="ameli")
        b1a, b5a, _ = spline(np.log(ta.A.to_numpy()), np.log(ta.R_std.to_numpy()))
        reg = t.assign(reg=mapping("dep", "reg").reindex(t.index).to_numpy()).groupby("reg")[["R", "B1", "N"]].sum()
        reg_f = formes((1e5 * reg.N / reg.B1).to_numpy(), (reg.R / reg.B1 / (reg.R.sum() / reg.B1.sum())).to_numpy())
        s = sfa(np.log(t.A.to_numpy()), np.log(t.R_std.to_numpy()))
        qx = pd.qcut(t.A, 5, labels=False).to_numpy()
        res["professions"][p] = dict(
            decisif=r, placebo=plac, verdict=v, m2b_servi=servi, non_attribuable=na,
            rapporte=dict(annees_2018=dict(beta_Q1=stab["beta_Q1"], beta_Q5=stab["beta_Q5"], delta=stab["delta"],
                                           dAIC=stab["formes"]["dAIC"], annees_offre=stab["annees_offre"]),
                          hors_paris_pc=dict(n=idf["n"], beta_Q1=idf["beta_Q1"], beta_Q5=idf["beta_Q5"],
                                             delta=idf["delta"], dAIC=idf["formes"]["dAIC"]),
                          A_ameli=dict(beta_Q1=float(b1a), beta_Q5=float(b5a),
                                       note="pente biaisée vers 1 par l'erreur commune (A1.1)"),
                          regions=dict(n=len(reg), dAIC=reg_f["dAIC"]),
                          sfa=dict(b=s["b"], sigma_u=s["sigma_u"], sigma_v=s["sigma_v"], converge=s["converge"],
                                   u_moyen_par_quintile=[float(s["u"][qx == k].mean()) for k in range(5)])))
        print(f"{p:13s} n={r['n']} βQ1={r['beta_Q1']:.3f} IC{r['IC_beta_Q1']} βQ5={r['beta_Q5']:.3f} "
              f"δ={r['delta']:.3f} IC{[round(v_, 3) for v_ in r['IC_delta']]} ΔAIC={r['formes']['dAIC']:.2f} "
              f"placebo βQ1={b1p:.3f} -> {v}", flush=True)
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
