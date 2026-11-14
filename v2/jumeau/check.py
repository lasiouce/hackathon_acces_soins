"""Critères d'acceptation de l'axe 0, écrits pour pouvoir échouer.

Run (racine du dépôt) : PYTHONPATH=v2 uv run python -m jumeau.check   -> v2/artifacts/a0_jumeau/results.json
Code de sortie 1 si un critère échoue. Chaque critère porte la valeur mesurée par la revue adversariale
sur le code d'avant (`avant`), quand elle existe : c'est la preuve que le test sait échouer.

  C1 reproduction   stock-flux v1 réécrit en modules : predict, et par cellule × âge × année → 2050
  C2 composition    un scénario passé par twin_of exécute ses modules (régulation : effet non nul)
  C3 plug-in        module factice déposé hors du paquet, exécuté par twin_of ; module inconnu refusé
  C4 démographie    régulation vers un public vide, mêmes taux : le total ne bouge pas (déplacement pur)
  C5 dépendances    composition sans le flux lu, lecture non déclarée, double producteur : refusés
  C6 scénario       clé mal orthographiée, opération ou axe inconnus : refusés ; aller-retour JSON identique
  C7 leviers        retraite + 1 an et quotas × 1,1 contre le vrai chemin v1 (app/levers.project_flow)
  C8 agrégation     commune -> dep -> rég -> national exact ; unité non rattachée refusée ; écart au RPPS mesuré
  C9 reproductible  deux runs sur les mêmes instances ne partagent pas d'état (formation)
  C10 vieillissement tranches de largeurs différentes : fractions par tranche, total conservé
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
from jumeau.modules.entrees import evenement_quotas
from jumeau.modules.formation import pool_drees
from jumeau.modules.vieillissement import fractions
from jumeau.scenario import Event, Scenario
from jumeau.state import Geography, State

OUT = Path("v2/artifacts/a0_jumeau")
STOCK_FLOW = [V1.StockFlowNational, V1.StockFlowLocal, V1.StockFlowLocalRecent, V1.StockFlowLocalPipeline,
              V1.StockFlowLocalTrendEntries]
PROFS = ["sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers-liberaux", "infirmiers-salaries", "specialistes"]
H2050 = 2050
ZONES = ["06", "13", "34", "66", "83"]        # illustration (densité kiné élevée), pas le zonage conventionnel
REG = ("vieillissement", "sorties", "entrees", "regulation")
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
    return twin_of(V1.StockFlowLocal, Scenario(modules=REG), sectors=("public",))().fit(t, (o - 5, o), o)


def c2_composition():
    est = kine_sector(public_history=True)
    base = est.trajectory(H2050, Scenario(modules=REG))
    reg = est.trajectory(H2050, Scenario("régulation kinés", params={"regulation.zones": {"kines": ZONES}}, modules=REG))
    c = reg.states[H2050].cells
    zp = ((c.sector == "prive") & c.territory.isin(ZONES)).to_numpy()
    pub = (c.sector == "public").to_numpy()
    d = float(reg.states[H2050].N[zp].sum() - base.states[H2050].N[zp].sum())
    err = raises(lambda: est.trajectory(2030, Scenario(params={"regulation.zones": {"kines": ZONES}})))
    crit("C2", "les modules du scénario passent par twin_of", f"privé dans les zones 2050 : {d:+.0f} ; "
         f"régulation hors composition → {err}", d < 0 and err is not None, avant="écart 0,0 avec le tendanciel")
    return dict(prive_zones_base=float(base.states[H2050].N[zp].sum()), prive_zones_regul=float(reg.states[H2050].N[zp].sum()),
                public_base=float(base.states[H2050].N[pub].sum()), public_regul=float(reg.states[H2050].N[pub].sum()),
                total_base=float(base.states[H2050].N.sum()), total_regul=float(reg.states[H2050].N.sum()),
                moved=float(sum(np.clip(x, 0, None).sum() for _, f, _, x in reg.ledger if f == "regulation")))


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
        for scn in (Scenario(modules=REG), Scenario(params={"regulation.zones": {"kines": ZONES}}, modules=REG)):
            tot.append(run(est.state, est.modules(scn), scn, H2050, floor=floor).states[H2050].N.sum())
        out[floor] = float(tot[1] - tot[0])
    crit("C4", "la régulation déplace sans créer (public vide, taux de repli)", f"Δ total 2050 sans plancher "
         f"{out[False]:+.1e} ; avec plancher {out[True]:+.3f} personne ; {est.hist.borrowed} cellules en repli",
         abs(out[False]) < 1e-6, avant="+822 kinés en 2050")


class Espion(Module):
    name, order, needs = "espion", 25, ()

    def step(self, state, ctx):
        ctx.delta(self, "sorties")
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
    crit("C5", "dépendances déclarées et vérifiées", f"sans `sorties` → {a} | double producteur → {b is not None} | "
         f"lecture non déclarée → {c is not None}", all([a, b, c]),
         avant="régulation sans `sorties` : tous les entrants bloqués, sans erreur")


def c6_scenario():
    t = stock_table(["dentistes"])
    _, fit, o, _ = latest_design("dentistes", t)
    est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
    typo = raises(lambda: est.trajectory(2030, Scenario(params={"sorties.decalage_retaite": 1.0})))
    badop = raises(lambda: est.trajectory(2030, Scenario(events=[Event("sorties.decalage_retraite", o + 1, 1.0, "pow")])))
    axis = raises(lambda: est.trajectory(2030, Scenario(events=[Event("sorties.decalage_retraite", o + 1, 1.0,
                                                                      selector={"departement": "13"})])))
    scn = Scenario("retraite + quotas", events=[Event("sorties.decalage_retraite", o + 1, 1.0, selector={"territory": ["13", "75"]}),
                                                evenement_quotas(1.1, o, 6)], seed=7)
    back = Scenario.from_json(scn.to_json())
    gap = float(np.abs(est.trajectory(H2050, scn).states[H2050].N - est.trajectory(H2050, back).states[H2050].N).max())
    crit("C6", "scénario validé et sérialisable", f"faute de frappe → {typo} | opération → {badop is not None} | "
         f"axe → {axis is not None} | aller-retour JSON écart {gap}",
         all([typo, badop, axis]) and gap == 0 and back.to_json() == scn.to_json(),
         avant="clé mal orthographiée ignorée : résultat = tendanciel")


def c7_levers():
    sys.path.insert(0, "app")
    import levers as LV
    t = stock_table(["dentistes"])
    _, fit, o, _ = latest_design("dentistes", t)
    v1 = V1.StockFlowLocal().fit(t, fit, o)
    est = twin_of(V1.StockFlowLocal)().fit(t, fit, o)
    years = list(range(o + 1, H2050 + 1))
    out = {}
    for lab, vals, scn in [("retraite + 1 an", {"retirement": 1.0}, Scenario(events=[Event("sorties.decalage_retraite", o + 1, 1.0)])),
                           ("quotas × 1,1 (L = 6)", {"entries": 1.1}, Scenario(events=[evenement_quotas(1.1, o, LV.LAG["dentistes"])]))]:
        a = LV.project_flow(v1, "dentistes", H2050, vals)
        b = est.trajectory(H2050, scn).totals(("territory",))
        b.index.name = a.index.name
        out[lab] = dict(gap=float((a[years] - b.reindex(a.index)[years]).abs().max().max()),
                        effet_2050_pct=float(100 * (a[H2050].sum() / est.trajectory(H2050).states[H2050].N.sum() - 1)))
    crit("C7", "leviers = chemin v1 (app/levers.project_flow)",
         " ; ".join(f"{k} : écart max {v['gap']}, effet {v['effet_2050_pct']:+.2f} %" for k, v in out.items()),
         all(v["gap"] < 1e-9 for v in out.values()), avant="quotas : +226 dentistes en 2050 (un an trop tôt)")
    return out


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
        for e in ests:
            e.trajectory(H2050, scn(e.origin))
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
    tm = timing()
    res = dict(criteres=RESULTS, regulation_kines=regul, leviers=levers, agregation=agg, temps=tm,
               modules={n: [p.__dict__ for p in c.params] for n, c in REGISTRY.items()
                        if n not in ("factice", "espion", "double")})
    (OUT / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    failed = [r["id"] for r in RESULTS if not r["ok"]]
    print("échecs :", failed or "aucun")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
