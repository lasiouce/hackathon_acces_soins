"""Diplômés à l'étranger : flux séparé, avec son propre multiplicateur.

Le flux ajusté `entrees.flux` contient déjà les arrivées de diplômés à l'étranger (le RPPS ne les distingue
pas). Pour ne pas les compter deux fois, on n'ajoute pas un flux : on **isole leur part** des entrées
positives de l'année, puis on la multiplie.
  part_p = min(1, flux_p / Σ I⁺_p)   I⁺ = entrées nettes positives ajustées (sante.model.fit_rates), toutes
                                      cellules de la profession dans l'état (l'état doit couvrir la profession)
  ajout  = part_p · entrées⁺ · (m − 1)
La part formée en France, (1 − part_p) · entrées⁺, est celle que suit `lien_formation`. Hypothèse : les
diplômés à l'étranger se répartissent entre territoires, sexes et âges comme les entrées ajustées (supposé ;
DD76 donne un âge moyen d'entrée de 28 ans, non utilisé ici).
Flux (DD76, tableaux 12-13 ; ER 1075 pour MK), par an : SF 70 · CD 665 · MK 1 175 ; PH et IDE : non publié
→ 0, le levier est sans effet pour eux (dit, pas caché).
"""
import numpy as np

from jumeau.history import stock_flow_rates
from jumeau.module import Add, Module, Param, par_profession, register

FLUX = {"sages-femmes": 70.0, "dentistes": 665.0, "kines": 1175.0, "*": 0.0}


def part_etrangere(hist, state, flux) -> np.ndarray:
    """Part des diplômés à l'étranger dans les entrées positives, par cellule (même valeur pour une profession)."""
    _, inflow, _ = stock_flow_rates(hist, state)
    pos = np.clip(inflow, 0, None).sum(axis=1)
    prof = state.cells.profession.to_numpy()
    tot = {p: pos[prof == p].sum() for p in np.unique(prof)}
    f = par_profession(flux, prof)
    denom = np.array([tot[p] for p in prof])
    return np.minimum(1.0, np.where(denom > 0, f / np.where(denom > 0, denom, 1), 0.0))


@register
class Etrangers(Module):
    name = "etrangers"
    order = 36
    needs = ("entrees",)
    params = (
        Param("flux", FLUX, "personnes/an, par profession",
              "DREES, Les Dossiers n° 76 (2021), tableaux 12 et 13 ; ER n° 1075 (MK, 2016) ; fiche axe 1 "
              "param-age-entree-exercice", "RPPS 2020 ; 2016", "sourcé",
              "Diplômés à l'étranger entrant chaque année. PH, IDE : non publié → 0.", (0.0, 1e5)),
        Param("multiplicateur", 1.0, "× flux observé", "fiche param-age-entree-exercice (plage supposée × [0,5 ; 2])",
              "—", "supposé", "Reconnaissance des diplômes, procédures d'autorisation d'exercice.", (0.0, 3.0),
              "attirer"),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        m = ctx.param(self, "multiplicateur")
        if np.all(np.asarray(m) == 1):
            return []
        share = part_etrangere(self.hist, state, ctx.param(self, "flux"))[:, None]
        e_pos = np.clip(ctx.delta(self, "entrees"), 0, None)
        mm = np.reshape(m, (-1, 1)) if np.ndim(m) else m
        return [Add(self.name, share * e_pos * (mm - 1.0), src="diplomes_etranger")]
