"""Les sept critères de l'axe 0 du module de besoin (voir __main__.py)."""
import hashlib
import tempfile
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from sante import estimators as V1
from jumeau.estimators import twin_of
from jumeau.history import sector_table
from jumeau.state import State

from besoin.couverture import SANS_COUVERTURE, agrege, couverture, offre
from besoin.cube import Cube, Population, mapping
from besoin.estimateurs.m0 import M0
from besoin.interface import PROFESSIONS, discover
from besoin.sortie import besoin_api
from besoin.transferts import Transfert, appliquer, l23

H, REF = 2050, 2026
RESULTS = []


def crit(cid, critere, mesure, ok, controle=None):
    RESULTS.append(dict(id=cid, critere=critere, mesure=mesure, ok=bool(ok), controle=controle))
    print(f"{'OK ' if ok else 'ÉCHEC'} {cid} {critere} : {mesure}" + (f"  (contrôle : {controle})" if controle else ""),
          flush=True)


@lru_cache(maxsize=None)
def etat(profs: tuple) -> dict:
    """Trajectoire tendancielle du jumeau (stock-flux à taux locaux, comme bench_commune), origine comprise."""
    t = sector_table(list(profs))
    o = int(t.year.max())
    est = twin_of(V1.StockFlowLocal)().fit(t, (o - 5, o), o)
    return {o: est.state, **est.trajectory(H).states}


def empreinte(e: dict) -> str:
    h = hashlib.sha256()
    for y in sorted(e):
        h.update(np.ascontiguousarray(e[y].N).tobytes())
        h.update(pd.util.hash_pandas_object(e[y].cells, index=False).to_numpy().tobytes())
    return h.hexdigest()


def densite_pandas(e: dict, scenario="central") -> pd.DataFrame:
    """Chemin indépendant : format long du jumeau, secteur privé, sur la population lue à nouveau du parquet."""
    long = pd.concat([s.to_frame() for y, s in e.items() if y >= REF], ignore_index=True)
    long = long[long.sector == "prive"]
    S = long.groupby(["profession", "territory", "year"]).n.sum()
    p = pd.read_parquet("data/processed/population.parquet")
    P = p[p.scenario == scenario].groupby(["dep", "year"])["pop"].sum().rename_axis(["territory", "year"])
    d = (S / P.reindex(S.index.droplevel("profession")).to_numpy()).rename("d").reset_index()
    d["d26"] = d.groupby(["profession", "territory"]).d.transform(lambda x: x[d.loc[x.index, "year"] == REF].iloc[0])
    return d


def b1_m0():
    pires, ctrl = {}, {}
    for p in PROFESSIONS:
        e = etat((p,))
        r = besoin_api(e)
        d = densite_pandas(e)
        C = pd.DataFrame(r["couverture_base"][p], index=r["territories"], columns=r["years"]).stack()
        C.index.names = ["territory", "year"]
        x = d.set_index(["territory", "year"])
        want = (x.d / x.d26)
        got = C.reindex(want.index)
        fin = np.isfinite(want.to_numpy())
        same_nan = bool((np.isfinite(got.to_numpy()) == fin).all())
        pires[p] = float(np.abs(got.to_numpy()[fin] - want.to_numpy()[fin]).max()) if same_nan else float("inf")
        # contrôle : la même densité sur un autre scénario de population doit dépasser la tolérance
        xh = densite_pandas(e, "pop_haute").set_index(["territory", "year"])
        ctrl[p] = float(np.nanmax(np.abs(got.to_numpy() - (xh.d / xh.d26).reindex(want.index).to_numpy())))
    worst = max(pires.values())
    crit("B1", "M0 : C = densité / densité₂₀₂₆ (5 professions, dép., 2026–2050)",
         f"écart max {worst:.2e} ; " + ", ".join(f"{k} {v:.1e}" for k, v in pires.items()), worst < 1e-9,
         f"population Omphale « haute » au lieu de « centrale » : écart {min(ctrl.values()):.2e} (≥ 1e-9 attendu)")


def b2_identite():
    e = etat(("kines", "pharmaciens"))
    h0 = empreinte(e)
    S_before = offre(e).values.copy()
    pop = Population.load()
    r0 = besoin_api(e, pop)
    r_zero = besoin_api(e, pop, transferts=[l23(s_inf=0.0), Transfert("t", "kines", "pharmaciens", 0.3, 2.0, 0.0, 2.0,
                                                                         2027, 0.5)])
    r_on = besoin_api(e, pop, transferts=[l23(), Transfert("t", "kines", "pharmaciens", 0.3, 2.0, 0.5, 2.0, 2027, 0.5)])
    h1 = empreinte(e)
    S_after = offre(e).values
    eq = lambda a, b: all(np.array_equal(np.array(a[k], float), np.array(b[k], float), equal_nan=True) for k in a)
    ident = dict(N=h0 == h1, offre=np.array_equal(S_before, S_after), besoin=eq(r0["besoin"], r_zero["besoin"]),
                 couverture=eq(r0["couverture"], r_zero["couverture"]),
                 base=eq(r0["couverture_base"], r_on["couverture_base"]))
    moved = not eq(r0["couverture"], r_on["couverture"])
    crit("B2", "transferts à 0 : effectifs, offre, B et C identiques bit à bit ; N jamais écrit",
         ", ".join(f"{k} {'=' if v else '≠'}" for k, v in ident.items()), all(ident.values()) and moved,
         f"transfert actif : couverture {'≠' if moved else '='} base (≠ attendu)")


def b3_additivite():
    e = etat(("kines", "pharmaciens"))
    pop = Population.load()
    est = M0().fit(pop, e, REF)
    years = list(range(REF, H + 1))
    Bd = est.predict(pop, e, years)
    Bc = est.predict(pop.ventile(), e, years)
    rel = lambda a, b: float(np.abs(a.values - b.values).max() / np.abs(b.values).max())
    cd = Bc.up("dep", mapping("com", "dep"))
    errs = {"com→dep": rel(cd, Bd), "com→reg": rel(Bc.up("reg"), Bd.up("reg")),
            "dep→nat": rel(Bd.up("nat"), Bc.up("nat")), "pop com→dep": float(
                np.abs(pop.ventile().up("dep").total() - pop.total()).max() / pop.total().max())}
    # C régional : rapport des sommes, recalculé à la main ; la moyenne des C départementaux sert de contrôle
    S = offre(e, years)
    Creg = agrege(S, Bd, "reg")
    m = mapping("dep", "reg")
    Sd, Bdd = S.to_frame("S"), Bd.sel(professions=list(S.professions)).to_frame("B")
    f = Sd.merge(Bdd, on=["profession", "territory", "year"]).assign(reg=lambda x: x.territory.map(m))
    g = f.groupby(["profession", "reg", "year"])[["S", "B"]].sum()
    g["r"] = g.S / g.B
    want = g.r / g.r.xs(REF, level="year").reindex(g.index.droplevel("year")).to_numpy()
    got = Creg.to_frame("C").set_index(["profession", "territory", "year"]).C.reindex(want.index)
    errC = float(np.abs(got.to_numpy() - want.to_numpy()).max())
    Cdep = couverture(S, Bd).to_frame("C").assign(reg=lambda x: x.territory.map(m))
    mean = Cdep.groupby(["profession", "reg", "year"]).C.mean().reindex(want.index)
    ctrl = float(np.abs(mean.to_numpy() - want.to_numpy()).max())
    worst = max(errs.values())
    crit("B3", "additivité de B entre échelles (10⁻⁹ relatif) ; C agrégé par sommes",
         ", ".join(f"{k} {v:.1e}" for k, v in errs.items()) + f" ; C rég. {errC:.1e}", worst < 1e-9 and errC < 1e-9,
         f"moyenne des C dép. au lieu du rapport des sommes : écart {ctrl:.2e} (≥ 1e-9 attendu)")


def b4_conservation():
    e = etat(("kines", "pharmaciens"))
    pop = Population.load()
    years = list(range(REF, H + 1))
    B = M0().fit(pop, e, REF).predict(pop, e, years)
    trs = [l23(k=0.7, mu=0.1, s_inf=0.8, a=0.05), Transfert("kines→PH", "kines", "pharmaciens", 0.2, 1.5, 0.8, 2.0,
                                                            2028, 0.25)]
    B1, det = appliquer(B, trs)
    lhs = B1.values.sum(axis=(0, 1)) - B.values.sum(axis=(0, 1))

    def attendu(k_bias=0.0):
        out = np.zeros(len(years))
        for tr in trs:                                    # sources disjointes des cibles : B_A = B avant transfert
            BA = B.values[B.p(tr.source)].sum(axis=0)
            raw = tr.s_inf * (1 - np.exp(-np.maximum(np.array(years) - tr.t0, 0) / tr.tau)) * (np.array(years) >= tr.t0)
            sa = np.maximum(raw - tr.s_deja, 0) * tr.a           # L23 : seule la part au-delà de s(2026) agit (P1-4)
            k = tr.k + k_bias
            out += sa * BA * (k - 1) + tr.mu * sa * BA * k
        return out
    err = float(np.abs(lhs - attendu()).max())
    ctrl = float(np.abs(lhs - attendu(1e-3)).max())
    refus = []
    for bad in [lambda: Transfert("x", "kines", "pharmaciens", 0.9, 1, 1.2, 1, 2026),     # s·a = 1,08 > 1
                lambda: Transfert("x", "kines", "pharmaciens", 0.5, 0, 0.5, 1, 2026),     # k = 0
                lambda: Transfert("x", "kines", "medecine-generale", 0.5, 1, 0.5, 1, 2026)]:
        try:
            bad()
            refus.append(False)
        except ValueError:
            refus.append(True)
    pos = bool((B1.values >= 0).all())
    crit("B4", "conservation ΣB' − ΣB = s·a·B_A·(k−1) + m (10⁻⁶ ETP), contraintes refusées",
         f"écart max {err:.2e} ETP sur {np.abs(lhs).max():.0f} ETP déplacés ; refus {sum(refus)}/3 ; B' ≥ 0 {pos}",
         err < 1e-6 and all(refus) and pos, f"k biaisé de 10⁻³ : écart {ctrl:.2e} ETP (≥ 1e-6 attendu)")


def b5_latence(n=60):
    pop = Population.load()
    out = {}
    for p in PROFESSIONS:
        e = etat((p,))
        besoin_api(e, pop)                                 # chauffe (import, caches)
        ts = []
        for _ in range(n):
            t0 = time.perf_counter()
            besoin_api(e, pop, transferts=[l23()] if p == "pharmaciens" else ())
            ts.append((time.perf_counter() - t0) * 1e3)
        out[p] = (float(np.percentile(ts, 50)), float(np.percentile(ts, 95)))
    p95 = max(v[1] for v in out.values())
    crit("B5", f"latence besoin_api au département, une profession, {REF}–{H}, n = {n}",
         f"95ᵉ centile max {p95:.2f} ms ; " + ", ".join(f"{k} p50 {a:.2f} / p95 {b:.2f}" for k, (a, b) in out.items()),
         p95 < 5.0, "budget 5 ms (supposé, hérité du plan)")


def b6_plugin():
    root = Path(__file__).resolve().parents[1]
    files = lambda: {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(root.rglob("*.py"))}
    before = files()
    e = etat(("kines",))
    with tempfile.TemporaryDirectory() as d:
        Path(d, "m0_double.py").write_text(
            "from besoin.estimateurs.m0 import M0\nfrom besoin.interface import register\n\n\n"
            "@register\nclass M0Double(M0):\n    name = 'M0-double'\n    norme = 'test : deux fois M0'\n\n"
            "    def predict(self, pop, etat=None, years=None):\n"
            "        from dataclasses import replace\n        B = super().predict(pop, etat, years)\n"
            "        return replace(B, values=2 * B.values)\n")
        r = besoin_api(e, estimateur="M0-double", plugins=[d])
    base = besoin_api(e)
    double = np.allclose(np.array(r["besoin"]["kines"]), 2 * np.array(base["besoin"]["kines"]), rtol=1e-12)
    same_c = np.array_equal(np.array(r["couverture"]["kines"]), np.array(base["couverture"]["kines"]), equal_nan=True)
    try:
        besoin_api(e, estimateur="inconnu")
        refuse = False
    except KeyError:
        refuse = True
    unchanged = files() == before
    crit("B6", "estimateur ajouté hors du paquet, servi par nom ; aucun fichier de v2/besoin modifié",
         f"servi {r['estimateur']}, B × 2 {double}, C identique (r̄ s'annule) {same_c}, inconnu refusé {refuse}, "
         f"{len(before)} fichiers inchangés {unchanged}", double and same_c and refuse and unchanged,
         f"registre : {sorted(discover())}")


def b7_o2():
    e = etat(("kines", "pharmaciens"))
    r = besoin_api(e, transferts=[l23()])
    keys = {k for part in ("besoin", "couverture", "couverture_base") for k in r[part]}
    leak = sorted(keys & SANS_COUVERTURE)
    st = e[REF]
    mg = State(st.cells.assign(profession="medecine-generale"), st.ages, st.N, st.year, st.level)
    sp = State(st.cells.assign(profession="specialistes"), st.ages, st.N, st.year, st.level)
    S = offre(e, [REF])
    fake = Cube(np.array(["medecine-generale"]), S.territories, S.years, S.values[:1], S.level)
    B = M0().fit(Population.load(), e, REF).predict(Population.load(), e, [REF])
    chemins = {"offre MG": lambda: offre({REF: mg}), "offre spécialistes": lambda: offre({REF: sp}),
               "couverture MG": lambda: couverture(fake, B), "agrege MG": lambda: agrege(fake, B, "reg"),
               "cible MG": lambda: l23().__class__("x", "kines", "medecine-generale", 0.1, 1, 0.1, 1, 2026),
               "cible spécialistes": lambda: Transfert("x", "kines", "specialistes", 0.1, 1, 0.1, 1, 2026)}
    refus = {}
    for k, f in chemins.items():
        try:
            f()
            refus[k] = False
        except ValueError:
            refus[k] = True
    source_ok = len(r["transferts"]) == 1 and r["transferts"][0]["source"] == "medecine-generale" \
        and max(r["transferts"][0]["etp_liberes_source"]) > 0
    crit("B7", "aucun indice de couverture pour la MG ni les spécialistes (O2) ; MG source permise",
         f"clés de sortie hors O2 {leak or 'aucune'} ; chemins refusés {sum(refus.values())}/{len(refus)} ; "
         f"ETP de MG libérés rapportés {source_ok}", not leak and all(refus.values()) and source_ok,
         ", ".join(k for k, v in refus.items() if not v) or "tous les chemins refusés")


CRITERES = [b1_m0, b2_identite, b3_additivite, b4_conservation, b5_latence, b6_plugin, b7_o2]
