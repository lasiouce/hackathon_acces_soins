"""Entrées nettes : N <- N + k(t) · m · (I + pente · h).

I = flux annuel net ajusté dans les tranches où la rétention brute dépasse 1 (entrées, retours,
arrivées d'autres territoires). k(t) = taille relative de la cohorte en formation (DREES, inscrits)
si `filiere` est activé, sinon 1. m = multiplicateur de scénario (quotas) : evenement_quotas()
construit l'événement daté. Convention v1 (app/levers.project_flow) : les entrées de l'année
origine + L_p sont encore au niveau de base ; m s'applique à partir de origine + L_p + 1.
"""
import numpy as np

from jumeau.history import SOURCE_RPPS, stock_flow_rates
from jumeau.module import Add, Module, Param, register
from jumeau.scenario import Event
from sante.pipeline import scale


def evenement_quotas(m: float, origin: int, lag: int, selector: dict | None = None, source: str = "") -> Event:
    """Quotas × m décidés à l'origine : effet sur les entrées à partir de origin + lag + 1 (convention v1)."""
    return Event("entrees.multiplicateur", origin + lag + 1, m, "set", selector=selector or {}, source=source)


@register
class Entrees(Module):
    name = "entrees"
    order = 30
    params = (
        Param("flux", None, "personnes/an", SOURCE_RPPS, "fenêtre d'ajustement", "mesuré",
              "Entrées nettes annuelles par cellule × âge (moyenne de la fenêtre, ou des dernières années)."),
        Param("filiere", False, "booléen", "DREES, inscrits par année d'étude (990_drees_mmop2)", "2020–2025", "mesuré",
              "Entrées proportionnelles à la cohorte en formation (CD, PH, spécialistes)."),
        Param("multiplicateur", 1.0, "× niveau actuel", "Loi OTSS 2019 ; arrêtés d'objectifs 2021 et 2026", "2026",
              "supposé", "Effet d'un changement de quotas sur les entrées, après le délai de formation."),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        _, inflow, slope = stock_flow_rates(self.hist, state)
        inflow = ctx.param(self, "flux", base=inflow)
        k = 1.0
        if ctx.param(self, "filiere"):
            k = np.array([scale(p, ctx.origin, ctx.h)[-1] for p in state.cells["profession"]])[:, None]
        amount = k * (inflow + slope * ctx.h)
        m = ctx.param(self, "multiplicateur")
        if np.any(m != 1):
            amount = amount * (np.reshape(m, (-1, 1)) if np.ndim(m) else m)
        return [Add(self.name, amount, src="entrees")]
