"""Sorties (retraite, décès, cessation, nettes des reprises) : N <- s · N, s = rétention nette annuelle.

s est ajusté par profession × territoire × sexe × âge (sante.model.fit_rates, plafonné à 1). Deux
leviers déplacent les sorties à partir des taux de sortie e = 1 − s (mécanismes repris de app/levers.py) :
  decalage_retraite Δ (ans)   e[60–69] × max(0, 1 − Δ/5)
  cumul_multiplicateur k      e[65+]  × max(0, 1 − part_cumul · (k − 1))
"""
import numpy as np

from jumeau.history import SOURCE_RPPS, stock_flow_rates
from jumeau.module import Module, Param, Rate, register


@register
class Sorties(Module):
    name = "sorties"
    order = 20
    params = (
        Param("retention", None, "par an", SOURCE_RPPS, "fenêtre d'ajustement", "mesuré",
              "Rétention nette annuelle par cellule × âge, moindres carrés sur la fenêtre, plafonnée à 1."),
        Param("decalage_retraite", 0.0, "années", "Loi n° 2023-270 ; LFSS 2026 (passage âge légal → sorties : hypothèse)",
              "2023", "supposé"),
        Param("cumul_multiplicateur", 1.0, "× part 2018", "DREES ER n° 1097 (médecins ; autres professions : hypothèse)",
              "2018", "supposé"),
        Param("part_cumul", 0.10, "part", "DREES ER n° 1097", "2018", "sourcé",
              "Part des libéraux en cumul emploi-retraite (médecins)."),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        s = ctx.param(self, "retention", base=stock_flow_rates(self.hist, state)[0])
        d, k = ctx.param(self, "decalage_retraite"), ctx.param(self, "cumul_multiplicateur")
        if np.any(d != 0) or np.any(k != 1):
            a = state.ages
            col = lambda v: np.reshape(v, (-1, 1)) if np.ndim(v) else v
            m = np.ones_like(state.N)
            m = np.where((a >= 60) & (a <= 65), m * np.maximum(0.0, 1.0 - col(d) / 5.0), m)
            m = np.where(a >= 65, m * np.maximum(0.0, 1.0 - ctx.param(self, "part_cumul") * (col(k) - 1.0)), m)
            s = 1.0 - (1.0 - s) * m
        return [Rate(self.name, s, to="sorties")]
