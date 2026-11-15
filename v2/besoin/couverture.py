"""Offre lue dans les états du jumeau et indice de couverture indexé à l'année de référence.

  offre(etat)          S[profession, territoire, année] en ETP = effectif du secteur privé (« libéral ») × activité.
                       Lit les états, ne les écrit jamais. Refuse la médecine générale et les spécialistes (O2).
  couverture(S, B)     C(T,t) = [S(T,t) / B(T,t)] / [S₀(T,ref) / B₀(T,ref)], où (S₀, B₀) est la base (sans
                       transfert, scénario de base) : un transfert actif dès `ref` se lit donc contre la même base.
  agrege(S, B, to)     C au niveau `to` = rapport des **sommes** de numérateurs et de dénominateurs, jamais une
                       moyenne de C (C n'est pas additif, B et S le sont).

Aucun indice n'est produit pour SANS_COUVERTURE, quel que soit l'appel (test « aucun C pour la MG »).
"""
from dataclasses import replace

import numpy as np

from jumeau.module import Param

from besoin.cube import Cube
from besoin.interface import PROFESSIONS

SANS_COUVERTURE = frozenset({"medecine-generale", "specialistes"})     # décision O2, registre 2026-11-15
ALIAS = {"infirmiers-liberaux": "infirmiers"}                         # table v1 : libéraux = secteur privé
ACTIVITE = Param("activite", 1.0, "ETP par professionnel", "placeholder en attendant la fiche q_p de l'axe 1",
                 "—", "supposé", "1 professionnel = 1 ETP ; s'annule dans C tant qu'il est constant dans le temps",
                 bounds=(0.0, 2.0))
_CACHE: dict = {}


def _codes(cells, sector: str):
    """(lignes gardées, professions, territoires, indice de profession, indice de territoire) pour une table de
    cellules ; mis en cache par objet (les états d'une trajectoire partagent la même table)."""
    key = (id(cells), sector)
    hit = _CACHE.get(key)
    if hit is not None and hit[0] is cells:
        return hit[1:]
    prof = cells.profession.astype(str).map(lambda p: ALIAS.get(p, p)).to_numpy()
    bad = sorted(set(prof) & SANS_COUVERTURE)
    if bad:
        raise ValueError(f"offre de {bad} : interdite (O2, aucune offre MG ni spécialiste projetée dans le besoin)")
    sec = cells.sector.astype(str).to_numpy()
    in_sector = (sec == sector) | (sec == "tous") if sector in set(sec) else np.ones(len(sec), bool)
    keep = np.flatnonzero(np.isin(prof, PROFESSIONS) & in_sector)
    pl, pi = np.unique(prof[keep], return_inverse=True)
    tl, ti = np.unique(cells.territory.astype(str).to_numpy()[keep], return_inverse=True)
    out = (keep, pl, tl, pi, ti)
    _CACHE[key] = (cells,) + out
    return out


def offre(etat: dict, years=None, sector: str = "prive", activite: float | None = None) -> Cube:
    """etat : année -> State. S en ETP, au niveau des états. Le secteur « prive » est la sortie « libéral »."""
    years = np.array(sorted(etat) if years is None else list(years))
    q = ACTIVITE.value if activite is None else float(activite)
    groups = {}                                        # table de cellules -> colonnes (années) qui la partagent
    for j, y in enumerate(years):
        cells = etat[int(y)].cells
        groups.setdefault(id(cells), (cells, []))[1].append(j)
    codes = {g: _codes(c, sector) for g, (c, _) in groups.items()}
    profs = np.unique(np.concatenate([c[1] for c in codes.values()]))
    terrs = np.unique(np.concatenate([c[2] for c in codes.values()]))
    vals = np.zeros((len(profs) * len(terrs), len(years)))
    for g, (_, cols) in groups.items():
        keep, pl, tl, pi, ti = codes[g]
        flat = np.searchsorted(profs, pl)[pi] * len(terrs) + np.searchsorted(terrs, tl)[ti]
        n = np.column_stack([etat[int(years[j])].N.sum(axis=1)[keep] for j in cols])
        part = np.zeros((len(profs) * len(terrs), len(cols)))
        np.add.at(part, flat, n)
        vals[:, cols] = part * q
    return Cube(profs, terrs, years, vals.reshape(len(profs), len(terrs), len(years)), etat[int(years[0])].level, "ETP")


def aligne(S: Cube, B: Cube) -> tuple[Cube, Cube]:
    """Mêmes professions (celles de S, hors SANS_COUVERTURE), territoires (ceux de B) et années (celles de S)."""
    bad = sorted(set(S.professions) & SANS_COUVERTURE)
    if bad:
        raise ValueError(f"couverture de {bad} : interdite (O2)")
    if S.level != B.level:
        raise ValueError(f"niveaux différents : offre {S.level}, besoin {B.level}")
    Bs = B.sel(professions=list(S.professions), years=list(S.years))
    if len(S.territories) == len(B.territories) and (S.territories == B.territories).all():
        return S, Bs
    pos = np.minimum(np.searchsorted(B.territories, S.territories), len(B.territories) - 1)
    extra = S.territories[B.territories[pos] != S.territories]
    if len(extra):
        raise ValueError(f"{len(extra)} territoires d'offre sans population, ex. {list(extra[:5])}")
    vals = np.zeros((len(S.professions), len(B.territories), len(S.years)))
    vals[:, pos] = S.values
    return replace(S, territories=B.territories, values=vals), Bs


def couverture(S: Cube, B: Cube, ref: int = 2026, S0: Cube | None = None, B0: Cube | None = None) -> Cube:
    """Indice de couverture indexé à `ref` ; (S0, B0) = base de l'indexation (par défaut S, B)."""
    S, B = aligne(S, B)
    S0, B0 = (S, B) if S0 is None and B0 is None else aligne(S if S0 is None else S0, B if B0 is None else B0)
    j = S0.y(ref)
    with np.errstate(divide="ignore", invalid="ignore"):
        base = S0.values[:, :, j] / B0.values[:, :, j]
        C = (S.values / B.values) / base[:, :, None]
    return replace(S, values=C, unit=f"indice, {ref} = 1")


def agrege(S: Cube, B: Cube, to: str, ref: int = 2026, S0: Cube | None = None, B0: Cube | None = None) -> Cube:
    """C au niveau `to` par sommes de numérateurs et de dénominateurs."""
    up = lambda c: None if c is None else c.up(to)
    return couverture(S.up(to), B.up(to), ref, up(S0), up(B0))
