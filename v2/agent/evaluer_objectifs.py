"""Mesure l'assistant sur les questions d'objectif et de politique hors modèle (questions.yaml, écrites avant `planifier`).

Contrôles automatiques, en plus de l'ancrage strict, du vocabulaire et du lexique (evaluer_chatbot.py) :
  objectif     : la réponse commence par l'objectif compris (« Objectif ») et l'outil planifier a été appelé ;
  deja_atteint : la réponse dit « déjà atteint » ;
  impossible   : la réponse dit que la cible est hors d'atteinte ;
  melanges     : chaque mélange renvoyé par planifier, rejoué sur la passerelle, atteint la cible ;
  traduction   : « traduction supposée », ou « pas dans le modèle » / « hors du périmètre ».
Écrit score_objectifs.txt et reponses_objectifs.jsonl.  Run : uv run python v2/agent/evaluer_objectifs.py
"""
import json
import re
import statistics
import sys
import time
import uuid
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluer_chatbot as E  # noqa: E402
import garde_fous  # noqa: E402

IMPOSSIBLE = re.compile(r"hors d'atteinte|pas atteignable|n'est pas atteinte?|inatteignable|impossible|n'atteint pas la cible", re.I)


def main():
    Y = yaml.safe_load((HERE / "questions.yaml").read_text())
    qs = Y["objectifs"] + Y["hors_modele"]
    rows = []
    with open(HERE / "reponses_objectifs.jsonl", "w") as f:
        for i, q in enumerate(qs, 1):
            d = E.post(E.CARTE + "/api/agent", {"question": q["q"], "session": "evalo-" + uuid.uuid4().hex[:8]})
            if "error" in d:
                print(f"{i}/{len(qs)} {q['id']} ERREUR {d['error']}", flush=True)
                rows.append({"id": q["id"], "erreur": d["error"]})
                continue
            txt, tl = d["reponse"], d["reponse"].lower()
            sorties = [E.rejouer(a) for a in d["appels"]] + [E.rejouer({"outil": "perimetre"}), "pour 100 000 habitants"]
            anc = garde_fous.ancrage(txt, sorties, q["q"], None)
            nq, badq = E.qualifs(txt, sorties)
            outils = [a["outil"] for a in d["appels"]]
            chk = {"ancrage": anc["ok"], "qualificatifs": not badq, "lexique": d["lexique"]["ok"]}
            if q.get("objectif"):
                chk["objectif_annonce"] = txt.lstrip("*# ").lower().startswith("objectif")
                chk["planifier"] = "planifier" in outils
                plans = [s for a, s in zip(d["appels"], sorties) if a["outil"] == "planifier" and isinstance(s, dict) and "cible" in s]
                ms = [(m, s["cible"]) for s in plans for m in s.get("melanges", [])]
                chk["melanges_atteignent"] = all(m["valeur_obtenue"] >= c for m, c in ms) if ms else None
                if q.get("deja_atteint"):
                    chk["deja_atteint"] = "déjà atteint" in tl
                if q.get("impossible"):
                    chk["impossible"] = bool(IMPOSSIBLE.search(txt))
            if q.get("traduction"):
                chk["traduction"] = any(w in tl for w in ("traduction supposée", "pas dans le modèle", "hors du périmètre"))
            chk = {k: v for k, v in chk.items() if v is not None}
            row = {"id": q["id"], "q": q["q"], **chk, "nb_melanges": len(ms) if q.get("objectif") else None,
                   "non_ancres": anc["non_ancres"], "qualifs_non_conformes": badq, "termes": d["lexique"]["termes"],
                   "outils": outils, "secondes": d["secondes"], "statut_chatbot": d["verification"]["statut"], "reponse": txt}
            rows.append(row)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{i}/{len(qs)} {q['id']} " + " ".join(f"{k}={'ok' if v else 'NON'}" for k, v in chk.items())
                  + f" {d['secondes']} s", flush=True)
    ok = [r for r in rows if "erreur" not in r]
    lines = [f"Objectifs et politiques hors modèle — {time.strftime('%Y-%m-%d %H:%M')} — {len(rows)} questions (erreurs : {len(rows) - len(ok)})"]
    for k in ("objectif_annonce", "planifier", "melanges_atteignent", "deja_atteint", "impossible", "traduction",
              "ancrage", "qualificatifs", "lexique"):
        a, b = sum(r[k] for r in ok if k in r), sum(1 for r in ok if k in r)
        if b:
            lines.append(f"{k} : {a}/{b}")
    lines.append(f"mélanges proposés au total : {sum(r['nb_melanges'] or 0 for r in ok)}")
    if ok:
        s = sorted(r["secondes"] for r in ok)
        lines.append(f"latence : médiane {statistics.median(s):.1f} s, max {s[-1]:.1f} s")
    for r in ok:
        bad = [k for k, v in r.items() if isinstance(v, bool) and not v]
        if bad:
            lines.append(f"  {r['id']} : {', '.join(bad)} {r['non_ancres'] or ''} {r['qualifs_non_conformes'] or ''} {r['termes'] or ''}".rstrip())
    out = "\n".join(lines)
    (HERE / "score_objectifs.txt").write_text(out + "\n")
    print("\n" + out)


if __name__ == "__main__":
    main()
