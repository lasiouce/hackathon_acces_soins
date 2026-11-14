"""Critères d'acceptation de l'axe 0, écrits pour pouvoir échouer.

Run (racine du dépôt) : PYTHONPATH=v2 uv run python -m jumeau.check   -> v2/artifacts/a0_jumeau/results.json
Code de sortie 1 si un critère échoue. Chaque critère porte la valeur mesurée par la revue adversariale
sur le code d'avant (`avant`), quand elle existe : c'est la preuve que le test sait échouer.

  C1 reproduction   stock-flux v1 réécrit en modules : predict, et par cellule × âge × année → 2050
  C2 composition    un scénario passé par twin_of exécute ses modules ; régulation sur l'état réel (public
                    de l'axe 4) : effet non nul dans les zones, total inchangé sans plancher
  C3 plug-in        module factice déposé hors du paquet, exécuté par twin_of ; module inconnu refusé
  C4 démographie    régulation vers un public vide, mêmes taux : le total ne bouge pas (déplacement pur)
  C5 dépendances    composition sans le flux lu, lecture non déclarée, double producteur : refusés
  C6 scénario       clé mal orthographiée, opération ou axe inconnus : refusés ; aller-retour JSON identique
  C7 leviers        quotas × 1,1 contre le vrai chemin v1 (app/levers.project_flow) ; retraite contre le
                    séjour attendu (B1 : + Δ ans en 65+, 60–64 × (1 − Δ/5), 55–59 × (1 − Δ/10), montée 3 mois/an)
  C8 agrégation     commune -> dep -> rég -> national exact ; unité non rattachée refusée ; écart au RPPS mesuré
  C9 reproductible  deux runs sur les mêmes instances ne partagent pas d'état (formation)
  C10 vieillissement tranches de largeurs différentes : fractions par tranche, total conservé
  C12 paramètres sourcés de l'axe 1 (θ, répartition, exemption, abandon, cumul)
  C13 troisième revue : bornes composées et ajustées, JSON + over, événements non numériques, règle
                    « entrées ≤ sorties » contre une formule indépendante, bloqués jamais négatifs, retraite
                    exacte avec plusieurs tranches ≥ 65
  C14 leviers branchés (chantier) : identité au tendanciel, effet de chaque levier, délai, région,
                    comparaison aux chiffres cités (DD76, ER 1319, DREES retraite), familles
  C15 vitesse : 5 professions à la commune ≤ 2 s (bench_commune), chemin rapide = chemin complet
  C16 vivier réel (DREES 491) : reconstitution des diplômés, identité, effet, backtests contre la persistance
  C17 diplômés à l'étranger : entrée dans la tranche de 28 ans, total inchangé
  C18 infirmiers par secteur (axe 4) : totaux = SNDS + BTS, projetables
  C11 scénario posé sur la base : trajectory(Scenario()) = predict sur la variante filière ; quotas > 0
  T  temps          recalcul d'un scénario jusqu'en 2050
"""
import json
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

from sante import estimators as V1
from sante.backtest import DESIGN
from sante.model import KEYS, fit_rates, project, stock_table
from jumeau.engine import apply, build, run
from jumeau.estimators import twin_of
from jumeau.history import History, sector_table
from jumeau.module import REGISTRY, Module, Shift, discover
from jumeau.engine import Context
from jumeau.modules.entrees import evenement_quotas
from jumeau.modules.sorties import Sorties, evenement_retraite
from jumeau.modules.formation import pool_drees
from jumeau.modules.vieillissement import fractions
from jumeau.scenario import LEVIERS as LEVIERS_, Event, Scenario
from jumeau.state import Geography, State

OUT = Path("v2/artifacts/a0_jumeau")
STOCK_FLOW = [V1.StockFlowNational, V1.StockFlowLocal, V1.StockFlowLocalRecent, V1.StockFlowLocalPipeline,
              V1.StockFlowLocalTrendEntries]
PROFS = ["sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers-liberaux", "infirmiers-salaries", "specialistes"]
H2050 = 2050
ZONES = ["06", "13", "34", "66", "83"]        # illustration (densité kiné élevée), pas le zonage conventionnel
REG = ("vieillissement", "sorties", "entrees", "regulation")
SALARIAT = {"voisine": 0.0, "salariat": 1.0, "sortie": 0.0}     # mécanisme visible au département (C2, C4)
RESULTS = []


def crit(cid, critere, mesure, ok, avant=None):
    RESULTS.append(dict(id=cid, critere=critere, mesure=mesure, ok=bool(ok), avant=avant))
    print(f"{'OK ' if ok else 'ÉCHEC'} {cid} {critere} : {mesure}" + (f"  (avant : {avant})" if avant else ""), flush=True)


def raises(fn, exc=Exception) -> str | None:
    try:
        fn()
    except exc as e:
        return f"{type(e).__name__}: {e}"[:140]
    return None


def latest_design(prof, t):
    o = int(t.year.max())
    return prof, (max(int(t.year.min()), o - 5), o), o, [o + 5, H2050]


def c1_reproduction():
    rows, cell = [], []
    for prof, fit, origin, targets in DESIGN + [latest_design(p, stock_table([p])) for p in PROFS]:
        t = stock_table([prof])
        for cls in STOCK_FLOW:
            a, b = cls().fit(t, fit, origin), twin_of(cls)().fit(t, fit, origin)
            for y in targets:
                pa, pb = a.predict(y), b.predict(y)
                rows.append(dict(profession=prof, origin=origin, target=y, model=cls.__name__,
                                 gap=float((pa - pb).abs().max()), same_index=bool(pa.index.equals(pb.index))))
    for prof in PROFS:
        t = stock_table([prof])
        _, fit, o, _ = latest_design(prof, t)
        p = project(t, o, H2050 - o, fit_rates(t[t.year <= o], fit, shrink=200))
        p = p.pivot_table(index=KEYS + ["year"], columns="age_lo", values="n").sort_index()
        traj = twin_of(V1.StockFlowLocal)().fit(t, fit, o).trajectory(H2050)
        q = pd.concat([pd.DataFrame(s.N, columns=s.ages).assign(**s.cells.rename(columns={"territory": "dep"})[KEYS], year=y)
                       for y, s in traj.states.items()]).set_index(KEYS + ["year"]).sort_index()
        cell.append(dict(profession=prof, n=int(q.size), gap=float(np.abs(p.to_numpy() - q.to_numpy()).max())))
    r = pd.DataFrame(rows)
    r.to_csv(OUT / "reproduction.csv", index=False)
    g, gc = r.gap.max(), max(c["gap"] for c in cell)
    crit("C1", "reproduction de predict (v1)", f"max |écart| {g} sur {len(r)} comparaisons ; par cellule × âge × année "
         f"{gc} sur {sum(c['n'] for c in cell)} valeurs", g == 0 and gc == 0 and r.same_index.all())


def kine_sector(public_history: bool):
    """Kinés à 2 secteurs. public_history=False : public vide (taux de repli = privé) ; True : axe 4, part centrale."""
    t = sector_table(["kines"])
    if not public_history:
        t = t[t.sector == "prive"]
    o = int(t.year.max())
    return twin_of(V1.StockFlowLocal, Scenario(modules=REG))().fit(t, (o - 5, o), o)


def c2_composition():
    """Kinés et dentistes, état réel à 2 secteurs (axe 4). La régulation doit réduire le privé des zones et,
    sans plancher, laisser le total inchangé (destination par défaut : secteur `bloques`, démographie du privé)."""
    out = {}
    zlist = {"kines": ZONES, "dentistes": ZONES}
    for prof in ["kines", "dentistes"]:
        t = sector_table([prof])
        o = int(t.year.max())
        est = twin_of(V1.StockFlowLocal, Scenario(modules=REG))().fit(t, (o - 5, o), o)
        reg_scn = Scenario("régulation", params={"regulation.zones": {prof: zlist[prof]},
                                                 "regulation.repartition": SALARIAT}, modules=REG)
        res = {}
        for floor in (False, True):
            b = run(est.state, est.modules(reg_scn), Scenario(modules=REG), H2050, floor=floor)
            r = run(est.state, est.modules(reg_scn), reg_scn, H2050, floor=floor)
            c = r.states[H2050].cells
            zp = ((c.sector == "prive") & c.territory.isin(zlist[prof])).to_numpy()
            cb = b.states[H2050].cells
            zpb = ((cb.sector == "prive") & cb.territory.isin(zlist[prof])).to_numpy()
            res[floor] = dict(d_total=float(r.states[H2050].N.sum() - b.states[H2050].N.sum()),
                              d_prive_zones=float(r.states[H2050].N[zp].sum() - b.states[H2050].N[zpb].sum()),
                              bloques_2050=float(r.states[H2050].N[(c.sector == "bloques").to_numpy()].sum()),
                              moved=float(sum(np.clip(x, 0, None).sum() for _, f, _, x in r.ledger if f == "regulation")))
        pub = Scenario("régulation vers le public", params={"regulation.zones": {prof: zlist[prof]},
                                                             "regulation.repartition": SALARIAT,
                                                             "regulation.destination": "public"}, modules=REG)
        rp = run(est.state, est.modules(pub), pub, H2050, floor=False).states[H2050].N.sum()
        res["destination_public_d_total"] = float(rp - run(est.state, est.modules(pub), Scenario(modules=REG), H2050,
                                                                floor=False).states[H2050].N.sum())
        out[prof] = res
    est = kine_sector(public_history=True)
    err = raises(lambda: est.trajectory(2030, Scenario(params={"regulation.zones": {"kines": ZONES}},
                                                       modules=("vieillissement", "sorties", "entrees"))))
    ok = all(v[False]["d_prive_zones"] < 0 and abs(v[False]["d_total"]) < 1e-6 for v in out.values()) and err is not None
    crit("C2", "régulation exécutée par twin_of, sans créer ni supprimer (état réel, 2 secteurs)",
         " ; ".join(f"{p} : privé des zones {v[False]['d_prive_zones']:+.0f}, Δ total sans plancher {v[False]['d_total']:+.1e} "
                    f"(avec plancher {v[True]['d_total']:+.2f}) ; vers le public : {v['destination_public_d_total']:+.0f}"
                    for p, v in out.items()) + f" ; hors composition → {err is not None}",
         ok, avant="1re revue : écart 0,0 avec le tendanciel ; 2e revue : Δ total +254 dentistes, −474 kinés")
    return out


DUMMY = '''
import numpy as np
from jumeau.module import Add, Module, Param, register

@register
class Factice(Module):
    name = "factice"
    order = 90
    params = (Param("bonus", 1.0, "personnes/an/cellule×âge", "test d'acceptation axe 0", "2026", "supposé"),)

    def step(self, state, ctx):
        return [Add(self.name, np.full_like(state.N, ctx.param(self, "bonus")), src="factice")]
'''


def c3_plugin():
    unknown = raises(lambda: build(("vieillissement", "factice")))
    t = stock_table(["sages-femmes"])
    _, fit, o, _ = latest_design("sages-femmes", t)
    ref = twin_of(V1.StockFlowLocal)().fit(t, fit, o).trajectory(o + 1).states[o + 1].N
    with tempfile.TemporaryDirectory() as d:
        Path(d, "factice.py").write_text(DUMMY)
        discover(d)
        est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
        scn = Scenario("factice", params={"factice.bonus": 2.0}, modules=("vieillissement", "sorties", "entrees", "factice"))
        tr = est.trajectory(o + 1, scn)
        written = float(sum(x.sum() for _, f, _, x in tr.ledger if f == "factice"))
        expected = 2.0 * est.state.N.size
        base_gap = float(np.abs(est.trajectory(o + 1).states[o + 1].N - ref).max())
    crit("C3", "module factice exécuté par twin_of, sans autre fichier", f"flux inscrit {written:.0f} = attendu "
         f"{expected:.0f} ; tendanciel inchangé (écart {base_gap}) ; inconnu avant dépôt → {unknown is not None}",
         written == expected and base_gap == 0 and unknown is not None,
         avant="test contournant twin_of ; « aucun fichier modifié » ne pouvait pas échouer")


def c4_demography():
    """Déplacement pur : sans plancher à 0 (modèle linéaire), Δ total (régulation − tendanciel) doit être nul.
    Avec plancher, l'écart restant vient de troncatures différentes et est rapporté."""
    est = kine_sector(public_history=False)
    out = {}
    for floor in (False, True):
        tot = []
        for scn in (Scenario(modules=REG), Scenario(params={"regulation.zones": {"kines": ZONES},
                                                            "regulation.repartition": SALARIAT}, modules=REG)):
            tot.append(run(est.state, est.modules(scn), scn, H2050, floor=floor).states[H2050].N.sum())
        out[floor] = float(tot[1] - tot[0])
    crit("C4", "la régulation déplace sans créer (privé seul, destination vide en repli)", f"Δ total 2050 sans plancher "
         f"{out[False]:+.1e} ; avec plancher {out[True]:+.3f} personne ; {est.hist.borrowed} cellules en repli",
         abs(out[False]) < 1e-6, avant="+822 kinés en 2050")


class Espion(Module):
    name, order, needs = "espion", 25, ()

    def step(self, state, ctx):
        ctx.delta(self, "sorties")
        return []


class Diplomes(Module):
    name, order, needs = "lecteur_diplomes", 6, ("formation",)

    def step(self, state, ctx):
        self.lu = ctx.pool_out(self, "formation", "diplomes")
        ctx.delta(self, "formation")
        return []


class Double(Module):
    name, order, produces = "double", 35, ("entrees",)

    def step(self, state, ctx):
        return []


def c5_dependencies():
    REGISTRY.setdefault("espion", Espion)
    REGISTRY.setdefault("double", Double)
    a = raises(lambda: build(("vieillissement", "entrees", "regulation")))
    b = raises(lambda: build(("vieillissement", "sorties", "entrees", "double")))
    t = stock_table(["sages-femmes"])
    _, fit, o, _ = latest_design("sages-femmes", t)
    est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
    c = raises(lambda: est.trajectory(o + 1, Scenario(modules=("vieillissement", "sorties", "espion", "entrees"))), KeyError)
    REGISTRY.setdefault("lecteur_diplomes", Diplomes)
    from jumeau.modules.formation import pool_drees
    st = est.state.copy()
    st.pool = pool_drees()
    comp = ("formation", "lecteur_diplomes", "vieillissement", "sorties", "entrees")
    mods = build(comp)
    for m in mods:
        m.fit(est.hist)
    d = raises(lambda: run(st, mods, Scenario(modules=comp), o + 1), TypeError)
    lu = getattr(mods[1], "lu", None)
    crit("C5", "dépendances déclarées et vérifiées", f"sans `sorties` → {a} | double producteur → {b is not None} | "
         f"lecture non déclarée → {c is not None} | flux Pool par ctx.delta → {d is not None}, par ctx.pool_out → "
         f"{None if lu is None else round(float(lu.sum()))} diplômés", all([a, b, c, d]) and lu is not None,
         avant="régulation sans `sorties` : tous les entrants bloqués, sans erreur")


def c6_scenario():
    t = stock_table(["dentistes"])
    _, fit, o, _ = latest_design("dentistes", t)
    est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
    typo = raises(lambda: est.trajectory(2030, Scenario(params={"sorties.decalage_retaite": 1.0})))
    badop = raises(lambda: est.trajectory(2030, Scenario(events=[Event("sorties.decalage_retraite", o + 1, 1.0, "pow")])))
    axis = raises(lambda: est.trajectory(2030, Scenario(events=[Event("sorties.decalage_retraite", o + 1, 1.0,
                                                                      selector={"departement": "13"})])))
    sel_val = [raises(lambda sel=sel: est.trajectory(2030, Scenario(events=[Event("sorties.decalage_retraite", o + 1, 1.0,
                                                                                   selector=sel)])))
               for sel in ({"profession": "dentiste"}, {"territory": 6})]
    bound = raises(lambda: est.trajectory(2030, Scenario(events=[evenement_quotas(110, o, 6)])))
    scn = Scenario("retraite + quotas", events=[Event("sorties.decalage_retraite", o + 1, 1.0, selector={"territory": ["13", "75"]}),
                                                evenement_quotas(1.1, o, 6)], seed=7)
    back = Scenario.from_json(scn.to_json())
    gap = float(np.abs(est.trajectory(H2050, scn).states[H2050].N - est.trajectory(H2050, back).states[H2050].N).max())
    crit("C6", "scénario validé et sérialisable", f"faute de frappe → {typo} | opération → {badop is not None} | "
         f"axe → {axis is not None} | 'dentiste' → {sel_val[0]} | territoire 6 → {sel_val[1] is not None} | "
         f"quotas × 110 → {bound} | aller-retour JSON écart {gap}",
         all([typo, badop, axis, bound] + sel_val) and gap == 0 and back.to_json() == scn.to_json(),
         avant="1re revue : clé mal orthographiée ignorée ; 2e revue : {'profession': 'dentiste'} et {'territory': 6} → "
               "tendanciel, quotas × 110 → +5 085 033 dentistes")


def c7_levers():
    """Quotas : contre le vrai chemin v1. Retraite : contre le séjour attendu (B1), pas contre la v1, qui porte le défaut."""
    sys.path.insert(0, "app")
    import levers as LV
    t = stock_table(["dentistes"])
    _, fit, o, _ = latest_design("dentistes", t)
    v1 = V1.StockFlowLocal().fit(t, fit, o)
    est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
    years = list(range(o + 1, H2050 + 1))
    a = LV.project_flow(v1, "dentistes", H2050, {"entries": 1.1})
    b = est.trajectory(H2050, Scenario(events=[evenement_quotas(1.1, o, LV.LAG["dentistes"])])).totals(("territory",))
    b.index.name = a.index.name
    q_gap = float((a[years] - b.reindex(a.index)[years]).abs().max().max())
    # retraite : état à tranche ouverte 65+ (axe 4, dentistes), taux de sortie avant / après le levier
    ts = sector_table(["dentistes"])
    os_ = int(ts.year.max())
    es = twin_of(V1.StockFlowLocal)().fit(ts, (os_ - 5, os_), os_)
    mod = es.modules(es.scenario)[[m.name for m in es.modules(es.scenario)].index("sorties")]
    ages = es.state.ages
    dev = {}
    for d in (1.0, 2.0, 5.0):
        scn = Scenario(params={"sorties.decalage_retraite": d})
        ctx = Context(os_ + 1, os_, scn, es.state.cells, np.random.default_rng(0), len(ages))
        e0 = 1 - mod.step(es.state, Context(os_ + 1, os_, Scenario(), es.state.cells, np.random.default_rng(0), len(ages)))[0].factor
        e1 = 1 - mod.step(es.state, ctx)[0].factor
        top, m6064, m5559 = ages >= 65, (ages >= 60) & (ages < 65), (ages >= 55) & (ages < 60)
        pos = e0[:, top] > 0
        stay = (1 / e1[:, top][pos] - 1 / e0[:, top][pos])
        dev[d] = dict(sejour_65plus_moyen=float(stay.mean()), ecart_max_sejour=float(np.abs(stay - d).max()),
                      ratio_60_64=float(np.nanmax(np.abs(e1[:, m6064] - e0[:, m6064] * max(0, 1 - d / 5)))),
                      ratio_55_59=float(np.nanmax(np.abs(e1[:, m5559] - e0[:, m5559] * max(0, 1 - d / 10)))))
    ramp = [ev.value for ev in evenement_retraite(1.0, o)]
    ok = q_gap < 1e-9 and all(v["ecart_max_sejour"] < 1e-9 and v["ratio_60_64"] < 1e-12 and v["ratio_55_59"] < 1e-12
                               for v in dev.values()) and ramp == [0.25, 0.5, 0.75, 1.0]
    eff = {d: float(100 * (es.trajectory(H2050, Scenario(params={"sorties.decalage_retraite": d})).states[H2050].N.sum()
                           / es.trajectory(H2050).states[H2050].N.sum() - 1)) for d in (1.0, 2.0)}
    crit("C7", "leviers : quotas = v1, retraite = séjour attendu",
         f"quotas × 1,1 : écart max {q_gap:.1e} ; retraite : séjour en 65+ +{dev[1.0]['sejour_65plus_moyen']:.3f} / "
         f"+{dev[2.0]['sejour_65plus_moyen']:.3f} / +{dev[5.0]['sejour_65plus_moyen']:.3f} an pour Δ = 1 / 2 / 5 "
         f"(écart max {max(v['ecart_max_sejour'] for v in dev.values()):.1e}) ; montée {ramp} ; effet 2050 Δ = 1 : "
         f"{eff[1.0]:+.2f} %, Δ = 2 : {eff[2.0]:+.2f} %", ok,
         avant="quotas +226 (un an trop tôt) ; retraite : séjour 65+ +1,31 an pour Δ = 1, infini pour Δ ≥ 5")
    return dict(quotas_gap=q_gap, retraite=dev, effet_2050_pct=eff, montee=ramp)


def c12_regulation_params():
    """Paramètres sourcés de l'axe 1 : θ, répartition des bloqués, exemption, voisins ; défauts abandon et cumul."""
    from jumeau.module import par_profession
    from jumeau.modules.formation import Formation
    from jumeau.modules.sorties import Sorties as So
    est = kine_sector(public_history=True)
    o = est.origin
    z = {"regulation.zones": {"kines": ZONES}}

    def first_year(extra, floor=False, until=None):
        scn = Scenario(params={**z, **extra}, modules=REG).over(est.scenario)
        return run(est.state, est.modules(scn), scn, until or o + 1, floor=floor)

    moved = lambda tr: float(sum(np.clip(x, 0, None).sum() for _, f, _, x in tr.ledger if f == "regulation"))
    m1 = moved(first_year({"regulation.repartition": SALARIAT, "regulation.theta": 1.0}))
    m08 = moved(first_year({"regulation.repartition": SALARIAT, "regulation.theta": 0.8}))
    mex = moved(first_year({"regulation.repartition": SALARIAT, "regulation.theta": 1.0,
                            "regulation.part_exemptee": {"kines": 0.5, "*": 0.0}}))
    base = run(est.state, est.modules(Scenario(modules=REG)), Scenario(modules=REG), H2050, floor=False)
    dflt = first_year({}, until=H2050)                                   # défaut : 100 % voisine, au département
    d_default = float(np.abs(dflt.states[H2050].N - base.states[H2050].N).max())
    so = first_year({"regulation.repartition": {"voisine": 0.0, "salariat": 0.0, "sortie": 1.0}})      # année o + 1
    gone = float(sum(x.sum() for _, f, _, x in so.ledger if f == "regulation_sortie"))
    d_tot = float(so.states[o + 1].N.sum() - base.states[o + 1].N.sum())
    import dataclasses
    com = dataclasses.replace(est.state, level="com")
    no_vois = raises(lambda: run(com, est.modules(Scenario(params=z, modules=REG)), Scenario(params=z, modules=REG).over(est.scenario), o + 1))
    bad_rep = raises(lambda: first_year({"regulation.repartition": {"voisine": 0.5, "salariat": 0.2, "sortie": 0.0}}))
    bad_ab = raises(lambda: est.trajectory(o + 1, Scenario(params={"sorties.part_cumul": {"*": 1.5}})))
    ab = par_profession(Formation.param("abandon").value, ["infirmiers", "dentistes"])
    pc = par_profession(So.param("part_cumul").value, ["infirmiers-liberaux", "sages-femmes", "dentistes"])
    ok = (abs(m08 / m1 - 0.8) < 1e-12 and abs(mex / m1 - 0.5) < 1e-12 and d_default == 0 and gone < 0
          and abs(d_tot - gone) < 1e-6 and all([no_vois, bad_rep, bad_ab])
          and abs(ab[0] - (1 - 0.718 ** (1 / 3))) < 1e-4 and ab[1] == 0 and list(pc) == [0.015, 0.008, 0.047])
    crit("C12", "paramètres sourcés (axe 1) câblés : θ, répartition, exemption, abandon, cumul",
         f"θ 0,8 / 1 → {m08 / m1:.3f} des bloqués ; exemption 50 % → {mex / m1:.3f} ; défaut 100 % voisine au "
         f"département → écart {d_default} ; 100 % sortie, année 1 → Δ total {d_tot:+.1f} = compte {gone:+.1f} ; commune sans "
         f"voisins → {no_vois is not None} ; répartition ≠ 1 → {bad_rep is not None} ; part 1,5 → {bad_ab is not None} ; "
         f"abandon IDE {ab[0]:.4f}, autres {ab[1]} ; cumul IDE/SF/CD {[float(v) for v in pc]}", ok,
         avant="abandon 0, cumul 0,10 pour toutes les professions, plafond strict, destination unique")
    return dict(theta_ratio=m08 / m1, exempt_ratio=mex / m1, sortie_d_total=d_tot, abandon=list(ab), part_cumul=list(pc))


def c13_review3():
    from jumeau.engine import apply
    from jumeau.modules.sorties import sejour_65plus
    t = stock_table(["dentistes"])
    _, fit, o, _ = latest_design("dentistes", t)
    est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
    stacked = raises(lambda: est.trajectory(o + 1, Scenario(events=[Event("entrees.multiplicateur", o + 1, 3.0, "mul")
                                                                    for _ in range(5)])))
    nan = raises(lambda: est.trajectory(o + 1, Scenario(events=[Event("entrees.multiplicateur", o + 1, float("nan"))])))
    ret = raises(lambda: est.trajectory(o + 1, Scenario(events=[Event("sorties.retention", o + 1, 1.3, "mul")])))
    ks = kine_sector(public_history=True)
    scn = Scenario.from_json(Scenario(params={"regulation.zones": {"kines": ZONES}}).to_json())
    after = scn.over(ks.scenario)
    json_ok = "regulation" in after.composition
    zones_ev = raises(lambda: ks.trajectory(o + 1, Scenario(events=[Event("regulation.zones", o + 1, 1.0)])))
    # règle « entrées ≤ sorties » : une année à la main, puis comparaison à une formule indépendante
    reg_scn = Scenario(params={"regulation.zones": {"kines": ZONES}, "regulation.repartition": SALARIAT,
                               "regulation.theta": 1.0}, modules=REG).over(ks.scenario)
    mods = ks.modules(reg_scn)
    x = ks.state.copy()
    for m in mods:
        x = m.prepare(x, reg_scn)
    ctx = Context(ks.origin + 1, ks.origin, reg_scn, x.cells, np.random.default_rng(0), len(x.ages))
    N = x.N
    for m in mods[:-1]:
        for f in m.step(x.__class__(x.cells, x.ages, N, x.year, x.level, x.pool, x._key), ctx):
            new = apply(N, f)
            ctx.deltas[f.name] = new - N
            N = new
    mv = mods[-1].step(x.__class__(x.cells, x.ages, N, x.year, x.level, x.pool, x._key), ctx)[0]
    c = x.cells
    reg = ((c.profession == "kines") & c.territory.isin(ZONES) & (c.sector == "prive")).to_numpy()
    e_pos = np.clip(ctx.deltas["entrees"], 0, None).sum(1)
    exits = -ctx.deltas["sorties"].sum(1)
    expected = np.where(reg, np.maximum(e_pos - exits, 0), 0)
    got = np.zeros(len(c))
    np.add.at(got, mv.src, mv.amount.sum(1))
    rule_gap = float(np.abs(got - expected).max())
    kept = e_pos[reg] - got[reg]
    rule_ok = rule_gap < 1e-9 and (kept <= exits[reg] + 1e-9).all() and (mv.amount >= 0).all()
    # bloqués jamais négatifs avant plancher, jusqu'en 2050
    tr = run(ks.state, mods, reg_scn, H2050, floor=False)
    neg = min(float(st.N[(st.cells.sector == "bloques").to_numpy()].min()) for st in tr.states.values())
    # retraite avec plusieurs tranches ≥ 65 (spécialistes, tranches v1 65–69, 70–74, 75+)
    tsp = stock_table(["specialistes"])
    _, fsp, osp, _ = latest_design("specialistes", tsp)
    esp = twin_of(V1.StockFlowLocal)().fit(tsp, fsp, osp)
    mod = esp.modules(esp.scenario)[[m.name for m in esp.modules(esp.scenario)].index("sorties")]
    a65 = esp.state.ages >= 65
    mk = lambda scn: Context(osp + 1, osp, scn, esp.state.cells, np.random.default_rng(0), len(esp.state.ages))
    s0 = mod.step(esp.state, mk(Scenario()))[0].factor[:, a65]
    s2 = mod.step(esp.state, mk(Scenario(params={"sorties.decalage_retraite": 2.0})))[0].factor[:, a65]
    okc = (1 - s0[:, -1]) > 0
    dstay = sejour_65plus(s2[okc], 0.2) - sejour_65plus(s0[okc], 0.2)
    multi_gap = float(np.abs(dstay - 2.0).max())
    ok = all([stacked, nan, ret, zones_ev]) and json_ok and rule_ok and neg >= -1e-9 and multi_gap < 1e-6
    crit("C13", "troisième revue : bornes, JSON, règle de régulation, retraite multi-tranches",
         f"×3 empilé 5 fois → {stacked is not None} ; NaN → {nan is not None} ; rétention ×1,3 → {ret is not None} ; "
         f"JSON + over garde la régulation {json_ok} ; événement sur zones → {zones_ev is not None} ; règle entrées ≤ "
         f"sorties : écart à la formule {rule_gap:.1e} sur {int(reg.sum())} cellules ; bloqués min {neg:.2e} ; "
         f"retraite Δ = 2, {int(a65.sum())} tranches ≥ 65 : écart de séjour max {multi_gap:.1e}", ok,
         avant="×243 → +14 317 % ; rétention > 1 ; JSON perdait la régulation ; séjour ≠ +Δ ; règle non testée ; "
               "entrées négatives déplacées ; événement sur zones → plantage")


def c14_levers():
    from jumeau.module import REGISTRY as R
    from jumeau.modules.etrangers import part_etrangere, FLUX
    from jumeau.modules.entrees import selecteur_region
    from jumeau.scenario import LEVIERS, FAMILLES
    out, oks = {}, []
    t = stock_table(["dentistes", "pharmaciens"])
    o = int(t.year.max())
    est = twin_of(V1.StockFlowLocal)().fit(t, (o - 5, o), o)
    base = est.trajectory(H2050)
    tot = lambda tr, y, prof=None: float(tr.states[y].N[(tr.states[y].cells.profession == prof).to_numpy()].sum()
                                         if prof else tr.states[y].N.sum())
    # a. identité
    lv = est.trajectory(H2050, Scenario(modules=LEVIERS))
    out["identite"] = float(np.abs(lv.states[H2050].N - base.states[H2050].N).max())
    oks.append(out["identite"] == 0)
    # b. capacité ×1,2 (dentistes, L = 6) : rien avant o + 7, puis effet ; diplômés × 1,2 en régime
    cap = est.trajectory(H2050, Scenario(modules=LEVIERS, events=[Event("formation.capacite", o + 1, 1.2,
                                                                         selector={"profession": "dentistes"})]))
    eff = {y: tot(cap, y, "dentistes") / tot(base, y, "dentistes") - 1 for y in (o + 6, o + 7, H2050)}
    g = [x for y, f, a, x in cap.ledger if f == "formation" and a == "diplomes" and y == H2050][0]
    g0 = [x for y, f, a, x in cap.ledger if f == "formation" and a == "diplomes_reference" and y == H2050][0]
    ph = abs(tot(cap, H2050, "pharmaciens") / tot(base, H2050, "pharmaciens") - 1)
    out["capacite_cd"] = dict(effet_o6=eff[o + 6], effet_o7=eff[o + 7], effet_2050_pct=100 * eff[H2050],
                              diplomes_ratio=float(g["dentistes"] / g0["dentistes"]), pharmaciens=ph,
                              dd76_2050_pct="±9 % pour ±20 % de quotas (DD76, audit des sources axe 1)")
    oks.append(abs(eff[o + 6]) < 1e-12 and eff[o + 7] > 0 and abs(g["dentistes"] / g0["dentistes"] - 1.2) < 1e-9
               and ph < 1e-12)
    # c. abandon IFSI : diviser la perte par deux (ρ 0,718 → 0,859)
    ti = stock_table(["infirmiers-liberaux"])
    oi = int(ti.year.max())
    ei = twin_of(V1.StockFlowLocal)().fit(ti, (oi - 5, oi), oi)
    a1 = 1 - (1 - (1 - 0.718) / 2) ** (1 / 3)
    ab = ei.trajectory(H2050, Scenario(modules=LEVIERS, params={"formation.abandon": {"infirmiers": a1, "*": 0.0}}))
    bi = ei.trajectory(H2050)
    gi = [x for y, f, a, x in ab.ledger if f == "formation" and a == "diplomes" and y == H2050][0]
    gi0 = [x for y, f, a, x in ab.ledger if f == "formation" and a == "diplomes_reference" and y == H2050][0]
    ratio = float(gi.iloc[0] / gi0.iloc[0])
    out["abandon_ifsi"] = dict(diplomes_ratio=ratio, attendu=(1 - (1 - 0.718) / 2) / 0.718,
                               effet_2050_pct=100 * (tot(ab, H2050) / tot(bi, H2050) - 1),
                               er1319="≈ +14 % de places ; équivalent DREES en effectifs ≈ +7,9 % en 2050 (audit des sources axe 1) : écart")
    oks.append(abs(ratio - out["abandon_ifsi"]["attendu"]) < 1e-9 and tot(ab, H2050) > tot(bi, H2050))
    # d. diplômés étrangers ×2 : ajout année 1 = part · entrées⁺ ; une profession à flux nul n'est pas touchée
    et = est.trajectory(o + 1, Scenario(modules=LEVIERS, params={"etrangers.multiplicateur": 2.0}))
    added = float(sum(x.sum() for y, f, a, x in et.ledger if f == "etrangers"))
    e_pos = float(sum(np.clip(x, 0, None).sum() for y, f, a, x in et.ledger if f == "entrees") * 0)  # registre net
    share = part_etrangere(est.hist, est.state, FLUX)
    cd = (est.state.cells.profession == "dentistes").to_numpy()
    et50 = est.trajectory(H2050, Scenario(modules=LEVIERS, params={"etrangers.multiplicateur": 2.0}))
    zero = est.trajectory(H2050, Scenario(modules=LEVIERS, params={"etrangers.multiplicateur": 2.0,
                                                                   "etrangers.flux": {"dentistes": 1300.0, "*": 0.0}}))
    out["etrangers_x2"] = dict(part_cd=float(share[cd][0]), part_ph=float(share[~cd][0]), ajout_annee1=added,
                               effet_2050_cd_pct=100 * (tot(et50, H2050, "dentistes") / tot(base, H2050, "dentistes") - 1),
                               effet_2050_ph_pct=100 * (tot(et50, H2050, "pharmaciens") / tot(base, H2050, "pharmaciens") - 1),
                               ph_flux_nul=tot(zero, H2050, "pharmaciens") - tot(base, H2050, "pharmaciens"))
    oks.append(added > 0 and out["etrangers_x2"]["ph_flux_nul"] == 0 and 0 < share[cd][0] <= 1
               and out["etrangers_x2"]["effet_2050_ph_pct"] > 0)
    # e. départs précoces × 0,5
    pr = est.trajectory(H2050, Scenario(params={"sorties.multiplicateur_precoces": 0.5}))
    out["precoces_x05_pct"] = 100 * (tot(pr, H2050) / tot(base, H2050) - 1)
    oks.append(out["precoces_x05_pct"] > 0)
    # f. quotas régionaux (Auvergne-Rhône-Alpes, 84) : rien hors région
    sel = selecteur_region("84", est.state.cells, "dentistes")
    rq = est.trajectory(H2050, Scenario(events=[evenement_quotas(1.2, o, 6, selector=sel)]))
    c = rq.states[H2050].cells
    inr = c.territory.isin(sel["territory"]).to_numpy() & (c.profession == "dentistes").to_numpy()
    out["quotas_region_84"] = dict(hors_region=float(np.abs(rq.states[H2050].N[~inr] - base.states[H2050].N[~inr]).max()),
                                   region_pct=100 * (rq.states[H2050].N[inr].sum() / base.states[H2050].N[inr].sum() - 1))
    oks.append(out["quotas_region_84"]["hors_region"] == 0 and out["quotas_region_84"]["region_pct"] > 0)
    # g. part des zones régulées (kinés, 5 dép.)
    ks = kine_sector(public_history=True)
    mv = {}
    for pz in (0.0, 0.6, 1.0):
        tr = run(ks.state, ks.modules(Scenario(modules=REG)), Scenario(
            params={"regulation.zones": {"kines": ZONES}, "regulation.repartition": SALARIAT,
                    "regulation.part_zones": {"kines": pz, "*": 1.0}}, modules=REG).over(ks.scenario), ks.origin + 1)
        mv[pz] = float(sum(np.clip(x, 0, None).sum() for _, f, _, x in tr.ledger if f == "regulation"))
    out["part_zones_deplaces_annee1"] = mv
    one = raises(lambda: run(ks.state, ks.modules(Scenario(modules=REG)), Scenario(
        params={"regulation.zones": {"kines": ZONES[:1]}, "regulation.repartition": SALARIAT,
                "regulation.part_zones": {"kines": 0.4, "*": 1.0}}, modules=REG).over(ks.scenario), ks.origin + 1))
    out["une_zone_part_arrondie_a_0"] = one
    oks.append(mv[0.0] == 0 and 0 < mv[0.6] < mv[1.0] and one is None)
    # h. retraite + 1 an : effet en 2050 (le repère DREES ≈ +1 % — plus de 60 ans, tous modes, plafond 67 ans,
    #    dès 2020 — n'est pas comparable ; rapporté, pas testé)
    ret = {}
    for p in ("kines", "infirmiers-liberaux"):
        tp = stock_table([p])
        op = int(tp.year.max())
        ep = twin_of(V1.StockFlowLocal)().fit(tp, (op - 5, op), op)
        ret[p] = 100 * (ep.trajectory(H2050, Scenario(params={"sorties.decalage_retraite": 1.0})).states[H2050].N.sum()
                        / ep.trajectory(H2050).states[H2050].N.sum() - 1)
    out["retraite_plus1_2050_pct"] = ret
    oks.append(all(v > 0 for v in ret.values()))
    # i. familles et métadonnées des leviers
    levers = [(n, p) for n, cls in R.items() for p in cls.params if p.famille]
    numeric = lambda v: (isinstance(v, (int, float)) and not isinstance(v, bool)) or (
        isinstance(v, dict) and v and all(isinstance(x, (int, float)) for x in v.values()))
    bad = [f"{n}.{p.name}" for n, p in levers
           if p.famille not in FAMILLES or not p.source or (numeric(p.value) and p.bounds is None)]
    out["leviers"] = {f"{n}.{p.name}": p.famille for n, p in levers}
    oks.append(not bad and len(levers) >= 10)
    crit("C14", "leviers branchés : identité, effets, délai, région, chiffres cités",
         f"identité LEVIERS {out['identite']} ; capacité CD ×1,2 : 0 en {o + 6}, +{100 * eff[o + 7]:.2f} % en {o + 7}, "
         f"{out['capacite_cd']['effet_2050_pct']:+.1f} % en 2050 (DD76 : ±9 % pour ±20 %) ; IFSI perte ÷ 2 : "
         f"diplômés ×{ratio:.3f}, IDE {out['abandon_ifsi']['effet_2050_pct']:+.1f} % en 2050 (DREES en effectifs ≈ +7,9 % : écart) ; étrangers ×2 : part CD {share[cd][0]:.2f}, "
         f"{out['etrangers_x2']['effet_2050_cd_pct']:+.1f} % CD, {out['etrangers_x2']['effet_2050_ph_pct']:+.1f} % PH (flux nul → 0) ; précoces ×0,5 {out['precoces_x05_pct']:+.1f} % ; "
         f"quotas région 84 : hors région 0, région {out['quotas_region_84']['region_pct']:+.1f} % ; part zones 0/0,6/1 → "
         f"{mv[0.0]:.0f}/{mv[0.6]:.0f}/{mv[1.0]:.0f} déplacés ; retraite +1 : "
         + ", ".join(f"{k} {v:+.2f} %" for k, v in ret.items()) + f" (repère DREES non comparable) ; {len(levers)} leviers, "
         f"familles {sorted(set(out['leviers'].values()))} ; sous-tests {oks}", all(oks), avant="leviers absents ou non branchés")
    return out


def c15_speed():
    """5 professions à la commune (état ventilé par population, ~700 000 cellules), chemin rapide (registre coupé),
    origine → 2050, scénario retraite + quotas : ≤ 2 s mesurées. Le chemin rapide donne le même état que le chemin
    complet (écart 0)."""
    from jumeau import bench_commune as B
    r = B.main()
    e = B.dep_estimators()[0]
    st, hist = B.to_communes(e)
    sc = B.scenario(e.origin)
    mods = build(sc.composition)
    for m in mods:
        m.fit(hist)
    full = run(st, mods, sc, H2050).states[H2050].N
    fast = run(st, mods, sc, H2050, ledger=False, keep=[H2050]).states[H2050].N
    gap = float(np.abs(full - fast).max())
    crit("C15", "vitesse à la commune : 5 professions ≤ 2 s", f"{r['seconds']:.2f} s réel, {r['cpu_seconds']:.2f} s CPU "
         f"(médianes ; {r['cells']} cellules, 24 ans ; charge machine {r['load']:.1f}) ; chemin rapide = chemin complet "
         f"(écart {gap})", r["seconds"] <= 2.0 and gap == 0,
         avant="3,99 s mesurées (registre complet, np.roll, sorties et entrées recalculées chaque année)")
    return dict(r, gap_rapide_complet=gap)


def c16_vivier():
    """Vivier réel (DREES 491) : reconstitution des diplômés, identité en mode levier, effet en mode vivier,
    professions sans série inchangées ; backtest des diplômés et du stock IDE contre la persistance (exploratoire)."""
    from jumeau import vivier as V
    out, oks = {}, []
    ti = stock_table(["infirmiers-liberaux"])
    oi = int(ti.year.max())
    ei = twin_of(V1.StockFlowLocal)().fit(ti, (oi - 5, oi), oi)
    base = ei.trajectory(H2050)
    reel = Scenario(modules=LEVIERS_, params={"formation.vivier": "reel"})
    tr = ei.trajectory(H2050, reel)
    out["identite_reel_levier"] = float(np.abs(tr.states[H2050].N - base.states[H2050].N).max())
    g = {y: float(x.iloc[0]) for y, f, a, x in tr.ledger if a == "diplomes"}
    obs = V.ecoles().set_index(["profession", "year"]).diplomes
    out["diplomes_modele_vs_obs"] = {y: (g[y], float(obs[("infirmiers", y)])) for y in (oi + 1, oi + 2)}
    rec = max(abs(m / o_ - 1) for m, o_ in out["diplomes_modele_vs_obs"].values())
    viv = ei.trajectory(H2050, Scenario(modules=LEVIERS_, params={"formation.vivier": "reel",
                                                                   "lien_formation.mode": "vivier"}))
    out["mode_vivier_ide_2050_pct"] = 100 * (viv.states[H2050].N.sum() / base.states[H2050].N.sum() - 1)
    tc = stock_table(["dentistes"])
    oc = int(tc.year.max())
    ec = twin_of(V1.StockFlowLocal)().fit(tc, (oc - 5, oc), oc)
    vc = ec.trajectory(H2050, Scenario(modules=LEVIERS_, params={"formation.vivier": "reel", "lien_formation.mode": "vivier"}))
    out["dentistes_sans_serie_491"] = float(np.abs(vc.states[H2050].N - ec.trajectory(H2050).states[H2050].N).max())
    oks += [out["identite_reel_levier"] == 0, rec < 0.02, out["mode_vivier_ide_2050_pct"] != 0,
            out["dentistes_sans_serie_491"] == 0]
    # backtest des diplômés 2019-2025, abandon calibré sur 2016-2018 seulement
    bt = {}
    e = V.ecoles().set_index(["profession", "year"])
    for p, L in V.DUREE_ECOLE.items():
        a = V.abandon_annuel(p, (2016, 2018))
        o_ = e.loc[p].diplomes
        ins = e.loc[p].inscrits1
        yrs = [y for y in range(2019, 2026) if not np.isnan(o_.get(y, np.nan))]
        pred = np.array([ins[y - L] * (1 - a) ** L for y in yrs])
        naive = o_[2018] if not np.isnan(o_[2018]) else o_[2017]
        bt[p] = dict(mape_vivier=float(100 * np.mean(np.abs(pred / o_[yrs].to_numpy() - 1))),
                     mape_persistance=float(100 * np.mean(np.abs(naive / o_[yrs].to_numpy() - 1))))
    out["backtest_diplomes_2019_2025"] = bt
    # backtest du stock IDE libéraux, origine 2018 → 2023 (exploratoire, non pré-enregistré)
    t18 = ti[ti.year <= 2023]
    a18 = V.abandon_annuel("infirmiers", (2016, 2018))
    actual = t18[t18.year == 2023].groupby("dep").n.sum()
    keep = t18[t18.year == 2018].groupby("dep").n.sum() >= 30
    res = {}
    for lab, scn in [("stock-flux local", None),
                     ("vivier", Scenario(modules=LEVIERS_, params={"formation.vivier": "reel", "lien_formation.mode": "vivier",
                                                                   "formation.abandon": {"infirmiers": a18, "*": 0.0}}))]:
        est = twin_of(V1.StockFlowLocal)().fit(t18, (2013, 2018), 2018)
        x = est.trajectory(2023, scn).states[2023]
        pred = pd.Series(x.N.sum(1)).groupby(x.cells.territory.to_numpy()).sum()
        ape = (pred / actual - 1).abs()[keep[keep].index] * 100
        res[lab] = dict(mape=float(ape.mean()), national_pct=float(100 * (pred.sum() / actual.sum() - 1)))
    out["backtest_stock_ide_2018_2023"] = res
    crit("C16", "vivier réel (DREES 491) branché",
         f"reel + levier = tendanciel ({out['identite_reel_levier']}) ; diplômés IDE modèle / observés "
         + ", ".join(f"{y} : {m:.0f}/{o_:.0f}" for y, (m, o_) in out["diplomes_modele_vs_obs"].items())
         + f" ; mode vivier IDE 2050 {out['mode_vivier_ide_2050_pct']:+.2f} % ; dentistes (pas de série 491) écart "
         f"{out['dentistes_sans_serie_491']} ; backtest diplômés 2019-2025 (MAPE vivier / persistance) : "
         + ", ".join(f"{p} {v['mape_vivier']:.1f}/{v['mape_persistance']:.1f} %" for p, v in bt.items())
         + " ; stock IDE 2018→2023 (MAPE dép.) : " + ", ".join(f"{k} {v['mape']:.2f} %" for k, v in res.items()),
         all(oks), avant="vivier relatif stationnaire, sans lien aux inscrits réels")
    return out


def c17_age_etrangers():
    """Diplômés à l'étranger : l'ajout entre dans la tranche de 28 ans, total inchangé."""
    from jumeau.modules.etrangers import FLUX
    t = sector_table(["dentistes"])
    o = int(t.year.max())
    est = twin_of(V1.StockFlowLocal)().fit(t, (o - 5, o), o)
    tr = run(est.state, est.modules(Scenario(modules=LEVIERS_)), Scenario(modules=LEVIERS_, params={
        "etrangers.multiplicateur": 2.0}).over(est.scenario), o + 1)
    from jumeau.engine import Context
    ages = est.state.ages
    band = int(np.searchsorted(ages, 28, side="right") - 1)
    mod = [m for m in est.modules(Scenario(modules=LEVIERS_)) if m.name == "etrangers"][0]
    total = float(sum(x.sum() for _, f, _, x in tr.ledger if f == "etrangers"))
    # recalcul direct de la répartition par âge sur une année
    sc = Scenario(modules=LEVIERS_, params={"etrangers.multiplicateur": 2.0}).over(est.scenario)
    ctx = Context(o + 1, o, sc, est.state.cells, np.random.default_rng(0), len(ages))
    ctx.deltas["entrees"] = np.clip(est.hist._cache[("rates", len(est.state.cells))][1], 0, None)
    amt = mod.step(est.state, ctx)[0].amount
    other = float(np.abs(np.delete(amt, band, axis=1)).max())
    ok = abs(total - FLUX["dentistes"]) < 1e-6 and other == 0 and amt[:, band].sum() > 0
    crit("C17", "diplômés à l'étranger entrés à 28 ans", f"tranche {ages[band]}+ seule (hors tranche : {other}) ; "
         f"ajout année 1 = {total:.1f} = flux CD {FLUX['dentistes']:.0f} × (2 − 1)", ok,
         avant="ajout réparti comme les entrées ajustées (tous âges)")
    return dict(tranche=int(ages[band]), total=total)


def c18_infirmiers():
    """Infirmiers dans sector_table : totaux par dep × année = SNDS libéraux (v1) + BTS salariés (v1), privé ⊇ libéraux ;
    projetables par le jumeau (2 secteurs) jusqu'en 2050."""
    t = sector_table(["infirmiers"])
    s = pd.read_parquet("data/processed/stock.parquet")
    lib = s[(s.profession == "infirmiers-liberaux") & ~s.dep.isin(["999", "20"])].groupby(["dep", "year"]).n.sum()
    sal = pd.read_parquet("data/processed/stock_nurses_salaried.parquet")
    sal = sal[~sal.dep.isin(["999", "20"])].groupby(["dep", "year"]).n.sum()
    src = (lib + sal).dropna()
    got = t.groupby(["dep", "year"]).n.sum()
    j = pd.concat([got, src], axis=1, keys=["jumeau", "sources"]).dropna()
    gap = float((j.jumeau - j.sources).abs().max())
    prv = t[t.sector == "prive"].groupby(["dep", "year"]).n.sum()
    lib_ok = bool(((prv - lib).dropna() >= -1e-9).all())
    o = int(t.year.max())
    est = twin_of(V1.StockFlowLocal)().fit(t, (o - 5, o), o)
    tr = est.trajectory(H2050)
    c = tr.states[H2050].cells
    p2050 = float(tr.states[H2050].N[(c.sector == "prive").to_numpy()].sum())
    crit("C18", "infirmiers par secteur (axe 4) cohérents avec SNDS + BTS, projetables",
         f"{len(j)} dep × années, écart max {gap:.1e} ; privé ⊇ libéraux {lib_ok} ; {o} : privé "
         f"{t[(t.year == o) & (t.sector == 'prive')].n.sum():.0f}, public {t[(t.year == o) & (t.sector == 'public')].n.sum():.0f} ; "
         f"privé 2050 (tendanciel) {p2050:.0f}", gap < 1e-6 and lib_ok and len(j) >= 1000 and p2050 > 0,
         avant="infirmiers absents de sector_table (table sans âge ni sexe)")
    return dict(gap=gap, n=len(j), prive_2050=p2050)


def c11_over():
    t = stock_table(["dentistes"])
    _, fit, o, _ = latest_design("dentistes", t)
    est = twin_of(V1.StockFlowLocalPipeline)().fit(t, fit, o)
    p = float(est.predict(H2050).sum())
    b = float(est.trajectory(H2050, Scenario()).states[H2050].N.sum())
    q = float(est.trajectory(H2050, Scenario(events=[evenement_quotas(1.1, o, 6)])).states[H2050].N.sum())
    crit("C11", "un scénario se pose sur le scénario de base (variante filière)",
         f"predict {p:.1f} ; trajectory(Scenario()) {b:.1f} ; quotas × 1,1 : {100 * (q / b - 1):+.2f} %",
         abs(b / p - 1) < 1e-12 and q > b, avant="trajectory(Scenario()) 82 374 contre predict 102 987 ; quotas → −15,2 %")


def c8_aggregation():
    c = pd.read_parquet("data/processed/stock_commune.parquet")
    y = int(c.year.max())
    c = c[c.year == y].assign(sex="ensemble")
    geo = Geography.from_data()
    f = State.from_table(c, y, level="com", sector="prive").to_frame()
    reg_of = geo.table.drop_duplicates("dep").set_index("dep").reg
    direct = {"dep": c.groupby(["profession", "dep"]).n.sum(),
              "reg": c.assign(reg=c.dep.map(reg_of)).groupby(["profession", "reg"]).n.sum(),
              "nat": c.groupby("profession").n.sum()}
    gaps = {}
    for lvl in ["dep", "reg", "nat"]:
        up = geo.up(f, lvl, "com")
        got = up.groupby(["profession", "territory"]).n.sum() if lvl != "nat" else up.groupby("profession").n.sum()
        gaps[lvl] = float(np.abs(got.to_numpy() - direct[lvl].reindex(got.index).to_numpy()).max())
    unmapped = raises(lambda: geo.up(pd.concat([f, f.head(1).assign(territory="99999")]), "dep", "com"))
    # écart externe : CartoSanté (libéraux, par commune) vs RPPS (libéral + mixte, par département), même année
    r = pd.read_parquet("data/processed/stock.parquet")
    r = r[(r.year == y) & (r.mode3 == "liberal_mixte") & r.profession.isin(["dentistes", "kines"]) & (r.source == "RPPS")]
    rp = r.groupby(["profession", "dep"]).n.sum()
    ext = {}
    for p in ["dentistes", "kines"]:
        a, b = direct["dep"][p], rp[p]
        common = a.index.intersection(b.index)
        ext[p] = dict(cartosante=float(a.sum()), rpps=float(b.sum()), ecart_pct=float(100 * (a.sum() / b.sum() - 1)),
                      ecart_dep13=float(a.get("13", 0) - b.get("13", 0)),
                      mape_dep_pct=float((100 * (a[common] / b[common] - 1).abs()).mean()))
    crit("C8", "agrégation commune → national, rattachements vérifiés", f"écarts internes {gaps} ; commune inconnue refusée "
         f"{unmapped is not None} ; CartoSanté vs RPPS {y} : " + ", ".join(f"{p} {v['ecart_pct']:+.1f} %" for p, v in ext.items()),
         all(v == 0 for v in gaps.values()) and unmapped is not None,
         avant="comparaison circulaire ; commune non rattachée gardée en NaN")
    return dict(year=y, communes=int(c.com.nunique()), interne=gaps, externe=ext)


def c9_reproducible():
    t = stock_table(["dentistes", "pharmaciens"])
    est = twin_of(V1.StockFlowLocal)().fit(t, (2021, 2026), 2026)
    comp = ("formation", "vieillissement", "sorties", "entrees")
    scn = Scenario(params={"formation.abandon": 0.05}, modules=comp)

    def grads(pool, mods):
        st = est.state.copy()
        st.pool = pool
        tr = run(st, mods, scn, 2028)
        return float(sum(x.sum() for _, f, a, x in tr.ledger if a == "diplomes" and _ == 2028))

    mods = est.modules(scn)
    p1 = pool_drees()
    g1, g2 = grads(p1, mods), grads(p1 * 2, mods)          # mêmes instances, deux runs
    fresh = build(comp)
    for m in fresh:
        m.fit(est.hist)
    g2_fresh = grads(p1 * 2, fresh)
    crit("C9", "aucun état partagé entre deux runs", f"diplômés 2028 : vivier ×1 {g1:.0f}, vivier ×2 {g2:.0f}, "
         f"instances neuves {g2_fresh:.0f}", g2 == g2_fresh and abs(g2 - 2 * g1) < 1e-6,
         avant="Formation._intake gardé d'un run à l'autre")


def c10_ageing():
    f = fractions([0, 40, 50, 55, 60], [39, 49, 54, 59, 99])
    x = np.array([[150.0, 100, 50, 50, 80]])
    y = apply(x, Shift("v", f))
    ok = abs(y.sum() - x.sum()) < 1e-12 and np.isclose(y[0, 1], 100 - 10 + 150 / 15)
    crit("C10", "vieillissement à largeurs variables", f"fractions {np.round(f, 3).tolist()} ; total {x.sum()} → {y.sum()}",
         ok, avant="1/5 codé en dur")


def timing(reps=5):
    scn = lambda o: Scenario("retraite +1, quotas ×1,1", events=[Event("sorties.decalage_retraite", o + 1, 1.0),
                                                                    evenement_quotas(1.1, o, 5)])
    ests = []
    for p in PROFS:
        t = stock_table([p])
        _, fit, o, _ = latest_design(p, t)
        ests.append(twin_of(V1.StockFlowLocal)().fit(t, fit, o))
        ests[-1].trajectory(o + 1)
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for e in ests:                                   # run() direct : trajectory() met en cache par scénario
            sc = scn(e.origin).over(e.scenario)
            run(e.state, e.modules(sc), sc, H2050)
        ts.append(time.perf_counter() - t0)
    out = dict(dep_7_professions_s=float(np.median(ts)), dep_cells=int(sum(len(e.state.cells) for e in ests)))
    e = ests[PROFS.index("kines")]
    k = 35_000 // e.state.cells.territory.nunique() + 1
    for nsec in (1, 2):
        cells = pd.concat([e.state.cells.assign(territory=e.state.cells.territory + f"_{i}", sector=f"s{j}")
                           for i in range(k) for j in range(nsec)], ignore_index=True)
        big = State(cells, e.state.ages, np.tile(e.state.N, (k * nsec, 1)), e.state.year)
        hist = History(e.hist.table, e.origin, e.fit_years, options=e.hist.options)
        S, I, P = e.hist._cache[("rates", len(e.state.cells))]
        hist._cache[("rates", len(cells))] = tuple(np.tile(a, (k * nsec, 1)) for a in (S, I, P))
        mods = build(("vieillissement", "sorties", "entrees"))
        for m in mods:
            m.fit(hist)
        ts = []
        for _ in range(3):
            t0 = time.perf_counter()
            run(big, mods, scn(e.origin), H2050)
            ts.append(time.perf_counter() - t0)
        out[f"commune_1prof_{nsec}sect_s"] = float(np.median(ts))
        out[f"commune_1prof_{nsec}sect_cells"] = len(cells)
    out["commune_5prof_2sect_s_extrapole"] = 5 * out["commune_1prof_2sect_s"]
    crit("T", "temps de recalcul jusqu'en 2050", f"{1000 * out['dep_7_professions_s']:.0f} ms (dép., 7 professions) ; "
         f"{out['commune_1prof_2sect_s']:.2f} s (taille commune, 1 profession × 2 secteurs) ; "
         f"≈ {out['commune_5prof_2sect_s_extrapole']:.1f} s extrapolé à 5 professions", True)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    discover()
    c1_reproduction()
    regul = c2_composition()
    c3_plugin()
    c4_demography()
    c5_dependencies()
    c6_scenario()
    levers = c7_levers()
    agg = c8_aggregation()
    c9_reproducible()
    c10_ageing()
    c11_over()
    c12_regulation_params()
    c13_review3()
    leviers = c14_levers()
    vitesse = c15_speed()
    viv = c16_vivier()
    age = c17_age_etrangers()
    inf = c18_infirmiers()
    tm = timing()
    res = dict(infirmiers=inf, vivier_reel=viv, age_etrangers=age, vitesse_commune=vitesse, leviers_branches=leviers, criteres=RESULTS, regulation=regul, leviers=levers, agregation=agg, temps=tm,
               modules={n: [p.__dict__ for p in c.params] for n, c in REGISTRY.items()
                        if n not in ("factice", "espion", "double", "lecteur_diplomes")})
    (OUT / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    failed = [r["id"] for r in RESULTS if not r["ok"]]
    print("échecs :", failed or "aucun")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
