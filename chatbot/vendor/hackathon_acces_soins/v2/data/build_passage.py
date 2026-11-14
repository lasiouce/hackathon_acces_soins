"""Axe 4 — tables de passage commune → EPCI → bassin de vie → département → région (COG 2026), et petits effectifs.

Run : uv run python v2/data/build_passage.py   (après build_commune, build_annuaire, build_pharmaciens ; ≈ 10 s)

1. passage_commune.parquet : tout code commune rencontré (ancien, actuel, arrondissement) → géocode du jumeau
   (commune COG 2026, ou arrondissement pour Paris / Lyon / Marseille) → commune parente → EPCI (geo.api, 2026)
   → bassin de vie 2022 (Insee, géographie 2026) → département → région. Les anciens codes sont ramenés au COG
   2026 par le fichier Insee des événements depuis 1943 (fusions, communes nouvelles, changements de code),
   appliqué transitivement (même fonction que build_finess_histo.py).
2. petits_effectifs.parquet : effectif par unité (commune, EPCI, bassin de vie, département) et profession,
   pour trois mesures : privés Annuaire (nov. 2026, 5 professions), libéraux CartoSanté 2025 (IDE, MK, CD),
   pharmaciens reconstitués 2026 (build_pharmaciens). Résumé par classes 0 / 1–4 / 5–29 / 30–99 / ≥ 100 :
   petits_effectifs_classes.csv (pour l'axe 3, N4).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_finess_histo import cog2026  # noqa: E402

OUT = ROOT / "v2" / "data" / "processed"
PLM = {"75056", "13055", "69123"}


def passage() -> pd.DataFrame:
    geo = pd.read_parquet(OUT / "commune_geo.parquet")
    remap = cog2026()
    cur = geo[~geo["com"].isin(PLM)].copy()          # géocodes du jumeau (arrondissements pour PLM)
    cur["code_source"] = cur["com"]
    cur["type"] = np.where(cur["com"] != cur["parent"], "arrondissement", "commune 2026")
    old = pd.DataFrame({"code_source": list(remap), "com": [remap[c] for c in remap]})
    old = old[~old["code_source"].isin(cur["com"]) & old["com"].isin(geo["com"])]
    old = old.merge(geo, on="com", how="left").assign(type="ancien code (fusion ou changement)")
    plm = geo[geo["com"].isin(PLM)].assign(code_source=lambda x: x["com"], type="commune PLM (agrégat)")
    p = pd.concat([cur, old, plm], ignore_index=True)
    cols = ["code_source", "type", "com", "parent", "epci", "bv2022", "bv2022_lib", "dep", "reg"]
    return p[cols].rename(columns={"com": "geocode"})


def classes(per: pd.Series) -> dict:
    b = pd.cut(per, [-0.1, 0.5, 4.999, 29.999, 99.999, np.inf], labels=["0", "1–4", "5–29", "30–99", "≥100"])
    return b.value_counts().reindex(["0", "1–4", "5–29", "30–99", "≥100"]).to_dict()


def main():
    p = passage()
    p.to_parquet(OUT / "passage_commune.parquet", index=False)
    print(p["type"].value_counts().to_dict())
    print("sans EPCI :", int(p["epci"].isna().sum()), "; sans BV :", int(p["bv2022"].isna().sum()))

    units = p[p["type"].isin(["commune 2026", "arrondissement"])].set_index("geocode")
    fr = units[units["dep"].str.len().eq(2) | units["dep"].isin(["971", "972", "973", "974", "976"])]
    to_geo = p.set_index("code_source")["geocode"]
    m = []
    a = pd.read_parquet(OUT / "annuaire_commune.parquet")
    a = a[(a["statut"] == "prive") & (a["com"] != "")]
    m.append(a.groupby(["profession", "com"])["personnes"].sum().rename("n").reset_index()
             .assign(mesure="privés Annuaire 2026-11-13"))
    s = pd.read_parquet(OUT / "commune_stock.parquet")
    s = s[s["year"] == 2025]
    m.append(s.groupby(["profession", "com"])["n"].sum().reset_index().assign(mesure="libéraux CartoSanté 2025"))
    ph = pd.read_parquet(OUT / "pharmaciens_commune_annee.parquet")
    ph = ph[ph["year"] == 2026]
    m.append(ph.groupby("com")["n_prive_central"].sum().rename("n").reset_index()
             .assign(profession="pharmaciens", mesure="pharmaciens reconstitués 2026 (privé, centrale)"))
    m = pd.concat(m, ignore_index=True)
    m["geocode"] = m["com"].map(to_geo).fillna(m["com"])
    rows, summ = [], []
    for (mes, prof), g in m.groupby(["mesure", "profession"]):
        for lvl in ["com", "epci", "bv2022", "dep"]:
            key = g["geocode"] if lvl == "com" else g["geocode"].map(units[lvl])
            per = g.groupby(key)["n"].sum()
            allu = fr.index if lvl == "com" else fr[lvl].dropna().unique()
            per = per.reindex(pd.Index(allu), fill_value=0.0)
            rows.append(per.rename("n").rename_axis("unite").reset_index()
                        .assign(niveau=lvl, profession=prof, mesure=mes))
            summ.append({"mesure": mes, "profession": prof, "niveau": lvl, "unites": len(per), **classes(per),
                         "mediane": per.median(), "p90": per.quantile(0.9),
                         "part_pros_unites_lt30": per[per < 30].sum() / per.sum()})
    pd.concat(rows, ignore_index=True).to_parquet(OUT / "petits_effectifs.parquet", index=False)
    summ = pd.DataFrame(summ)
    summ.to_csv(OUT / "petits_effectifs_classes.csv", index=False)
    print(summ[summ["niveau"].isin(["com", "epci"])].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
