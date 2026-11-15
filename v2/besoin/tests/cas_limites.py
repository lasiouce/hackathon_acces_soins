"""Cas limites de la dérivation du besoin (§4) pour M1–M3, chacun avec un contrôle qui doit échouer.

  L1 profil plat   ω ≡ 1 ⇒ C(M1) = C(M0) à 10⁻⁹ près (5 professions de l'offre servies par M1)
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


CAS_LIMITES = [l1_profil_plat]
