"""Conteneurs du module de besoin.

Cube        valeurs [profession, territoire, année] étiquetées, au niveau `level` (com, dep, reg, nat) ; s'agrège
            vers le haut par somme exacte (B et l'offre sont additifs, C ne l'est pas : voir couverture.py).
Population  habitants [territoire, année, sexe, âge] ; Omphale 2022 au département (load), ventilable à la commune
            au prorata de la population communale (ventile), agrégeable vers le haut (up).
"""
from dataclasses import dataclass, replace
from functools import cached_property, lru_cache

import numpy as np
import pandas as pd

LEVELS = ["com", "dep", "reg", "nat"]
POP_FILE = "data/processed/population.parquet"     # Insee Omphale 2022, dep × sexe × âge quinquennal × année, 3 scénarios
GEO_FILE = "v2/data/processed/commune_geo.parquet"  # Insee, com -> dep -> reg, population communale


def mapping(frm: str, to: str, geo: pd.DataFrame | None = None) -> pd.Series:
    """Table de passage frm -> to (une ligne par unité frm). nat = "FR"."""
    g = (geo if geo is not None else geo_table()).assign(nat="FR")
    m = g[[frm, to]].drop_duplicates().set_index(frm)[to]
    if not m.index.is_unique:
        raise ValueError(f"table de passage : une unité {frm} rattachée à plusieurs {to}")
    return m


@lru_cache(maxsize=1)
def geo_table() -> pd.DataFrame:
    return pd.read_parquet(GEO_FILE, columns=["com", "dep", "reg", "population"])


def _up(values: np.ndarray, territories: np.ndarray, m: pd.Series, axis: int):
    tgt = m.reindex(territories)
    if tgt.isna().any():
        lost = territories[tgt.isna().to_numpy()]
        raise ValueError(f"{len(lost)} unités sans rattachement, ex. {list(lost[:5])}")
    labels, inv = np.unique(tgt.to_numpy().astype(str), return_inverse=True)
    shape = list(values.shape)
    shape[axis] = len(labels)
    out = np.zeros(shape)
    np.add.at(out, (slice(None),) * axis + (inv,), values)
    return out, labels


@dataclass(frozen=True)
class Cube:
    professions: np.ndarray
    territories: np.ndarray
    years: np.ndarray
    values: np.ndarray             # [profession, territoire, année]
    level: str = "dep"
    unit: str = "ETP-équivalents"

    def __post_init__(self):
        if self.values.shape != (len(self.professions), len(self.territories), len(self.years)):
            raise ValueError(f"forme {self.values.shape} ≠ étiquettes "
                             f"{(len(self.professions), len(self.territories), len(self.years))}")

    def up(self, to: str, m: pd.Series | None = None) -> "Cube":
        """Somme exacte vers le niveau `to` (on ne descend jamais : ventiler est un choix de modèle)."""
        if LEVELS.index(to) < LEVELS.index(self.level):
            raise ValueError("on n'agrège que vers le haut")
        if to == self.level:
            return self
        vals, labels = _up(self.values, self.territories, mapping(self.level, to) if m is None else m, axis=1)
        return replace(self, territories=labels, values=vals, level=to)

    def sel(self, professions=None, years=None) -> "Cube":
        pi = slice(None) if professions is None else [self.p(p) for p in professions]
        if years is None or (len(years) == len(self.years) and (np.asarray(years) == self.years).all()):
            yi = slice(None)
        else:
            yi = [self.y(y) for y in years]
        return replace(self, professions=self.professions[pi], years=self.years[yi], values=self.values[pi][:, :, yi])

    def p(self, prof: str) -> int:
        hit = np.flatnonzero(self.professions == prof)
        if not len(hit):
            raise KeyError(f"profession {prof!r} absente (cube : {list(self.professions)})")
        return int(hit[0])

    def y(self, year: int) -> int:
        hit = np.flatnonzero(self.years == year)
        if not len(hit):
            raise KeyError(f"année {year} absente ({self.years.min()}–{self.years.max()})")
        return int(hit[0])

    def to_frame(self, name="valeur") -> pd.DataFrame:
        idx = pd.MultiIndex.from_product([self.professions, self.territories, self.years],
                                         names=["profession", "territory", "year"])
        return pd.DataFrame({name: self.values.ravel()}, index=idx).reset_index()


@dataclass(frozen=True)
class Population:
    territories: np.ndarray
    years: np.ndarray
    sexes: np.ndarray
    ages: np.ndarray               # bornes basses des tranches
    P: np.ndarray                  # [territoire, année, sexe, âge], habitants
    level: str = "dep"
    scenario: str = "central"
    source: str = "Insee, projections Omphale 2022 (data/processed/population.parquet)"

    @classmethod
    def load(cls, scenario: str = "central") -> "Population":
        return _load(scenario)

    def total(self) -> np.ndarray:
        """Habitants [territoire, année]."""
        return self._total

    @cached_property
    def _total(self) -> np.ndarray:
        return self.P.sum(axis=(2, 3))

    def years_index(self, years) -> np.ndarray:
        pos = np.searchsorted(self.years, years)
        if (pos >= len(self.years)).any() or (self.years[np.minimum(pos, len(self.years) - 1)] != years).any():
            raise KeyError(f"années hors de la projection de population ({self.years.min()}–{self.years.max()})")
        return pos

    def up(self, to: str, m: pd.Series | None = None) -> "Population":
        if to == self.level:
            return self
        vals, labels = _up(self.P, self.territories, mapping(self.level, to) if m is None else m, axis=0)
        return replace(self, territories=labels, P=vals, level=to)

    def ventile(self, geo: pd.DataFrame | None = None) -> "Population":
        """Population communale = population départementale × part communale (recensement, figée dans le temps).
        Hypothèse (supposé) : la structure par âge et sexe d'une commune est celle de son département. Somme exacte
        par département, par construction ; seulement pour des tests et des scénarios, pas une projection communale."""
        g = geo if geo is not None else geo_table()
        g = g[g.dep.isin(self.territories) & (g.population > 0)]
        w = (g.population / g.groupby("dep").population.transform("sum")).to_numpy()
        di = np.searchsorted(self.territories, g.dep.to_numpy())
        return replace(self, territories=g.com.to_numpy(), P=self.P[di] * w[:, None, None, None], level="com",
                       source=self.source + " ventilée au prorata de la population communale (commune_geo)")


@lru_cache(maxsize=4)
def _load(scenario: str) -> Population:
    p = pd.read_parquet(POP_FILE)
    p = p[p.scenario == scenario]
    if p.empty:
        raise KeyError(f"scénario de population {scenario!r} inconnu")
    terr, years = np.sort(p.dep.unique()), np.sort(p.year.unique())
    sexes, ages = np.sort(p.sex.unique()), np.sort(p.age_lo.unique())
    P = np.zeros((len(terr), len(years), len(sexes), len(ages)))
    P[np.searchsorted(terr, p.dep), np.searchsorted(years, p.year), np.searchsorted(sexes, p.sex),
      np.searchsorted(ages, p.age_lo)] = p["pop"].to_numpy()
    return Population(terr, years, sexes, ages, P, "dep", scenario)
