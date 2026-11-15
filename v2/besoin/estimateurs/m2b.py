"""M2b, « saturation » : le besoin est le recours des territoires saturés (dérivation du 2026-11-15, §6).

    R_std = ρ_max · A / (A + K)   ⇒   B₂ᵦ = ρ_max · B₁ ,   besoin non satisfait = B₂ᵦ − R
**Tué par P-B2 le 2026-11-15** pour les quatre professions testées (IDE, MK, CD, SF) : aucun plateau établi
(rapport v2/docs/lab/reports/2026-11-15-besoin-pb2-saturation.md). Le code et le verdict restent ; la classe n'est
**pas enregistrée** (`@register` retiré), donc aucun chemin de service ne peut la choisir. Elle reste importable
pour la reproduction et les tests de cas limites.
"""
from dataclasses import replace

from besoin.cube import Cube, Population
from besoin.estimateurs.m1 import M1
from besoin.estimateurs.recours import PROF_AMELI
from besoin.interface import NeedEstimator

VERDICT = ("tué par P-B2 (2026-11-15) : borne haute de l'IC à 98,75 % de δ ≥ 0 pour IDE, MK, CD, SF ; "
           "pente du premier quintile non distinguable de 0 pour IDE, MK, SF ; placebo non attribuable pour MK, CD")


class M2b(NeedEstimator):
    name = "M2b"
    servi = False
    norme = "besoin = recours au plateau de saturation (ρ_max × recours standardisé par l'âge)"
    assumptions = "Le recours plafonne quand l'offre croît (R2) ; " + VERDICT
    professions = tuple(PROF_AMELI)

    def __init__(self, rho_max: dict | None = None):
        self.rho_max = rho_max

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M2b":
        super().fit(pop, etat, ref)
        if self.rho_max is None:
            from besoin.estimateurs.recours import table
            from besoin.validation.pb2 import formes
            dep = pop if pop.level == "dep" else Population.load(pop.scenario)
            self.rho_max = {}
            for p in self.professions:
                t, _ = table(p, dep, (2023, 2024, 2025))
                f = formes(t.A.to_numpy(), t.R_std.to_numpy())["sat"]
                self.rho_max[p] = f.get("rho_max", float("nan"))
        self.m1 = M1().fit(pop, etat, ref)
        return self

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        B1 = self.m1.predict(pop, etat, years).sel(professions=list(self.professions))
        import numpy as np
        r = np.array([self.rho_max[p] for p in B1.professions])
        return replace(B1, values=B1.values * r[:, None, None])
