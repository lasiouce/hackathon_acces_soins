"""M2a, « AREA » : recours régressé sur le besoin et sur l'offre, offre fixée à la moyenne nationale (dérivation du
2026-11-15, §6 ; Gravelle et coll. 2003, formules de capitation anglaises).

Ajustement transversal au département (années 2023–2025, comme P-B2) :
    log R_std(d) = α + β · log A(d) + γ · log M(d) + ε
  R_std  recours standardisé par l'âge (patientèle × effectif ameli / B₁, 1 = France ; amendement A1.1)
  A      densité standardisée de l'offre libérale du jumeau (100 000 · N / B₁)
  M      indice de morbidité standardisé par âge et sexe (cartographie des pathologies 2024, recours.morbidite)
Besoin à accès moyen : A fixé à la moyenne nationale, donc le terme β·log Ā est une constante qui s'annule dans C :
    B₂ₐ(p, T, t) = r̄_p · B₁(p, T, t) · M(T)^γ_p ,   M figé à 2024 (supposé)
Il ne dépend pas de l'offre locale : en zone sans offre, B₂ₐ > 0 (cas limite §4).
Professions : IDE, MK, CD, SF (patientèle) ; pharmaciens non applicables (demande dérivée, dérivation §6).
Au-dessus du département, M d'une commune est celui de son département (ventilation de la Population).
"""
import numpy as np
import pandas as pd

from jumeau.module import Param

from besoin.cube import Cube, Population, mapping
from besoin.estimateurs.m1 import M1
from besoin.estimateurs.recours import PROF_AMELI, morbidite
from besoin.interface import NeedEstimator, register

YEARS = (2023, 2024, 2025)


def ajuste(prof: str, pop: Population, years=YEARS) -> dict:
    """α, β, γ par MCO sur les départements ; IC à 95 % de γ (erreurs homoscédastiques, indicatif)."""
    from besoin.estimateurs.recours import table
    t, _ = table(prof, pop, years)
    m = morbidite().reindex(t.index)
    ok = m.notna()
    X = np.column_stack([np.ones(ok.sum()), np.log(t.A[ok]), np.log(m[ok])])
    y = np.log(t.R_std[ok].to_numpy())
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ c
    s2 = e @ e / (len(y) - 3)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    return dict(alpha=float(c[0]), beta=float(c[1]), gamma=float(c[2]), se_gamma=float(se[2]), n=int(ok.sum()),
                r2=float(1 - e @ e / ((y - y.mean()) ** 2).sum()))


@register
class M2a(NeedEstimator):
    name = "M2a"
    norme = ("besoin = recours qu'aurait chaque territoire à accès moyen (offre fixée à la densité nationale), "
             "compte tenu de son âge et de sa morbidité ; méthode AREA")
    assumptions = ("Le recours dépend de l'âge, de la morbidité et de l'offre. On retire l'effet de l'offre locale "
                   "en la fixant à la moyenne nationale. La morbidité de 2024 est figée. L'offre n'est pas "
                   "supposée exogène au besoin (R1) : c'est une hypothèse, pas une mesure.")
    professions = tuple(PROF_AMELI)
    params = (
        Param("gamma", None, "élasticité du recours standardisé à la morbidité", "MCO transversal au département, "
              "ajusté par fit() (patientèle × démographie data.ameli.fr 2023–2025 ; cartographie des pathologies "
              "2024)", "2023–2025", "mesuré", "exposant de M dans B₂ₐ"),
        Param("morbidite", "indice départemental 2024, figé", "sans dimension",
              "cartographie des pathologies, data.ameli.fr (ODbL), standardisation indirecte âge × sexe", "2024",
              "supposé", "figé dans le temps (hypothèse)"),
    )

    def __init__(self, coefs: dict | None = None, morb: pd.Series | None = None):
        self.coefs, self.morb = coefs, morb

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M2a":
        super().fit(pop, etat, ref)
        dep = pop if pop.level == "dep" else Population.load(pop.scenario)
        self.coef = self.coefs or {p: ajuste(p, dep) for p in self.professions}
        self.M = morbidite() if self.morb is None else self.morb
        self.m1 = M1().fit(pop, etat, ref)
        return self

    def _M(self, territories, level):
        if level == "dep":
            return self.M.reindex(territories).fillna(1.0).to_numpy()
        if level == "com":
            return self.M.reindex(mapping("com", "dep").reindex(territories).to_numpy()).fillna(1.0).to_numpy()
        raise ValueError("M2a : niveau com ou dep (agréger le cube ensuite, B est additif)")

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        B1 = self.m1.predict(pop, etat, years).sel(professions=list(self.professions))
        M = self._M(pop.territories, pop.level)
        g = np.array([self.coef[p]["gamma"] for p in B1.professions])
        from dataclasses import replace
        return replace(B1, values=B1.values * (M[None, :] ** g[:, None])[:, :, None])
