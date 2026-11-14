"""B4 : la borne r ≤ 1,2 de l'observatoire fait-elle s'emballer les entrées ? Croissance annuelle nationale
projetée 2026 -> 2050 (origine = dernière année) contre la croissance observée sur les 10 dernières années.
Lancer : PYTHONPATH=v2 uv run python -m methodes.b4"""
import pandas as pd

from methodes import estimators as M
from methodes.perimetres import prive

t = prive()
rows = []
for p in t.profession.unique():
    tp = t[t.profession == p]
    last = int(tp.year.max())
    first = 2017 if p == "kines" else 2012
    tot = tp.groupby("year").n.sum()
    obs = (tot[last] / tot[last - min(9, last - first)]) ** (1 / min(9, last - first)) - 1
    r = {"profession": p, "obs_%/an": 100 * obs}
    for cls in (M.Uniforme, M.ObservatoireR12):
        e = cls().fit(tp, (first, last), last)
        n = e.predict(2050).sum()
        r[f"{cls.__name__}_%/an"] = 100 * ((n / tot[last]) ** (1 / (2050 - last)) - 1)
        r[f"{cls.__name__}_2050/{last}"] = n / tot[last]
        if cls is M.ObservatoireR12:
            c = e.modules(e.scenario)[1]
            from methodes.modules import calibration
            cc = calibration(e.hist, e.state)
            r["part_cellules_r>1_hors_entrees_%"] = 100 * float(((cc["s"] > 1) & (cc["alo"] >= 35)[None, :]).sum()
                                                                / (cc["alo"] >= 35).sum() / len(cc["s"]))
    rows.append(r)
print(pd.DataFrame(rows).round(2).to_string(index=False))
pd.DataFrame(rows).to_csv("v2/methodes/out/b4.csv", index=False)
