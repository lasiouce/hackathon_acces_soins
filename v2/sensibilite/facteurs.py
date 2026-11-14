"""Facteurs de l'axe 5 et modèle Y = f(x) : N « libéral » (secteur privé, total national) en 2030, 2040, 2050.

Chaque facteur est tiré dans [0, 1) puis traduit : continu (bornes lo, hi) ou discret (niveaux, tranche égale).
Familles : E choix d'estimation, D données, P paramètres, L leviers (scénario, pas une incertitude).
Les plages et leur statut sont recopiés dans le rapport et dans decisions.md (2026-11-14, axe 5).

Le jumeau tourne au département, secteur privé seul : sans régulation ni transition, aucun flux ne relie le
privé et le public, donc simuler le public ne change pas Y. Infirmiers : `secteur_stock` n'a ni âge ni sexe ;
on prend « infirmiers-liberaux » (v1, SNDS par âge, 2012–2023), soit environ 36 % du privé (98 854 / 277 788).
"""
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from sante import estimators as V1
from sante.model import stock_table
from jumeau.estimators import twin_of
from jumeau.history import sector_table
from jumeau.modules.entrees import evenement_quotas
from jumeau.scenario import Scenario

PROFS = ("sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers")
YEARS = (2030, 2040, 2050)
SEED = 20261114
# délai de formation L_p (v2/sante/levers_v1.LAG, v1 : supposé)
LAG = {"pharmaciens": 6, "dentistes": 6, "sages-femmes": 5, "kines": 5, "infirmiers": 3}
# part des libéraux en cumul emploi-retraite (fiche param-cumul-emploi-retraite, COR 2016, données 2015 : sourcé)
CUMUL = {"sages-femmes": 0.008, "dentistes": 0.047, "pharmaciens": 0.018, "kines": 0.015, "infirmiers": 0.015}
SHRINK = (20, 200, 2000, None)                 # None = taux nationaux (profession × sexe)
ENTREES = ("plates", "recentes")            # « tendance » exclue : explose à 2050 (rapport axe 5, grille hors Sobol)


@dataclass(frozen=True)
class F:
    name: str
    family: str          # E, D, P, L
    lo: float = 0.0
    hi: float = 1.0
    levels: tuple = ()   # discret si non vide
    status: str = ""
    source: str = ""

    def value(self, u):
        if self.levels:
            return self.levels[min(int(u * len(self.levels)), len(self.levels) - 1)]
        return self.lo + u * (self.hi - self.lo)


def factors(prof: str, levers: bool = True) -> list[F]:
    f = [
        F("fenetre", "E", levels=(2, 3, 5, 8), status="choix", source="observatoire A5 ; v1 fenêtre 5 ans"),
        F("shrink", "E", levels=SHRINK, status="choix", source="axe 3 N1 (défaut 200)"),
        F("entrees", "E", levels=ENTREES, status="choix", source="sante.estimators (plates / récentes 2 ans)"),
        F("fraction", "P", 0.18, 0.22, status="supposé (±10 %)",
          source="vieillissement.fraction 0,2 : âges uniformes dans la tranche"),
        F("part_cumul", "P", 0.5 * CUMUL[prof], 2.0 * CUMUL[prof], status="sourcé ×[0,5 ; 2] (millésime 2015)",
          source="fiche param-cumul-emploi-retraite"),
    ]
    if prof in ("dentistes", "pharmaciens"):
        f.append(F("filiere", "E", levels=(False, True), status="choix", source="DREES inscrits 2020–2025"))
    if prof != "infirmiers":
        f.append(F("part_privee", "D", levels=("min", "central", "max"), status="mesuré (bornes axe 4)",
                   source="axe 4, secteur_stock"))
    if levers:
        f += [
            F("decalage_retraite", "L", 0.0, 2.0, status="levier", source="sorties.decalage_retraite (Loi 2023-270)"),
            F("cumul_multiplicateur", "L", 1.0, 2.0, status="levier", source="sorties.cumul_multiplicateur"),
            F("quotas", "L", 0.8, 1.2, status="levier", source="DREES DD76 : quotas ±20 % ; délai L_p supposé"),
        ]
    return f


@lru_cache
def _table(prof: str, variant: str) -> pd.DataFrame:
    if prof == "infirmiers":
        t = stock_table(["infirmiers-liberaux"]).assign(profession="infirmiers")
    else:
        t = sector_table([prof], variant)
        t = t[t.sector == "prive"].drop(columns="sector")
    return t


def origin(prof: str) -> int:
    return int(_table(prof, "central").year.max())


class Model:
    """Y(x) pour une profession ; les ajustements sont mis en cache par combinaison de choix discrets."""

    def __init__(self, prof: str, levers: bool = True):
        self.prof, self.f = prof, factors(prof, levers)
        self.o = origin(prof)
        self._fits = {}
        self.runs = 0

    def estimator(self, w, shrink, entrees, filiere, variant):
        key = (w, shrink, entrees, filiere, variant)
        if key not in self._fits:
            v1 = type("V", (V1.StockFlowLocal,), {"shrink": shrink, "inflow_recent": 2 if entrees == "recentes" else None,
                                                   "inflow_trend": entrees == "tendance", "pipeline": filiere})
            t = _table(self.prof, variant)
            self._fits[key] = twin_of(v1)().fit(t, (self.o - w, self.o), self.o)
        return self._fits[key]

    def values(self, u) -> dict:
        return {f.name: f.value(ui) for f, ui in zip(self.f, u)}

    def __call__(self, u) -> np.ndarray:
        v = self.values(u)
        est = self.estimator(v["fenetre"], v["shrink"], v["entrees"], v.get("filiere", False),
                             v.get("part_privee", "central"))
        params = {"vieillissement.fraction": v["fraction"], "sorties.part_cumul": v["part_cumul"],
                  "sorties.decalage_retraite": v.get("decalage_retraite", 0.0),
                  "sorties.cumul_multiplicateur": v.get("cumul_multiplicateur", 1.0),
                  "entrees.filiere": v.get("filiere", False)}
        ev = []
        if v.get("quotas", 1.0) != 1.0:
            ev = [evenement_quotas(v["quotas"], self.o, LAG[self.prof])]
        tr = est.trajectory(max(YEARS), Scenario(name="axe5", params=params, events=ev))
        est._traj.clear()                  # le jumeau met chaque trajectoire en cache : sans ça, la mémoire croît par run
        self.runs += 1
        return np.array([tr.states[y].N.sum() for y in YEARS])
