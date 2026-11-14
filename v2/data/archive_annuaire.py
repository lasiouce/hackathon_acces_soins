"""Axe 4 — archivage de l'Annuaire Santé : un instantané daté, puis les flux entre deux instantanés.

Run : uv run python v2/data/archive_annuaire.py [--local]   (depuis la racine ; ≈ 1 min avec téléchargement)

L'ANS republie chaque jour l'extraction en libre accès sur data.gouv.fr, sans archive. Pour avoir des flux
d'installation individuels par commune (logit de l'axe 2), il faut garder nous-mêmes des instantanés.
  1. Télécharge le zip du jour (≈ 230 Mo ; la taille est affichée avant), sauf avec --local qui réutilise le
     dernier fichier PS_LibreAcces_Personne_activite_*.txt de v2/data/raw/annuaire/.
  2. Écrit un instantané réduit, sans nom ni prénom : v2/data/raw/annuaire/archive/<AAAA-MM-JJ>.parquet
     (identifiant RPPS, profession, civilité, mode, commune, secteur, FINESS juridique, genre d'activité).
     L'identifiant RPPS est public dans l'extraction ; il reste dans raw/ (non versionné) et sert au seul appariement.
  3. Compare au précédent instantané et écrit les flux agrégés (aucun identifiant) :
     v2/data/processed/annuaire_flux_<avant>_<après>.parquet : profession × commune × type, où type ∈
       entree (personne absente avant, présente après, dans la profession),
       sortie (présente avant, absente après),
       arrivee / depart (même personne, commune d'activité ajoutée / retirée),
       stable.
Aucune tâche planifiée n'est créée : la fréquence est une décision de l'équipe (open.md).
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "v2" / "data" / "raw" / "annuaire"
ARCH = RAW / "archive"
OUT = ROOT / "v2" / "data" / "processed"
DATASET = "https://www.data.gouv.fr/api/1/datasets/6aaace635061abc0468090bb/"
PROF = {"21": "pharmaciens", "40": "dentistes", "50": "sages-femmes", "60": "infirmiers", "70": "kines"}
COLS = {"Identifiant PP": "pp", "Code civilité": "civ", "Code profession": "prof", "Code mode exercice": "mode",
        "Numéro FINESS établissement juridique": "finess_ej", "Code commune (coord. structure)": "com",
        "Code secteur d'activité": "sect", "Code genre activité": "genre"}


def download() -> Path:
    meta = json.loads(urllib.request.urlopen(DATASET, timeout=60).read())
    res = meta["resources"][0]
    print(f"ressource : {res['title']} — {res.get('filesize', 0) / 1e6:.0f} Mo, modifiée {res['last_modified'][:10]}")
    z = RAW / res["title"]
    if not z.exists():
        subprocess.run(["curl", "-sSf", "-o", str(z), res["url"]], check=True)
    with zipfile.ZipFile(z) as f:
        name = next(n for n in f.namelist() if "Personne_activite" in n)
        f.extract(name, RAW)
    return RAW / name


def snapshot(txt: Path) -> tuple[str, pd.DataFrame]:
    stamp = re.search(r"_(\d{8})\d*\.txt$", txt.name).group(1)
    date = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}"
    d = pd.read_csv(txt, sep="|", usecols=list(COLS), dtype=str, quoting=3).rename(columns=COLS)
    d = d[d["prof"].isin(PROF) & d["genre"].notna() & (d["genre"] != "GENR04")]
    d["profession"] = d["prof"].map(PROF)
    d["com"] = d["com"].fillna("")
    d = d.drop(columns="prof").drop_duplicates()
    ARCH.mkdir(parents=True, exist_ok=True)
    d.to_parquet(ARCH / f"{date}.parquet", index=False)
    return date, d


def diff(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    ka = a[["pp", "profession", "com"]].drop_duplicates()
    kb = b[["pp", "profession", "com"]].drop_duplicates()
    m = ka.merge(kb, on=["pp", "profession", "com"], how="outer", indicator=True)
    in_a = pd.MultiIndex.from_frame(m[["pp", "profession"]]).isin(pd.MultiIndex.from_frame(ka[["pp", "profession"]]))
    in_b = pd.MultiIndex.from_frame(m[["pp", "profession"]]).isin(pd.MultiIndex.from_frame(kb[["pp", "profession"]]))
    right, left = (m["_merge"] == "right_only").to_numpy(), (m["_merge"] == "left_only").to_numpy()
    m["type"] = "stable"
    m.loc[right & ~in_a, "type"] = "entree"
    m.loc[right & in_a, "type"] = "arrivee"
    m.loc[left & ~in_b, "type"] = "sortie"
    m.loc[left & in_b, "type"] = "depart"
    return m.groupby(["profession", "com", "type"]).size().rename("n").reset_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="réutiliser le dernier .txt déjà présent")
    args = ap.parse_args()
    txt = sorted(RAW.glob("PS_LibreAcces_Personne_activite_*.txt"))[-1] if args.local else download()
    date, cur = snapshot(txt)
    print(f"instantané {date} : {len(cur)} activités, {cur['pp'].nunique()} personnes")
    prev = sorted(p for p in ARCH.glob("*.parquet") if p.stem < date)
    if not prev:
        print("aucun instantané antérieur : pas de flux à calculer")
        return
    before = pd.read_parquet(prev[-1])
    f = diff(before, cur)
    OUT.mkdir(parents=True, exist_ok=True)
    f.to_parquet(OUT / f"annuaire_flux_{prev[-1].stem}_{date}.parquet", index=False)
    print(f.pivot_table(index="profession", columns="type", values="n", aggfunc="sum", fill_value=0).to_string())


if __name__ == "__main__":
    main()
