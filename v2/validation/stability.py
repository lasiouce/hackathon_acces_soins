"""Axe 3, N7-B : verdict N1 origine par origine (2016, 2018, 2021 ; h = 5), tous les estimateurs du registre.

Protocole N7 (SHA-256 06ba47b91647…). Métrique, seuil N ≥ 30, bootstrap (2 000, graine 20261114) : ceux de N1.
Le bootstrap est vectorisé (poids multinomiaux sur les départements, mêmes tirages pour toutes les cellules) ; il
reproduit forecast.verdict à l'échantillonnage près.
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.stability [prive|ancien]
-> v2/validation/out/stab_<périmètre>_{errors.parquet,verdicts.csv,kendall.csv}
"""
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from validation import registry
from validation.forecast import BOOT, MIN_N, SEED, bench, design

OUT = Path(__file__).parent / "out"
ORIGINS, H = (2016, 2018, 2021), 5
NAIVES = ("naive_persistance", "naive_tendance")


def boot_delta(e: pd.DataFrame, cand: str, rng) -> dict:
    """e : erreurs d'une origine (h = 5, N ≥ 30). Δ = MAPE(cand) − MAPE(meilleure naïve), IC bootstrap."""
    deps = np.sort(e.territory.unique())
    profs = sorted(e.profession.unique())
    di = {d: i for i, d in enumerate(deps)}
    A = {}
    for m in (cand,) + NAIVES:
        M = np.full((len(profs), len(deps)), np.nan)
        for j, p in enumerate(profs):
            g = e[(e.model == m) & (e.profession == p)]
            M[j, [di[d] for d in g.territory]] = g.ape.to_numpy()
        A[m] = M
    point = {m: np.nanmean(np.nanmean(A[m], 1)) for m in A}
    best = min(NAIVES, key=lambda k: point[k])
    W = rng.multinomial(len(deps), np.full(len(deps), 1 / len(deps)), size=BOOT).astype(float)   # BOOT × dép.

    def mape(M):
        ok = ~np.isnan(M)
        num = W @ np.where(ok, M, 0).T                  # BOOT × prof
        den = W @ ok.T.astype(float)
        return np.nanmean(num / np.where(den > 0, den, np.nan), 1)
    d = mape(A[cand]) - mape(A[best])
    lo, hi = np.quantile(d, [0.025, 0.975])
    return {"mape": point[cand], "best_naive": best, "mape_naive": point[best], "delta": point[cand] - point[best],
            "lo": lo, "hi": hi, "issue": "gagne" if hi < 0 else ("perd" if lo > 0 else "égalité")}


def main(perim: str = "prive") -> None:
    from methodes.perimetres import ancien, prive
    t = prive() if perim == "prive" else ancien()
    grid = [(p, f, o, [o + H]) for p, f, o, tg in design(t) if o in ORIGINS and o + H in tg]
    names = list(registry.REGISTRY)
    errs = []
    t0 = time.time()
    for k, name in enumerate(names, 1):
        try:
            errs.append(bench({name: registry.get(name)}, t, grid))
        except Exception as ex:                          # un estimateur qui casse est rapporté, pas caché
            print(f"ÉCHEC {name}: {ex!r}", flush=True)
        print(f"{k}/{len(names)} {name} {time.time() - t0:.0f}s", flush=True)
    e = pd.concat(errs, ignore_index=True)
    OUT.mkdir(exist_ok=True)
    e.to_parquet(OUT / f"stab_{perim}_errors.parquet")
    e = e[(e.h == H) & (e.n_origin >= MIN_N)]
    rng = np.random.default_rng(SEED)
    rows = []
    for o in ORIGINS:
        eo = e[e.origin == o]
        for name in names:
            if name in NAIVES or name not in set(eo.model):
                continue
            rows.append({"origine": o, "estimateur": name, "statut": registry.REGISTRY[name][1],
                         "professions": ",".join(sorted(eo.profession.unique())), **boot_delta(eo, name, rng)})
    v = pd.DataFrame(rows)
    v.to_csv(OUT / f"stab_{perim}_verdicts.csv", index=False)
    piv = v.pivot(index="estimateur", columns="origine", values="delta")
    stable = piv.apply(lambda r: "stable" if (np.sign(r.dropna()) == np.sign(r.dropna().iloc[0])).all() else "instable", 1)
    rank = e.groupby(["origin", "model", "profession"]).ape.mean().groupby(["origin", "model"]).mean().unstack("origin")
    kt = [{"paire": f"{a}-{b}", "tau": kendalltau(rank[a], rank[b], nan_policy="omit").statistic} for a, b in combinations(ORIGINS, 2)]
    pd.DataFrame(kt).to_csv(OUT / f"stab_{perim}_kendall.csv", index=False)
    print(v.round(3).to_string())
    print(pd.concat([piv.round(3), stable.rename("signe")], axis=1).to_string())
    print(pd.DataFrame(kt).round(3).to_string())


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["prive"]))
