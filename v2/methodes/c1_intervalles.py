"""Intervalles de C1 : prévision conforme (a), réconciliation hiérarchique (b), les deux (c). Hors protocole N6
(gelé, non modifié) ; même banc, même CRPS sur log N, même bootstrap des départements.

Étape 1, `tirages --level dep|reg|nat` : C1 (θ fixé) ajusté à chaque (profession, origine ≤ 2021) de la grille N1, au
  niveau département, région (dep := région, sommé) ou France ; 200 trajectoires, totaux de o+1 à o+5 (≤ dernière
  année) -> out/c1i_tirages_{level}.parquet. Une ligne k/N par ajustement.
Étape 2, `eval` : distributions prédictives à h = 5, scores, verdicts -> out/c1i_*.{parquet,csv,json}.
  C1          tirages bruts (référence, identique à N6 pour l'origine 2021).
  C1-conf-h5  conforme normalisé, même horizon : z = (log y − m)/s, m, s = médiane et écart-type des log-tirages,
              couples (o′, h′ = 5), o′ + 5 ≤ o ; prédictive m + s·z. Seule l'origine 2021 est calculable.
  C1-conf     idem, tous horizons h′ ≤ 5 avec o′ + h′ ≤ o (le score normalisé ne dépend pas de h si s croît
              comme l'erreur) ; origines 2017–2021.
  C1-conf-hg  idem, z ramené à h = 5 par sd(z | h′) ∝ h′^γ ajusté sur le passé (post hoc : écrit après avoir vu que
              sd(z) croît de 0,80 à h′ = 1 à 1,12 à h′ = 5).
  C1-MinT     tirages réconciliés dép -> région -> France (MinT-WLS, W = variances des tirages de base, aucune
              donnée postérieure à l'origine), chaque tirage projeté (Panagiotelis et al. 2023).
  C1-MinT-conf  C1-MinT puis C1-conf sur ses propres scores passés.
  Références : persistance et tendance probabilistes N6 (origine 2021) ; et, sur toutes les origines, les mêmes
  naïves passées au conforme tous horizons (score e/√h′, prédictive log prédit + √h·z), à armes égales.
Lancer (racine) : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.c1_intervalles tirages --level dep
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes import calibrage, cohortes
from methodes.cohortes import CohortesEstimator
from methodes.perimetres import prive
from validation.forecast import H_MAIN, MIN_N, SEED, design

OUT = Path("v2/methodes/out")
LAST_ORIGIN, S, MIN_ERR, BOOT = 2021, 200, 20, 2000
NAIVES = ("naive_persistance", "naive_tendance")


# --- étape 1 : tirages ---------------------------------------------------------------------------------
def relabel(t, level):
    if level == "dep":
        return t
    d2r = calibrage.dep_to_region()
    t = t.assign(dep=t.dep.map(d2r).fillna("?") if level == "reg" else "FR")
    return t.groupby(["profession", "dep", "sex", "age_lo", "year"], as_index=False).n.sum()


def tirages(level, only=None):
    t = relabel(prive(), level)
    grid = [g for g in design(t) if g[2] <= LAST_ORIGIN]
    if only:
        grid = grid[:only]
    rows, t0 = [], time.time()
    for k, (prof, fit, o, _) in enumerate(grid, 1):
        tp = t[t.profession == prof]
        last = int(tp.year.max())
        years = [y for y in range(o + 1, o + H_MAIN + 1) if y <= last]
        est = CohortesEstimator().fit(tp[tp.year <= o], fit, o)
        draws = {y: [] for y in years}
        for s in range(S):
            tr = est.trajectory(years[-1], cohortes.Scenario(name=f"t{s}", params={"cohortes.tirage": s},
                                                             modules=cohortes.COMPOSITION))
            for y in years:
                draws[y].append(tr.states[y].total())
            est._traj.clear()
        for y in years:
            d = pd.concat(draws[y], axis=1)
            d.index = d.index.get_level_values(-1)
            rows.append(pd.DataFrame(d.to_numpy(np.float32), columns=[f"s{i}" for i in range(S)])
                        .assign(level=level, profession=prof, origin=o, year=y, territory=d.index.astype(str)))
        print(f"{k}/{len(grid)} ajustements · {level} {prof} {o} · {time.time() - t0:.0f} s", flush=True)
    pd.concat(rows, ignore_index=True).to_parquet(OUT / f"c1i_tirages_{level}{'_pilote' if only else ''}.parquet")


# --- étape 2 : distributions prédictives -------------------------------------------------------------
def crps(x, y):
    x = np.sort(x)
    n = len(x)
    return float(np.abs(x - y).mean() - (2 * np.arange(1, n + 1) - n - 1) @ x / n ** 2)


def score_row(model, prof, o, terr, x, y, n0):
    """x : échantillon de la prédictive sur log N ; y : log réel. Couverture par quantiles, comme banc_cohortes."""
    q = np.quantile(x, [.1, .25, .75, .9])
    return {"model": model, "profession": prof, "origin": o, "territory": terr, "n_origin": n0, "crps": crps(x, y),
            "pit": float((x <= y).mean()), "in80": bool(q[0] <= y <= q[3]), "in50": bool(q[1] <= y <= q[2])}


def actuals(t, level="dep"):
    return relabel(t, level).groupby(["profession", "dep", "year"]).n.sum()


def mint(D, R, F, d2r):
    """Réconcilie chaque tirage : D (dép × S), R (rég × S), F (1 × S) en niveaux ; W = diag(variances des tirages)."""
    deps, regs = D.index, R.index
    Sm = np.vstack([(np.asarray(d2r.reindex(deps).fillna("?"))[None, :] == np.asarray(regs)[:, None]).astype(float),
                    np.ones((1, len(deps))), np.eye(len(deps))])
    Y = np.vstack([R.to_numpy(), F.to_numpy(), D.to_numpy()])
    w = 1 / np.maximum(Y.var(1), 1e-6)
    StW = Sm.T * w
    G = np.linalg.solve(StW @ Sm, StW)
    return pd.DataFrame(G @ Y, index=deps)


def draws_by_key(level):
    d = pd.read_parquet(OUT / f"c1i_tirages_{level}.parquet")
    cols = [c for c in d.columns if c.startswith("s")]
    return {k: g.set_index("territory")[cols] for k, g in d.groupby(["profession", "origin", "year"])}


def naive_errors(t):
    from validation import registry
    from validation.forecast import bench
    grid = [g for g in design(t) if g[2] <= LAST_ORIGIN]
    e = bench({k: registry.get(k) for k in NAIVES}, t, grid)
    e = e[(e.actual > 0) & (e.pred > 0)].copy()
    e["e"] = np.log(e.actual / e.pred)
    return e


def logq(X):
    L = np.log(np.maximum(X.to_numpy(float), 0.5))
    return L, np.median(L, 1), np.maximum(L.std(1), 1e-4)


def rescale(zp):
    """Variante adaptative en h (ajoutée après lecture des premiers résultats, donc post hoc) : sd(z | h′) = c·h′^γ,
    γ par moindres carrés sur log sd ~ log h′ (horizons à ≥ 20 scores passés, au moins 2) ; z ramené à h = 5 par
    z·(5/h′)^γ. N'utilise que les scores dont la cible ≤ origine."""
    g = zp.groupby("h").z.agg(["std", "size"])
    g = g[g["size"] >= MIN_ERR]
    if len(g) < 2:
        return None
    gam = np.polyfit(np.log(g.index.to_numpy(float)), np.log(g["std"].to_numpy()), 1)[0]
    zp = zp[zp.h.isin(g.index)]
    return (zp.z * (H_MAIN / zp.h) ** gam).to_numpy()


def evaluate():
    t = prive()
    act = actuals(t)
    n_at = lambda p, o: act.loc[p].xs(o, level="year")
    D, R, F = draws_by_key("dep"), draws_by_key("reg"), draws_by_key("nat")
    d2r = calibrage.dep_to_region()
    rec = {k: mint(D[k], R[k], F[k], d2r) for k in D if k in R and k in F}
    rows, scores = [], {"C1": [], "C1-MinT": []}
    # scores normalisés z = (log y − m)/s de chaque (profession, o′, h′), cellules N ≥ 30
    for base, src in (("C1", D), ("C1-MinT", rec)):
        for (p, o, y), X in src.items():
            yv, n0 = act.loc[p].xs(y, level="year"), n_at(p, o)
            L, m, s = logq(X)
            for i, d in enumerate(X.index):
                if d in yv.index and yv[d] > 0 and n0.get(d, 0) >= MIN_N:
                    scores[base].append((p, o, y - o, d, (np.log(yv[d]) - m[i]) / s[i]))
    Z = {b: pd.DataFrame(v, columns=["profession", "origin", "h", "territory", "z"]) for b, v in scores.items()}
    for base, src in (("C1", D), ("C1-MinT", rec)):
        z = Z[base]
        for (p, o, y), X in src.items():
            if y - o != H_MAIN:
                continue
            yv, n0 = act.loc[p].xs(y, level="year"), n_at(p, o)
            L, m, s = logq(X)
            zp = z[(z.profession == p) & (z.origin + z.h <= o)]
            z5 = zp[zp.h == H_MAIN].z.to_numpy()
            za = zp.z.to_numpy()
            zg = rescale(zp)
            for i, d in enumerate(X.index):
                if not (d in yv.index and yv[d] > 0 and n0.get(d, 0) >= MIN_N):
                    continue
                ly = np.log(yv[d])
                rows.append(score_row(base, p, o, d, L[i], ly, n0[d]))
                if len(za) >= MIN_ERR:
                    rows.append(score_row(base + "-conf", p, o, d, m[i] + s[i] * za, ly, n0[d]))
                if zg is not None:
                    rows.append(score_row(base + "-conf-hg", p, o, d, m[i] + s[i] * zg, ly, n0[d]))
                if len(z5) >= MIN_ERR:
                    rows.append(score_row(base + "-conf-h5", p, o, d, m[i] + s[i] * z5, ly, n0[d]))
    e = naive_errors(t)
    cur = e[(e.h == H_MAIN) & (e.n_origin >= MIN_N)]
    for (k, p, o), g in cur.groupby(["model", "profession", "origin"]):
        past = e[(e.model == k) & (e.profession == p) & (e.n_origin >= MIN_N) & (e.origin + e.h <= o)]
        p5 = past[past.h == H_MAIN].e.to_numpy()
        za = (past.e / np.sqrt(past.h)).to_numpy()
        for r in g.itertuples():
            lp, ly = np.log(r.pred), np.log(r.actual)
            if len(p5) >= MIN_ERR:      # N6 tel que gelé (même h)
                rows.append(score_row(k, p, o, r.territory, lp + p5, ly, r.n_origin))
            if len(za) >= MIN_ERR:      # conforme tous horizons, à armes égales avec C1-conf
                rows.append(score_row(k + "-conf", p, o, r.territory, lp + np.sqrt(H_MAIN) * za, ly, r.n_origin))
    sc = pd.DataFrame(rows)
    sc.to_parquet(OUT / "c1i_scores.parquet")
    return report(sc)


def boot_delta(sc, a, b):
    """Δ = CRPS(a) − CRPS(b), cellules profession × origine à poids égal ; IC 95 % par bootstrap des départements
    (2 000 tirages multinomiaux, graine 20261114, mêmes poids pour toutes les cellules : corrélation conservée)."""
    rng = np.random.default_rng(SEED)
    deps = np.sort(sc.territory.unique())
    W = rng.multinomial(len(deps), np.full(len(deps), 1 / len(deps)), size=BOOT).astype(float)
    cells = sorted(set(map(tuple, sc[sc.model == a][["profession", "origin"]].drop_duplicates().to_numpy()))
                   & set(map(tuple, sc[sc.model == b][["profession", "origin"]].drop_duplicates().to_numpy())))

    def mat(k):
        g = sc[sc.model == k].pivot_table(index=["profession", "origin"], columns="territory", values="crps")
        return g.reindex(index=pd.MultiIndex.from_tuples(cells), columns=deps).to_numpy()
    out = {}
    for k in (a, b):
        M = mat(k)
        ok = ~np.isnan(M)
        num, den = W @ np.where(ok, M, 0).T, W @ ok.T.astype(float)
        out[k] = (np.nanmean(np.nanmean(M, 1)), np.nanmean(num / np.where(den > 0, den, np.nan), 1))
    d = out[a][1] - out[b][1]
    lo, hi = np.nanquantile(d, [.025, .975])
    return {"delta": float(out[a][0] - out[b][0]), "lo": float(lo), "hi": float(hi),
            "issue": "gagne" if hi < 0 else ("perd" if lo > 0 else "égalité"), "cellules": len(cells)}


def summary(g):
    return {"crps_log": float(g.groupby(["profession", "origin"]).crps.mean().mean()), "n": int(len(g)),
            "couv80": float(g.in80.mean()), "couv50": float(g.in50.mean()),
            "calibre": bool(0.75 <= g.in80.mean() <= 0.85 and 0.44 <= g.in50.mean() <= 0.56),
            "pit10": np.histogram(g.pit, bins=10, range=(0, 1))[0].tolist()}


def report(sc):
    res = {}
    # Test principal : origine 2021, cellules N6 (où la persistance probabiliste même h existe)
    cells = sc[sc.model == "naive_persistance"][["profession", "origin"]].drop_duplicates()
    p = sc.merge(cells, on=["profession", "origin"])
    deps = p[p.model == "naive_persistance"][["profession", "territory"]].drop_duplicates()
    p = p.merge(deps, on=["profession", "territory"])
    best = min(NAIVES, key=lambda k: summary(p[p.model == k])["crps_log"])
    res["principal"] = {"cellules": cells.astype(str).values.tolist(), "meilleure_naive": best, "modeles": {}}
    for k in sorted(p.model.unique()):
        g = p[p.model == k]
        r = summary(g)
        if k != best:
            r["vs_naive"] = boot_delta(p, k, best)
        if k.startswith("C1") and k != "C1":
            r["vs_C1"] = boot_delta(p, k, "C1")
        tiers = pd.qcut(g.n_origin, 3, labels=["petits", "moyens", "grands"])
        r["couv80_par_taille"] = g.groupby(tiers, observed=True).in80.mean().round(3).to_dict()
        res["principal"]["modeles"][k] = r
    # Secondaire : toutes les origines où C1-conf est défini (2017–2021, h = 5), vs naïves conformes tous horizons
    cells2 = sc[sc.model == "C1-conf"][["profession", "origin"]].drop_duplicates()
    q = sc.merge(cells2, on=["profession", "origin"])
    best2 = min(("naive_persistance-conf", "naive_tendance-conf"), key=lambda k: summary(q[q.model == k])["crps_log"])
    res["toutes_origines"] = {"cellules": cells2.astype(str).values.tolist(), "meilleure_naive": best2, "modeles": {}}
    for k in ("C1", "C1-conf", "C1-conf-hg", "C1-MinT", "C1-MinT-conf", "C1-MinT-conf-hg", "naive_persistance-conf", "naive_tendance-conf"):
        g = q[q.model == k]
        r = summary(g)
        if k != best2:
            r["vs_naive"] = boot_delta(q, k, best2)
        if k not in ("C1",) and k.startswith("C1"):
            r["vs_C1"] = boot_delta(q, k, "C1")
        r["par_origine"] = g.groupby(["origin", "profession"]).crps.mean().groupby("origin").mean().round(4).to_dict()
        r["couv80_par_profession"] = g.groupby("profession").in80.mean().round(3).to_dict()
        res["toutes_origines"]["modeles"][k] = r
    (OUT / "c1i_verdicts.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    for part in ("principal", "toutes_origines"):
        print(f"== {part} (meilleure naïve : {res[part]['meilleure_naive']})")
        for k, r in res[part]["modeles"].items():
            vn, vc = r.get("vs_naive", {}), r.get("vs_C1", {})
            print(f"{k:24s} CRPS {r['crps_log']:.4f} cov80 {r['couv80']:.3f} cov50 {r['couv50']:.3f} n {r['n']:5d} "
                  f"| vs naïve {vn.get('delta', 0):+.4f} [{vn.get('lo', 0):+.4f};{vn.get('hi', 0):+.4f}] {vn.get('issue', '')} "
                  f"| vs C1 {vc.get('delta', 0):+.4f} [{vc.get('lo', 0):+.4f};{vc.get('hi', 0):+.4f}]", flush=True)
    return res


def main(argv):
    if argv[0] == "tirages":
        tirages(argv[argv.index("--level") + 1], int(argv[argv.index("--only") + 1]) if "--only" in argv else None)
    elif argv[0] == "eval":
        evaluate()
    elif argv[0] == "report":
        report(pd.read_parquet(OUT / "c1i_scores.parquet"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
