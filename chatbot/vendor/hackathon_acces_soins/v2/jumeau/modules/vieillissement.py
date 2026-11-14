"""Vieillissement : chaque année, 1/largeur de chaque tranche passe à la tranche suivante.

`fraction` scalaire = même fraction pour toutes les tranches (0,2 : tranches quinquennales, convention
v1, appliquée aussi à la première tranche ouverte). Pour des tranches de largeurs différentes
(CartoSanté : < 40, 40–49, 50–54, 55–59, 60+), passer un tableau, par exemple fractions(age_lo, age_hi).
"""
import numpy as np

from jumeau.module import Module, Param, Shift, register


def fractions(age_lo, age_hi, first_lo: int = 25) -> np.ndarray:
    """1 / largeur par tranche ; la première tranche ouverte commence à `first_lo` ; la dernière (ouverte) garde tout."""
    lo = np.maximum(np.asarray(age_lo, float), first_lo)
    w = np.asarray(age_hi, float) - lo + 1
    f = 1.0 / w
    f[-1] = 0.0
    return f


@register
class Vieillissement(Module):
    name = "vieillissement"
    order = 10
    params = (Param("fraction", 0.2, "par an (scalaire ou une valeur par tranche)",
                    "tranches quinquennales du RPPS (1/5 an⁻¹)", "2012–2026", "mesuré",
                    "Part d'une tranche qui passe à la suivante en un an, hypothèse d'âges uniformes dans la tranche.",
                    (0.0, 1.0)),)

    def step(self, state, ctx):
        f = ctx.param(self, "fraction")
        if np.ndim(f) and len(f) != len(state.ages):
            raise ValueError(f"vieillissement : {len(f)} fractions pour {len(state.ages)} tranches")
        return [Shift(self.name, f)]
