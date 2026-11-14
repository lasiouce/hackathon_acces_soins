"""Mesure du défaut du levier retraite (open.md) sans modifier jumeau/modules/sorties.py (axe 0).

Le module `sorties` multiplie en permanence le taux de sortie de 60–64 ET de la tranche ouverte 65+ par
max(0, 1 − Δ/5) : sur 65+, le séjour moyen 1/e devient 1/(e (1 − Δ/5)), soit bien plus que + Δ ans.
Variante B1 (observatoire, reprise B1) déposée ici comme module de comparaison : 60–64 inchangé (× (1 − Δ/5)),
65+ : e' = e / (1 + Δ e), c'est-à-dire un séjour moyen 1/e + Δ. Même flux `sorties`, autre nom de module.

Run (racine) : PYTHONPATH=v2:. uv run python -m sensibilite.retraite_b1 -> v2/sensibilite/out/retraite_b1.csv
"""
import numpy as np
import pandas as pd

from jumeau.history import stock_flow_rates
from jumeau.module import Rate, register
from jumeau.modules.sorties import Sorties
from jumeau.scenario import Scenario
from sensibilite.facteurs import PROFS, YEARS, Model
from sensibilite.run import _default


@register
class SortiesB1(Sorties):
    name = "sorties_b1"
    produces = ("sorties",)

    def step(self, state, ctx):
        s = ctx.param(self, "retention", base=stock_flow_rates(self.hist, state)[0])
        d = float(ctx.param(self, "decalage_retraite"))
        if d != 0:
            a = state.ages
            e = 1.0 - s
            e = np.where((a >= 60) & (a < 65), e * max(0.0, 1.0 - d / 5.0), e)
            e = np.where(a >= 65, e / (1.0 + d * e), e)
            s = 1.0 - e
        return [Rate("sorties", s, to="sorties")]


def main():
    rows = []
    for p in PROFS:
        m = Model(p, levers=False)
        u = np.array([_default(f) for f in m.f])
        v = m.values(u)
        est = m.estimator(v["fenetre"], v["shrink"], v["entrees"], v.get("filiere", False), "central")
        comp_b1 = ("vieillissement", "sorties_b1", "entrees")
        base = est.trajectory(max(YEARS), Scenario(name="ref"))
        for d in (1.0, 2.0, 3.0):
            jm = est.trajectory(max(YEARS), Scenario(name="jumeau", params={"sorties.decalage_retraite": d}))
            b1 = est.trajectory(max(YEARS), Scenario(name="b1", params={"sorties_b1.decalage_retraite": d},
                                                     modules=comp_b1))
            for y in YEARS:
                n0 = base.states[y].N.sum()
                rows.append(dict(profession=p, delta_ans=d, annee=y, n_ref=n0,
                                 effet_jumeau_pct=100 * (jm.states[y].N.sum() / n0 - 1),
                                 effet_b1_pct=100 * (b1.states[y].N.sum() / n0 - 1)))
    r = pd.DataFrame(rows)
    r["surplus_x"] = r.effet_jumeau_pct / r.effet_b1_pct.where(r.effet_b1_pct.abs() > 1e-9)
    r.to_csv("v2/sensibilite/out/retraite_b1.csv", index=False)
    print(r.round(2).to_string())


if __name__ == "__main__":
    main()
