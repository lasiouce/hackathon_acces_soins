"""M3 : épidémiologique, prévalence × actes par cas (dérivation du 2026-11-15, §6 ; voie (i), observée).

    B₃(p, T, t) = Σ_{a,s} pop(T, t, a, s) · [ Σ_g prev(g, T, a, s) · n(p, g) + r₀(p, a, s) ] / prix_p
  g       les 16 groupes de niveau 1 de la cartographie des pathologies qui ont des effectifs (cancers, diabète,
          maladies cardioneurovasculaires, …, « pas de pathologie repérée ») ; au niveau 1, la dépense de la
          cartographie est une partition : Σ_g montant(g) + soins courants = total (mesuré : écart < 10⁻⁹)
  prev    effectifs 2024 / population de la cartographie, par département × âge quinquennal (95+) × sexe ;
          cellules masquées (< 11 patients) imputées à `impute` patients (5 par défaut ; 1 et 10 en sensibilité)
  n(p,g)  dépense remboursée nationale du poste de p attribuée au groupe g, par patient du groupe (jeu « depenses »)
  r₀      terme hors pathologie, national : profil total de M1 (P1 ; PH : DAMIR) moins la part des groupes à
          cet âge et ce sexe, tel que défini par P-B3 ; il peut être négatif aux âges où les groupes, à dépense
          par cas sans âge, surattribuent (part négative rapportée par `negatif`, en fraction du total)
  prix    prix moyen remboursé d'un acte de p, Open DAMIR 2025 (9 mois), national, secteur privé ; il ne fixe que
          le niveau (s'annule dans C)
Prévalences figées à 2024 (supposé) : la projection ne fait bouger que la pyramide. Indépendant de l'offre locale
(cas limite §4 : B₃ > 0 en zone sans offre). Au-dessus du département : sommer le cube (B est additif).
"""
from dataclasses import replace
from functools import lru_cache

import numpy as np
import pandas as pd

from jumeau.module import Param

from besoin.cube import Cube, Population, mapping
from besoin.estimateurs.m1 import DAMIR_CODE, M1, _damir_qte
from besoin.estimateurs.recours import ODBL
from besoin.interface import NeedEstimator, register

POSTE = {"infirmiers": "Soins infirmiers remboursés", "kines": "Soins de kinésithérapie remboursés",
         "dentistes": "Soins dentaires remboursés", "sages-femmes": "Soins de sages-femmes remboursés",
         "pharmaciens": "Médicaments remboursés"}
ANNEE = 2024
TOTAL, COURANTS = "POP_TOT_IND", "top_SoiCour"


@lru_cache(maxsize=1)
def _depenses() -> pd.DataFrame:
    e = pd.read_parquet(ODBL + "ameli_pathologies_depenses.parquet")
    return e[e.annee == ANNEE]


def groupes() -> list:
    e = _depenses()
    l1 = e[e.niveau_prioritaire.fillna("").str.contains("1") & ~e.top.isin([TOTAL, COURANTS])]
    return sorted(l1.top.unique())


def n_par_cas(prof: str) -> pd.Series:
    """€ remboursés du poste de p par patient du groupe g (national, 2024)."""
    e = _depenses()
    e = e[(e.dep_niv_2 == POSTE[prof]) & e.top.isin(groupes())].set_index("top")
    return (e.montant / e.ntop).rename(prof)


def total_poste(prof: str) -> float:
    e = _depenses()
    return float(e[(e.dep_niv_2 == POSTE[prof]) & (e.top == TOTAL)].montant.iloc[0])


@lru_cache(maxsize=3)
def prevalences(impute: float = 5.0) -> tuple:
    """(prev [g, département, sexe, âge] alignée sur la Population Omphale, prev nationale [g, sexe, âge],
    départements, groupes). Âges 00-04 … 95et+, sexes F, H."""
    d = pd.read_parquet(ODBL + "ameli_pathologies_effectifs.parquet",
                        columns=["annee", "top", "cla_age_5", "sexe", "region", "departement", "ntop", "npop"])
    g = groupes()
    d = d[(d.annee == ANNEE) & d.top.isin(g) & (d.cla_age_5 != "tsage") & d.sexe.isin(["1", "2"])].copy()
    d["ntop"] = d.ntop.fillna(impute)
    d["age_lo"] = d.cla_age_5.str[:2].astype(int)
    d["sex"] = d.sexe.map({"1": "H", "2": "F"})
    d["prev"] = d.ntop / d.npop.where(d.npop > 0)
    nat = d[d.region == "99"]
    loc = d[(d.departement != "999") & (d.region != "99")]
    deps = np.sort(loc.departement.unique())
    sexes, ages = np.array(["F", "H"]), np.arange(0, 100, 5)
    P = np.zeros((len(g), len(deps), 2, 20))
    gi, di = np.searchsorted(g, loc.top), np.searchsorted(deps, loc.departement)
    P[gi, di, np.searchsorted(sexes, loc.sex), loc.age_lo.to_numpy() // 5] = loc.prev.fillna(0).to_numpy()
    Pn = np.zeros((len(g), 2, 20))
    Pn[np.searchsorted(g, nat.top), np.searchsorted(sexes, nat.sex), nat.age_lo.to_numpy() // 5] = \
        nat.prev.fillna(0).to_numpy()
    return P, Pn, deps, np.array(g)


def prix(prof: str) -> float:
    """€ remboursés par unité de quantité, Open DAMIR 2025 (9 mois), secteur privé, national."""
    d = pd.read_parquet("v2/data/processed/besoin/damir_profils.parquet", columns=["prof", "ppu", "qte", "rem_mnt"])
    d = d[(d.prof == DAMIR_CODE[prof]) & (d.ppu == 2)]
    return float(d.rem_mnt.sum() / d.qte.sum())


@register
class M3(NeedEstimator):
    name = "M3"
    norme = ("besoin = morbidité locale (cartographie des pathologies 2024) × soins remboursés par patient de chaque "
             "pathologie au niveau national, plus un terme hors pathologie par âge et sexe")
    assumptions = ("Chaque territoire a besoin, pour chaque pathologie, des soins qu'un patient de cette pathologie "
                   "reçoit en moyenne en France. Les prévalences par âge et sexe de 2024 sont figées ; seule la "
                   "pyramide bouge. Les pathologies sont repérées par la consommation de soins : la circularité "
                   "du recours n'est que diluée (moyenne nationale), pas levée.")
    professions = tuple(POSTE)
    params = (
        Param("prev", "cartographie 2024, 16 groupes de niveau 1", "patients / habitant",
              "CNAM, data.ameli.fr, jeu « effectifs » (ODbL)", "2024", "mesuré",
              "cellules < 11 masquées, imputées à 5 (sensibilité 1 et 10) ; figées dans le temps (supposé)"),
        Param("n_par_cas", "dépense remboursée du poste par patient du groupe", "€ / patient",
              "CNAM, data.ameli.fr, jeu « depenses » (ODbL), national", "2024", "mesuré",
              "voie (i) : observée, hérite de la censure, diluée au national"),
        Param("prix", "Open DAMIR, montant remboursé / quantité", "€ / acte",
              "Open DAMIR, flux 2025-01 à 2025-09, secteur privé", "2025 (9 mois)", "mesuré", "niveau seulement"),
    )

    def __init__(self, impute: float = 5.0):
        self.impute = impute

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M3":
        super().fit(pop, etat, ref)
        P, Pn, self.deps, g = prevalences(self.impute)
        self.prev = P
        dep = pop if pop.level == "dep" else Population.load(pop.scenario)
        if not (np.array_equal(dep.ages, np.arange(0, 100, 5)) and list(dep.sexes) == ["F", "H"]):
            raise ValueError("M3 : tranches Omphale attendues 0…95, sexes F, H")
        W = M1().omega(dep)
        Pnat = dep.P[:, dep.years_index([ANNEE])[0]].sum(axis=0)          # [sexe, âge]
        self.n, self.r0, self.negatif, self.prix = {}, {}, {}, {}
        for p in self.professions:
            n = n_par_cas(p).reindex(g).fillna(0).to_numpy()
            T = total_poste(p)
            prof_tot = T * W[p] / (W[p] * Pnat).sum()                         # € par habitant, [sexe, âge]
            grp = np.einsum("gsa,g->sa", Pn, n)
            r0 = prof_tot - grp
            self.negatif[p] = float((np.minimum(r0, 0) * Pnat).sum() / T)
            self.n[p], self.r0[p] = n, r0
            self.prix[p] = prix(p)
        return self

    def par_habitant(self, territories, level) -> dict:
        """€ par habitant [territoire, sexe, âge] par profession (prévalences du département de rattachement)."""
        deps = territories if level == "dep" else mapping("com", "dep").reindex(territories).to_numpy()
        pos = np.searchsorted(self.deps, deps)
        ok = (pos < len(self.deps)) & (self.deps[np.minimum(pos, len(self.deps) - 1)] == deps)
        if not ok.all():
            raise ValueError(f"M3 : {int((~ok).sum())} territoires sans prévalence, ex. {list(np.asarray(deps)[~ok][:5])}")
        return {p: np.einsum("gtsa,g->tsa", self.prev[:, pos], self.n[p]) + self.r0[p][None] for p in self.professions}

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        if pop.level not in ("dep", "com"):
            raise ValueError("M3 : niveau com ou dep (agréger le cube ensuite, B est additif)")
        years = pop.years if years is None else np.asarray(list(years))
        P = pop.P[:, pop.years_index(years)]
        h = self.par_habitant(pop.territories, pop.level)
        profs = np.array(self.professions)
        V = np.stack([np.einsum("tysa,tsa->ty", P, h[p]) / self.prix[p] for p in profs])
        return Cube(profs, pop.territories, years, V, pop.level, "actes")
