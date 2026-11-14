"""Calibrage stock-flux généralisé (axe 2) : opérateur de vieillissement, shrinkage, tendance des seniors.

Même forme que sante.model.fit_rates (v1) : N(t+1) = s · A(N(t)) + I, avec s ≤ 1 ajusté par moindres
carrés sur la fenêtre, et I = flux net moyen là où le ratio brut dépasse 1. Ce qui change :
  A          opérateur de vieillissement. "uniforme" = v1 (1/5 de la tranche passe chaque année) ;
             "interp" = désagrégation en âges simples (densité linéaire par morceaux entre milieux de
             tranches, masse conservée par tranche), vieillissement d'un an, réagrégation.
  hier       None = taux du département rétrécis vers le national (v1) ;
             table dep -> région = rétrécis vers la région, elle-même rétrécie vers le national.
  trend60    pente nationale (profession × sexe × tranche ≥ 60) de la rétention sur la fenêtre.
  obs_r12    schéma de l'observatoire (B4) : r = 1 et entrées = résidus moyens (5 dernières années)
             dans les tranches < 35 ans, r borné à [0,5 ; 1,2] ailleurs, sans entrées.
Avec A = "uniforme", hier = None, trend60 = False, le résultat est identique à fit_rates (vérifié
par methodes.verif).
"""
import numpy as np
import pandas as pd

from sante.model import KEYS, _cube

FIRST_W, TOP_W = 5, 10      # largeur supposée de la tranche du bas (20–24) et de la tranche ouverte (65–74)
SENIOR = 60                 # tranches concernées par la tendance de rétention


class Ages:
    """Passage tranches <-> âges simples pour des bornes basses `lo` (ex. 0, 25, 30, …, 65)."""

    def __init__(self, lo):
        lo = np.asarray(lo, int)
        self.lo = lo
        w = np.diff(lo).astype(int)
        w[0] = FIRST_W                                   # tranche « moins de 25 » traitée comme 20–24 (supposé)
        self.w = np.append(w, TOP_W)                     # tranche ouverte traitée comme 65–74 (supposé)
        start = np.append(lo[1] - FIRST_W, lo[1:])
        self.single = np.concatenate([np.arange(s, s + k) for s, k in zip(start, self.w)])
        self.band = np.repeat(np.arange(len(lo)), self.w)            # tranche de chaque âge simple
        centers = start + self.w / 2.0
        # densité aux âges simples = interpolation linéaire des densités moyennes de tranche (poids fixes)
        x = self.single + 0.5
        W = np.zeros((len(x), len(lo)))
        j = np.clip(np.searchsorted(centers, x) - 1, 0, len(lo) - 2)
        f = np.clip((x - centers[j]) / (centers[j + 1] - centers[j]), 0, 1)
        W[np.arange(len(x)), j] = 1 - f
        W[np.arange(len(x)), j + 1] = f
        self.W = W / self.w[None, :]                     # appliqué aux effectifs de tranche
        self.U = np.eye(len(lo))[self.band] / self.w[self.band][:, None]   # désagrégation uniforme
        self.agg = np.eye(len(lo))[self.band].T          # [tranche, âge simple]

    def split(self, N, how="interp"):
        """N [..., tranche] -> n [..., âge simple], masse de chaque tranche conservée."""
        if how == "uniforme":
            return N @ self.U.T
        d = np.maximum(N @ self.W.T, 0)
        tot = d @ self.agg.T                             # [..., tranche]
        uni = N @ self.U.T
        scale = np.divide(N, tot, out=np.zeros_like(N, dtype=float), where=tot > 0)
        return np.where((tot > 0)[..., self.band], d * scale[..., self.band], uni)

    def merge(self, n):
        return n @ self.agg.T

    @staticmethod
    def shift(n):
        """Un an de plus pour chaque âge simple ; le dernier âge est ouvert."""
        y = np.zeros_like(n)
        y[..., 1:] = n[..., :-1]
        y[..., -1] += n[..., -1]
        return y

    def age(self, N, how="interp"):
        """Opérateur A sur des tranches : désagrège, vieillit d'un an, réagrège."""
        return self.merge(self.shift(self.split(N, how)))


def fit(t: pd.DataFrame, fit_years, shrink=200.0, aging="uniforme", hier: pd.Series | None = None,
        trend60=False, obs_r12=False, inflow_recent=None) -> dict:
    """t : profession, dep, sex, age_lo, year, n. Renvoie s, inflow, b60, tbar ([cellule, tranche]) et cells."""
    N, cells, ages, years = _cube(t)
    yi = (years >= fit_years[0]) & (years <= fit_years[1])
    Nf, yrs = N[:, :, yi], years[yi]
    A = Ages(ages)
    base = np.stack([A.age(Nf[:, :, k], aging) for k in range(Nf.shape[2] - 1)], axis=2)
    nxt = Nf[:, :, 1:]
    num, den = nxt.sum(2), base.sum(2)
    grp = cells.groupby(["profession", "sex"]).ngroup().to_numpy()
    nat = np.zeros_like(num)
    for g in np.unique(grp):
        m = grp == g
        nat[m] = num[m].sum(0) / np.maximum(den[m].sum(0), 1e-9)
    prior = nat
    if hier is not None:                                 # département -> région -> national
        reg = cells.dep.map(hier).to_numpy()
        if pd.isna(reg).any():
            raise ValueError(f"départements sans région : {sorted(set(cells.dep[pd.isna(reg)]))[:5]}")
        prior = np.zeros_like(num)
        for key in set(zip(grp, reg)):
            m = (grp == key[0]) & (reg == key[1])
            prior[m] = (num[m].sum(0) + shrink * nat[m][0]) / (den[m].sum(0) + shrink)
    r = nat if shrink is None else (num + shrink * prior) / (den + shrink)
    out = {"cells": cells, "ages": ages, "A": A, "aging": aging}
    if obs_r12:
        entry = ages < 35                                # ses ENTRY_BANDS : < 25, 25–29, 30–34
        s = np.where(entry[None, :], 1.0, np.clip(r, 0.5, 1.2))
        e = nxt - s[:, :, None] * base
        inflow = np.where(entry[None, :], e[:, :, -5:].mean(2), 0.0)
        return {**out, "s": s, "inflow": inflow, "b60": np.zeros_like(s), "tbar": 0.0}
    s = np.minimum(r, 1.0)
    e = nxt - s[:, :, None] * base
    inflow = np.where(r > 1.0, (e if inflow_recent is None else e[:, :, -inflow_recent:]).mean(2), 0.0)
    b60 = np.zeros_like(s)
    tau = yrs[1:].astype(float)                          # année d'arrivée de chaque transition
    tbar = float(tau.mean())
    if trend60:
        sen = ages >= SENIOR
        tt = tau - tbar
        for g in np.unique(grp):
            m = grp == g
            R = nxt[m][:, sen].sum(0) / np.maximum(base[m][:, sen].sum(0), 1e-9)     # [tranche, t]
            b60[np.ix_(m, sen)] = ((R * tt).sum(1) / (tt ** 2).sum())[None, :]
        b60 = np.where(r > 1.0, 0.0, b60)                # pas de tendance là où les entrées sont absolues
    return {**out, "s": s, "inflow": inflow, "b60": b60, "tbar": tbar}


def dep_to_region() -> pd.Series:
    r = pd.read_parquet("data/processed/stock.parquet", columns=["dep", "region"]).drop_duplicates()
    return r.dropna().drop_duplicates("dep").set_index("dep").region.astype(str)
