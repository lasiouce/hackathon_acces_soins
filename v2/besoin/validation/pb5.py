"""P-B5 : backtest du recours 2016 → 2025 par la structure d'âge (protocole gelé v2/validation/preregistered/
2026-11-15-besoin-p-b5-backtest.md, amendement A1.3 ; écarts dans v2/docs/lab/reports/2026-11-15-besoin-pb5-backtest.md).

Run (racine du dépôt) : PYTHONPATH=v2 uv run --with scikit-learn --with xlrd --with openpyxl python -m besoin.validation.pb5
                         -> v2/artifacts/besoin_pb5/results.json

  persistance  R̂ = R(2016) · pop(2025)/pop(2016)
  M1           R̂ = R(2016) · B₁(2025)/B₁(2016),  B₁ = Σ pop · ω (APL ; P2 = colonne 2022 en sensibilité)
  GBM          R̂ = R̂_M1 · exp(ŷ), ŷ ≈ log[R(2025)/R̂_M1] ; une région laissée de côté ; hyperparamètres gelés
  Δ₁ = MAPE_M1 − MAPE_pers ; Δ_GBM = MAPE_GBM − MAPE_M1 ; IC 98,75 % (bootstrap des départements, B = 2 000)
  M1 gagne si borne haute IC(Δ₁) < 0, perd si Δ₁ ≥ 0, sinon égalité ; H-B1 retenue si ≥ 3/4 gagnés, rejetée si
  ≥ 2/4 perdus ; le GBM entre si borne haute IC(Δ_GBM) < 0.
"""
import json
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from besoin.cube import Population, mapping
from besoin.estimateurs.m1 import CODE, poids_apl
from besoin.estimateurs.recours import PROF_AMELI, _secteur, recours

OUT = Path("v2/artifacts/besoin_pb5")
INSEE = "v2/data/raw/insee/estim-pop-dep-sexe-aq-1975-2023.xls"
GRILLE = "v2/data/raw/insee/grille_densite_7_niveaux_2016.xlsx"
O, CIBLE, CTRL = 2016, 2025, 2021
B, SEED, NIV = 2000, 20261115, 1 - 0.05 / 4
GBM = dict(max_iter=200, learning_rate=0.05, max_depth=3, min_samples_leaf=10, random_state=20261115)   # gelés
IDF = {"75", "92", "93", "94"}


@lru_cache(maxsize=4)
def insee(year: int) -> pd.DataFrame:
    """[département] × colonnes (sexe, age_lo) : estimation Insee au 1ᵉʳ janvier."""
    d = pd.read_excel(INSEE, sheet_name=str(year), header=None)
    d = d[d[0].astype(str).str.fullmatch(r"\d[\dAB]\d?")].set_index(0)
    ages = np.arange(0, 100, 5)
    cols = {("H", a): 23 + i for i, a in enumerate(ages)} | {("F", a): 44 + i for i, a in enumerate(ages)}
    out = pd.DataFrame({k: pd.to_numeric(d[c]) for k, c in cols.items()})
    out.index = out.index.astype(str)
    return out


def population(year: int, omphale: Population) -> Population:
    """Population Insee (2016, 2021, 2023) ; 2025 = Insee 2023 × Omphale 2025 / Omphale 2023 (écart 1)."""
    base = 2023 if year > 2023 else year
    t = insee(base)
    terr = np.array(sorted(set(t.index) & set(omphale.territories)))
    P = np.zeros((len(terr), 1, len(omphale.sexes), len(omphale.ages)))
    for i, s in enumerate(omphale.sexes):
        for j, a in enumerate(omphale.ages):
            P[:, 0, i, j] = t.loc[terr, (s, int(a))].to_numpy()
    if year > 2023:
        oi = np.searchsorted(omphale.territories, terr)
        y0, y1 = omphale.years_index([2023, year])
        with np.errstate(divide="ignore", invalid="ignore"):
            g = np.where(omphale.P[oi, y0] > 0, omphale.P[oi, y1] / omphale.P[oi, y0], 1.0)
        P[:, 0] *= g
    return Population(terr, np.array([year]), omphale.sexes, omphale.ages, P, "dep", "insee",
                      f"Insee, estimations de population {base}" + (" × Omphale 2022" if year > 2023 else ""))


def omega(prof: str, pop: Population, colonne: int | None = None) -> np.ndarray:
    from besoin.estimateurs.m1 import COLONNE, FEMMES
    w = poids_apl()
    w = w[(w.prof == CODE[prof]) & (w.annee == (colonne or COLONNE[prof]))].set_index("age_lo").omega
    row = w.reindex(np.minimum(pop.ages, 90)).to_numpy()
    out = np.tile(row, (len(pop.sexes), 1))
    if prof in FEMMES:
        out[pop.sexes != "F"] = 0.0
    return out


def bstd(pop: Population, w) -> pd.Series:
    return pd.Series(np.einsum("tsa,sa->t", pop.P[:, 0], w), index=pop.territories)


def grille() -> pd.Series:
    d = pd.read_excel(GRILLE, header=4, dtype={"CODGEO": str})
    d["dep"] = np.where(d.CODGEO.str.startswith("97"), d.CODGEO.str[:3], d.CODGEO.str[:2])
    tot = d.groupby("dep").PMUN14.sum()
    return (d[d.DENS <= 4].groupby("dep").PMUN14.sum().reindex(tot.index).fillna(0) / tot).rename("part_dense")


def predictions(prof, pops, cible, colonne=None, o=O):
    """DataFrame [département] : R(o), R(cible), R̂_pers, R̂_M1."""
    R = recours(prof, [o, cible]) if cible in recours(prof, [cible]).columns else recours(prof, [o])
    p0, p1 = pops[o], pops[cible]
    w = omega(prof, p0, colonne)
    b0, b1 = bstd(p0, w), bstd(p1, w)
    n0, n1 = pd.Series(p0.P[:, 0].sum(axis=(1, 2)), p0.territories), pd.Series(p1.P[:, 0].sum(axis=(1, 2)),
                                                                              p1.territories)
    d = sorted(set(R.dropna().index) & set(b0.index) & set(b1.index))
    t = pd.DataFrame({"R0": R.loc[d, o], "R": R.loc[d, cible] if cible in R.columns else np.nan})
    t["pers"] = t.R0 * n1[d] / n0[d]
    t["M1"] = t.R0 * b1[d] / b0[d]
    return t


def covariables(prof, t, pops, cible, o=O):
    p0 = pops[o]
    pop0 = pd.Series(p0.P[:, 0].sum(axis=(1, 2)), p0.territories)
    ages = p0.ages
    parts = {k: pd.Series(p0.P[:, 0][:, :, m].sum(axis=(1, 2)), p0.territories) / pop0
             for k, m in (("p0_14", ages < 15), ("p15_59", (ages >= 15) & (ages < 60)),
                          ("p60_74", (ages >= 60) & (ages < 75)), ("p75", ages >= 75))}
    def an(q):
        """Année o si l'effectif du jumeau l'a, sinon la plus récente avant o, sinon la plus ancienne."""
        dispo = [int(c) for c in _secteur(q).columns[_secteur(q).notna().any()]]
        avant = [y for y in dispo if y <= o]
        return max(avant) if avant else min(dispo)
    dens = lambda q: _secteur(q)[an(q)].reindex(t.index)
    autres = sum(dens(q) for q in PROF_AMELI if q != prof)
    X = pd.DataFrame(index=t.index)
    X["log_recours_hab"] = np.log(t.R0 / pop0[t.index])
    for k, v in parts.items():
        X[k] = v[t.index]
    X["log_dB1"] = np.log(t.M1 / t.R0)
    X["log_dens"] = np.log(1e5 * dens(prof) / pop0[t.index])
    X["log_dens_autres"] = np.log(1e5 * autres / pop0[t.index])
    X["part_dense"] = grille().reindex(t.index)
    X["drom"] = t.index.str.startswith("97").astype(float)
    return X, {q: an(q) for q in PROF_AMELI}


def gbm_loro(X, y, g):
    from sklearn.ensemble import HistGradientBoostingRegressor
    yhat = np.full(len(y), np.nan)
    for r in np.unique(g):
        te = g == r
        m = HistGradientBoostingRegressor(**GBM).fit(X[~te], y[~te])
        yhat[te] = m.predict(X[te])
    return yhat


def mape(pred, R, w=None):
    e = np.abs(pred - R) / R
    return float(100 * (e.mean() if w is None else (e * w).sum() / w.sum()))


def boot(ap, bp, R):
    """IC 98,75 % de MAPE(a) − MAPE(b), départements tirés avec remise."""
    rng = np.random.default_rng(SEED)
    ea, eb = np.abs(ap - R) / R, np.abs(bp - R) / R
    d = np.empty(B)
    for i in range(B):
        j = rng.integers(0, len(R), len(R))
        d[i] = 100 * (ea[j].mean() - eb[j].mean())
    return [float(np.quantile(d, (1 - NIV) / 2)), float(np.quantile(d, 1 - (1 - NIV) / 2))]


def juge(d1, ic):
    return "gagne" if ic[1] < 0 else "perd" if d1 >= 0 else "égalité"


def bilan(v):
    w, l = sum(x == "gagne" for x in v.values()), sum(x == "perd" for x in v.values())
    return "H-B1 retenue" if w >= 3 else "H-B1 rejetée" if l >= 2 else "non tranchée"


def main():
    import sklearn
    OUT.mkdir(parents=True, exist_ok=True)
    om = Population.load()
    pops = {y: population(y, om) for y in (O, CTRL, 2023, CIBLE)}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    reg = mapping("dep", "reg")
    res = dict(commit=commit, sklearn=sklearn.__version__, B=B, seed=SEED, niveau=NIV, gbm=GBM, professions={})
    verd, verd_p2 = {}, {}
    for p in PROF_AMELI:
        t = predictions(p, pops, CIBLE)
        R = t.R.to_numpy()
        m_pers, m_m1 = mape(t.pers.to_numpy(), R), mape(t.M1.to_numpy(), R)
        d1, ic1 = m_m1 - m_pers, boot(t.M1.to_numpy(), t.pers.to_numpy(), R)
        X, ans = covariables(p, t, pops, CIBLE)
        y = np.log(t.R / t.M1).to_numpy()
        g = reg.reindex(t.index).astype(str).to_numpy()
        gb = t.M1.to_numpy() * np.exp(gbm_loro(X.to_numpy(), y, g))
        m_gbm = mape(gb, R)
        dg, icg = m_gbm - m_m1, boot(gb, t.M1.to_numpy(), R)
        verd[p] = juge(d1, ic1)
        # sensibilité P2 : poids APL de la colonne 2022 (A1.3)
        t2 = predictions(p, pops, CIBLE, colonne=2022)
        R2 = t2.R.to_numpy()
        d12 = mape(t2.M1.to_numpy(), R2) - mape(t2.pers.to_numpy(), R2)
        verd_p2[p] = juge(d12, boot(t2.M1.to_numpy(), t2.pers.to_numpy(), R2))
        # rapporté, non décisif
        tc = predictions(p, pops, CTRL)
        Rc = tc.R.to_numpy()
        t23 = predictions(p, pops, 2023)
        R23 = t23.R.to_numpy()
        w = pd.Series(pops[O].P[:, 0].sum(axis=(1, 2)), pops[O].territories)[t.index].to_numpy()
        k = ~t.index.isin(IDF)
        res["professions"][p] = dict(
            n=len(t), plis=int(len(np.unique(g))), annees_densite=ans,
            MAPE=dict(pers=m_pers, M1=m_m1, GBM=m_gbm), delta1=d1, IC_delta1=ic1, verdict_M1=verd[p],
            delta_GBM=dg, IC_delta_GBM=icg, GBM_entre=bool(icg[1] < 0),
            P2=dict(delta1=d12, verdict_M1=verd_p2[p]),
            rapporte=dict(h5_2021=dict(pers=mape(tc.pers.to_numpy(), Rc), M1=mape(tc.M1.to_numpy(), Rc)),
                          cible_2023=dict(pers=mape(t23.pers.to_numpy(), R23), M1=mape(t23.M1.to_numpy(), R23)),
                          pondere=dict(pers=mape(t.pers.to_numpy(), R, w), M1=mape(t.M1.to_numpy(), R, w),
                                       GBM=mape(gb, R, w)),
                          hors_paris_pc=dict(pers=mape(t.pers.to_numpy()[k], R[k]), M1=mape(t.M1.to_numpy()[k], R[k]),
                                             GBM=mape(gb[k], R[k]))))
        print(f"{p:13s} n={len(t)} MAPE pers {m_pers:.2f} M1 {m_m1:.2f} GBM {m_gbm:.2f} | Δ₁ {d1:+.2f} "
              f"IC[{ic1[0]:+.2f}, {ic1[1]:+.2f}] -> {verd[p]} (P2 : {verd_p2[p]}) | Δ_GBM {dg:+.2f} "
              f"IC[{icg[0]:+.2f}, {icg[1]:+.2f}] -> GBM {'entre' if icg[1] < 0 else 'n’entre pas'}", flush=True)
    res["H_B1"], res["H_B1_P2"] = bilan(verd), bilan(verd_p2)
    res["H_B1_final"] = res["H_B1"] if res["H_B1"] == res["H_B1_P2"] else "dépendante du profil"
    print("H-B1 :", res["H_B1"], "| P2 :", res["H_B1_P2"], "| final :", res["H_B1_final"])
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
