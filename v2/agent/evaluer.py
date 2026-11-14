"""Mesure l'agent sur le jeu écrit avant le code (questions.yaml) : ancrage, lexique, « pas dans le modèle », flux,
latence, coût. Écrit score.txt (résumé) et reponses.jsonl (réponses complètes, pour relecture).

Run (racine du dépôt, serveur de la carte lancé, ANTHROPIC_API_KEY définie) :
    uv run python v2/agent/evaluer.py            # tout le jeu
    uv run python v2/agent/evaluer.py q01 q06    # quelques questions
Coût dérivé : ~0,15 $ par question avec claude-opus-5-5, à mesurer (score.txt donne le coût mesuré).
"""
import json
import statistics
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agent  # noqa: E402

FLUX = ("entrée", "sortie", "installation", "départ", "cessation", "diplômé", "flux")


def main(ids):
    qs = yaml.safe_load((HERE / "questions.yaml").read_text())["questions"]
    qs = [q for q in qs if not ids or q["id"] in ids]
    ok, msg = agent.disponible()
    if not ok:
        sys.exit(msg)
    rows = []
    with open(HERE / "reponses.jsonl", "w") as f:
        for i, q in enumerate(qs, 1):
            r = agent.repondre(q["q"], q.get("contexte"))
            if "erreur" in r:
                print(f"{i}/{len(qs)} {q['id']} ERREUR {r['erreur']}", flush=True)
                rows.append({"id": q["id"], "erreur": r["erreur"]})
                continue
            t = r["reponse"].lower()
            chk = {"ancrage": r["ancrage"]["ok"], "lexique": r["lexique"]["ok"]}
            if q.get("hors_modele"):
                chk["hors_modele"] = "pas dans le modèle" in t
            if q.get("flux"):
                chk["flux"] = any(w in t for w in FLUX)
            row = {"id": q["id"], "q": q["q"], **chk, "nombres": r["ancrage"]["nombres"],
                   "non_ancres": r["ancrage"]["non_ancres"], "termes": r["lexique"]["termes"],
                   "outils": [a["outil"] for a in r["appels"]], "secondes": r["secondes"], "cout_usd": r["cout_usd"],
                   "reponse": r["reponse"]}
            rows.append(row)
            f.write(json.dumps({**row, "appels": r["appels"]}, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{i}/{len(qs)} {q['id']} " + " ".join(f"{k}={'ok' if v else 'NON'}" for k, v in chk.items())
                  + f" {r['secondes']} s {r['cout_usd']} $", flush=True)
    ok_rows = [r for r in rows if "erreur" not in r]
    n = len(ok_rows)
    taux = lambda k: (sum(r[k] for r in ok_rows if k in r), sum(1 for r in ok_rows if k in r))
    nb = sum(r["nombres"] for r in ok_rows)
    nn = sum(len(r["non_ancres"]) for r in ok_rows)
    lines = [f"Évaluation de l'agent — {time.strftime('%Y-%m-%d %H:%M')} — modèle {agent.MODELE}, effort {agent.EFFORT}",
             f"questions : {len(rows)} (erreurs : {len(rows) - n})"]
    for k, lab in (("ancrage", "réponses entièrement ancrées"), ("lexique", "réponses sans terme de jugement"),
                   ("hors_modele", "« pas dans le modèle » quand attendu"), ("flux", "flux nommés quand attendu")):
        a, b = taux(k)
        lines.append(f"{lab} : {a}/{b}" + (f" ({100 * a / b:.0f} %)" if b else ""))
    lines.append(f"nombres ancrés : {nb - nn}/{nb}" + (f" ({100 * (nb - nn) / nb:.1f} %)" if nb else ""))
    if n:
        s = sorted(r["secondes"] for r in ok_rows)
        lines.append(f"latence : médiane {statistics.median(s):.1f} s, max {s[-1]:.1f} s")
        lines.append(f"coût : {sum(r['cout_usd'] for r in ok_rows):.2f} $ au total, "
                     f"{statistics.mean(r['cout_usd'] for r in ok_rows):.3f} $ par question")
    for r in ok_rows:
        bad = [k for k in ("ancrage", "lexique", "hors_modele", "flux") if k in r and not r[k]]
        if bad:
            lines.append(f"  {r['id']} : {', '.join(bad)} {r['non_ancres'] or ''} {r['termes'] or ''}".rstrip())
    out = "\n".join(lines)
    if not ids:
        (HERE / "score.txt").write_text(out + "\n")
    print("\n" + out)


if __name__ == "__main__":
    main(sys.argv[1:])
