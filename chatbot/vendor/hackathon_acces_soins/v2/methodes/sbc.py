"""Calibration par simulation (SBC) et contrôle prédictif a posteriori du modèle APC (étape 1).

SBC : on garde le plan d'observation réel (dentistes, privé, femmes, fenêtre 2012–2021) et θ̂ ajusté ;
pour l = 1..L on tire β ~ a priori(θ̂), y ~ N(Xβ, D(θ̂)), puis la loi a posteriori ; on relève le rang de
la vraie valeur parmi 99 tirages a posteriori pour 4 quantités : π(≥60, dernière année), γ (cohorte du
milieu), w (premier département, première tranche) et η prévu à h = 5 (même cellule).
  A : θ fixé à la vérité (teste le code)        B : θ ré-estimé à chaque jeu (teste le Bayes empirique)
Rangs uniformes attendus (test de Kolmogorov-Smirnov). PPC : couverture à 90 % de y dans l'échantillon,
par profession, origine 2021.
Lancer : PYTHONPATH=v2 uv run --with scipy python -m methodes.sbc  -> v2/methodes/out/apc_sbc.json
"""
import json

import numpy as np
from scipy.stats import kstest

from methodes.apc import APC
from methodes.calibrage import dep_to_region
from methodes.perimetres import prive


def ranks(g, th, rng, L, refit, S=99):
    P = g.prior(th).toarray()
    Lp = np.linalg.cholesky(P)
    o, nt, nb = g.off, g.nt, g.sizes["mu"]
    sen = int(np.argmax(g.ages[g.bands] >= 60)) if (g.ages[g.bands] >= 60).any() else 0
    q = lambda beta: np.array([beta[o["pi"] + 2 * nt + nt - 1], beta[o["gamma"] + g.sizes["gamma"] // 2],
                               beta[o["w"]], g.eta(beta, 5)[0, 0]])
    out = []
    for _ in range(L):
        beta = np.linalg.solve(Lp.T, rng.standard_normal(g.p))
        y = g.X @ beta + rng.standard_normal(len(g.y)) * np.sqrt(g.noise(th))
        if refit:
            g.fit(y=y, th0=tuple(th))
        else:
            g.theta = th
            g.P, g.Q, g.L, _, g.m, _ = g.posterior(th, y)
        d = g.draws(S, rng)
        tr = q(beta)
        out.append([(np.array([q(d[:, s])[j] for s in range(S)]) < tr[j]).sum() for j in range(4)])
    return np.array(out)


def main():
    t = prive()
    rng = np.random.default_rng(20261114)
    tp = t[(t.profession == "dentistes") & (t.year <= 2021)]
    m = APC(tp, (2012, 2021), dep_to_region(), S=10)
    g = m.groups[0]
    th = g.theta.copy()
    res = {"theta_vrai": th.tolist()}
    for label, refit, L in (("A_theta_fixe", False, 200), ("B_theta_reestime", True, 40)):
        r = ranks(g, th, rng, L, refit)
        res[label] = {"L": L, "ks_p": [float(kstest(r[:, j] / 99.0, "uniform").pvalue) for j in range(4)],
                      "quantites": ["pi_60plus_T", "gamma_milieu", "w_dep1_tranche1", "eta_h5"],
                      "hist_rangs_5": [np.histogram(r[:, j], bins=5, range=(0, 99))[0].tolist() for j in range(4)]}
        print(label, res[label]["ks_p"])
    ppc = {}
    for p in t.profession.unique():
        tp = t[(t.profession == p) & (t.year <= 2021)]
        mm = APC(tp, (2017 if p == "kines" else 2012, 2021), dep_to_region(), S=10)
        cov = []
        for g in mm.groups:
            mu = g.X @ g.m
            sd = np.sqrt(g.noise(g.theta))
            cov.append(np.abs(g.y - mu) <= 1.645 * sd)
        ppc[p] = float(np.concatenate(cov).mean())
    res["ppc_couverture90_y"] = ppc
    print("PPC", ppc)
    open("v2/methodes/out/apc_sbc.json", "w").write(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
