"""Variante d'entrées « tendance » (pente linéaire des entrées nettes prolongée) : grille hors Sobol.

Exclue du plan de Sobol (decisions.md, axe 5) parce qu'elle fait exploser N(2050) ; on la mesure ici sur la
grille fenêtre × variante d'entrées, les autres facteurs au tendanciel par défaut.
Run (racine) : PYTHONPATH=v2:. uv run python -m sensibilite.tendance -> v2/sensibilite/out/tendance_grille.csv
"""
import numpy as np
import pandas as pd

from sensibilite.facteurs import PROFS, YEARS, Model
from sensibilite.run import _default


def main():
    rows = []
    for p in PROFS:
        m = Model(p, levers=False)
        v = m.values(np.array([_default(f) for f in m.f]))
        for w in (2, 3, 5, 8):
            for e in ("plates", "recentes", "tendance"):
                est = m.estimator(w, v["shrink"], e, v.get("filiere", False), "central")
                tr = est.trajectory(max(YEARS))
                rows += [dict(profession=p, fenetre=w, entrees=e, annee=y, n=tr.states[y].N.sum()) for y in YEARS]
    d = pd.DataFrame(rows)
    d.to_csv("v2/sensibilite/out/tendance_grille.csv", index=False)
    print(d[d.annee == 2050].pivot_table(index=["profession", "fenetre"], columns="entrees", values="n").round(-2))


if __name__ == "__main__":
    main()
