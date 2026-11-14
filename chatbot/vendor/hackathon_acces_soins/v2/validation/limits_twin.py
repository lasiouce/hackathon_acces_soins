"""Axe 3, N2 partie B (SHA-256 bc5df3083cc5…) : cas limites L1–L3 sur le jumeau (variante par défaut).

  L1  h → 0       : l'état du jumeau à l'origine = effectif observé (profession × département), écart ≤ 1e-9
  L2  h → ∞       : scénario tendanciel (stationnaire), N(o + 200) contre Q·C = Σ_t total d'une seule promotion
                    d'entrées lancée dans un état vide (entrées × 0 après la première année) ; et état initial × 0,5
  L3  h < L       : formation.capacite × 1,2 dès o + 1 ; aucun écart avant o + L_p + 1 (convention du module)
Périmètre privé (methodes.perimetres.prive), origine 2026 (infirmiers libéraux : 2023), fenêtre complète.
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.limits_twin -> v2/validation/out/limits_twin.json
"""
import json
import time
from pathlib import Path

import numpy as np

from jumeau.modules.formation import DUREE
from jumeau.scenario import LEVIERS, Event, Scenario
from validation.limits import TOL_L1, TOL_L2, TOL_L3

OUT = Path(__file__).parent / "out"
T_INF = 200


def fitted(t, prof):
    from validation import registry
    tp = t[t.profession == prof]
    o = int(tp.year.max())
    first = 2017 if prof == "kines" else int(tp.year.min())
    return registry.get("jumeau_taux_locaux")().fit(tp, (first, o), o), tp, o


def totals(tr, years):
    return np.array([tr.states[y].N.sum() for y in years])


def l1(est, tp, o):
    obs = tp[tp.year == o].groupby("dep").n.sum()
    st = est.state
    got = st.to_frame().groupby("territory").n.sum() if hasattr(st, "to_frame") else None
    gap = float(((got.reindex(obs.index) - obs).abs() / obs.where(obs > 0)).max())
    return {"ecart_max": gap, "passe": gap <= TOL_L1}


def l2(est, o):
    years = range(o + 1, o + T_INF + 1)
    base = est.trajectory(o + T_INF)
    NT = float(base.states[o + T_INF].N.sum())
    st0 = est.state
    try:
        est.state = st0.copy(); est.state.N[:] = 0.5 * st0.N; est._traj = {}
        NT_half = float(est.trajectory(o + T_INF).states[o + T_INF].N.sum())
        est.state = st0.copy(); est.state.N[:] = 0.0; est._traj = {}
        one = Scenario(name="une_promotion", events=[Event("entrees.multiplicateur", o + 2, 0.0, "set")])
        QC = float(totals(est.trajectory(o + T_INF, one), years).sum())
    finally:
        est.state, est._traj = st0, {}
    g, d = NT / QC - 1, abs(NT / NT_half - 1)
    return {"N_T": NT, "Q_C": QC, "ecart_QC": g, "N_T_etat_moitie": NT_half, "dependance_etat_initial": d,
            "passe": bool(abs(g) <= TOL_L2 and d <= TOL_L2)}


def l3(est, prof, o):
    L = DUREE.get(prof.replace("-liberaux", ""), DUREE.get(prof))
    base = Scenario(name="leviers", modules=LEVIERS)
    shock = Scenario(name="quota", modules=LEVIERS, params={"formation.capacite": 1.2})
    yrs = list(range(o + 1, o + L + 6))
    a, b = totals(est.trajectory(yrs[-1], base), yrs), totals(est.trajectory(yrs[-1], shock), yrs)
    rel = np.abs(b - a) / a
    early = [i for i, y in enumerate(yrs) if y <= o + L]
    gap = float(rel[early].max())
    first = next((y for y, r in zip(yrs, rel) if r > TOL_L3), None)
    return {"L_p": L, "ecart_avant": gap, "premiere_annee_d_effet": first, "attendu": o + L + 1,
            "passe": bool(gap <= TOL_L3 and first is not None)}


def main():
    from methodes.perimetres import prive
    t = prive()
    res, t0 = {}, time.time()
    profs = sorted(t.profession.unique())
    for k, p in enumerate(profs, 1):
        est, tp, o = fitted(t, p)
        r = {"origine": o}
        for name, f in (("L1", lambda: l1(est, tp, o)), ("L2", lambda: l2(est, o)), ("L3", lambda: l3(est, p, o))):
            try:
                r[name] = f()
            except Exception as ex:          # un cas qui ne s'exécute pas est rapporté, pas caché
                r[name] = {"erreur": repr(ex)[:300], "passe": False}
        res[p] = r
        print(f"{k}/{len(profs)} {p} {time.time() - t0:.0f}s", flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "limits_twin.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float))
    print(json.dumps(res, indent=1, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
