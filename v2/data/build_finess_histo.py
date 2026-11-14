"""Axe 4 — FINESS historique 2004–2025 : officines, maisons de santé et centres de santé par commune et par an.

Run : uv run python v2/data/build_finess_histo.py   (depuis la racine ; ≈ 1 min ; lit le zip de 196 Mo dézippé)

Source : FINESS, « Extraction du fichier des établissements », historique 2004–2025 (data.gouv.fr, fichier
etalab-stock-et-historique-2004-2025.zip, un état au 31/12 de chaque année). Encodage latin-1 jusqu'en 2024,
UTF-8 ensuite (détecté).

Catégories retenues : 620 pharmacie d'officine ; 603 maison de santé (L.6223-3) ; 124 centre de santé.
Flux d'officines entre deux états successifs, par numéro FINESS d'établissement :
  ouverture  = numéro présent en t, absent en t−1 ;
  fermeture  = présent en t−1, absent en t ;
  transfert  = présent les deux années, commune changée (compté −1 / +1 sur les communes).
Une officine transférée sous un nouveau numéro apparaît comme fermeture + ouverture (biais documenté).

Sorties (v2/data/processed/) : finess_commune_annee.parquet (com, year, categorie, n),
officines_flux_commune.parquet (com, year, ouvertures, fermetures, transferts_entrants, transferts_sortants),
finess_histo_checks.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "v2" / "data" / "raw" / "finess" / "historique" / "etalab-stock-et-historique-2004-2024"
OUT = ROOT / "v2" / "data" / "processed"
CATS = {"620": "officine", "603": "maison_de_sante", "124": "centre_de_sante"}


def read(year: int) -> pd.DataFrame:
    f = DIR / f"etalab_stock_et_{year}1231.csv"
    raw = f.read_bytes()
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        txt = raw.decode("latin-1")
    from io import StringIO
    d = pd.read_csv(StringIO(txt), sep=";", dtype=str, usecols=["nofinesset", "cog", "categetab", "dateouvert"])
    d = d[d["categetab"].isin(CATS)]
    d["categorie"] = d["categetab"].map(CATS)
    d["year"] = year
    return d


def main():
    years = list(range(2004, 2026))
    frames = {y: read(y) for y in years}
    allf = pd.concat(frames.values(), ignore_index=True)
    stock = allf.groupby(["cog", "year", "categorie"]).size().rename("n").reset_index().rename(columns={"cog": "com"})
    OUT.mkdir(parents=True, exist_ok=True)
    stock["source"] = "FINESS historique 2004–2025 (état au 31/12), data.gouv.fr"
    stock.to_parquet(OUT / "finess_commune_annee.parquet", index=False)

    rows = []
    for y in years[1:]:
        a = frames[y - 1][frames[y - 1]["categorie"] == "officine"].set_index("nofinesset")["cog"]
        b = frames[y][frames[y]["categorie"] == "officine"].set_index("nofinesset")["cog"]
        a, b = a[~a.index.duplicated()], b[~b.index.duplicated()]
        opened = b[~b.index.isin(a.index)].value_counts().rename("ouvertures")
        closed = a[~a.index.isin(b.index)].value_counts().rename("fermetures")
        both = a.index.intersection(b.index)
        moved = both[(a.loc[both] != b.loc[both]).to_numpy()]
        tin = b.loc[moved].value_counts().rename("transferts_entrants")
        tout = a.loc[moved].value_counts().rename("transferts_sortants")
        r = pd.concat([opened, closed, tin, tout], axis=1).fillna(0).astype(int)
        r.index.name = "com"
        rows.append(r.reset_index().assign(year=y))
    flux = pd.concat(rows, ignore_index=True)
    flux.to_parquet(OUT / "officines_flux_commune.parquet", index=False)

    nat = stock.pivot_table(index="year", columns="categorie", values="n", aggfunc="sum", fill_value=0)
    nf = flux.groupby("year")[["ouvertures", "fermetures", "transferts_entrants"]].sum()
    chk = nat.join(nf)
    off = chk["officine"]
    chk["solde_flux"] = chk["ouvertures"] - chk["fermetures"]
    chk["delta_stock"] = off.diff()
    chk["ecart_identite"] = chk["delta_stock"] - chk["solde_flux"]
    chk.to_csv(OUT / "finess_histo_checks.csv")
    print(chk.to_string())


if __name__ == "__main__":
    main()
