"""Axe 5, partie 2 : Sobol sur les leviers branchés (axe 0, commit 063c192) à côté des incertitudes.

Composition LEVIERS du jumeau (formation, vieillissement, sorties, entrées, lien_formation, étrangers, régulation),
tendanciel identique au stock-flux. Deux groupes de facteurs :
  décision      ce que le décideur règle : quotas, capacité, abandon IFSI, diplômés étrangers, part des zones
                régulées, report de la retraite, cumul emploi-retraite, départs précoces
  connaissance  ce que nous ignorons : choix d'estimation (fenêtre, shrink, entrées, filière), part privée des
                salariés ambigus, fraction de vieillissement, part en cumul, et la réponse des acteurs à la
                régulation (θ, destination des entrants bloqués, part exemptée)
Indices de Sobol par facteur et par groupe (S_G, ST_G) : la part de variance qui vient de la décision, celle qui
vient de la connaissance, et leur interaction (1 − S_déc − S_conn).

Zones de régulation au département : départements dont ≥ 50 % des communes sont en « remplacement seul »
(zonage actuel), ordonnés par part décroissante ; même règle que v2/prototype/server.py:zones(). Statu quo :
part_zones = 0 (tendanciel sans régulation, comme le jumeau par défaut).
Infirmiers : table privée de l'axe 4 (v2/data/processed/infirmiers_secteur_age_sexe.parquet, statut privé,
hypothèse H_ind) : périmètre privé complet, pas seulement les libéraux comme dans la partie 1.

Run (racine) : PYTHONPATH=<instantané du jumeau>:v2:. uv run python -m sensibilite.leviers [--n 1024] [--pilot]
"""
import argparse
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

import jumeau.modules.entrees as _entrees
from sante import estimators as V1
from jumeau.estimators import twin_of
from jumeau.history import sector_table
from jumeau.modules.entrees import evenement_quotas
from jumeau.scenario import LEVIERS, Scenario
from sensibilite.facteurs import CUMUL, LAG, PROFS, SEED, SHRINK, YEARS, F
from sensibilite.methodes import bootstrap

_entrees.scale = lru_cache(maxsize=None)(_entrees.scale)
OUT = Path("v2/sensibilite/out")
ETRANGERS = ("sages-femmes", "dentistes", "kines")          # flux étranger publié (DD76, ER 1075) ; PH, IDE : 0


@lru_cache
def zones() -> dict:
    z = pd.read_parquet("v2/data/processed/zonage_commune.parquet")
    z = z[z.millesime.str.startswith("actuel")]
    z = z.assign(dep=np.where(z.com.str.startswith("97"), z.com.str[:3], z.com.str[:2]))
    share = z.assign(rs=z.statut == "remplacement_seul").groupby(["profession", "dep"]).rs.mean()
    return {p: list(s[s >= 0.5].sort_values(ascending=False).index) for p, s in share.groupby(level=0)
            for s in [s.droplevel(0)]}


@lru_cache
def table(prof: str, variant: str) -> pd.DataFrame:
    if prof == "infirmiers":
        t = pd.read_parquet("v2/data/processed/infirmiers_secteur_age_sexe.parquet")
        t = t[(t.statut == "prive") & ~t.dep.isin(["999", "20"])]
        t = t.groupby(["dep", "sex", "age_lo", "year"], as_index=False).n.sum().assign(profession="infirmiers", sector="prive")
        return t[t.year >= t.groupby("dep").year.transform("min").max()]          # années complètes seulement
    t = sector_table([prof], variant)
    return t[t.sector == "prive"]                     # colonne sector gardée : « bloques » emprunte la démographie du privé


def factors(prof: str, knowledge_only: bool = False) -> list[F]:
    reg = bool(zones().get(prof))
    k = [F("fenetre", "C", levels=(2, 3, 5, 8)), F("shrink", "C", levels=SHRINK),
         F("entrees", "C", levels=("plates", "recentes")),
         F("fraction", "C", 0.18, 0.22, status="supposé ±10 %"),
         F("part_cumul", "C", 0.5 * CUMUL[prof], 2.0 * CUMUL[prof], status="sourcé × [0,5 ; 2]")]
    if prof in ("dentistes", "pharmaciens"):
        k.append(F("filiere", "C", levels=(False, True)))
    if prof != "infirmiers":
        k.append(F("part_privee", "C", levels=("min", "central", "max")))
    if reg:
        k += [F("theta", "C", 0.5, 1.0, status="supposé (fiche θ : plage 0,5–1 pour l'axe 5)"),
              F("repartition", "C", levels=("voisine", "salariat", "sortie"), status="non mesurable")]
    if prof == "dentistes":
        k.append(F("part_exemptee", "C", 0.0, 0.06, status="supposé (spécialistes ≈ 6 % du stock, fiche)"))
    if knowledge_only:
        return k
    d = [F("quotas", "D", 0.8, 1.2, status="DD76 ±20 %"), F("capacite", "D", 0.8, 1.2, status="DD76 ±20 %"),
         F("decalage_retraite", "D", 0.0, 2.0), F("cumul_multiplicateur", "D", 0.5, 2.0),
         F("multiplicateur_precoces", "D", 0.5, 1.5)]
    if prof == "infirmiers":
        d.append(F("abandon", "D", 0.056, 0.105, status="dérivé (ρ 2009-2018 → 2022)"))
    if prof in ETRANGERS:
        d.append(F("etrangers", "D", 0.5, 2.0, status="supposé × [0,5 ; 2]"))
    if reg:
        d.append(F("part_zones", "D", 0.0, 1.0, status="levier (0 = pas de régulation)"))
    return k + d


DEFAULT = {"fenetre": 5, "shrink": 200, "entrees": "plates", "filiere": False, "part_privee": "central",
           "fraction": 0.2, "theta": 0.8, "repartition": "voisine", "part_exemptee": 0.0, "quotas": 1.0,
           "capacite": 1.0, "decalage_retraite": 0.0, "cumul_multiplicateur": 1.0, "multiplicateur_precoces": 1.0,
           "abandon": 0.1045, "etrangers": 1.0, "part_zones": 0.0}


class Model:
    def __init__(self, prof: str, knowledge_only: bool = False):
        self.prof, self.f = prof, factors(prof, knowledge_only)
        self.o = int(table(prof, "central").year.max())
        self._fits, self.runs, self.deps = {}, 0, None

    def estimator(self, w, shrink, entrees, filiere, variant):
        key = (w, shrink, entrees, filiere, variant)
        if key not in self._fits:
            v1 = type("V", (V1.StockFlowLocal,), {"shrink": shrink, "inflow_recent": 2 if entrees == "recentes" else None,
                                                   "inflow_trend": False, "pipeline": filiere})
            est = twin_of(v1, Scenario(modules=LEVIERS), sectors=("bloques",))()
            self._fits[key] = est.fit(table(self.prof, variant), (self.o - w, self.o), self.o)
        return self._fits[key]

    def values(self, u) -> dict:
        v = dict(DEFAULT)
        v.update({f.name: f.value(ui) for f, ui in zip(self.f, u)})
        if "part_cumul" not in v:
            v["part_cumul"] = CUMUL[self.prof]
        return v

    def scenario(self, v) -> Scenario:
        p = self.prof
        params = {"vieillissement.fraction": v["fraction"], "sorties.part_cumul": {p: v["part_cumul"], "*": v["part_cumul"]},
                  "sorties.decalage_retraite": v["decalage_retraite"],
                  "sorties.cumul_multiplicateur": v["cumul_multiplicateur"],
                  "sorties.multiplicateur_precoces": v["multiplicateur_precoces"],
                  "entrees.filiere": v["filiere"], "formation.capacite": v["capacite"],
                  "formation.abandon": {p: v["abandon"] if p == "infirmiers" else 0.0, "*": 0.0},
                  "etrangers.multiplicateur": v["etrangers"]}
        z = zones().get(p)
        if z and int(round(v["part_zones"] * len(z))) > 0:
            params.update({"regulation.zones": {p: z}, "regulation.part_zones": {p: v["part_zones"], "*": 1.0},
                           "regulation.theta": v["theta"],
                           "regulation.repartition": {k: float(k == v["repartition"]) for k in ("voisine", "salariat", "sortie")},
                           "regulation.part_exemptee": {p: v["part_exemptee"], "*": 0.0}})
        ev = [evenement_quotas(v["quotas"], self.o, LAG[p])] if v["quotas"] != 1.0 else []
        return Scenario(name="axe5-leviers", params=params, events=ev, modules=LEVIERS)

    def __call__(self, u, deps: bool = False):
        v = self.values(u)
        est = self.estimator(v["fenetre"], v["shrink"], v["entrees"], v["filiere"], v.get("part_privee", "central"))
        tr = est.trajectory(max(YEARS), self.scenario(v))
        est._traj.clear()                         # le jumeau met chaque trajectoire en cache (mémoire)
        self.runs += 1
        y = []
        for yr in YEARS:
            s = tr.states[yr]
            y.append(s.N[(s.cells.sector == "prive").to_numpy()].sum())
        if not deps:
            return np.array(y)
        s = tr.states[max(YEARS)]
        m = (s.cells.sector == "prive").to_numpy()
        d = pd.Series(s.N[m].sum(axis=1), index=s.cells.territory[m].to_numpy()).groupby(level=0).sum()
        if self.deps is None:
            self.deps = d.index.to_numpy()
        return np.array(y), d.reindex(self.deps).to_numpy()


def design(k: int, groups: dict, n: int, rng) -> np.ndarray:
    """[n, 2 + k + g, k] : A, B, A_B^(i) pour chaque facteur, puis A_B^(G) pour chaque groupe."""
    A, B = rng.random((n, k)), rng.random((n, k))
    cols = [A, B]
    for i in range(k):
        x = A.copy(); x[:, i] = B[:, i]; cols.append(x)
    for idx in groups.values():
        x = A.copy(); x[:, idx] = B[:, idx]; cols.append(x)
    return np.stack(cols, axis=1)


def indices(Y: np.ndarray, k: int, ng: int):
    """Y [n, 2 + k + g] -> S1, ST par facteur puis par groupe (Saltelli 2010 sur Y centré, Jansen)."""
    Y = Y - Y[:, :2].mean()
    yA, yB, yAB = Y[:, 0], Y[:, 1], Y[:, 2:]
    V = np.var(np.concatenate([yA, yB]))
    S1 = np.mean(yB[:, None] * (yAB - yA[:, None]), axis=0) / V
    ST = 0.5 * np.mean((yA[:, None] - yAB) ** 2, axis=0) / V
    return S1, ST


def progress(label, j, n, t0):
    if j % 200 == 0 or j == n:
        el = time.time() - t0
        print(f"{label} {j}/{n} {el:.0f}s reste ~{el / max(j, 1) * (n - j):.0f}s", flush=True)


def run_prof(prof, n, rng, n_mc):
    m = Model(prof)
    k, names = len(m.f), [f.name for f in m.f]
    groups = {"connaissance": [i for i, f in enumerate(m.f) if f.family == "C"],
              "decision": [i for i, f in enumerate(m.f) if f.family == "D"]}
    X = design(k, groups, n, rng)
    flat = X.reshape(-1, k)
    Y, t0 = np.empty((len(flat), len(YEARS))), time.time()
    for j, u in enumerate(flat):
        Y[j] = m(u)
        progress(f"{prof}/leviers", j + 1, len(flat), t0)
    Y = Y.reshape(n, -1, len(YEARS))
    np.savez_compressed(OUT / f"L_{prof}.npz", X=X, Y=Y, names=np.array(names))
    rows = []
    labels = names + [f"[{g}]" for g in groups]
    fam = [f.family for f in m.f] + ["G"] * len(groups)
    for yi, yr in enumerate(YEARS):
        S1, ST = indices(Y[:, :, yi], k, len(groups))
        b1, bt = [], []
        for _ in range(300):
            i = rng.integers(0, n, n)
            a, c = indices(Y[i, :, yi], k, len(groups))
            b1.append(a); bt.append(c)
        q1, qt = np.percentile(b1, [2.5, 97.5], axis=0), np.percentile(bt, [2.5, 97.5], axis=0)
        for j, nm in enumerate(labels):
            rows.append(dict(profession=prof, annee=yr, facteur=nm, groupe=fam[j], S1=S1[j], S1_lo=q1[0, j],
                             S1_hi=q1[1, j], ST=ST[j], ST_lo=qt[0, j], ST_hi=qt[1, j]))
    # fourchettes départementales : connaissance seule, décisions au statu quo
    mk = Model(prof, knowledge_only=True)
    U = rng.random((n_mc, len(mk.f)))
    nat, dep, t0 = [], [], time.time()
    for j, u in enumerate(U):
        a, b = mk(u, deps=True)
        nat.append(a); dep.append(b)
        progress(f"{prof}/fourchettes-dep", j + 1, n_mc, t0)
    dep = np.array(dep)
    ref = mk(np.array([_u(f) for f in mk.f]), deps=True)[1]
    D = pd.DataFrame({"profession": prof, "dep": mk.deps, "n_ref_2050": ref, "p05": np.percentile(dep, 5, axis=0),
                      "p50": np.median(dep, axis=0), "p95": np.percentile(dep, 95, axis=0)})
    D["largeur_rel_pct"] = 100 * (D.p95 - D.p05) / D.n_ref_2050
    return pd.DataFrame(rows), D, m.runs + mk.runs


def _u(f):
    v = DEFAULT[f.name] if f.name in DEFAULT else None
    if f.levels:
        return (f.levels.index(v) + 0.5) / len(f.levels)
    if v is None:
        v = (f.lo * f.hi) ** 0.5
    return (v - f.lo) / (f.hi - f.lo)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--n", type=int, default=1024)
    a.add_argument("--mc", type=int, default=1000)
    a.add_argument("--profs", default=",".join(PROFS))
    a.add_argument("--tag", default="")
    args = a.parse_args()
    rng = np.random.default_rng(SEED)
    S, D, t0 = [], [], time.time()
    for prof in args.profs.split(","):
        s, d, runs = run_prof(prof, args.n, rng, args.mc)
        S.append(s); D.append(d)
        print(f"FAIT {prof} : {runs} runs, {time.time() - t0:.0f}s", flush=True)
    pd.concat(S).to_csv(OUT / f"leviers_sobol{args.tag}.csv", index=False)
    pd.concat(D).to_csv(OUT / f"fourchettes_dep{args.tag}.csv", index=False)
    print(f"TOTAL {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
