"""Tables d'entrée du banc (profession, dep, sex, age_lo, year, n) par périmètre.

prive()   périmètre cible « libéral » = privé (axe 4, part privée centrale des salariés ambigus).
          Infirmiers : l'axe 4 ne donne pas l'âge des salariés privés ; on garde les infirmiers
          libéraux du RPPS (data/processed/stock.parquet), et le rapport le dit.
ancien()  ancien périmètre libéral + mixte (mode3 == liberal_mixte), pour comparaison avec K1.
"""
import pandas as pd

from jumeau.history import sector_table

PROFS = ["sages-femmes", "dentistes", "pharmaciens", "kines"]
IDE = "infirmiers-liberaux"
COLS = ["profession", "dep", "sex", "age_lo", "year", "n"]


def _ide() -> pd.DataFrame:
    s = pd.read_parquet("data/processed/stock.parquet")
    s = s[(s.profession == IDE) & ~s.dep.isin(["999", "20"])]
    return s.groupby(COLS[:-1], as_index=False).n.sum()


def prive(variant: str = "central") -> pd.DataFrame:
    t = sector_table(PROFS, variant)
    t = t[t.sector == "prive"].drop(columns="sector")
    t = t.groupby(COLS[:-1], as_index=False).n.sum()
    return pd.concat([t, _ide()], ignore_index=True)[COLS]


def ancien() -> pd.DataFrame:
    s = pd.read_parquet("data/processed/stock.parquet")
    s = s[s.profession.isin(PROFS + [IDE]) & (s.mode3 == "liberal_mixte") & ~s.dep.isin(["999", "20"])
          & ((s.profession != "kines") | (s.source == "RPPS"))]
    return s.groupby(COLS[:-1], as_index=False).n.sum()[COLS]
