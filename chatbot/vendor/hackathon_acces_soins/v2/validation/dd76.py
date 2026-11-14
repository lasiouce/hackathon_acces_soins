"""Axe 3, N2 (SHA-256 bc5df3083cc5…) partie A et N7-D (06ba47b91647…) : reproduction DREES à 2050, réconciliation.

  A    DD76 tendanciel (CD, SF, PH) : tous modes (sante.model.stock_table), origine 2020, taux nationaux et entrées
       moyens 2016–2020, en ratios N(t)/N(2020). Tolérance ±2 % (2030), ±3 % (2040, 2050) ; forme PH et SF.
  D1   ER 1319 tendanciel, infirmiers « libéraux » (data.drees drees_projections_infirmieres_2024, sexe Ensemble) :
       infirmiers libéraux RPPS, origine 2021, taux et entrées moyens 2017–2021, ratios N(t)/N(2021).
  D2   Réconciliation des dentistes à 2050 : 3 facteurs (périmètre, origine et fenêtre, niveau des entrées),
       valeurs de Shapley sur les 8 configurations.
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.dd76 -> v2/validation/out/dd76_*.json
"""
import json
from itertools import permutations, product
from math import factorial
from pathlib import Path

import numpy as np
import pandas as pd

from sante.model import fit_rates, project, stock_table

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "out"
DD76 = {"dentistes": {2020: 41800, 2030: 45900, 2040: 53900, 2050: 61800},
        "pharmaciens": {2020: 72600, 2040: 76600, 2050: 81100},
        "sages-femmes": {2020: 23000, 2030: 26200, 2040: 28600, 2050: 29300}}
TOL = {2030: 2.0, 2040: 3.0, 2050: 3.0}


def nat_path(t, origin, fit, until=2050, shrink=None, recent=None):
    r = fit_rates(t[t.year <= origin], fit, shrink=shrink, inflow_recent=recent)
    p = project(t, origin, until - origin, r)
    s = p.groupby("year").n.sum()
    s.loc[origin] = t[t.year == origin].n.sum()
    return s.sort_index()


def part_a():
    t = stock_table(list(DD76))
    out = {}
    for prof, tgt in DD76.items():
        s = nat_path(t[t.profession == prof], 2020, (2016, 2020))
        g = s / s[2020]
        row = {"N2020_nous": float(s[2020]), "N2050_nous": float(s[2050])}
        for y, v in tgt.items():
            if y == 2020:
                continue
            ecart = 100 * (g[y] / (v / tgt[2020]) - 1)
            row[str(y)] = {"ratio_nous": float(g[y]), "ratio_dd76": v / tgt[2020], "ecart_%": float(ecart),
                           "passe": bool(abs(ecart) <= TOL[y])}
        if prof == "pharmaciens":
            yy = s.loc[2024:2030]
            row["forme_creux"] = {"min_annee": int(yy.idxmin()), "min_ratio": float(yy.min() / s[2020]),
                                  "passe": bool(yy.min() < s[2020])}
        if prof == "sages-femmes":
            d1, d2 = s[2040] - s[2030], s[2050] - s[2040]
            row["forme_plateau"] = {"croiss_2030_2040": float(d1), "croiss_2040_2050": float(d2),
                                    "passe": bool(d2 < d1 / 3)}
        row["passe"] = all(v["passe"] for k, v in row.items() if isinstance(v, dict))
        out[prof] = row
    return out


def part_d1():
    d = pd.read_csv(ROOT / "v2/validation/raw/er1319/proj.csv", sep=";")
    x = d[d.scenario.str.startswith("1-") & (d.tranche_d_age == "00-Ensemble") & (d.sexe == "0-Ensemble")
          & (d.mode_d_exercice == "4-Libéral")].set_index("annee").nombre_d_infirmieres_en_emploi
    s0 = pd.read_parquet(ROOT / "data/processed/stock.parquet")
    s0 = s0[(s0.profession == "infirmiers-liberaux") & ~s0.dep.isin(["999", "20"])]
    t = s0.groupby(["profession", "dep", "sex", "age_lo", "year"], as_index=False).n.sum()
    s = nat_path(t, 2021, (2017, 2021))
    out = {"N2021_nous": float(s[2021]), "N2021_er1319": int(x[2021])}
    for y in (2030, 2040, 2050):
        ecart = 100 * ((s[y] / s[2021]) / (x[y] / x[2021]) - 1)
        out[str(y)] = {"ratio_nous": float(s[y] / s[2021]), "ratio_er1319": float(x[y] / x[2021]),
                       "ecart_%": float(ecart), "passe": bool(abs(ecart) <= TOL[y])}
    out["passe"] = all(v["passe"] for k, v in out.items() if isinstance(v, dict))
    out["observe_2022_2023"] = {str(y): float(t[t.year == y].n.sum()) for y in (2022, 2023)}
    out["er1319_2022_2023"] = {str(y): int(x[y]) for y in (2022, 2023)}
    return out


def part_d2():
    from methodes.perimetres import prive
    tous = stock_table(["dentistes"])
    pr = prive()
    pr = pr[pr.profession == "dentistes"]
    F = {"perimetre": (tous, pr), "origine": ((2020, (2016, 2020)), (2026, (2012, 2026))), "entrees": (None, 2)}
    names = list(F)
    val = {}
    for bits in product((0, 1), repeat=3):
        t = F["perimetre"][bits[0]]
        o, fit = F["origine"][bits[1]]
        val[bits] = float(nat_path(t, o, fit, shrink=200, recent=F["entrees"][bits[2]])[2050])
    base, top = val[(0, 0, 0)], val[(1, 1, 1)]
    phi = dict.fromkeys(names, 0.0)
    for order in permutations(range(3)):
        b = [0, 0, 0]
        for i in order:
            before = val[tuple(b)]
            b[i] = 1
            phi[names[i]] += (val[tuple(b)] - before) / factorial(3)
    gap = top - DD76["dentistes"][2050]
    res = {"configs": {"".join(map(str, k)): v for k, v in val.items()},
           "N2050_cible_nous_prive_2026_entrees_recentes": top,
           "N2050_defaut_prive_2026_entrees_moyennes": val[(1, 1, 0)],
           "N2050_base_tous_modes_2020": base, "DD76_2050": DD76["dentistes"][2050], "ecart_total": gap,
           "shapley": phi, "residu_reproduction": base - DD76["dentistes"][2050],
           "part_residu_%": 100 * (base - DD76["dentistes"][2050]) / gap}
    res["passe"] = abs(res["part_residu_%"]) <= 25
    # observé : entrées nettes des jeunes tranches, pour lire le saut 2025–2026 (descriptif)
    y = pr[pr.age_lo < 35].groupby("year").n.sum()
    res["prive_moins_35_par_annee"] = {int(k): float(v) for k, v in y.loc[2018:2026].items()}
    return res


def main():
    OUT.mkdir(exist_ok=True)
    res = {"A_DD76": part_a(), "D1_ER1319": part_d1(), "D2_dentistes": part_d2()}
    (OUT / "dd76_results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
