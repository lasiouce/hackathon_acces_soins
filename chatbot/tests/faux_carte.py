"""Fausse API de la carte : GET /api/couverture, même forme que v2/prototype-carte/server.py (couverture_carte).

Valeurs fictives, pour les tests seulement. Refuse (400) les professions sans couverture (règle O2).
Run : python tests/faux_carte.py <port>
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ANNEES = list(range(2026, 2051))
O2 = {"medecine-generale", "specialistes"}


def zone(cb, cs, w):
    return {"cb": cb, "cs": cs, "ecart": [s / b - 1 for s, b in zip(cs, cb)], "min": [v * (1 - w) for v in cs],
            "max": [v * (1 + w) for v in cs]}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        p = q.get("prof", "")
        if u.path != "/api/couverture" or p in O2:
            self.send_response(400 if p in O2 else 404)
            self.end_headers()
            return
        l23 = q.get("l23") == "1" and p == "pharmaciens"
        cb = [1 - 0.004 * (y - 2026) for y in ANNEES]
        cs = [b * (1 - (0.02 * min(1, (y - 2026) / 5) if l23 else 0)) for y, b in zip(ANNEES, cb)]
        w = 0.03 if p in ("kines", "infirmiers") else 0.0
        z = zone(cb, cs, w)
        j = {"prof": p, "ref": 2026, "years": ANNEES, "central": "M1", "estimateurs": ["M1", "M2a"] if w else ["M1"],
             "fr": z, "regs": {"R84": z}, "deps": {"63": z, "69": z}, "fourchette_visible": bool(w),
             "l23": {"actif": True, "params": [{"name": "a", "status": "supposé", "source": "x"},
                                               {"name": "s_inf", "status": "mesuré", "source": "y"}],
                     "transferts": [{"transfert": "L23 vaccination en officine", "source": "medecine-generale",
                                     "cible": "pharmaciens", "etp_liberes_source": [120.0] * len(ANNEES),
                                     "actes_mg_liberes": [1500000] * len(ANNEES)}]} if l23 else None}
        b = json.dumps(j).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
