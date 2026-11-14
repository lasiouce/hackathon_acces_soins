"""Évalue l'étape d'analyse par modèle de langage sur les jeux à l'aveugle 5 et 6, avec la grille de
v2/langage/evaluer_hors_echantillon.py (décision du 2026-11-14 : « un modèle de langage pour l'analyse seule,
évalué sur les jeux 5 et 6 »). Point de comparaison : le compilateur à glossaire sur le jeu 6, 21/30 (70 %), seul
jeu encore à l'aveugle pour lui (le jeu 5 a servi à le corriger au tour 6 ; contrôle --deterministe : 30/30 et 21/30).

Le modèle reçoit le prompt système du chatbot et un seul outil, `regler_scenario` ; on note son premier appel.

Run (racine du dépôt) :
    ANTHROPIC_API_KEY=... uv run python eval/evaluer_analyse.py      # 60 appels à l'API
    uv run python eval/evaluer_analyse.py --deterministe             # contrôle de la grille : 30/30 et 21/30
"""
import collections
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from chat import agent as A  # noqa: E402
from passerelle import requetes as O  # noqa: E402   (outil d'évaluation hors ligne : pas le processus du chatbot)
from passerelle import schemas as SC  # noqa: E402

LANGAGE = O.V2 / "langage"

JEUX = ["cas_test_hors_echantillon_5.yaml", "cas_test_hors_echantillon_6.yaml"]
OUTIL = {"name": "regler_scenario",
         "description": "Traduit la demande en un scénario du jumeau : leviers modifiés, profession, territoire, et politiques non modélisées.",
         "input_schema": {"type": "object", "additionalProperties": False, "required": ["leviers", "profession", "territoire", "non_modelise"],
                          "properties": {"leviers": SC.LEVIERS,
                                         "profession": {"anyOf": [SC.PROF, {"type": "null"}]},
                                         "territoire": SC.TERR,
                                         "non_modelise": {"type": "array", "items": {"type": "string"},
                                                          "description": "Libellés des politiques demandées qui ne sont pas des leviers du jumeau."}}}}
CONSIGNE = ("Mode évaluation : n'appelle aucun autre outil. Appelle une seule fois regler_scenario avec la traduction de la demande "
            "(leviers au tendanciel omis ; territoire « France » si aucun n'est cité). Leviers et politiques non modélisées : "
            + json.dumps(O.decrire_leviers(), ensure_ascii=False))


def par_llm(texte: str) -> dict:
    client = A._client()
    rep = client.messages.create(model=A.MODELE, max_tokens=4000, output_config={"effort": A.EFFORT},
                                 system=[{"type": "text", "text": A.systeme(O.perimetre()) + "\n\n" + CONSIGNE, "cache_control": {"type": "ephemeral"}}],
                                 tools=[OUTIL], messages=[{"role": "user", "content": texte}])
    u = next((b for b in rep.content if b.type == "tool_use"), None)
    if u is None:
        return {"leviers": {}, "profession": None, "territoire": "FR", "non_modelise": [], "brut": "aucun appel"}
    x = u.input
    try:
        terr = O.territoire(x.get("territoire"))
    except O.ErreurOutil:
        terr = "?"
    try:
        lv = O.leviers(x.get("leviers"))
    except O.ErreurOutil:                     # hors bornes : on compte faux, comme un réglage invalide
        lv = {"invalide": json.dumps(x.get("leviers"))}
    return {"leviers": lv, "profession": x.get("profession"), "territoire": terr, "non_modelise": x.get("non_modelise") or []}


def par_glossaire(texte: str) -> dict:
    r = O.NL().compile(texte)
    return {"leviers": r["leviers_valides"], "profession": r["profession"], "territoire": r["territoire"] or "FR",
            "non_modelise": r["non_modelise"]}


def main():
    f = par_glossaire if "--deterministe" in sys.argv else par_llm
    D = {l["k"]: l["default"] for l in O.S().LEVIERS_UI}

    def norm_lv(d):   # même convention que v2/langage/evaluer_hors_echantillon.py
        out = {}
        for k, v in (d or {}).items():
            if isinstance(v, bool):
                v = int(v)
            if k in D and (v == D[k] or (isinstance(D[k], bool) and v == int(D[k]))):
                continue
            out[k] = round(float(v), 3) if isinstance(v, (int, float)) else v
        return out

    total_ok = total_n = 0
    for jeu in JEUX:
        cas = yaml.safe_load((LANGAGE / jeu).read_text(encoding="utf-8"))
        tot, ok, fld, fails = collections.Counter(), collections.Counter(), collections.Counter(), []
        for c in cas:
            r, a, cat = f(c["texte"]), c["attendu"], c.get("categorie", "?")
            tot[cat] += 1
            got = {"leviers": norm_lv(r["leviers"]), "profession": r["profession"], "territoire": r["territoire"] or "FR",
                   "non_modelise": bool(r["non_modelise"])}
            exp = {"leviers": norm_lv(a.get("leviers")), "profession": a.get("profession"), "territoire": a.get("territoire") or "FR",
                   "non_modelise": bool(a.get("non_modelise"))}
            bad = [k for k in exp if got[k] != exp[k]]
            for k in exp:
                fld[k] += k not in bad
            if not bad:
                ok[cat] += 1
            else:
                fails.append((c["id"], cat, c["texte"], {k: (got[k], exp[k]) for k in bad}))
        n = len(cas)
        total_ok += sum(ok.values())
        total_n += n
        print(f"\n## {jeu} : exact {sum(ok.values())}/{n} = {sum(ok.values()) / n:.0%}")
        print({k: f"{ok[k]}/{tot[k]}" for k in tot})
        print({k: f"{fld[k]}/{n}" for k in fld})
        for x in fails:
            print("-", x)
    print(f"\nTOTAL jeux 5 + 6 : {total_ok}/{total_n} = {total_ok / total_n:.0%} "
          f"({'glossaire' if f is par_glossaire else A.MODELE + ', effort ' + A.EFFORT})\n"
          "Référence glossaire à l'aveugle : jeu 6 = 21/30 (70 %). Le jeu 5 a servi à corriger le glossaire au tour 6 : "
          "il n'est plus à l'aveugle pour lui (30/30 en échantillon), il l'est toujours pour le modèle de langage.")


if __name__ == "__main__":
    main()
