"""Vivier en formation (national) : inscrits par profession × année d'étude.

Chaque année, pour chaque profession :
  - l'année d'étude k passe en k+1 avec un abandon a (par profession, voir `abandon`) ;
  - la dernière année devient `diplomes` (compte du registre) ;
  - la première année reçoit `capacite` (places, × la première année du début du run).
Deux viviers avancent côte à côte : celui du scénario et un vivier de **référence** aux valeurs par défaut
(abandon et capacité du tendanciel). Le compte `diplomes_reference` permet au module `lien_formation`
de mesurer k(t) = diplômés / diplômés de référence, qui vaut exactement 1 au tendanciel.

Vivier : `state.pool` s'il est fourni (inscrits DREES absolus, pool_drees : CD, PH) ; sinon un vivier
**relatif** stationnaire, une ligne par profession de l'état : n_k = (1 − a₀)^(k−1), k = 1..L_p. Le niveau
n'a pas d'importance, seul le rapport au vivier de référence sert.
Délai : une hausse de capacité dès l'année origine + 1 donne ses premiers diplômés en origine + L_p + 1,
même convention que les quotas v1 (evenement_quotas).
"""
import numpy as np
import pandas as pd

from jumeau.module import Add, Module, Param, Pool, par_profession, register

# Abandon annuel équivalent, infirmiers : 1 − ρ^(1/3) avec ρ = diplômés(t+3) / inscrits en 1re année(t) = 0,718
# (entrée 2022, DREES jeu 491, fiche axe 1 param-ide-rendement-diplomes) ; niveau 2009-2018 : ρ ≈ 0,84 → 0,056.
ABANDON = {"infirmiers": 1 - 0.718 ** (1 / 3), "*": 0.0}
# Durée des études L_p (années) : délais de app/levers.LAG (v1), supposés.
DUREE = {"specialistes": 10, "pharmaciens": 6, "dentistes": 6, "sages-femmes": 5, "kines": 5, "infirmiers": 3}


@register
class Formation(Module):
    name = "formation"
    order = 5
    params = (
        Param("abandon", ABANDON, "par an, par profession",
              "DREES, enquête Écoles, jeu 491 (séries longues 1966-2025), via fiches axe 1 param-ide-rendement-diplomes "
              "et param-ide-abandon-1a", "entrée 2022 (mise à jour 29/10/2026)", "sourcé",
              "IDE : 1 − 0,718^(1/3) ≈ 0,105 / an, dérivé d'un rendement mesuré (redoublements compris). Autres "
              "professions : 0, supposé (pas de source ; le « 30 % » IDE n'avait pas de source primaire). "
              "Plage IDE : 0,056 (niveau 2009-2018) à 0,105. Se fixe par `params` (dict par profession).",
              (0.0, 1.0), "former"),
        Param("capacite", 1.0, "× première année du début du run", "arrêtés d'objectifs 2021 et 2026 ; DD76 (±20 %)",
              "2026", "supposé", "Places en 1re année. Événements datés avec sélecteur `profession` seulement.",
              (0.0, 3.0), "former"),
        Param("duree", DUREE, "années, par profession", "app/levers.LAG (v1)", "—", "supposé",
              "Durée des études du vivier relatif.", (1.0, 15.0)),
    )

    def begin(self, state, ctx):
        """Vivier initial (scénario) et vivier de référence, remis à zéro à chaque run."""
        if state.pool is not None and not state.pool.empty:
            self._pool = state.pool.copy()
        else:
            profs = sorted(state.cells.profession.unique())
            a0 = par_profession(self.param("abandon").value, profs)
            L = par_profession(ctx.param(self, "duree"), profs).astype(int)
            self._pool = pd.Series({(p, k): (1 - a) ** (k - 1) for p, a, l in zip(profs, a0, L) for k in range(1, l + 1)},
                                   dtype=float).rename_axis(["profession", "k"])
        self._ref = self._pool.copy()
        self._intake = {p: float(s.droplevel(0).sort_index().iloc[0]) for p, s in self._pool.groupby(level=0)}

    @staticmethod
    def _advance(pool, abandon, capacity, intake):
        new, grads, drop = {}, {}, {}
        for prof, s in pool.groupby(level=0):
            s = s.droplevel(0).sort_index()
            a = float(abandon[prof])
            kept = s * (1 - a)
            drop[prof] = float((s * a).sum())
            grads[prof] = float(kept.iloc[-1])
            shifted = kept.iloc[:-1].rename(lambda k: k + 1)
            row = pd.concat([pd.Series({s.index.min(): intake[prof] * float(capacity[prof])}), shifted])
            new.update({(prof, k): v for k, v in row.items()})
        return pd.Series(new).rename_axis(["profession", "k"]), pd.Series(grads), pd.Series(drop)

    def step(self, state, ctx):
        profs = sorted(self._pool.index.get_level_values(0).unique())
        pf = pd.DataFrame({"profession": profs})
        a = dict(zip(profs, par_profession(ctx.param(self, "abandon"), profs)))
        q = dict(zip(profs, np.broadcast_to(ctx.param(self, "capacite", cells=pf), (len(profs),)).astype(float)))
        a0 = dict(zip(profs, par_profession(self.param("abandon").value, profs)))
        q0 = dict.fromkeys(profs, float(self.param("capacite").value))
        self._pool, grads, drop = self._advance(self._pool, a, q, self._intake)
        self._ref, grads_ref, _ = self._advance(self._ref, a0, q0, self._intake)
        return [Pool(self.name, self._pool, {"diplomes": grads, "abandons": drop, "diplomes_reference": grads_ref})]


@register
class LienFormation(Module):
    """Relie le vivier aux entrées : la part formée en France des entrées positives de l'année suit k(t).
    Ajoute (1 − part étrangère) · entrées⁺ · (k − 1), k = diplômés / diplômés de référence (= 1 au tendanciel).
    La part étrangère vient du module `etrangers` (même calcul), pour ne pas compter deux fois."""
    name = "lien_formation"
    order = 35
    needs = ("entrees", "formation")
    params = ()

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        from jumeau.modules.etrangers import Etrangers, part_etrangere
        g = ctx.pool_out(self, "formation", "diplomes")
        g0 = ctx.pool_out(self, "formation", "diplomes_reference")
        if g is None or g0 is None:
            return []
        ratio = (g / g0.where(g0 > 0)).fillna(1.0)
        k = state.cells.profession.map(ratio).fillna(1.0).to_numpy()[:, None]
        if np.all(k == 1.0):
            return []
        e_pos = np.clip(ctx.delta(self, "entrees"), 0, None)
        share = part_etrangere(self.hist, state, ctx.param_of("etrangers", "flux", Etrangers.param("flux").value))[:, None]
        return [Add(self.name, (1 - share) * e_pos * (k - 1.0), src="diplomes_france")]


def pool_drees(year: int | None = None) -> pd.Series:
    """Vivier observé : inscrits DREES (990_drees_mmop2, 2020–2025) aux années d'étude utilisées par
    sante.pipeline.SPEC (CD, PH ; années 2 à 6). Les autres professions n'ont pas de série ici (axe 4)."""
    from sante.pipeline import SPEC, enrolments
    e = enrolments()
    year = int(e.year.max()) if year is None else year
    rows = {}
    for prof, (dip, ks, last) in SPEC.items():
        if prof == "specialistes":                        # phase 2 ; DES année 4 seule, pas un vivier complet
            continue
        x = e[(e.type_de_diplome == dip) & (e.year == year) & e.k.isin(ks)]
        rows.update({(prof, int(k)): float(n) for k, n in zip(x.k, x.n)})
    return pd.Series(rows).rename_axis(["profession", "k"])
