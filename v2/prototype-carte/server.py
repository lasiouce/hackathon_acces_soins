"""Écran de décision V2 (carte plein écran) : sert index.html, /geo et /api/* du prototype V1.

Run (racine du dépôt) : uv run python v2/prototype-carte/server.py [port]   -> http://localhost:8767

Réutilise v2/prototype/server.py (Model, leviers par famille, parse_levers : mêmes bornes que /api/scenario).
Ajouts : /geo (contours départementaux, coordonnées arrondies à 1e-3°, gzip) et /api/carte
(une valeur 2026 / 2050 par département, tendanciel et scénario, en un seul appel), /api/interpret
(phrase d'un·e élu·e -> réglage des leviers, par le compilateur déterministe de v2/langage),
/api/agent (POST : question -> réponse de l'agent de v2/agent, qui explique les sorties sans calculer ; la clé
ANTHROPIC_API_KEY reste côté serveur) et /api/agent/etat.
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
    out = {d: {"o": float(obs[i]), "b26": float(b26[i]), "s26": float(s26[i]), "b50": float(b50[i]), "s50": float(s50[i]),
               "p26": pp(d, y26), "p50": pp(d, V1.H)}
           for i, d in enumerate(codes)}
    return {"prof": prof, "origin": m.o, "y26": y26, "k": m.k, "deps": out, "activite": lv["activite"], "pop_scen": lv["pop_scen"],
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
            ok, msg = _agent().disponible()
            return self.send_json({"disponible": ok, "message": msg})
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
        hist = [{"role": m.get("role"), "texte": str(m.get("texte", ""))[:4000]} for m in body.get("historique", [])[-8:]
                if isinstance(m, dict) and m.get("role") in ("user", "assistant")]
        try:
            r = _agent().repondre(q, body.get("contexte") or None, hist)
        except Exception as e:
            return self.send_json({"error": f"{type(e).__name__}"}, 500)
        if "erreur" in r:
            return self.send_json({"error": r["erreur"]}, 503)
        r["appels"] = [{"outil": a["outil"], "entree": a["entree"]} for a in r["appels"]]   # sorties complètes : côté serveur
        return self.send_json(r)


_AG = None


def _agent():
    """Agent de v2/agent, chargé au premier appel (la carte démarre sans lui, et sans clé)."""
    global _AG
    if _AG is None:
        sp = importlib.util.spec_from_file_location("agent", HERE.parent / "agent" / "agent.py")
        _AG = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(_AG)
    return _AG


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
