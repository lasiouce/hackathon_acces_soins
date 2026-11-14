"""Banc N4 de K2 (inscrite après l'échec de K, avant son propre passage). Même grille, même exclusion.
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.banc_communes_k2"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.banc_communes import H, ORIGINS, PROFS
from methodes.communes import exclusion, k2_band, k2_interval, k2_point, load
from validation.fine_scale import BINS, LABELS, n_min, size_errors

OUT = Path("v2/methodes/out")


def main():
    rows, cov = [], []
    for prof in PROFS:
        N, years, geo = load(prof)
        tot = N.sum(1)
        for o in ORIGINS:
            n0, act = tot[:, list(years).index(o)], tot[:, list(years).index(o + H)]
            keep = ~exclusion(tot, years, o, H)
            p = k2_point(N, years, geo, o, H)
            lo, hi = k2_interval(p, n0, k2_band(N, years, geo, o, H))
            idx = pd.Index(geo.com)
            rows.append(size_errors(pd.Series(p, idx)[keep], pd.Series(act, idx)[keep], pd.Series(n0, idx)[keep])
                        .reset_index().assign(profession=prof, origine=o))
            d = pd.DataFrame({"n0": n0, "in80": (act >= lo) & (act <= hi), "ok": ~np.isnan(lo)})[keep & (n0 >= 1)]
            d["cls"] = pd.cut(d.n0, BINS, right=False, labels=LABELS)
            g = d[d.ok].groupby("cls", observed=False).agg(couverture=("in80", "mean"), communes=("in80", "size"))
            cov.append(g.reset_index().assign(profession=prof, origine=o, sans_bande=int((~d.ok).sum())))
            print(prof, o, "couverture80", round(d[d.ok].in80.mean(), 3), "sans bande", int((~d.ok).sum()), flush=True)
    T, C = pd.concat(rows), pd.concat(cov)
    T.to_csv(OUT / "com_k2_tables.csv", index=False)
    C.to_csv(OUT / "com_k2_couverture.csv", index=False)
    w = C.assign(n=C.communes * C.couverture).groupby(["profession", "cls"], observed=False).agg(
        n=("n", "sum"), communes=("communes", "sum"))
    w["couverture"] = w.n / w.communes
    w["passe"] = w.couverture.between(0.75, 0.85)
    nm = {f"{p} {o}": n_min(T[(T.profession == p) & (T.origine == o)].set_index("cls")) for p in PROFS for o in ORIGINS}
    res = {"couverture_par_classe": {f"{p}|{c}": {"couverture": round(float(r.couverture), 3), "communes": int(r.communes),
                                                 "passe": bool(r.passe)} for (p, c), r in w.iterrows() if r.communes},
           "couverture_2020": {f"{r.profession}|{r.cls}": round(float(r.couverture), 3)
                               for r in C[C.origine == 2020].itertuples() if r.communes},
           "N_min": {k: (None if np.isinf(v) else v) for k, v in nm.items()}}
    (OUT / "com_k2_verdicts.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(w.round(3).to_string())


if __name__ == "__main__":
    main()
