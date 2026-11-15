"""Passerelle en lecture seule vers le jumeau : le seul processus qui charge le code du modèle.

Run : uv run python -m passerelle.server [port]          -> http://127.0.0.1:8770

Surface exposée (rien d'autre) :
    GET /v1/sante                     état, version exacte du modèle (commit, code modifié ou non)
    GET /v1/outils                    liste blanche des requêtes et schémas de leurs arguments
    GET /v1/requete/<nom>?args=<json> une requête de la liste blanche, arguments validés avant tout calcul
Toute autre méthode (POST, PUT, DELETE…) : 405. Aucun fichier servi, aucun chemin accepté en argument,
écoute sur 127.0.0.1 seulement. Les erreurs internes ne renvoient pas de trace d'exécution.
"""
from __future__ import annotations

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from passerelle import requetes as R
from passerelle import schemas as SC

# nom de la requête -> fonction ; noms d'arguments du schéma -> noms Python
FONCTIONS = {"perimetre": R.perimetre, "projeter": R.projeter, "comparer": R.comparer, "balayer": R.balayer,
             "classer": R.classer, "atteindre": R.atteindre, "effets_des_leviers": R.effets_des_leviers, "planifier": R.planifier, "traduire_politique": R.traduire_politique, "couverture": R.couverture, "decrire_leviers": R.decrire_leviers, "incertitude": R.incertitude,
             "interpreter_phrase": R.interpreter}
ARGS = {"profession": "profession_", "territoire": "territoire_", "leviers": "leviers_"}
assert set(FONCTIONS) == set(SC.OUTILS), "liste blanche et fonctions désalignées"
VERSION = None


def executer(nom: str, args: dict) -> dict:
    """Valide puis exécute une requête de la liste blanche. Lève SC.Invalide ou R.ErreurOutil."""
    if nom not in SC.OUTILS:
        raise SC.Invalide(f"requête inconnue {nom!r} ; autorisées : {sorted(SC.OUTILS)}")
    SC.valider(SC.OUTILS[nom][1], args)
    return FONCTIONS[nom](**{ARGS.get(k, k): v for k, v in args.items()})


class Handler(BaseHTTPRequestHandler):
    server_version = "passerelle-jumeau"

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _refus(self):
        self._json({"erreur": "méthode non autorisée : la passerelle est en lecture seule (GET)"}, 405)

    do_POST = do_PUT = do_PATCH = do_DELETE = _refus

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/v1/sante":
            return self._json({"ok": True, "version_modele": VERSION})
        if u.path == "/v1/outils":
            return self._json({"outils": SC.definitions(), "version_modele": VERSION})
        if u.path.startswith("/v1/requete/"):
            nom = unquote(u.path[len("/v1/requete/"):])
            q = parse_qs(u.query)
            try:
                args = json.loads(q.get("args", ["{}"])[0])
            except json.JSONDecodeError:
                return self._json({"erreur": "args : JSON invalide", "type": "invalide"}, 400)
            t0 = time.perf_counter()
            try:
                res = executer(nom, args)
            except SC.Invalide as e:
                return self._json({"erreur": str(e), "type": "invalide"}, 400)
            except R.ErreurOutil as e:
                return self._json({"erreur": str(e), "type": "hors_modele"}, 422)
            except Exception as e:   # pas de trace d'exécution renvoyée
                print(f"erreur interne {nom}: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                return self._json({"erreur": f"erreur interne du modèle ({type(e).__name__})", "type": "interne"}, 500)
            return self._json({"resultat": res, "version_modele": VERSION, "ms": round((time.perf_counter() - t0) * 1000, 1)})
        return self._json({"erreur": "introuvable"}, 404)


def main():
    global VERSION
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
    VERSION = R.version_modele()
    t0 = time.perf_counter()
    for p in R.S().PROFS:
        R.S().model(p)
        print(f"{p} chargé ({time.perf_counter() - t0:.1f} s)", flush=True)
    etat = "⚠ CODE DU MODÈLE MODIFIÉ LOCALEMENT" if VERSION["code_modifie_localement"] else "propre"
    print(f"modèle {VERSION['commit']} ({etat})\npasserelle prête : http://127.0.0.1:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
