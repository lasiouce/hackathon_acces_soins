"""Recours, offre observée et morbidité au département, pour M2a, M2b, M3 et les passages P-B2, P-B3, P-B5.

Pas un estimateur (rien n'est enregistré ici) : des lecteurs de données, tous à la maille département.
  recours(p, years)     R = file active moyenne × effectif (data.ameli.fr, patientèle et démographie, ODbL ;
                        amendement A1.1). Lignes « 999 » (régions) et région « 99 » (France) exclues.
  effectif_ameli(p, …)  effectif libéral data.ameli.fr (tout âge, tout sexe)
  offre_obs(p, years)   effectif libéral observé du jumeau (secteur privé, état historique), somme âge × sexe
  pstd(p, pop, years)   population standardisée Σ pop · ω (poids APL, M1), sans niveau
  table(p, pop, years)  [département] R_std, A, R, B₁, N moyennés sur les années (P-B2, M2a, M2b)
  morbidite(year)       indice de morbidité standardisé par âge et sexe (cartographie des pathologies, ODbL) :
                        part observée des consommants avec au moins une pathologie, un traitement chronique, une
                        maternité ou une hospitalisation repérés, rapportée à la part attendue aux taux nationaux
Les tables ODbL ne sont jamais commitées (décision du 2026-11-15) : elles sont lues dans v2/data/odbl/besoin/.
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from besoin.cube import Population
from besoin.estimateurs.m1 import CODE, omega_apl

ODBL = "v2/data/odbl/besoin/"
PROF_AMELI = {"infirmiers": "IDE", "kines": "MK", "dentistes": "CD", "sages-femmes": "SF"}
TOP_TOTAL, TOP_AUCUNE = "POP_TOT_IND", "POP_TOT_ABS"      # consommants tous régimes ; sans pathologie repérée


def _dep(d: pd.DataFrame) -> pd.DataFrame:
    return d[(d.departement != "999") & (d.region != "99")]


@lru_cache(maxsize=1)
def _patientele() -> pd.DataFrame:
    return _dep(pd.read_parquet(ODBL + "ameli_patientele.parquet"))


@lru_cache(maxsize=1)
def _demographie() -> pd.DataFrame:
    d = pd.read_parquet(ODBL + "ameli_demographie.parquet",
                        columns=["annee", "prof", "region", "departement", "classe_age", "libelle_sexe", "effectif"])
    d = _dep(d)
    return d[(d.classe_age == "tout_age") & (d.libelle_sexe == "tout sexe") & d.prof.notna()]


def effectif_ameli(prof: str, years) -> pd.DataFrame:
    """[département × année] effectif libéral data.ameli.fr."""
    d = _demographie()
    d = d[(d.prof == PROF_AMELI[prof]) & d.annee.isin(list(years))]
    return d.pivot_table(index="departement", columns="annee", values="effectif", aggfunc="sum")


def recours(prof: str, years) -> pd.DataFrame:
    """[département × année] R = file active moyenne × effectif ; NaN si la file active est masquée."""
    p = _patientele()
    p = p[(p.prof == PROF_AMELI[prof]) & p.annee.isin(list(years))]
    fa = p.pivot_table(index="departement", columns="annee", values="patients_uniques_moy", aggfunc="first")
    return (fa.astype(float) * effectif_ameli(prof, years)).reindex(fa.index)


@lru_cache(maxsize=8)
def _secteur(prof: str) -> pd.DataFrame:
    from jumeau.history import sector_table
    t = sector_table([prof])
    return t[t.sector == "prive"].groupby(["dep", "year"]).n.sum().unstack()


def offre_obs(prof: str, years) -> pd.DataFrame:
    """[département × année] effectif libéral (secteur privé) observé du jumeau."""
    return _secteur(prof).reindex(columns=list(years))


def pstd(prof: str, pop: Population, years) -> pd.DataFrame:
    """[département × année] population standardisée Σ pop · ω (poids APL de M1)."""
    w = omega_apl(prof, pop.sexes, pop.ages) if prof in CODE else np.ones((len(pop.sexes), len(pop.ages)))
    P = pop.P[:, pop.years_index(list(years))]
    return pd.DataFrame(np.einsum("tysa,sa->ty", P, w), index=pop.territories, columns=list(years))


@lru_cache(maxsize=1)
def _pathologies() -> pd.DataFrame:
    d = pd.read_parquet(ODBL + "ameli_pathologies_effectifs.parquet",
                        columns=["annee", "top", "cla_age_5", "sexe", "region", "departement", "ntop", "npop"])
    return d


def morbidite(year: int = 2024) -> pd.Series:
    """Indice standardisé (1 = France) de la part des consommants avec au moins un repérage de la cartographie."""
    d = _pathologies()
    d = d[(d.annee == year) & d.top.isin([TOP_TOTAL, TOP_AUCUNE]) & (d.cla_age_5 != "tsage") & d.sexe.isin(["1", "2"])]
    nat = d[d.region == "99"]
    loc = _dep(d)
    k = ["cla_age_5", "sexe"]
    tn = nat.pivot_table(index=k, columns="top", values="ntop", aggfunc="sum")
    taux = (tn[TOP_TOTAL] - tn[TOP_AUCUNE]) / nat.pivot_table(index=k, columns="top", values="npop",
                                                              aggfunc="sum")[TOP_TOTAL]
    tl = loc.pivot_table(index=["departement"] + k, columns="top", values="ntop", aggfunc="sum")
    npop = loc[loc.top == TOP_TOTAL].set_index(["departement"] + k).npop
    obs = (tl[TOP_TOTAL] - tl[TOP_AUCUNE]).groupby("departement").sum()
    att = (npop * taux.reindex(npop.droplevel(0).index).to_numpy()).groupby("departement").sum()
    return (obs / att).rename("morbidite")


def table(prof, pop, years, offre="jumeau"):
    """DataFrame [département] : R_std, A, et les sommes utiles (R, B₁, N) ; jointure des trois sources."""
    yrs = [y for y in years if y in offre_obs(prof, years).dropna(axis=1, how="all").columns] if offre == "jumeau" \
        else list(years)
    R = recours(prof, years)[list(years)]
    Bs = pstd(prof, pop, years)
    N = offre_obs(prof, yrs) if offre == "jumeau" else effectif_ameli(prof, yrs)
    d = sorted(set(R.dropna().index) & set(Bs.index) & set(N.dropna().index))
    r = (R.loc[d] / Bs.loc[d, list(years)]).mean(axis=1)
    nat = (R.loc[d].sum() / Bs.loc[d, list(years)].sum()).mean()
    A = (1e5 * N.loc[d, yrs] / Bs.loc[d, yrs]).mean(axis=1)
    return pd.DataFrame({"R_std": r / nat, "A": A, "R": R.loc[d].mean(axis=1), "B1": Bs.loc[d, list(years)].mean(axis=1),
                         "N": N.loc[d, yrs].mean(axis=1)}), yrs
