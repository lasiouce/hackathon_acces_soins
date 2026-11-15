"""Budget d'erreur de A2 et C1 au banc N1 (privé, MAPE dép. h = 5, mêmes origines et cellules que tab:prive).

Question : où est l'erreur, avant de choisir une méthode plus riche (gravitaire, agents, apprentissage) ?
Avec des tranches de 5 ans et h = 5, la tranche b à la cible vient de la tranche b − 5 à l'origine (cohorte
alignée). On découpe la prévision du département d en trois blocs selon l'âge à la cible :
  Y  moins de 35 ans    surtout des entrées (installations) ;
  M  35 à 59 ans        cohortes en milieu de carrière : mobilité entre départements et sorties précoces ;
  R  60 ans et plus     départs en retraite.
L'erreur relative signée e = (P − A) / A est la somme exacte e_Y + e_M + e_R, et chaque e_k se coupe en une part
nationale (le total national du bloc, par sexe × tranche) et une part locale (la répartition entre départements).
Oracles, une composante à la fois (MAPE quand on donne au modèle la vraie valeur de cette composante) :
  bloc_k        P_k := A_k                                (tout le bloc exact)
  nat_k         P_k := P_k × A_nat / P_nat par sexe × tranche (niveau national exact, répartition du modèle)
  nat_total     P   := P × A_nat / P_nat sur le total     (biais national total retiré)
  nat_tous      nat_k sur les trois blocs à la fois       (tout le national exact ; reste l'écart local)
  rnat_M        P_M := N_o × r_nat, r_nat = rapport de cohorte national observé (aucun écart local de mobilité)
La part locale d'un bloc (bloc_k − nat_k) borne ce qu'un modèle de la répartition (gravitaire, agents) peut gagner.
Plancher de bruit : si les événements (entrées, sorties) sont indépendants, Var(N_T) ≈ F, avec F = Σ |solde de
cohorte| (borne basse des flux bruts) ; E|N_T − E N_T| ≈ √(2F/π). Aucun modèle ponctuel ne descend sous ce plancher.
Parts de MSE : E[e_k · e] / E[e²] (s'additionnent à 1). IC : bootstrap des départements (graine et nombre de
tirages du banc N1, mêmes tirages pour toutes les colonnes).
Lancer : PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.budget_erreur
  -> v2/methodes/out/budget_erreurs.parquet (prévisions par âge, ignoré par git), budget_erreur.json, budget_erreur.log
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from methodes.cohortes import CohortesEstimator
from methodes.estimators import ShrinkHier
from methodes.perimetres import prive
from validation.forecast import BOOT, H_MAIN, MIN_N, SEED, design

OUT = Path("v2/methodes/out")
MODELS = {"A2": ShrinkHier, "C1": CohortesEstimator}
BLOCS = {"Y": (0, 34), "M": (35, 59), "R": (60, 200)}
PARTIEL = (0.25, 0.5)
TAILLES = [30, 100, 300, 1000, np.inf]


def bloc(age):
    return np.select([age < 35, age < 60], ["Y", "M"], "R")


def source(age):
    """Tranche d'origine de la cohorte qui occupe `age` à o + 5 (−1 : pas de source, entrées pures)."""
    return np.where(age == 0, -1, np.where(age == 25, 0, np.where(age == 75, 70, age - 5)))


def predictions(t: pd.DataFrame) -> pd.DataFrame:
    """Prévision par (modèle, profession, origine, dep, sexe, tranche) à h = 5, et réel à o et à o + 5."""
    f = OUT / "budget_erreurs.parquet"
    if f.exists():
        return pd.read_parquet(f)
    grid = [(p, fit, o) for p, fit, o, tg in design(t) if o + H_MAIN in tg]
    rows, t0 = [], time.time()
    for k, (prof, fit, o) in enumerate(grid, 1):
        tp = t[t.profession == prof]
        for name, E in MODELS.items():
            est = E().fit(tp[tp.year <= o], fit, o)
            x = est.trajectory(o + H_MAIN).states[o + H_MAIN]
            p = (pd.DataFrame(x.N, columns=x.ages).assign(dep=x.cells.territory.to_numpy(), sex=x.cells.sex.to_numpy())
                 .melt(id_vars=["dep", "sex"], var_name="age_lo", value_name="pred")
                 .groupby(["dep", "sex", "age_lo"], as_index=False).pred.sum())
            rows.append(p.assign(model=name, profession=prof, origin=o))
        print(f"{k}/{len(grid)} {prof} {o} · {time.time() - t0:.0f} s", flush=True)
    p = pd.concat(rows, ignore_index=True)
    p["age_lo"] = p.age_lo.astype(int)
    a = t.groupby(["profession", "dep", "sex", "age_lo", "year"]).n.sum()
    p["actual"] = a.reindex(pd.MultiIndex.from_arrays([p.profession, p.dep, p.sex, p.age_lo, p.origin + H_MAIN])
                            ).fillna(0).to_numpy()
    p["n_o_src"] = 0.0
    src = source(p.age_lo.to_numpy())
    for s_age in np.unique(src[src >= 0]):
        sel = src == s_age
        ages = [70, 75] if s_age == 70 else [s_age]           # 75+ à la cible vient de 70–74 et 75+
        v = sum(a.reindex(pd.MultiIndex.from_arrays([p.profession[sel], p.dep[sel], p.sex[sel],
                                                     np.full(sel.sum(), aa), p.origin[sel]])).fillna(0).to_numpy()
                for aa in ages)
        p.loc[sel, "n_o_src"] = v
    p.to_parquet(f, index=False)
    return p


def per_dep(p: pd.DataFrame, t: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par (modèle, profession, origine, dep) : APE du modèle et de chaque oracle, e_k, plancher, taille."""
    p = p.assign(bloc=bloc(p.age_lo.to_numpy()))
    g = ["model", "profession", "origin"]
    nat = p.groupby(g + ["sex", "age_lo"])[["pred", "actual", "n_o_src"]].transform("sum")
    p["pred_nat"] = p.pred * np.where(nat.pred > 0, nat.actual / nat.pred, 1.0)     # niveau national exact
    r_nat = np.where(nat.n_o_src > 0, nat.actual / nat.n_o_src, 0.0)
    p["pred_rnat"] = np.where(p.age_lo == 0, p.pred_nat, p.n_o_src * r_nat)          # aucun écart local de cohorte
    p["solde"] = (p.actual - np.where(p.age_lo == 0, 0.0, p.n_o_src)).abs()
    k = g + ["dep"]
    d = p.groupby(k)[["pred", "actual", "pred_nat", "solde"]].sum()
    pb = p.pivot_table(index=k, columns="bloc", values=["pred", "actual", "pred_nat", "pred_rnat", "solde"], aggfunc="sum",
                       fill_value=0)
    n_o = t.groupby(["profession", "dep", "year"]).n.sum()
    d["n_origin"] = n_o.reindex(pd.MultiIndex.from_arrays([d.index.get_level_values("profession"),
                                                            d.index.get_level_values("dep"),
                                                            d.index.get_level_values("origin")])).to_numpy()
    d = d[(d.n_origin >= MIN_N) & (d.actual > 0)].copy()
    pb = pb.reindex(d.index)
    A, P = d.actual, d.pred
    ape = lambda pred: 100 * (pred - A).abs() / A                                    # noqa: E731
    d["ape"] = ape(P)
    for b in BLOCS:
        d[f"e_{b}"] = 100 * (pb[("pred", b)] - pb[("actual", b)]) / A
        d[f"e_{b}_nat"] = 100 * (pb[("pred", b)] - pb[("pred_nat", b)]) / A
        d[f"e_{b}_loc"] = d[f"e_{b}"] - d[f"e_{b}_nat"]
        d[f"ape_bloc_{b}"] = ape(P - pb[("pred", b)] + pb[("actual", b)])
        d[f"ape_nat_{b}"] = ape(P - pb[("pred", b)] + pb[("pred_nat", b)])
        for f in PARTIEL:                    # un modèle qui réduit l'écart local du bloc d'une fraction f
            d[f"ape_part{int(100 * f)}_{b}"] = ape(P - f * (pb[("pred_nat", b)] - pb[("actual", b)]))
        d[f"bruit2_{b}"] = 1e4 * pb[("solde", b)] / A ** 2                          # variance poissonienne, %²
    d["ape_rnat_M"] = ape(P - pb[("pred", "M")] + pb[("pred_rnat", "M")])
    d["ape_nat_tous"] = ape(d.pred_nat)
    tot = d.groupby(g)[["pred", "actual"]].transform("sum")
    d["ape_nat_total"] = ape(P * tot.actual / tot.pred)
    d["e"] = 100 * (P - A) / A
    d["plancher"] = 100 * np.sqrt(2 * d.solde / np.pi) / A
    d["taille"] = pd.cut(d.n_origin, TAILLES, right=False, labels=["30–99", "100–299", "300–999", "1000+"])
    return d.reset_index().rename(columns={"dep": "territory"})


def weights(deps) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    return np.stack([np.bincount(pd.Index(deps).get_indexer(rng.choice(deps, len(deps))), minlength=len(deps))
                     for _ in range(BOOT)]).astype(float)                            # [B, D], mêmes tirages que N1


def pooled(d: pd.DataFrame, cols, W, deps, cells=None) -> dict:
    """Moyenne par cellule profession × origine, puis à poids égal sur les cellules : point et tirages [B]."""
    out = {}
    for c in cols:
        a = d.pivot_table(index=["profession", "origin"], columns="territory", values=c).reindex(columns=deps)
        if cells is not None:
            a = a.reindex(cells)
        mask = a.notna().to_numpy(float)
        v = np.nan_to_num(a.to_numpy())
        with np.errstate(invalid="ignore", divide="ignore"):
            b = np.nanmean((W @ v.T) / (W @ mask.T), axis=1)
        out[c] = (float(np.nanmean(v.sum(1) / mask.sum(1))), b)
    return out


def ci(x):
    return [round(float(np.nanquantile(x, .025)), 2), round(float(np.nanquantile(x, .975)), 2)]


def analyse(d: pd.DataFrame, W, deps) -> dict:
    """Pour un modèle (et un sous-ensemble de cellules) : MAPE, gains des oracles, parts de MSE, plancher."""
    cols = (["ape", "ape_nat_total", "ape_nat_tous", "ape_rnat_M", "plancher"] + [f"ape_bloc_{b}" for b in BLOCS]
            + [f"ape_nat_{b}" for b in BLOCS] + [f"ape_part{int(100 * f)}_{b}" for b in BLOCS for f in PARTIEL])
    r = pooled(d, cols, W, deps)
    base_pt, base_b = r["ape"]
    res = {"mape": [round(base_pt, 2), ci(base_b)],
           "plancher_poisson": [round(r["plancher"][0], 2), ci(r["plancher"][1])],
           "part_plancher": [round(r["plancher"][0] / base_pt, 3), ci(r["plancher"][1] / base_b)],
           "gain_oracle": {}}
    names = {"ape_nat_total": "national_total", "ape_nat_tous": "national_tous_blocs",
             "ape_rnat_M": "M_rapport_cohorte_national"}
    names |= {f"ape_part{int(100 * f)}_{b}": f"{b}_local_reduit_{int(100 * f)}pct" for b in BLOCS for f in PARTIEL}
    names |= {f"ape_bloc_{b}": f"{b}_exact" for b in BLOCS} | {f"ape_nat_{b}": f"{b}_national" for b in BLOCS}
    for c, nm in names.items():
        res["gain_oracle"][nm] = [round(base_pt - r[c][0], 2), ci(base_b - r[c][1])]
    for b in BLOCS:                                                                   # part locale = exact − national
        res["gain_oracle"][f"{b}_local"] = [round(r[f"ape_nat_{b}"][0] - r[f"ape_bloc_{b}"][0], 2),
                                            ci(r[f"ape_nat_{b}"][1] - r[f"ape_bloc_{b}"][1])]
    e2 = (d.e ** 2).sum()
    res["part_mse"] = {c[2:]: round(float((d[c] * d.e).sum() / e2), 3)
                       for c in [f"e_{b}{s}" for b in BLOCS for s in ("_nat", "_loc")]}
    e2 = (d.e ** 2).mean()
    res["mse"] = {"total_pct2": round(float(e2), 1),
                  "part_bruit": round(float(sum(d[f"bruit2_{b}"].mean() for b in BLOCS) / e2), 3)}
    for b in BLOCS:                     # MSE du bloc et part de bruit poissonien dans cette MSE
        res["mse"][b] = {"mse_pct2": round(float((d[f"e_{b}"] ** 2).mean()), 1),
                         "part_bruit": round(float(d[f"bruit2_{b}"].mean() / (d[f"e_{b}"] ** 2).mean()), 3)}
    return res


def persistance(d: pd.DataFrame) -> dict:
    """Corrélation de l'écart local d'un département entre deux origines distantes de 5 ans (fenêtres disjointes).
    Un écart qui persiste est appris par un modèle de la répartition ; un écart qui ne persiste pas est du bruit."""
    out = {}
    for b in BLOCS:
        x = d.pivot_table(index=["profession", "territory"], columns="origin", values=f"e_{b}_loc")
        pairs = [(o, o + 5) for o in x.columns if o + 5 in x.columns]
        v = pd.concat([x[[a, c]].dropna().set_axis(["a", "c"], axis=1) for a, c in pairs])
        out[b] = {"r": round(float(v.a.corr(v.c)), 2), "n": len(v), "paires_origines": pairs}
    return out


def taille(d: pd.DataFrame) -> dict:
    g = d.groupby("taille", observed=True)
    out = g.agg(n=("ape", "size"), mape=("ape", "mean"), plancher=("plancher", "mean")).round(2)
    x = np.log(d.n_origin)
    slope = float(np.polyfit(x, np.log(d.ape.clip(lower=0.05)), 1)[0])
    return {"par_classe": out.reset_index().astype({"taille": str}).to_dict("records"),
            "pente_log_ape_log_n": round(slope, 2), "pente_log_plancher_log_n": round(
                float(np.polyfit(x, np.log(d.plancher.clip(lower=0.05)), 1)[0]), 2)}


def main() -> int:
    t = prive()
    p = predictions(t)
    d = per_dep(p, t)
    deps = d.territory.unique()
    W = weights(deps)
    res = {"protocole": {"h": H_MAIN, "min_n": MIN_N, "graine": SEED, "tirages": BOOT,
                         "cellules": int(d.groupby(["profession", "origin"]).ngroups / len(MODELS)),
                         "couples_dep_cellule": int(len(d) / len(MODELS))}}
    for m in MODELS:
        dm = d[d.model == m]
        res[m] = {"global": analyse(dm, W, deps), "taille": taille(dm), "persistance": persistance(dm),
                  "profession": {}}
        for prof, dp in dm.groupby("profession"):
            res[m]["profession"][prof] = analyse(dp, W, deps)
    (OUT / "budget_erreur.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for m in MODELS:
        gl = res[m]["global"]
        print(f"\n== {m} : MAPE {gl['mape']}  plancher {gl['plancher_poisson']}  part {gl['part_plancher']}")
        for k, v in sorted(gl["gain_oracle"].items(), key=lambda kv: -kv[1][0]):
            print(f"  oracle {k:28s} gain {v[0]:+6.2f}  IC95 {v[1]}")
        print("  parts de MSE", gl["part_mse"])
        print("  MSE et bruit", gl["mse"])
        print("  persistance de l'écart local", res[m]["persistance"])
        print("  taille", res[m]["taille"])
        for prof, v in res[m]["profession"].items():
            go = v["gain_oracle"]
            print(f"  {prof:20s} MAPE {v['mape'][0]:5.2f} plancher {v['plancher_poisson'][0]:5.2f} "
                  f"Y {go['Y_exact'][0]:+.2f} (loc {go['Y_local'][0]:+.2f}) M {go['M_exact'][0]:+.2f} "
                  f"(loc {go['M_local'][0]:+.2f}) R {go['R_exact'][0]:+.2f} nat {go['national_total'][0]:+.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
