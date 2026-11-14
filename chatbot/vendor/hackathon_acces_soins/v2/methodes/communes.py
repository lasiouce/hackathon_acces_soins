"""Projection communale calibrée (chantier « projection communale fiable ») : modèle K.

Dérivation : v2/docs/lab/derivations/2026-11-14-axe2-communes.md. Par profession, commune c, tranche a
(CartoSanté : < 40, 40–49, 50–54, 55–59, 60+), année τ :
  B(a,τ) = (1 − f_a) N(a,τ−1) + f_{a−1} N(a−1,τ−1),  f = (1/15, 1/10, 1/5, 1/5, 0)
  r rétréci nat → région → dép → EPCI → commune (pseudo-effectif k = 200) ; s = min(1, r)
  e = N − s·B ; total départemental E_d (niveau local, Kalman, comme C1) ; part communale q hiérarchique
  (k_q = 20 personnes, a priori au prorata du stock) ; N(a,τ) = max(0, s·B + q·L_d)
  Var prédictive = α_h μ + β_h μ², mesurés dans la fenêtre par pseudo-prévisions (origines o−h, o−h−1, o−h−2)
Données : data/processed/stock_commune.parquet (protocole N4), v2/data/processed/commune_geo.parquet (axe 4).
"""
import numpy as np
import pandas as pd
from scipy.optimize import nnls
from scipy.stats import nbinom, poisson

from methodes.cohortes import Level, kalman

F = np.array([1 / 15, 1 / 10, 1 / 5, 1 / 5, 0.0])
K_R, K_Q, WINDOW = 200.0, 20.0, 6
BANDS = ["Moins de 40 ans", "40 à 49 ans", "50 à 54 ans", "55 à 59 ans", "60 ans et plus"]


def load(prof: str):
    """(N [commune, tranche, année], années, table des communes : com, dep, epci, reg)."""
    s = pd.read_parquet("data/processed/stock_commune.parquet", filters=[("profession", "==", prof)])
    w = s.pivot_table(index="com", columns=["age_band", "year"], values="n", aggfunc="sum", fill_value=0)
    years = np.sort(s.year.unique())
    w = w.reindex(columns=pd.MultiIndex.from_product([BANDS, years]), fill_value=0)
    N = w.to_numpy(float).reshape(len(w), len(BANDS), len(years))
    geo = pd.read_parquet("v2/data/processed/commune_geo.parquet", columns=["com", "epci", "reg"])
    g = pd.DataFrame({"com": w.index}).merge(s.groupby("com").dep.first().reset_index(), on="com", how="left")
    g = g.merge(geo, on="com", how="left")
    g["epci"] = g.epci.fillna("c" + g.com)                      # commune sans EPCI : son propre groupe
    g["reg"] = g.reg.fillna("d" + g.dep)
    return N, years, g


def age(x):
    y = x * (1 - F)[None, :]
    y[:, 1:] += x[:, :-1] * F[None, :-1]
    return y


def _codes(v):
    return pd.factorize(pd.Series(v))[0]


def shrink(num, den, chain, k):
    """chain : codes du plus grossier au plus fin (région, dép, EPCI, commune) ; renvoie r [commune, tranche]."""
    r = np.broadcast_to(num.sum(0) / np.maximum(den.sum(0), 1e-9), num.shape).copy()
    for codes in chain:
        ng = codes.max() + 1
        ns, ds = np.zeros((ng, num.shape[1])), np.zeros((ng, num.shape[1]))
        np.add.at(ns, codes, num)
        np.add.at(ds, codes, den)
        parent = np.zeros((ng, num.shape[1]))
        parent[codes] = r                                          # tous les membres d'un groupe ont le même parent
        r = ((ns + k * parent) / (ds + k))[codes]
    return r


class K:
    def __init__(self, N, years, geo, origin, mult=1.0):
        yi = (years > origin - WINDOW) & (years <= origin)
        Nf = N[:, :, yi]
        nt = Nf.shape[2] - 1
        B = np.stack([age(Nf[:, :, t]) for t in range(nt)], axis=2)
        nxt = Nf[:, :, 1:]
        self.dep_i = _codes(geo.dep)
        epci_i, reg_i = _codes(geo.dep + "|" + geo.epci), _codes(geo.reg)
        com_i = np.arange(len(geo))
        r = shrink(nxt.sum(2), B.sum(2), [reg_i, self.dep_i, epci_i, com_i], K_R)
        self.s = np.minimum(r, 1.0)
        e = nxt - self.s[:, :, None] * B                          # [c, a, τ]
        nd = self.dep_i.max() + 1
        Ed = np.zeros((nd, e.shape[1], nt))
        np.add.at(Ed, self.dep_i, e)
        lev = Level([Ed[d, a] for d in range(nd) for a in range(e.shape[1])])
        su, sv = np.exp(lev.z)
        self.L = np.array([[kalman(Ed[d, a], su * np.sqrt(max(np.abs(Ed[d, a]).mean(), 1.0)),
                                   sv * np.sqrt(max(np.abs(Ed[d, a]).mean(), 1.0)))[1]
                            for a in range(e.shape[1])] for d in range(nd)]) * mult
        # parts hiérarchiques dép → EPCI → commune
        No = Nf[:, :, -1]
        S = e.sum(2)
        Sd, Se, Nd, Ne = (np.zeros((n, S.shape[1])) for n in (nd, epci_i.max() + 1, nd, epci_i.max() + 1))
        np.add.at(Sd, self.dep_i, S)
        np.add.at(Se, epci_i, S)
        np.add.at(Nd, self.dep_i, No)
        np.add.at(Ne, epci_i, No)
        ne_d = np.zeros(nd)
        e_dep = np.zeros(epci_i.max() + 1, int)
        e_dep[epci_i] = self.dep_i
        np.add.at(ne_d, e_dep, 1)
        nc_e = np.bincount(epci_i).astype(float)
        pi_e = np.where(Nd[e_dep] > 0, Ne / np.maximum(Nd[e_dep], 1e-9), 1 / ne_d[e_dep][:, None])
        pi_c = np.where(Ne[epci_i] > 0, No / np.maximum(Ne[epci_i], 1e-9), 1 / nc_e[epci_i][:, None])
        q_e = (Se + K_Q * pi_e) / (Sd[e_dep] + K_Q)
        q_c = (S + K_Q * q_e[epci_i] * pi_c) / (Se[epci_i] + K_Q * q_e[epci_i]) * q_e[epci_i]
        fallback = pi_e[epci_i] * pi_c                             # au prorata du stock
        bad = (Sd[self.dep_i] <= 0) | ~np.isfinite(q_c)
        self.q = np.where(bad, fallback, q_c)
        self.N0, self.origin = No, origin

    def project(self, h, N0=None):
        x = self.N0 if N0 is None else N0
        out = []
        for _ in range(h):
            x = np.maximum(self.s * age(x) + self.q * self.L[self.dep_i], 0.0)
            out.append(x)
        return out                                                   # liste de [c, a], années origine+1..+h


def exclusion(tot, years, o, h):
    """Règle de N4 : saut de plus de 3 écarts de Poisson d'une année sur l'autre entre o − 5 et o + h."""
    cols = [list(years).index(y) for y in range(o - 5, o + h + 1) if y in years]
    span = tot[:, cols]
    return (np.abs(np.diff(span, axis=1)) > 3 * np.sqrt(np.maximum(span[:, :-1], 1))).any(1)


def variance(N, years, geo, origin, h, lags=(0, 1, 2)):
    """(α, β) de Var = α μ + β μ², par pseudo-prévisions dans la fenêtre (cibles ≤ origine)."""
    tot = N.sum(1)
    X, y = [], []
    for lag in lags:
        o2 = origin - h - lag
        if o2 - WINDOW + 1 < years[0]:
            continue
        m = K(N, years, geo, o2)
        mu = m.project(h)[-1].sum(1)
        act = tot[:, list(years).index(o2 + h)]
        keep = (tot[:, list(years).index(o2)] >= 1) & ~exclusion(tot, years, o2, h)
        X.append(np.c_[mu[keep], mu[keep] ** 2])
        y.append((act[keep] - mu[keep]) ** 2)
    if not X:
        return np.nan, np.nan
    X, y = np.vstack(X), np.concatenate(y)
    w = 1 / np.maximum(X[:, 0], 1.0)                                # résidu relatif : chaque commune compte
    coef, _ = nnls(X * w[:, None], y * w)
    return float(coef[0]), float(coef[1])


def quantiles(mu, a, b, qs=(0.1, 0.9)):
    V = a * mu + b * mu ** 2
    out = []
    for q in qs:
        nb = V > mu * 1.0001
        r = np.where(nb, mu ** 2 / np.maximum(V - mu, 1e-12), 1.0)
        p = np.where(nb, r / (r + mu), 0.5)
        qq = np.where(nb, nbinom.ppf(q, np.maximum(r, 1e-9), np.clip(p, 1e-12, 1)), poisson.ppf(q, np.maximum(mu, 1e-12)))
        out.append(np.where(mu > 0, qq, 0.0))
    return out


# --- K2 (inscrite après l'échec de K) : part tenue × total départemental de K, bande empirique par classe --------
from validation.fine_scale import BINS  # noqa: E402


def k2_point(N, years, geo, origin, h):
    tot = N.sum(1)
    n0 = tot[:, list(years).index(origin)]
    m = K(N, years, geo, origin)
    mu = m.project(h)[-1].sum(1)
    di = m.dep_i
    D, D0 = np.bincount(di, mu), np.bincount(di, n0)
    return np.where(D0[di] > 0, n0 / np.maximum(D0[di], 1e-9) * D[di], 0.0)


def k2_band(N, years, geo, origin, h, lags=(0, 1, 2), min_n=20):
    """Quantiles (10 %, 90 %) de log((réel + ½)/(prédit + ½)) par classe de taille, pseudo-prévisions ≤ origine."""
    tot = N.sum(1)
    errs = {i: [] for i in range(len(BINS) - 1)}
    for lag in lags:
        o2 = origin - h - lag
        if o2 - WINDOW + 1 < years[0]:
            continue
        p = k2_point(N, years, geo, o2, h)
        n0, act = tot[:, list(years).index(o2)], tot[:, list(years).index(o2 + h)]
        keep = (n0 >= 1) & ~exclusion(tot, years, o2, h)
        cls = np.digitize(n0, BINS[1:-1])
        for i in errs:
            sel = keep & (cls == i)
            errs[i].extend(np.log((act[sel] + 0.5) / (p[sel] + 0.5)))
    q = {}
    for i in errs:                                                   # classe trop pauvre : on la fusionne avec ses voisines
        e, j = list(errs[i]), 1
        while len(e) < min_n and j < len(errs):
            e = e + list(errs.get(i - j, [])) + list(errs.get(i + j, []))
            j += 1
        q[i] = (np.quantile(e, .1), np.quantile(e, .9)) if len(e) >= min_n else (np.nan, np.nan)
    return q


def k2_interval(p, n0, q):
    cls = np.digitize(n0, BINS[1:-1])
    lo = np.array([q[c][0] for c in cls])
    hi = np.array([q[c][1] for c in cls])
    return np.maximum((p + 0.5) * np.exp(lo) - 0.5, 0), (p + 0.5) * np.exp(hi) - 0.5
