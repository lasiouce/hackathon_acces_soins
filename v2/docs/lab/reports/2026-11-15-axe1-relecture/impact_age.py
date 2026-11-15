"""Impact de l'âge d'entrée des diplômés à l'étranger (28 → 26 MK, 28 → 31 PH, 28 → 32 CD) sur N(2050), multiplicateur 2."""
import numpy as np
from jumeau.check import sector_table, twin_of, V1, run, Scenario, LEVIERS_
for prof, alt in [("kines", 26.0), ("pharmaciens", 31.0), ("dentistes", 32.0)]:
    t = sector_table([prof]); o = int(t.year.max())
    est = twin_of(V1.StockFlowLocal)().fit(t, (o - 5, o), o)
    out = {}
    for a in (28.0, alt):
        sc = Scenario(modules=LEVIERS_, params={"etrangers.multiplicateur": 2.0, "etrangers.age_entree": a}).over(est.scenario)
        tr = run(est.state, est.modules(sc), sc, 2050)
        out[a] = tr.states[2050].N.sum()
    print(prof, "ages", list(est.state.ages), {k: round(v, 1) for k, v in out.items()},
          "écart %+.1f (%.3f %%)" % (out[alt] - out[28.0], 100 * (out[alt] - out[28.0]) / out[28.0]))
