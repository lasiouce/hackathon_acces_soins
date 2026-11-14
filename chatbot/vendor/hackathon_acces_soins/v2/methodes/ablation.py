"""EXPLORATOIRE (inscrit après avoir vu le banc N1 du 2026-11-14) : pourquoi le schéma de l'observatoire (B4)
fait-il mieux que A0 ? Trois ingrédients séparés : entrées au niveau récent (5 ans), shrinkage hiérarchique,
borne 1,2 (croissance proportionnelle au stock hors entrées). Aucune affirmation de précision n'en découle.
Lancer : PYTHONPATH=v2 uv run python -m methodes.ablation"""
import pandas as pd

from methodes.estimators import _variant
from methodes.perimetres import prive
from validation import registry
from validation.forecast import bench, design

V = {
    "A0": registry.get("jumeau_taux_locaux"),
    "A0+recent5": _variant("R5", "A0 + entrées récentes 5 ans", "", inflow_recent=5),
    "A2+recent5": _variant("H5", "A2 + entrées récentes 5 ans", "", hier=True, inflow_recent=5),
    "B4 sans hier": _variant("O1", "B4 sans hiérarchie", "", obs_r12=True),
    "B4": registry.get("axe2_obs_r12"),
}
t = prive()
e = bench(V, t, design(t))
m = e[(e.n_origin >= 30)]
g = m.groupby(["model", "h", "profession", "origin"]).ape.mean()
p = g.groupby(["model", "h", "profession"]).mean().unstack("profession")
p["pooled"] = g.groupby(["model", "h"]).mean()
nat = m.groupby(["model", "h", "profession", "origin"]).apply(lambda x: 100 * (x.pred.sum() / x.actual.sum() - 1))
p["biais_nat_moy"] = nat.groupby(["model", "h"]).mean()
print(p.round(2).to_string())
p.round(3).to_csv("v2/methodes/out/ablation_exploratoire.csv")
