"""Banc communal (protocole N4, SHA 91f897cc5071, fonctions de validation.fine_scale) pour le modèle K.

Professions IDE, MK, CD ; origines 2014, 2016, 2018, 2020 ; h = 5 ; exclusion des sauts (règle N4).
Estimateurs : K (moyenne μ et bande P10–P90 binomiale négative), défaut N4 avec oracle (total dép. réel × part
tenue), défaut sans oracle (total dép. de K × part tenue), persistance.
Sorties : P80 de |erreur| par classe et N_min (règle N4), couverture de la bande à 80 % par classe et profession.
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.banc_communes > v2/methodes/out/com_banc.log
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.communes import K, exclusion, load, quantiles, variance
from validation.fine_scale import BINS, LABELS, n_min, share_out, size_errors

OUT = Path("v2/methodes/out")
PROFS = ("infirmiers-liberaux", "kines", "dentistes")
ORIGINS, H = (2014, 2016, 2018, 2020), 5


def main():
    t0 = time.time()
    rows, cov, k = [], [], 0
    for prof in PROFS:
        N, years, geo = load(prof)
        tot = N.sum(1)
        com = pd.Index(geo.com)
        dep = pd.Series(geo.dep.to_numpy(), index=com)
        for o in ORIGINS:
            io, it = list(years).index(o), list(years).index(o + H)
            n0, act = pd.Series(tot[:, io], index=com), pd.Series(tot[:, it], index=com)
            keep = ~exclusion(tot, years, o, H)
            m = K(N, years, geo, o)
            mu = pd.Series(m.project(H)[-1].sum(1), index=com)
            a, b = variance(N, years, geo, o, H)
            lo, hi = quantiles(mu.to_numpy(), a, b)
            preds = {"K": mu,
                     "defaut_oracle": share_out(act.groupby(dep).sum(), n0, dep),
                     "defaut_sans_oracle": share_out(mu.groupby(dep).sum(), n0, dep),
                     "persistance": n0}
            for name, p in preds.items():
                tab = size_errors(p[keep], act[keep], n0[keep]).reset_index().assign(profession=prof, origine=o,
                                                                                     estimateur=name)
                rows.append(tab)
            d = pd.DataFrame({"n0": n0, "act": act, "lo": lo, "hi": hi, "mu": mu})[keep & (n0.to_numpy() >= 1)]
            d["cls"] = pd.cut(d.n0, BINS, right=False, labels=LABELS)
            d["in80"] = (d.act >= d.lo) & (d.act <= d.hi)
            g = d.groupby("cls", observed=False).agg(couverture=("in80", "mean"), communes=("in80", "size"))
            cov.append(g.reset_index().assign(profession=prof, origine=o, alpha=a, beta=b))
            k += 1
            print(f"{k}/{len(PROFS) * len(ORIGINS)} · {prof} {o} · α={a:.2f} β={b:.4f} · "
                  f"couverture80 {d.in80.mean():.3f} · {time.time() - t0:.0f} s", flush=True)
    T = pd.concat(rows, ignore_index=True)
    C = pd.concat(cov, ignore_index=True)
    T.to_csv(OUT / "com_tables.csv", index=False)
    C.to_csv(OUT / "com_couverture.csv", index=False)
    res = {"N_min": {}, "couverture_par_classe": {}, "P80_par_classe": {}}
    for est in T.estimateur.unique():
        nm = {f"{p} {o}": n_min(T[(T.estimateur == est) & (T.profession == p) & (T.origine == o)].set_index("cls"))
              for p in PROFS for o in ORIGINS}
        res["N_min"][est] = {k2: (None if np.isinf(v) else v) for k2, v in nm.items()}
        res["P80_par_classe"][est] = (T[T.estimateur == est].groupby(["profession", "cls"], observed=False)["P80_abs_%"]
                                      .mean().round(1).unstack().to_dict())
    w = C.assign(n=C.communes * C.couverture)
    agg = w.groupby(["profession", "cls"], observed=False).agg(n=("n", "sum"), communes=("communes", "sum"))
    agg["couverture"] = agg.n / agg.communes
    agg["passe"] = agg.couverture.between(0.75, 0.85)
    res["couverture_par_classe"] = {f"{p}|{c}": {"couverture": round(float(r.couverture), 3), "communes": int(r.communes),
                                                 "passe": bool(r.passe)} for (p, c), r in agg.iterrows() if r.communes}
    c20 = C[C.origine == 2020]
    res["couverture_2020"] = {f"{r.profession}|{r.cls}": round(float(r.couverture), 3)
                              for r in c20.itertuples() if r.communes}
    (OUT / "com_verdicts.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    print(agg.round(3).to_string(), flush=True)
    print(json.dumps(res["N_min"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
