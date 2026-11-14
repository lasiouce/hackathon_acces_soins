"""Étape 1 du programme de l'axe 2 : rétention nette en âge-période-cohorte (APC), bayésien gaussien.

Dérivation : v2/docs/lab/derivations/2026-11-14-axe2-apc-sorties.md. Pour chaque profession × sexe :
  y_i = log((N(a, τ) + ½) / (B(a, τ−1) + ½)),  B = vieillissement uniforme d'un an (comme A0)
  y_i ~ N(η_i, σ_e²/B_i + ω²)
  η_i = μ_a + π_{g(a),τ} + γ_{τ−âge_a} + v_{rég(d),a} + w_{d,a}
  μ_a ~ N(0, 10²) ; π_g : marche aléatoire d'ordre 1 (π_g,1 ~ N(0,1), incréments N(0, σ_π²)), g ∈ {<35, 35–59, ≥60}
  γ : marche aléatoire d'ordre 1 sur la cohorte (γ_1 ~ N(0,1), incréments N(0, σ_γ²))
  v ~ N(0, τ_r²) région × tranche ; w ~ N(0, τ_d²) département × tranche
Seules les tranches dont la rétention nationale de la fenêtre est ≤ 1 sont modélisées (règle de A0) ; les
autres gardent s et I de A0. Hyperparamètres θ = (σ_π, σ_γ, τ_r, τ_d, σ_e, ω) : maximum de la vraisemblance
marginale (Bayes empirique) ; loi a posteriori des effets exacte et gaussienne sachant θ̂ (pas de MCMC).
Prévision : π et γ prolongés à plat (marche d'ordre 1), variance croissante ; s = min(1, exp(η)).
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.optimize import minimize

from methodes.calibrage import Ages
from sante.model import _cube

GROUPS = (35, 60)               # bornes des groupes d'âge de l'effet de période
H_MAX = 30                      # horizon maximal des tirages pré-calculés
THETA = ("sigma_pi", "sigma_gamma", "tau_reg", "tau_dep", "sigma_e", "omega")


def _rw1(n, sigma, first_sd=1.0):
    """Précision d'une marche aléatoire d'ordre 1 de longueur n, premier terme N(0, first_sd²)."""
    D = sp.diags([-np.ones(n - 1), np.ones(n - 1)], [0, 1], shape=(n - 1, n))
    Q = (D.T @ D) / sigma ** 2
    Q = Q.tolil()
    Q[0, 0] += 1.0 / first_sd ** 2
    return Q.tocsc()


class Group:
    """Une profession × sexe : observations, matrice de plan, loi a posteriori."""

    def __init__(self, N, base, ages, years, dep, reg, bands):
        self.ages, self.bands = ages, bands                       # bands : indices des tranches modélisées
        nc, _, nt = base.shape
        c, a, k = np.meshgrid(np.arange(nc), bands, np.arange(nt), indexing="ij")
        c, a, k = c.ravel(), a.ravel(), k.ravel()
        B, Nn = base[c, a, k], N[c, a, k + 1]
        ok = B >= 5
        self.c, self.a, self.k, self.B = c[ok], a[ok], k[ok], B[ok]
        self.y = np.log((Nn[ok] + 0.5) / (self.B + 0.5))
        self.tau = years[1:]                                      # année d'arrivée de chaque transition
        self.nt, self.nc = nt, nc
        lo = ages[self.a]
        self.g = np.searchsorted(GROUPS, lo, side="right")        # 0 : <35, 1 : 35–59, 2 : ≥60
        self.kmin = int(self.tau[0] - ages[bands].max())
        self.kmax = int(self.tau[-1] - ages[bands].min())
        kappa = self.tau[self.k] - lo - self.kmin
        self.ureg, reg_i = np.unique(reg, return_inverse=True)
        self.reg_i = reg_i
        bi = {b: j for j, b in enumerate(bands)}
        ai = np.array([bi[x] for x in self.a])
        nb, ng, nk, nr = len(bands), 3, self.kmax - self.kmin + 1, len(self.ureg)
        self.sizes = {"mu": nb, "pi": ng * nt, "gamma": nk, "v": nr * nb, "w": nc * nb}
        off = np.cumsum([0] + list(self.sizes.values()))
        self.off = dict(zip(self.sizes, off[:-1]))
        self.p = int(off[-1])
        cols = np.stack([self.off["mu"] + ai, self.off["pi"] + self.g * nt + self.k, self.off["gamma"] + kappa,
                         self.off["v"] + reg_i[self.c] * nb + ai, self.off["w"] + self.c * nb + ai], axis=1)
        n = len(self.y)
        self.X = sp.csr_matrix((np.ones(5 * n), (np.repeat(np.arange(n), 5), cols.ravel())), shape=(n, self.p))
        self.ai_of_band = bi

    def prior(self, th):
        s_pi, s_g, t_r, t_d = th[:4]
        nb, nt = self.sizes["mu"], self.nt
        blocks = [sp.identity(nb) / 100.0] + [_rw1(nt, s_pi) for _ in range(3)] + [_rw1(self.sizes["gamma"], s_g),
                  sp.identity(self.sizes["v"]) / t_r ** 2, sp.identity(self.sizes["w"]) / t_d ** 2]
        return sp.block_diag(blocks, format="csc")

    def logdet_prior(self, th):
        """log|P| analytique : bloc i.i.d. n·log(1/t²) ; marche d'ordre 1 : −2(n−1)·log σ (premier terme N(0,1))."""
        s_pi, s_g, t_r, t_d = th[:4]
        return (self.sizes["mu"] * np.log(1 / 100.0) - 3 * 2 * (self.nt - 1) * np.log(s_pi)
                - 2 * (self.sizes["gamma"] - 1) * np.log(s_g) - self.sizes["v"] * 2 * np.log(t_r)
                - self.sizes["w"] * 2 * np.log(t_d))

    def noise(self, th, B=None):
        return th[4] ** 2 / (self.B if B is None else B) + th[5] ** 2

    def posterior(self, th, y=None):
        y = self.y if y is None else y
        P = self.prior(th).toarray()
        dinv = 1.0 / self.noise(th)
        XtD = self.X.T.multiply(dinv).tocsr()
        Q = P + (XtD @ self.X).toarray()
        b = XtD @ y
        L = np.linalg.cholesky(Q)
        m = np.linalg.solve(L.T, np.linalg.solve(L, b))
        return P, Q, L, b, m, dinv

    def loglik(self, th, y=None):
        y = self.y if y is None else y
        P, Q, L, b, m, dinv = self.posterior(th, y)
        ldP = self.logdet_prior(th)
        ldQ = 2 * np.log(np.diag(L)).sum()
        return 0.5 * (ldP - ldQ + np.log(dinv).sum() - (dinv * y * y).sum() + b @ m)

    def fit(self, y=None, th0=(0.02, 0.02, 0.02, 0.03, 0.3, 0.02)):
        f = lambda z: -self.loglik(np.exp(z), y)
        r = minimize(f, np.log(th0), method="L-BFGS-B", bounds=[(np.log(1e-4), np.log(3.0))] * 6)
        self.theta = np.exp(r.x)
        self.P, self.Q, self.L, _, self.m, _ = self.posterior(self.theta, y)
        return self

    def draws(self, S, rng):
        z = rng.standard_normal((self.p, S))
        return self.m[:, None] + np.linalg.solve(self.L.T, z)               # [p, S]

    def eta(self, beta, h, innov=None):
        """η [cellule, tranche modélisée] pour l'année origine + h, pour un vecteur d'effets beta.
        innov : (incréments de période [3, H], incréments de cohorte [H]) cumulés, ou None (moyenne)."""
        nb, nt = self.sizes["mu"], self.nt
        o = self.off
        lo = self.ages[self.bands]
        mu = beta[o["mu"]:o["mu"] + nb]
        g = np.searchsorted(GROUPS, lo, side="right")
        pi_last = beta[o["pi"] + g * nt + nt - 1]
        tau = self.tau[-1] + h
        kappa = tau - lo - self.kmin
        nk = self.sizes["gamma"]
        gam = beta[o["gamma"] + np.minimum(kappa, nk - 1)]
        if innov is not None:
            dpi, dg = innov
            pi_last = pi_last + dpi[g, h - 1]
            extra = np.maximum(kappa - (nk - 1), 0)                     # cohortes jamais vues
            gam = gam + np.where(extra > 0, dg[np.maximum(extra - 1, 0)], 0.0)
        v = beta[o["v"]:o["v"] + self.sizes["v"]].reshape(-1, nb)[self.reg_i]
        w = beta[o["w"]:o["w"] + self.sizes["w"]].reshape(-1, nb)
        return mu[None, :] + pi_last[None, :] + gam[None, :] + v + w

    def identification(self):
        """sd a posteriori / sd a priori marginale des effets de cohorte (1 = la donnée n'apprend rien)."""
        o, nk = self.off["gamma"], self.sizes["gamma"]
        Pinv = np.linalg.inv(self.P)
        Qinv = np.linalg.inv(self.Q)
        idx = np.arange(o, o + nk)
        return np.sqrt(np.diag(Qinv)[idx] / np.diag(Pinv)[idx])


class APC:
    """Ajuste un Group par profession × sexe sur la table t ; sert η sur les cellules du cube (ordre de _cube)."""

    def __init__(self, t, fit_years, dep2reg: pd.Series, S=100, seed=20261114):
        N, cells, ages, years = _cube(t)
        yi = (years >= fit_years[0]) & (years <= fit_years[1])
        N, years = N[:, :, yi], years[yi]
        A = Ages(ages)
        base = np.stack([A.age(N[:, :, k], "uniforme") for k in range(N.shape[2] - 1)], axis=2)
        self.cells, self.ages, self.S = cells, ages, S
        self.groups = []
        rng = np.random.default_rng(seed)
        for _, idx in cells.groupby(["profession", "sex"]).indices.items():
            num, den = N[idx][:, :, 1:].sum((0, 2)), base[idx].sum((0, 2))
            bands = np.flatnonzero(num / np.maximum(den, 1e-9) <= 1.0)
            if len(bands) == 0:
                continue
            g = Group(N[idx], base[idx], ages, years, cells.dep.iloc[idx].to_numpy(),
                      cells.dep.iloc[idx].map(dep2reg).fillna("?").to_numpy(), bands).fit()
            g.idx = idx
            g.beta = g.draws(S, rng)
            th = g.theta
            g.dpi = np.cumsum(rng.standard_normal((S, 3, H_MAX)) * th[0], axis=2)
            g.dg = np.cumsum(rng.standard_normal((S, H_MAX)) * th[1], axis=1)
            Blast = np.maximum(base[idx][:, bands, -1], 1.0)
            g.noise_sd = np.sqrt(g.noise(th, Blast))                          # [cellule, tranche]
            g.rng_noise = rng.standard_normal((S, H_MAX) + Blast.shape)
            self.groups.append(g)

    def log_retention(self, h, draw=-1):
        """η [cellule du cube, tranche] (NaN hors tranches modélisées) pour origine + h ; draw = -1 : moyenne."""
        out = np.full((len(self.cells), len(self.ages)), np.nan)
        for g in self.groups:
            if draw < 0:
                e = g.eta(g.m, h)
            else:
                e = g.eta(g.beta[:, draw], h, (g.dpi[draw], g.dg[draw]))
            out[np.ix_(g.idx, g.bands)] = e
        return out

    def log_noise(self, h, draw):
        """Bruit annuel de la rétention réalisée, log-normal de moyenne 1 : ε − var/2 (0 hors tranches modélisées)."""
        out = np.zeros((len(self.cells), len(self.ages)))
        if draw >= 0:
            for g in self.groups:
                out[np.ix_(g.idx, g.bands)] = g.noise_sd * g.rng_noise[draw, h - 1] - g.noise_sd ** 2 / 2
        return out


# --- Branchement sur le jumeau : module `apc_sorties` et estimateur -----------------------------------
from jumeau.module import Module, Param, Rate, register          # noqa: E402
from jumeau.state import AXES                                     # noqa: E402
from methodes.calibrage import dep_to_region                      # noqa: E402
from methodes.estimators import MethodEstimator                   # noqa: E402
from methodes.modules import calibration                          # noqa: E402

SRC = "DREES RPPS (stocks par tranche × année), rétention nette de cohorte ; APC gaussien, Bayes empirique"


def apc_of(hist, state) -> tuple:
    """(APC, indices des cellules de l'état dans l'ordre du cube), mis en cache sur hist."""
    key = ("apc", len(state.cells))
    if key not in hist._cache:
        t = hist.table.rename(columns={hist.level: "dep"})
        t = t.drop(columns="sector") if "sector" in t else t
        m = APC(t, hist.fit_years, dep_to_region(), S=hist.options.get("S", 100))
        idx = state.index(m.cells.rename(columns={"dep": "territory"}).assign(sector=state.cells.sector.iloc[0])[AXES])
        hist._cache[key] = (m, idx)
    return hist._cache[key]


@register
class APCSorties(Module):
    name = "apc_sorties"
    order = 20
    produces = ("sorties",)
    params = (
        Param("tirage", -1, "indice", SRC, "fenêtre d'ajustement", "mesuré",
              "-1 = moyenne a posteriori ; k ≥ 0 = k-ième tirage prédictif (effets, innovations, bruit annuel)."),
        Param("periode_60plus", 0.0, "log de la rétention", SRC, "fenêtre d'ajustement", "supposé",
              "Décalage additif de l'effet de période des ≥ 60 ans (réforme retraite, cumul emploi-retraite)."),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        c = calibration(self.hist, state)                         # s de A0 hors tranches modélisées
        m, idx = apc_of(self.hist, state)
        k = int(ctx.param(self, "tirage"))
        eta, eps = np.full_like(state.N, np.nan), np.zeros_like(state.N)
        eta[idx] = m.log_retention(ctx.h, k)
        eps[idx] = m.log_noise(ctx.h, k)
        d = ctx.param(self, "periode_60plus")
        eta = eta + np.where(np.asarray(state.ages)[None, :] >= 60, np.reshape(d, (-1, 1)) if np.ndim(d) else d, 0.0)
        # plafond à 1 sur la rétention attendue (comme A0) ; le bruit annuel réalisé s'applique ensuite
        s = np.where(np.isnan(eta), c["s"], np.minimum(1.0, np.exp(eta)) * np.exp(eps))
        return [Rate("sorties", s, to="sorties")]


COMPOSITION_APC = ("methodes_vieillissement", "apc_sorties", "methodes_entrees")


class APCEstimator(MethodEstimator):
    name = "APC rétention nette"
    assumptions = "Rétention nette en âge-période-cohorte gaussien (Bayes empirique), période prolongée à plat."
    options = {"shrink": 200.0, "aging": "uniforme", "S": 100}
    from jumeau.scenario import Scenario as _S
    scenario = _S(name="tendanciel", modules=COMPOSITION_APC)

    def sample(self, target: int, S: int | None = None) -> pd.DataFrame:
        """Tirages prédictifs : DataFrame [(profession, dep)] × S."""
        from jumeau.scenario import Scenario
        S = S or self.options["S"]
        cols = {}
        for k in range(S):
            tr = self.trajectory(target, Scenario(name=f"tirage{k}", params={"apc_sorties.tirage": k},
                                                  modules=COMPOSITION_APC))
            cols[k] = tr.states[target].total()
        return pd.DataFrame(cols)
