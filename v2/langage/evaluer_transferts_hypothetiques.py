"""Score du compilateur sur cas_test_transferts_hypothetiques.yaml (10 phrases écrites avant le code, non ajustées).

Run (racine du dépôt) : uv run python v2/langage/evaluer_transferts_hypothetiques.py
Correspondance = transfert hypothétique (source, cible, mode, p, t0 si attendu) + profession + territoire + drapeau O2.
"""
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from compilateur import compile  # noqa: E402

ok = 0
cas = yaml.safe_load((HERE / "cas_test_transferts_hypothetiques.yaml").read_text(encoding="utf-8"))["cas"]
for c in cas:
    r, a = compile(c["texte"]), c["attendu"]
    h = (r["transferts_hypothetiques"] or [None])[0]
    exp = a["hypothetique"]
    got = None if h is None else {k: h[k] for k in ("source", "cible", "mode", "p")} | ({"t0": h["t0"]} if "t0" in (exp or {}) else {})
    good = (got == exp and r["profession"] == a["profession"] and r["territoire"] == a["territoire"]
            and r["o2_cible"] == a.get("o2_cible", False))
    ok += good
    if not good:
        print("ÉCHEC", c["id"], got, exp, r["profession"], r["territoire"], r["o2_cible"], r["non_compris"])
print(f"{ok}/{len(cas)}")
sys.exit(0 if ok == len(cas) else 1)
