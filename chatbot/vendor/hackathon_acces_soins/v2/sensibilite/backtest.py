"""Composante (b) des fourchettes : erreur de backtest du jumeau sur le privé, extrapolée à 2050 (méthode A3).

Banc N1 (v2/validation/forecast.py : origines glissantes, h ∈ {1, 3, 5, 8, 10}) avec le défaut confirmatoire
twin_of(StockFlowLocal), sur la table privée (variante centrale ; infirmiers : libéraux v1). Pour chaque
profession : erreur relative signée du total national par (origine, h), puis pente a de |erreur| ∝ h ajustée
par l'origine (moindres carrés sans constante). Fourchette extrapolée ± 1,6 · a · h (observatoire A3 : × 1,6
pour couvrir environ 8 cas sur 10 ; facteur cité, non reproduit ici). Aucun backtest n'existe au-delà de h = 10.

Run (racine) : PYTHONPATH=v2:. uv run python -m sensibilite.backtest -> v2/sensibilite/out/backtest*.csv
"""
import numpy as np
import pandas as pd

from sante import estimators as V1
from jumeau.estimators import twin_of
from sensibilite.facteurs import PROFS, YEARS, _table, origin
from validation.forecast import bench, design

K_A3 = 1.6


def main():
    errs = []
    for p in PROFS:
        t = _table(p, "central")
        e = bench({"twin": twin_of(V1.StockFlowLocal)}, t, design(t))
        nat = e.groupby(["profession", "origin", "h"])[["actual", "pred"]].sum().reset_index()
        nat["err_pct"] = 100 * (nat.pred - nat.actual) / nat.actual
        dep = e[e.n_origin >= 30].groupby(["profession", "origin", "h"]).ape.mean().rename("mape_dep").reset_index()
        errs.append(nat.merge(dep))
    E = pd.concat(errs)
    E.to_csv("v2/sensibilite/out/backtest_erreurs.csv", index=False)
    rows = []
    for p, g in E.groupby("profession"):
        h, a_nat = g.h.to_numpy(float), np.abs(g.err_pct.to_numpy())
        slope = (h * a_nat).sum() / (h ** 2).sum()
        slope_dep = (h * g.mape_dep).sum() / (h ** 2).sum()
        o = origin(p)
        for y in YEARS:
            H = y - o
            rows.append(dict(profession=p, annee=y, h=H, pente_nat_pct_par_an=slope, pente_dep_pct_par_an=slope_dep,
                             biais_moyen_h5_pct=g[g.h == 5].err_pct.mean(), n_cas=len(g), h_max_observe=int(g.h.max()),
                             demi_largeur_nat_pct=K_A3 * slope * H, demi_largeur_dep_pct=K_A3 * slope_dep * H))
    B = pd.DataFrame(rows)
    B.to_csv("v2/sensibilite/out/backtest_fourchette.csv", index=False)
    print(B.round(2).to_string())


if __name__ == "__main__":
    main()
