"""M1 : recours standardisé par âge et sexe (dérivation du 2026-11-15, §6).

B₁(p, T, t) = r̄_p · Σ_{a,s} pop(T, t, a, s) · ω(p, a, s), en ETP-équivalents.
  ω   forme relative du recours : poids de standardisation des fichiers APL de la DREES (DCIR, 19 tranches
      quinquennales jusqu'à 90+), fiche param-besoin-poids-age-apl. Colonne 2024 (DCIR 2022) pour IDE, CD, SF ;
      2023 (DCIR 2021) pour les MK, faute de colonne 2024 publiée. SF : poids sur les femmes, 0 pour les hommes.
      Omphale a deux tranches au-delà de 90 ans (90–94, 95+) : toutes deux prennent le poids « 90 et plus ».
  r̄   niveau : en attendant Open DAMIR (axe 4), offre nationale / population standardisée nationale à l'année de
      référence (supposé). Il s'annule dans C, comme pour M0.
Pharmaciens et médecine générale : pas de poids APL ; forme par le profil Open DAMIR (param-besoin-profil-damir) :
quantités des flux de janvier à septembre 2025, secteur privé, par tranche décennale (80+ plat) et sexe, rapportées
à la population Omphale 2025. `profil="damir"` l'applique à toutes les professions (P2 de P-B1). Spécialistes :
non servis (absents du cube, jamais remplacés par M0).

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
DAMIR = "v2/data/processed/besoin/damir_profils.parquet"
DAMIR_CODE = {**{"infirmiers": "IDE", "kines": "MK", "dentistes": "CD", "sages-femmes": "SF"},
              "pharmaciens": "PH", "medecine-generale": "MG"}
CODE = {"infirmiers": "IDE", "kines": "MK", "dentistes": "CD", "sages-femmes": "SF"}
COLONNE = {"infirmiers": 2024, "kines": 2023, "dentistes": 2024, "sages-femmes": 2024}
FEMMES = {"sages-femmes"}
DAMIR_PROFS = ("infirmiers", "kines", "dentistes", "sages-femmes", "pharmaciens", "medecine-generale")


R_BAR_SOURCE = 0.9e-3      # ETP par habitant standardisé : repli si le niveau mesuré manque (supposé)
# Niveau de la demande des sources, calé à l'année de référence sur l'effectif libéral mesuré (1 professionnel = 1 temps
# plein, comme les cibles) : ameli, « Démographie des professionnels de santé », France, 1er janvier 2025 (décision P1-4).
NIVEAU_SOURCE = {"medecine-generale": 56005}


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


@lru_cache(maxsize=1)
def _damir_qte() -> pd.DataFrame:
    """Quantités Open DAMIR (flux 2025-01 à 2025-09), secteur privé, par profession × tranche décennale × sexe."""
    d = pd.read_parquet(DAMIR, columns=["prof", "age", "sexe", "ppu", "qte"])
    d = d[(d.ppu == 2) & d.age.between(0, 80) & d.sexe.isin([1, 2])]
    return d.groupby(["prof", "age", "sexe"]).qte.sum().reset_index()


def omega_damir(prof: str, pop: Population, year: int = 2025) -> np.ndarray:
    """ω [sexe, âge] = r(a,s) / r̄, r = quantité DAMIR / population Omphale de la tranche décennale (80+ plat)."""
    q = _damir_qte()
    q = q[q.prof == DAMIR_CODE[prof]].set_index(["sexe", "age"]).qte
    ages = np.asarray(pop.ages)
    dec = np.where(ages < 20, 0, np.minimum(ages // 10 * 10, 80))
    P = pop.P[:, pop.years_index([year])[0]].sum(axis=0)              # [sexe, âge], France entière
    code = {"H": 1, "F": 2}
    r = np.zeros_like(P)
    for i, sx in enumerate(pop.sexes):
        for d in np.unique(dec):
            m = dec == d
            r[i, m] = q.get((code[sx], int(d)), 0.0) / P[i, m].sum()
    return r / ((r * P).sum() / P.sum())


@register
class M1(NeedEstimator):
    name = "M1"
    norme = ("besoin = recours national par âge et sexe de l'année de base (DCIR, poids APL de la DREES), appliqué "
             "à la pyramide de chaque territoire ; le recours y est pris pour le besoin")
    assumptions = ("Chaque habitant compte selon le recours moyen de sa tranche d'âge (et de son sexe pour les "
                   "sages-femmes), figé à l'année de base. Le recours est censuré par l'offre : là où elle manque, "
                   "ce besoin est trop bas (dérivation §2.3).")
    professions = tuple(DAMIR_CODE)
    params = (
        Param("omega", "poids APL par tranche quinquennale (19 tranches, 90+)", "sans dimension",
              "DREES, jeu 530 APL, onglet « Paramètres » (fiche param-besoin-poids-age-apl)",
              "DCIR 2022 (colonne 2024) ; MK : DCIR 2021 (colonne 2023)", "mesuré",
              "forme du profil seulement ; SF sur la population féminine"),
        Param("omega_damir", "quantités par tranche décennale et sexe / population", "sans dimension",
              "Open DAMIR, flux 2025-01 à 2025-09, PRS_PPU_SEC = 2 (fiche param-besoin-profil-damir)",
              "2025 (9 mois)", "mesuré", "pharmaciens et MG ; 80+ plat ; biais saisonnier ≤ 1,3 % (axe 4)"),
        Param("r_bar", None, "ETP par habitant standardisé",
              "offre nationale / population standardisée nationale à l'année de référence, ajusté par fit() ; "
              "MG (source) : effectif libéral ameli au 1er janvier 2025 (56 005) / population standardisée",
              "Omphale 2022 ; état du jumeau ; ameli 2025", "supposé",
              "s'annule dans C des cibles ; MG : niveau mesuré (ameli), fixe son poids dans un transfert"),
    )

    def __init__(self, omega: dict | None = None, profil: str = "apl"):
        """profil « apl » (P1 : poids APL ; pharmaciens et MG par DAMIR) ou « damir » (P2 : DAMIR pour tous)."""
        self.omega_fixe, self.profil = omega, profil

    def omega(self, pop: Population) -> dict:
        if self.omega_fixe is not None:
            return {p: np.asarray(w, float) for p, w in self.omega_fixe.items()}
        W = {p: omega_damir(p, pop) for p in DAMIR_PROFS}
        if self.profil == "apl":
            W |= {p: omega_apl(p, pop.sexes, pop.ages) for p in CODE}
        return W

    def standard(self, pop: Population, years) -> tuple[np.ndarray, np.ndarray]:
        """(professions, P_std [profession, territoire, année]) = Σ_{a,s} pop · ω."""
        W = self.omega(pop)
        profs = np.array(sorted(W))
        P = pop.P[:, pop.years_index(years)]                                  # [territoire, année, sexe, âge]
        return profs, np.stack([np.einsum("tysa,sa->ty", P, W[p]) for p in profs])

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M1":
        super().fit(pop, etat, ref)
        profs, Pstd = self.standard(pop, [ref])
        self.r_bar = {p: (NIVEAU_SOURCE[p] / Pstd[i].sum() if p in NIVEAU_SOURCE else R_BAR_SOURCE)
                      for i, p in enumerate(profs)}
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
        r = np.array([self.r_bar.get(p, R_BAR_SOURCE) for p in profs])
        return Cube(profs, pop.territories, years, r[:, None, None] * Pstd, pop.level)
