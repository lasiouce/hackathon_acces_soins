"""Fausse API de la carte : GET /api/couverture selon le contrat du plan besoin-carte (2026-11-15, étape 1).

Forme de besoin.sortie.besoin_api (profession -> [territoire][année]). Valeurs fictives, pour les tests seulement.
Refuse (400) les professions sans couverture (règle O2), comme couverture.aligne.
Run : python tests/faux_carte.py <port>
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ANNEES = list(range(2026, 2051))
O2 = {"medecine-generale", "specialistes"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p, t = q.get("prof", ""), q.get("terr", "FR")
        if u.path != "/api/couverture" or p in O2:
            self.send_response(400 if p in O2 else 404)
            self.end_headers()
            return
        l23, t0 = q.get("l23") == "1", int(q.get("l23_t0", 2026))
        base = [1 - 0.004 * (y - 2026) for y in ANNEES]
        scn = [b * (1 - (0.02 * min(1, (y - t0) / 5) if l23 and y > t0 and p == "pharmaciens" else 0)) for y, b in zip(ANNEES, base)]
        j = {"estimateur": "M1", "ref": 2026, "years": ANNEES, "territories": [t],
             "couverture": {p: [scn]}, "couverture_base": {p: [base]},
             "transferts": [{"transfert": "L23 vaccination en officine", "source": "medecine-generale", "cible": "pharmaciens",
                             "etp_liberes_source": [120.0] * len(ANNEES)}] if l23 else [],
             "hypotheses": {"params": [{"name": "a", "status": "supposé", "source": "x"}, {"name": "s_inf", "status": "mesuré", "source": "y"}]}}
        if p in ("kines", "infirmiers"):
            j["couverture_min"] = {p: [[v * 0.97 for v in scn]]}
            j["couverture_max"] = {p: [[v * 1.03 for v in scn]]}
        b = json.dumps(j).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
