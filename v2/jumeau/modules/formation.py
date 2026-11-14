"""Vivier en formation (national) : inscrits par profession × année d'étude.

Chaque année : l'année d'étude k passe en k+1 avec un abandon a (par profession, voir `abandon`) ; la dernière année devient
`diplomes` (compte du registre) ; la première année reçoit `capacite` (quota) × la dernière cohorte
observée. Les diplômés ne sont pas encore injectés dans N : les entrées viennent du module
`entrees` (flux ajusté). Relier les deux est un module de l'axe 2 (diplômés → filières → installation).
"""
import pandas as pd

from jumeau.module import Module, Param, Pool, par_profession, register

# Abandon annuel équivalent, infirmiers : 1 − ρ^(1/3) avec ρ = diplômés(t+3) / inscrits en 1re année(t) = 0,718
# (entrée 2022, DREES jeu 491, fiche axe 1 param-ide-rendement-diplomes) ; niveau 2009-2018 : ρ ≈ 0,84 → 0,056.
ABANDON = {"infirmiers": round(1 - 0.718 ** (1 / 3), 4), "*": 0.0}


@register
class Formation(Module):
    name = "formation"
    order = 5
    params = (
        Param("abandon", ABANDON, "par an, par profession",
              "DREES, enquête Écoles, jeu 491 (séries longues 1966-2025), via fiches axe 1 param-ide-rendement-diplomes "
              "et param-ide-abandon-1a", "entrée 2022 (mise à jour 29/10/2026)", "sourcé",
              "IDE : 1 − 0,718^(1/3) ≈ 0,105 / an, dérivé d'un rendement mesuré (redoublements compris). Autres "
              "professions : 0, supposé (pas de source ; le « 30 % » IDE n'avait pas de source primaire).", (0.0, 1.0)),
        Param("capacite", 1.0, "× première année observée", "arrêtés d'objectifs 2021 et 2026", "2026", "supposé", "", (0.0, 5.0)),
    )

    def begin(self, state, ctx):
        self._intake = {}                  # première année observée, par profession ; remis à zéro à chaque run

    def step(self, state, ctx):
        p = state.pool
        if p is None or p.empty:
            return []
        q = float(ctx.param(self, "capacite"))
        ab = ctx.param(self, "abandon")
        new, grads, drop = {}, {}, {}
        for prof, s in p.groupby(level=0):
            a = float(par_profession(ab, [prof])[0])
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
