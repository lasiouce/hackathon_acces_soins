"""Banc C1-GBM : modèle global (GBM, MLP) contre A2 sur la grille N1 du périmètre privé (mêmes origines que tab:prive).

Test d'abandon inscrit avant (v2/docs/lab/derivations/2026-11-15-c1-gbm-global.md) : accepté si la borne haute de l'IC
bootstrap 95 % de MAPE(candidat) − MAPE(A2) à h = 5 est < 0, sinon rejeté. Tirages appariés (methodes.banc.boot).
Contrôle de fuite : perturbation de toutes les données postérieures à l'origine -> prédictions identiques.
Lancer : OMP_NUM_THREADS=4 PYTHONPATH=v2 uv run --with scikit-learn==1.9.1 python -m methodes.c1_gbm   -> v2/methodes/out/c1_gbm*
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.banc import boot, summary
from methodes.gbm import GlobalGBM, GlobalMLP, population
from methodes.perimetres import prive
from validation import registry
from validation.forecast import BOOT, H_MAIN, MIN_N, SEED, bench, design

OUT = Path("v2/methodes/out")
A2 = "axe2_shrink_hier"
NAIVES = ("naive_persistance", "naive_tendance")
CANDS = {"c1_gbm_global": GlobalGBM, "c1_mlp_global": GlobalMLP}


def leak_check(t: pd.DataFrame, pop: pd.DataFrame, origin: int = 2019) -> dict:
    """Remplace stock et population d'années > origine par du bruit : les prédictions doivent rester identiques."""
    rng = np.random.default_rng(1)
    t2, pop2 = t.copy(), pop.copy()
    t2.loc[t2.year > origin, "n"] = rng.uniform(0, 1e4, (t2.year > origin).sum())
    pop2.loc[pop2.year > origin, "pop"] = rng.uniform(0, 1e7, (pop2.year > origin).sum())
    res = {}
    for name, E in CANDS.items():
        preds = []
        for tt, pp in ((t, pop), (t2, pop2)):
            E.panel, E.pop, E._cache = tt, pp, {}
            e = E().fit(tt[(tt.profession == "dentistes") & (tt.year <= origin)], (2012, origin), origin)
            preds.append(pd.concat([e.predict(y) for y in range(origin + 1, int(t.year.max()) + 1)]))
        res[name] = float((preds[0] - preds[1]).abs().max())
    return res


def paired(e: pd.DataFrame, cand: str) -> dict:
    """Δ = MAPE(cand) − MAPE(A2) à h = 5, IC bootstrap apparié, au total et par profession."""
    out = {}
    for prof in [None] + sorted(e.profession.unique()):
        ee = e if prof is None else e[e.profession == prof]
        m = ee[(ee.h == H_MAIN) & (ee.n_origin >= MIN_N)]
        if m.empty:
            continue
        b = boot(ee, (cand, A2) + NAIVES)
        pooled = m.groupby(["model", "profession", "origin"]).ape.mean().groupby("model").mean()
        d = b[cand] - b[A2]
        lo, hi = np.quantile(d, [0.025, 0.975])
        out[prof or "total"] = {
            "mape": round(float(pooled[cand]), 2), "mape_A2": round(float(pooled[A2]), 2),
            "mape_tendance": round(float(pooled["naive_tendance"]), 2),
            "delta": round(float(pooled[cand] - pooled[A2]), 2), "ci95": [round(float(lo), 2), round(float(hi), 2)],
            "ci975_bonferroni": [round(float(np.quantile(d, .0125)), 2), round(float(np.quantile(d, .9875)), 2)],
            "origines": int(m.origin.nunique()), "cellules": int(m.groupby(["profession", "origin"]).ngroups),
            "issue": "gagne" if hi < 0 else ("perd" if lo > 0 else "égalité"),
        }
    out["verdict"] = "accepté" if out["total"]["ci95"][1] < 0 else "rejeté"
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    t, pop = prive(), population()
    leak = leak_check(t, pop)
    print("contrôle de fuite (écart max après perturbation du futur) :", leak)
    assert all(v == 0 for v in leak.values()), "fuite détectée"
    for E in CANDS.values():
        E.panel, E.pop, E._cache = t, pop, {}
    ests = {k: registry.get(k) for k in NAIVES + (A2,)} | CANDS
    t0 = time.perf_counter()
    e = bench(ests, t, design(t))
    secs = time.perf_counter() - t0
    e.to_parquet(OUT / "c1_gbm_erreurs.parquet", index=False)
    cells = summary(e)
    cells.to_csv(OUT / "c1_gbm_cellules.csv", index=False)
    res = {"secondes_banc": round(secs, 1), "fuite": leak, "boot": BOOT, "graine": SEED,
           "mape_par_h": cells.groupby(["model", "h"]).mape.mean().round(2).unstack().to_dict("index"),
           "biais_nat_h5": cells[cells.h == H_MAIN].groupby(["model", "profession"]).biais_nat.mean().round(2)
           .unstack().to_dict("index")}
    for k in CANDS:
        res[k] = paired(e, k)
    (OUT / "c1_gbm_verdicts.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(f"banc {secs:.0f} s")
    for k in CANDS:
        print(f"\n== {k} : {res[k]['verdict']} ==")
        for p, v in res[k].items():
            if p != "verdict":
                print(f"{p:20s} MAPE {v['mape']:6.2f} A2 {v['mape_A2']:6.2f} tend {v['mape_tendance']:6.2f} "
                      f"Δ {v['delta']:+.2f} IC95 [{v['ci95'][0]:+.2f};{v['ci95'][1]:+.2f}] {v['issue']} "
                      f"({v['cellules']} cellules)")
    print("\nMAPE par h :", json.dumps(res["mape_par_h"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
