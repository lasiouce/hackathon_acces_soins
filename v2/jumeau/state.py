"""L'état du jumeau.

N[cellule, âge] avec cellule = (profession, secteur, territoire, sexe) ; `level` dit ce qu'est le
territoire (com, dep, reg, nat). Le secteur est un axe de l'état, pas un filtre : un entrant bloqué
ou une transition privé <-> public change de cellule au lieu de disparaître. Les valeurs de secteur
dépendent de ce que la donnée sépare (le RPPS ne sépare pas public et privé chez les salariés,
axe 4) ; `ensure_sector` crée des cellules vides pour une destination encore non observée.
Le vivier en formation (`pool`) est national : (profession, année d'étude) -> inscrits.
Geography relie commune -> département -> région -> national et agrège sans perte.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

AXES = ["profession", "sector", "territory", "sex"]
LEVELS = ["com", "dep", "reg", "nat"]


@dataclass
class State:
    cells: pd.DataFrame            # colonnes AXES, index 0..n-1
    ages: np.ndarray
    N: np.ndarray                  # [cellule, âge], float
    year: int
    level: str = "dep"
    pool: pd.Series | None = None
    _key: dict = field(default=None, repr=False)

    @classmethod
    def from_table(cls, t: pd.DataFrame, year: int, level: str = "dep", sector: str = "tous") -> "State":
        """t : profession, <level>, sex, age_lo, year, n (+ sector). Les cellules sont celles de toute la
        table (vides si absentes à `year`), dans l'ordre trié des axes, comme sante.model._cube."""
        t = t.rename(columns={level: "territory"})
        if "sector" not in t:
            t = t.assign(sector=sector)
        ages = np.sort(t.age_lo.unique())
        cells = t[AXES].drop_duplicates().sort_values(AXES).reset_index(drop=True)
        wide = (t[t.year == year].pivot_table(index=AXES, columns="age_lo", values="n", aggfunc="sum", fill_value=0)
                .reindex(index=pd.MultiIndex.from_frame(cells), columns=ages, fill_value=0))
        return cls(cells, ages, wide.to_numpy(dtype=float), year, level)

    def copy(self) -> "State":
        return State(self.cells, self.ages, self.N.copy(), self.year, self.level,
                     None if self.pool is None else self.pool.copy(), self._key)

    def index(self, keys: pd.DataFrame) -> np.ndarray:
        """Indices des cellules pour des lignes (profession, sector, territory, sex) ; -1 si absente."""
        if self._key is None:
            self._key = {k: i for i, k in enumerate(self.cells.itertuples(index=False, name=None))}
        return np.array([self._key.get(k, -1) for k in keys[AXES].itertuples(index=False, name=None)])

    def ensure_sector(self, sector: str) -> "State":
        """Ajoute, pour chaque (profession, territoire, sexe), une cellule vide du secteur donné."""
        new = self.cells.assign(sector=sector).drop_duplicates()
        new = new[self.index(new) < 0]
        if new.empty:
            return self
        cells = pd.concat([self.cells, new], ignore_index=True)
        N = np.vstack([self.N, np.zeros((len(new), len(self.ages)))])
        return State(cells, self.ages, N, self.year, self.level, self.pool)

    def to_frame(self) -> pd.DataFrame:
        """Format long : AXES + age_lo + year + n."""
        return (pd.DataFrame(self.N, columns=self.ages).assign(**self.cells, year=self.year)
                .melt(id_vars=AXES + ["year"], var_name="age_lo", value_name="n"))

    def total(self, by=("profession", "territory")) -> pd.Series:
        return pd.Series(self.N.sum(axis=1)).groupby([self.cells[c] for c in by]).sum()


@dataclass
class Geography:
    """Table de passage commune -> dep -> reg -> nat (une ligne par commune)."""
    table: pd.DataFrame            # colonnes com, dep, reg, nat

    @classmethod
    def from_data(cls) -> "Geography":
        """Communes CartoSanté (com, dep) ; région depuis le RPPS (dep -> region, millésime 2026)."""
        com = pd.read_parquet("data/processed/stock_commune.parquet", columns=["com", "dep"]).drop_duplicates()
        reg = pd.read_parquet("data/processed/stock.parquet", columns=["dep", "region"]).drop_duplicates()
        g = com.merge(reg.rename(columns={"region": "reg"}), on="dep", how="left").assign(nat="FR")
        return cls(g.reset_index(drop=True))

    def up(self, frame: pd.DataFrame, to: str, frm: str = "com") -> pd.DataFrame:
        """Agrège un format long (colonne `territory` au niveau `frm`) au niveau `to`. Somme exacte."""
        if LEVELS.index(to) < LEVELS.index(frm):
            raise ValueError("on n'agrège que vers le haut ; descendre demande un module de ventilation")
        m = self.table[[frm, to]].drop_duplicates().set_index(frm)[to]
        if not m.index.is_unique:
            raise ValueError(f"table de passage : une unité {frm} rattachée à plusieurs {to}")
        out = frame.assign(territory=frame["territory"].map(m))
        lost = frame.loc[out.territory.isna(), "territory"].unique()
        if len(lost):
            raise ValueError(f"{len(lost)} unités {frm} sans rattachement {to}, ex. {list(lost[:5])}")
        keys = [c for c in frame.columns if c != "n"]
        return out.groupby(keys, as_index=False, dropna=False)["n"].sum()
