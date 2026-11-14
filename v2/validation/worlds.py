"""Axe 3, N5 (SHA-256 1046545b17c0…) : mondes simulés à vérité connue ; et SBC de N6 (d1cc665cb864…).

Générateur en âges simples 25–69 ans, deux sexes, dynamique en espérance (aucun code partagé avec l'estimateur) :
  sorties : hasard b avant a0 ans, puis rampe linéaire jusqu'à 1 à 70 ans (défaut b = 0,5 %, a0 = 55) ;
  entrées : E par an, réparties également sur 25–34 ans, ajoutées après vieillissement.
Observation comme le RPPS : tranches de 5 ans (25 … 65–69) × sexe × département. M3 : comptes de Poisson.
Historique 12 ans (2000–2011, origine 2011), projection 15 ans (vérité = espérance, sans bruit).
Estimateur testé : variante par défaut N1 = stock-flux à taux locaux (sante.estimators.StockFlowLocal, identique
à jumeau_taux_locaux d'après l'axe 0).
Run (racine) : PYTHONPATH=v2 uv run --with scipy python -m validation.worlds [n5|sbc|all]  -> v2/validation/out/worlds_*
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).parent / "out"
SEED, REPS, NDEP, HIST, HOR = 20261114, 20, 30, 12, 15
AGES = np.arange(25, 70)
BANDS = np.arange(25, 70, 5)
Y0 = 2000
ORIGIN = Y0 + HIST - 1


def hazard(b=0.005, a0=55.0):
    h = np.where(AGES < a0, b, b + (AGES - a0) / (70 - a0) * (1 - b))
    return np.clip(h, 0, 1)


def step(x, h, E):
    """x [.., âge] -> année suivante : survie et vieillissement d'un an, puis entrées sur 25–34 ans."""
    y = np.zeros_like(x)
    y[..., 1:] = x[..., :-1] * (1 - h[:-1])
    y[..., :10] += E[..., None] / 10
    return y


def stationary(h, E=1.0):
    x = np.zeros(len(AGES))
    for _ in range(120):
        x = step(x, h, np.array(E))
    return x


def world(kind: str, rng, sizes=None):
    """-> (hist [dép, sexe, âge, 12 ans], truth [dép, sexe, âge, 15 ans]) en espérance."""
    sizes = rng.uniform(np.log(30), np.log(4000), NDEP) if sizes is None else sizes
    N0 = np.exp(sizes) / 2                                    # par sexe
    h0 = hazard()
    pyr = stationary(h0)
    C = pyr.sum()
    x = (N0[:, None, None] * pyr / C) * np.ones((1, 2, 1))
    E0 = np.repeat((N0 / C)[:, None], 2, 1)
    if kind == "M2":
        x[..., (AGES >= 35) & (AGES <= 44)] *= 0.5            # cohorte creuse
    if kind == "M4":
        x[..., (AGES >= 44) & (AGES <= 49)] *= 2.0            # nombreuse : 55–60 ans à l'origine
    series = []
    for t in range(HIST + HOR):
        series.append(x)
        h, E = h0, E0
        if kind == "M5":
            E = E0 * 1.03 ** t
        if kind == "M6" and t >= HIST // 2:
            E = E0 * 1.4
        if kind == "M7":
            h = hazard(a0=55 + 3 * min(t, HIST - 1) / (HIST - 1))
        x = step(x, h, E)
    S = np.stack(series, -1)
    return S[..., :HIST], S[..., HIST:]


def to_bands(S):
    return np.stack([S[..., (AGES >= b) & (AGES < b + 5), :].sum(-2) for b in BANDS], -2)   # [dép, sexe, bande, t]


def table(B, years):
    d, s, b, t = np.indices(B.shape)
    return pd.DataFrame({"profession": "p", "dep": (d + 1).ravel().astype(str), "sex": np.array(["F", "H"])[s.ravel()],
                         "age_lo": BANDS[b.ravel()], "year": np.asarray(years)[t.ravel()], "n": B.ravel()})


def run_n5():
    from sante.estimators import StockFlowLocal
    rows, t0 = [], time.time()
    kinds = ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]
    for k, kind in enumerate(kinds, 1):
        for r in range(REPS):
            rng = np.random.default_rng(SEED + r)
            H_, T_ = world(kind, rng)
            Bh, Bt = to_bands(H_), to_bands(T_)
            if kind == "M3":
                Bh = rng.poisson(Bh).astype(float)
            obs = table(Bh, range(Y0, ORIGIN + 1))
            est = StockFlowLocal().fit(obs, (Y0, ORIGIN), ORIGIN)
            from sante.model import project
            p = project(obs, ORIGIN, HOR, est.rates)
            for h in (5, 10, 15):
                pr = p[p.year == ORIGIN + h]
                tr = table(Bt[..., [h - 1]], [ORIGIN + h])
                m = pr.merge(tr, on=["profession", "dep", "sex", "age_lo", "year"], suffixes=("_p", "_t"))
                bydep = m.groupby("dep")[["n_p", "n_t"]].sum()
                old = m[m.age_lo >= 60][["n_p", "n_t"]].sum()
                rows.append({"monde": kind, "rep": r, "h": h,
                             "err_nat_%": 100 * (m.n_p.sum() / m.n_t.sum() - 1),
                             "mape_dep_%": 100 * ((bydep.n_p - bydep.n_t).abs() / bydep.n_t).mean(),
                             "err_60plus_%": 100 * (old.n_p / old.n_t - 1)})
        print(f"{k}/{len(kinds)} {kind} {time.time() - t0:.0f}s", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "worlds_n5.csv", index=False)
    # plancher de Poisson de M3 : MAPE d'un tirage de Poisson des vraies valeurs à l'origine (dérivé, même mondes)
    floor = []
    for r in range(REPS):
        rng = np.random.default_rng(SEED + r)
        H_, _ = world("M3", rng)
        tot = to_bands(H_)[..., -1].sum((1, 2))
        floor.append(100 * np.mean(np.abs(rng.poisson(tot) - tot) / tot))
    return res, float(np.mean(floor))


def judge(res: pd.DataFrame, floor: float) -> dict:
    g = res.groupby(["monde", "h"])
    summ = g[["err_nat_%", "mape_dep_%", "err_60plus_%"]].mean().round(3)
    h15 = res[res.h == 15].set_index(["monde", "rep"])
    h5 = res[res.h == 5].set_index(["monde", "rep"])
    v = {}
    for m in ("M1", "M3"):
        e = h15.loc[m, "err_nat_%"].abs()
        v[m] = {"max_abs_err_nat_h15": float(e.max()), "passe": bool((e <= 1).all())}
    v["M3"]["mape_dep_h15"] = float(h15.loc["M3", "mape_dep_%"].mean())
    v["M3"]["plancher_poisson_%"] = floor
    v["M3"]["mape_dans_plancher_pm2"] = bool(abs(v["M3"]["mape_dep_h15"] - floor) <= 2)
    v["M2"] = {"err_nat_h15_moy": float(h15.loc["M2", "err_nat_%"].mean()), "passe": None}
    v["M4"] = {"err_60plus_h5_pos": int((h5.loc["M4", "err_60plus_%"] > 0).sum()),
               "err_60plus_h5_moy": float(h5.loc["M4", "err_60plus_%"].mean()),
               "err_60plus_h15_moy": float(h15.loc["M4", "err_60plus_%"].mean())}
    v["M4"]["passe"] = v["M4"]["err_60plus_h5_pos"] >= 16
    for m in ("M5", "M6", "M7"):
        neg = int((h15.loc[m, "err_nat_%"] < 0).sum())
        v[m] = {"negatifs_sur_20": neg, "err_nat_h15_moy": float(h15.loc[m, "err_nat_%"].mean()), "passe": neg >= 16}
    v["M5"]["ecart_a_-12.4_pts"] = float(abs(v["M5"]["err_nat_h15_moy"] + 12.4))
    v["M5"]["passe_ampleur"] = v["M5"]["ecart_a_-12.4_pts"] <= 3
    return {"verdicts": v, "resume": summ.reset_index().to_dict("records")}


# ---------- SBC (N6) : 200 mondes M3, un département de taille médiane ----------
def rates_np(B):
    """Même calcul que sante.model.fit_rates (un département, shrink=None) : B [sexe, bande, année]."""
    cur, prev = B[:, :, :-1], np.roll(B[:, :, :-1], 1, axis=1)
    prev[:, 0] = 0
    base = 0.8 * cur + 0.2 * prev
    base[:, -1] = cur[:, -1] + 0.2 * B[:, -2, :-1]
    nxt = B[:, :, 1:]
    r = nxt.sum(-1) / np.maximum(base.sum(-1), 1e-9)
    s = np.minimum(r, 1.0)
    e = nxt - s[..., None] * base
    inflow = np.where(r > 1.0, e.mean(-1), 0.0)
    return s, inflow


def params(B):
    s, inflow = rates_np(B)
    return np.r_[s[0, [3, 4, 5, 6, 7]], inflow[0].sum()]      # femmes : s(40, 45, 50, 55, 60), entrées totales


PNAMES = ["s40", "s45", "s50", "s55", "s60", "entrees"]


def run_sbc(W=200, L=99):
    from sante.model import fit_rates
    rng0 = np.random.default_rng(SEED)
    size = np.log(np.sqrt(30 * 4000))                          # médiane de la loi log-uniforme (dérivé, ≈ 346)
    # contrôle : rates_np == fit_rates sur un exemple
    H_, _ = world("M1", rng0, sizes=np.full(1, size))
    B = to_bands(H_)[0]
    s_ref, i_ref, _ = fit_rates(table(B[None], range(Y0, ORIGIN + 1)), (Y0, ORIGIN))
    s_np, i_np = rates_np(B)
    check = float(max(np.abs(s_ref[0] - s_np[0]).max(), np.abs(i_ref[0] - i_np[0]).max()))   # cellule F
    ranks, t0 = [], time.time()
    for w in range(W):
        rng = np.random.default_rng(SEED + 1000 + w)
        b, a0 = rng.uniform(0.003, 0.01), rng.uniform(53, 58)
        globals()["_h"] = hazard(b, a0)
        h0 = hazard(b, a0)
        pyr = stationary(h0)
        N0 = np.exp(size) / 2
        x = np.repeat((N0 * pyr / pyr.sum())[None], 2, 0)
        E = np.full(2, N0 / pyr.sum())
        ser = []
        for _ in range(HIST):
            ser.append(x)
            x = step(x, h0, E)
        Bt = to_bands(np.stack(ser, -1)[None])[0]            # vérité (espérance)
        Bo = rng.poisson(Bt).astype(float)                    # observé
        th = params(Bt)
        boot = np.array([params(rng.poisson(Bo).astype(float)) for _ in range(L)])
        u = rng.uniform(size=len(th))                          # départage aléatoire des égalités
        ranks.append((boot < th).sum(0) + np.floor(u * ((boot == th).sum(0) + 1)))
        if (w + 1) % 20 == 0:
            print(f"{w + 1}/{W} SBC {time.time() - t0:.0f}s", flush=True)
    R = np.array(ranks)
    out = {"controle_rates_np_vs_fit_rates": check, "W": W, "L": L, "alpha_bonferroni": 0.01 / len(PNAMES)}
    for j, n in enumerate(PNAMES):
        cnt = np.histogram(R[:, j], bins=20, range=(0, L + 1))[0]
        p = float(stats.chisquare(cnt).pvalue)
        out[n] = {"hist20": cnt.tolist(), "p": p, "passe": p >= 0.01 / len(PNAMES),
                  "rang_moyen_norm": float(R[:, j].mean() / L)}
    return out


def main(what="all"):
    OUT.mkdir(exist_ok=True)
    res = {}
    if what in ("n5", "all"):
        r, floor = run_n5()
        res["N5"] = judge(r, floor)
        print(json.dumps(res["N5"]["verdicts"], indent=1, ensure_ascii=False), flush=True)
    if what in ("sbc", "all"):
        res["SBC"] = run_sbc()
        print(json.dumps(res["SBC"], indent=1, ensure_ascii=False))
    (OUT / f"worlds_{what}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["all"]))
