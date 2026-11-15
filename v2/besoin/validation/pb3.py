"""P-B3 : M3 contre M1 sur l'indice 2050 (A) ; morbidité et recours standardisé hors échantillon (B).
Protocole gelé v2/validation/preregistered/2026-11-15-besoin-p-b3-pathologies.md, amendement A1.2 ; écarts dans
v2/docs/lab/reports/2026-11-15-besoin-pb3-pathologies.md.

Run (racine du dépôt) : PYTHONPATH=v2 uv run python -m besoin.validation.pb3  -> v2/artifacts/besoin_pb3/results.json

(A) S₃ = part des départements où |C₃/C₁ − 1| < 0,02 en 2050 ; ρ = Spearman(C₃, C₁) ; M3 réduit au recoupement si
    S₃ > 0,90 et ρ ≥ 0,98 aux trois imputations (1, 5, 10).
(B) y = log R_std ; modèle y = α + γ log(B₃/B₁)(2024) ; R²_oos par validation croisée une région laissée de côté ;
    ΔR² = R²_oos − 0 ; H-B3 retenue si ΔR² ≥ 0,10 et borne basse IC 98,75 % > 0 ; rejetée si ΔR² < 0,10.
    Placebo : log(B₃/B₁) d'une autre profession (IDE → MK → CD → SF → IDE) ; « non spécifique » si ΔR²_pl ≥ ½ ΔR².
"""
import json
import subprocess
from pathlib import Path

import numpy as np

from besoin.couverture import couverture, offre
from besoin.cube import Population, mapping
from besoin.estimateurs.m1 import M1
from besoin.estimateurs.m3 import M3
from besoin.estimateurs.recours import PROF_AMELI, pstd, table
from besoin.validation.pb1 import etat_servi, spearman

OUT = Path("v2/artifacts/besoin_pb3")
REF, H, AN = 2026, 2050, 2024
SEUIL_ECART, SEUIL_PART, SEUIL_RHO, SEUIL_R2 = 0.02, 0.90, 0.98, 0.10       # gelés
B, SEED, NIV = 2000, 20261115, 1 - 0.05 / 4
IMPUTES = (1.0, 5.0, 10.0)
PLACEBO = {"infirmiers": "kines", "kines": "dentistes", "dentistes": "sages-femmes", "sages-femmes": "infirmiers"}


def indice(prof, e, pop, m3s):
    years = [REF, H]
    S = offre(e, years)
    c1 = couverture(S, M1().fit(pop, e, REF).predict(pop, e, years), REF)
    a = c1.values[c1.p(prof), :, c1.y(H)]
    out = {}
    for imp, m3 in m3s.items():
        c3 = couverture(S, m3.predict(pop, e, years), REF)
        b = c3.values[c3.p(prof), :, c3.y(H)]
        ok = np.isfinite(a) & np.isfinite(b)
        q = b[ok] / a[ok] - 1
        S3, rho = float((np.abs(q) < SEUIL_ECART).mean()), spearman(b[ok], a[ok])
        top = np.argsort(-np.abs(q))[:5]
        out[str(imp)] = dict(n=int(ok.sum()), S3=S3, rho=rho, reduit=bool(S3 > SEUIL_PART and rho >= SEUIL_RHO),
                             ecart=dict(min=float(q.min()), q1=float(np.quantile(q, .25)), med=float(np.median(q)),
                                        q3=float(np.quantile(q, .75)), max=float(q.max())),
                             top5=[(str(c3.territories[ok][i]), float(q[i])) for i in top])
    return out


def r2_oos(x, y, g):
    """R² hors échantillon, une région laissée de côté : 1 − Σ(y − ŷ)² / Σ(y − ȳ_train)²."""
    num = den = 0.0
    for r in np.unique(g):
        te, tr = g == r, g != r
        X = np.column_stack([np.ones(tr.sum()), x[tr]])
        c, *_ = np.linalg.lstsq(X, y[tr], rcond=None)
        num += ((y[te] - c[0] - c[1] * x[te]) ** 2).sum()
        den += ((y[te] - y[tr].mean()) ** 2).sum()
    return 1 - num / den


def ratio_log(prof, m3, pop, deps):
    B3 = m3.predict(pop, None, [AN])
    b3 = B3.values[B3.p(prof), :, 0]
    b1 = pstd(prof, pop, [AN])[AN].reindex(B3.territories).to_numpy()
    s = dict(zip(B3.territories, np.log(b3 / b1)))
    return np.array([s[d] for d in deps])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pop = Population.load()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    m3s = {imp: M3(imp).fit(pop) for imp in IMPUTES}
    res = dict(commit=commit, B=B, seed=SEED, niveau=NIV, A={}, B_test={},
               construction={p: dict(r0_negatif=m3s[5.0].negatif[p], prix=m3s[5.0].prix[p]) for p in M3.professions})
    for p in M3.professions:
        r = indice(p, etat_servi(p), pop, m3s)
        red = all(v["reduit"] for v in r.values())
        res["A"][p] = dict(par_imputation=r, verdict="M3 réduit au recoupement" if red else "M3 retenu pour l'indice")
        c = r["5.0"]
        print(f"(A) {p:13s} " + " ".join(f"imp{k}: S3={v['S3']:.3f} ρ={v['rho']:.4f}" for k, v in r.items())
              + f" -> {res['A'][p]['verdict']}", flush=True)
    reg = mapping("dep", "reg")
    tabs = {p: table(p, pop, (2023, 2024, 2025))[0] for p in PROF_AMELI}
    for p in PROF_AMELI:
        t = tabs[p]
        deps = np.array(sorted(set(t.index) & set(tabs[PLACEBO[p]].index)))
        y = np.log(t.R_std.reindex(deps).to_numpy())
        x = ratio_log(p, m3s[5.0], pop, deps)
        xp = ratio_log(PLACEBO[p], m3s[5.0], pop, deps)
        g = reg.reindex(deps).astype(str).to_numpy()
        d0, dp = r2_oos(x, y, g), r2_oos(xp, y, g)
        rng = np.random.default_rng(SEED)
        bs = np.empty(B)
        for i in range(B):
            j = rng.integers(0, len(y), len(y))
            bs[i] = r2_oos(x[j], y[j], g[j])
        lo, hi = float(np.quantile(bs, (1 - NIV) / 2)), float(np.quantile(bs, 1 - (1 - NIV) / 2))
        v = "H-B3 retenue" if (d0 >= SEUIL_R2 and lo > 0) else "H-B3 rejetée" if d0 < SEUIL_R2 else "non tranchée"
        if d0 > 0 and dp >= 0.5 * d0:
            v += " ; non spécifique (placebo)"
        X = np.column_stack([np.ones(len(y)), x])
        gam = float(np.linalg.lstsq(X, y, rcond=None)[0][1])
        res["B_test"][p] = dict(n=len(y), plis=int(len(np.unique(g))), dR2=float(d0), IC=[lo, hi],
                                placebo=dict(profession=PLACEBO[p], dR2=float(dp)), gamma_plein=gam, verdict=v)
        print(f"(B) {p:13s} n={len(y)} ΔR²={d0:.3f} IC[{lo:.3f}, {hi:.3f}] placebo({PLACEBO[p]}) {dp:.3f} "
              f"γ={gam:.2f} -> {v}", flush=True)
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
