"""GBM de P-B5, servi comme **prédicteur du recours seulement**, jamais comme besoin (décision du 2026-11-15,
option (a) choisie par l'utilisateur·rice).

Pourquoi pas un besoin : le gain du GBM sur M1 suit la croissance de l'offre 2016 → 2025 (corrélation de 0,54 à 0,71
entre sa cible et la croissance de l'effectif, diagnostic a posteriori de P-B5). Servi comme besoin, il rendrait B
dépendant de l'offre, contraire au cas limite « offre nulle ». La classe n'est donc pas une NeedEstimator et n'est
pas enregistrée : aucun chemin de besoin_api ne peut la choisir.

  QUALIFIE   professions où le GBM bat M1 au-delà de l'IC à 98,75 % (P-B5) : IDE, CD, SF ; pas les kinés
  H          horizon validé : 9 ans (2016 → 2025) ; aucun autre horizon n'est servi
  predit(p, origine)  recours départemental R̂(origine + 9) = R̂_M1 · exp(ŷ), modèle appris sur toutes les
             paires 2016 → 2025, hyperparamètres gelés de P-B5 ; unité : patients (file active × effectif)
Lit les estimations Insee (`v2/data/raw/insee/`, hors dépôt) et les tables ODbL : scikit-learn, xlrd, openpyxl requis.
"""
from functools import lru_cache

import numpy as np
import pandas as pd

QUALIFIE = frozenset({"infirmiers", "dentistes", "sages-femmes"})
H = 9
STATUT = ("prédicteur du recours (patients), validé à h = 9 sur 2016 → 2025 par P-B5 ; jamais un besoin ; "
          "son gain suit la croissance de l'offre")


def _verifie(prof: str):
    if prof not in QUALIFIE:
        raise ValueError(f"GBM du recours : {prof!r} non qualifié par P-B5 (qualifiés : {sorted(QUALIFIE)})")


@lru_cache(maxsize=8)
def _pop(year: int):
    from besoin.cube import Population
    from besoin.validation.pb5 import population
    return population(year, Population.load())


@lru_cache(maxsize=4)
def modele(prof: str):
    """HistGradientBoostingRegressor appris sur toutes les paires départementales 2016 → 2025."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from besoin.validation import pb5
    _verifie(prof)
    pops = {y: _pop(y) for y in (pb5.O, pb5.CIBLE)}
    t = pb5.predictions(prof, pops, pb5.CIBLE)
    X, _ = pb5.covariables(prof, t, pops, pb5.CIBLE)
    y = np.log(t.R / t.M1).to_numpy()
    return HistGradientBoostingRegressor(**pb5.GBM).fit(X.to_numpy(), y), list(X.columns)


def predit(prof: str, origine: int = 2025) -> pd.DataFrame:
    """[département] R0 (recours observé à l'origine), M1 (R̂ par l'âge), GBM (R̂ corrigé), à origine + 9."""
    from besoin.validation import pb5
    _verifie(prof)
    m, cols = modele(prof)
    cible = origine + H
    pops = {origine: _pop(origine), cible: _pop(cible)}
    t = pb5.predictions(prof, pops, cible, o=origine)
    X, _ = pb5.covariables(prof, t, pops, cible, o=origine)
    out = t[["R0", "M1"]].assign(GBM=t.M1 * np.exp(m.predict(X[cols].to_numpy())))
    out.attrs.update(profession=prof, origine=origine, cible=cible, unite="patients", statut=STATUT)
    return out
