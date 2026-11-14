"""Axe 3, niveau 2 : cas limites analytiques (protocole N2, SHA-256 bc5df3083cc5…).

Fonctions génériques ; `step` est un pas annuel N[âge] -> N[âge] (pour le jumeau : un pas du moteur sous un
scénario stationnaire, sommé sur les cellules), `entrants` = Q, flux annuel constant.
  l1_persistence(est, observed, origin)      predict(origin) = observé, écart relatif max
  l2_equilibrium(step, Q, n0, years)         N(T)/(Q·C) − 1 et dépendance à l'état initial
  l3_quota_lock(run_base, run_shock, t0, L)  aucun effet d'un choc de quota avant t0 + L
"""
import numpy as np
import pandas as pd

TOL_L1, TOL_L2, TOL_L3 = 1e-9, 0.01, 1e-9


def l1_persistence(est, observed: pd.Series, origin: int) -> dict:
    p = est.predict(origin).reindex(observed.index)
    gap = float(((p - observed).abs() / observed.where(observed > 0)).max())
    return {"ecart_max": gap, "passe": gap <= TOL_L1}


def _run(step, n, years):
    tot = []
    for _ in range(years):
        n = step(n)
        tot.append(n.sum())
    return n, np.array(tot)


def career_length(step_no_entry, n_ages: int, years: int) -> float:
    """C = personnes-années d'une cohorte d'un entrant (âge 0) lancée dans un état vide, sans autre entrée."""
    n = np.zeros(n_ages)
    n[0] = 1.0
    _, tot = _run(step_no_entry, n, years)
    return float(1.0 + tot.sum())


def l2_equilibrium(step, step_no_entry, Q: float, n0: np.ndarray, years: int = 200) -> dict:
    C = career_length(step_no_entry, len(n0), years)
    a, _ = _run(step, n0.copy(), years)
    b, _ = _run(step, 0.5 * n0, years)
    gap = float(a.sum() / (Q * C) - 1)
    dep = float(abs(a.sum() / b.sum() - 1))
    return {"C": C, "N_star": Q * C, "N_T": float(a.sum()), "ecart_QC": gap, "dependance_etat_initial": dep,
            "passe": abs(gap) <= TOL_L2 and dep <= TOL_L2}


def l3_quota_lock(base: pd.Series, shock: pd.Series, t0: int, L: int) -> dict:
    """base, shock : effectif total par année. Aucun écart avant t0 + L."""
    early = [y for y in base.index if y < t0 + L]
    gap = float(((shock[early] - base[early]).abs() / base[early]).max()) if early else 0.0
    return {"ecart_avant_L": gap, "passe": gap <= TOL_L3}
