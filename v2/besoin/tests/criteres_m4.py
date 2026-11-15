"""Critères de M4 (2SFCA, paliers DREES), écrits pour pouvoir échouer ; lancés par besoin.tests avec ceux de l'axe 0.

  M4a conservation  Σ_i P_i A_i = Σ_j S_j à 10⁻⁹ relatif, distancier réel, 4 professions, offre et besoin tirés au sort
  M4b rayon 0       seules les paires à 0 km : A_i = S_i / P_i (densité de la commune) à 10⁻¹²
  M4c rayon ∞       tous les poids à 1 : A_i = Σ S / Σ P (densité nationale) pour toute commune, à 10⁻¹²
  M4d O2            aucune accessibilité ni couverture pour la MG ou les spécialistes
Chaque critère porte un contrôle : la même mesure sur une entrée faussée doit dépasser la tolérance.
"""
import numpy as np
import pandas as pd
from scipy import sparse

from besoin.cube import Cube
from besoin.estimateurs.m4 import CODE, M4, _paires, deux_etapes, matrice
from besoin.tests.criteres import crit

APL = "v2/data/processed/besoin/apl_commune.parquet"


def _communes(n=None):
    a = pd.read_parquet(APL, columns=["com", "annee"])
    c = np.sort(a.com[a.annee == 2024].unique())
    return c if n is None else c[:n]


def m4a_conservation():
    com = _communes()
    rng = np.random.default_rng(20261115)
    pires, ctrl = {}, {}
    for p, code in CODE.items():
        W = matrice(com, code)
        S = rng.gamma(0.3, 2.0, len(com)) * (rng.random(len(com)) < 0.3)
        P = rng.lognormal(6, 1.5, len(com))
        A, _, b = deux_etapes(W, S, P)
        pires[code] = b["conservation_ecart_rel"]
        # contrôle : étape 2 sur des poids différents de l'étape 1 (paliers SF contre paliers CD) -> conservation violée
        W2 = matrice(com, "SF" if code != "SF" else "CD")
        R = S / (W.T @ P)
        ctrl[code] = abs((P * (W2 @ R)).sum() - S.sum()) / S.sum()
    worst = max(pires.values())
    crit("M4a", "conservation Σ P·A = Σ S (distancier réel, 4 professions)",
         f"écart relatif max {worst:.1e} ; {len(com)} communes", worst <= 1e-9 and min(ctrl.values()) > 1e-9,
         f"poids d'étape 2 ≠ étape 1 : écart min {min(ctrl.values()):.1e}")


def m4b_rayon_zero():
    com = _communes()
    d = _paires()
    W0 = matrice(com, "CD", paires=d[d.d_km == 0])
    rng = np.random.default_rng(1)
    S, P = rng.gamma(0.5, 2.0, len(com)), rng.lognormal(6, 1.5, len(com))
    A, _, _ = deux_etapes(W0, S, P)
    err = float(np.max(np.abs(A - S / P) / (S / P).clip(1e-300)))
    Af, _, _ = deux_etapes(matrice(com, "CD"), S, P)
    ctrl = float(np.max(np.abs(Af - S / P) / (S / P).clip(1e-300)))
    crit("M4b", "rayon 0 ⇒ M4 = densité de la commune", f"écart relatif max {err:.1e} ; diagonale seule "
         f"{W0.nnz == len(com)}", err <= 1e-12 and W0.nnz == len(com) and ctrl > 1e-12,
         f"rayon des paliers : écart max {ctrl:.2f}")


def m4c_rayon_infini():
    n = 400
    rng = np.random.default_rng(2)
    S, P = rng.gamma(0.5, 2.0, n) * (rng.random(n) < 0.5), rng.lognormal(6, 1.5, n)
    A, _, _ = deux_etapes(sparse.csr_matrix(np.ones((n, n))), S, P)
    nat = S.sum() / P.sum()
    err = float(np.max(np.abs(A / nat - 1)))
    com = _communes(n)
    Af, _, _ = deux_etapes(matrice(com, "CD"), S, P)
    ctrl = float(np.max(np.abs(Af / nat - 1)))
    crit("M4c", "rayon ∞ ⇒ M4 = densité nationale, uniforme", f"écart relatif max {err:.1e} sur {n} communes",
         err <= 1e-12 and ctrl > 1e-12, f"paliers DREES : écart max {ctrl:.2f}")


def m4d_o2():
    com = _communes(50)
    yrs = np.array([2026])
    fake = Cube(np.array(["medecine-generale"]), com, yrs, np.ones((1, len(com), 1)), "com")
    spe = Cube(np.array(["specialistes"]), com, yrs, np.ones((1, len(com), 1)), "com")
    B = Cube(np.array(list(CODE)), com, yrs, np.ones((len(CODE), len(com), 1)), "com")
    refus = {}
    for k, S in {"MG": fake, "spécialistes": spe}.items():
        try:
            M4().accessibilite(S, B)
            refus[k] = False
        except ValueError:
            refus[k] = True
    sans = not ({"medecine-generale", "specialistes"} & set(M4.professions))
    ok_cd = M4().accessibilite(Cube(np.array(["dentistes"]), com, yrs, np.ones((1, len(com), 1)), "com"), B)[0]
    crit("M4d", "aucune accessibilité M4 pour la MG ni les spécialistes (O2)",
         f"refus {sum(refus.values())}/{len(refus)} ; professions de M4 sans MG ni spécialistes {sans}",
         all(refus.values()) and sans and np.isfinite(ok_cd.values).all(),
         "les dentistes passent (le refus vise O2, pas tout appel)")


CRITERES = [m4a_conservation, m4b_rayon_zero, m4c_rayon_infini, m4d_o2]
