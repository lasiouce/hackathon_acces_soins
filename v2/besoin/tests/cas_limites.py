"""Cas limites de la dérivation du besoin (§4) pour M1–M3, chacun avec un contrôle qui doit échouer.

  L1 profil plat   ω ≡ 1 ⇒ C(M1) = C(M0) à 10⁻⁹ près (5 professions de l'offre servies par M1)
  L2 offre nulle   offre mise à 0 dans des départements ⇒ B(M2a), B(M2b), B(M3) > 0 partout, et inchangé
  L3 O2            M1, M2a, M3 servis par besoin_api : aucun indice de couverture pour la MG ni les spécialistes
"""
import numpy as np

from besoin.couverture import couverture, offre
from besoin.cube import Population
from besoin.estimateurs.m0 import M0
from besoin.estimateurs.m1 import M1, CODE
from besoin.tests.criteres import REF, crit, etat


def l1_profil_plat():
    pop = Population.load()
    pires, ctrl = {}, {}
    for p in CODE:
        e = etat((p,))
        yrs = [y for y in sorted(e) if y >= REF]
        S = offre(e, yrs)
        C0 = couverture(S, M0().fit(pop, e, REF).predict(pop, e, yrs), REF)
        plat = M1({p: np.ones((len(pop.sexes), len(pop.ages)))})
        C1 = couverture(S, plat.fit(pop, e, REF).predict(pop, e, yrs), REF)
        Ca = couverture(S, M1().fit(pop, e, REF).predict(pop, e, yrs), REF)
        a, b, c = (x.values[x.p(p)] for x in (C0, C1, Ca))
        fin = np.isfinite(a)
        pires[p] = float(np.abs(a[fin] - b[fin]).max()) if (np.isfinite(b) == fin).all() else float("inf")
        ctrl[p] = float(np.nanmax(np.abs(a - c)))                     # contrôle : le vrai profil doit s'écarter
    crit("L1", "profil plat ⇒ C(M1) = C(M0) (dép., 2026–2050)", f"écart max {max(pires.values()):.2e}",
         max(pires.values()) < 1e-9 and min(ctrl.values()) > 1e-9,
         f"profil APL : écart min sur les professions {min(ctrl.values()):.2e}")


def _sans_offre(e: dict, deps) -> dict:
    """Copie de la trajectoire où l'effectif est nul dans `deps` (toutes années)."""
    from dataclasses import replace
    out = {}
    for y, st in e.items():
        N = st.N.copy()
        N[st.cells.territory.astype(str).isin(deps).to_numpy()] = 0
        out[y] = replace(st, N=N)
    return out


def _estimateurs():
    from besoin.estimateurs.m2a import M2a
    from besoin.estimateurs.m2b import M2b
    out = [M2a, M2b]
    try:
        from besoin.estimateurs.m3 import M3
        out.append(M3)
    except ImportError:
        pass
    return out


def l2_offre_nulle():
    pop = Population.load()
    e = etat(("kines",))
    yrs = [y for y in sorted(e) if y >= REF]
    deps = ["23", "48", "05"]
    e0 = _sans_offre(e, deps)
    S0 = offre(e0, yrs)
    nul = bool((S0.values[S0.p("kines"), np.isin(S0.territories, deps)] == 0).all())
    res, ctrl = {}, None
    for cls in _estimateurs():
        B = cls().fit(pop, e, REF).predict(pop, e0, yrs)
        Bref = cls().fit(pop, e, REF).predict(pop, e, yrs)
        i = np.isin(B.territories, deps)
        res[cls.name] = bool((B.values[:, i] > 0).all() and np.allclose(B.values, Bref.values, rtol=1e-12))
    # contrôle : un « besoin » égal à l'offre observée s'annule là où l'offre est nulle
    ctrl = float(S0.values[S0.p("kines"), np.isin(S0.territories, deps)].max())
    crit("L2", "offre nulle ⇒ B > 0 (M2a, M2b, M3), indépendant de l'offre locale", f"{res} ; offre nulle {nul}",
         nul and all(res.values()) and ctrl == 0, f"besoin = offre : max {ctrl} dans les départements sans offre")


def l3_o2():
    from besoin.couverture import SANS_COUVERTURE
    from besoin.sortie import besoin_api
    e = etat(("kines",))
    fuites = {}
    for name in ["M1", "M2a"] + (["M3"] if any(c.name == "M3" for c in _estimateurs()) else []):
        r = besoin_api(e, estimateur=name)
        fuites[name] = sorted(set(r["couverture"]) & SANS_COUVERTURE)
    crit("L3", "aucun C pour la MG ni les spécialistes (M1, M2a, M3)", f"fuites {fuites}",
         not any(fuites.values()), "M1 produit B_MG (source O2) : le cube le contient, la couverture non")


CAS_LIMITES = [l1_profil_plat, l2_offre_nulle, l3_o2]
