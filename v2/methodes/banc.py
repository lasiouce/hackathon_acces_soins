"""Banc N1 (protocole axe 3, SHA eb527ecb06a0) sur les variantes inscrites de l'axe 2.

Utilise validation.forecast (design, bench, verdict) sans le modifier. Le bootstrap vectorisé ci-dessous
reproduit les tirages de verdict() (même graine, même séquence) pour donner, en plus, l'IC à 99 %
(Bonferroni sur 5 variantes) et l'écart exploratoire à la référence stock-flux (A0).
Lancer : PYTHONPATH=v2 uv run python -m methodes.banc   -> v2/methodes/out/
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.perimetres import ancien, prive
from validation import registry
from validation.forecast import BOOT, H_MAIN, MIN_N, SEED, bench, design, verdict

OUT = Path("v2/methodes/out")
NAIVES = ("naive_persistance", "naive_tendance")
A0 = "jumeau_taux_locaux"
CANDS = ("axe2_ages_interp", "axe2_ages_simples", "axe2_shrink_hier", "axe2_retention60", "axe2_combine")
DIAG = ("axe2_obs_r12",)


def boot(e: pd.DataFrame, models) -> dict:
    """MAPE poolée par tirage bootstrap des départements (mêmes tirages que verdict) : model -> [BOOT]."""
    m = e[(e.h == H_MAIN) & (e.n_origin >= MIN_N)]
    deps = m.territory.unique()
    rng = np.random.default_rng(SEED)
    W = np.stack([np.bincount(pd.Index(deps).get_indexer(rng.choice(deps, len(deps))), minlength=len(deps))
                  for _ in range(BOOT)]).astype(float)                       # [B, D]
    out = {}
    for k in models:
        a = (m[m.model == k].pivot_table(index=["profession", "origin"], columns="territory", values="ape")
             .reindex(columns=deps))
        mask = a.notna().to_numpy(float)
        v = np.nan_to_num(a.to_numpy())
        out[k] = ((W @ v.T) / (W @ mask.T)).mean(1)                         # moyenne des cellules à poids égal
    return out


def summary(e: pd.DataFrame) -> pd.DataFrame:
    g = e[e.n_origin >= MIN_N].groupby(["model", "profession", "origin", "h"])
    cell = pd.DataFrame({"mape": g.ape.mean(), "wape": g.apply(lambda x: 100 * (x.pred - x.actual).abs().sum()
                                                                / x.actual.sum()),
                         "biais_nat": g.apply(lambda x: 100 * (x.pred.sum() / x.actual.sum() - 1))})
    return cell.reset_index()


def run(label: str, t: pd.DataFrame) -> dict:
    names = NAIVES + (A0,) + CANDS + DIAG
    ests = {k: registry.get(k) for k in names}
    t0 = time.perf_counter()
    e = bench(ests, t, design(t))
    secs = time.perf_counter() - t0
    e.to_parquet(OUT / f"erreurs_{label}.parquet", index=False)
    cells = summary(e)
    cells.to_csv(OUT / f"cellules_{label}.csv", index=False)
    b = boot(e, names)
    res = {"perimetre": label, "secondes_banc": round(secs, 1), "candidats": {}}
    for k in CANDS + (A0,) + DIAG:
        v = verdict(e, k)                                                   # critère officiel (IC 95 %)
        best = v["best_naive"]
        d = b[k] - b[best]
        d0 = b[k] - b[A0]
        h5 = cells[(cells.h == H_MAIN) & (cells.model == k)]
        ref5 = cells[(cells.h == H_MAIN) & (cells.model == best)].set_index(["profession", "origin"]).mape
        sign = (h5.set_index(["profession", "origin"]).mape - ref5).groupby(level="profession").agg(
            lambda x: f"{(x < 0).sum()}/{len(x)}")
        res["candidats"][k] = {
            **v, "ci_boot_vectorise_95": [float(np.quantile(d, .025)), float(np.quantile(d, .975))],
            "ci99_bonferroni": [float(np.quantile(d, .005)), float(np.quantile(d, .995))],
            "delta_vs_A0": float(v["mape"][k] - v["mape"][A0]),
            "ci95_vs_A0": [float(np.quantile(d0, .025)), float(np.quantile(d0, .975))],
            "origines_gagnees_par_profession": sign.to_dict(),
            "mape_h5_par_profession": h5.groupby("profession").mape.mean().round(2).to_dict(),
            "biais_nat_h5_par_profession": h5.groupby("profession").biais_nat.mean().round(2).to_dict(),
            "mape_par_h": cells[cells.model == k].groupby(["h", "profession", "origin"]).mape.mean()
            .groupby("h").mean().round(2).to_dict(),
        }
    return res


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    which = sys.argv[1:] or ["prive", "ancien"]
    out = {}
    for label in which:
        out[label] = run(label, {"prive": prive, "ancien": ancien}[label]())
        (OUT / f"verdicts_{label}.json").write_text(json.dumps(out[label], indent=1, ensure_ascii=False, default=str))
        r = out[label]["candidats"]
        print(f"\n== périmètre {label} ({out[label]['secondes_banc']} s) ==")
        for k, v in r.items():
            print(f"{k:22s} MAPE h5 {v['mape'][k]:6.2f}  vs {v['best_naive']} {v['mape'][v['best_naive']]:6.2f}  "
                  f"Δ {v['delta']:+.2f} IC95 [{v['ci'][0]:+.2f};{v['ci'][1]:+.2f}] {v['issue']:8s} "
                  f"| vs A0 {v['delta_vs_A0']:+.2f} [{v['ci95_vs_A0'][0]:+.2f};{v['ci95_vs_A0'][1]:+.2f}] "
                  f"| nat {v['precision_nationale']} h1ok {v['limite_h1_ok']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
