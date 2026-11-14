"""Mesure le chatbot intégré à la carte (relais /api/agent -> chatbot/) sur le jeu écrit avant le code (questions.yaml).

Pour chaque question (nouvelle session, contexte de la carte s'il est donné) :
  - ancrage strict (garde_fous.ancrage) : chaque nombre de la réponse se retrouve, à la précision affichée, dans les
    résultats des requêtes que le chatbot a lancées (rejouées sur la passerelle : le jumeau est déterministe), dans la
    question ou dans le contexte ;
  - vérification du chatbot (chatbot/chat/verif.py, tolérance ±6 %) : ok / corrigee / bloquee ;
  - lexique neutre ; « pas dans le modèle » ou « Hors du périmètre du modèle » quand attendu ; flux nommés quand attendu.
Écrit score_chatbot.txt et reponses_chatbot.jsonl.

Run (carte 8767, passerelle 8770 et chatbot 8768 lancés, voir README « Chatbot ») :
    uv run python v2/agent/evaluer_chatbot.py
"""
import json
import statistics
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import garde_fous  # noqa: E402
import importlib.util  # noqa: E402

_sp = importlib.util.spec_from_file_location("verif_chatbot", HERE.parents[1] / "chatbot" / "chat" / "verif.py")
VQ = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(VQ)          # qualificatifs : vocabulaire de v2/docs/lab/lexicon.md


def qualifs(txt: str, sorties: list) -> tuple[int, list]:
    """(nombre de qualificatifs du vocabulaire dans la réponse, liste des non conformes ou hors vocabulaire)."""
    t, n = txt.lower(), 0
    for mot in VQ._VOCAB:
        n += t.count(mot)
        t = t.replace(mot, " ")
    return n, VQ.qualifs_non_rattaches(txt, VQ.qualificatifs(sorties))

CARTE, PASSERELLE = "http://127.0.0.1:8767", "http://127.0.0.1:8770"
FLUX = ("entrée", "sortie", "installation", "départ", "cessation", "diplômé", "flux")
HORS = ("pas dans le modèle", "hors du périmètre du modèle", "limite du modèle")
NOMS = {"FR": "France"}


def post(url, corps):
    req = Request(url, data=json.dumps(corps).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=180) as r:
        return json.load(r)


def rejouer(appel):
    url = f"{PASSERELLE}/v1/requete/{quote(appel['outil'])}?args={quote(json.dumps(appel.get('entree') or {}, ensure_ascii=False))}"
    try:
        with urlopen(url, timeout=120) as r:
            res = json.load(r)["resultat"]
    except Exception as e:          # requête refusée : son message d'erreur a été vu par le modèle de langage
        return {"erreur": str(e)}
    return {k: v for k, v in res.items() if not k.startswith("_")}


def main():
    qs = yaml.safe_load((HERE / "questions.yaml").read_text())["questions"]
    terr = {t["id"]: t["name"] for t in json.load(urlopen(CARTE + "/api/meta"))["territories"]}
    rows = []
    with open(HERE / "reponses_chatbot.jsonl", "w") as f:
        for i, q in enumerate(qs, 1):
            c = q.get("contexte")
            ctx = {**c, "territoire": terr.get(c.get("terr", "FR"), c.get("terr")), "annee": 2050} if c else None
            t0 = time.perf_counter()
            d = post(CARTE + "/api/agent", {"question": q["q"], "contexte": ctx, "session": "eval-" + uuid.uuid4().hex[:8]})
            if "error" in d:
                print(f"{i}/{len(qs)} {q['id']} ERREUR {d['error']}", flush=True)
                rows.append({"id": q["id"], "erreur": d["error"]})
                continue
            # le périmètre est dans le prompt système du chatbot ; « pour 100 000 habitants » est une unité, pas un résultat
            sorties = [rejouer(a) for a in d["appels"]] + [rejouer({"outil": "perimetre"}), "pour 100 000 habitants"]
            txt = d["reponse"]
            anc = garde_fous.ancrage(txt, sorties, q["q"], ctx)
            nq, badq = qualifs(txt, sorties)
            chk = {"ancrage": anc["ok"], "qualificatifs": not badq, "lexique": d["lexique"]["ok"], "verif_chatbot": d["verification"]["statut"] != "bloquee"}
            if q.get("hors_modele"):
                chk["hors_modele"] = any(h in txt.lower() for h in HORS)
            if q.get("flux"):
                chk["flux"] = any(w in txt.lower() for w in FLUX)
            row = {"id": q["id"], "q": q["q"], "mode": d["mode"], **chk, "statut_chatbot": d["verification"]["statut"],
                   "nombres": anc["nombres"], "non_ancres": anc["non_ancres"], "nb_qualifs": nq, "qualifs_non_conformes": badq,
                   "carte": d.get("carte"), "termes": d["lexique"]["termes"],
                   "outils": [a["outil"] for a in d["appels"]], "appels": d["appels"], "secondes": d["secondes"],
                   "secondes_relais": round(time.perf_counter() - t0, 1), "reponse": txt}
            rows.append(row)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{i}/{len(qs)} {q['id']} " + " ".join(f"{k}={'ok' if v else 'NON'}" for k, v in chk.items())
                  + f" ({row['statut_chatbot']}) {row['secondes']} s", flush=True)
    ok = [r for r in rows if "erreur" not in r]
    taux = lambda k: (sum(r[k] for r in ok if k in r), sum(1 for r in ok if k in r))
    nb, nn = sum(r["nombres"] for r in ok), sum(len(r["non_ancres"]) for r in ok)
    modes = sorted({r["mode"] for r in ok})
    lines = [f"Chatbot intégré (relais carte -> chatbot/) — {time.strftime('%Y-%m-%d %H:%M')} — mode(s) {', '.join(modes)}",
             f"questions : {len(rows)} (erreurs : {len(rows) - len(ok)})"]
    nqt, nqb = sum(r["nb_qualifs"] for r in ok), sum(len(r["qualifs_non_conformes"]) for r in ok)
    for k, lab in (("ancrage", "réponses entièrement ancrées (règle stricte, précision affichée)"),
                   ("qualificatifs", "réponses dont tous les qualificatifs viennent des résultats (vocabulaire imposé)"),
                   ("verif_chatbot", "réponses non bloquées par la vérification du chatbot (±6 %)"),
                   ("lexique", "réponses sans terme de jugement"),
                   ("hors_modele", "hors périmètre signalé quand attendu"), ("flux", "flux nommés quand attendu")):
        a, b = taux(k)
        lines.append(f"{lab} : {a}/{b}" + (f" ({100 * a / b:.0f} %)" if b else ""))
    lines.append(f"statuts du chatbot : " + ", ".join(f"{s} {sum(r['statut_chatbot'] == s for r in ok)}"
                                                    for s in ("ok", "corrigee", "bloquee")))
    if nb:
        lines.append(f"nombres ancrés (strict) : {nb - nn}/{nb} ({100 * (nb - nn) / nb:.1f} %)")
    lines.append(f"qualificatifs du vocabulaire employés : {nqt} ; non conformes ou hors vocabulaire : {nqb}"
                 + (f" ({100 * (nqt - min(nqb, nqt)) / nqt:.0f} % conformes)" if nqt else ""))
    lines.append(f"réponses avec un scénario affichable sur la carte : {sum(1 for r in ok if r.get('carte'))}/{len(ok)}")
    if ok:
        s = sorted(r["secondes"] for r in ok)
        lines.append(f"latence (chatbot) : médiane {statistics.median(s):.1f} s, max {s[-1]:.1f} s")
    for r in ok:
        bad = [k for k in ("ancrage", "qualificatifs", "verif_chatbot", "lexique", "hors_modele", "flux") if k in r and not r[k]]
        if bad:
            lines.append(f"  {r['id']} : {', '.join(bad)} {r['non_ancres'] or ''} {r['qualifs_non_conformes'] or ''} "
                         f"{r['termes'] or ''}".rstrip())
    out = "\n".join(lines)
    (HERE / "score_chatbot.txt").write_text(out + "\n")
    print("\n" + out)


if __name__ == "__main__":
    main()
