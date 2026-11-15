"""IQVIA-Pharmastat, vaccination contre la grippe en officine (data.gouv.fr), saisons 2020-21 à 2026-27.

Run (racine du dépôt) : uv run python v2/besoin/donnees/iqvia.py   (≈ 5 s ; 18 CSV, < 1 Mo, dans
v2/data/raw/besoin/iqvia/ s'ils manquent)

Source : IQVIA France, jeux « Vaccination Grippe AAAA-AAAA » sur data.gouv.fr, Licence Ouverte 2.0. Panel d'environ
60 à 90 % des officines (lignes UNIVERS, PHARMACIES, POURCENTAGE de `campagne`), **extrapolé** à la France : ce
n'est pas un recensement. Trois fichiers par saison :
  - campagne : totaux de fin de campagne (actes VGP, doses J07E1), avec la saison précédente à la même date (`cible`) ;
  - doses-actes : série quotidienne nationale, 65 ans et plus / moins de 65 ans, saison courante et précédente ;
  - couverture : cumul régional pour 10 000 habitants (régions 2016 ; DOM absents, observé).
Sorties (Licence Ouverte 2.0, commitées) : v2/data/processed/besoin/
  - iqvia_campagne.parquet : campagne, date, variable, valeur (et valeur de la saison précédente, `cible`) ;
  - iqvia_quotidien.parquet : campagne, date, jour, variable, groupe, valeur (une saison prise dans son propre fichier) ;
  - iqvia_regional.parquet : campagne, region, code, variable, groupe, valeur (pour 10 000 hab.).
Contrôle : Σ quotidien (deux groupes) = total de campagne publié, par saison et par variable, à 0,5 % près.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import CACHE, controle, ecrire  # noqa: E402

S = "https://static.data.gouv.fr/resources/"
URLS = {  # saison (année de début) -> fichiers ; liens lus le 2026-11-15 par l'API data.gouv.fr
    2021: ["vaccination-grippe-2021-2022/20231028-075149/couverture-2021.csv",
           "vaccination-grippe-2021-2022/20231028-075027/campagne-2021.csv",
           "vaccination-grippe-2020-2021/20231028-074724/doses-actes-2021.csv"],
    2022: ["vaccination-grippe-2021-2022-1/20231028-130402/couverture-2022.csv",
           "vaccination-grippe-2021-2022-1/20231028-130314/campagne-2022.csv",
           "vaccination-grippe-2021-2022-1/20231028-130217/doses-actes-2022.csv"],
    2023: ["vaccination-grippe-2023-2024/20240320-120344/doses-actes-2023.csv",
           "vaccination-grippe-2023-2024/20240320-120343/couverture-2023.csv",
           "vaccination-grippe-2023-2024/20240320-120342/campagne-2023.csv"],
    2024: ["vaccination-grippe-2024-2025/20251023-092806/couverture-2024.csv",
           "vaccination-grippe-2024-2025/20251023-092805/campagne-2024.csv",
           "vaccination-grippe-2024-2025/20251023-092807/doses-actes-2024.csv"],
    2025: ["vaccination-grippe-2025-2026/20261022-122142/doses-actes-2025.csv",
           "vaccination-grippe-2025-2026/20261022-122131/campagne-2025.csv",
           "vaccination-grippe-2025-2026/20261022-122132/couverture-2025.csv"],
    2026: ["vaccination-grippe-2026-2027/20261112-092655/doses-actes-2026.csv",
           "vaccination-grippe-2026-2027/20261112-092654/couverture-2026.csv",
           "vaccination-grippe-2026-2027/20261112-092652/campagne-2026.csv"],
}
CMD = "uv run python v2/besoin/donnees/iqvia.py"


def lire(rel: str) -> pd.DataFrame:
    p = CACHE / "iqvia" / Path(rel).name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(urllib.request.urlopen(S + rel, timeout=60).read())
    return pd.read_csv(p, dtype={"code": str})


def main():
    camp, quot, reg = [], [], []
    for an, fichiers in URLS.items():
        saison = f"{an}-{an + 1}"
        for rel in fichiers:
            d = lire(rel)
            nom = Path(rel).name
            if nom.startswith("campagne"):
                camp.append(d)
            elif nom.startswith("doses-actes"):
                # la saison précédente est reprise de son propre fichier, sauf 2020-21 (pas de fichier propre)
                quot.append(d[(d.campagne == saison) | ((an == 2021) & (d.campagne == "2020-2021"))])
            else:
                reg.append(d.assign(campagne=saison))
    camp = pd.concat(camp, ignore_index=True)
    quot = pd.concat(quot, ignore_index=True)
    reg = pd.concat(reg, ignore_index=True)[["campagne", "region", "code", "variable", "groupe", "valeur"]]
    ctl = []
    fin = camp[camp.variable.isin(["ACTE(VGP)", "DOSES(J07E1)"])]
    for r in fin.itertuples():
        q = quot[(quot.campagne == r.campagne) & (quot.variable == r.variable) & (quot.date <= r.date)]
        ctl.append(controle(f"IQVIA {r.variable} {r.campagne} au {r.date}", q.valeur.sum(), r.valeur,
                            source_publie="IQVIA, campagne-AAAA.csv (total de campagne)"))
    src = "IQVIA France (Pharmastat), Vaccination Grippe 2021-2022 à 2026-2027, data.gouv.fr"
    mil = "saisons 2021-22 à 2026-27 ; série quotidienne 2020-21 reprise du fichier 2021-22 ; 2026-27 (en cours, au " + str(camp.date.max()) + ")"
    ecrire(camp, "iqvia_campagne", licence="LO2", source=src, millesime=mil, commande=CMD, controles=ctl,
           dom="national (France entière extrapolée ; périmètre DOM non documenté)")
    ecrire(quot, "iqvia_quotidien", licence="LO2", source=src, millesime=mil, commande=CMD,
           dom="national (France entière extrapolée ; périmètre DOM non documenté)")
    ecrire(reg, "iqvia_regional", licence="LO2", source=src, millesime=mil, commande=CMD,
           dom=f"régions présentes : {', '.join(sorted(reg.code.unique()))} (aucun DOM)")
    print(f"campagne {len(camp)}, quotidien {len(quot)}, régional {len(reg)} lignes")


if __name__ == "__main__":
    main()
