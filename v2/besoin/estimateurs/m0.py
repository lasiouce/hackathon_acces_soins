"""M0 : besoin proportionnel à la population (baseline de la dérivation du 2026-11-15, §6).

B₀(p, T, t) = r̄_p · pop(T, t), en ETP-équivalents. Indexé à l'année de référence, C = densité / densité_ref :
r̄_p s'annule dans C, il ne fixe que le niveau de B (et donc le poids relatif des professions dans un transfert).
"""
import numpy as np

from jumeau.module import Param

from besoin.cube import Cube, Population
from besoin.interface import NeedEstimator, register

PLACEHOLDER = "placeholder en attendant les fiches de l'axe 1 (v2/docs/lab/fiches/)"


@register
class M0(NeedEstimator):
    name = "M0"
    norme = ("besoin = l'offre par habitant de l'année de référence au niveau national, appliquée à chaque "
             "territoire ; ni âge, ni sexe, ni morbidité")
    assumptions = ("Le besoin de chaque profession suit le nombre d'habitants : chaque habitant compte autant, "
                   "quel que soit son âge. C'est la densité pour 100 000 habitants, indexée à l'année de référence.")
    params = (
        Param("r_bar", {"medecine-generale": 0.9e-3, "specialistes": 0.9e-3}, "ETP par habitant",
              PLACEHOLDER + " ; professions de sortie : offre nationale / population nationale à l'année de "
              "référence, ajusté par fit()", "Omphale 2022 ; état du jumeau", "supposé",
              "norme choisie, pas une mesure ; médecine générale et spécialistes : sources de transferts seulement"),
    )

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M0":
        super().fit(pop, etat, ref)
        fixed = dict(self.param("r_bar").value)
        need = [p for p in self.professions if p not in fixed]
        if need:
            if etat is None or ref not in etat:
                raise ValueError(f"M0.fit : r̄ de {need} ajusté sur l'offre de {ref}, état {ref} absent")
            from besoin.couverture import offre
            S = offre({ref: etat[ref]})
            nat = pop.total()[:, pop.years_index([ref])[0]].sum()
            for p in need:
                fixed[p] = float(S.values[S.p(p)].sum() / nat) if p in set(S.professions) else np.nan
        self.r_bar = fixed
        return self

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        years = pop.years if years is None else np.asarray(list(years))
        P = pop.total()[:, pop.years_index(years)]                     # [territoire, année]
        profs = np.array([p for p in self.professions if np.isfinite(self.r_bar.get(p, np.nan))])
        r = np.array([self.r_bar[p] for p in profs])
        return Cube(profs, pop.territories, years, r[:, None, None] * P[None], pop.level)

