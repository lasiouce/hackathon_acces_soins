"""Évalue le compilateur sur cas_test.yaml (cas écrits avant le code, non ajustés).

Run (racine du dépôt) : uv run python v2/langage/evaluer.py
Correspondance exacte = leviers (après parse_levers, défauts complétés) + profession + territoire.
non_modelise est mesuré à part (ensemble des identifiants).
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compilateur import compile, serveur  # noqa: E402

HERE = Path(__file__).resolve().parent


def main():
    S = serveur()
    cas = yaml.safe_load((HERE / "cas_test.yaml").read_text(encoding="utf-8"))["cas"]
    champs = {"leviers": 0, "profession": 0, "territoire": 0, "non_modelise": 0}
    exact, echecs, par_cat = 0, [], {}
    for c in cas:
        a = c["attendu"]
        r = compile(c["texte"])
        att_lv, err = S.parse_levers({k: ("1" if v is True else "0" if v is False else str(v))
                                      for k, v in (a.get("leviers") or {}).items()})
        assert not err, (c["id"], err)
        ok = {"leviers": r["leviers_valides"] == att_lv,
              "profession": r["profession"] == a.get("profession"),
              "territoire": r["territoire"] == a.get("territoire", "FR"),
              "non_modelise": {x["id"] for x in r["non_modelise"]} == set(a.get("non_modelise") or [])}
        for k, v in ok.items():
            champs[k] += v
        e = ok["leviers"] and ok["profession"] and ok["territoire"]
        exact += e
        tot = par_cat.setdefault(c["categorie"], [0, 0])
        tot[0] += e
        tot[1] += 1
        if not all(ok.values()):
            diff = {k: v for k, v in r["leviers_valides"].items() if v != att_lv[k]}
            echecs.append((c, ok, r, {k: (v, att_lv[k]) for k, v in diff.items()}))
    n = len(cas)
    print(f"Correspondance exacte (leviers + profession + territoire) : {exact}/{n} = {exact / n:.0%}")
    for k, v in champs.items():
        print(f"  {k:<13} {v}/{n} = {v / n:.0%}")
    print("Par catégorie (exacte) : " + ", ".join(f"{k} {a}/{b}" for k, (a, b) in par_cat.items()))
    print(f"\nÉchecs ({len(echecs)}, tout champ confondu) :")
    for c, ok, r, diff in echecs:
        ko = [k for k, v in ok.items() if not v]
        print(f"- #{c['id']} [{c['categorie']}] {c['texte']}")
        print(f"    champs faux : {', '.join(ko)}")
        if diff:
            print(f"    leviers (obtenu, attendu) : {diff}")
        if not ok["profession"] or not ok["territoire"]:
            print(f"    profession/territoire obtenus : {r['profession']} / {r['territoire']}")
        if not ok["non_modelise"]:
            print(f"    non_modelise obtenu : {[x['id'] for x in r['non_modelise']]} ; attendu {c['attendu'].get('non_modelise')}")


if __name__ == "__main__":
    main()
