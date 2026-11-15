"""M1 : recours standardisé par âge et sexe (dérivation du 2026-11-15, §6).

B₁(p, T, t) = r̄_p · Σ_{a,s} pop(T, t, a, s) · ω(p, a, s), en ETP-équivalents.
  ω   forme relative du recours : poids de standardisation des fichiers APL de la DREES (DCIR, 19 tranches
      quinquennales jusqu'à 90+), fiche param-besoin-poids-age-apl. Colonne 2024 (DCIR 2022) pour IDE, CD, SF ;
      2023 (DCIR 2021) pour les MK, faute de colonne 2024 publiée. SF : poids sur les femmes, 0 pour les hommes.
      Omphale a deux tranches au-delà de 90 ans (90–94, 95+) : toutes deux prennent le poids « 90 et plus ».
  r̄   niveau : en attendant Open DAMIR (axe 4), offre nationale / population standardisée nationale à l'année de
      référence (supposé). Il s'annule dans C, comme pour M0.
Pharmaciens, médecine générale, spécialistes : pas de poids APL. Leur forme viendra du profil Open DAMIR
(param-besoin-profil-damir) ; d'ici là M1 ne les sert pas (ils sont absents du cube, jamais remplacés par M0).

`omega` peut être passé au constructeur ({profession: tableau [sexe, âge] aligné sur la population}) : c'est ce que
font les tests de cas limites (profil plat ⇒ M1 = M0).
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from jumeau.module import Param

from besoin.cube import Cube, Population
from besoin.interface import NeedEstimator, register

APL = "v2/data/processed/besoin/apl_parametres.parquet"
CODE = {"infirmiers": "IDE", "kines": "MK", "dentistes": "CD", "sages-femmes": "SF"}
COLONNE = {"infirmiers": 2024, "kines": 2023, "dentistes": 2024, "sages-femmes": 2024}
FEMMES = {"sages-femmes"}


@lru_cache(maxsize=1)
def poids_apl() -> pd.DataFrame:
    """Poids d'âge publiés : colonnes prof (code DREES), annee, age_lo (borne basse de la tranche), omega."""
    d = pd.read_parquet(APL)
    d = d[d.bloc == "poids_age"].copy()
    lo = d.cle.str.extract(r"(\d+)")[0].astype(int)
    d["age_lo"] = np.where(d.cle.str.startswith("Moins"), 0, lo)
    return d.rename(columns={"valeur": "omega"})[["prof", "annee", "age_lo", "omega"]]


def omega_apl(prof: str, sexes, ages) -> np.ndarray:
    """ω [sexe, âge] aligné sur une Population ; tranches au-delà de 90 ans = poids « 90 et plus »."""
    w = poids_apl()
    w = w[(w.prof == CODE[prof]) & (w.annee == COLONNE[prof])].set_index("age_lo").omega
    if len(w) != 19:
        raise ValueError(f"poids APL {prof} {COLONNE[prof]} : {len(w)} tranches au lieu de 19")
    row = w.reindex(np.minimum(np.asarray(ages), 90)).to_numpy()
    if np.isnan(row).any():
        raise ValueError(f"poids APL {prof} : tranches d'âge non appariées {list(np.asarray(ages)[np.isnan(row)])}")
    out = np.tile(row, (len(sexes), 1))
    if prof in FEMMES:
        out[np.asarray(sexes) != "F"] = 0.0
    return out


@register
class M1(NeedEstimator):
    name = "M1"
    norme = ("besoin = recours national par âge et sexe de l'année de base (DCIR, poids APL de la DREES), appliqué "
             "à la pyramide de chaque territoire ; le recours y est pris pour le besoin")
    assumptions = ("Chaque habitant compte selon le recours moyen de sa tranche d'âge (et de son sexe pour les "
                   "sages-femmes), figé à l'année de base. Le recours est censuré par l'offre : là où elle manque, "
                   "ce besoin est trop bas (dérivation §2.3).")
    professions = tuple(CODE)
    params = (
        Param("omega", "poids APL par tranche quinquennale (19 tranches, 90+)", "sans dimension",
              "DREES, jeu 530 APL, onglet « Paramètres » (fiche param-besoin-poids-age-apl)",
              "DCIR 2022 (colonne 2024) ; MK : DCIR 2021 (colonne 2023)", "mesuré",
              "forme du profil seulement ; SF sur la population féminine"),
        Param("r_bar", None, "ETP par habitant standardisé",
              "offre nationale / population standardisée nationale à l'année de référence, ajusté par fit() ; "
              "niveau Open DAMIR en attente (axe 4)", "Omphale 2022 ; état du jumeau", "supposé",
              "s'annule dans C"),
    )

    def __init__(self, omega: dict | None = None):
        self.omega_fixe = omega

    def omega(self, pop: Population) -> dict:
        if self.omega_fixe is not None:
            return {p: np.asarray(w, float) for p, w in self.omega_fixe.items()}
        return {p: omega_apl(p, pop.sexes, pop.ages) for p in self.professions}

    def standard(self, pop: Population, years) -> tuple[np.ndarray, np.ndarray]:
        """(professions, P_std [profession, territoire, année]) = Σ_{a,s} pop · ω."""
        W = self.omega(pop)
        profs = np.array(sorted(W))
        P = pop.P[:, pop.years_index(years)]                                  # [territoire, année, sexe, âge]
        return profs, np.stack([np.einsum("tysa,sa->ty", P, W[p]) for p in profs])

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M1":
        super().fit(pop, etat, ref)
        profs, Pstd = self.standard(pop, [ref])
        self.r_bar = {p: 1.0 for p in profs}
        if etat is not None and ref in etat:
            from besoin.couverture import offre
            S = offre({ref: etat[ref]})
            for i, p in enumerate(profs):
                if p in set(S.professions):
                    self.r_bar[p] = float(S.values[S.p(p)].sum() / Pstd[i].sum())
        return self

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        years = pop.years if years is None else np.asarray(list(years))
        profs, Pstd = self.standard(pop, years)
        r = np.array([self.r_bar.get(p, 1.0) for p in profs])
        return Cube(profs, pop.territories, years, r[:, None, None] * Pstd, pop.level)
