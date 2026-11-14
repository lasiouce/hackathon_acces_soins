"""Prototype de l'écran de décision (direction A) : sert index.html et /api/* à partir du jumeau.

Run (racine du dépôt) : uv run python v2/prototype/server.py [port]   -> http://localhost:8766

Pour une profession, un territoire et des leviers, renvoie :
  - l'observé (secteur privé = « libéral » au sens de la décision du 2026-11-14) jusqu'à l'origine,
  - le tendanciel et le scénario jusqu'en 2050 (twin_of(StockFlowLocal), état à 2 secteurs),
  - l'écart scénario − tendanciel décomposé par flux du registre (somme exacte : même état de départ),
  - une fourchette indicative : pente d'erreur de backtest × horizon × 1,6 (méthode de l'observatoire,
    reprise A3), mesurée ici sur le total national privé. Aucun backtest n'existe à 2050 : extrapolation.
Limites du prototype : grain départemental (la commune coûte ~3 s par scénario) ; la régulation communale
est approchée au département (≥ 50 % des communes en « remplacement seul ») ; le levier retraite a une
anomalie connue (tranche 65+ ouverte, open.md).
"""
import json
import os
import sys
import time
from functools import lru_cache
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "v2"), str(ROOT)]
os.chdir(ROOT)

from sante import estimators as V1  # noqa: E402
from jumeau.estimators import twin_of  # noqa: E402
from jumeau.history import sector_table  # noqa: E402
from jumeau.module import REGISTRY, discover  # noqa: E402
from jumeau.modules.entrees import evenement_quotas, selecteur_region  # noqa: E402
from jumeau.modules.sorties import evenement_retraite  # noqa: E402
from jumeau.scenario import FAMILLES, LEVIERS, Scenario  # noqa: E402

HERE = Path(__file__).resolve().parent
PROFS = {"sages-femmes": "Sages-femmes", "dentistes": "Chirurgiens-dentistes", "pharmaciens": "Pharmaciens",
         "kines": "Masseurs-kinésithérapeutes", "infirmiers": "Infirmiers"}
# Infirmiers : table axe 4 par secteur × âge × sexe (SNDS libéraux + BTS salariés, 2013-2023), branchée dans
# jumeau.history.sector_table ; totaux vérifiés contre les sources (critère C18 du jumeau).
MISSING = {}
try:   # version du code, pour la traçabilité des fiches exportées
    import subprocess
    VERSION = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip() or "?"
except Exception:
    VERSION = "?"
LAG = {"pharmaciens": 6, "dentistes": 6, "sages-femmes": 5, "kines": 5, "infirmiers": 3}   # v2/sante/levers_v1.py (supposé)
DECISION = 2026
# Leviers suspendus tant que les défauts de la seconde revue du jumeau sont ouverts
# (v2/docs/lab/reports/2026-11-14-revue-adversariale-axe0-v2.md) : retraite (tranche 65+), régulation (non conservative).
# Réactivés après la troisième revue (2026-11-14) : plus de défaut bloquant dans le jumeau ; conservation
# vérifiée (total tous secteurs scénario − tendanciel ≤ 0,5 personne en 2050 pour CD, MK, SF).
SUSPENDUS: dict = {}
H = 2050
# Modèle servi : C1 (cohortes bayésiennes, axe 2 étape 2 : taux de base surchargés, v2/methodes/c1_jumeau.py) par
# défaut ; A0 (stock-flux à taux locaux) par JUMEAU_MODELE=A0. Décision « C1 servi par la carte » (2026-11-14).
MODELE_CHOIX = os.environ.get("JUMEAU_MODELE", "C1").upper()
REG = LEVIERS          # composition « leviers » du jumeau (commit 063c192) : tendanciel identique à l'écart 0,0
# Leviers exposés, par famille (décision du 2026-11-14). `param` renvoie au Param du jumeau : son statut
# (sourcé / supposé), sa source et son unité sont lus dans le registre, pas recopiés ici.
LEVIERS_UI = [
    dict(k="quotas", famille="former", type="range", param="entrees.multiplicateur", label="Places en formation",
         min=0.7, max=1.5, step=0.05, default=1.0, fmt="pct", delai="lent : après la durée des études"),
    dict(k="quotas_region", famille="former", type="toggle", param="entrees.multiplicateur", default=0,
         label="… seulement dans la région affichée", delai="lent"),
    dict(k="etrangers", famille="attirer", type="range", param="etrangers.multiplicateur", label="Diplômés étrangers accueillis",
         min=0.0, max=2.0, step=0.1, default=1.0, fmt="x", delai="moyen : 1 à 3 ans"),
    dict(k="regul", famille="installer", type="toggle", param="regulation.zones", default=0,
         label="Installation régulée (remplacement d'un départ seulement)", delai="rapide"),
    dict(k="part_zones", famille="installer", type="range", param="regulation.part_zones", label="Part des zones régulées",
         min=0.0, max=1.0, step=0.1, default=1.0, fmt="pct0", delai="rapide"),
    dict(k="dest", famille="installer", type="select", param="regulation.repartition", label="Les entrants bloqués vont…",
         options={"salariat": "vers le salariat", "sortie": "hors de la profession", "voisine": "dans une zone voisine"},
         default="salariat", delai="rapide"),
    dict(k="retraite", famille="retenir", type="range", param="sorties.decalage_retraite", label="Report de la cessation d'activité",
         min=0.0, max=3.0, step=0.5, default=0.0, fmt="ans", delai="rapide, montée de 3 mois par an"),
    dict(k="cumul", famille="retenir", type="range", param="sorties.cumul_multiplicateur", label="Cumul emploi-retraite",
         min=0.5, max=2.0, step=0.1, default=1.0, fmt="x", delai="rapide"),
    dict(k="precoces", famille="retenir", type="range", param="sorties.multiplicateur_precoces", label="Départs avant 60 ans",
         min=0.5, max=1.5, step=0.1, default=1.0, fmt="x", delai="rapide"),
    # Hypothèses de contexte : pas des politiques, et hors du jumeau (appliquées à la sortie). Statut et source écrits ici.
    dict(k="pop_scen", famille="contexte", type="select", param=None, label="Population (Insee Omphale 2022)",
         options={"central": "scénario central", "pop_basse": "population basse", "pop_haute": "population haute"},
         default="central", delai="—", status="sourcé",
         source="Insee, Omphale 2022, tableaux détaillés départements (page 7747107) : 3 scénarios, 2018–2070",
         unit="habitants"),
    dict(k="activite", famille="contexte", type="range", param=None, label="Activité moyenne par professionnel",
         min=0.8, max=1.1, step=0.05, default=1.0, fmt="pct", delai="immédiat", status="supposé",
         source="aucune série ouverte d'équivalents temps plein vérifiée ; DREES, Les Dossiers n° 76 (2021) projette « à comportements constants » (= 1)",
         unit="× activité d'aujourd'hui"),
]
UI = {l["k"]: l for l in LEVIERS_UI}


@lru_cache(maxsize=1)
def population() -> pd.DataFrame:
    """Habitants par (scénario, année) × département, Insee Omphale 2022 (data/processed/population.parquet, chargeur v1)."""
    p = pd.read_parquet(ROOT / "data" / "processed" / "population.parquet")
    return p.groupby(["scenario", "year", "dep"])["pop"].sum().unstack("dep")


def pop_series(scen: str, deps, years) -> list[float]:
    t = population().loc[scen]
    cols = [d for d in deps if d in t.columns]
    return [float(t.loc[y, cols].sum()) if y in t.index else float("nan") for y in years]


def lever_meta():
    reg = discover()
    params = {f"{n}.{p.name}": p for n, c in reg.items() for p in c.params}
    out = []
    for l in LEVIERS_UI:
        p = params.get(l["param"])
        out.append({**l, "status": p.status if p else l.get("status", "?"), "source": p.source if p else l.get("source", ""),
                    "unit": p.unit if p else l.get("unit", "")})
    return out
REGIONS = {"11": "Île-de-France", "24": "Centre-Val de Loire", "27": "Bourgogne-Franche-Comté", "28": "Normandie",
           "32": "Hauts-de-France", "44": "Grand Est", "52": "Pays de la Loire", "53": "Bretagne",
           "75": "Nouvelle-Aquitaine", "76": "Occitanie", "84": "Auvergne-Rhône-Alpes",
           "93": "Provence-Alpes-Côte d'Azur", "94": "Corse", "01": "Guadeloupe", "02": "Martinique", "03": "Guyane",
           "04": "La Réunion", "06": "Mayotte"}


@lru_cache(maxsize=1)
def geo() -> pd.DataFrame:
    s = pd.read_parquet("data/processed/stock.parquet", columns=["dep", "dep_name", "region"]).drop_duplicates("dep")
    return s.assign(region_name=s.region.map(REGIONS).fillna(s.region)).set_index("dep")


@lru_cache(maxsize=1)
def zones() -> dict:
    """Départements dont ≥ 50 % des communes sont en « remplacement seul » (zonage actuel), par profession."""
    z = pd.read_parquet("v2/data/processed/zonage_commune.parquet")
    z = z[z.millesime.str.startswith("actuel")]
    z = z.assign(dep=np.where(z.com.str.startswith("97"), z.com.str[:3], z.com.str[:2]))
    share = z.assign(rs=z.statut == "remplacement_seul").groupby(["profession", "dep"]).rs.mean()
    # ordre de priorité : la part de communes en « remplacement seul » décroissante (regulation.part_zones l'utilise)
    return {p: list(s[s >= 0.5].sort_values(ascending=False).index) for p, s in share.groupby(level=0)
            for s in [s.droplevel(0)]}


# Diplômés annuels France entière quand data/raw (non versionné) est absent : seules valeurs publiées dans le dépôt.
# Infirmiers : DREES, enquête Écoles, jeu 491, diplômés t+3 des entrées 2020-2022 (fiche param-ide-rendement-diplomes,
# mise à jour 29/10/2026). Aucune valeur citée dans le dépôt pour les autres professions.
DIPLOMES_FICHES = {"infirmiers": [(2023, 24215), (2024, 25249), (2025, 26020)]}


class Model:
    def __init__(self, prof: str):
        t = sector_table([prof])
        self.prof, self.o = prof, int(t.year.max())
        self.t = t
        self.est = twin_of(V1.StockFlowLocal, Scenario(modules=REG), sectors=("public",))().fit(t, (self.o - 5, self.o), self.o)
        if MODELE_CHOIX == "C1":
            from methodes.c1_jumeau import install, pente
            install(self.est, prof, H)
        self.modele = MODELE_CHOIX
        self.base = self.est.trajectory(H, Scenario(modules=REG))
        self.cells = self.base.states[H].cells.reset_index(drop=True)
        self.obs = t[t.sector == "prive"].groupby(["dep", "year"]).n.sum()
        self.k = pente(prof) if MODELE_CHOIX == "C1" else self.error_slope()

    def error_slope(self) -> float:
        """Pente |erreur| / horizon du total national privé, origines o−9 … o−3, × 1,6 (≈ 8 cas sur 10)."""
        obs = self.t[self.t.sector == "prive"].groupby("year").n.sum()
        hs, es = [], []
        for c in range(max(int(self.t.year.min()) + 5, self.o - 9), self.o - 2):
            tc = self.t[self.t.year <= c]
            e = twin_of(V1.StockFlowLocal, Scenario(modules=REG), sectors=("public",))().fit(tc, (c - 5, c), c)
            tr = e.trajectory(self.o, Scenario(modules=REG))
            for y in range(c + 1, self.o + 1):
                s = tr.states[y]
                pred = s.N[(s.cells.sector == "prive").to_numpy()].sum()
                hs.append(y - c)
                es.append(abs(pred / obs[y] - 1))
        h, e = np.array(hs, float), np.array(es)
        return float(1.6 * (h * e).sum() / (h ** 2).sum()) if len(h) else float("nan")

    def scenario(self, lv: dict, terr: str = "FR") -> Scenario:
        d = max(self.o, DECISION)
        ev, params = [], {}
        if lv["quotas"] != 1:
            sel = None
            if lv["quotas_region"]:
                g = geo()
                reg = terr[1:] if terr.startswith("R") else g.loc[terr[1:], "region"] if terr.startswith("D") else None
                if reg is None:
                    raise ValueError("quotas régionaux : choisir une région ou un département")
                sel = selecteur_region(reg, self.est.state.cells, self.prof)
            ev.append(evenement_quotas(lv["quotas"], d, LAG[self.prof], selector=sel, source="prototype : quotas"))
        if lv["etrangers"] != 1:
            params["etrangers.multiplicateur"] = lv["etrangers"]
        if lv["retraite"]:
            ev += evenement_retraite(lv["retraite"], d, source="prototype : report de la cessation")
        if lv["cumul"] != 1:
            params["sorties.cumul_multiplicateur"] = lv["cumul"]
        if lv["precoces"] != 1:
            params["sorties.multiplicateur_precoces"] = lv["precoces"]
        # même arrondi que le jumeau (regulation.py : round(part × n)) ; 0 zone retenue = pas de régulation
        if lv["regul"] and zones().get(self.prof) and int(round(lv["part_zones"] * len(zones()[self.prof]))) > 0:
            params["regulation.zones"] = {self.prof: zones()[self.prof]}
            params["regulation.part_zones"] = {self.prof: lv["part_zones"], "*": 1}
            params["regulation.repartition"] = {k: float(k == lv["dest"]) for k in ("voisine", "salariat", "sortie")}
        return Scenario("prototype", params=params, events=ev, modules=REG)

    def answer(self, lv, terr):
        t0 = time.perf_counter()
        scn = self.est.trajectory(H, self.scenario(lv, terr))
        ms = (time.perf_counter() - t0) * 1000
        g = geo()
        # identifiants préfixés : « 84 » est à la fois une région (ARA) et un département (Vaucluse)
        if terr.startswith("D") and terr[1:] in g.index:
            deps = [terr[1:]]
        elif terr.startswith("R"):
            deps = list(g.index[g.region == terr[1:]])
        else:
            deps = list(g.index)
        deps = [d for d in deps if d in set(self.cells.territory)]
        c = self.cells
        # les cellules dépendent du scénario (la régulation ajoute un secteur « bloques ») : masque par trajectoire
        def mk(tr, dep_list):
            cc = tr.states[H].cells
            return ((cc.sector == "prive") & cc.territory.isin(dep_list)).to_numpy()
        mb, ms_ = mk(self.base, deps), mk(scn, deps)
        masks = {id(self.base): mb, id(scn): ms_}
        years = list(range(self.o, H + 1))
        tot = lambda tr, y: float(tr.states[y].N[masks[id(tr)]].sum()) if y > self.o else self.obs_total(deps, self.o)
        base = [tot(self.base, y) for y in years]
        sc = [tot(scn, y) for y in years]
        flows = {}
        for tr, sign in ((scn, 1), (self.base, -1)):
            for y, f, _, v in tr.ledger:
                if f == "vieillissement":
                    continue
                v = np.asarray(v)
                if v.ndim != 1 or len(v) != len(masks[id(tr)]):
                    continue        # comptes du vivier national (formation : diplômés, abandons) : pas des cellules
                flows.setdefault(f, np.zeros(len(years)))[y - self.o] += sign * float(v[masks[id(tr)]].sum())
        flows = {f: np.cumsum(v).round(1).tolist() for f, v in flows.items() if np.abs(v).sum() > 1e-6}
        # matrice : départements du territoire (ou tous) × années, écart relatif et niveau
        my = [y for y in years if (y - self.o) % 3 == 0 or y == H]
        rows = []
        show = deps if len(deps) > 1 else [d for d in g.index[g.region == g.loc[deps[0], "region"]] if d in set(c.territory)]
        for dep in show:
            m1, m2 = mk(self.base, [dep]), mk(scn, [dep])
            b = [float(self.base.states[y].N[m1].sum()) if y > self.o else self.obs_total([dep], self.o) for y in my]
            s_ = [float(scn.states[y].N[m2].sum()) if y > self.o else b[i] for i, y in enumerate(my)]
            rows.append({"dep": dep, "id": "D" + dep, "name": g.loc[dep, "dep_name"], "base": b, "scn": s_})
        series, series_meta = self.series(scn, masks, deps, years)
        pyramide = self.pyramide(scn, masks, deps, years)
        hist = sorted(self.obs[self.obs.index.get_level_values(0).isin(deps)].groupby(level=1).sum().items())
        return {"prof": self.prof, "label": PROFS[self.prof], "origin": self.o, "decision": max(self.o, DECISION),
                "lag": LAG[self.prof], "first_effect": max(self.o, DECISION) + LAG[self.prof] + 1,
                "years": years, "base": base, "scn": sc, "obs": [[int(y), float(n)] for y, n in hist],
                "flows": flows, "series": series, "series_meta": series_meta, "pyramide": pyramide, "k": self.k, "modele": self.modele, "matrix": {"years": my, "rows": rows},
                "regul_deps": zones().get(self.prof, []), "ms": round(ms, 1),
                # contexte : habitants (scénario Omphale choisi) et densité pour 100 000 ; activité appliquée au scénario seul
                "pop": (pop := pop_series(lv["pop_scen"], deps, years)), "pop_scen": lv["pop_scen"], "activite": lv["activite"],
                "dens_base": [b / p * 1e5 if p else None for b, p in zip(base, pop)],
                "dens_scn": [s_ * lv["activite"] / p * 1e5 if p else None for s_, p in zip(sc, pop)]}

    def series(self, scn, masks, deps, years):
        """Séries annuelles de la carte, même territoire et mêmes années que base / scn : âge moyen, part des 60 ans et plus,
        entrées et sorties du stock libéral. Tout vient de l'état N[cellule, tranche d'âge] et du registre du jumeau."""
        o, ages = self.o, self.est.state.ages
        mid = np.array([(a + (ages[i + 1] if i + 1 < len(ages) else a + 10)) / 2 - 0.5 for i, a in enumerate(ages)])
        mid[0] = (ages[1] - 1 + 20) / 2           # première tranche « moins de 25 ans » : entrée en exercice supposée à 20 ans
        old = ages >= 60
        st0 = self.est.state
        m0 = ((st0.cells.sector == "prive") & st0.cells.territory.isin(deps)).to_numpy()
        out = {k: {"base": [], "scn": []} for k in ("age_moyen", "part_60p", "entrees", "sorties")}
        for key, tr in (("base", self.base), ("scn", scn)):
            mk = masks[id(tr)]
            flow_in, flow_out = np.zeros(len(years)), np.zeros(len(years))
            for y, f, _, v in tr.ledger:
                if f in ("vieillissement", "plancher"):
                    continue
                v = np.asarray(v)
                if v.ndim != 1 or len(v) != len(mk):
                    continue
                v = v[mk]
                flow_in[y - o] += v[v > 0].sum()
                flow_out[y - o] -= v[v < 0].sum()
            for i, y in enumerate(years):
                x = (st0.N[m0] if y == o else tr.states[y].N[mk]).sum(axis=0)
                n = x.sum()
                out["age_moyen"][key].append(round(float(x @ mid / n), 2) if n > 0 else None)
                out["part_60p"][key].append(round(float(x[old].sum() / n), 4) if n > 0 else None)
                out["entrees"][key].append(None if y == o else round(float(flow_in[i]), 1))
                out["sorties"][key].append(None if y == o else round(float(flow_out[i]), 1))
        # observé : même définition (privé, territoire), tranches d'âge du RPPS
        t = self.t[(self.t.sector == "prive") & self.t.dep.isin(deps)] if "dep" in self.t else None
        if t is not None and len(t):
            w = t.assign(a=t.age_lo.map(dict(zip(ages, mid)))).groupby("year").apply(
                lambda g: pd.Series({"age": (g.a * g.n).sum() / g.n.sum(), "p60": g.n[g.age_lo >= 60].sum() / g.n.sum()}),
                include_groups=False)
            out["age_moyen"]["obs"] = [[int(y), round(float(r.age), 2)] for y, r in w.iterrows()]
            out["part_60p"]["obs"] = [[int(y), round(float(r.p60), 4)] for y, r in w.iterrows()]
        src = "RPPS 2012–2026 (DREES / ANS), jumeau v2 : "
        meta = {"age_moyen": {"label": "Âge moyen", "unit": "ans",
                              "source": src + "centres des tranches d'âge de 5 ans (moins de 25 ans : 20–24 ; 65 ans et plus : 65–74, centre 69,5), approché"},
                "part_60p": {"label": "Part des 60 ans et plus", "unit": "%", "facteur": 100,
                             "source": src + "tranches 60–64 et 65 ans et plus, valeurs en fraction (0–1)"},
                "entrees": {"label": "Entrées dans l'effectif libéral", "unit": "professionnels / an",
                            "source": src + "formés en France, diplômés étrangers et autres entrées nettes du registre des flux (hors vieillissement)"},
                "sorties": {"label": "Sorties de l'effectif libéral", "unit": "professionnels / an",
                            "source": src + "cessations, retraites et autres sorties nettes du registre des flux (hors vieillissement)"}}
        self.diplomes(scn, masks, years, out, meta, deps)
        return out, meta

    def _diplomes_ref(self):
        """Diplômés annuels de référence, France entière (niveau, source, observé [[année, n]]). Le vivier du jumeau est relatif
        (stationnaire) : seul le niveau observé donne des professionnels / an. None si aucune série n'existe."""
        if getattr(self, "_dref", None) is not None:
            return self._dref
        ref = (None, None, [])
        try:
            from jumeau.vivier import LIGNES, ecoles
            if self.prof in LIGNES:
                e = ecoles()[lambda x: x.profession == self.prof].dropna(subset=["diplomes"])
                obs = [[int(y), float(n)] for y, n in zip(e.year, e.diplomes)]
                last = [n for y, n in obs if y > obs[-1][0] - 3]
                ref = (float(np.mean(last)), "DREES, enquête Écoles, jeu 491 (séries longues 1966-2025), diplômés : moyenne %d–%d"
                       % (obs[-1][0] - 2, obs[-1][0]), obs)
        except Exception:
            pass          # fichier brut absent (data/raw n'est pas versionné) : repli sur les valeurs citées dans les fiches
        if ref[0] is None and self.prof in DIPLOMES_FICHES:
            obs = DIPLOMES_FICHES[self.prof]
            ref = (float(np.mean([n for _, n in obs[-3:]])),
                   "DREES, enquête Écoles, jeu 491, diplômés %d, %d et %d (valeurs de la fiche param-ide-rendement-diplomes), moyenne"
                   % tuple(y for y, _ in obs[-3:]), [[y, float(n)] for y, n in obs])
        self._dref = ref
        return ref

    def diplomes(self, scn, masks, years, out, meta, deps):
        """diplomes, installes_diplomes, taux_installation. Les diplômés n'existent qu'à l'échelle France (vivier national du jumeau) :
        les trois séries sont France entière pour 'diplomes' et le taux ; 'installes_diplomes' suit le territoire."""
        o, st0 = self.o, self.est.state
        d0, dsrc, dobs = self._diplomes_ref()
        from jumeau.modules.etrangers import Etrangers, part_etrangere
        if not hasattr(self, "_share"):
            sh = part_etrangere(self.est.hist, st0, Etrangers.param("flux").value)
            self._share = dict(zip(st0.cells.profession, sh))
        share = self._share
        n = len(years)
        res = {}
        for key, tr in (("base", self.base), ("scn", scn)):
            cells = tr.states[H].cells
            mk = masks[id(tr)]
            fr = ((cells.sector == "prive")).to_numpy()
            sh = cells.profession.map(share).fillna(0.0).to_numpy()
            ins_t, ins_f = np.zeros(n), np.zeros(n)
            e_nat = np.zeros(n)
            g = np.ones(n)
            gg, g0 = {}, {}
            for y, f, a, v in tr.ledger:
                if f == "formation" and a in ("diplomes", "diplomes_reference"):
                    (gg if a == "diplomes" else g0)[y] = float(np.asarray(v).sum())
                    continue
                if (f, a) not in (("entrees", "entrees"), ("lien_formation", "diplomes_france")):
                    continue
                v = np.asarray(v)
                if v.ndim != 1 or len(v) != len(mk):
                    continue
                w = np.clip(v, 0, None) * (1 - sh) if f == "entrees" else v
                ins_t[y - o] += w[mk].sum()
                ins_f[y - o] += w[fr].sum()
                if f == "entrees":
                    e_nat[y - o] += np.clip(v, 0, None)[fr].sum()
            for y in gg:
                if g0.get(y):
                    g[y - o] = gg[y] / g0[y]
            res[key] = (ins_t, ins_f, e_nat, g)
        q = np.where(res["base"][2] > 0, res["scn"][2] / np.where(res["base"][2] > 0, res["base"][2], 1), 1.0)
        dip = {"base": d0 * np.ones(n) if d0 else None, "scn": d0 * q * res["scn"][3] if d0 else None}
        national = len(deps) >= len(set(st0.cells.territory))
        for key in ("base", "scn"):
            d = dip[key]
            ins_t, ins_f = res[key][0], res[key][1]
            ok = d is not None
            out.setdefault("diplomes", {})[key] = [None if (y == o or not ok) else round(float(d[i]), 1) for i, y in enumerate(years)]
            out.setdefault("installes_diplomes", {})[key] = [None if y == o else round(float(ins_t[i]), 1) for i, y in enumerate(years)]
            out.setdefault("taux_installation", {})[key] = [None if (y == o or not ok or d[i] <= 0) else round(float(ins_f[i] / d[i]), 4)
                                                            for i, y in enumerate(years)]
        if dobs and national:
            out["diplomes"]["obs"] = dobs
        sc = {"base": "tendanciel", "scn": "scénario"}
        meta["diplomes"] = {"label": "Diplômés par an", "unit": "professionnels / an",
                            "source": (dsrc or "aucune série de diplômés pour cette profession")
                            + " ; niveau tenu constant (vivier relatif du jumeau), × effet des quotas sur les entrées et du levier de capacité",
                            "note": "France entière : le vivier de formation du jumeau est national, les diplômés ne sont pas répartis par territoire."}
        meta["installes_diplomes"] = {"label": "Diplômés s'installant en libéral", "unit": "professionnels / an",
                                      "source": "jumeau v2 : part formée en France (1 − part des diplômés à l'étranger, fiche param-diplomes-etrangers-flux) "
                                                "des entrées positives du registre des flux, secteur privé du territoire",
                                      "note": "Approché : les entrées du RPPS mêlent premières installations, retours et arrivées d'autres secteurs ou territoires, "
                                              "non séparés dans les données ; le taux peut donc dépasser 100 %."}
        meta["taux_installation"] = {"label": "Taux d'installation des diplômés", "unit": "%", "facteur": 100,
                                     "source": "installés / diplômés, France entière, secteur privé : rapport de deux séries, paramètre du jumeau "
                                               "et non une observation (part étrangère fixe, entrées ajustées sur la fenêtre RPPS)",
                                     "note": ("taux de la France entière" if not national else "France entière")
                                             + " : les diplômés ne sont connus qu'à cette échelle ; les quotas multiplient installés et diplômés "
                                               "dans la même proportion, le taux ne bouge pas"}

    def pyramide(self, scn, masks, deps, years):
        """Pyramide des âges du stock libéral : effectif par tranche d'âge et par année (mêmes territoire, années et définition
        que base / scn) ; observé = dernière année du RPPS, secteur privé."""
        o, ages, st0 = self.o, self.est.state.ages, self.est.state
        m0 = ((st0.cells.sector == "prive") & st0.cells.territory.isin(deps)).to_numpy()
        lab = ["<%d" % ages[1]] + ["%d–%d" % (a, ages[i + 2] - 1) for i, a in enumerate(ages[1:-1])] + ["%d+" % ages[-1]]
        res = {"tranches": lab}
        for key, tr in (("base", self.base), ("scn", scn)):
            mk = masks[id(tr)]
            res[key] = [[round(float(x), 1) for x in (st0.N[m0] if y == o else tr.states[y].N[mk]).sum(axis=0)] for y in years]
        res["obs"] = {str(o): [round(float(x), 1) for x in st0.N[m0].sum(axis=0)]}
        res["source"] = "RPPS 2012–2026 (DREES / ANS), secteur privé, jumeau v2 : effectif par tranche d'âge de l'état N[cellule, tranche]"
        return res

    def obs_total(self, deps, y) -> float:
        o = self.obs
        return float(o[o.index.get_level_values(0).isin(deps) & (o.index.get_level_values(1) == y)].sum())


MODELS: dict = {}


def model(prof):
    if prof not in MODELS:
        MODELS[prof] = Model(prof)
    return MODELS[prof]


def territories():
    g = geo()
    regs = sorted({r for r in g.region}, key=lambda r: REGIONS.get(r, r))
    return [{"id": "FR", "name": "France", "level": "national"}] + [
        {"id": "R" + r, "name": REGIONS.get(r, r), "level": "région",
         "deps": [{"id": "D" + d, "name": g.loc[d, "dep_name"]} for d in g.index[g.region == r]]}
        for r in regs if r in REGIONS]


def parse_levers(q: dict):
    """Leviers d'une requête (clé -> chaîne) : (dict validé, None) ou (None, message d'erreur)."""
    lv = {}
    for k, l in UI.items():
        raw = q.get(k, l["default"])
        if l["type"] == "select":
            if raw not in l["options"]:
                return None, f"{k} : valeur inconnue {raw!r}"
            lv[k] = raw
        elif l["type"] == "toggle":
            lv[k] = str(raw) in ("1", "true")
        else:
            try:
                v = float(raw)
            except ValueError:
                return None, f"{k} : valeur non numérique"
            if not l["min"] <= v <= l["max"]:
                return None, f"{l['label']} hors bornes [{l['min']} ; {l['max']}] : {v}"
            lv[k] = v
    return lv, None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/api/meta":
                return self.send_json({"professions": PROFS, "missing": MISSING, "territories": territories(), "version": VERSION,
                                       "levers": lever_meta(), "familles": FAMILLES})
            if u.path == "/api/scenario":
                prof = q.get("prof", "kines")
                if prof not in PROFS:
                    return self.send_json({"error": f"profession inconnue {prof!r}"}, 400)
                lv, err = parse_levers(q)
                if err:
                    return self.send_json({"error": err}, 400)
                return self.send_json(model(prof).answer(lv, q.get("terr", "FR")))
        except Exception as e:  # le prototype montre l'erreur plutôt que de planter
            return self.send_json({"error": f"{type(e).__name__}: {e}"}, 500)
        return super().do_GET()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    t0 = time.perf_counter()
    for p in PROFS:
        model(p)
        print(f"{p}: origine {MODELS[p].o}, pente d'erreur {MODELS[p].k:.4f}/an ({time.perf_counter() - t0:.1f} s)", flush=True)
    print(f"prêt : http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
