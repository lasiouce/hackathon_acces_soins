"""Mondes simulés à âges simples connus : le vieillissement uniforme biaise-t-il les seniors ? (kill test A1)

Vérité : un effectif par âge simple (20 à 74+), des sorties par âge, des entrées entre 23 et 29 ans,
des générations inégales (un pic de taille `pic` centré sur un âge `centre` à l'origine). On observe
seulement les tranches quinquennales, on ajuste sur 10 ans, on projette à h = 5 et 10.
Comparés : uniforme (v1, A0), interp (A1a), âges simples (A1b). Mesure : erreur sur le total et sur
les 60 ans et plus. Aucune donnée réelle n'est lue.
Lancer : PYTHONPATH=v2 uv run python -m methodes.monde
"""
import itertools

import numpy as np
import pandas as pd

from methodes.calibrage import Ages, fit

LO = np.array([0, 25, 30, 35, 40, 45, 50, 55, 60, 65])
A = Ages(LO)
X = A.single                                         # 20 … 74 (74 = 74 ans et plus)


def monde(pic, centre, croissance, T=25, seed=0):
    """Effectifs par âge simple, années 0..T-1."""
    exit_ = np.where(X < 55, 0.01, np.where(X < 60, 0.02, np.where(X < 65, 0.08, 0.25)))
    entry = np.where((X >= 23) & (X <= 29), 1.0, 0.0)
    entry = entry / entry.sum() * 300
    n = 100 * np.exp(-((X - 45) / 25) ** 2) + pic * np.exp(-((X - centre) / 3) ** 2)
    out = [n]
    for k in range(1, T):
        y = np.zeros_like(n)
        y[1:] = n[:-1]
        y[-1] += n[-1]
        n = y * (1 - exit_) + entry * (1 + croissance) ** k
        out.append(n)
    return np.array(out)                                          # [T, âge simple]


def projeter(c, N0, h, simple):
    s, I = c["s"][0], c["inflow"][0]
    if simple:
        x, sb, Ib = A.split(N0[None, :], "interp")[0], s[A.band], I[A.band] / A.w[A.band]
        for _ in range(h):
            x = sb * A.shift(x) + Ib
        return A.merge(x)
    x = N0.copy()
    for _ in range(h):
        x = s * A.age(x[None, :], c["aging"])[0] + I
    return x


def main():
    rows = []
    for pic, centre, cr in itertools.product([0, 60, 120], [40, 50, 55], [0.0, 0.02]):
        truth = monde(pic, centre, cr)
        bands = np.array([A.merge(n) for n in truth])            # [T, tranche]
        t = pd.DataFrame([{"profession": "x", "dep": "d", "sex": "F", "age_lo": a, "year": 2000 + k, "n": bands[k, j]}
                          for k in range(len(bands)) for j, a in enumerate(LO)])
        o = 2009
        for name, aging, simple in [("uniforme", "uniforme", False), ("A1a interp", "interp", False),
                                    ("A1b simples", "interp", True)]:
            c = fit(t[t.year <= o], (2000, o), shrink=None, aging=aging)
            for h in (5, 10):
                p, v = projeter(c, bands[o - 2000], h, simple), bands[o - 2000 + h]
                rows.append({"pic": pic, "centre": centre, "croissance": cr, "methode": name, "h": h,
                             "err_total_%": 100 * (p.sum() / v.sum() - 1),
                             "err_60plus_%": 100 * (p[LO >= 60].sum() / v[LO >= 60].sum() - 1)})
    r = pd.DataFrame(rows)
    r.to_csv("v2/methodes/out/monde.csv", index=False)
    agg = r.assign(abs_tot=r["err_total_%"].abs(), abs_60=r["err_60plus_%"].abs()).groupby(["h", "methode"])
    print(agg[["abs_tot", "abs_60"]].agg(["mean", "max"]).round(2).to_string())
    print(r.groupby(["h", "methode"])[["err_total_%", "err_60plus_%"]].mean().round(2).to_string())


if __name__ == "__main__":
    main()
