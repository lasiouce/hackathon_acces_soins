"""Axe 4 — grain communal : stock libéral par commune (CartoSanté + Marseille), géographie, contrôles, petits effectifs.

Run : uv run python v2/data/build_commune.py   (depuis la racine, après build_secteur.py et build_annuaire.py ; ≈ 1 min)

1. Stock libéral par commune × tranche d'âge (CartoSanté, FNPS/SNDS, actifs au 31/12) : on part de la table v1
   `data/processed/stock_commune.parquet` (IDE, MK, CD ; Marseille absente) et on ajoute Marseille par ses
   16 arrondissements (référentiel arm2026). Leurs séries vont de 2010 à 2025, dans l'ordre croissant : la somme
   des arrondissements reproduit l'écart du dép. 13 à l'unité près pour les infirmiers (contrôlé ici). Un
   arrondissement à série partielle (13203 kinés, 13216 dentistes) reçoit le reste « dép. 13 − autres communes »,
   en total seulement. Avant 2010, Marseille n'existe qu'en total (commune 13055 = reste du dép. 13).
2. Géographie : commune ou arrondissement → commune parente, EPCI (geo.api.gouv.fr), bassin de vie 2022 (Insee,
   au 01/01/2026), département, région, population légale.
3. Contrôles : Σ communes par dép. × année contre le RPPS DREES (libéral + mixte, kinés et dentistes) et le SNDS
   (infirmiers libéraux) ; Annuaire Santé (privé, nov. 2026) par dép. contre la centrale DREES 2026.
4. Petits effectifs : distribution des effectifs privés par unité (commune, bassin de vie, EPCI, département) et
   bruit observé d'une année sur l'autre selon la taille.

Sorties (v2/data/processed/) : commune_stock.parquet, commune_geo.parquet, commune_checks.csv,
annuaire_checks_dep.csv, grain_petits_effectifs.csv, grain_bruit.csv
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "v2"))   # paquet sante (ex-v1)
from sante.cartosante import axes, get_data  # noqa: E402  (v1, lecture seule ; lit le cache data/raw/cartosante)

RAW = ROOT / "v2" / "data" / "raw"
OUT = ROOT / "v2" / "data" / "processed"
DS = {"kine_popage": "kines", "infi_popage": "infirmiers", "dent_popage": "dentistes"}
V1 = {"kines": "kines", "infirmiers": "infirmiers-liberaux", "dentistes": "dentistes"}
PLM = {"132": "13055", "751": "75056", "693": "69123"}


def marseille(ds: str, prof: str, sc: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    years, ages, titles = axes(ds)
    band = {c: t for c, t in titles.items()}
    tot_code = ages[0]
    dep = get_data("dep", ds)
    d13 = dep[(dep["code"] == "13") & (dep["age"] == tot_code)].set_index("year")["n"]
    others = sc[(sc["profession"] == V1[prof]) & (sc["dep"] == "13")].groupby("year")["n"].sum()
    gap = (d13 - others.reindex(d13.index, fill_value=0)).rename("gap")
    t = (RAW / "cartosante" / f"GetData_arm2026_{ds}.xml").read_text()
    a = pd.DataFrame(re.findall(r"<Row><K>(132\d\d)</K><V>([^<]*)</V></Row>", t), columns=["com", "n"])
    a["n"] = pd.to_numeric(a["n"], errors="coerce")
    a["i"] = a.groupby("com").cumcount()
    per = a.groupby("com").size()
    nb = len(ages)
    arr_years = list(range(2010, 2010 + 16))
    full = per[per == 16 * nb].index
    a = a[a["com"].isin(full)].copy()
    a["year"] = [arr_years[i // nb] for i in a["i"]]
    a["age"] = [ages[i % nb] for i in a["i"]]
    bands = a[a["age"] != tot_code].assign(age_band=lambda x: x["age"].map(band))
    sum_full = a[a["age"] == tot_code].groupby("year")["n"].sum()
    rows = [bands[["com", "year", "age_band", "n"]].assign(estime=False)]
    resid = (gap.reindex(arr_years) - sum_full).rename("n")
    for com in per.index.difference(full):
        rows.append(resid.reset_index().assign(com=com, age_band="Total (reste du dép. 13)", estime=True))
    pre = gap[gap.index < 2010].reset_index().assign(com="13055", age_band="Total (reste du dép. 13)", estime=True)
    rows.append(pre)
    m = pd.concat(rows, ignore_index=True)
    chk = pd.DataFrame({"gap_dep13": gap.reindex(arr_years), "somme_arr_complets": sum_full,
                        "arr_partiels": len(per) - len(full)}).assign(profession=prof)
    return m.assign(profession=prof), chk


def paris_lyon(ds: str, prof: str, sc: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Paris (751xx) et Lyon (6938x) : la table v1 les porte en commune (75056, 69123) ; on les remplace par leurs
    arrondissements (séries complètes, ordre croissant jusqu'en 2025). Les arrondissements à série partielle
    reçoivent le reste « commune − arrondissements complets », en total seulement."""
    years, ages, titles = axes(ds)
    tot_code, nb = ages[0], len(ages)
    t = (RAW / "cartosante" / f"GetData_arm2026_{ds}.xml").read_text()
    out, chk = [], []
    for prefix, parent in (("751", "75056"), ("6938", "69123")):
        a = pd.DataFrame(re.findall(rf"<Row><K>({prefix}\d+)</K><V>([^<]*)</V></Row>", t), columns=["com", "n"])
        a["n"] = pd.to_numeric(a["n"], errors="coerce")
        a["i"] = a.groupby("com").cumcount()
        per = a.groupby("com").size()
        ny = per.max() // nb
        arr_years = list(range(2026 - ny, 2026))
        full = per[per == ny * nb].index
        a = a[a["com"].isin(full)].copy()
        a["year"] = [arr_years[i // nb] for i in a["i"]]
        a["age"] = [ages[i % nb] for i in a["i"]]
        bands = a[a["age"] != tot_code].assign(age_band=lambda x: x["age"].map(titles))
        sum_full = a[a["age"] == tot_code].groupby("year")["n"].sum()
        target = sc[(sc["profession"] == V1[prof]) & (sc["com"] == parent)].groupby("year")["n"].sum()
        out.append(bands[["com", "year", "age_band", "n"]].assign(estime=False))
        resid = (target.reindex(arr_years) - sum_full).rename("n")
        partial = per.index.difference(full)
        for com in partial:
            out.append((resid / len(partial)).reset_index().assign(com=com, age_band=f"Total (reste de {parent})",
                                                                   estime=True))
        chk.append(pd.DataFrame({"commune": target.reindex(arr_years), "somme_arr_complets": sum_full,
                                 "arr_partiels": len(partial)}).assign(profession=prof, ville=parent))
    m = pd.concat(out, ignore_index=True)
    m["dep"] = m["com"].str[:2]
    return m.assign(profession=prof), pd.concat(chk)


def geography() -> pd.DataFrame:
    c = pd.DataFrame(json.loads((RAW / "insee" / "geoapi_communes.json").read_text()))
    arm = pd.DataFrame(json.loads((RAW / "insee" / "geoapi_arm.json").read_text()))
    bv = pd.read_excel(RAW / "insee" / "BV2022_au_01-01-2026.xlsx", sheet_name="Composition_communale",
                       skiprows=5, engine="calamine")[["CODGEO", "BV2022", "LIBBV2022"]]
    c = c.rename(columns={"code": "com", "codeEpci": "epci", "codeDepartement": "dep", "codeRegion": "reg"})
    arm = arm.rename(columns={"code": "com", "codeDepartement": "dep"})
    arm["parent"] = arm["com"].str[:3].map(PLM)
    c["parent"] = c["com"]
    g = pd.concat([c, arm], ignore_index=True)
    par = c.set_index("com")
    g["epci"] = g["epci"].fillna(g["parent"].map(par["epci"]))
    g["reg"] = g["reg"].fillna(g["parent"].map(par["reg"]))
    g = g.merge(bv.rename(columns={"CODGEO": "parent", "BV2022": "bv2022", "LIBBV2022": "bv2022_lib"}),
                on="parent", how="left")
    return g[["com", "nom", "parent", "dep", "reg", "epci", "bv2022", "bv2022_lib", "population"]]


def main():
    sc = pd.read_parquet(ROOT / "data" / "processed" / "stock_commune.parquet")
    parts, mchk = [], []
    for ds, prof in DS.items():
        m, c = marseille(ds, prof, sc)
        parts.append(m), mchk.append(c)
    pl, plchk = [], []
    for ds, prof in DS.items():
        m, c = paris_lyon(ds, prof, sc)
        pl.append(m), plchk.append(c)
    base = sc[~sc["com"].isin(["75056", "69123"])]
    base = base.assign(profession=base["profession"].map({v: k for k, v in V1.items()}), estime=False)
    mar = pd.concat(parts, ignore_index=True)
    mar["dep"] = "13"
    pl = pd.concat(pl, ignore_index=True)
    # années où Paris / Lyon existent en commune mais pas encore en arrondissements : on garde la ligne commune
    city = {"751": "75056", "693": "69123"}
    first_arr = pl.groupby(["profession", pl["com"].str[:3].map(city)])["year"].min()
    early = sc[sc["com"].isin(["75056", "69123"])].assign(
        profession=lambda x: x["profession"].map({v: k for k, v in V1.items()}), estime=False)
    early = early[early["year"] < [first_arr.get((p, c), 9999) for p, c in zip(early["profession"], early["com"])]]
    cols = ["profession", "year", "com", "dep", "age_band", "n", "estime"]
    stock = pd.concat([base[cols], mar[cols], pl[cols], early[cols]], ignore_index=True)
    plchk = pd.concat(plchk)
    d = (plchk["commune"] - plchk["somme_arr_complets"])
    print("Paris / Lyon : commune − Σ arrondissements complets (min, max)")
    print(d.groupby([plchk["profession"], plchk["ville"]]).agg(["min", "max"]))
    stock["source"] = "CartoSanté *_popage (FNPS/SNDS, actifs au 31/12), extraits 2026-11-13 et 2026-11-14"
    OUT.mkdir(parents=True, exist_ok=True)
    stock.to_parquet(OUT / "commune_stock.parquet", index=False)
    mchk = pd.concat(mchk)
    print("Marseille : écart dép. 13 − Σ arrondissements complets (max par profession)")
    print((mchk["gap_dep13"] - mchk["somme_arr_complets"]).groupby(mchk["profession"]).agg(["min", "max"]))

    geo = geography()
    geo.to_parquet(OUT / "commune_geo.parquet", index=False)

    # Contrôle 1 : Σ communes (CartoSanté, 31/12/Y) contre DREES (1er janvier Y+1, et Y)
    dr = pd.read_parquet(ROOT / "data" / "processed" / "stock.parquet")
    dr = dr[dr["mode3"] == "liberal_mixte"].replace({"profession": {"infirmiers-liberaux": "infirmiers"}})
    dr = dr.groupby(["profession", "dep", "year"])["n"].sum()
    cs = stock.groupby(["profession", "dep", "year"])["n"].sum()
    rows = []
    for lag in (0, 1):
        ref = dr.rename(index=lambda y: y - lag, level="year") if lag else dr
        j = pd.concat([cs.rename("communes"), ref.rename("drees")], axis=1, join="inner")
        j = j[j["drees"] > 0]
        nat = j.groupby(["profession", "year"]).sum()
        nat["ecart_pct"] = 100 * (nat["communes"] / nat["drees"] - 1)
        rows.append(nat.reset_index().assign(dep="FR", alignement="31/12/Y vs 1/1/Y+1" if lag else "même année Y"))
        j["ecart_pct"] = 100 * (j["communes"] / j["drees"] - 1)
        rows.append(j.reset_index().assign(alignement="31/12/Y vs 1/1/Y+1" if lag else "même année Y"))
    checks = pd.concat(rows, ignore_index=True)
    checks.to_csv(OUT / "commune_checks.csv", index=False)
    fr = checks[checks["dep"] == "FR"].pivot_table(index=["profession", "year"], columns="alignement",
                                                   values="ecart_pct")
    print(fr.round(1).groupby(level=0).tail(4).to_string())

    # Contrôle 2 : Annuaire (privé, nov. 2026) par dép. contre la centrale DREES 2026 (secteur_split)
    an = pd.read_parquet(OUT / "annuaire_commune.parquet")
    an = an[an["dep"] != ""].groupby(["profession", "dep"])["personnes"].sum().rename("annuaire_tous")
    anp = pd.read_parquet(OUT / "annuaire_commune.parquet")
    anp = anp[(anp["dep"] != "") & (anp["statut"] == "prive")].groupby(["profession", "dep"])["personnes"].sum()
    sp = pd.read_parquet(OUT / "secteur_split.parquet")
    sp = sp[(sp["mode3"] == "tous") & (sp["dep"] != "FR")]
    sp = sp[sp["year"] == sp.groupby("profession")["year"].transform("max")].groupby(["profession", "dep"])[
        ["n", "n_prive_central", "n_prive_sur"]].sum()
    sp["n_prive_max"] = sp["n_prive_sur"] + (sp["n"] - sp["n_prive_sur"])  # borne lâche, remplacée ci-dessous
    j = pd.concat([an, anp.rename("annuaire_prive"), sp], axis=1, join="inner")
    j["ecart_total_pct"] = 100 * (j["annuaire_tous"] / j["n"] - 1)
    j["ecart_prive_pct"] = 100 * (j["annuaire_prive"] / j["n_prive_central"] - 1)
    j.reset_index().to_csv(OUT / "annuaire_checks_dep.csv", index=False)
    print(j.groupby("profession")[["ecart_total_pct", "ecart_prive_pct"]].median().round(1))

    # Petits effectifs : effectifs privés (Annuaire nov. 2026) par unité
    a = pd.read_parquet(OUT / "annuaire_commune.parquet")
    a = a[(a["statut"] == "prive") & (a["com"] != "")]
    a = a.groupby(["profession", "com"])["personnes"].sum().reset_index()
    geo_fr = geo[geo["dep"].str.len().eq(2) | geo["dep"].isin(["971", "972", "973", "974", "976"])]
    units = geo.set_index("com")
    res = []
    for lvl in ["com", "bv2022", "epci", "dep"]:
        for prof, g in a.groupby("profession"):
            key = g["com"] if lvl == "com" else g["com"].map(units[lvl])
            per = g.groupby(key)["personnes"].sum()
            # unités : communes (Paris, Lyon, Marseille remplacées par leurs arrondissements) ou leurs regroupements
            allu = geo_fr.loc[~geo_fr["com"].isin(PLM.values()), lvl].dropna().unique()
            per = per.reindex(pd.Index(allu), fill_value=0)
            bins = pd.cut(per, [-0.1, 0.5, 4.999, 29.999, 99.999, np.inf], labels=["0", "1–4", "5–29", "30–99", "≥100"])
            r = bins.value_counts().reindex(["0", "1–4", "5–29", "30–99", "≥100"]).to_dict()
            share_lt30 = per[per < 30].sum() / per.sum()
            res.append({"niveau": lvl, "profession": prof, "unites": len(per), **{f"n_{k}": v for k, v in r.items()},
                        "mediane": per.median(), "part_pros_unites_lt30": share_lt30,
                        "bruit_poisson_median_pct": 100 / np.sqrt(per[per > 0].median())})
    small = pd.DataFrame(res)
    small.to_csv(OUT / "grain_petits_effectifs.csv", index=False)
    print(small.round(3).to_string(index=False))

    # Bruit observé : |log(N_2025 / N_2024)| par classe de taille, commune et bassin de vie (CartoSanté)
    st = stock[stock["year"].isin([2024, 2025])].copy()
    st["unit_com"] = st["com"]
    st["unit_bv"] = st["com"].map(units["bv2022"]).fillna(st["com"].map(lambda c: c))
    out = []
    for lvl in ["unit_com", "unit_bv"]:
        p = st.groupby(["profession", lvl, "year"])["n"].sum().unstack("year").dropna()
        p = p[(p[2024] > 0) & (p[2025] > 0)]
        p["cls"] = pd.cut(p[2024], [0, 4.999, 29.999, 99.999, np.inf], labels=["1–4", "5–29", "30–99", "≥100"])
        p["abs_dlog"] = np.abs(np.log(p[2025] / p[2024]))
        r = p.groupby(["profession", "cls"], observed=True)["abs_dlog"].agg(["median", "size"]).reset_index()
        out.append(r.assign(niveau=lvl.replace("unit_", "")))
    noise = pd.concat(out, ignore_index=True)
    noise.to_csv(OUT / "grain_bruit.csv", index=False)
    print(noise.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
