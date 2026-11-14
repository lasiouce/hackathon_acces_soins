"""Axe 4 — Annuaire Santé (RPPS, extraction en libre accès) → effectifs par commune × secteur public / privé.

Run : uv run python v2/data/build_annuaire.py   (depuis la racine du dépôt, ≈ 40 s)

Entrée : ANS, « Annuaire Santé – extractions des données en libre accès » (data.gouv.fr), fichier
PS_LibreAcces_Personne_activite_<horodatage>.txt (une ligne par activité, une ligne vide d'activité pour les
inscrits sans activité). Pas d'âge dans l'extraction ; le sexe est lu sur la civilité (M / MME).
On ne garde ni nom ni identifiant dans les sorties : seulement des comptes.

Statut d'une activité :
  1. mode libéral (L) → prive ;
  2. sinon, si l'activité a un FINESS juridique → statut juridique FINESS (≥ 47 privé, sinon public ;
     40–46, sécurité sociale, compté public, comme dans build_secteur.py) ;
  3. sinon, code secteur d'activité RPPS (table SECTEUR_RPPS) → prive / public / ambigu.
Statut de la personne : une activité libérale → privé (mixtes inclus) ; sinon une activité publique → public ;
sinon une activité ambiguë → ambigu ; sinon privé. Le lieu, lui, se répartit : une personne à k activités
compte 1/k dans la commune de chacune ; les sommes donnent des personnes, pas des activités.

Sorties (v2/data/processed/)
  annuaire_commune.parquet  profession, com, dep, sexe, mode, statut, diplome (fr / ue / autre), personnes, activites,
                            extraction
  annuaire_checks.csv       comptes de contrôle (lignes, personnes, commune manquante)
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "v2" / "data" / "raw"
OUT = ROOT / "v2" / "data" / "processed"

PROF = {"21": "pharmaciens", "40": "dentistes", "50": "sages-femmes", "60": "infirmiers", "70": "kines"}
COLS = {"Identifiant PP": "pp", "Code civilité": "civ", "Code profession": "prof", "Code mode exercice": "mode",
        "Numéro FINESS établissement juridique": "finess_ej", "Code commune (coord. structure)": "com",
        "Code Département (structure)": "dep", "Code secteur d'activité": "sect",
        "Code section tableau pharmaciens": "sec_ph", "Code genre activité": "genre"}

PUBLIC = {"SA01", "SA02", "SA06", "SA14", "SA15", "SA19", "SA24", "SA26", "SA27", "SA37", "SA47", "SA68"}
PRIVE = {"SA03", "SA04", "SA07", "SA08", "SA09", "SA10", "SA11", "SA23", "SA25", "SA28", "SA29", "SA31",
         "SA32", "SA33", "SA34", "SA36", "SA38", "SA39", "SA40", "SA42", "SA44", "SA45", "SA46", "SA48",
         "SA52", "SA56", "SA58", "SA59", "SA61", "SA64", "SA65", "SA69"}
# le reste (EHPAD SA17, handicap SA16, centres de santé SA05, autre sanitaire SA30, non défini SA43, …) : ambigu


def finess_status() -> pd.Series:
    ej = pd.read_csv(RAW / "finess" / "etalab-cs1100501-stock-20260512-0339.csv", sep=";", skiprows=1,
                     header=None, encoding="latin1", dtype=str, usecols=[1, 16])
    ej.columns = ["ej", "sj"]
    sj = pd.to_numeric(ej["sj"], errors="coerce")
    return pd.Series(sj.ge(47).map({True: "prive", False: "public"}).where(sj.notna()).values, index=ej["ej"])


def main():
    path = sorted((RAW / "annuaire").glob("PS_LibreAcces_Personne_activite_*.txt"))[-1]
    stamp = re.search(r"_(\d{8})\d*\.txt$", path.name).group(1)
    extraction = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
    d = pd.read_csv(path, sep="|", usecols=list(COLS), dtype=str, quoting=3, encoding="utf-8").rename(columns=COLS)
    d = d[d["prof"].isin(PROF)]
    n_rows, n_pers = len(d), d["pp"].nunique()
    active = d[d["genre"].notna() & (d["genre"] != "GENR04")].copy()       # GENR04 = activité non soignante
    n_inactive = n_pers - active["pp"].nunique()

    ej = finess_status()
    active["statut"] = "ambigu"
    active.loc[active["sect"].isin(PUBLIC), "statut"] = "public"
    active.loc[active["sect"].isin(PRIVE), "statut"] = "prive"
    via_ej = active["finess_ej"].map(ej)
    active.loc[via_ej.notna(), "statut"] = via_ej[via_ej.notna()]
    active.loc[active["mode"] == "L", "statut"] = "prive"
    # Statut de la personne (décision « libéral = privé ») : une activité libérale → privé (libéraux et mixtes) ;
    # sinon une activité publique → public ; sinon une activité ambiguë → ambigu ; sinon privé.
    flags = pd.DataFrame({"pp": active["pp"], "lib": active["mode"] == "L", "pub": active["statut"] == "public",
                          "amb": active["statut"] == "ambigu"})
    any_ = flags.groupby("pp")[["lib", "pub", "amb"]].transform("max")
    has_lib, has_pub, has_amb = any_["lib"], any_["pub"], any_["amb"]
    active["statut_activite"] = active["statut"]
    active["statut"] = "prive"
    active.loc[~has_lib & has_amb, "statut"] = "ambigu"
    active.loc[~has_lib & has_pub, "statut"] = "public"
    # Origine du diplôme (fichier Dipl_AutExerc) : fr si un diplôme d'État français, sinon ue (UE / EEE), sinon autre.
    dp = sorted((RAW / "annuaire").glob("PS_LibreAcces_Dipl_AutExerc_*.txt"))[-1]
    dip = pd.read_csv(dp, sep="|", dtype=str, quoting=3, usecols=["Identifiant PP", "Code type diplôme obtenu"])
    dip.columns = ["pp", "t"]
    dip = dip[dip["pp"].isin(active["pp"])]
    org = pd.DataFrame({"pp": dip["pp"], "fr": dip["t"] == "DE", "ue": dip["t"] == "DEEE"}).groupby("pp").max()
    origin = pd.Series(np.select([org["fr"], org["ue"]], ["fr", "ue"], "autre"), index=org.index)
    active["diplome"] = active["pp"].map(origin).fillna("inconnu")
    active["w"] = 1.0 / active.groupby("pp")["pp"].transform("size")
    active["profession"] = active["prof"].map(PROF)
    active["sexe"] = active["civ"].map({"M": "H", "MME": "F"})
    active["mode"] = active["mode"].map({"L": "liberal", "S": "salarie", "B": "benevole"}).fillna("inconnu")
    active["com"] = active["com"].fillna("")
    # « Code Département (structure) » est vide dans l'extraction : on le dérive du code commune.
    active["dep"] = np.where(active["com"].str.startswith("97"), active["com"].str[:3], active["com"].str[:2])
    out = (active.groupby(["profession", "com", "dep", "sexe", "mode", "statut", "diplome"], as_index=False)
           .agg(personnes=("w", "sum"), activites=("w", "size")))
    out["extraction"] = extraction
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT / "annuaire_commune.parquet", index=False)

    chk = active.groupby("profession").agg(personnes=("w", "sum"), activites=("w", "size"),
                                           sans_commune=("com", lambda s: (s == "").mean()),
                                           via_finess=("finess_ej", lambda s: s.map(ej).notna().mean()))
    pr = out.pivot_table(index="profession", columns="statut", values="personnes", aggfunc="sum", fill_value=0)
    chk = chk.join(pr)
    dp_share = out.pivot_table(index="profession", columns="diplome", values="personnes", aggfunc="sum", fill_value=0)
    chk = chk.join((dp_share.div(dp_share.sum(axis=1), axis=0)).add_prefix("part_diplome_"))
    chk["extraction"] = extraction
    chk.to_csv(OUT / "annuaire_checks.csv")
    print(f"lignes {n_rows}, personnes {n_pers}, sans activité de soin {n_inactive}")
    print(chk.round(3).to_string())


if __name__ == "__main__":
    sys.exit(main())
