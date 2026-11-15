"""Axe 5 du besoin, étape 2 : statistiques gelées sur la grille (protocole 2026-11-15, SHA-256 10a5b285…).

  E_π(T) = |Y(π) − Y(statu quo)|          estimateur servi, Omphale central, offre moyenne, transfert central
  D(T)   = max_e Y(e) − min_e Y(e)        statu quo, mêmes réglages ; e parmi les estimateurs survivants
  R_π(T) = E_π / D ;  R < 1 ⇒ « non distinguable du choix du modèle de besoin » (seuil gelé)
  S_X    = Var(E[Y | X]) / Var(Y) sur la grille π × e × ω × k (× j), niveaux équiprobables
Règle d'affichage déclenchée si, au national en 2050, R(quotas × 1,2) < 1 ou S_e > S_π.

Run (racine, après grille.py) : PYTHONPATH=v2 uv run python -m sensibilite.besoin.stats
  -> out/resultats.json, out/ratio_dep.csv, out/variance_dep.csv
"""
import json

import numpy as np
import pandas as pd

from sensibilite.besoin.grille import OUT, PROFS, SERVI

DECISIVE, SEUIL, H = "quotas x1,2", 1.0, 2050
AXES = ("politique", "estimateur", "omphale", "offre", "transfert")


def charge(prof):
    z = np.load(OUT / f"grille_{prof}.npz", allow_pickle=False)
    return {k: z[k] for k in z.files}


def parts(Y: np.ndarray) -> dict:
    """Parts des effets principaux de chaque axe de Y[π, e, ω, k, j] (niveaux équiprobables) et reste."""
    v = Y.var()
    out = {}
    for i, a in enumerate(AXES):
        if Y.shape[i] == 1:
            out[a] = 0.0
            continue
        m = Y.mean(axis=tuple(x for x in range(Y.ndim) if x != i))
        out[a] = float(m.var() / v) if v > 0 else 0.0
    out["interactions"] = 1.0 - sum(out.values())
    return out


def q(x, p):
    x = x[np.isfinite(x)]
    return float(np.quantile(x, p)) if len(x) else float("nan")


def profession(prof: str) -> tuple[dict, list, list]:
    g = charge(prof)
    pols, est, var_ = list(g["politiques"]), list(g["estimateurs"]), list(g["variantes"])
    terr, years = list(g["territoires"]), list(g["annees"])
    Y, Yref = g["Y"].astype(float), g["Yref"]
    i0, ie = pols.index("statu quo"), est.index(SERVI.get(prof, "M1"))
    allest = est + var_
    res = {"estimateurs": est, "variantes": var_, "politiques": {}, "annees": {}}
    rows, vrows = [], []
    for t in years:
        yi = years.index(t)
        ref = Yref[:, :, 0, :, yi]                                   # [π, e, T], Omphale central, offre moyenne
        D = np.nanmax(ref[i0, :len(est)], axis=0) - np.nanmin(ref[i0, :len(est)], axis=0)
        sc = {}
        for name, sel in (("sans M0", [e for e in est if e != "M0"]), *[(f"avec {v}", est + [v]) for v in var_]):
            ix = [allest.index(e) for e in sel]
            sc[name] = float(np.nanmax(ref[i0, ix, -1]) - np.nanmin(ref[i0, ix, -1]))
        Yo = Y[i0, ie, 0, :, 0, :, yi]                               # [k, T] statu quo, servi, central
        r_t = dict(D_FR=float(D[-1]), D_dep_med=q(D[:-1], .5), D_dep_p10=q(D[:-1], .1), D_dep_p90=q(D[:-1], .9),
                   D_variantes_FR=sc,
                   echelle_omphale_FR=float(np.nanmax(Yref[i0, ie, :, -1, yi]) - np.nanmin(Yref[i0, ie, :, -1, yi])),
                   echelle_offre_p5_p95_FR=q(Yo[:, -1], .95) - q(Yo[:, -1], .05),
                   C_FR_par_estimateur={e: float(np.exp(ref[i0, allest.index(e), -1])) for e in allest},
                   politiques={})
        if prof == "pharmaciens":
            il = pols.index("L23 vaccination en officine")
            dl = Y[il, ie, 0, 0, :, -1, yi] - Y[i0, ie, 0, 0, 0, -1, yi]      # log(B₀/B') : ρ s'annule
            r_t["echelle_transfert_p5_p95_FR"] = q(dl, .95) - q(dl, .05)
        for ip, pn in enumerate(pols):
            if ip == i0:
                continue
            E = np.abs(ref[ip, ie] - ref[i0, ie])
            with np.errstate(divide="ignore", invalid="ignore"):
                R = np.where(D > 0, E / D, np.inf)
            ok = np.isfinite(E[:-1]) & np.isfinite(D[:-1])
            r_t["politiques"][pn] = dict(E_FR=float(E[-1]), R_FR=float(R[-1]),
                                         verdict_FR="distinguable" if R[-1] >= SEUIL else "non distinguable",
                                         R_dep_med=q(R[:-1][ok], .5), R_dep_p10=q(R[:-1][ok], .1),
                                         R_dep_p90=q(R[:-1][ok], .9),
                                         part_dep_distinguable=float((R[:-1][ok] >= SEUIL).mean()),
                                         n_dep=int(ok.sum()))
            if t == H:
                rows += [dict(profession=prof, territoire=terr[i], politique=pn, E=E[i], D=D[i], R=R[i])
                         for i in range(len(terr))]
        # décomposition de la variance par territoire
        sh = []
        for i in range(len(terr)):
            y = Y[:, :, :, :, :, i, yi]
            if not np.isfinite(y).all():
                continue
            p = parts(y)
            sh.append(p)
            if t == H:
                vrows.append(dict(profession=prof, territoire=terr[i], **p))
        fr = [p for p, i in zip(sh, range(len(terr))) if terr[i] == "FR"]
        dep = pd.DataFrame(sh[:-1] if fr else sh)
        r_t["variance_FR"] = parts(Y[:, :, :, :, :, -1, yi])
        r_t["variance_dep"] = {a: dict(med=float(dep[a].median()), p10=float(dep[a].quantile(.1)),
                                       p90=float(dep[a].quantile(.9))) for a in dep.columns}
        best = max(r_t["politiques"], key=lambda k: r_t["politiques"][k]["E_FR"])
        r_t["meilleur_levier"] = best
        res["annees"][int(t)] = r_t
    h = res["annees"][H]
    res["regle_affichage"] = bool(h["politiques"][DECISIVE]["R_FR"] < SEUIL
                                  or h["variance_FR"]["estimateur"] > h["variance_FR"]["politique"])
    return res, rows, vrows


def main():
    out, rows, vrows = {}, [], []
    for p in PROFS:
        if not (OUT / f"grille_{p}.npz").exists():
            print(f"{p}: grille absente")
            continue
        r, a, b = profession(p)
        out[p], rows, vrows = r, rows + a, vrows + b
        h = r["annees"][H]
        d = h["politiques"][DECISIVE]
        b_ = h["meilleur_levier"]
        print(f"{p:13s} D_FR={h['D_FR']:.3f}  quotas×1,2 E={d['E_FR']:.3f} R={d['R_FR']:.2f} ({d['verdict_FR']}), "
              f"dép. R≥1 {d['part_dep_distinguable']:.0%} | meilleur {b_} R={h['politiques'][b_]['R_FR']:.2f} | "
              f"S_π={h['variance_FR']['politique']:.2f} S_e={h['variance_FR']['estimateur']:.2f} "
              f"S_ω={h['variance_FR']['omphale']:.2f} S_k={h['variance_FR']['offre']:.2f} "
              f"S_j={h['variance_FR']['transfert']:.3f} | règle={r['regle_affichage']}")
    (OUT / "resultats.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    pd.DataFrame(rows).to_csv(OUT / "ratio_dep.csv", index=False, float_format="%.5g")
    pd.DataFrame(vrows).to_csv(OUT / "variance_dep.csv", index=False, float_format="%.4g")


if __name__ == "__main__":
    main()
