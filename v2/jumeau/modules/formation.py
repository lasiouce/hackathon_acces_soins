"""Vivier en formation (national) : inscrits par profession × année d'étude.

Chaque année : l'année d'étude k passe en k+1 avec un abandon a ; la dernière année devient
`diplomes` (compte du registre) ; la première année reçoit `capacite` (quota) × la dernière cohorte
observée. Les diplômés ne sont pas encore injectés dans N : les entrées viennent du module
`entrees` (flux ajusté). Relier les deux est un module de l'axe 2 (diplômés → filières → installation).
"""
import pandas as pd

from jumeau.module import Module, Param, Pool, register


@register
class Formation(Module):
    name = "formation"
    order = 5
    params = (
        Param("abandon", 0.0, "par an", "à sourcer (axe 1 : enquête écoles DREES ; IDE ≈ 30 % à vérifier)", "—",
              "supposé"),
        Param("capacite", 1.0, "× première année observée", "arrêtés d'objectifs 2021 et 2026", "2026", "supposé"),
    )

    def begin(self, state, ctx):
        self._intake = {}                  # première année observée, par profession ; remis à zéro à chaque run

    def step(self, state, ctx):
        p = state.pool
        if p is None or p.empty:
            return []
        a, q = float(ctx.param(self, "abandon")), float(ctx.param(self, "capacite"))
        new, grads, drop = {}, {}, {}
        for prof, s in p.groupby(level=0):
            s = s.droplevel(0).sort_index()
            first = s.index.min()
            kept = s * (1 - a)
            drop[prof] = float((s * a).sum())
            grads[prof] = float(kept.iloc[-1])
            shifted = kept.iloc[:-1].rename(lambda k: k + 1)
            self._intake.setdefault(prof, float(s.loc[first]))
            row = pd.concat([pd.Series({first: self._intake[prof] * q}), shifted])
            new.update({(prof, k): v for k, v in row.items()})
        return [Pool(self.name, pd.Series(new).rename_axis(["profession", "k"]),
                     {"diplomes": pd.Series(grads), "abandons": pd.Series(drop)})]


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
