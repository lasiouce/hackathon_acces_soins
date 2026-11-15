"""Sortie du module de besoin, prête pour l'API (pas branchée dans la carte sans accord).

besoin_api(etat, …) -> dict
  besoin            B' [profession][territoire][année], ETP-équivalents, après transferts (professions de sortie)
  couverture        C sous le scénario et les transferts, indexé sur la base à `ref`
  couverture_base   C du scénario de base, sans transfert
  transferts        par transfert et par année, totaux nationaux : temps libéré chez la source (« ETP de MG
                    libérés »), reçu par la cible, expansion m
  hypotheses        norme, hypothèses et paramètres avec leur statut
Les professions de SANS_COUVERTURE (MG, spécialistes) n'apparaissent que comme source dans `transferts`.
"""
from besoin.couverture import ACTIVITE, SANS_COUVERTURE, couverture, offre
from besoin.cube import Population
from besoin.interface import discover
from besoin.transferts import appliquer


def _param(p) -> dict:
    return dict(name=p.name, value=p.value, unit=p.unit, source=p.source, vintage=p.vintage, status=p.status, doc=p.doc)


def besoin_api(etat: dict, pop: Population | None = None, estimateur: str = "M0", transferts=(), ref: int = 2026,
               etat_base: dict | None = None, level: str | None = None, years=None, plugins=()) -> dict:
    """etat : année -> State (scénario) ; etat_base : idem pour la base (défaut : etat). level : niveau de sortie
    (défaut : celui des états) ; au-dessus, B et S sont sommés avant le rapport, jamais C moyenné."""
    pop = Population.load() if pop is None else pop
    base = etat if etat_base is None else etat_base
    years = [y for y in sorted(etat) if y >= ref] if years is None else list(years)
    est = discover(*plugins)[estimateur]().fit(pop, base, ref)
    B0 = est.predict(pop, base, years)
    B1, detail = appliquer(B0, transferts)
    S = offre(etat, years)
    S0 = S if etat_base is None else offre(base, years)
    if level is not None and level != S.level:
        B0, B1, S, S0 = (c.up(level) for c in (B0, B1, S, S0))
    C0 = couverture(S0, B0, ref)
    C1 = couverture(S, B1, ref, S0, B0)
    profs = [p for p in C1.professions if p not in SANS_COUVERTURE]
    Bo = B1.sel(professions=profs)
    return {
        "estimateur": est.name, "norme": est.norme, "unite": B1.unit, "ref": ref, "niveau": C1.level,
        "years": [int(y) for y in C1.years], "territories": C1.territories.tolist(),
        "besoin": {p: Bo.values[Bo.p(p)].tolist() for p in profs},
        "couverture": {p: C1.values[C1.p(p)].tolist() for p in profs},
        "couverture_base": {p: C0.values[C0.p(p)].tolist() for p in profs},
        "transferts": [dict(transfert=d["transfert"], source=d["source"], cible=d["cible"],
                            etp_liberes_source=d["libere"].sum(axis=0).tolist(),
                            etp_recus_cible=d["recu"].sum(axis=0).tolist(), expansion=d["m"].sum(axis=0).tolist())
                       for d in detail],
        "hypotheses": {"assumptions": est.assumptions, "params": est.hypotheses() + [_param(ACTIVITE)],
                       "population": pop.source, "scenario_population": pop.scenario},
    }
