"""Axe 4 — pharmaciens par commune et par an (2012–2026), reconstitués.

Run : uv run python v2/data/build_pharmaciens.py   (après build_secteur.py et build_finess_histo.py ; ≈ 30 s)

Aucune source ouverte ne donne les pharmaciens par commune avant l'instantané de l'Annuaire Santé (nov. 2026).
Reconstitution en deux composantes, calées chaque année sur le département DREES (RPPS, au 1er janvier) :
  1. Officine (secteur DREES « Pharmacie ») : N_off(c, t) = officines(c, t−1) · r(d, t), avec
     r(d, t) = pharmaciens d'officine du dép. (DREES, 1/1/t) / officines du dép. (FINESS, 31/12/t−1).
     Σ communes = DREES dép. par construction.
  2. Hors officine (laboratoires, industrie, établissements, autres), par statut prive / public / ambigu :
     N_aut(c, t, s) = DREES dép. (t, s) · part de la commune dans le dép. pour ce statut, prise dans l'Annuaire
     Santé du 2026-11-13 et tenue fixe dans le temps (supposé).
Test posé avant de lancer : la composante officine 2026 (officines fin 2025 × r) comparée aux pharmaciens
d'officine de l'Annuaire (secteur SA33, nov. 2026). Seuil : erreur absolue relative médiane ≤ 25 % sur les
communes à au moins 5 pharmaciens d'officine, et ≤ 10 % à l'EPCI. Un échec dit que le ratio départemental ne
tient pas à l'échelle locale (taille des officines très variable).

Sorties (v2/data/processed/) : pharmaciens_commune_annee.parquet (com, dep, year, n_officine, n_autres_prive,
n_autres_public, n_autres_ambigu, n_prive_central), pharmaciens_checks.csv
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "v2" / "data" / "raw"
OUT = ROOT / "v2" / "data" / "processed"


def dep_of(com: pd.Series) -> pd.Series:
    return pd.Series(np.where(com.str.startswith("97"), com.str[:3], com.str[:2]), index=com.index)


def annuaire_ph() -> pd.DataFrame:
    """Pharmaciens actifs par commune (nov. 2026) : officine (SA33) et hors officine par statut d'activité."""
    path = sorted((RAW / "annuaire").glob("PS_LibreAcces_Personne_activite_*.txt"))[-1]
    cols = {"Identifiant PP": "pp", "Code profession": "prof", "Code mode exercice": "mode",
            "Numéro FINESS établissement juridique": "ej", "Code commune (coord. structure)": "com",
            "Code secteur d'activité": "sect", "Code genre activité": "genre"}
    d = pd.read_csv(path, sep="|", usecols=list(cols), dtype=str, quoting=3).rename(columns=cols)
    d = d[(d["prof"] == "21") & d["genre"].notna() & (d["genre"] != "GENR04") & d["com"].notna()]
    d["w"] = 1.0 / d.groupby("pp")["pp"].transform("size")
    d["off"] = d["sect"].isin(["SA33", "SA39", "SA38", "SA65"])   # officine, mutualiste, minière, antenne
    return d


def main():
    st = pd.read_parquet(OUT / "secteur_stock.parquet")
    st = st[st["profession"] == "pharmaciens"]
    off_dep = st[st["secteur"] == "Pharmacie"].groupby(["dep", "year"])["n"].sum().rename("ph_off")
    aut = st[st["secteur"] != "Pharmacie"].groupby(["dep", "year", "statut"])["n"].sum().unstack(fill_value=0)
    aut = aut.add_prefix("aut_")

    fin = pd.read_parquet(OUT / "finess_commune_annee.parquet")
    fin = fin[fin["categorie"] == "officine"].copy()
    fin["dep"] = dep_of(fin["com"])
    fin["year"] = fin["year"] + 1                       # FINESS au 31/12/t−1 ↔ DREES au 1/1/t
    off_fin_dep = fin.groupby(["dep", "year"])["n"].sum().rename("officines_dep")
    r = pd.concat([off_dep, off_fin_dep], axis=1, join="inner")
    r["r"] = r["ph_off"] / r["officines_dep"]
    f = fin.merge(r["r"].reset_index(), on=["dep", "year"], how="inner")
    f["n_officine"] = f["n"] * f["r"]

    an = annuaire_ph()
    an["dep"] = dep_of(an["com"])
    ej = pd.read_csv(RAW / "finess" / "etalab-cs1100501-stock-20260512-0339.csv", sep=";", skiprows=1, header=None,
                     encoding="latin1", dtype=str, usecols=[1, 16])
    ej.columns = ["ej", "sj"]
    sj = pd.to_numeric(ej["sj"], errors="coerce")
    ejs = pd.Series(np.where(sj >= 47, "prive", "public"), index=ej["ej"])[sj.notna().values]
    an["statut"] = np.where(an["mode"] == "L", "prive", an["ej"].map(ejs).fillna("ambigu"))
    hors = an[~an["off"]].groupby(["dep", "com", "statut"])["w"].sum()
    share = (hors / hors.groupby(level=["dep", "statut"]).transform("sum")).rename("part").reset_index()
    # repli : statut absent de l'Annuaire dans un dép. → parts communales hors officine, tous statuts
    allst = an[~an["off"]].groupby(["dep", "com"])["w"].sum()
    allst = (allst / allst.groupby(level="dep").transform("sum")).rename("part").reset_index()
    have = set(zip(share["dep"], share["statut"]))
    extra = [allst[allst["dep"] == d].assign(statut=s) for d in allst["dep"].unique()
             for s in ["prive", "public", "ambigu"] if (d, s) not in have]
    share = pd.concat([share] + extra, ignore_index=True)
    rows = []
    for s in ["prive", "public", "ambigu"]:
        a = aut[f"aut_{s}"].rename("tot").reset_index()
        sh = share[share["statut"] == s]
        m = a.merge(sh, on="dep", how="inner")
        m[f"n_autres_{s}"] = m["tot"] * m["part"]
        rows.append(m[["dep", "com", "year", f"n_autres_{s}"]])
    out = f[["com", "dep", "year", "n_officine"]]
    for x in rows:
        out = out.merge(x, on=["com", "dep", "year"], how="outer")
    out = out.fillna(0.0)
    p_amb = 0.5
    out["n_prive_central"] = out["n_officine"] + out["n_autres_prive"] + p_amb * out["n_autres_ambigu"]
    out["source"] = ("officines FINESS × ratio dép. DREES ; hors officine : DREES dép. × parts communales Annuaire "
                     "2026-11-13 (fixes)")
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT / "pharmaciens_commune_annee.parquet", index=False)

    # Contrôles : Σ communes = DREES dép. ; test 2026 contre l'Annuaire
    chk = out.groupby(["dep", "year"])[["n_officine", "n_autres_prive", "n_autres_public", "n_autres_ambigu"]].sum()
    tot = chk.sum(axis=1).rename("reconstitue")
    drees = st.groupby(["dep", "year"])["n"].sum().rename("drees")
    c = pd.concat([tot, drees], axis=1, join="inner")
    c["ecart_pct"] = 100 * (c["reconstitue"] / c["drees"] - 1)
    print("Σ communes vs DREES dép. : |écart| max % =", round(c["ecart_pct"].abs().max(), 3),
          "; médiane =", round(c["ecart_pct"].abs().median(), 3))

    obs = an[an["off"]].groupby("com")["w"].sum().rename("annuaire_officine")
    pred = out[out["year"] == 2026].set_index("com")["n_officine"].rename("reconstitue_2026")
    j = pd.concat([obs, pred], axis=1).fillna(0)
    big = j[j["annuaire_officine"] >= 5]
    are = (big["reconstitue_2026"] - big["annuaire_officine"]).abs() / big["annuaire_officine"]
    geo = pd.read_parquet(OUT / "commune_geo.parquet").set_index("com")["epci"]
    je = j.groupby(j.index.map(geo)).sum()
    je = je[je["annuaire_officine"] >= 5]
    are_e = (je["reconstitue_2026"] - je["annuaire_officine"]).abs() / je["annuaire_officine"]
    res = {"communes_n>=5": len(big), "ear_mediane_commune": are.median(), "ear_p90_commune": are.quantile(0.9),
           "epci_n>=5": len(je), "ear_mediane_epci": are_e.median(), "ear_p90_epci": are_e.quantile(0.9),
           "corr_commune": j.corr().iloc[0, 1],
           "annuaire_officine_total": j["annuaire_officine"].sum(), "reconstitue_officine_2026": j["reconstitue_2026"].sum()}
    verdict = "passe" if (res["ear_mediane_commune"] <= 0.25 and res["ear_mediane_epci"] <= 0.10) else "échoue"
    res["verdict"] = verdict
    pd.Series(res).to_csv(OUT / "pharmaciens_checks.csv")
    c.reset_index().to_csv(OUT / "pharmaciens_checks_dep.csv", index=False)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    nat = out.groupby("year")[["n_officine", "n_autres_prive", "n_autres_public", "n_autres_ambigu", "n_prive_central"]].sum()
    print(nat.round(0).to_string())


if __name__ == "__main__":
    main()
