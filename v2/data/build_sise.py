"""Inscrits en odontologie et en pharmacie par année d'études, France (données ouvertes SISE).

Run : uv run python v2/data/build_sise.py   (depuis la racine du dépôt, ≈ 10 s, réseau)

Remplace, pour le vivier de formation des dentistes et des pharmaciens, le fichier des organisateurs
(inscrits DREES par année d'études, fourni sous accord de confidentialité ; décision du 2026-11-15).

Source : MESR, « Effectifs d'étudiants inscrits dans les établissements publics sous tutelle du ministère en charge
de l'Enseignement supérieur » (SISE), jeu `fr-esr-sise-effectifs-d-etudiants-inscrits-esr-public`,
data.enseignementsup-recherche.gouv.fr, Licence Ouverte v2.0 (Etalab), rentrées 2017 à 2024.
Filtre : secteur disciplinaire « Odontologie » ou « Pharmacie », diplôme « Autres formations de santé » (le
diplôme d'État d'exercice ; hors masters, doctorats de recherche et HDR).
Année = année de rentrée (champ `rentree` : 2020 = année universitaire 2020-21), convention du fichier 990.
Année d'études k = niveau BAC + k (champ `degetu_lib`) ; « BAC + 6 et plus » (k = 6) mêle la 6e année, l'internat
et les thèses : à ne pas utiliser comme une cohorte propre.
Champ : établissements publics sous tutelle du MESR (les deux filières y sont presque entièrement).

Sorties :
  v2/data/raw/sise/sise_sante.json                réponse brute de l'API (non commitée)
  v2/data/processed/sise_sante.parquet            profession, k, year, n
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "v2" / "data" / "raw" / "sise"
OUT = ROOT / "v2" / "data" / "processed" / "sise_sante.parquet"
API = ("https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1/catalog/datasets/"
       "fr-esr-sise-effectifs-d-etudiants-inscrits-esr-public/records")
PROF = {"Odontologie": "dentistes", "Pharmacie": "pharmaciens"}


def fetch() -> list[dict]:
    q = {"select": "rentree,sect_disciplinaire_lib,degetu_lib,sum(effectif) as n",
         "where": "sect_disciplinaire_lib in (\"Odontologie\",\"Pharmacie\") "
                  "and diplome_lib=\"Autres formations de santé\"",
         "group_by": "rentree,sect_disciplinaire_lib,degetu_lib", "limit": 100}
    with urllib.request.urlopen(f"{API}?{urllib.parse.urlencode(q)}", timeout=60) as r:
        rows = json.load(r)["results"]
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "sise_sante.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return rows


def build(rows: list[dict]) -> pd.DataFrame:
    d = pd.DataFrame(rows)
    d["k"] = d.degetu_lib.str.extract(r"BAC \+ (\d+)").astype(float)
    d = d.dropna(subset=["k"])
    out = pd.DataFrame({"profession": d.sect_disciplinaire_lib.map(PROF), "k": d.k.astype(int),
                        "year": d.rentree.astype(int), "n": d.n.astype(float)})
    return out.sort_values(["profession", "k", "year"]).reset_index(drop=True)


if __name__ == "__main__":
    t = build(fetch())
    assert set(t.profession) == {"dentistes", "pharmaciens"} and t.year.nunique() >= 8, t.groupby("profession").year.agg(["min", "max"])
    t.to_parquet(OUT, index=False)
    print(t.pivot_table(index=["profession", "k"], columns="year", values="n").to_string())
