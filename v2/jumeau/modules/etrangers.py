"""Diplômés à l'étranger : flux séparé, avec son propre multiplicateur.

Le flux ajusté `entrees.flux` contient déjà les arrivées de diplômés à l'étranger (le RPPS ne les distingue
pas). Pour ne pas les compter deux fois, on n'ajoute pas un flux : on **isole leur part** des entrées
positives de l'année, puis on la multiplie.
  part_p = min(1, flux_p / Σ I⁺_p)   I⁺ = entrées nettes positives ajustées (sante.model.fit_rates), toutes
                                      cellules de la profession dans l'état (l'état doit couvrir la profession)
  ajout  = part_p · entrées⁺ · (m − 1)
La part formée en France, (1 − part_p) · entrées⁺, est celle que suit `lien_formation`.
Âge : l'ajout entre dans la tranche qui contient `age_entree` (28 ans, DD76, tableaux 12-13 : âge moyen des
diplômés à l'étranger à l'entrée, SF et CD ; repris pour MK, supposé). Territoires et sexes : comme les entrées
ajustées (supposé). Le total ajouté par cellule est inchangé ; seule sa répartition par âge change.
Flux par an (fiche axe 1 param-diplomes-etrangers-flux, 2026-11-14) : CD 1 300 (sourcé : Ordre 2022, 1 313
primo-inscrits diplômés à l'étranger ; 1 309 reconnaissances UE) · MK 2 200 (dérivé : 2 528 autorisations en
2023, CNOMK 2024 ; stock diplômés hors France +2 212 / an net 2020-2024 ; plage 1 700-2 500) · PH 240 (dérivé :
8,1 % des primo-inscrits de l'Ordre 2024-2025) · IDE 400 (sourcé, confiance faible : hypothèse DREES ER 1319 ;
plage 400-1 100) · SF 80 (dérivé ; plage 70-170). Variante basse (DD76, ER 1075, données 2015-2020) :
SF 70 · CD 665 · MK 1 175 · PH et IDE 0 (FLUX_BAS).
⚑ Définitions hétérogènes (primo-inscription, entrée RPPS, autorisation) : un flux d'entrées en activité est
probablement plus bas que les décisions de reconnaissance ; la part est plafonnée à 1.
"""
import numpy as np

from jumeau.history import stock_flow_rates
from jumeau.module import Add, Module, Param, par_profession, register

FLUX = {"sages-femmes": 80.0, "dentistes": 1300.0, "kines": 2200.0, "pharmaciens": 240.0, "infirmiers": 400.0, "*": 0.0}
FLUX_BAS = {"sages-femmes": 70.0, "dentistes": 665.0, "kines": 1175.0, "*": 0.0}


def part_etrangere(hist, state, flux) -> np.ndarray:
    """Part des diplômés à l'étranger dans les entrées positives, par cellule (même valeur pour une profession)."""
    _, inflow, _ = stock_flow_rates(hist, state)
    pos = np.clip(inflow, 0, None).sum(axis=1)
    prof = state.cells.profession.to_numpy()
    tot = {p: pos[prof == p].sum() for p in np.unique(prof)}
    f = par_profession(flux, prof)
    denom = np.array([tot[p] for p in prof])
    return np.minimum(1.0, np.where(denom > 0, f / np.where(denom > 0, denom, 1), 0.0))


@register
class Etrangers(Module):
    name = "etrangers"
    order = 36
    needs = ("entrees",)
    params = (
        Param("flux", FLUX, "personnes/an, par profession",
              "fiche axe 1 param-diplomes-etrangers-flux : Ordre CD 2022, CNOMK 2024, Ordre PH 2024-2025, DREES "
              "ER 1319 (IDE) ; variante basse FLUX_BAS : DD76 tableaux 12-13, ER 1075", "2022-2025", "sourcé",
              "Diplômés à l'étranger entrant chaque année. CD sourcé, MK/PH/SF dérivés, IDE confiance faible.",
              (0.0, 1e5)),
        Param("multiplicateur", 1.0, "× flux observé", "fiche param-age-entree-exercice (plage supposée × [0 ; 2])",
              "—", "supposé", "Reconnaissance des diplômes, procédures d'autorisation d'exercice.", (0.0, 3.0),
              "attirer"),
        Param("age_entree", 28.0, "ans", "DREES, Les Dossiers n° 76 (2021), tableaux 12 et 13 (SF, CD : 28 ans)",
              "RPPS 2020", "sourcé", "Âge d'entrée des diplômés à l'étranger ; l'ajout va dans la tranche qui le "
              "contient. MK : valeur SF/CD reprise, supposé.", (18.0, 70.0)),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        m = ctx.param(self, "multiplicateur")
        if np.all(np.asarray(m) == 1):
            return []
        share = part_etrangere(self.hist, state, ctx.param(self, "flux"))
        e_pos = np.clip(ctx.delta(self, "entrees"), 0, None).sum(axis=1)
        mm = np.ravel(m) if np.ndim(m) else m
        band = int(np.searchsorted(state.ages, ctx.param(self, "age_entree"), side="right") - 1)
        amount = np.zeros_like(state.N)
        amount[:, max(band, 0)] = share * e_pos * (mm - 1.0)
        return [Add(self.name, amount, src="diplomes_etranger")]
