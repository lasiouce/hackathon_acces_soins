"""Banc de vitesse à l'échelle de la commune : 5 professions, 2 secteurs, ~35 000 communes, origine → 2050.

État communal **ventilé** (mesure de temps et de chemin, pas une projection communale validée) :
chaque cellule départementale (profession, secteur, dep, sexe) est répartie entre les communes du
département au prorata de la population (Insee, v2/data/processed/commune_geo.parquet) ; les taux
ajustés au département sont recopiés sur ses communes. Les tranches d'âge diffèrent d'une source à
l'autre : un état par profession, temps total = somme.
  SF, CD, PH, MK : secteurs privé / public de l'axe 4 (sector_table, part centrale)
  IDE            : v1, infirmiers-liberaux (privé) et infirmiers-salaries (public), tranches v1

Run (racine) : PYTHONPATH=v2 uv run python -m jumeau.bench_commune [--profile]
"""
import sys
import time

import numpy as np
import pandas as pd

from sante import estimators as V1
from sante.model import stock_table
from jumeau.engine import build, run
from jumeau.estimators import twin_of
from jumeau.history import History, sector_table
from jumeau.modules.entrees import evenement_quotas
from jumeau.scenario import Event, Scenario
from jumeau.state import State

H = 2050


def scenario(o):
    return Scenario("retraite +1, quotas ×1,1", events=[Event("sorties.decalage_retraite", o + 1, 1.0),
                                                       evenement_quotas(1.1, o, 5)])


def dep_estimators():
    out = []
    for p in ["sages-femmes", "dentistes", "pharmaciens", "kines"]:
        t = sector_table([p])
        o = int(t.year.max())
        out.append(twin_of(V1.StockFlowLocal)().fit(t, (o - 5, o), o))
    ti = stock_table(["infirmiers-liberaux", "infirmiers-salaries"])
    ti = ti[ti.year >= 2013]
    ti = ti.assign(sector=np.where(ti.profession == "infirmiers-liberaux", "prive", "public"), profession="infirmiers")
    ti = ti.groupby(["profession", "sector", "dep", "sex", "age_lo", "year"], as_index=False).n.sum()
    o = int(ti.year.max())
    out.append(twin_of(V1.StockFlowLocal)().fit(ti, (o - 5, o), o))
    return out


def to_communes(est):
    """(state communal, History avec taux recopiés) à partir d'un estimateur départemental calibré."""
    est.trajectory(est.origin + 1)                          # calibre les taux
    S, I, P = est.hist._cache[("rates", len(est.state.cells))]
    geo = pd.read_parquet("v2/data/processed/commune_geo.parquet", columns=["com", "dep", "population"])
    geo = geo[geo.population > 0]
    geo["w"] = geo.population / geo.groupby("dep").population.transform("sum")
    c = est.state.cells.reset_index().rename(columns={"index": "i"})
    m = c.merge(geo, left_on="territory", right_on="dep", how="inner")
    idx = m.i.to_numpy()
    cells = m.assign(territory=m.com)[["profession", "sector", "territory", "sex"]].reset_index(drop=True)
    N = est.state.N[idx] * m.w.to_numpy()[:, None]
    st = State(cells, est.state.ages, N, est.state.year, level="com")
    hist = History(est.hist.table, est.origin, est.fit_years, options=est.hist.options)
    hist._cache[("rates", len(cells))] = (S[idx], I[idx] * m.w.to_numpy()[:, None], P[idx] * m.w.to_numpy()[:, None])
    return st, hist


def main(profile=False):
    ests = dep_estimators()
    states = []
    for e in ests:
        st, hist = to_communes(e)
        sc = scenario(e.origin)
        mods = build(sc.composition)
        for m in mods:
            m.fit(hist)
        states.append((st, mods, sc))
    run(*states[0][:2], states[0][2], states[0][0].year + 2)  # échauffement
    if profile:
        import cProfile
        import pstats
        pr = cProfile.Profile()
        pr.enable()
        for st, mods, sc in states:
            run(st, mods, sc, H, ledger=False)
        pr.disable()
        pstats.Stats(pr).sort_stats("tottime").print_stats(18)
        return
    ts, cpu = [], []
    for _ in range(3):
        t0, c0 = time.perf_counter(), time.process_time()
        for st, mods, sc in states:
            run(st, mods, sc, H, ledger=False)
        ts.append(time.perf_counter() - t0)
        cpu.append(time.process_time() - c0)        # temps CPU du processus : moins sensible aux autres charges
    cells = sum(len(st.cells) for st, _, _ in states)
    import os
    load = os.getloadavg()[0]
    print(f"5 professions, {cells} cellules communales, {H - states[0][0].year} ans : "
          f"médiane {np.median(ts):.2f} s réel, {np.median(cpu):.2f} s CPU (runs {[round(t, 2) for t in ts]}, "
          f"charge machine {load:.1f})")
    return dict(seconds=float(np.median(ts)), cpu_seconds=float(np.median(cpu)), runs=ts, cpu_runs=cpu, cells=cells,
                load=load)


if __name__ == "__main__":
    main(profile="--profile" in sys.argv)
