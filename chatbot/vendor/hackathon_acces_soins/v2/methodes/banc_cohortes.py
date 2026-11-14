"""Banc de l'étape 2 : N1 (MAPE, protocole eb527ecb06a0) et N6 (CRPS sur log N, PIT, couverture ; protocole gelé).

Estimateurs : naïves, A0 (jumeau_taux_locaux), APC (étape 1), C1 (θ fixé), C2 (θ propagé). Périmètre privé.
N6, distribution prédictive :
  - estimateurs à tirages (APC, C1, C2) : 200 tirages ;
  - estimateurs ponctuels : prédit × exp(e), e = erreurs log(réel/prédit) du même estimateur, même profession,
    h = 5, origines dont la cible ≤ l'origine courante, départements N ≥ 30 ; ≥ 20 erreurs, sinon exclu.
  - CRPS sur log N ; meilleure naïve probabiliste = celle des deux naïves au CRPS poolé le plus bas ;
    Δ et IC par le bootstrap des départements de N1 ; couverture des intervalles centraux à 80 et 50 %.
Secondaire (hors protocole) : couverture et CRPS des estimateurs à tirages sur toutes les origines.
Verdict par profession : Δ MAPE vs A0 et Δ CRPS vs meilleure naïve probabiliste, IC par bootstrap des dép.
Progression : une ligne k/N par ajustement dans le journal.
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.banc_cohortes > v2/methodes/out/coh_banc.log
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.apc import APCEstimator
from methodes.banc import boot
from methodes.cohortes import CohortesEstimator, CohortesLaplace
from methodes.perimetres import prive
from validation import registry
from validation.forecast import H_MAIN, MIN_N, SEED, bench, design, verdict

OUT = Path("v2/methodes/out")
FITTED, COUNT = {}, {"k": 0, "N": 0, "t0": time.time()}
DRAWS = ("axe2_apc", "axe2_cohortes_c1", "axe2_cohortes_c2")


def recorded(cls, key, **opts):
    class R(cls):
        options = {**cls.options, **opts}

        def fit(self, t, fit_years, origin):
            super().fit(t, fit_years, origin)
            FITTED[(key, t.profession.iloc[0], origin)] = self
            COUNT["k"] += 1
            print(f"{COUNT['k']}/{COUNT['N']} ajustements · {key} {t.profession.iloc[0]} {origin} · "
                  f"{time.time() - COUNT['t0']:.0f} s", flush=True)
            return self
    return R


def crps(x, y):
    x = np.sort(x)
    n = len(x)
    i = np.arange(1, n + 1)
    return float(np.abs(x - y).mean() - ((2 * i - n - 1) * x).sum() / (n * n))


def boot_pairs(df, col, a, b, B=2000):
    """IC 95 % de moyenne(col | a) − moyenne(col | b), cellules à poids égal, bootstrap des départements."""
    rng = np.random.default_rng(SEED)
    deps = df.territory.unique()
    piv = {k: df[df.model == k].pivot_table(index=["profession", "origin"], columns="territory", values=col)
           .reindex(columns=deps) for k in (a, b)}
    out = []
    for _ in range(B):
        w = np.bincount(pd.Index(deps).get_indexer(rng.choice(deps, len(deps))), minlength=len(deps)).astype(float)
        v = [np.nansum(p.to_numpy() * w, 1) / np.nansum(p.notna().to_numpy() * w, 1) for p in piv.values()]
        out.append(np.nanmean(v[0]) - np.nanmean(v[1]))
    d = float(piv[a].stack().groupby(level=[0, 1]).mean().mean() - piv[b].stack().groupby(level=[0, 1]).mean().mean())
    return d, [float(np.quantile(out, .025)), float(np.quantile(out, .975))]


def main():
    t = prive()
    grid = design(t)
    ests = {k: registry.get(k) for k in ("naive_persistance", "naive_tendance", "jumeau_taux_locaux")}
    ests["axe2_apc"] = recorded(APCEstimator, "axe2_apc", S=200)
    ests["axe2_cohortes_c1"] = recorded(CohortesEstimator, "axe2_cohortes_c1")
    ests["axe2_cohortes_c2"] = recorded(CohortesLaplace, "axe2_cohortes_c2")
    COUNT["N"] = 3 * len(grid)
    e = bench(ests, t, grid)
    e.to_parquet(OUT / "coh_erreurs.parquet", index=False)
    res = {"N1": {}, "N6": {}, "secondaire": {}, "par_profession": {}}
    b = boot(e, list(ests))
    for k in ("jumeau_taux_locaux",) + DRAWS:
        v = verdict(e, k)
        d0 = b[k] - b["jumeau_taux_locaux"]
        res["N1"][k] = {**v, "delta_vs_A0": float(v["mape"][k] - v["mape"]["jumeau_taux_locaux"]),
                        "ci95_vs_A0": [float(np.quantile(d0, .025)), float(np.quantile(d0, .975))]}
    print("N1 fait", flush=True)

    # --- N6 : distributions prédictives à h = 5 ---
    m = e[(e.h == H_MAIN) & (e.n_origin >= MIN_N)].copy()
    m["logerr"] = np.log(m.actual / m.pred.clip(lower=0.5))
    rows = []
    for (key, prof, origin), est in FITTED.items():
        cell = m[(m.profession == prof) & (m.origin == origin) & (m.model == key)]
        if cell.empty:
            continue
        smp = est.sample(origin + H_MAIN)
        smp.index = smp.index.set_names(["profession", "territory"])
        for _, r in cell.iterrows():
            x = smp.loc[(prof, r.territory)].to_numpy()
            rows.append({"model": key, "profession": prof, "origin": origin, "territory": r.territory,
                         "actual": r.actual, "n_origin": r.n_origin, "h": H_MAIN, "tirages": True,
                         "crps": crps(np.log(np.maximum(x, 0.5)), np.log(r.actual)),
                         "pit": float((x <= r.actual).mean()),
                         "in80": bool(np.quantile(x, .1) <= r.actual <= np.quantile(x, .9)),
                         "in50": bool(np.quantile(x, .25) <= r.actual <= np.quantile(x, .75))})
    for key in ("naive_persistance", "naive_tendance", "jumeau_taux_locaux"):
        mk = m[m.model == key]
        for (prof, origin), cell in mk.groupby(["profession", "origin"]):
            past = mk[(mk.profession == prof) & (mk.origin + H_MAIN <= origin)].logerr.to_numpy()
            if len(past) < 20:
                continue
            for _, r in cell.iterrows():
                x = np.log(max(r.pred, 0.5)) + past
                rows.append({"model": key, "profession": prof, "origin": origin, "territory": r.territory,
                             "actual": r.actual, "n_origin": r.n_origin, "h": H_MAIN, "tirages": False,
                             "crps": crps(x, np.log(r.actual)), "pit": float((x <= np.log(r.actual)).mean()),
                             "in80": bool(np.quantile(x, .1) <= np.log(r.actual) <= np.quantile(x, .9)),
                             "in50": bool(np.quantile(x, .25) <= np.log(r.actual) <= np.quantile(x, .75))})
    p = pd.DataFrame(rows)
    p.to_csv(OUT / "coh_probabiliste.csv", index=False)
    judged = p[~p.tirages][["profession", "origin"]].drop_duplicates()       # cellules où les naïves sont définies
    pj = p.merge(judged, on=["profession", "origin"])
    pooled = pj.groupby(["model", "profession", "origin"]).crps.mean().groupby("model").mean()
    best = min(("naive_persistance", "naive_tendance"), key=lambda k: pooled[k])
    for k in ("jumeau_taux_locaux",) + DRAWS:
        g = pj[pj.model == k]
        d, ci = boot_pairs(pj.rename(columns={}), "crps", k, best)
        res["N6"][k] = {"crps_log": float(pooled[k]), "meilleure_naive": best, "crps_naive": float(pooled[best]),
                        "delta": d, "ci95": ci, "issue": "gagne" if ci[1] < 0 else ("perd" if ci[0] > 0 else "égalité"),
                        "couverture80": float(g.in80.mean()), "couverture50": float(g.in50.mean()),
                        "calibre80": bool(0.75 <= g.in80.mean() <= 0.85), "calibre50": bool(0.44 <= g.in50.mean() <= 0.56),
                        "pit10": np.histogram(g.pit, bins=10, range=(0, 1))[0].tolist(), "n": int(len(g)),
                        "cellules": judged.astype(str).values.tolist()}
    res["N6"]["exclues"] = "cellules sans 20 erreurs passées : toutes sauf origine 2021 pour SF, CD, PH (h = 5)"
    for k in DRAWS:
        g = p[p.model == k]
        res["secondaire"][k] = {"couverture80_toutes_origines": float(g.in80.mean()),
                                "couverture50_toutes_origines": float(g.in50.mean()),
                                "crps_log_toutes_origines": float(g.groupby(["profession", "origin"]).crps.mean().mean()),
                                "couverture80_par_profession": g.groupby("profession").in80.mean().round(3).to_dict(),
                                "pit10": np.histogram(g.pit, bins=10, range=(0, 1))[0].tolist(), "n": int(len(g))}
    # --- verdicts par profession ---
    mm = m.rename(columns={"ape": "ape"})
    for prof in sorted(m.profession.unique()):
        res["par_profession"][prof] = {}
        for k in DRAWS:
            d, ci = boot_pairs(mm[mm.profession == prof], "ape", k, "jumeau_taux_locaux")
            r = {"mape_delta_vs_A0": d, "ci95": ci,
                 "N1": "bat" if ci[1] < 0 else ("échoue" if ci[0] > 0 else "égale")}
            pp = pj[pj.profession == prof]
            if not pp.empty and k in set(pp.model):
                d6, ci6 = boot_pairs(pp, "crps", k, best)
                r.update({"crps_delta_vs_naive": d6, "ci95_crps": ci6,
                          "N6": "bat" if ci6[1] < 0 else ("échoue" if ci6[0] > 0 else "égale"),
                          "couverture80": float(pp[pp.model == k].in80.mean())})
            res["par_profession"][prof][k] = r
    (OUT / "coh_verdicts.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    for k, v in res["N1"].items():
        print(f"N1 {k:20s} MAPE {v['mape'][k]:.2f} Δ vs A0 {v['delta_vs_A0']:+.2f} {[round(x, 2) for x in v['ci95_vs_A0']]} "
              f"vs naïve {v['issue']}", flush=True)
    for k, v in res["N6"].items():
        if isinstance(v, dict):
            print(f"N6 {k:20s} CRPS {v['crps_log']:.4f} vs {v['meilleure_naive']} {v['crps_naive']:.4f} {v['issue']} "
                  f"cov80 {v['couverture80']:.2f} cov50 {v['couverture50']:.2f}", flush=True)
    print(json.dumps(res["secondaire"], ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
