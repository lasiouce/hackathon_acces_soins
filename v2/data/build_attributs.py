"""Axe 4 — attributs des communes pour le logit d'installation : une table commune × année (2012–2025), sourcée.

Run : uv run python v2/data/build_attributs.py   (après build_commune, build_zonage, build_finess_histo, build_flux ; ≈ 1 min)

Clé : géocode COG 2026 (communes ; Paris, Lyon et Marseille par arrondissement), comme zonage_commune et
annuaire_commune. Colonnes et sources :
  population       Insee, séries historiques 1876–2023 (population municipale, géographie 2025) ; 2024–2025 =
                   2023 reportée (pop_source = 'report') ; arrondissements PLM : RP 2012 / 2017 / 2023 interpolé.
  part_0_14, part_65p, part_80p
                   Insee RP 2012, 2017, 2023 (« évolution et structure de la population », géographie 2026),
                   interpolation linéaire entre recensements, report hors bornes.
  dens7            Insee grille communale de densité à 7 niveaux, millésimes 2015–2024 (2012–2014 = 2015,
                   2025 = 2024) ; 1 = grands centres urbains … 7 = rural à habitat très dispersé.
  aav_cat          Insee aires d'attraction des villes 2020 (géographie 2026) : 11 commune-centre, 12 autre
                   commune du pôle principal, 13 pôle secondaire, 20 couronne, 30 hors attraction.
  dist_pole_km     distance à vol d'oiseau entre le centre de la commune (geo.api) et le centre de la commune-centre
                   d'AAV (cat. 11) la plus proche ; dérivé.
  n_officines, n_maisons_sante, n_centres_sante
                   FINESS historique (état au 31/12) ; catégories 620, 603, 124 (603 dès 2012, 124 dès 2014).
  z_<prof>_actuel, z_<prof>_2012
                   zonage conventionnel (statut) : CartoSanté actuel, Atlasanté génération 2012 (build_zonage).
  lib_<prof>, inet_<prof>
                   libéraux de la commune au 31/12 et proxy d'installations nettes (build_commune, build_flux).
Sortie : v2/data/processed/commune_attributs.parquet ; contrôles : commune_attributs_checks.csv
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "v2" / "data" / "raw" / "insee"
OUT = ROOT / "v2" / "data" / "processed"
YEARS = list(range(2012, 2026))
PLM = {"132": "13055", "751": "75056", "693": "69123"}


def xl(name: str, sheet: str, skip: int) -> pd.DataFrame:
    return pd.read_excel(RAW / name, sheet_name=sheet, skiprows=skip, engine="calamine", dtype={"CODGEO": str})


def census_age() -> pd.DataFrame:
    rows = []
    for y in (2012, 2017, 2023):
        for kind in ("COM", "ARM"):
            d = pd.read_excel(RAW / "base_cc_evol_struct_pop_2023.xlsx", sheet_name=f"{kind}_{y}", header=None,
                              engine="calamine")
            lab = [str(v) for v in d.iloc[0]]
            d = d.iloc[1:]
            d.columns = lab
            col = lambda s: next(c for c in lab if c.startswith(s))  # noqa: E731
            pop = pd.to_numeric(d[col("Population (princ)")], errors="coerce")
            p65 = pd.to_numeric(d[col("Pop 65-79 ans (princ)")], errors="coerce") + \
                pd.to_numeric(d[col("Pop 80 ans ou plus (princ)")], errors="coerce")
            rows.append(pd.DataFrame({
                "com": d[lab[0]].astype(str), "year": y, "pop_rp": pop,
                "part_0_14": pd.to_numeric(d[col("Pop 0-14 ans (princ)")], errors="coerce") / pop,
                "part_65p": p65 / pop,
                "part_80p": pd.to_numeric(d[col("Pop 80 ans ou plus (princ)")], errors="coerce") / pop}))
    return pd.concat(rows, ignore_index=True)


def interp(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Interpole linéairement par commune sur YEARS, report hors bornes."""
    out = []
    for c in cols:
        w = df.pivot_table(index="com", columns="year", values=c)
        w = w.reindex(columns=sorted(set(w.columns) | set(YEARS))).interpolate(axis=1, limit_direction="both")
        out.append(w[YEARS].stack().rename(c))
    return pd.concat(out, axis=1).reset_index().rename(columns={"level_1": "year"})


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def main():
    geo = pd.read_parquet(OUT / "commune_geo.parquet")
    geo = geo[~geo["com"].isin(PLM.values())]          # PLM : on garde les arrondissements
    base = geo[["com", "parent", "dep", "reg", "epci", "bv2022"]].merge(pd.DataFrame({"year": YEARS}), how="cross")

    # population annuelle
    ph = xl("base-pop-historiques-1876-2023.xlsx", "pop_1876_2023", 5)
    pcols = [c for c in ph.columns if str(c).startswith("PMUN") and int(str(c)[4:]) >= 2012]
    pop = ph.melt(id_vars="CODGEO", value_vars=pcols, var_name="y", value_name="population")
    pop["year"] = pop["y"].str[4:].astype(int)
    pop = pop.rename(columns={"CODGEO": "com"})[["com", "year", "population"]]
    last = pop[pop["year"] == 2023]
    carry = pd.concat([last.assign(year=y) for y in (2024, 2025)])
    pop = pd.concat([pop.assign(pop_source="Insee séries historiques"), carry.assign(pop_source="report 2023")])

    age = census_age()
    agei = interp(age, ["pop_rp", "part_0_14", "part_65p", "part_80p"])
    t = base.merge(pop, on=["com", "year"], how="left").merge(agei, on=["com", "year"], how="left")
    arm = t["population"].isna() & t["pop_rp"].notna()
    t.loc[arm, "population"] = t.loc[arm, "pop_rp"]
    t.loc[arm, "pop_source"] = "Insee RP interpolé"
    t = t.drop(columns="pop_rp")

    # densité
    dens = []
    for y in range(2015, 2025):
        d = xl(f"grille_densite_7_niveaux_{y}.xlsx", "Grille_Densite", 4)[["CODGEO", "DENS"]]
        dens.append(d.assign(year=y))
    dens = pd.concat(dens).rename(columns={"CODGEO": "com", "DENS": "dens7"})
    dens = pd.concat([dens] + [dens[dens["year"] == 2015].assign(year=y) for y in (2012, 2013, 2014)]
                     + [dens[dens["year"] == 2024].assign(year=2025)])
    t["dens_key"] = t["com"].where(~t["com"].str[:3].isin(PLM), t["parent"])
    t = t.merge(dens.rename(columns={"com": "dens_key"}), on=["dens_key", "year"], how="left")

    # AAV et distance au pôle
    aav = xl("AAV2020_au_01-01-2026.xlsx", "Composition_communale", 5)[["CODGEO", "AAV2020", "CATEAAV2020"]]
    aav = aav.rename(columns={"CODGEO": "dens_key", "AAV2020": "aav2020", "CATEAAV2020": "aav_cat"})
    t = t.merge(aav, on="dens_key", how="left")
    cen = pd.DataFrame(json.loads((RAW / "geoapi_communes_centre.json").read_text()))
    cen = pd.concat([cen, pd.DataFrame(json.loads((RAW / "geoapi_arm_centre.json").read_text()))])
    cen["lon"] = cen["centre"].map(lambda c: c["coordinates"][0] if isinstance(c, dict) else np.nan)
    cen["lat"] = cen["centre"].map(lambda c: c["coordinates"][1] if isinstance(c, dict) else np.nan)
    cen = cen.set_index("code")[["lon", "lat"]]
    poles = cen.loc[cen.index.intersection(aav.loc[aav["aav_cat"].astype(str) == "11", "dens_key"])]
    pts = cen.reindex(geo["com"])
    dmin = np.full(len(pts), np.inf)
    for lon, lat in poles.itertuples(index=False):
        dmin = np.minimum(dmin, haversine(pts["lon"].to_numpy(), pts["lat"].to_numpy(), lon, lat))
    dist = pd.Series(np.where(np.isfinite(dmin), dmin, np.nan), index=pts.index, name="dist_pole_km")
    t = t.merge(dist.rename_axis("com").reset_index(), on="com", how="left")

    # FINESS (officines, maisons de santé, centres de santé)
    f = pd.read_parquet(OUT / "finess_commune_annee.parquet")
    f = f.pivot_table(index=["com", "year"], columns="categorie", values="n", aggfunc="sum", fill_value=0)
    f = f.rename(columns={"officine": "n_officines", "maison_de_sante": "n_maisons_sante",
                          "centre_de_sante": "n_centres_sante"}).reset_index()
    t = t.merge(f, on=["com", "year"], how="left")
    for c in ["n_officines", "n_maisons_sante", "n_centres_sante"]:
        t[c] = t[c].fillna(0)

    # zonage
    z = pd.read_parquet(OUT / "zonage_commune.parquet")
    z["gen"] = np.where(z["millesime"].str.startswith("actuel"), "actuel", "2012")
    short = {"sages-femmes": "sf", "dentistes": "cd", "kines": "mk", "infirmiers": "ide"}
    z["col"] = "z_" + z["profession"].map(short) + "_" + z["gen"]
    zw = z.pivot_table(index="com", columns="col", values="statut", aggfunc="first").reset_index()
    t = t.merge(zw, on="com", how="left")

    # offre libérale et proxy d'installations
    s = pd.read_parquet(OUT / "commune_stock.parquet").groupby(["profession", "com", "year"])["n"].sum()
    sw = s.unstack("profession").rename(columns=lambda p: "lib_" + {"kines": "mk", "infirmiers": "ide",
                                                                      "dentistes": "cd"}[p]).reset_index()
    fl = pd.read_parquet(OUT / "flux_installations_commune.parquet").groupby(["profession", "com", "year"])["i_net"].sum()
    fw = fl.unstack("profession").rename(columns=lambda p: "inet_" + {"kines": "mk", "infirmiers": "ide",
                                                                        "dentistes": "cd"}[p]).reset_index()
    t = t.merge(sw, on=["com", "year"], how="left").merge(fw, on=["com", "year"], how="left")
    for c in [c for c in t.columns if c.startswith(("lib_", "inet_"))]:
        t[c] = t[c].fillna(0.0)                       # CartoSanté ne publie que les communes non vides
    t = t.drop(columns="dens_key")
    t.to_parquet(OUT / "commune_attributs.parquet", index=False)

    # contrôles : couverture par colonne et par année ; population totale
    cov = t.groupby("year").agg(**{c: (c, lambda s: s.notna().mean()) for c in
                                   ["population", "part_65p", "dens7", "aav_cat", "dist_pole_km", "z_mk_actuel"]})
    cov["population_totale"] = t.groupby("year")["population"].sum()
    fin_nat = pd.read_parquet(OUT / "finess_commune_annee.parquet")
    fin_nat = fin_nat[fin_nat["categorie"] == "officine"].groupby("year")["n"].sum()
    cov["officines_couvertes"] = t.groupby("year")["n_officines"].sum() / fin_nat
    for p in ["mk", "ide", "cd"]:
        cov[f"lib_{p}_total"] = t.groupby("year")[f"lib_{p}"].sum()
    cov.to_csv(OUT / "commune_attributs_checks.csv")
    print(t.shape)
    print(cov.round(4).to_string())
    print(t[t["com"] == "63113"][["year", "population", "part_65p", "dens7", "aav_cat", "dist_pole_km", "n_officines",
                                  "n_maisons_sante", "lib_mk", "inet_mk", "z_mk_actuel"]].tail(4).to_string(index=False))


if __name__ == "__main__":
    main()
