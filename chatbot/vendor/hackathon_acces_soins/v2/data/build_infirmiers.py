"""Axe 4 — infirmiers : secteur public / privé × âge × sexe par département, pour entrer dans le jumeau.

Run : uv run python v2/data/build_infirmiers.py   (après build_secteur.py et build_annuaire.py ; ≈ 2 s)

Le BTS donne dép × secteur (6 modalités) sans âge ni sexe ; la v1 (sante/nurses.py) donne les salariés
dép × âge × sexe (ratissés). Hypothèse H_ind : dans un dép. et une année, le secteur est indépendant de
l'âge et du sexe. La cellule vaut alors N[d, s] · N[d, a, x] / N[d] : c'est le point fixe d'un ratissage à deux
marges depuis une graine uniforme. Les libéraux (SNDS, dép × âge × sexe) sont privés.

Test de H_ind, posé avant de regarder le résultat : la part de femmes chez les salariés privés et chez les
salariés publics, observée dans l'Annuaire Santé (nov. 2026, civilité), par département. Sous H_ind elles
sont égales ; on rapporte l'écart médian en points. H_ind est rejetée si l'écart médian dépasse 3 points.

Sortie : v2/data/processed/infirmiers_secteur_age_sexe.parquet
  dep, year, statut (prive / public), mode3, age_band, age_lo, age_hi, sex, n, methode
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v2" / "data" / "processed"


def main():
    sal = pd.read_parquet(ROOT / "data" / "processed" / "stock_nurses_salaried.parquet")
    sal = sal.groupby(["dep", "year", "age_band", "age_lo", "age_hi", "sex"], as_index=False, dropna=False)["n"].sum()
    st = pd.read_parquet(OUT / "secteur_stock.parquet")
    bts = st[(st["profession"] == "infirmiers") & (st["source"] == "BTS")]
    bts = bts.groupby(["dep", "year", "statut", "mode3"], as_index=False)["n"].sum()
    bts["part"] = bts["n"] / bts.groupby(["dep", "year"])["n"].transform("sum")
    cell = sal.merge(bts[["dep", "year", "statut", "mode3", "part"]], on=["dep", "year"], how="inner")
    cell["n"] = cell["n"] * cell["part"]
    cell = cell.drop(columns="part").assign(methode="BTS dép × secteur ⊗ salariés dép × âge × sexe (H_ind)")
    lib = pd.read_parquet(ROOT / "data" / "processed" / "stock.parquet")
    lib = lib[lib["profession"] == "infirmiers-liberaux"]
    lib = lib.groupby(["dep", "year", "age_band", "age_lo", "age_hi", "sex"], as_index=False, dropna=False)["n"].sum()
    lib = lib.assign(statut="prive", mode3="liberal_mixte", methode="SNDS libéraux")
    out = pd.concat([cell, lib], ignore_index=True)
    out.to_parquet(OUT / "infirmiers_secteur_age_sexe.parquet", index=False)

    # Contrôle : marges reproduites
    m1 = out[out["mode3"] != "liberal_mixte"].groupby(["dep", "year", "statut", "mode3"])["n"].sum()
    e1 = (m1 - bts.set_index(["dep", "year", "statut", "mode3"])["n"]).abs().max()
    m2 = out[out["mode3"] != "liberal_mixte"].groupby(["dep", "year", "age_band", "sex"])["n"].sum()
    e2 = (m2 - sal.set_index(["dep", "year", "age_band", "sex"])["n"]).abs().max()
    print(f"marge dép × secteur : écart max {e1:.2e} ; marge dép × âge × sexe : écart max {e2:.2e}")
    y = out[out["year"] == out["year"].max()]
    print(y.groupby("statut")["n"].sum().round(0), "année", out["year"].max())

    # Test de H_ind sur la part de femmes (Annuaire, salariés)
    an = pd.read_parquet(OUT / "annuaire_commune.parquet")
    an = an[(an["profession"] == "infirmiers") & (an["mode"] == "salarie") & an["statut"].isin(["prive", "public"])
            & (an["dep"] != "")]
    f = an.pivot_table(index=["dep", "statut"], columns="sexe", values="personnes", aggfunc="sum", fill_value=0)
    f["part_f"] = f["F"] / (f["F"] + f["H"])
    w = f["part_f"].unstack("statut").dropna()
    w["ecart_pts"] = 100 * (w["prive"] - w["public"])
    print("H_ind, part de femmes privé − public (points), par dép. :", w["ecart_pts"].describe().round(2).to_dict())
    nat = an.groupby(["statut", "sexe"])["personnes"].sum().unstack()
    print("national :", (100 * nat["F"] / nat.sum(axis=1)).round(1).to_dict())
    verdict = "rejetée" if abs(w["ecart_pts"].median()) > 3 else "non rejetée"
    print("H_ind (seuil 3 points sur l'écart médian) :", verdict)
    w.to_csv(OUT / "infirmiers_test_hind.csv")


if __name__ == "__main__":
    main()
