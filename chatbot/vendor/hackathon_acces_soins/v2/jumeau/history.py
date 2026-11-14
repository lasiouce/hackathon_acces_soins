"""Historique observé que les modules lisent dans fit(), et calibrage stock-flux partagé.

Le calibrage des taux (rétention nette s, entrées nettes I, pente) réutilise sante.model.fit_rates
(v1, figée) sans la recopier : les modules `sorties` et `entrees` en prennent chacun leur part.
Il est fait par secteur, puis aligné sur les cellules de l'état.

Une cellule sans historique (ex. secteur public créé vide pour recevoir des entrants bloqués) n'a
pas de taux propres. Règle de repli (`supposé`) : elle prend la rétention s de la cellule de même
(profession, territoire, sexe) dans le secteur `repli` (privé par défaut), et aucune entrée propre
(I = 0, pente = 0) : elle ne reçoit que les flux qu'on lui envoie, et ses membres sortent au même
rythme qu'ils l'auraient fait dans leur secteur d'origine. Sans cellule de repli : erreur.
Les cellules en repli sont comptées dans hist.borrowed.

sector_table() construit l'historique par secteur (privé / public) à partir du travail de l'axe 4
(v2/data/processed/secteur_stock.parquet) : les salariés « ambigus » sont répartis par leur part
privée (centrale, minimale ou maximale).
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from sante.model import KEYS, _cube, fit_rates
from jumeau.state import AXES

SOURCE_RPPS = "DREES, RPPS (data/processed/stock.parquet)"
SOURCE_SECTEUR = "axe 4, v2/data/processed/secteur_stock.parquet (DREES RPPS 2012–2026 × secteur d'activité, FINESS)"


@dataclass
class History:
    table: pd.DataFrame                      # profession, <level>, sex, age_lo, year, n (+ sector), années <= origine
    origin: int
    fit_years: tuple
    level: str = "dep"
    options: dict = field(default_factory=dict)   # shrink, inflow_trend, inflow_recent, repli
    borrowed: int = 0
    _cache: dict = field(default_factory=dict, repr=False)


def stock_flow_rates(hist: History, state) -> tuple:
    """(s, inflow, slope), chacun [cellule de l'état, âge]."""
    key = ("rates", len(state.cells))
    if key in hist._cache:
        return hist._cache[key]
    o = hist.options
    t = hist.table.rename(columns={hist.level: "dep"})
    if "sector" not in t:
        t = t.assign(sector=state.cells.sector.iloc[0])
    S, I, P = (np.full_like(state.N, np.nan) for _ in range(3))
    for sector, ts in t.groupby("sector"):
        s, inflow, slope = fit_rates(ts[KEYS + ["age_lo", "year", "n"]], hist.fit_years, shrink=o.get("shrink"),
                                     inflow_trend=o.get("inflow_trend", False), inflow_recent=o.get("inflow_recent"))
        _, cells, ages, _ = _cube(ts)
        if not np.array_equal(ages, state.ages):
            raise ValueError("tranches d'âge de l'historique ≠ celles de l'état")
        idx = state.index(cells.rename(columns={"dep": "territory"}).assign(sector=sector)[AXES])
        ok = idx >= 0
        S[idx[ok]], I[idx[ok]], P[idx[ok]] = s[ok], inflow[ok], slope[ok]
    miss = np.flatnonzero(np.isnan(S[:, 0]))
    if miss.size:
        donor = state.index(state.cells.iloc[miss].assign(sector=o.get("repli", "prive")))
        if (donor < 0).any() or np.isnan(S[donor[donor >= 0], 0]).any():
            bad = state.cells.iloc[miss[donor < 0]].head(3).to_dict("records")
            raise ValueError(f"cellules sans historique ni cellule de repli, ex. {bad}")
        S[miss], I[miss], P[miss] = S[donor], 0.0, 0.0
    hist.borrowed = int(miss.size)
    hist._cache[key] = (S, I, P)
    return hist._cache[key]


INFIRMIERS = "v2/data/processed/infirmiers_secteur_age_sexe.parquet"
SOURCE_INFIRMIERS = ("axe 4, v2/data/build_infirmiers.py : libéraux SNDS (dep × âge × sexe) + salariés BTS DREES/Insee "
                     "(dep × secteur) croisés avec âge × sexe sous indépendance (H_ind)")


def infirmiers_table() -> pd.DataFrame:
    """Infirmiers par secteur (prive / public) × dep × âge × sexe, 2013-2023 (axe 4). Les libéraux sont tous privés ;
    les salariés sont ventilés par le BTS. 2012 est exclu : les salariés n'y sont pas observés (BTS à partir de 2013)."""
    d = pd.read_parquet(INFIRMIERS)
    d = d[(d.year >= 2013) & ~d.dep.isin(["999", "20"])]
    return (d.assign(profession="infirmiers", sector=d.statut)
            .groupby(["profession", "sector", "dep", "sex", "age_lo", "year"], as_index=False).n.sum())


def sector_table(professions, variant: str = "central") -> pd.DataFrame:
    """profession, sector (prive / public), dep, sex, age_lo, year, n. variant : central | min | max
    (part privée des salariés ambigus). Kinés : RPPS seul (ADELI rompt la série, règle v1).
    Infirmiers : table de l'axe 4 (infirmiers_table) ; le secteur y est déjà tranché par le BTS, `variant` est sans
    effet pour eux."""
    professions = list(professions)
    parts = []
    if "infirmiers" in professions:
        parts.append(infirmiers_table())
    rest = [p for p in professions if p != "infirmiers"]
    if rest:
        d = pd.read_parquet("v2/data/processed/secteur_stock.parquet")
        d = d[d.profession.isin(rest) & (d.age_band != "Ensemble") & (d.sex != "Ensemble")
              & ~d.dep.isin(["999", "20"]) & ((d.profession != "kines") | (d.source == "RPPS"))]
        p = {"central": d.p_central, "min": (d.statut == "prive").astype(float),
             "max": (d.statut != "public").astype(float)}[variant]
        lo = d.age_band.str.lower().str.extract(r"(\d+)")[0].astype(int)
        lo = lo.where(~d.age_band.str.lower().str.startswith("moins"), 0)
        base = d.assign(age_lo=lo)[["profession", "dep", "sex", "age_lo", "year"]]
        t = pd.concat([base.assign(sector="prive", n=d.n * p), base.assign(sector="public", n=d.n * (1 - p))])
        parts.append(t.groupby(["profession", "sector", "dep", "sex", "age_lo", "year"], as_index=False).n.sum())
    return pd.concat(parts, ignore_index=True)
