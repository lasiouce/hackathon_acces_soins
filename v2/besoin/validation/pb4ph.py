"""P-B4-PH : M4 (2SFCA, paliers V0) reproduit-il l'APL DREES V0 2013 aux pharmacies ?

Protocole gelé : v2/validation/preregistered/2026-11-15-besoin-p-b4-ph-apl-v0.md ;
écarts écrits avant calcul : v2/docs/lab/reports/2026-11-15-besoin-p-b4-ph-apl-v0.md (commit d9c772f).

Run (racine du dépôt) :
    uv run python v2/besoin/validation/pb4ph.py --cible <csv APL pharmacies V0> --raw <dossier insee>
Sortie : v2/besoin/validation/out/pb4ph.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "v2" / "data" / "processed"
OSRM = ROOT / "v2" / "data" / "odbl" / "besoin" / "distancier_osrm.parquet"
OUT = Path(__file__).resolve().parent / "out"
SEED, B = 20261115, 2000
PALIERS = ((5, 1.0), (10, 0.3), (15, 0.1))   # Notice V0 : [0,5) 1 ; [5,10) 0,3 ; [10,15) 0,1 ; ≥ 15 : 0


def poids(t: np.ndarray) -> np.ndarray:
    w = np.zeros_like(t, dtype=float)
    bas = -np.inf
    for haut, v in PALIERS:
        w[(t >= max(bas, 0)) & (t < haut)] = v
        bas = haut
    return w


def passage() -> pd.DataFrame:
    p = pd.read_parquet(PROC / "passage_commune.parquet")
    return p[["code_source", "geocode", "dep", "bv2022"]]


def vers_2026(df: pd.DataFrame, col: str, val: str, pas: pd.DataFrame) -> pd.Series:
    m = df.merge(pas[["code_source", "geocode"]], left_on=col, right_on="code_source", how="left")
    m["geocode"] = m["geocode"].fillna(m[col])
    return m.groupby("geocode")[val].sum()


def lire_cible(path: Path, pas: pd.DataFrame) -> pd.DataFrame:
    c = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    c["code"] = c["Commune"].str.slice(0, 5)
    c = c.rename(columns={"APL 2013 (nouveau distancier)": "apl2013", "APL 2010 (nouveau distancier)": "apl2010"})
    c = c[~c.code.str.startswith("97")]
    m = c.merge(pas[["code_source", "geocode"]], left_on="code", right_on="code_source", how="left")
    m["geocode"] = m["geocode"].fillna(m["code"])
    n = m.groupby("geocode").code.transform("nunique")
    un = m[n == 1].drop_duplicates("code")
    un = un[un.groupby("code").geocode.transform("nunique") == 1]
    out = un.set_index("geocode")[["apl2010", "apl2013"]]
    return out.apply(lambda c: pd.to_numeric(c, errors="coerce"))   # « ND » = non disponible → manquant (écart 9)


def apl(S: pd.Series, P: pd.Series, d: pd.DataFrame) -> tuple[pd.Series, float]:
    com = sorted(set(P.index) | set(S.index))
    ix = {c: i for i, c in enumerate(com)}
    i = d.com_i.map(ix).values
    j = d.com_j.map(ix).values
    w = poids(d.t_min.values)
    ok = ~(np.isnan(i.astype(float)) | np.isnan(j.astype(float))) & (w > 0)
    i, j, w = i[ok].astype(int), j[ok].astype(int), w[ok]
    W = sparse.coo_matrix((w, (i, j)), shape=(len(com), len(com))).tocsr()   # W[i, j] = w(t_ij), symétrique
    p = P.reindex(com).fillna(0).values
    s = S.reindex(com).fillna(0).values
    dem = W.T @ p                                    # Σ_k w(t_kj) P_k
    R = np.divide(s, dem, out=np.zeros_like(s), where=dem > 0)
    A = W @ R
    cons = float((p * A).sum() / s[dem > 0].sum() - 1)
    return pd.Series(A * 1e5, index=com), cons


def stats(df: pd.DataFrame) -> dict:
    rho = spearmanr(df.m4, df.apl).statistic
    pos = df[df.apl > 0]
    em = float(np.median(np.abs(pos.m4 - pos.apl) / pos.apl))
    n1 = spearmanr(df.n1, df.apl).statistic
    n2 = spearmanr(df.n2, df.apl).statistic
    return {"rho": float(rho), "em": em, "rho_n1": float(n1), "rho_n2": float(n2), "G": float(rho - max(n1, n2))}


def passage_annee(annee: int, cible: pd.DataFrame, pas, d, raw) -> tuple[pd.DataFrame, float]:
    f = pd.read_parquet(PROC / "finess_commune_annee.parquet")
    f = f[(f.categorie == "officine") & (f.year == annee)]
    S = vers_2026(f, "com", "n", pas)
    x = pd.read_excel(raw / "base-pop-historiques-1876-2023.xlsx", header=5, engine="calamine")
    col = {2013: "PMUN2011", 2010: "PMUN2008"}[annee]
    P = vers_2026(x.rename(columns={"CODGEO": "com"}), "com", col, pas)
    met = [c for c in P.index if not str(c).startswith("97")]
    P, S = P.loc[met], S.reindex(met).fillna(0)
    A, cons = apl(S, P, d)
    g = pas.drop_duplicates("geocode").set_index("geocode")
    df = pd.DataFrame({"apl": cible[f"apl{annee}"], "m4": A}).dropna()
    df["pop"] = P.reindex(df.index)
    df["n1"] = (S.reindex(df.index).fillna(0) / df["pop"] * 1e5).replace([np.inf], np.nan)
    bv = g["bv2022"].reindex(P.index)
    n2 = (S.groupby(bv).sum() / P.groupby(bv).sum() * 1e5)
    df["n2"] = n2.reindex(bv.reindex(df.index).values).values
    df["dep"] = g["dep"].reindex(df.index).values
    df = df.dropna(subset=["apl", "m4", "n1", "n2", "dep"])
    return df, cons


def main() -> None:
    a = sys.argv
    cible_csv = Path(a[a.index("--cible") + 1])
    raw = Path(a[a.index("--raw") + 1])
    pas = passage()
    d = pd.read_parquet(OSRM)[["com_i", "com_j", "t_min"]]
    d = pd.concat([d, d.rename(columns={"com_i": "com_j", "com_j": "com_i"})]).drop_duplicates(["com_i", "com_j"])
    cible = lire_cible(cible_csv, pas)
    res = {"protocole": "P-B4-PH", "graine": SEED, "B": B}
    for annee in (2013, 2010):
        df, cons = passage_annee(annee, cible, pas, d, raw)
        r = {"n_communes": int(len(df)), "conservation_ecart_relatif": cons, **stats(df)}
        if annee == 2013:
            rng = np.random.default_rng(SEED)
            deps = df.dep.unique()
            boot = []
            for _ in range(B):
                tir = rng.choice(deps, size=len(deps), replace=True)
                bs = pd.concat([df[df.dep == x] for x in tir])
                boot.append(stats(bs))
            bb = pd.DataFrame(boot)
            r["ic95"] = {k: [float(bb[k].quantile(0.025)), float(bb[k].quantile(0.975))] for k in ("rho", "em", "G")}
            taille = pd.cut(df["pop"], [0, 1000, 10000, np.inf], labels=["<1000", "1000-10000", ">10000"])
            r["rho_par_taille"] = {str(k): float(spearmanr(g.m4, g.apl).statistic) for k, g in df.groupby(taille, observed=True)}
            ecart = (df.m4 - df.apl).abs().sort_values(ascending=False).head(20)
            r["top20_ecarts"] = {k: [float(df.loc[k, "apl"]), float(df.loc[k, "m4"])] for k in ecart.index}
            r["moyennes"] = {"apl": float(df.apl.mean()), "m4": float(df.m4.mean())}
            ok = (r["rho"] >= 0.90) and (r["em"] <= 0.15) and (r["G"] >= 0.05) and (r["ic95"]["G"][0] > 0)
            r["verdict"] = "M4 reproduit l'APL V0 pharmacies" if ok else "échec : M4 pharmaciens reste un indice maison"
            r["bloquant_conservation"] = abs(cons) < 1e-9
        res[str(annee)] = r
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pb4ph.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: (v if k != "2013" else {kk: vv for kk, vv in v.items() if kk != "top20_ecarts"}) for k, v in res.items()},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
