"""Étape 2 du programme de l'axe 2 : cohortes par composantes, rétention ET entrées probabilistes.

Dérivation : v2/docs/lab/derivations/2026-11-14-axe2-cohortes-bayesiennes.md. Par profession × sexe :
  sorties   tranches où la rétention nationale ≤ 1 : APC gaussien de l'étape 1 (methodes.apc.Group)
  entrées   autres tranches (les plus jeunes) : flux net e_{d,τ} = N(a,τ) − s_d·B(a,τ−1) (s de A0)
            M_τ = Σ_d e_{d,τ} ; niveau local M_τ = L_τ + u_τ, L_τ = L_{τ−1} + v_τ (Kalman, σ_u et σ_v par
            maximum de vraisemblance, en relatif, communs aux sexes et tranches d'une profession)
            e_{d,τ} = π_d·M_τ·(1 + δ_rég + ζ_d) + ε,  δ ~ N(0,τ_r²), ζ ~ N(0,τ_d²), ε ~ N(0, σ_ε²·π_d|M̄| + ω_e²)
θ : maximum de la vraisemblance marginale ; `laplace=True` propage θ (log θ ~ N(log θ̂, H⁻¹), hessienne
numérique), chaque tirage reprenant la loi gaussienne exacte sachant θ_k.
Branchement : un module `cohortes` (produit les flux "sorties" et "entrees"), après methodes_vieillissement.
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.optimize import minimize

from jumeau.module import Add, Module, Param, Rate, register
from jumeau.scenario import Scenario
from jumeau.state import AXES
from methodes import apc as APCmod
from methodes.calibrage import Ages, dep_to_region, fit as calib_fit
from methodes.estimators import MethodEstimator
from sante.model import _cube

H_MAX = 30
LO, HI = np.log(1e-4), np.log(3.0)


def laplace(negll, z0, S, rng, step=0.05):
    """Tirages de log θ ~ N(z0, H⁻¹), H = hessienne numérique de negll en z0 (valeurs propres bornées)."""
    k = len(z0)
    H = np.zeros((k, k))
    f0 = negll(z0)
    for i in range(k):
        for j in range(i, k):
            ei, ej = np.eye(k)[i] * step, np.eye(k)[j] * step
            if i == j:
                H[i, i] = (negll(z0 + ei) - 2 * f0 + negll(z0 - ei)) / step ** 2
            else:
                H[i, j] = H[j, i] = (negll(z0 + ei + ej) - negll(z0 + ei - ej) - negll(z0 - ei + ej)
                                     + negll(z0 - ei - ej)) / (4 * step ** 2)
    w, V = np.linalg.eigh(H)
    w = np.maximum(w, 1.0)                       # direction plate : écart-type ≤ 1 en log (facteur e)
    C = (V / w) @ V.T
    z = z0[None, :] + rng.standard_normal((S, k)) @ np.linalg.cholesky(C).T
    return np.clip(z, LO, HI)


# --- entrées : niveau national (niveau local) -------------------------------------------------------
def kalman(m, su, sv, p0=None):
    """Filtre du niveau local sur la série m ; renvoie (log-vraisemblance, L_T|T, P_T|T). Premier point : diffus."""
    a = m[0]
    P, ll = (1e2 * (su ** 2 + sv ** 2 + 1) if p0 is None else p0), 0.0
    for t, y in enumerate(m):
        if t > 0:
            P = P + sv ** 2
        F = P + su ** 2
        v = y - a
        if t > 0:
            ll += -0.5 * (np.log(2 * np.pi * F) + v * v / F)
        K = P / F
        a, P = a + K * v, P * (1 - K)
    return ll, a, P


class Level:
    """σ_u, σ_v communs aux séries d'une profession ; variances absolues ∝ taille de la série (κ = moyenne de |M|) :
    u ~ N(0, σ_u²·κ), v ~ N(0, σ_v²·κ) (forme de Poisson, pour que les petites séries ne dictent pas les grandes)."""

    def __init__(self, series: list):
        self.series = [(M, max(np.abs(M).mean(), 1.0)) for M in series]
        self.z = minimize(self.negll, np.log([1.0, 0.5]), method="L-BFGS-B", bounds=[(LO, np.log(30.0))] * 2).x

    def negll(self, z):
        su, sv = np.exp(z)
        return -sum(kalman(M, su * np.sqrt(k), sv * np.sqrt(k))[0] for M, k in self.series)


# --- entrées : répartition hiérarchique ---------------------------------------------------------------
class Shares:
    """e_{d,τ} − π_d M_τ = π_d M_τ (δ_rég + ζ_d) + ε ; posterior gaussien exact sachant θ = (τ_r, τ_d, σ_ε, ω_e)."""

    def __init__(self, e, M, pi, reg_i):
        nd, nt = e.shape
        self.nd, self.nr = nd, int(reg_i.max()) + 1
        x = (pi[:, None] * M[None, :])                                # [d, τ]
        self.y = (e - x).ravel()
        d = np.repeat(np.arange(nd), nt)
        xv = x.ravel()
        self.scale = np.repeat(pi * max(np.abs(M).mean(), 1.0), nt)
        rows = np.concatenate([np.arange(nd * nt)] * 2)
        cols = np.concatenate([reg_i[d], self.nr + d])
        self.X = sp.csr_matrix((np.concatenate([xv, xv]), (rows, cols)), shape=(nd * nt, self.nr + nd))
        self.p = self.nr + nd
        self.reg_i = reg_i
        self.z = minimize(lambda z: -self.loglik(np.exp(z)), np.log([0.05, 0.1, 0.5, 0.5]), method="L-BFGS-B",
                          bounds=[(LO, HI)] * 4).x

    def noise(self, th):
        return th[2] ** 2 * self.scale + th[3] ** 2

    def posterior(self, th):
        pdiag = np.concatenate([np.full(self.nr, 1 / th[0] ** 2), np.full(self.nd, 1 / th[1] ** 2)])
        dinv = 1 / self.noise(th)
        XtD = self.X.T.multiply(dinv).tocsr()
        Q = np.diag(pdiag) + (XtD @ self.X).toarray()
        b = XtD @ self.y
        L = np.linalg.cholesky(Q)
        m = np.linalg.solve(L.T, np.linalg.solve(L, b))
        return pdiag, L, b, m, dinv

    def loglik(self, th):
        pdiag, L, b, m, dinv = self.posterior(th)
        return 0.5 * (np.log(pdiag).sum() - 2 * np.log(np.diag(L)).sum() + np.log(dinv).sum()
                      - (dinv * self.y ** 2).sum() + b @ m)

    def draw(self, th, rng):
        _, L, _, m, _ = self.posterior(th)
        return m + np.linalg.solve(L.T, rng.standard_normal(self.p))

    def mean(self):
        return self.posterior(np.exp(self.z))[3]

    def factor(self, beta):
        """1 + δ_rég + ζ_d, par département."""
        return 1 + beta[self.reg_i] + beta[self.nr:]


# --- modèle complet -----------------------------------------------------------------------------------
class Cohortes:
    def __init__(self, t, fit_years, S=200, laplace_theta=False, seed=20261114):
        N, cells, ages, years = _cube(t)
        yi = (years >= fit_years[0]) & (years <= fit_years[1])
        N, years = N[:, :, yi], years[yi]
        A = Ages(ages)
        base = np.stack([A.age(N[:, :, k], "uniforme") for k in range(N.shape[2] - 1)], axis=2)
        c0 = calib_fit(t, fit_years, shrink=200.0)                    # A0 : s et I
        s0, I0 = c0["s"], c0["inflow"]
        d2r = dep_to_region()
        self.cells, self.ages, self.S = cells, ages, S
        rng = np.random.default_rng(seed)
        self.apc, self.ent = [], []
        series, pending = [], []
        for _, idx in cells.groupby(["profession", "sex"]).indices.items():
            num, den = N[idx][:, :, 1:].sum((0, 2)), base[idx].sum((0, 2))
            rnat = num / np.maximum(den, 1e-9)
            apc_b, ent_b = np.flatnonzero(rnat <= 1.0), np.flatnonzero(rnat > 1.0)
            reg = cells.dep.iloc[idx].map(d2r).fillna("?").to_numpy()
            if len(apc_b):
                g = APCmod.Group(N[idx], base[idx], ages, years, cells.dep.iloc[idx].to_numpy(), reg, apc_b).fit()
                g.idx = idx
                self._apc_draws(g, S, rng, laplace_theta)
                self.apc.append(g)
            _, reg_i = np.unique(reg, return_inverse=True)
            for a in ent_b:
                e = N[idx][:, a, 1:] - s0[idx, a][:, None] * base[idx][:, a, :]      # [d, τ]
                M = e.sum(0)
                pi = N[idx][:, a, -1] / max(N[idx][:, a, -1].sum(), 1e-9)
                sh = Shares(e, M, pi, reg_i)
                rec = {"idx": idx, "a": a, "M": M, "pi": pi, "sh": sh, "I0": I0[idx, a]}
                series.append(M)
                pending.append(rec)
        self.level = Level(series) if series else None
        for rec in pending:
            self._ent_draws(rec, S, rng, laplace_theta)
            self.ent.append(rec)
        self.s0, self.I0 = s0, I0

    def _apc_draws(self, g, S, rng, lap):
        if lap:
            zs = laplace(lambda z: -g.loglik(np.exp(z)), np.log(g.theta), S, rng)
        else:
            zs = np.tile(np.log(g.theta), (S, 1))
        g.thetas = np.exp(zs)
        g.beta = np.empty((g.p, S))
        same = not lap
        if same:
            g.beta = g.draws(S, rng)
        else:
            for k in range(S):
                _, _, L, _, m, _ = g.posterior(g.thetas[k])
                g.beta[:, k] = m + np.linalg.solve(L.T, rng.standard_normal(g.p))
        g.dpi = np.cumsum(rng.standard_normal((S, 3, H_MAX)) * g.thetas[:, 0][:, None, None], axis=2)
        g.dg = np.cumsum(rng.standard_normal((S, H_MAX)) * g.thetas[:, 1][:, None], axis=1)
        g.zn = rng.standard_normal((S, H_MAX, g.nc, len(g.bands)))

    def _ent_draws(self, rec, S, rng, lap):
        sh = rec["sh"]
        M, nd = rec["M"], sh.nd
        mbar = M.mean()
        # niveau national : point et tirages
        kap = max(np.abs(M).mean(), 1.0)
        zl = laplace(self.level.negll, self.level.z, S, rng) if lap else np.tile(self.level.z, (S, 1))
        su0, sv0 = np.exp(self.level.z) * np.sqrt(kap)
        rec["L_point"] = kalman(M, su0, sv0)[1]
        paths = np.empty((S, H_MAX))
        for k in range(S):
            su, sv = np.exp(zl[k]) * np.sqrt(kap)
            _, a, P = kalman(M, su, sv)
            lev = a + np.sqrt(P) * rng.standard_normal() + np.cumsum(rng.standard_normal(H_MAX) * sv)
            paths[k] = lev + rng.standard_normal(H_MAX) * su
        rec["M_paths"] = paths
        # répartition
        zs = laplace(lambda z: -sh.loglik(np.exp(z)), sh.z, S, rng) if lap else np.tile(sh.z, (S, 1))
        rec["fac_point"] = sh.factor(sh.mean())
        fac = np.empty((S, nd))
        nsd = np.empty((S, nd))
        for k in range(S):
            th = np.exp(zs[k])
            fac[k] = sh.factor(sh.draw(th, rng))
            nsd[k] = np.sqrt(th[2] ** 2 * rec["pi"] * kap + th[3] ** 2)
        rec["fac"], rec["nsd"] = fac, nsd
        rec["eps"] = rng.standard_normal((S, H_MAX, nd))

    def rates(self, h, draw=-1):
        """(s, I) [cellule du cube, tranche] pour l'année origine + h ; draw = -1 : moyenne a posteriori."""
        s, I = self.s0.copy(), self.I0.copy()
        for g in self.apc:
            if draw < 0:
                e = g.eta(g.m, h)
                s[np.ix_(g.idx, g.bands)] = np.minimum(1.0, np.exp(e))
            else:
                e = g.eta(g.beta[:, draw], h, (g.dpi[draw], g.dg[draw]))
                th = g.thetas[draw]
                Blast = np.maximum(self._blast(g), 1.0)
                sd = np.sqrt(th[4] ** 2 / Blast + th[5] ** 2)
                s[np.ix_(g.idx, g.bands)] = np.minimum(1.0, np.exp(e)) * np.exp(sd * g.zn[draw, h - 1] - sd ** 2 / 2)
        for r in self.ent:
            if draw < 0:
                I[r["idx"], r["a"]] = r["pi"] * r["L_point"] * r["fac_point"]
            else:
                I[r["idx"], r["a"]] = (r["pi"] * r["M_paths"][draw, h - 1] * r["fac"][draw]
                                       + r["nsd"][draw] * r["eps"][draw, h - 1])
        return s, I

    def _blast(self, g):
        if not hasattr(g, "_B"):
            g._B = np.array([[g.B[(g.c == c) & (g.a == b)][-1] if ((g.c == c) & (g.a == b)).any() else 1.0
                              for b in g.bands] for c in range(g.nc)])
        return g._B


# --- branchement sur le jumeau ------------------------------------------------------------------------
def cohortes_of(hist, state):
    key = ("cohortes", len(state.cells))
    if key not in hist._cache:
        t = hist.table.rename(columns={hist.level: "dep"})
        t = t.drop(columns="sector") if "sector" in t else t
        o = hist.options
        m = Cohortes(t, hist.fit_years, S=o.get("S", 200), laplace_theta=o.get("laplace", False))
        idx = state.index(m.cells.rename(columns={"dep": "territory"}).assign(sector=state.cells.sector.iloc[0])[AXES])
        hist._cache[key] = (m, idx)
    return hist._cache[key]


SRC = "DREES RPPS (stocks par tranche × année), axe 4 (privé) ; cohortes par composantes, Bayes empirique"


@register
class CohortesModule(Module):
    name = "cohortes"
    order = 20
    produces = ("sorties", "entrees")
    params = (
        Param("tirage", -1, "indice", SRC, "fenêtre d'ajustement", "mesuré",
              "-1 = moyenne a posteriori ; k ≥ 0 = k-ième tirage prédictif."),
        Param("periode_60plus", 0.0, "log de la rétention", SRC, "fenêtre d'ajustement", "supposé",
              "Choc additif sur la rétention des ≥ 60 ans (réforme retraite, cumul emploi-retraite)."),
        Param("multiplicateur", 1.0, "× niveau national des entrées", "Loi OTSS 2019 ; arrêtés 2021 et 2026", "2026",
              "supposé", "Quotas × m, appliqué au niveau national M des entrées (à dater par Event)."),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        m, idx = cohortes_of(self.hist, state)
        s_c, I_c = m.rates(ctx.h, int(ctx.param(self, "tirage")))
        s, I = np.ones_like(state.N), np.zeros_like(state.N)
        s[idx], I[idx] = s_c, I_c
        d = ctx.param(self, "periode_60plus")
        if np.any(d != 0):
            s = np.minimum(1.0, s * np.exp(np.where(np.asarray(state.ages)[None, :] >= 60, d, 0.0)))
        k = ctx.param(self, "multiplicateur")
        return [Rate("sorties", s, to="sorties"), Add("entrees", I * k, src="entrees")]


COMPOSITION = ("methodes_vieillissement", "cohortes")


class CohortesEstimator(MethodEstimator):
    name = "C1 cohortes bayésiennes (θ fixé)"
    assumptions = "Rétention APC + entrées en niveau local national × parts hiérarchiques ; θ fixé à θ̂."
    options = {"shrink": 200.0, "aging": "uniforme", "S": 200, "laplace": False}
    scenario = Scenario(name="tendanciel", modules=COMPOSITION)

    def sample(self, target: int) -> pd.DataFrame:
        cols = {}
        for k in range(self.options["S"]):
            tr = self.trajectory(target, Scenario(name=f"t{k}", params={"cohortes.tirage": k}, modules=COMPOSITION))
            cols[k] = tr.states[target].total()
        return pd.DataFrame(cols)


class CohortesLaplace(CohortesEstimator):
    name = "C2 cohortes bayésiennes (θ propagé)"
    assumptions = "Comme C1, incertitude de θ propagée par Laplace sur log θ."
    options = {"shrink": 200.0, "aging": "uniforme", "S": 200, "laplace": True}
