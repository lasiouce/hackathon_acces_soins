"""Modules de l'axe 2 branchés sur le registre du jumeau (aucun fichier de v2/jumeau/ modifié).

Ils remplacent le trio vieillissement / sorties / entrees quand le calibrage change (methodes.calibrage),
et produisent les mêmes flux nommés ("vieillissement", "sorties", "entrees") : une composition contient
l'un ou l'autre trio, jamais les deux (build() refuse deux producteurs du même flux).
Options lues dans hist.options : aging (uniforme | interp), simple (état en âges simples), hier (bool),
shrink, trend60 (bool), obs_r12 (bool), inflow_recent.

Leviers (paramètres qu'un scénario modifie) :
  methodes_sorties.tendance_60plus   λ, multiplicateur de la pente de rétention des 60 ans et plus
                                     (1 = tendanciel, 0 = rétention stationnaire)
  methodes_sorties.decalage_retraite, .cumul_multiplicateur   même mécanisme que jumeau `sorties`
  methodes_entrees.multiplicateur    même mécanisme que jumeau `entrees` (sans délai : à dater par Event)
"""
import numpy as np

from jumeau.history import SOURCE_RPPS
from jumeau.module import Add, Module, Param, Rate, Shift, register
from jumeau.state import AXES
from methodes import calibrage

SRC_AGES = "désagrégation linéaire par morceaux des tranches quinquennales du RPPS (Sprague simplifié)"


def calibration(hist, state) -> dict:
    """Calibrage partagé par les trois modules, aligné sur les cellules de l'état ; mis en cache sur hist."""
    key = ("methodes", len(state.cells))
    if key in hist._cache:
        return hist._cache[key]
    o = hist.options
    t = hist.table.rename(columns={hist.level: "dep"})
    if "sector" in t:
        if t.sector.nunique() > 1:
            raise ValueError("methodes : un seul secteur à la fois (le calibrage par secteur n'est pas porté)")
        t = t.drop(columns="sector")
    c = calibrage.fit(t, hist.fit_years, shrink=o.get("shrink", 200.0), aging=o.get("aging", "uniforme"),
                      hier=calibrage.dep_to_region() if o.get("hier") else None, trend60=o.get("trend60", False),
                      obs_r12=o.get("obs_r12", False), inflow_recent=o.get("inflow_recent"))
    idx = state.index(c["cells"].rename(columns={"dep": "territory"}).assign(sector=state.cells.sector.iloc[0])[AXES])
    if (idx < 0).any() or len(set(idx)) != len(state.cells):
        raise ValueError("methodes : cellules du calibrage ≠ cellules de l'état")
    A = c["A"]
    simple = bool(o.get("simple"))
    band = A.band if simple else np.arange(len(A.lo))            # tranche de chaque colonne d'âge de l'état
    out = {"A": A, "simple": simple, "band": band, "alo": A.lo[band], "tbar": c["tbar"], "aging": c["aging"]}
    for k in ("s", "inflow", "b60"):
        v = np.empty_like(c[k])
        v[idx] = c[k]
        out[k] = v[:, band]
    if simple:                                                    # entrées de la tranche réparties sur ses âges
        out["inflow"] = out["inflow"] / A.w[band][None, :]
    hist._cache[key] = out
    return out


@register
class MethodesVieillissement(Module):
    name = "methodes_vieillissement"
    order = 10
    produces = ("vieillissement",)
    params = (Param("operateur", None, "—", SRC_AGES, "2012–2026", "supposé",
                    "uniforme (v1), interp (âges désagrégés chaque année) ou âges simples (état en années)."),)

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        c = calibration(self.hist, state)
        if c["simple"]:
            return [Shift("vieillissement", 1.0)]
        if c["aging"] == "uniforme":
            return [Shift("vieillissement", 0.2)]
        # Shift n'accepte qu'une fraction par tranche, pas par cellule : on rend le déplacement net (somme nulle)
        return [Add("vieillissement", c["A"].age(state.N, "interp") - state.N, src="vieillissement")]


@register
class MethodesSorties(Module):
    name = "methodes_sorties"
    order = 20
    produces = ("sorties",)
    params = (
        Param("retention", None, "par an", SOURCE_RPPS, "fenêtre d'ajustement", "mesuré",
              "Rétention nette par cellule × tranche, moindres carrés après l'opérateur de vieillissement."),
        Param("tendance_60plus", 1.0, "× pente ajustée", SOURCE_RPPS + ", pente nationale 60+ sur la fenêtre",
              "fenêtre d'ajustement", "mesuré",
              "λ : s(t) = min(1, s + λ·b·(t − t̄)) pour les tranches ≥ 60 ans ; 0 = rétention stationnaire."),
        Param("decalage_retraite", 0.0, "années", "Loi n° 2023-270 ; LFSS 2026 (passage âge légal → sorties : hypothèse)",
              "2023", "supposé"),
        Param("cumul_multiplicateur", 1.0, "× part 2018", "DREES ER n° 1097 (médecins ; autres professions : hypothèse)",
              "2018", "supposé"),
        Param("part_cumul", 0.10, "part", "DREES ER n° 1097", "2018", "sourcé"),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        c = calibration(self.hist, state)
        lam = ctx.param(self, "tendance_60plus")
        s = c["s"]
        if np.any(c["b60"] != 0):
            s = np.clip(s + np.reshape(lam, (-1, 1)) * c["b60"] * (ctx.year - c["tbar"]), 0.0, 1.0)
        s = ctx.param(self, "retention", base=s)
        d, k = ctx.param(self, "decalage_retraite"), ctx.param(self, "cumul_multiplicateur")
        if np.any(d != 0) or np.any(k != 1):                      # mécanisme de jumeau.modules.sorties, par tranche
            a, col = c["alo"], (lambda v: np.reshape(v, (-1, 1)) if np.ndim(v) else v)
            m = np.ones_like(state.N)
            m = np.where((a >= 60) & (a <= 65), m * np.maximum(0.0, 1.0 - col(d) / 5.0), m)
            m = np.where(a >= 65, m * np.maximum(0.0, 1.0 - ctx.param(self, "part_cumul") * (col(k) - 1.0)), m)
            s = 1.0 - (1.0 - s) * m
        return [Rate("sorties", s, to="sorties")]


@register
class MethodesEntrees(Module):
    name = "methodes_entrees"
    order = 30
    produces = ("entrees",)
    params = (
        Param("flux", None, "personnes/an", SOURCE_RPPS, "fenêtre d'ajustement", "mesuré",
              "Entrées nettes annuelles par cellule × âge (moyenne de la fenêtre)."),
        Param("multiplicateur", 1.0, "× niveau actuel", "Loi OTSS 2019 ; arrêtés d'objectifs 2021 et 2026", "2026",
              "supposé"),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        c = calibration(self.hist, state)
        amount = ctx.param(self, "flux", base=c["inflow"])
        m = ctx.param(self, "multiplicateur")
        if np.any(m != 1):
            amount = amount * (np.reshape(m, (-1, 1)) if np.ndim(m) else m)
        return [Add("entrees", amount, src="entrees")]


COMPOSITION = ("methodes_vieillissement", "methodes_sorties", "methodes_entrees")
