"""Axe 3, N4 (SHA-256 91f897cc5071…) : erreur de projection communale à 5 ans par classe de taille, N_min.

Données (protocole) : data/processed/stock_commune.parquet (CartoSanté, IDE, MK, CD). Origines 2014, 2016, 2018,
2020 ; h = 5 (rapporté aussi h = 1, 3). Ajustement : 6 années jusqu'à l'origine.
Estimateurs : persistance ; tendance linéaire communale (plancher 0) ; DÉFAUT = total départemental de la cible
(oracle, la projection N1 n'étant pas figée) × part communale à l'origine.
Exclusion : communes dont l'effectif saute de plus de 3 écarts de Poisson (3·√max(n,1)) d'une année sur l'autre
entre origine − 5 et la cible (fusions) ; comptées.
N_min : plus petite classe dont elle-même et toutes les classes au-dessus ont P80 |erreur| ≤ 25 %, pour les trois
professions, dans ≥ 3 origines sur 4. Bande P10–P90 par classe calibrée sur 2014–2018, testée sur 2020 (75–85 %).
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.fine_scale_run -> v2/validation/out/fine_*
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from validation.fine_scale import BINS, LABELS, P80_MAX, n_min, share_out, size_errors

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"
ORIGINS, H_MAIN = (2014, 2016, 2018, 2020), 5


def wide(prof):
    s = pd.read_parquet(ROOT / "data/processed/stock_commune.parquet", filters=[("profession", "==", prof)])
    w = s.groupby(["com", "year"]).n.sum().unstack("year").fillna(0)
    dep = s.groupby("com").dep.first()
    return w, dep


def preds(w, dep, o, h):
    n0, tgt = w[o], w[o + h]
    yrs = list(range(o - 5, o + 1))
    X = np.array(yrs, float)
    Y = w[yrs].to_numpy()
    sl = ((X - X.mean()) * (Y - Y.mean(1, keepdims=True))).sum(1) / ((X - X.mean()) ** 2).sum()
    trend = pd.Series(np.maximum(Y.mean(1) + sl * (o + h - X.mean()), 0), index=w.index)
    dep_tot = tgt.groupby(dep).sum()
    default = share_out(dep_tot, n0, dep.reindex(w.index))
    span = w[list(range(o - 5, o + h + 1))].to_numpy()
    jump = (np.abs(np.diff(span, axis=1)) > 3 * np.sqrt(np.maximum(span[:, :-1], 1))).any(1)
    return {"persistance": n0, "tendance": trend, "defaut_oracle": default}, tgt, n0, pd.Series(jump, index=w.index)


def main():
    OUT.mkdir(exist_ok=True)
    rows, excl, rel = [], [], []
    for prof in ("infirmiers-liberaux", "kines", "dentistes"):
        w, dep = wide(prof)
        for o in ORIGINS:
            for h in (1, 3, 5):
                if o + h not in w.columns or o - 5 not in w.columns:
                    continue
                P, tgt, n0, jump = preds(w, dep, o, h)
                keep = ~jump
                excl.append({"profession": prof, "origine": o, "h": h, "exclues": int(jump.sum()),
                             "communes": int((n0 >= 1).sum())})
                for name, p in P.items():
                    tab = size_errors(p[keep], tgt[keep], n0[keep])
                    rows.append(tab.reset_index().assign(profession=prof, origine=o, h=h, estimateur=name))
                if h == H_MAIN:
                    d = pd.DataFrame({"pred": P["defaut_oracle"], "actual": tgt, "n0": n0})[keep]
                    d = d[(d.n0 >= 1) & (d.actual > 0)]
                    d["cls"] = pd.cut(d.n0, BINS, right=False, labels=LABELS)
                    d["r"] = d.actual / d.pred.where(d.pred > 0)
                    rel.append(d.assign(profession=prof, origine=o))
                    # communes à 0 à l'origine : erreur absolue moyenne en effectif
                    z = (n0 == 0) & keep
                    excl[-1]["zero_origine_erreur_abs_moy"] = float((P["defaut_oracle"][z] - tgt[z]).abs().mean())
    T = pd.concat(rows, ignore_index=True)
    T.to_csv(OUT / "fine_tables.csv", index=False)
    pd.DataFrame(excl).to_csv(OUT / "fine_exclusions.csv", index=False)
    m = T[(T.h == H_MAIN) & (T.estimateur == "defaut_oracle")]
    # N_min par (profession, origine), puis règle : 3 professions, ≥ 3 origines sur 4
    nm = {}
    for (p, o), g in m.groupby(["profession", "origine"]):
        nm[(p, o)] = n_min(g.set_index("cls"))
    cand = sorted(set(BINS[:-1]))
    rule = None
    for b in cand:
        ok = all(sum(nm[(p, o)] <= b for o in ORIGINS if (p, o) in nm) >= 3
                 for p in ("infirmiers-liberaux", "kines", "dentistes"))
        if ok:
            rule = b
            break
    # bande P10–P90 de r = réel/prédit par classe, sur 2014–2018 ; couverture sur 2020
    R = pd.concat(rel, ignore_index=True).dropna(subset=["r"])
    cal = R[R.origine < 2020].groupby(["profession", "cls"], observed=True).r.quantile([0.1, 0.9]).unstack()
    test = R[R.origine == 2020].join(cal, on=["profession", "cls"])
    test["in"] = (test.r >= test[0.1]) & (test.r <= test[0.9])
    cov = test.groupby(["profession", "cls"], observed=True)["in"].agg(["mean", "size"]).reset_index()
    cov["passe"] = cov["mean"].between(0.75, 0.85)
    cov.to_csv(OUT / "fine_couverture.csv", index=False)
    piv = m.pivot_table(index="cls", columns=["profession", "origine"], values="P80_abs_%", observed=False).round(1)
    res = {"N_min_par_profession_origine": {f"{p} {o}": (None if np.isinf(v) else v) for (p, o), v in nm.items()},
           "N_min_regle": rule, "P80_max": P80_MAX,
           "couverture_2020_classes_ge_3": cov[cov.cls != "1–2"][["profession", "cls", "mean", "size", "passe"]]
           .astype({"cls": str}).to_dict("records")}
    (OUT / "fine_results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float))
    print(piv.to_string())
    ref = T[(T.h == H_MAIN)].pivot_table(index="cls", columns="estimateur", values="P80_abs_%", observed=False).round(1)
    print(ref.to_string())
    print(json.dumps(res, indent=1, ensure_ascii=False, default=float)[:3000])
    print(pd.DataFrame(excl).groupby("profession")[["exclues", "communes"]].sum())


if __name__ == "__main__":
    main()
