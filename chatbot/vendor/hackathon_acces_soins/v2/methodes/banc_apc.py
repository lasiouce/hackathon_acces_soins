"""Banc N1 de l'étape 1 (APC des sorties), inscrit avant passage (registry « axe2_apc », 03:58).

MAPE : validation.forecast (protocole N1, inchangé) sur naïves, A0, A3 et APC, périmètre privé.
Secondaire (programme de l'axe 2) : à h = 5, N ≥ 30, CRPS relatif (% de l'effectif réel ; pour une prévision
ponctuelle, CRPS = |erreur|), PIT et couverture des intervalles à 80 et 90 % de l'APC (S = 100 tirages).
Lancer : PYTHONPATH=v2 uv run --with scipy python -m methodes.banc_apc  -> v2/methodes/out/apc_*
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.apc import APCEstimator
from methodes.banc import boot
from methodes.perimetres import prive
from validation import registry
from validation.forecast import H_MAIN, MIN_N, bench, design, verdict

OUT = Path("v2/methodes/out")
FITTED = {}


class Recorded(APCEstimator):
    def fit(self, t, fit_years, origin):
        super().fit(t, fit_years, origin)
        FITTED[(t.profession.iloc[0], origin)] = self
        return self


def crps(samples: np.ndarray, y: float) -> float:
    x = np.sort(samples)
    n = len(x)
    return float(np.abs(x - y).mean() - (x[:, None] - x[None, :]).__abs__().sum() / (2 * n * n))


def main():
    names = ("naive_persistance", "naive_tendance", "jumeau_taux_locaux", "axe2_retention60")
    ests = {k: registry.get(k) for k in names}
    ests["axe2_apc"] = Recorded
    t = prive()
    e = bench(ests, t, design(t))
    e.to_parquet(OUT / "apc_erreurs.parquet", index=False)
    b = boot(e, list(ests))
    res = {}
    for k in ("axe2_apc", "jumeau_taux_locaux", "axe2_retention60"):
        v = verdict(e, k)
        d0 = b[k] - b["jumeau_taux_locaux"]
        res[k] = {**v, "delta_vs_A0": float(v["mape"][k] - v["mape"]["jumeau_taux_locaux"]),
                  "ci95_vs_A0": [float(np.quantile(d0, .025)), float(np.quantile(d0, .975))]}
    # secondaire : CRPS, PIT, couverture à h = 5
    m = e[(e.h == H_MAIN) & (e.n_origin >= MIN_N)]
    rows = []
    for (prof, origin), est in FITTED.items():
        cell = m[(m.profession == prof) & (m.origin == origin) & (m.model == "axe2_apc")]
        if cell.empty:
            continue
        smp = est.sample(origin + H_MAIN)
        smp.index = smp.index.set_names(["profession", "territory"])
        for _, r in cell.iterrows():
            x = smp.loc[(prof, r.territory)].to_numpy()
            rows.append({"profession": prof, "origin": origin, "territory": r.territory, "actual": r.actual,
                         "crps": crps(x, r.actual), "pit": float((x <= r.actual).mean()),
                         "in80": bool(np.quantile(x, .1) <= r.actual <= np.quantile(x, .9)),
                         "in90": bool(np.quantile(x, .05) <= r.actual <= np.quantile(x, .95)),
                         "mean_draws": float(x.mean())})
    p = pd.DataFrame(rows)
    p.to_csv(OUT / "apc_probabiliste.csv", index=False)
    pt = m.assign(crps=(m.pred - m.actual).abs())
    crel = {k: float((g.crps / g.actual * 100).groupby([g.profession, g.origin]).mean().mean())
            for k, g in pt.groupby("model")}
    crel["axe2_apc (tirages)"] = float((p.crps / p.actual * 100).groupby([p.profession, p.origin]).mean().mean())
    hist, _ = np.histogram(p.pit, bins=10, range=(0, 1))
    res["probabiliste_h5"] = {"crps_relatif_%": crel, "couverture80": float(p.in80.mean()),
                              "couverture90": float(p.in90.mean()), "pit_histogramme_10": hist.tolist(),
                              "n": int(len(p))}
    (OUT / "apc_verdicts.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    for k in ("axe2_apc", "jumeau_taux_locaux", "axe2_retention60"):
        v = res[k]
        print(f"{k:20s} MAPE {v['mape'][k]:.2f} vs {v['best_naive']} {v['mape'][v['best_naive']]:.2f} Δ {v['delta']:+.2f} "
              f"[{v['ci'][0]:+.2f};{v['ci'][1]:+.2f}] {v['issue']} | vs A0 {v['delta_vs_A0']:+.2f} "
              f"[{v['ci95_vs_A0'][0]:+.2f};{v['ci95_vs_A0'][1]:+.2f}] | h1 {v['limite_h1_ok']} nat {v['precision_nationale']}")
    print(json.dumps(res["probabiliste_h5"], ensure_ascii=False))


if __name__ == "__main__":
    main()
