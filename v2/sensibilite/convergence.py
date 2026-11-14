"""Convergence des indices de Sobol : ST et largeur de l'IC bootstrap en fonction de N, sur les sorties brutes.

Pour chaque plan sauvé (out/Y_<prof>_<famille>.npz, partie 1 ; out/L_<prof>.npz, partie 2), on recalcule les
indices sur les N premières lignes (N = 128, 256, 512, …), avec 300 tirages bootstrap. Critère retenu
(décision axe 5) : N suffit si, pour chaque facteur de ST ≥ 0,05 à 2050, l'IC 95 % est plus étroit que ST
et l'écart de ST à la valeur à N max est < 0,05.
Run (racine) : PYTHONPATH=v2:. uv run python -m sensibilite.convergence -> out/convergence.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

from sensibilite.facteurs import SEED
from sensibilite.leviers import indices

OUT = Path("v2/sensibilite/out")


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for f in sorted(OUT.glob("Y_*.npz")) + sorted(OUT.glob("L_*.npz")):
        z = np.load(f, allow_pickle=True)
        Y, names = z["Y"], list(z["names"])
        k = len(names)
        ng = Y.shape[1] - 2 - k
        labels = names + [f"[groupe {g}]" for g in range(ng)]
        nmax = Y.shape[0]
        Ns = [n for n in (128, 256, 512, 1024, 2048) if n <= nmax]
        for n in Ns:
            y = Y[:n, :, -1]                                     # 2050
            _, ST = indices(y, k, ng)
            bt = []
            for _ in range(300):
                i = rng.integers(0, n, n)
                bt.append(indices(y[i], k, ng)[1])
            lo, hi = np.percentile(bt, [2.5, 97.5], axis=0)
            for j, nm in enumerate(labels):
                rows.append(dict(plan=f.stem, N=n, facteur=nm, ST=ST[j], ic_largeur=hi[j] - lo[j]))
    d = pd.DataFrame(rows)
    fin = d[d.N == d.groupby("plan").N.transform("max")][["plan", "facteur", "ST"]].rename(columns={"ST": "ST_Nmax"})
    d = d.merge(fin)
    d["ecart_a_Nmax"] = (d.ST - d.ST_Nmax).abs()
    d.to_csv(OUT / "convergence.csv", index=False)
    big = d[d.ST_Nmax >= 0.05]
    s = big.groupby(["plan", "N"]).agg(ic_max=("ic_largeur", "max"), ecart_max=("ecart_a_Nmax", "max"),
                                       ic_plus_large_que_ST=("ic_largeur", lambda x: int((x > big.loc[x.index, "ST"]).sum())))
    print(s.round(3).to_string())


if __name__ == "__main__":
    main()
