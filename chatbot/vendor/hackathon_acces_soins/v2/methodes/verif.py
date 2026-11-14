"""Vérifications des méthodes de l'axe 2, sans regarder aucune cible (aucun score de banc ici).

  V1  calibrage uniforme = sante.model.fit_rates (s et entrées), écart 0
  V2  composition methodes aux options v1 = twin_of(StockFlowLocal) : predict identique, écart 0
  V3  désagrégation : masse de chaque tranche conservée ; vieillissement A conserve la masse totale
  V4  levier λ (tendance_60plus) : λ = 0 rend la rétention stationnaire = variante sans tendance
  V5  temps de recalcul par scénario au département (5 professions)
Lancer : PYTHONPATH=v2 uv run python -m methodes.verif   (code de sortie 1 en cas d'échec)
"""
import sys
import time

import numpy as np

from jumeau.estimators import twin_of
from jumeau.scenario import Scenario
from methodes import calibrage, estimators as M
from methodes.modules import COMPOSITION
from methodes.perimetres import prive
from sante.estimators import StockFlowLocal
from sante.model import fit_rates


def main() -> int:
    t = prive()
    ok = True
    o, fy = 2021, (2012, 2021)
    tp = t[(t.profession == "dentistes") & (t.year <= o)]
    s, i, _ = fit_rates(tp, fy, shrink=200)
    c = calibrage.fit(tp, fy, shrink=200)
    d1 = max(np.abs(s - c["s"]).max(), np.abs(i - c["inflow"]).max())
    print(f"V1 calibrage uniforme vs fit_rates : écart max {d1:.2e}")
    ok &= d1 < 1e-9

    worst = 0.0
    for p in t.profession.unique():
        tp = t[(t.profession == p) & (t.year <= o)]
        f = (2017, o) if p == "kines" else (2012, o)
        a = M.Uniforme().fit(tp, f, o).predict(o + 5)
        b = twin_of(StockFlowLocal)().fit(tp, f, o).predict(o + 5)
        worst = max(worst, float((a - b.reindex(a.index)).abs().max()))
    print(f"V2 composition methodes (options v1) vs twin_of(StockFlowLocal) : écart max {worst:.2e} personnes")
    ok &= worst < 1e-6

    A = calibrage.Ages(np.array([0, 25, 30, 35, 40, 45, 50, 55, 60, 65]))
    N = np.abs(np.random.default_rng(1).normal(100, 60, (50, 10)))
    d3 = max(np.abs(A.merge(A.split(N)) - N).max(), np.abs(A.age(N).sum(1) - N.sum(1)).max())
    print(f"V3 conservation (désagrégation, vieillissement) : écart max {d3:.2e}")
    ok &= d3 < 1e-9

    tp = t[(t.profession == "pharmaciens") & (t.year <= o)]
    e = M.Retention60().fit(tp, (2012, o), o)
    lam0 = e.trajectory(o + 5, Scenario(params={"methodes_sorties.tendance_60plus": 0.0}, modules=COMPOSITION))
    ref = M.Uniforme().fit(tp, (2012, o), o).predict(o + 5)
    got = lam0.states[o + 5].total()
    d4 = float((got.values - ref.values).__abs__().max())
    print(f"V4 λ = 0 vs sans tendance : écart max {d4:.2e} personnes ; "
          f"λ = 1 vs 0, national 2026 : {e.predict(o + 5).sum() - ref.sum():+.0f}")
    ok &= d4 < 1e-6

    for cls in (M.Uniforme, M.AgesInterp, M.AgesSimples, M.Combine):
        ests = [cls().fit(t[(t.profession == p) & (t.year <= o)], (2017 if p == "kines" else 2012, o), o)
                for p in t.profession.unique()]
        for e in ests:
            e.trajectory(o + 1)                                   # calibrage hors chrono
        t0 = time.perf_counter()
        for e in ests:
            e.trajectory(2050, Scenario(name="x", modules=COMPOSITION))
        print(f"V5 {cls.name:32s} recalcul 5 professions × dép jusqu'en 2050 : {1000 * (time.perf_counter() - t0):.0f} ms")
    print("OK" if ok else "ÉCHEC")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
