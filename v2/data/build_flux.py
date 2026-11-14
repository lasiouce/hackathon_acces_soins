"""Axe 4 — proxy d'installations libérales par commune et par an (IDE, MK, CD), 2005–2025.

Run : uv run python v2/data/build_flux.py   (après build_commune.py ; ≈ 5 s)

Définition (solde, pas flux brut) :
    I_net(c, t) = N_<40(c, t) − N_<40(c, t−1) + a_dep(t−1) · N_<40(c, t−1)
  - N_<40 : libéraux de moins de 40 ans actifs au 31/12 (CartoSanté, FNPS/SNDS) ;
  - a_dep : part des moins de 40 ans qui passent 40 ans dans l'année, prise dans la pyramide du département
    (DREES RPPS libéral + mixte pour MK et CD ; SNDS pour les IDE) : N_35–39 / 5 / N_<40.
  I_net = entrées − sorties avant 40 ans (cessations, départs vers le salariat ou une autre commune).
  Biais : solde, donc sous-estime les entrées brutes de la mobilité et des sorties précoces ; un déménagement
  entre communes compte +1 / −1. Il ne voit que les libéraux (pas le salariat).

Tests posés avant de lancer :
  T1 (cohérence) : Σ communes de I_net = I_net calculé sur le pull départemental CartoSanté (même formule), à 1 %.
  T2 (falsification) : MK, année blanche de diplômés 2018 (DREES ER 1159) → I_net national 2018 < 0,8 × la
      moyenne de 2016–2017 et 2019–2020. Si non, le proxy ne voit pas les promotions et doit être rejeté.

Sorties (v2/data/processed/) : flux_installations_commune.parquet (profession, com, dep, year, n_lt40, n_lt40_prev,
a_dep, i_net), flux_checks.csv
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "v2"))   # paquet sante (ex-v1)
from sante.cartosante import axes, get_data  # noqa: E402  (v1, lecture seule)

OUT = ROOT / "v2" / "data" / "processed"
DS = {"kine_popage": "kines", "infi_popage": "infirmiers", "dent_popage": "dentistes"}
V1 = {"kines": "kines", "infirmiers": "infirmiers-liberaux", "dentistes": "dentistes"}


def aging_share() -> pd.DataFrame:
    s = pd.read_parquet(ROOT / "data" / "processed" / "stock.parquet")
    s = s[s["mode3"] == "liberal_mixte"]
    s = s[s["profession"].isin(V1.values())].replace({"profession": {v: k for k, v in V1.items()}})
    lt40 = s[s["age_lo"] < 40].groupby(["profession", "dep", "year"])["n"].sum()
    a3539 = s[s["age_lo"] == 35].groupby(["profession", "dep", "year"])["n"].sum()
    a = (a3539 / 5 / lt40).rename("a_dep").reset_index()
    # CartoSanté compte au 31/12/Y ≈ RPPS au 1/1/Y+1 : on prend la pyramide de l'année Y+1, sinon Y
    a["year"] = a["year"] - 1
    return a


def main():
    st = pd.read_parquet(OUT / "commune_stock.parquet")
    st = st[st["age_band"] == "Moins de 40 ans"]
    n = st.groupby(["profession", "com", "dep", "year"])["n"].sum().rename("n_lt40").reset_index()
    full = n.pivot_table(index=["profession", "com", "dep"], columns="year", values="n_lt40", fill_value=0)
    long = full.stack().rename("n_lt40").reset_index()
    long = long.sort_values(["profession", "com", "year"])
    long["n_lt40_prev"] = long.groupby(["profession", "com"])["n_lt40"].shift(1)
    long = long.dropna(subset=["n_lt40_prev"])
    # années où la commune existe dans la série (CartoSanté commence en 2004/05/06 selon la profession)
    first = n.groupby("profession")["year"].min()
    long = long[long["year"] > long["profession"].map(first)]
    a = aging_share()
    long["year_prev"] = long["year"] - 1
    long = long.merge(a.rename(columns={"year": "year_prev"}), on=["profession", "dep", "year_prev"], how="left")
    nat_a = a.groupby(["profession", "year"])["a_dep"].median()
    miss = long["a_dep"].isna()
    long.loc[miss, "a_dep"] = [nat_a.get((p, y - 1), nat_a.loc[p].iloc[0]) for p, y in
                               zip(long.loc[miss, "profession"], long.loc[miss, "year"])]
    long = long.drop(columns="year_prev")
    long["i_net"] = long["n_lt40"] - long["n_lt40_prev"] + long["a_dep"] * long["n_lt40_prev"]
    long["source"] = "CartoSanté *_popage (moins de 40 ans) ; pyramide DREES RPPS / SNDS ; solde, pas flux brut"
    OUT.mkdir(parents=True, exist_ok=True)
    long.to_parquet(OUT / "flux_installations_commune.parquet", index=False)

    # T1 : même formule sur le pull départemental
    rows = []
    for ds, prof in DS.items():
        years, ages, titles = axes(ds)
        lt = next(c for c, t in titles.items() if t.startswith("Moins"))
        d = get_data("dep", ds)
        d = d[d["age"] == lt].rename(columns={"code": "dep"}).groupby(["dep", "year"])["n"].sum().unstack()
        d = d.stack().rename("n").reset_index().sort_values(["dep", "year"])
        d["prev"] = d.groupby("dep")["n"].shift(1)
        d = d.dropna().assign(year_prev=lambda x: x["year"] - 1)
        d = d.merge(a[a["profession"] == prof].drop(columns="profession").rename(columns={"year": "year_prev"}),
                    on=["dep", "year_prev"], how="left")
        d["a_dep"] = d["a_dep"].fillna(d["a_dep"].median())
        d["i_dep"] = d["n"] - d["prev"] + d["a_dep"] * d["prev"]
        nat_dep = d.groupby("year")["i_dep"].sum()
        nat_com = long[long["profession"] == prof].groupby("year")["i_net"].sum()
        j = pd.concat([nat_com.rename("somme_communes"), nat_dep.rename("pull_dep")], axis=1).dropna()
        j["ecart_pct"] = 100 * (j["somme_communes"] / j["pull_dep"] - 1)
        rows.append(j.reset_index().assign(profession=prof))
    chk = pd.concat(rows, ignore_index=True)
    chk.to_csv(OUT / "flux_checks.csv", index=False)
    print(chk.pivot_table(index="year", columns="profession", values=["somme_communes", "ecart_pct"]).round(1).to_string())

    mk = chk[chk["profession"] == "kines"].set_index("year")["somme_communes"]
    ref = mk.loc[[2016, 2017, 2019, 2020]].mean()
    print(f"T2 MK : I_net 2018 = {mk.loc[2018]:.0f} ; moyenne 2016-17 & 2019-20 = {ref:.0f} ; "
          f"ratio {mk.loc[2018] / ref:.2f} → {'passe' if mk.loc[2018] < 0.8 * ref else 'ÉCHOUE'}")
    t1 = chk.groupby("profession")["ecart_pct"].apply(lambda s: s.abs().max())
    print("T1 max |écart| % :", t1.round(2).to_dict())


if __name__ == "__main__":
    main()
