"""Axe 4 — séparer public et privé dans le stock RPPS / ADELI / BTS.

Run : uv run python v2/data/build_secteur.py   (depuis la racine du dépôt, ≈ 30 s)

Idée. Les fichiers DREES bruts croisent déjà dép × secteur d'activité × mode d'exercice × âge × sexe ;
le loader v1 (sante/load.py) gardait le secteur à « Ensemble ». On relit le secteur et on classe :
  - libéral et mixte                          -> prive (décision v2 « libéral = privé »)
  - salarié, secteur sans ambiguïté           -> prive ou public
  - salarié, secteur mixte public/privé       -> ambigu ; part privée centrale prise dans FINESS
    (statut juridique des établissements de la catégorie), bornes 0 et 1.
Infirmiers : BTS (salariés, secteur public/privé déjà séparé) + SNDS (libéraux, tous privés).

Sorties (v2/data/processed/)
  secteur_stock.parquet  profession, source, year, dep, mode, mode3, secteur, statut, p_central, age_band, sex, n
  secteur_split.parquet  profession × year × dep (+ 'FR') × mode3 : n, n_prive_sur, n_public_sur, n_ambigu,
                         n_prive_central, part_prive_min / central / max, source, millesime
  secteur_checks.csv     Σ cellules détaillées vs total France du fichier, par profession × année
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from sante.load import code_label, dep_code, is_total  # noqa: E402  (v1, lecture seule)

RAW = ROOT / "data" / "raw" / "drees"
FINESS = ROOT / "v2" / "data" / "raw" / "finess"
OUT = ROOT / "v2" / "data" / "processed"

FILES = {
    "pharmaciens_rpps_2012_2026": ("pharmaciens", "RPPS"),
    "sages_femmes_rpps_2012_2026": ("sages-femmes", "RPPS"),
    "chirurgiens_dentistes_rpps_2012_2026": ("dentistes", "RPPS"),
    "kinesitherapeutes_rpps_2017_2026": ("kines", "RPPS"),
    "kinesitherapeutes_adeli_2012_2016": ("kines", "ADELI"),
}
MILLESIME_DREES = "DREES, démographie des professionnels de santé depuis 2012, publication 2026-07-02"
MILLESIME_FINESS = "FINESS extraction établissements + entités juridiques au 2026-05-04 (data.gouv, 2026-05-12)"

MODE3 = {"Libéral": "liberal_mixte", "Mixte": "liberal_mixte", "Libéraux ou mixtes": "liberal_mixte",
         "Salarié hospitalier": "salarie_hosp", "Salariés hospitaliers": "salarie_hosp",
         "Autre Salarié": "autre_salarie", "Autres salariés": "autre_salarie"}

# Libellé de secteur (sans code) -> classe pour un salarié. Les classes « ambigu:<proxy> » prennent leur part
# privée centrale dans FINESS (proxy) ou valent 0,5 faute de source (« inconnu »).
SECTEUR = {
    "Hôpital public": "public",
    "Etablissement privé ESPIC": "prive",
    "Etablissement privé lucratif": "prive",
    "Pharmacie": "prive",            # officine (y c. mutualiste ; pharmacie minière négligeable)
    "Laboratoire": "prive",          # LBM et laboratoires pharmaceutiques ; les labos hospitaliers sont sous « Hôpital »
    "Médicament": "prive",           # fabrication, exploitation, répartition
    "Cabinet individuel": "prive",
    "Cabinet de groupe, société": "prive",
    "Cabinet de groupe,exercice en societé": "prive",
    "Centre de santé, maison de santé": "ambigu:centre_sante",
    "Centre de santé": "ambigu:centre_sante",
    "Prévention": "ambigu:pmi",
    "Etablissement sanitaire et social": "ambigu:medico_social",
    "Etablissement pour handicapés": "ambigu:handicap",
    "Etablissement pour personnes âgées": "ambigu:ehpad",
    "Autre établissement sanitaire et social": "ambigu:medico_social",
    "Prévention et établissement de santé": "ambigu:inconnu",
    "Sécurité sociale,ministère,collectivité,association": "ambigu:inconnu",
    "Autre secteur": "ambigu:inconnu",
    "Autres secteurs": "ambigu:inconnu",
}

# BTS infirmiers salariés : secteur déjà public / privé
BTS_SECTEUR = {"1": ("Hôpital public", "public", "salarie_hosp"), "2": ("Hôpital privé", "prive", "salarie_hosp"),
               "3": ("Social ou médico-social public", "public", "autre_salarie"),
               "4": ("Social ou médico-social privé", "prive", "autre_salarie"),
               "5": ("Autre secteur public", "public", "autre_salarie"),
               "6": ("Autre secteur privé", "prive", "autre_salarie")}

# FINESS : catégories d'établissement par proxy (codes de la nomenclature « catégorie d'établissement »)
PROXY_CATS = {
    "centre_sante": ["124"],
    "pmi": ["223", "228"],                                   # PMI, centres de planification / santé sexuelle
    "ehpad": ["500"],
    "handicap": ["182", "183", "186", "190", "255", "437", "448"],   # médicalisés : SESSAD, IME, ITEP, CAMSP, MAS, FAM/EAM
}
PROXY_CATS["medico_social"] = PROXY_CATS["ehpad"] + PROXY_CATS["handicap"]


def finess_shares() -> pd.DataFrame:
    """Part privée (établissements) par proxy. Statut juridique FINESS : 01–39 public ; 40–46 sécurité sociale,
    compté public (administration de sécurité sociale) ; 47–99 privé (mutuelles, associations, sociétés)."""
    et = pd.read_csv(FINESS / "etalab-cs1100502-stock-20260512-0339.csv", sep=";", skiprows=1, header=None,
                     encoding="latin1", dtype=str, usecols=[1, 2, 3, 4, 18])
    et.columns = ["et", "ej", "rs", "rsl", "cat"]
    ej = pd.read_csv(FINESS / "etalab-cs1100501-stock-20260512-0339.csv", sep=";", skiprows=1, header=None,
                     encoding="latin1", dtype=str, usecols=[1, 16])
    ej.columns = ["ej", "sj"]
    m = et.merge(ej, on="ej", how="left")
    m["prive"] = pd.to_numeric(m["sj"], errors="coerce") >= 47
    rows = []
    for proxy, cats in PROXY_CATS.items():
        sel = m[m["cat"].isin(cats)]
        rows.append((proxy, len(sel), sel["prive"].mean()))
    dent = m[(m["cat"] == "124") & (m["rs"].fillna("") + m["rsl"].fillna("")).str.contains("DENT")]
    rows.append(("centre_sante_dentaire", len(dent), dent["prive"].mean()))
    return pd.DataFrame(rows, columns=["proxy", "n_etab", "p_prive"]).set_index("proxy")


def p_central(classe: str, profession: str, shares: pd.DataFrame) -> tuple[float, str]:
    if classe == "prive":
        return 1.0, "classement"
    if classe == "public":
        return 0.0, "classement"
    proxy = classe.split(":")[1]
    if proxy == "inconnu":
        return 0.5, "supposé (aucune source ouverte)"
    if proxy == "centre_sante" and profession == "dentistes":
        proxy = "centre_sante_dentaire"
    return float(shares.loc[proxy, "p_prive"]), f"FINESS {proxy} (n={int(shares.loc[proxy, 'n_etab'])} étab.)"


def load_drees(stem: str, profession: str, source: str, shares: pd.DataFrame):
    df = pd.read_excel(RAW / f"{stem}.xlsx", sheet_name="Effectifs", engine="calamine")
    years = [c for c in df.columns if str(c).startswith("effectif_")]
    dims = ["territoire", "region", "departement", "secteur_activite", "exercice", "tranche_age", "sexe"]
    df = df[dims + years]
    tot = df[dims].apply(lambda col: col.map(is_total))
    nat = df[tot.drop(columns="territoire").all(axis=1) & df["territoire"].astype(str).str.startswith("0")]
    national = nat[years].iloc[0]
    keep = ~df["territoire"].astype(str).str.startswith("0")
    for d in dims[1:]:
        keep &= ~tot[d]
    long = df[keep].melt(id_vars=dims, value_vars=years, var_name="year", value_name="n")
    long["year"] = long["year"].str.slice(-4).astype(int)
    long["n"] = pd.to_numeric(long["n"], errors="coerce").fillna(0.0)
    sect = long["secteur_activite"].map(lambda s: code_label(s)[1])
    mode = long["exercice"].map(lambda s: code_label(s)[1])
    out = pd.DataFrame({
        "profession": profession, "source": source, "year": long["year"],
        "dep": long["departement"].map(lambda s: dep_code(code_label(s)[0])),
        "mode": mode, "mode3": mode.map(MODE3), "secteur": sect,
        "age_band": long["tranche_age"].map(lambda s: code_label(s)[1]),
        "sex": long["sexe"].map(lambda s: {"1": "H", "2": "F"}[code_label(s)[0]]),
        "n": long["n"],
    })
    unknown = set(out["secteur"]) - set(SECTEUR)
    assert not unknown, f"secteur non classé : {unknown}"
    salarie = out["mode3"] != "liberal_mixte"
    out["statut"] = "prive"
    out.loc[salarie, "statut"] = out.loc[salarie, "secteur"].map(SECTEUR).str.split(":").str[0]
    pc = {s: p_central(c, profession, shares) for s, c in SECTEUR.items()}
    out["p_central"] = 1.0
    out.loc[salarie, "p_central"] = out.loc[salarie, "secteur"].map(lambda s: pc[s][0])
    out["p_source"] = "libéral ou mixte"
    out.loc[salarie, "p_source"] = out.loc[salarie, "secteur"].map(lambda s: pc[s][1])
    check = out.groupby("year")["n"].sum().rename("sum_detailed").to_frame()
    check["national_total"] = [float(national[f"effectif_{y}"]) for y in check.index]
    check["profession"], check["source"] = profession, source
    return out, check.reset_index()


def load_nurses():
    """Infirmiers : BTS salariés dép × secteur (sans croisement âge/sexe) + SNDS libéraux dép."""
    b = pd.read_excel(RAW / "infirmieres_salariees_bts_2013_2023.xlsx", sheet_name="Effectifs", engine="calamine")
    years = [c for c in b.columns if str(c).startswith("effectif_")]
    base = (b["Spécialité"].str.startswith("0") & b["Sexe"].str.startswith("0")
            & b["Tranche d'âge"].str.startswith("00"))
    nat = b[base & b["Région"].str.startswith("00") & b["Secteur d'activité"].str.startswith("0-")]
    national = nat[years].iloc[0]
    d = b[base & ~b["Région"].str.startswith("00") & ~b["Département"].astype(str).str.contains("Ensemble|entière")
          & ~b["Secteur d'activité"].str.startswith("0-")]
    long = d.melt(id_vars=["Département", "Secteur d'activité"], value_vars=years, var_name="year", value_name="n")
    code = long["Secteur d'activité"].str.split("-").str[0]
    sal = pd.DataFrame({
        "profession": "infirmiers", "source": "BTS", "year": long["year"].str.slice(-4).astype(int),
        "dep": long["Département"].map(lambda s: dep_code(code_label(s)[0])),
        "mode": "Salarié", "mode3": code.map(lambda c: BTS_SECTEUR[c][2]),
        "secteur": code.map(lambda c: BTS_SECTEUR[c][0]), "statut": code.map(lambda c: BTS_SECTEUR[c][1]),
        "age_band": "Ensemble", "sex": "Ensemble", "n": pd.to_numeric(long["n"], errors="coerce").fillna(0.0)})
    sal["p_central"] = (sal["statut"] == "prive").astype(float)
    sal["p_source"] = "BTS (secteur public / privé)"
    check = sal.groupby("year")["n"].sum().rename("sum_detailed").to_frame()
    check["national_total"] = [float(national[f"effectif_{y}"]) for y in check.index]
    check["profession"], check["source"] = "infirmiers", "BTS"

    lib = pd.read_parquet(ROOT / "data" / "processed" / "stock.parquet")
    lib = lib[lib["profession"] == "infirmiers-liberaux"].groupby(["year", "dep"], as_index=False)["n"].sum()
    lib = lib.assign(profession="infirmiers", source="SNDS", mode="Libéral", mode3="liberal_mixte",
                     secteur="Libéral (SNDS)", statut="prive", age_band="Ensemble", sex="Ensemble",
                     p_central=1.0, p_source="libéral ou mixte")
    return pd.concat([sal, lib], ignore_index=True), check.reset_index()


def split(stock: pd.DataFrame) -> pd.DataFrame:
    s = stock.assign(
        n_prive_sur=stock["n"].where(stock["statut"] == "prive", 0.0),
        n_public_sur=stock["n"].where(stock["statut"] == "public", 0.0),
        n_ambigu=stock["n"].where(stock["statut"] == "ambigu", 0.0),
        n_prive_central=stock["n"] * stock["p_central"])
    cols = ["n", "n_prive_sur", "n_public_sur", "n_ambigu", "n_prive_central"]
    keys = ["profession", "source", "year", "dep", "mode3"]
    by_dep = s.groupby(keys, as_index=False)[cols].sum()
    fr = s.assign(dep="FR").groupby(keys, as_index=False)[cols].sum()
    out = pd.concat([by_dep, fr], ignore_index=True)
    tot = out.copy()
    tot = tot.groupby(["profession", "source", "year", "dep"], as_index=False)[cols].sum().assign(mode3="tous")
    out = pd.concat([out, tot], ignore_index=True)
    out["part_prive_min"] = out["n_prive_sur"] / out["n"]
    out["part_prive_max"] = (out["n_prive_sur"] + out["n_ambigu"]) / out["n"]
    out["part_prive_central"] = out["n_prive_central"] / out["n"]
    out["millesime"] = out["source"].map(lambda s: MILLESIME_DREES if s != "SNDS" else
                                         "DREES infirmières libérales SNDS 2012–2023, publication 2026-07-02")
    out["millesime_part_centrale"] = MILLESIME_FINESS
    return out


def main():
    shares = finess_shares()
    stocks, checks = [], []
    for stem, (prof, src) in FILES.items():
        s, c = load_drees(stem, prof, src, shares)
        stocks.append(s), checks.append(c)
    s, c = load_nurses()
    stocks.append(s), checks.append(c)
    stock = pd.concat(stocks, ignore_index=True)
    checks = pd.concat(checks, ignore_index=True)
    checks["ecart_pct"] = 100 * (checks["sum_detailed"] / checks["national_total"] - 1)
    # kinés RPPS 2017 : Σ secteurs > « Ensemble » de 0,18 % dans le fichier source lui-même
    assert checks["ecart_pct"].abs().max() < 0.25, checks.sort_values("ecart_pct").to_string()
    OUT.mkdir(parents=True, exist_ok=True)
    stock["millesime"] = stock["source"].map(lambda s: MILLESIME_DREES)
    stock.to_parquet(OUT / "secteur_stock.parquet", index=False)
    sp = split(stock)
    sp.to_parquet(OUT / "secteur_split.parquet", index=False)
    checks.to_csv(OUT / "secteur_checks.csv", index=False)
    shares.to_csv(OUT / "secteur_finess_shares.csv")
    print(shares.round(3).to_string())
    print("check max |écart| % :", round(checks["ecart_pct"].abs().max(), 4))
    last = sp[(sp["dep"] == "FR") & (sp["mode3"] == "tous")]
    last = last[last["year"] == last.groupby("profession")["year"].transform("max")]
    print(last[["profession", "source", "year", "n", "n_prive_sur", "n_ambigu", "n_prive_central",
                "part_prive_min", "part_prive_central", "part_prive_max"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
