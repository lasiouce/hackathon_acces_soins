"""Écran de décision V2 (carte plein écran) : sert index.html, /geo et /api/* du prototype V1.

Run (racine du dépôt) : uv run python v2/prototype-carte/server.py [port]   -> http://localhost:8767

Réutilise v2/prototype/server.py (Model, leviers par famille, parse_levers : mêmes bornes que /api/scenario).
Ajouts : /geo (contours départementaux, coordonnées arrondies à 1e-3°, gzip) et /api/carte
(une valeur 2026 / 2050 par département, tendanciel et scénario, en un seul appel), /api/interpret
(phrase d'un·e élu·e -> réglage des leviers, par le compilateur déterministe de v2/langage),
/api/agent (POST : question -> relais vers le chatbot de chatbot/, port 8768, qui explique les sorties sans calculer ;
la clé ANTHROPIC_API_KEY reste dans son processus) et /api/agent/etat.
"""
import gzip
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("proto_v1", HERE.parent / "prototype" / "server.py")
V1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V1)   # fait le chdir vers la racine et charge le jumeau

# Compilateur langage naturel (v2/langage) : il réutilise le module V1 déjà chargé, pas de second jumeau
spec = importlib.util.spec_from_file_location("compilateur", HERE.parent / "langage" / "compilateur.py")
NL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(NL)
NL.serveur = lambda: V1

GEO = HERE / "assets" / "departements-avec-outre-mer.geojson"


def _round(c):
    return [_round(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]


_GEO: bytes = b""
# DROM en encarts près de la métropole (comme les cartes Insee) : centre cible (lon, lat) et facteur d'échelle.
# Positions schématiques, pas géographiques ; le survol et la fiche donnent le vrai nom.
ENCARTS = {"971": (-6.9, 48.1, 0.9), "972": (-6.9, 47.1, 1.4), "973": (-6.9, 45.9, 0.3),
           "974": (-6.9, 44.7, 1.0), "976": (-6.9, 43.7, 1.6)}


def _encart(f):
    code = f["properties"]["code"]
    if code not in ENCARTS:
        return
    tx, ty, k = ENCARTS[code]
    pts = []
    def walk(c):
        if isinstance(c[0], list):
            for x in c:
                walk(x)
        else:
            pts.append(c)
    walk(f["geometry"]["coordinates"])
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    for p in pts:
        p[0], p[1] = tx + (p[0] - cx) * k, ty + (p[1] - cy) * k


def geo_bytes() -> bytes:
    global _GEO
    if not _GEO:
        g = json.loads(GEO.read_text())
        for f in g["features"]:
            _encart(f)
            f["geometry"]["coordinates"] = _round(f["geometry"]["coordinates"])
        _GEO = gzip.compress(json.dumps(g, separators=(",", ":")).encode(), 6)
    return _GEO


_REG: bytes = b""


def regions_bytes() -> bytes:
    """Limites régionales sans géométrie externe : arêtes des départements dont les deux côtés sont
    dans deux régions différentes (les côtes se lisent sur le fond). Coordonnées arrondies : les arêtes communes coïncident."""
    global _REG
    if not _REG:
        g = json.loads(gzip.decompress(geo_bytes()))
        reg = V1.geo().region.to_dict()
        seen: dict = {}
        n: dict = {}
        for f in g["features"]:
            r = reg.get(f["properties"]["code"], f["properties"]["code"])
            polys = f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]
            for poly in polys:
                for ring in poly:
                    for a, b in zip(ring, ring[1:]):
                        if a != b:
                            k = tuple(sorted((tuple(a), tuple(b))))
                            seen.setdefault(k, set()).add(r)
                            n[k] = n.get(k, 0) + 1
        lines = [list(map(list, k)) for k, rs in seen.items() if len(rs) > 1]
        cote = [list(map(list, k)) for k in seen if n[k] == 1]   # arête d'un seul département : côte ou frontière
        out = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {},
               "geometry": {"type": "MultiLineString", "coordinates": lines}},
               {"type": "Feature", "properties": {"cote": 1}, "geometry": {"type": "MultiLineString", "coordinates": cote}}]}
        _REG = gzip.compress(json.dumps(out, separators=(",", ":")).encode(), 6)
    return _REG


def carte(prof: str, lv: dict, terr: str = "FR") -> dict:
    """Effectif libéral par département : observé à l'origine, tendanciel et scénario en 2026 et 2050."""
    m = V1.model(prof)
    t0 = time.perf_counter()
    scn = m.est.trajectory(V1.H, m.scenario(lv, terr))
    codes = np.unique(m.cells.territory.to_numpy()[(m.cells.sector == "prive").to_numpy()])

    def agg(tr, y):
        # cellules propres à chaque trajectoire : la régulation ajoute un secteur « bloques » au scénario
        st = tr.states[y]
        pr = (st.cells.sector == "prive").to_numpy()
        tot = pd.Series(np.asarray(st.N)[pr].reshape(int(pr.sum()), -1).sum(1), index=st.cells.territory.to_numpy()[pr])
        return tot.groupby(level=0).sum().reindex(codes).fillna(0).to_numpy()
    obs = m.obs.xs(m.o, level=1).reindex(codes).fillna(0).to_numpy()
    y26 = max(V1.DECISION, m.o)   # 2026 = origine actuelle : valeur observée
    b26, s26 = (obs, obs) if y26 <= m.o else (agg(m.base, y26), agg(scn, y26))
    b50, s50 = agg(m.base, V1.H), agg(scn, V1.H)
    P = V1.population().loc[lv["pop_scen"]]          # habitants, Insee Omphale 2022, scénario choisi
    pp = lambda d, y: float(P.loc[y, d]) if d in P.columns else 0.0
    # séries annuelles y26..H pour le curseur d'année (le moteur garde déjà chaque année)
    years = list(range(y26, V1.H + 1))
    B = np.column_stack([b26 if y == y26 else agg(m.base, y) for y in years])
    S_ = np.column_stack([s26 if y == y26 else agg(scn, y) for y in years])
    r = lambda v: round(float(v), 1)
    out = {d: {"o": float(obs[i]), "b26": float(b26[i]), "s26": float(s26[i]), "b50": float(b50[i]), "s50": float(s50[i]),
               "p26": pp(d, y26), "p50": pp(d, V1.H),
               "b": [r(v) for v in B[i]], "s": [r(v) for v in S_[i]], "p": [round(pp(d, y)) for y in years]}
           for i, d in enumerate(codes)}
    return {"prof": prof, "origin": m.o, "y26": y26, "years": years, "k": m.k, "deps": out, "activite": lv["activite"], "pop_scen": lv["pop_scen"],
            "regul_deps": V1.zones().get(prof, []), "ms": round((time.perf_counter() - t0) * 1000, 1)}


class Handler(V1.Handler):
    def __init__(self, *a, **k):
        super(V1.Handler, self).__init__(*a, directory=str(HERE), **k)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/geo", "/geo-regions"):
            b = geo_bytes() if u.path == "/geo" else regions_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/geo+json")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            return self.wfile.write(b)
        if u.path == "/api/carte":
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            prof = q.get("prof", "kines")
            if prof not in V1.PROFS:
                return self.send_json({"error": f"profession inconnue {prof!r}"}, 400)
            lv, err = V1.parse_levers(q)          # mêmes leviers, mêmes bornes que /api/scenario
            if err:
                return self.send_json({"error": err}, 400)
            try:
                return self.send_json(carte(prof, lv, q.get("terr", "FR")))
            except Exception as e:
                return self.send_json({"error": f"{type(e).__name__}: {e}"}, 500)
        if u.path == "/api/interpret":     # texte -> leviers ; traduit, ne calcule rien (v2/langage/README.md)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            texte = q.get("q", "").strip()[:500]
            if not texte:
                return self.send_json({"error": "texte vide"}, 400)
            try:
                return self.send_json(NL.compile(texte, q.get("prof"), q.get("terr")))
            except Exception as e:
                return self.send_json({"error": f"{type(e).__name__}: {e}"}, 500)
        if u.path == "/api/agent/etat":
            code, j = _chatbot("GET", "/api/etat")
            if code != 200:
                return self.send_json({"disponible": False, "message": "Assistant non lancé (chatbot/, port 8768) : "
                                       "la carte reste utilisable. Voir le README, « Chatbot »."})
            mode = "IA (" + j.get("modele", "?") + ")" if j.get("mode") == "llm" else "sans IA (glossaire de l'équipe)"
            return self.send_json({"disponible": True, "mode": j.get("mode"), "message": f"Assistant prêt, mode {mode}.",
                                   "modele": MODELE})
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/agent":
            return self.send_json({"error": "inconnu"}, 404)
        n = int(self.headers.get("Content-Length") or 0)
        if not 0 < n <= 65536:
            return self.send_json({"error": "requête vide ou trop longue"}, 400)
        try:
            body = json.loads(self.rfile.read(n))
            q = str(body.get("question", "")).strip()[:1000]
        except (ValueError, AttributeError):
            return self.send_json({"error": "JSON invalide"}, 400)
        if not q:
            return self.send_json({"error": "question vide"}, 400)
        ctx = body.get("contexte") or {}
        sid = str(body.get("session") or "carte")[:64]
        msg = q
        if ctx.get("prof"):        # contexte de la carte : rattache « et si… » à ce qui est affiché ; mode IA seulement
            lv = ", ".join(f"{k}={v}" for k, v in (ctx.get("leviers") or {}).items()) or "aucun (tendanciel)"
            msg = (f"{q}\n\n[Contexte de la carte, pas une question : profession {ctx['prof']} ; territoire "
                   f"{ctx.get('territoire') or ctx.get('terr')} ; leviers modifiés : {lv} ; année affichée "
                   f"{ctx.get('annee') or 2050} ; densités exprimées pour 100 000 habitants.]")
        code, j = _chatbot("GET", "/api/etat")
        if code == 200 and j.get("mode") != "llm":
            msg = q                # le glossaire lit la phrase seule ; il garde profession et territoire d'un tour à l'autre
        code, r = _chatbot("POST", "/api/chat", {"session": sid, "message": msg})
        if code != 200 or "erreur" in r:
            return self.send_json({"error": r.get("erreur") or "Chatbot non lancé (port 8768)."}, 503)
        lx = _lexique(r.get("texte", ""))
        return self.send_json({"reponse": r.get("texte", ""), "mode": r.get("mode"), "verification": r.get("verification"),
                               "carte": _scenario_carte(r.get("appels", [])), "objectif": _objectif(r.get("appels", [])),
                               "graphiques": (r.get("graphiques") or [])[:2],   # construits par le chatbot à partir des résultats
                               "lexique": lx, "appels": [{"outil": a["outil"], "resume": a.get("resume"), "entree": a.get("entree")} for a in r.get("appels", [])],
                               "secondes": r.get("duree_s")})


CHATBOT = os.environ.get("CHATBOT_URL", "http://127.0.0.1:8768")

# Modèle servi par la carte (V1.Model : C1 par défaut, A0 par JUMEAU_MODELE=A0) : affiché sous chaque réponse de l'assistant.
# Même texte que MODELE dans chatbot/passerelle/requetes.py (périmètre du chatbot) ; chiffres cités des articles.
MODELES = {
    "C1": {
        "nom": "Modèle bayésien hiérarchique (cohortes, entrées comprises ; C1, axe 2)",
        "equation": "N(t+1) = rétention × vieillissement de N(t) + entrées, par profession × département × sexe × tranche d'âge de 5 ans ; rétention nette en âge-période-cohorte, entrées = niveau national (filtre de Kalman) × parts départementales",
        "estimation": "Bayes empirique, moyenne a posteriori ; fenêtre de 2012 (kinés 2017) à la dernière année ; effets département et région rétrécis ; secteur privé seulement, le salariat public garde les taux de A0",
        "leviers": "événements datés du jumeau (modules entrées, sorties, diplômés étrangers, régulation) appliqués aux taux de C1, au même état de départ ; état à 2 secteurs (libéral = privé, salarié)",
        "precision": "MAPE 7,73 % par département à 5 ans, secteur privé, contre 8,68 % pour le modèle stock-flux multi-échelle (A0) et 9,30 % pour la tendance linéaire (mesuré, article axe 2) ; gain plus faible sur les origines récentes (dentistes, pharmaciens)",
        "fourchette": "± pente de l'erreur nationale de C1 au banc × horizon × 1,6, environ 8 cas sur 10 (même méthode que A0) ; extrapolée au-delà d'environ 10 ans ; la bande probabiliste propre de C1 n'est calibrée qu'au département (77,6 %) et n'est pas publiée au national",
        "approximation": "rétention de C1 tenue à sa moyenne sur l'horizon : écart de −1,1 à +1,2 % sur le total privé national à 5 ans (mesuré) ; infirmiers : C1 mesuré au banc sur les libéraux, la carte sert la table privée de l'axe 4",
        "alternative": "Modèle stock-flux multi-échelle (A0, MAPE 8,68 %) : servi si JUMEAU_MODELE=A0",
        "sources": "v2/papers/axe2-methodes/main.pdf ; v2/methodes/cohortes.py ; v2/methodes/c1_jumeau.py ; v2/jumeau/ ; v2/prototype/server.py (Model)",
    },
    "A0": {
        "nom": "Modèle stock-flux multi-échelle (taux départementaux rétrécis vers le national ; A0, axe 2)",
        "equation": "N(t+1) = rétention × vieillissement de N(t) + entrées, par profession × département × sexe × tranche d'âge de 5 ans",
        "estimation": "rétention nette et entrées ajustées sur les 5 dernières années observées ; taux départementaux rétrécis vers le national (poids 200 personnes, supposé)",
        "leviers": "événements datés du jumeau (modules entrées, sorties, diplômés étrangers, régulation) appliqués au même état de départ ; état à 2 secteurs (libéral = privé, salarié)",
        "precision": "MAPE 8,68 % par département à 5 ans, secteur privé, contre 9,30 % pour la tendance linéaire (mesuré, article axe 2, tableau 1)",
        "fourchette": "± pente de l'erreur de backtest × horizon × 1,6, environ 8 cas sur 10 (facteur cité, non reproduit ; article axe 5) ; extrapolée au-delà d'environ 10 ans",
        "alternative": "Modèle bayésien hiérarchique (C1, MAPE 7,73 % au même banc) : servi par défaut (JUMEAU_MODELE=C1)",
        "sources": "v2/papers/axe2-methodes/main.pdf ; v2/sante/estimators.py (StockFlowLocal) ; v2/jumeau/ ; v2/prototype/server.py (Model)",
    },
}
# Modèle servi : même variable que v2/prototype/server.py (MODELE_CHOIX), C1 par défaut.
MODELE = MODELES[os.environ.get("JUMEAU_MODELE", "C1").upper()]


def _objectif(appels: list) -> dict | None:
    """Question d'objectif : ce que l'assistant a compris (cible, horizon, territoire, référence), lu dans l'appel planifier."""
    for a in reversed(appels):
        e = a.get("entree") or {}
        if a.get("outil") in ("planifier", "atteindre") and not a.get("erreur") and e.get("profession") in V1.PROFS:
            return {"prof": e["profession"], "terr": a.get("code_territoire") or "FR", "annee": e.get("annee"),
                    "grandeur": e.get("grandeur", "effectif"), "hausse_pct": e.get("hausse_pct"),
                    "valeur_cible": e.get("valeur_cible"), "reference": e.get("reference", "tendanciel"),
                    "exclus": e.get("leviers_exclus") or []}
    return None


def _scenario_carte(appels: list) -> dict | None:
    """Scénario simulé par le chatbot, au format de la carte (profession, territoire, leviers, année) : le panneau propose
    de l'afficher, rien n'est appliqué sans clic. Parmi les calculs réussis, on préfère ceux qui ont des leviers, puis
    un territoire plus fin que la France (les appels « France » servent souvent de référence), puis le dernier."""
    cands = []
    for i, a in enumerate(appels):
        e = a.get("entree") or {}
        if a.get("erreur") or a.get("outil") not in ("projeter", "comparer", "balayer", "planifier", "traduire_politique") or not a.get("code_territoire"):
            continue
        lv = dict(e.get("leviers") or {})
        if a["outil"] in ("planifier", "traduire_politique"):      # premier mélange vérifié / essai d'ampleur basse
            lv = dict(a.get("reglage_carte") or {})
        if a["outil"] == "comparer":       # le dernier scénario comparé
            sc = e.get("scenarios") or []
            lv = dict((sc[-1] or {}).get("leviers") or {}) if sc else {}
        if a["outil"] == "balayer":
            lv = dict(e.get("autres_leviers") or {})
        ans = e.get("annees") or ([e["annee"]] if e.get("annee") else [])
        if e.get("profession") not in V1.PROFS:
            continue
        c = {"prof": e["profession"], "terr": a["code_territoire"], "leviers": lv, "annee": max(ans) if ans else 2050}
        cands.append(((bool(lv), c["terr"] != "FR", i), c))
    return max(cands, key=lambda x: x[0])[1] if cands else None


def _chatbot(methode: str, chemin: str, corps: dict | None = None) -> tuple[int, dict]:
    """Relais vers le chatbot de chatbot/ (moteur unique, décision du 2026-11-14) ; la clé reste dans son processus."""
    from urllib.error import HTTPError, URLError
    from urllib.request import Request, urlopen
    data = json.dumps(corps).encode() if corps is not None else None
    req = Request(CHATBOT + chemin, data=data, method=methode, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=120) as r:
            return r.status, json.load(r)
    except HTTPError as e:
        try:
            return e.code, json.load(e)
        except ValueError:
            return e.code, {}
    except (URLError, OSError):
        return 0, {}


_LX = None


def _lexique(texte: str) -> dict:
    """Contrôle du lexique neutre (v2/agent/garde_fous.py) appliqué à la réponse du chatbot."""
    global _LX
    if _LX is None:
        sp = importlib.util.spec_from_file_location("garde_fous", HERE.parent / "agent" / "garde_fous.py")
        _LX = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(_LX)
    return _LX.lexique(texte)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    os.environ.setdefault("AGENT_CARTE_URL", f"http://127.0.0.1:{port}")   # l'agent interroge ce serveur-ci
    t0 = time.perf_counter()
    geo_bytes()
    regions_bytes()
    for p in V1.PROFS:
        V1.model(p)
        print(f"{p}: origine {V1.MODELS[p].o} ({time.perf_counter() - t0:.1f} s)", flush=True)
    print(f"prêt : http://localhost:{port}", flush=True)
    V1.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
