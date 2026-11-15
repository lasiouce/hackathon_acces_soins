"""P-B1 : M1 contre M0 sur l'indice de couverture 2050 (protocole gelé v2/validation/preregistered/
2026-11-15-besoin-p-b1-age.md ; écarts dans v2/docs/lab/reports/2026-11-15-besoin-pb1-age.md).

Run (racine du dépôt) : PYTHONPATH=v2 uv run python -m besoin.validation.pb1  -> v2/artifacts/besoin_pb1/results.json

  B₀ = pop ; B₁ = Σ pop·ω ; C_k = [N(2050)/B_k(2050)] / [N(2026)/B_k(2026)]
  S₁ = part des départements où |C₁/C₀ − 1| < 0,02 ; ρ = Spearman(C₁, C₀)
  abandon de l'âge si S₁ > 0,90 et ρ ≥ 0,98 sous P1 et sous P2 ; P2 (Open DAMIR) absent ici (écart 1).
"""
import json
import subprocess
from pathlib import Path

import numpy as np

from besoin.couverture import couverture, offre
from besoin.cube import Population
from besoin.estimateurs.m0 import M0
from besoin.estimateurs.m1 import M1, CODE

OUT = Path("v2/artifacts/besoin_pb1")
REF, H, MID = 2026, 2050, 2035
SEUIL_ECART, SEUIL_PART, SEUIL_RHO = 0.02, 0.90, 0.98       # gelés


def rangs(x):
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[o] = np.arange(len(x))
    for v in np.unique(x):                                     # rangs moyens pour les égalités
        m = x == v
        if m.sum() > 1:
            r[m] = r[m].mean()
    return r


def spearman(a, b) -> float:
    try:
        from scipy.stats import spearmanr
        return float(spearmanr(a, b).statistic)
    except ImportError:
        return float(np.corrcoef(rangs(a), rangs(b))[0, 1])


def etat_servi(prof: str) -> dict:
    from prototype.server import Model
    m = Model(prof)
    return {m.o: m.est.state, **m.base.states}


def stats(prof: str, etat: dict, pop: Population, year: int) -> dict:
    years = [REF, year]
    S = offre(etat, years)
    C = {}
    for name, est in (("M0", M0()), ("M1", M1())):
        B = est.fit(pop, etat, REF).predict(pop, etat, years)
        c = couverture(S, B, REF)
        C[name], terr = c.values[c.p(prof), :, c.y(year)], c.territories
    ok = np.isfinite(C["M0"]) & np.isfinite(C["M1"])
    q = C["M1"][ok] / C["M0"][ok] - 1
    S1 = float((np.abs(q) < SEUIL_ECART).mean())
    rho = spearman(C["M1"][ok], C["M0"][ok])
    top = np.argsort(-np.abs(q))[:5]
    return dict(annee=year, n_dep=int(ok.sum()), n_retires=int((~ok).sum()), S1=S1, rho=rho,
                abandon_P1=bool(S1 > SEUIL_PART and rho >= SEUIL_RHO),
                ecart=dict(min=float(q.min()), q1=float(np.quantile(q, .25)), med=float(np.median(q)),
                           q3=float(np.quantile(q, .75)), max=float(q.max())),
                top5=[(str(terr[ok][i]), float(q[i])) for i in top])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    pops = {s: Population.load(s) for s in ("central", "pop_basse", "pop_haute")}
    res = dict(commit=commit, seuils=dict(ecart=SEUIL_ECART, part=SEUIL_PART, rho=SEUIL_RHO), professions={})
    for prof in CODE:
        e = etat_servi(prof)
        r = dict(decisif=stats(prof, e, pops["central"], H),
                 rapporte={"pop_basse": stats(prof, e, pops["pop_basse"], H),
                           "pop_haute": stats(prof, e, pops["pop_haute"], H),
                           "central_2035": stats(prof, e, pops["central"], MID)})
        d = r["decisif"]
        r["verdict"] = ("en attente de P2 (P1 conclut à l'abandon)" if d["abandon_P1"]
                        else "M1 retenu (P1 conclut au maintien ; P2 ne peut pas renverser)")
        res["professions"][prof] = r
        print(f"{prof:13s} S1={d['S1']:.3f} rho={d['rho']:.4f} n={d['n_dep']} -> {r['verdict']}", flush=True)
    res["professions"]["pharmaciens"] = dict(verdict="aucun verdict : P2 (Open DAMIR) en attente de l'axe 4")
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print("pharmaciens    -> aucun verdict (P2 en attente)")


if __name__ == "__main__":
    main()
