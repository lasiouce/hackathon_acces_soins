"""Loaders: raw DREES / Insee Excel files -> tidy parquet in data/processed/.

Run: uv run python -m sante.load
Outputs
  stock.parquet       profession, year, dep, dep_name, region, mode, mode3, age_band, age_lo, age_hi, sex, specialty, n
  population.parquet  scenario, year, dep, dep_name, sex, age_lo, age_hi, pop
  checks.csv          per profession x year: sum of detailed cells vs the file's own France total
Sources: DREES "La démographie des professionnels de santé depuis 2012" (data.drees, 2026-07-02);
         Insee Omphale 2022 "tableaux détaillés départements" (page 7747107).
"""
import re
import unicodedata
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/processed")

# file stem -> (profession, source register)
DREES = {
    "medecins_rpps_2012_2026": ("medecins", "RPPS"),
    "chirurgiens_dentistes_rpps_2012_2026": ("dentistes", "RPPS"),
    "pharmaciens_rpps_2012_2026": ("pharmaciens", "RPPS"),
    "sages_femmes_rpps_2012_2026": ("sages-femmes", "RPPS"),
    "kinesitherapeutes_rpps_2017_2026": ("kines", "RPPS"),
    "kinesitherapeutes_adeli_2012_2016": ("kines", "ADELI"),
    "infirmieres_liberales_snds_2012_2023": ("infirmiers-liberaux", "SNDS"),
}

# exercice label -> harmonised 3-level mode (ADELI merges libéral and mixte)
MODE3 = {"Libéral": "liberal_mixte", "Mixte": "liberal_mixte", "Libéraux ou mixtes": "liberal_mixte",
         "Salarié hospitalier": "salarie_hosp", "Salariés hospitaliers": "salarie_hosp",
         "Autre Salarié": "autre_salarie", "Autres salariés": "autre_salarie"}


def code_label(s: str) -> tuple[str, str]:
    """'002 -Aisne' / '76 - Occitanie' / '01-Ain' -> ('002', 'Aisne')."""
    m = re.match(r"^\s*([0-9A-Za-z]+)\s*-\s*(.*)$", str(s))
    return (m.group(1), m.group(2).strip()) if m else ("", str(s).strip())


def is_total(s) -> bool:
    return "ensemble" in str(s).lower()


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"^(la|le|les)\s+", "", s.strip())   # "La Réunion" vs "Réunion"
    return re.sub(r"[^a-z]", "", s.replace("saint", "st"))


def dep_code(raw_code: str) -> str:
    """Normalise to Insee COG: '002' -> '02', '02A' -> '2A', '971' stays."""
    c = raw_code.upper()
    if len(c) == 3 and c[0] == "0":
        c = c[1:]
    return {"0A": "2A", "0B": "2B"}.get(c, c)


def age_bounds(label: str) -> tuple[int, int | None]:
    """'entre 30 et 34 ans' -> (30, 34); 'moins de 25 ans' -> (0, 24); '65 ans et plus' -> (65, None)."""
    label = label.lower()
    nums = [int(x) for x in re.findall(r"\d+", label)]
    if "moins" in label:
        return 0, nums[-1] - 1
    if "plus" in label:
        return nums[-1], None
    return nums[-2], nums[-1]


def load_drees(stem: str, profession: str, source: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_excel(RAW / "drees" / f"{stem}.xlsx", sheet_name="Effectifs", engine="calamine")
    df.columns = [unicodedata.normalize("NFC", str(c)).strip() for c in df.columns]
    years = [c for c in df.columns if c.startswith("effectif_")]
    dims = [c for c in df.columns if c not in years and not c.startswith("...") and not c.startswith("Unnamed")]
    df = df[dims + years]
    tot = df[dims].apply(lambda col: col.map(is_total))

    # national total row: every dimension at its aggregate level (territoire = France entière)
    nat = df[tot.drop(columns=["territoire"], errors="ignore").all(axis=1)]
    if "territoire" in df:
        nat = nat[nat["territoire"].astype(str).str.startswith("0")]
    national = nat[years].iloc[0]

    # detailed cells: every dimension detailed, except activity sector kept at its aggregate
    keep = pd.Series(True, index=df.index)
    for d in dims:
        if d == "territoire":
            keep &= ~df[d].astype(str).str.startswith("0")
        elif d == "secteur_activite":
            keep &= tot[d]
        elif d == "specialites_agregees":
            keep &= ~tot[d]
        else:
            keep &= ~tot[d]
    det = df[keep]

    long = det.melt(id_vars=dims, value_vars=years, var_name="year", value_name="n")
    long["year"] = long["year"].str.slice(-4).astype(int)
    dep = long["departement"].map(code_label)
    reg = long["region"].map(code_label)
    out = pd.DataFrame({
        "profession": profession, "source": source, "year": long["year"],
        "dep": [dep_code(c) for c, _ in dep], "dep_name": [n for _, n in dep],
        "region": [c.zfill(2) for c, _ in reg],
        "mode": long["exercice"].map(lambda s: code_label(s)[1]) if "exercice" in long else "Libéral",
        "age_band": long["tranche_age"].map(lambda s: code_label(s)[1]),
        "sex": long["sexe"].map(lambda s: {"1": "H", "2": "F"}[code_label(s)[0]]),
        "specialty": long["specialites"].map(lambda s: code_label(s)[1]) if "specialites" in long else "",
        "n": long["n"].fillna(0).astype(float),
    })
    out["mode3"] = out["mode"].map(MODE3)
    bounds = out["age_band"].map(age_bounds)
    out["age_lo"] = [b[0] for b in bounds]
    out["age_hi"] = pd.array([b[1] for b in bounds], dtype="Int64")

    check = out.groupby("year")["n"].sum().rename("sum_detailed").to_frame()
    check["national_total"] = [national[f"effectif_{y}"] for y in check.index]
    check["profession"], check["source"] = profession, source
    return out, check.reset_index()


def load_omphale(dep_names: pd.Series) -> pd.DataFrame:
    by_name = {norm_name(n): c for c, n in dep_names.items()}
    frames = []
    for scen, stem in [("central", "Central"), ("pop_basse", "Pop_basse"), ("pop_haute", "Pop_haute")]:
        df = pd.read_excel(RAW / "omphale" / f"omphale_2022_{stem}.xlsx", sheet_name="Population",
                           skiprows=5, engine="calamine")
        years = [c for c in df.columns if str(c).startswith("POP_")]
        long = df.melt(id_vars=["ZONE", "SEXE", "TRAGE"], value_vars=years, var_name="year", value_name="pop")
        lo_hi = long["TRAGE"].str.extract(r"\[(\d+);(\d*)")
        frames.append(pd.DataFrame({
            "scenario": scen, "year": long["year"].str.slice(-4).astype(int),
            "dep": long["ZONE"].map(lambda z: by_name.get(norm_name(z))), "dep_name": long["ZONE"],
            "sex": long["SEXE"].map({1: "H", 2: "F"}),
            "age_lo": lo_hi[0].astype(int),
            "age_hi": pd.to_numeric(lo_hi[1], errors="coerce").sub(1).astype("Int64"),
            "pop": long["pop"].astype(float),
        }))
    pop = pd.concat(frames, ignore_index=True)
    missing = sorted(pop.loc[pop["dep"].isna(), "dep_name"].unique())
    if missing:
        raise ValueError(f"Omphale zones with no DREES département code: {missing}")
    return pop


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stocks, checks = [], []
    for stem, (prof, src) in DREES.items():
        s, c = load_drees(stem, prof, src)
        stocks.append(s)
        checks.append(c)
        print(f"{prof:20s} {src:5s} rows={len(s):>8,}  years={s.year.min()}-{s.year.max()}  dép={s.dep.nunique()}")
    stock = pd.concat(stocks, ignore_index=True)
    stock.to_parquet(OUT / "stock.parquet", index=False)

    check = pd.concat(checks, ignore_index=True)
    check["gap_pct"] = 100 * (check["sum_detailed"] / check["national_total"] - 1)
    check.to_csv(OUT / "checks.csv", index=False)

    # every (code, name) spelling seen across files: médecins mislabels 62 as "Nord-Pas-de-Calais"
    names = stock.drop_duplicates(["dep", "dep_name"]).set_index("dep_name")["dep"]
    names = pd.Series(names.index, index=names.values)
    pop = load_omphale(names)
    # one display name per département, from the non-médecins files
    clean = stock[stock.profession != "medecins"].drop_duplicates("dep").set_index("dep")["dep_name"]
    stock["dep_name"] = stock["dep"].map(clean).fillna(stock["dep_name"])
    stock.to_parquet(OUT / "stock.parquet", index=False)
    pop.to_parquet(OUT / "population.parquet", index=False)
    print(f"population           rows={len(pop):>8,}  dép={pop.dep.nunique()}  scenarios={pop.scenario.nunique()}")
    print(f"max |gap| detailed vs national total: {check.gap_pct.abs().max():.3f} %")


if __name__ == "__main__":
    main()
