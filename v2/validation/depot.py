"""Axe 3, N1 (dépôt, SHA-256 eb527ecb06a0…) et N8 (97ef367fd221…) : prévisions déposées avant le RPPS 2027.

Variante par défaut (registre « jumeau_taux_locaux »), périmètre privé, origine 2026, fenêtre complète ;
cibles 2027, 2028, 2030 par profession × département ; bande √h de N8 : log N ~ N(log prédit, s²·h), s² = moyenne
de e²/h′ sur toutes les erreurs passées du banc (o′ ≥ 2016, o′ + h′ ≤ 2026). Quantiles 10, 25, 50, 75, 90 %.
Infirmiers libéraux exclus (série RPPS arrêtée en 2023 dans nos données).
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.depot
-> v2/validation/depot/jumeau_taux_locaux_2026-11-14.parquet (+ .sha256)
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from validation import registry

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "depot"
ORIGIN, TARGETS, Q = 2026, (2027, 2028, 2030), (0.10, 0.25, 0.50, 0.75, 0.90)


def main():
    from methodes.perimetres import prive
    t = prive()
    e = pd.read_parquet(ROOT / "v2/methodes/out/erreurs_prive.parquet")
    e = e[(e.model == "jumeau_taux_locaux") & (e.actual > 0) & (e.pred > 0) & (e.origin + e.h <= ORIGIN)]
    e = e.assign(lerr=np.log(e.actual / e.pred))
    rows = []
    for p in sorted(t.profession.unique()):
        tp = t[t.profession == p]
        if tp.year.max() < ORIGIN:
            continue
        first = 2017 if p == "kines" else int(tp.year.min())
        est = registry.get("jumeau_taux_locaux")().fit(tp, (first, ORIGIN), ORIGIN)
        ep = e[e.profession == p]
        s = float(np.sqrt((ep.lerr ** 2 / ep.h).mean()))
        for y in TARGETS:
            pr = est.predict(y)
            h = y - ORIGIN
            d = pr.reset_index().rename(columns={"n": "pred", 0: "pred"})
            d = d.rename(columns={d.columns[-1]: "pred"}).assign(cible=y, h=h, s=s, n_erreurs=len(ep))
            for q in Q:
                d[f"q{int(q * 100)}"] = d.pred * np.exp(norm.ppf(q) * s * np.sqrt(h))
            rows.append(d)
    out = pd.concat(rows, ignore_index=True).assign(origine=ORIGIN, perimetre="prive", variante="jumeau_taux_locaux")
    OUT.mkdir(exist_ok=True)
    f = OUT / "jumeau_taux_locaux_2026-11-14.parquet"
    out.to_parquet(f, index=False)
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    (OUT / (f.name + ".sha256")).write_text(h + "  " + f.name + "\n")
    print(out.groupby(["profession", "cible"])[["pred", "q10", "q90"]].sum().round(0).to_string())
    print("SHA-256", h)


if __name__ == "__main__":
    main()
