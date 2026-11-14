"""Le jumeau derrière l'interface Estimator de la v1 (fit / predict / assumptions).

twin_of(V1) fabrique, pour une classe stock-flux de sante.estimators, son équivalent sur le jumeau :
mêmes options d'ajustement, mais la projection passe par l'état, les modules et le moteur. Le banc
(sante.backtest) et l'app peuvent ainsi les comparer sans rien savoir du jumeau.

trajectory(until, scenario) pose le scénario passé sur le scénario de base (Scenario.over : la filière
d'une variante n'est pas perdue), puis construit et calibre sa composition (cache par composition) : un
module ajouté au scénario est exécuté, ou une erreur dit pourquoi il ne peut pas l'être. Une table avec une colonne `sector` donne un état sectorisé ; `sectors` ajoute des secteurs vides
(ex. destination de la régulation).
"""
import pandas as pd

from sante.estimators import Estimator
from sante.model import KEYS
from jumeau.engine import build, run
from jumeau.history import History
from jumeau.scenario import Scenario
from jumeau.state import State


class TwinEstimator(Estimator):
    options: dict = {}
    scenario = Scenario()
    level = "dep"
    sectors: tuple = ()

    def fit(self, t, fit_years, origin):
        super().fit(t, fit_years, origin)
        st = State.from_table(t, origin, self.level)
        for s in self.sectors:
            st = st.ensure_sector(s)
        self.state = st
        self.hist = History(t[t.year <= origin], origin, fit_years, self.level, dict(self.options))
        self._mods, self._traj = {}, {}
        return self

    def modules(self, scenario: Scenario) -> list:
        key = tuple(sorted(scenario.composition))
        if key not in self._mods:
            mods = build(scenario.composition)
            for m in mods:
                m.fit(self.hist)
            self._mods[key] = mods
        return self._mods[key]

    def trajectory(self, until: int, scenario: Scenario | None = None):
        """scenario est posé **sur** le scénario de base de l'estimateur (Scenario.over) : ses paramètres
        priment, ses événements s'ajoutent, la composition et la filière de la base sont gardées s'il n'en dit rien."""
        scn = self.scenario if scenario is None else scenario.over(self.scenario)
        key = scn.to_json()
        if key in self._traj and max(self._traj[key].states) >= until:
            return self._traj[key]
        tr = run(self.state, self.modules(scn), scn, until)
        self._traj[key] = tr
        return tr

    def predict(self, target):
        """Même agrégation que StockFlow.predict (format long puis somme par profession × dep)."""
        x = self.trajectory(target).states[target]
        cells = x.cells.rename(columns={"territory": "dep"})[KEYS]
        p = pd.DataFrame(x.N, columns=x.ages).assign(**cells, year=target).melt(
            id_vars=KEYS + ["year"], var_name="age_lo", value_name="n")
        return p.groupby(["profession", "dep"]).n.sum()


def twin_of(v1cls, scenario: Scenario | None = None, sectors: tuple = ()) -> type:
    opts = {"shrink": v1cls.shrink, "inflow_trend": v1cls.inflow_trend, "inflow_recent": v1cls.inflow_recent}
    base = Scenario(name="tendanciel", params={"entrees.filiere": True} if v1cls.pipeline else {})
    scn = base if scenario is None else scenario.over(base)
    return type(f"Twin{v1cls.__name__}", (TwinEstimator,),
                {"name": f"{v1cls.name} [jumeau]", "assumptions": v1cls.assumptions, "options": opts,
                 "scenario": scn, "sectors": tuple(sectors)})
