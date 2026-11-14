"""Dépôt de prévisions (protocole N1) : origine = dernière année observée → 2027, 2028, 2030, par profession × dép.
Variantes : A0 (jumeau_taux_locaux) et C1 (axe2_cohortes_c1 : moyenne a posteriori + quantiles 10/50/90 de 200 tirages).
Périmètre privé. Écrit v2/validation/depot/<variante>_2026-11-14.parquet ; l'empreinte va dans decisions.md.
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.depot"""
import hashlib
from pathlib import Path

import pandas as pd

from methodes.perimetres import prive
from validation import registry

OUT = Path("v2/validation/depot")
TARGETS = (2027, 2028, 2030)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t = prive()
    for name in ("jumeau_taux_locaux", "axe2_cohortes_c1"):
        rows = []
        for p in t.profession.unique():
            tp = t[t.profession == p]
            o = int(tp.year.max())
            est = registry.get(name)().fit(tp, (2017 if p == "kines" else 2012, o), o)
            for y in TARGETS:
                r = est.predict(y).rename("pred").reset_index().assign(origine=o, cible=y)
                if hasattr(est, "sample"):
                    q = est.sample(y).quantile([.1, .5, .9], axis=1).T
                    q.columns = ["q10", "q50", "q90"]
                    r = r.merge(q.reset_index().rename(columns={"territory": "dep"}), on=["profession", "dep"])
                rows.append(r)
        d = pd.concat(rows, ignore_index=True).assign(variante=name, perimetre="privé central")
        f = OUT / f"{name}_2026-11-14.parquet"
        d.to_parquet(f, index=False)
        print(f, len(d), hashlib.sha256(f.read_bytes()).hexdigest()[:12],
              d.groupby(["profession", "cible"]).pred.sum().unstack().round(0).to_dict())


if __name__ == "__main__":
    main()
