"""P-B4 : M4 reproduit-il l'APL DREES 2024 commune par commune (IDE, MK, SF, CD) ? Passage du protocole gelé.

Protocole : v2/validation/preregistered/2026-11-15-besoin-p-b4-apl.md (gelé, horodaté 02:17:19 UTC le 2026-11-15).
Écarts écrits avant le passage : v2/docs/lab/reports/2026-11-15-besoin-p-b4-apl.md, § « Écarts au protocole ».

Run (racine du dépôt, liens data/raw et v2/data/raw présents le temps du passage ; ≈ 3 min) :
    PYTHONPATH=v2 uv run python -m besoin.validation.pb4      -> v2/artifacts/besoin_pb4/{results.json, ecarts_*.csv}

Entrées (APL de l'année N : état N−2) :
  cible     APL DREES N par commune (apl_commune.parquet, LO 2.0), France métropolitaine
  P^std     colonne pop_std du même fichier (population N−2 × ω de la DREES ; écart E2)
  S_j       effectif libéral < 65 ans au 31/12/N−2 (CartoSanté FNPS/SNDS : commune_stock pour IDE, MK, CD ; fichier
            sf_popage pour les SF, écart E4) × ETP départemental (honoraires sans dépassement moyens / médiane, E5)
  temps     vol d'oiseau × 1,3 / 50 km/h (repli du protocole, E1)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from besoin.cube import Population
from besoin.estimateurs.m4 import CODE, PAR, M4, deux_etapes, matrice, paliers

OUT = Path("v2/artifacts/besoin_pb4")
APL = "v2/data/processed/besoin/apl_commune.parquet"
STOCK = "v2/data/processed/commune_stock.parquet"
SECTEUR = "v2/data/processed/secteur_stock.parquet"
INFIRMIERS = "v2/data/processed/infirmiers_secteur_age_sexe.parquet"   # SNDS libéraux dep × âge (secteur_stock : Ensemble)
GEO = "v2/data/processed/commune_geo.parquet"
HONO = "v2/data/odbl/besoin/ameli_honoraires.parquet"
SF_XML = "data/raw/cartosante/GetData_com2026_sf_popage.xml"
PLM = {"13055": "132", "75056": "751", "69123": "6938"}         # commune -> préfixe de ses arrondissements
B, GRAINE, ALPHA = 2000, 20261115, 0.0125                       # Bonferroni 4 professions : IC à 98,75 %
SEUILS = dict(rho=0.90, em=0.15, gain=0.05)


def dep_of(com: pd.Series) -> pd.Series:
    return com.str[:3].where(com.str.startswith("97"), com.str[:2])


def part_moins_65(prof: str, year: int) -> tuple[pd.Series, pd.Series]:
    """Par département, RPPS libéral + mixte (secteur_stock ; SNDS libéraux pour les infirmiers) : part des 60–64 ans
    dans les 60 ans et plus, et part des moins de 65 ans dans l'ensemble (lignes communales sans tranche d'âge).
    Département absent : part nationale."""
    if prof == "infirmiers":
        s = pd.read_parquet(INFIRMIERS, columns=["year", "dep", "mode3", "age_band", "n"])
        s = s.assign(age_band=s.age_band.str.replace("Entre", "entre").str.replace("Moins", "moins"))
    else:
        s = pd.read_parquet(SECTEUR, columns=["profession", "year", "dep", "mode3", "age_band", "n"])
        s = s[s.profession == prof]
    s = s[(s.year == year) & (s.mode3 == "liberal_mixte")]
    g = s.groupby(["dep", "age_band"]).n.sum().unstack(fill_value=0)
    bands = [c for c in g.columns if c.startswith("entre") or c.startswith("moins") or c == "65 ans et plus"]
    n6064, n65 = g["entre 60 et 64 ans"], g["65 ans et plus"]
    tot = g[bands].sum(axis=1)
    nat = (n6064.sum() / (n6064.sum() + n65.sum()), 1 - n65.sum() / tot.sum())
    p60 = (n6064 / (n6064 + n65)).where((n6064 + n65) > 0, nat[0])
    ptot = (1 - n65 / tot).where(tot > 0, nat[1])
    return p60.rename("p60"), ptot.rename("ptot")


def sf_communes(year: int) -> pd.DataFrame:
    """CartoSanté sf_popage (com2026) : 14 années croissantes (2012–2025) × 7 tranches (Total d'abord), par commune.
    Ordre vérifié : la somme des tranches égale le total (écart 8 sur 4 297 sur les 3 000 premières communes)."""
    t = Path(SF_XML).read_text()
    d = pd.DataFrame(re.findall(r"<Row><K>([^<]*)</K><V>([^<]*)</V></Row>", t), columns=["com", "n"])
    d["n"] = pd.to_numeric(d.n, errors="coerce").fillna(0)
    per = d.groupby("com").size()
    d = d[d.com.isin(per[per == 98].index)].copy()
    d["i"] = d.groupby("com").cumcount()
    d["year"], d["band"] = 2012 + d.i // 7, d.i % 7
    d = d[(d.year == year) & (d.band > 0)]
    labels = {1: "Moins de 40 ans", 2: "Moins de 40 ans", 3: "40 à 49 ans", 4: "50 à 54 ans", 5: "55 à 59 ans",
              6: "60 ans et plus"}
    return d.assign(age_band=d.band.map(labels)).groupby(["com", "age_band"], as_index=False).n.sum()


def effectifs(prof: str, year: int, pop_tot: pd.Series) -> pd.Series:
    """Effectif libéral de moins de 65 ans par commune au 31/12/year (écart E3 pour la tranche 60+)."""
    if prof == "sages-femmes":
        c = sf_communes(year)
    else:
        c = pd.read_parquet(STOCK, columns=["profession", "year", "com", "age_band", "n"])
        c = c[(c.profession == prof) & (c.year == year)]
    c = c.assign(dep=dep_of(c.com))
    p60, ptot = part_moins_65(prof, year)
    k = np.where(c.age_band == "60 ans et plus", c.dep.map(p60).fillna(p60.mean()),
                 np.where(c.age_band.str.startswith("Total"), c.dep.map(ptot).fillna(ptot.mean()), 1.0))
    n = (c.n * k).groupby(c.com).sum()
    for parent, pre in PLM.items():                                    # SF : PLM en commune seule -> arrondissements
        if parent in n.index:
            arr = pop_tot[pop_tot.index.str.startswith(pre) & (pop_tot.index != parent)]
            n = pd.concat([n.drop(parent), n[parent] * arr / arr.sum()]).groupby(level=0).sum()
    return n


def etp(prof: str, year: int) -> pd.Series:
    """ETP moyen départemental = honoraires sans dépassement moyens / médiane des départements métropolitains (E5)."""
    h = pd.read_parquet(HONO, columns=["annee", "prof", "departement", "type_honoraires_niveau_1",
                                       "type_honoraires_niveau_2", "montant_honoraires_moyens"])
    h = h[(h.prof == CODE[prof]) & (h.annee == year) & h.type_honoraires_niveau_2.isna()
          & (h.departement != "999") & ~h.departement.str.startswith("97")]
    m = h.pivot_table(index="departement", columns="type_honoraires_niveau_1", values="montant_honoraires_moyens",
                      aggfunc="sum")
    sans_dep = m["Ensemble des honoraires"] - m.get("Dépassements", 0).fillna(0)
    return (sans_dep / sans_dep.median()).rename("etp")


def calcul(prof: str, annee: int, detour=1.3, vitesse=50.0) -> tuple[pd.DataFrame, dict]:
    """M4, N1, N2 et l'APL publiée sur les communes métropolitaines de l'APL `annee` (entrées annee − 2)."""
    a = pd.read_parquet(APL)
    a = a[(a.prof == CODE[prof]) & (a.annee == annee) & ~a.com.str.startswith("97")].set_index("com")
    n = effectifs(prof, annee - 2, a.pop_tot)
    e = etp(prof, annee - 2)
    S_all = n * dep_of(n.index.to_series()).map(e).fillna(1.0).to_numpy()
    com = a.index.to_numpy()
    S = S_all.reindex(com, fill_value=0.0).to_numpy()
    P = a.pop_std.to_numpy()
    paliers(CODE[prof])
    W = matrice(com, CODE[prof], detour, vitesse)
    A, _, bilan = deux_etapes(W, S, P)
    geo = pd.read_parquet(GEO, columns=["com", "bv2022"]).set_index("com").bv2022
    bv = geo.reindex(com).fillna(pd.Series(com, index=com)).to_numpy()
    sb = pd.Series(S).groupby(bv).transform("sum").to_numpy()
    pb = pd.Series(P).groupby(bv).transform("sum").to_numpy()
    f = pd.DataFrame(dict(com=com, dep=dep_of(pd.Series(com)).to_numpy(), pop=a.pop_tot.to_numpy(), P=P, S=S,
                          apl=a.apl.to_numpy(), m4=PAR * A,
                          n1=np.divide(PAR * S, P, out=np.zeros_like(S), where=P > 0),
                          n2=np.divide(PAR * sb, pb, out=np.zeros_like(S), where=pb > 0)))
    hors = S_all.drop(index=[c for c in com if c in S_all.index]).sum()
    bilan.update(offre_hors_champ=float(hors), offre_totale=float(S_all.sum()), communes=len(f),
                 apl_manquante=int(f.apl.isna().sum()), effectif_moins_65=float(n.reindex(com).sum()))
    return f.dropna(subset=["apl"]), bilan


def rho(x, y) -> float:
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def em(m, apl) -> float:
    pos = apl > 0
    return float(np.median(np.abs(m[pos] - apl[pos]) / apl[pos]))


def stats(f: pd.DataFrame) -> dict:
    r = {k: rho(f[k].to_numpy(), f.apl.to_numpy()) for k in ("m4", "n1", "n2")}
    return dict(rho_m4=r["m4"], rho_n1=r["n1"], rho_n2=r["n2"], gain=r["m4"] - max(r["n1"], r["n2"]),
                em=em(f.m4.to_numpy(), f.apl.to_numpy()))


def bootstrap(f: pd.DataFrame, b=B, seed=GRAINE) -> dict:
    """Départements entiers tirés avec remise ; M4 n'est pas recalculé (protocole)."""
    rng = np.random.default_rng(seed)
    deps = f.dep.unique()
    rows = {d: np.flatnonzero(f.dep.to_numpy() == d) for d in deps}
    X = f[["m4", "n1", "n2", "apl"]].to_numpy()
    out = {k: [] for k in ("rho_m4", "em", "gain")}
    for _ in range(b):
        idx = np.concatenate([rows[d] for d in rng.choice(deps, len(deps))])
        x = X[idx]
        r = [rho(x[:, k], x[:, 3]) for k in range(3)]
        out["rho_m4"].append(r[0])
        out["gain"].append(r[0] - max(r[1], r[2]))
        out["em"].append(em(x[:, 0], x[:, 3]))
    return {k: [float(np.quantile(v, ALPHA / 2)), float(np.quantile(v, 1 - ALPHA / 2))] for k, v in out.items()}


def kappa(f: pd.DataFrame) -> float:
    """Variante secondaire : scalaire sur l'ETP qui minimise EM (A est linéaire en S)."""
    grid = np.arange(0.5, 2.0005, 0.001)
    pos = f.apl > 0
    m, y = f.m4[pos].to_numpy(), f.apl[pos].to_numpy()
    return float(grid[np.argmin([np.median(np.abs(k * m - y) / y) for k in grid])])


def par_taille(f: pd.DataFrame) -> dict:
    cut = pd.cut(f["pop"], [-1, 999, 10000, np.inf], labels=["<1000", "1000-10000", ">10000"])
    return {str(k): dict(n=len(g), rho=rho(g.m4.to_numpy(), g.apl.to_numpy())) for k, g in f.groupby(cut, observed=True)}


def sensibilite_omphale(prof: str, f: pd.DataFrame) -> float:
    """Hors protocole (contrôle de l'écart E2) : P^std = structure par âge du département (Omphale 2022, 2022) ×
    population communale, poids ω figés ; Spearman de M4 contre l'APL 2024."""
    pop = Population.load()
    pop = pop.__class__(pop.territories, pop.years, pop.sexes, pop.ages, pop.P[:, pop.years_index([2022])],
                        pop.level, pop.scenario, pop.source)
    pc = pop.ventile()
    Bc = M4().predict(pc, years=[2022])
    P = pd.Series(Bc.values[Bc.p(prof), :, 0], Bc.territories)
    P = (P / P.groupby(dep_of(P.index.to_series())).transform("sum")
         * pd.Series(f.P.to_numpy(), f.com.to_numpy()).groupby(f.dep.to_numpy()).sum().reindex(
             dep_of(P.index.to_series())).to_numpy())          # même total départemental que pop_std
    # PLM : ventile() rend la commune parente ; on la répartit sur ses arrondissements au prorata de pop_std
    Pf = P.reindex(f.com.to_numpy()).to_numpy()
    for parent, pre in PLM.items():
        m = f.com.str.startswith(pre).to_numpy() & (f.com != parent).to_numpy()
        if parent in P.index and m.any():
            Pf[m] = P[parent] * f.P.to_numpy()[m] / f.P.to_numpy()[m].sum()
    Pf = np.nan_to_num(Pf)
    W = matrice(f.com.to_numpy(), CODE[prof])
    A, _, _ = deux_etapes(W, f.S.to_numpy(), Pf)
    return rho(A, f.apl.to_numpy())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {}
    for prof in CODE:
        f, bilan = calcul(prof, 2024)                                   # bloquant : deux_etapes lève si 10⁻⁹ échoue
        st = stats(f)
        ic = bootstrap(f)
        ok = dict(rho=st["rho_m4"] >= SEUILS["rho"], em=st["em"] <= SEUILS["em"],
                  gain=st["gain"] >= SEUILS["gain"] and ic["gain"][0] > 0)
        f22, _ = calcul(prof, 2022)
        k = kappa(f22)
        f23, _ = calcul(prof, 2023)
        top = f.assign(ecart_rel=(f.m4 - f.apl) / f.apl.where(f.apl > 0)).reindex(
            (f.m4 - f.apl).abs().sort_values(ascending=False).index).head(20)
        top.to_csv(OUT / f"ecarts_{CODE[prof]}.csv", index=False)
        res[prof] = dict(**st, ic_98_75=ic, criteres=ok, verdict="méthode de l'APL (repli)" if all(ok.values())
                         else "indice maison", bilan=bilan,
                         rapporte=dict(par_taille=par_taille(f), rho_2023=stats(f23)["rho_m4"],
                                       em_2023=stats(f23)["em"], kappa_2022=k,
                                       em_2024_kappa=em(k * f.m4.to_numpy(), f.apl.to_numpy()),
                                       rho_omphale=sensibilite_omphale(prof, f),
                                       moyenne_m4=float((f.P * f.m4).sum() / f.P.sum()),
                                       moyenne_apl=float((f.P * f.apl).sum() / f.P.sum())))
        print(prof, json.dumps({k: v for k, v in res[prof].items() if k != "rapporte"}, ensure_ascii=False),
              flush=True)
        print("  rapporté", json.dumps(res[prof]["rapporte"], ensure_ascii=False), flush=True)
    (OUT / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res


if __name__ == "__main__":
    main()
    sys.exit(0)
