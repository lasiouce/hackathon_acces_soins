"""Interface du chatbot : sert index.html et /api/*. N'importe aucun code du modèle (passe par chat/client.py).

Run : uv run python -m chat.server [port]          -> http://localhost:8768   (la passerelle doit tourner)
"""
from __future__ import annotations

import json
import sys
import threading
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from chat import agent as A
from chat import client as C

HERE = Path(__file__).resolve().parent
SESSIONS: dict = {}
VERROUS: dict = {}
MAX_SESSIONS = 200


def session(sid: str):
    if sid not in SESSIONS:
        if len(SESSIONS) >= MAX_SESSIONS:
            vieux = next(iter(SESSIONS))
            SESSIONS.pop(vieux)
            VERROUS.pop(vieux, None)
        SESSIONS[sid] = A.Conversation()
        VERROUS[sid] = threading.Lock()
    return SESSIONS[sid], VERROUS[sid]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/etat"):
            try:
                v = C.sante()["version_modele"]
            except C.PasserelleInjoignable as e:
                return self._json({"mode": "indisponible", "erreur": str(e)})
            return self._json({"mode": "llm" if A.cle_disponible() else "deterministe", "modele": A.MODELE, "version_modele": v})
        if self.path.split("?")[0] in ("/", "/index.html"):
            self.path = "/index.html"
            return super().do_GET()
        return self._json({"erreur": "introuvable"}, 404)   # aucun autre fichier servi

    def do_POST(self):
        try:
            q = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length", 0)), 20000)) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json({"erreur": "JSON invalide"}, 400)
        sid = str(q.get("session") or uuid.uuid4())[:64]
        if self.path == "/api/reset":
            SESSIONS.pop(sid, None)
            return self._json({"ok": True})
        if self.path == "/api/chat":
            msg = str(q.get("message", "")).strip()[:2000]
            if not msg:
                return self._json({"erreur": "message vide"}, 400)
            conv, verrou = session(sid)
            with verrou:
                try:
                    return self._json({**conv.envoyer(msg), "session": sid})
                except C.PasserelleInjoignable as e:
                    return self._json({"erreur": str(e)}, 503)
                except Exception as e:
                    print(f"erreur : {type(e).__name__}: {e}", file=sys.stderr, flush=True)
                    return self._json({"erreur": f"erreur interne ({type(e).__name__})"}, 500)
        return self._json({"erreur": "introuvable"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
    try:
        v = C.sante()["version_modele"]
        print(f"passerelle OK, modèle {v['commit']}" + (" (⚠ code modifié localement)" if v["code_modifie_localement"] else ""))
    except C.PasserelleInjoignable as e:
        print(f"⚠ {e}")
    print(f"mode : {'llm (' + A.MODELE + ')' if A.cle_disponible() else 'déterministe (pas de clé d’API)'}\n"
          f"prêt : http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
