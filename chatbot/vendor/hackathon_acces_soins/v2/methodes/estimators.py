"""Les méthodes de l'axe 2 derrière l'interface Estimator (fit / predict), sur le jumeau.

Chaque variante = des options de calibrage (methodes.calibrage) + la composition methodes.modules.
  AgesInterp      A1a  vieillissement non uniforme dans la tranche (désagrégé chaque année)
  AgesSimples     A1b  état en âges simples, désagrégé une fois à l'origine, cohortes suivies
  ShrinkHier      A2   département -> région -> national, k = 200 aux deux niveaux
  Retention60     A3   rétention des 60 ans et plus en tendance (pente nationale, λ = 1)
  Combine         A123 A1a + A2 + A3 (pré-spécifiée)
  ObservatoireR12 B4   schéma de l'observatoire (r ∈ [0,5 ; 1,2], entrées = résidus < 35 ans), diagnostic
  Uniforme        contrôle : composition methodes avec les options v1 (doit égaler twin_of(StockFlowLocal))
"""
import numpy as np

from jumeau.estimators import TwinEstimator
from jumeau.scenario import Scenario
from jumeau.state import State
from methodes.modules import COMPOSITION, calibration


class MethodEstimator(TwinEstimator):
    options = {"shrink": 200.0, "aging": "uniforme"}
    scenario = Scenario(name="tendanciel", modules=COMPOSITION)

    def fit(self, t, fit_years, origin):
        super().fit(t, fit_years, origin)
        if self.options.get("simple"):
            # calibrage par tranche, déjà déplié sur les âges simples ; mêmes cellules, donc le cache reste valide
            c = calibration(self.hist, self.state)
            st = self.state
            self.state = State(st.cells, c["A"].single.astype(int), c["A"].split(st.N, "interp"), st.year, st.level)
        return self


def _variant(cls_name, name, assumptions, **opts):
    return type(cls_name, (MethodEstimator,), {"name": name, "assumptions": assumptions,
                                               "options": {"shrink": 200.0, "aging": "uniforme", **opts}})


Uniforme = _variant("Uniforme", "contrôle methodes = taux locaux", "Contrôle : options v1 dans la composition methodes.")
AgesInterp = _variant("AgesInterp", "A1a âges interpolés",
                      "Comme les taux locaux, mais chaque année les tranches sont désagrégées en âges simples "
                      "(densité linéaire par morceaux), vieillies d'un an et réagrégées.", aging="interp")
AgesSimples = _variant("AgesSimples", "A1b âges simples",
                       "État en âges simples (20 à 74+), désagrégé à l'origine ; vieillissement exact d'un an ; "
                       "rétention et entrées calibrées par tranche avec l'opérateur A1a.", aging="interp", simple=True)
ShrinkHier = _variant("ShrinkHier", "A2 shrinkage hiérarchique",
                      "Taux du département rétrécis vers la région (k = 200), elle-même vers le national (k = 200).",
                      hier=True)
Retention60 = _variant("Retention60", "A3 rétention 60+ en tendance",
                       "Rétention des tranches ≥ 60 ans prolongée par sa pente nationale sur la fenêtre (λ = 1).",
                       trend60=True)
Combine = _variant("Combine", "A123 combinaison", "A1a + A2 + A3.", aging="interp", hier=True, trend60=True)
ObservatoireR12 = _variant("ObservatoireR12", "B4 observatoire r ≤ 1,2",
                           "Schéma de l'observatoire : r = 1 et entrées = résidus moyens (5 ans) sous 35 ans ; "
                           "ailleurs r rétréci dép -> rég -> nat et borné à [0,5 ; 1,2].", hier=True, obs_r12=True)
