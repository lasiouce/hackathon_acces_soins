"""Axe 3, niveau 3 : différence de différences sur le zonage conventionnel (protocole pré-enregistré).

Protocole : v2/validation/preregistered/2026-11-14-axe3-n3-leviers-did.md (SHA-256 c37e36457f12…).
Run (racine du dépôt) : PYTHONPATH=v2 uv run --with scipy python -m validation.did  -> v2/validation/out/

Cellule = département × classe de zone ; Y = effectif libéral CartoSanté (somme des communes appariées).
D[d, t] = log Y[d, traitée, t] − log Y[d, témoin, t]. Tout estimateur ici est une moyenne entre départements
de différences de D : c'est la DiD à effets fixes cellule et département × année, écrite en clair.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
ZONAGE = Path(__file__).parent / "raw" / "zonage_conv_c987.geojson"
OUT = Path(__file__).parent / "out"
SEED, BOOT = 20261114, 2000
MIN_Y = 10


def zonage() -> pd.DataFrame:
    feats = json.loads(ZONAGE.read_text())["features"]
    z = pd.DataFrame([f["properties"] for f in feats])[["codgeo", "z_infi", "z_kine", "z_dent"]]
    return z.rename(columns={"codgeo": "com"})


def cells(prof: str, zcol: str, zones: tuple, ref_year: int) -> tuple[pd.DataFrame, dict]:
    """Y[dep, zone, year] sur les communes appariées ; renvoie aussi le bilan d'appariement."""
    s = pd.read_parquet(ROOT / "data/processed/stock_commune.parquet", filters=[("profession", "==", prof)])
    s = s.groupby(["com", "dep", "year"], as_index=False).n.sum()
    z = zonage()[["com", zcol]].rename(columns={zcol: "zone"})
    m = s.merge(z, on="com", how="left")
    ref = m[m.year == ref_year]
    match = {"profession": prof, "ref_year": ref_year,
             "communes": int(ref.com.nunique()), "communes_appariees": int(ref.zone.notna().sum()),
             "effectif_ref": int(ref.n.sum()), "effectif_apparie_ref": int(ref.loc[ref.zone.notna(), "n"].sum()),
             "effectif_zone9_ref": int(ref.loc[ref.zone == "9", "n"].sum())}
    m = m[m.zone.isin(zones)]
    return m.groupby(["dep", "zone", "year"]).n.sum().unstack("year"), match


def diff(Y: pd.DataFrame, treated: str, control: str, ref_year: int) -> tuple[pd.DataFrame, pd.Series]:
    """D[d, t] pour les départements dont les deux cellules ont Y >= MIN_Y à l'année de référence."""
    a, b = Y.xs(treated, level="zone"), Y.xs(control, level="zone")
    deps = a.index.intersection(b.index)
    a, b = a.loc[deps], b.loc[deps]
    keep = (a[ref_year] >= MIN_Y) & (b[ref_year] >= MIN_Y)
    a, b = a[keep], b[keep]
    with np.errstate(divide="ignore"):
        D = np.log(a) - np.log(b)
    return D.replace([np.inf, -np.inf], np.nan), a[ref_year]


def t_ci(x: np.ndarray, w: np.ndarray | None = None) -> dict:
    x = np.asarray(x, float)
    ok = ~np.isnan(x)
    x = x[ok]
    G = len(x)
    if w is not None:
        w = np.asarray(w, float)[ok]
        w = w / w.sum()
        est = float((w * x).sum())
        se = float(np.sqrt(G / (G - 1) * (w ** 2 * (x - est) ** 2).sum()))
    else:
        est, se = float(x.mean()), float(x.std(ddof=1) / np.sqrt(G))
    q = stats.t.ppf(0.975, G - 1)
    p = float(2 * stats.t.sf(abs(est) / se, G - 1)) if se > 0 else float("nan")
    return {"est": est, "se": se, "lo": est - q * se, "hi": est + q * se, "p": p, "G": G}


def did(D: pd.DataFrame, pre: list, post: list, w=None) -> dict:
    return t_ci(D[post].mean(1) - D[pre].mean(1), w)


def event_study(D: pd.DataFrame, ref: int) -> pd.DataFrame:
    rows = [{"year": k, **t_ci(D[k] - D[ref])} for k in D.columns if k != ref]
    return pd.DataFrame(rows).set_index("year")


def hotelling(D: pd.DataFrame, leads: list, ref: int) -> dict:
    """H0 : E[D_k − D_ref] = 0 pour tous les k de `leads` ; T² de Hotelling entre départements -> F(q, G − q)."""
    X = (D[leads].sub(D[ref], axis=0)).dropna().to_numpy()
    G, q = X.shape
    m, S = X.mean(0), np.cov(X, rowvar=False)
    T2 = G * m @ np.linalg.solve(S, m)
    F = (G - q) / (q * (G - 1)) * T2
    return {"T2": float(T2), "F": float(F), "df": [q, G - q], "p": float(stats.f.sf(F, q, G - q)), "G": G}


def slope(D: pd.DataFrame, years: list, ref: int) -> dict:
    """Pente moyenne de D − D_ref sur `years` (MCO par département, puis moyenne entre départements)."""
    X = np.array(years, float) - np.mean(years)
    Y = D[years].sub(D[ref], axis=0).dropna()
    b = (Y.to_numpy() * X).sum(1) / (X ** 2).sum()
    return t_ci(b)


def theta(Y: pd.DataFrame, D: pd.DataFrame, post: list, ref: int) -> dict:
    """Part contraignante du plafond : β_obs / β_mod, IC par bootstrap des départements."""
    c = Y.xs("3", level="zone").loc[D.index]
    g3 = np.log(c[post]).sub(np.log(c[ref]), axis=0)
    mod = np.minimum(0, -g3).mean(1).to_numpy()
    obs = D[post].sub(D[ref], axis=0).mean(1).to_numpy()
    ok = ~(np.isnan(mod) | np.isnan(obs))
    mod, obs = mod[ok], obs[ok]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(obs), (BOOT, len(obs)))
    boot = obs[idx].mean(1) / mod[idx].mean(1)
    return {"beta_obs": float(obs.mean()), "beta_mod": float(mod.mean()), "theta": float(obs.mean() / mod.mean()),
            "lo": float(np.quantile(boot, 0.025)), "hi": float(np.quantile(boot, 0.975)), "G": int(len(obs))}


def placebo_verdict(b_pl: dict, b_main: dict) -> str:
    same = np.sign(b_pl["est"]) == np.sign(b_main["est"])
    return "échoue (même signe, ≥ moitié)" if same and abs(b_pl["est"]) >= 0.5 * abs(b_main["est"]) else "passe"


def e1() -> dict:
    yrs_pre, yrs_post, ref = list(range(2004, 2009)), list(range(2012, 2020)), 2008
    Y, match = cells("infirmiers-liberaux", "z_infi", ("1", "3", "4", "5"), ref)
    D, w = diff(Y, "5", "3", ref)
    D = D[list(range(2004, 2020))]
    es = event_study(D, ref)
    main = did(D, yrs_pre, yrs_post)
    res = {
        "appariement": match,
        "G": int(D.notna().all(1).sum()),
        "T1_tendances_paralleles": hotelling(D, [2004, 2005, 2006, 2007], ref),
        "T2_placebo_date_2006": did(D, [2004, 2005], [2006, 2007, 2008]),
        "T5_effet": main,
        "T5_effet_pondere": did(D, yrs_pre, yrs_post, w.loc[D.index]),
        "transition_2009_2011": did(D, yrs_pre, [2009, 2010, 2011]),
    }
    # T3 : dentistes, même traitement z_infi ; série dentiste dès 2006
    Yd, match_d = cells("dentistes", "z_infi", ("3", "5"), ref)
    Dd, _ = diff(Yd, "5", "3", ref)
    res["T3_placebo_dentistes"] = did(Dd, [2006, 2007, 2008], yrs_post)
    res["T3_placebo_dentistes"]["appariement"] = match_d
    res["T3_verdict"] = placebo_verdict(res["T3_placebo_dentistes"], main)
    # T4 : zone 4 (très dotée, non régulée) vs 3
    D4, _ = diff(Y, "4", "3", ref)
    res["T4_placebo_zone4"] = did(D4[list(range(2004, 2020))], yrs_pre, yrs_post)
    res["T4_verdict"] = placebo_verdict(res["T4_placebo_zone4"], main)
    # secondaire, rapporté : incitations en zone 1 (très sous-dotée) vs 3
    D1, _ = diff(Y, "1", "3", ref)
    res["zone1_incitations"] = did(D1[list(range(2004, 2020))], yrs_pre, yrs_post)
    res["mecanisme_theta"] = theta(Y, D, yrs_post, ref)
    t1, t2 = res["T1_tendances_paralleles"]["p"] >= 0.10, res["T2_placebo_date_2006"]["lo"] <= 0 <= res["T2_placebo_date_2006"]["hi"]
    res["design_valide"] = bool(t1 and t2 and res["T3_verdict"] == "passe" and res["T4_verdict"] == "passe")
    es4 = event_study(D4[list(range(2004, 2020))], ref)
    esd = event_study(Dd, ref)
    return res, es, es4, esd


def e2() -> dict:
    ref = 2011
    Y, match = cells("kines", "z_kine", ("3", "5"), ref)
    D, _ = diff(Y, "5", "3", ref)
    D = D[list(range(2005, 2018))]
    return {"appariement": match, "G": int(D.notna().all(1).sum()),
            "tendances_paralleles": hotelling(D, list(range(2005, 2011)), ref),
            "pente_marche_2011_2014": slope(D, [2011, 2012, 2013, 2014], ref),
            "pente_arret_2014_2017": slope(D, [2014, 2015, 2016, 2017], 2014),
            "difference_pentes": t_ci(_slopes(D, [2014, 2015, 2016, 2017]) - _slopes(D, [2011, 2012, 2013, 2014]))}, event_study(D, ref)


def _slopes(D, years):
    X = np.array(years, float) - np.mean(years)
    return (D[years].to_numpy() * X).sum(1) / (X ** 2).sum()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    r1, es, es4, esd = e1()
    r2, es_k = e2()
    es.to_csv(OUT / "did_e1_event_study.csv")
    es4.to_csv(OUT / "did_e1_event_study_zone4.csv")
    esd.to_csv(OUT / "did_e1_event_study_dentistes.csv")
    es_k.to_csv(OUT / "did_e2_event_study_kines.csv")
    (OUT / "did_results.json").write_text(json.dumps({"E1_infirmiers": r1, "E2_kines": r2}, indent=1, ensure_ascii=False))
    print(json.dumps({"E1_infirmiers": r1, "E2_kines": r2}, indent=1, ensure_ascii=False))
    print(es.round(4).to_string())


if __name__ == "__main__":
    main()
