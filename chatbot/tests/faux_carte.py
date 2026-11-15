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
        bad = p in O2 or q.get("tr_cible", "infirmiers") in O2
        if u.path != "/api/couverture" or bad:
            self.send_response(400 if bad else 404)
            self.end_headers()
            return
        tr = "tr_cible" in q and q["tr_cible"] == p
        ta = float(q.get("tr_a", 0.1)) * float(q.get("tr_sinf", 1)) * float(q.get("tr_k", 1))
        l23 = q.get("l23") == "1" and p == "pharmaciens"
        cb = [1 - 0.004 * (y - 2026) for y in ANNEES]
        cs = [b * (1 - (0.02 * min(1, (y - 2026) / 5) if l23 else 0)) / (1 + (0.3 * ta * min(1, (y - 2026) / 5) if tr else 0))
              for y, b in zip(ANNEES, cb)]
        w = 0.03 if p in ("kines", "infirmiers") else 0.0
        z = zone(cb, cs, w)
        j = {"prof": p, "ref": 2026, "years": ANNEES, "central": "M1", "estimateurs": ["M1", "M2a"] if w else ["M1"],
             "fr": z, "regs": {"R84": z}, "deps": {"63": z, "69": z}, "fourchette_visible": bool(w),
             "l23": {"actif": True, "params": [{"name": "a", "status": "supposé", "source": "x"},
                                               {"name": "s_inf", "status": "mesuré", "source": "y"}],
                     "transferts": [{"transfert": "L23 vaccination en officine", "source": "medecine-generale",
                                     "cible": "pharmaciens", "etp_liberes_source": [120.0] * len(ANNEES),
                                     "actes_mg_liberes": [1500000] * len(ANNEES)}]} if l23 else None,
             "transfert_hypothetique": {"actif": True, "statut": "hypothèse de l'utilisateur", "source": q.get("tr_src"),
                                        "cible": q["tr_cible"], "params": [
                                            {"name": k, "value": float(q.get(f"tr_{k}", d)), "unit": "u",
                                             "status": "hypothèse de l'utilisateur" if f"tr_{k}" in q else "supposé (défaut, hypothèse de l'utilisateur)"}
                                            for k, d in (("a", 0.1), ("sinf", 1), ("k", 1), ("tau", 2.4), ("t0", 2026))],
                                        "besoin_source": {"estimateur": "M1", "statut": "niveau supposé"},
                                        "etp_source_transferes": [300.0 * ta] * len(ANNEES),
                                        "note": "transfert proposé par l'utilisateur·rice, pas un levier de la carte"} if tr else None}
        b = json.dumps(j).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
