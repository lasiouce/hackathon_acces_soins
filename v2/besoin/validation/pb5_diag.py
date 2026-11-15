"""Diagnostic a posteriori de P-B5 (non décisif, écrit après le passage) : GBM sans les covariables de densité, et
corrélation de sa cible avec la croissance de l'effectif ameli 2016 → 2025.
Run : PYTHONPATH=v2 uv run --with scikit-learn --with xlrd --with openpyxl python v2/besoin/validation/pb5_diag.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from besoin.cube import Population, mapping
from besoin.estimateurs.recours import PROF_AMELI, effectif_ameli
from besoin.validation import pb5
om = Population.load()
pops = {y: pb5.population(y, om) for y in (pb5.O, pb5.CIBLE)}
reg = mapping("dep", "reg")
for p in PROF_AMELI:
    t = pb5.predictions(p, pops, pb5.CIBLE)
    X, _ = pb5.covariables(p, t, pops, pb5.CIBLE)
    y = np.log(t.R / t.M1).to_numpy(); g = reg.reindex(t.index).astype(str).to_numpy(); R = t.R.to_numpy()
    sans = X.drop(columns=["log_dens", "log_dens_autres"])
    gb = t.M1.to_numpy() * np.exp(pb5.gbm_loro(sans.to_numpy(), y, g))
    E = effectif_ameli(p, [2016, 2025]); gN = (E[2025] / E[2016]).reindex(t.index)
    c = np.corrcoef(np.log(gN), y)[0, 1]
    print(f"{p:13s} MAPE GBM sans densités {pb5.mape(gb, R):.2f} ; croissance effectif ameli 2016→2025 médiane {gN.median():.2f} ; corr(log croiss. N, cible GBM) {c:.2f}")
