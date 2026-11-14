"""Calibration par simulation (SBC) de l'étape 2 : 5 professions × 2 sexes × 200 jeux, θ ré-estimé à chaque jeu.

Pour chaque profession × sexe, on garde le plan d'observation réel (périmètre privé, fenêtre complète jusqu'à
l'origine 2021) et θ̂ ajusté ; chaque jeu tire les effets dans l'a priori(θ̂), simule les données, ré-estime θ,
puis relève le rang de la vraie valeur parmi 99 tirages a posteriori (Talts et al. 2018, § 4.1) :
  sorties (APC)     π(≥ 60 ans, dernière année), w(département médian, 1re tranche), η(même cellule, h = 5)
  entrées (parts)   ζ du département médian et δ de sa région, tranche d'entrée principale
  entrées (niveau)  L_T, niveau national de la tranche d'entrée principale (σ_u, σ_v ré-estimés)
Critère N6 : χ² à 19 ddl sur 20 classes de rangs, p ≥ 0,01 / k (Bonferroni sur les k quantités).
Les mondes N5 de l'axe 3 ne sont pas encore écrits (v2/validation/worlds.py absent) : SBC sur plan réel.
Progression : une ligne k/N par jeu. Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.sbc2 [L]
"""
import json
import sys
import time

import numpy as np
from scipy.stats import chi2

from methodes.cohortes import Cohortes, Level, Shares, kalman
from methodes.perimetres import prive

S_POST = 99


def chi2_p(r):
    obs = np.histogram(r, bins=20, range=(0, S_POST + 1))[0]
    exp = len(r) / 20
    return float(chi2.sf(((obs - exp) ** 2 / exp).sum(), 19))


def apc_ranks(g, th, rng):
    P = g.prior(th).toarray()
    beta = np.linalg.solve(np.linalg.cholesky(P).T, rng.standard_normal(g.p))
    y = g.X @ beta + rng.standard_normal(len(g.y)) * np.sqrt(g.noise(th))
    g.fit(y=y, th0=tuple(th))
    d = g.draws(S_POST, rng)
    nt, o = g.nt, g.off
    dmed = int(np.argsort(np.bincount(g.c, minlength=g.nc))[g.nc // 2])
    nb = g.sizes["mu"]
    q = lambda b: np.array([b[o["pi"] + 2 * nt + nt - 1], b[o["w"] + dmed * nb], g.eta(b, 5)[dmed, 0]])
    tr = q(beta)
    qs = np.array([q(d[:, s]) for s in range(S_POST)])
    return (qs < tr).sum(0)


def share_ranks(sh, th, rng, dmed):
    beta = np.concatenate([rng.standard_normal(sh.nr) * th[0], rng.standard_normal(sh.nd) * th[1]])
    y = sh.X @ beta + rng.standard_normal(len(sh.y)) * np.sqrt(sh.noise(th))
    sh.y = y
    from scipy.optimize import minimize
    sh.z = minimize(lambda z: -sh.loglik(np.exp(z)), np.log(th), method="L-BFGS-B",
                    bounds=[(np.log(1e-4), np.log(3.0))] * 4).x
    thh = np.exp(sh.z)
    d = np.array([sh.draw(thh, rng) for _ in range(S_POST)])
    idx = [sh.reg_i[dmed], sh.nr + dmed]
    return (d[:, idx] < beta[idx]).sum(0)


def level_ranks(M_shape, kap, z, rng):
    su, sv = np.exp(z) * np.sqrt(kap)
    n = len(M_shape)
    L = M_shape[0] + np.cumsum(np.r_[0, rng.standard_normal(n - 1) * sv])
    M = L + rng.standard_normal(n) * su
    lev = Level([M])
    su2, sv2 = np.exp(lev.z) * np.sqrt(max(np.abs(M).mean(), 1.0))
    _, a, P = kalman(M, su2, sv2)
    draws = a + np.sqrt(P) * rng.standard_normal(S_POST)
    return int((draws < L[-1]).sum())


def main():
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t = prive()
    rng = np.random.default_rng(20261114)
    res, t0, k = {}, time.time(), 0
    profs = list(t.profession.unique())
    N = len(profs) * 2 * L
    for p in profs:
        tp = t[(t.profession == p) & (t.year <= 2021)]
        m = Cohortes(tp, (2017 if p == "kines" else 2012, 2021), S=2)
        for sex in ("F", "H"):
            g = next((g for g in m.apc if m.cells.sex.iloc[g.idx[0]] == sex), None)
            ents = [r for r in m.ent if m.cells.sex.iloc[r["idx"][0]] == sex]
            ent = max(ents, key=lambda r: np.abs(r["M"]).mean()) if ents else None
            ranks = {"pi60_T": [], "w_dep_median": [], "eta_h5": [], "zeta_dep_median": [], "delta_region": [],
                     "niveau_L_T": []}
            th_apc = g.theta.copy() if g is not None else None
            th_sh = np.exp(ent["sh"].z) if ent is not None else None
            dmed = int(np.argsort(ent["pi"])[len(ent["pi"]) // 2]) if ent is not None else 0
            for l in range(L):
                if g is not None:
                    r = apc_ranks(g, th_apc, rng)
                    for key, v in zip(("pi60_T", "w_dep_median", "eta_h5"), r):
                        ranks[key].append(int(v))
                if ent is not None:
                    sh = Shares.__new__(Shares)
                    sh.__dict__.update(ent["sh"].__dict__)
                    r = share_ranks(sh, th_sh, rng, dmed)
                    ranks["zeta_dep_median"].append(int(r[1]))
                    ranks["delta_region"].append(int(r[0]))
                    ranks["niveau_L_T"].append(level_ranks(ent["M"], max(np.abs(ent["M"]).mean(), 1.0), m.level.z, rng))
                k += 1
                if k % 10 == 0:
                    print(f"{k}/{N} jeux · {p} {sex} · {time.time() - t0:.0f} s", flush=True)
            kq = sum(1 for v in ranks.values() if v)
            res[f"{p}|{sex}"] = {q: {"p_chi2": chi2_p(np.array(v)), "n": len(v),
                                     "rangs20": np.histogram(v, bins=20, range=(0, 100))[0].tolist()}
                                 for q, v in ranks.items() if v}
            res[f"{p}|{sex}"]["seuil_bonferroni"] = 0.01 / max(kq, 1)
            json.dump(res, open("v2/methodes/out/coh_sbc.json", "w"), indent=1)
    fails = [(c, q) for c, v in res.items() for q, x in v.items() if isinstance(x, dict) and x["p_chi2"] < v["seuil_bonferroni"]]
    print("échecs :", fails, flush=True)


if __name__ == "__main__":
    main()
