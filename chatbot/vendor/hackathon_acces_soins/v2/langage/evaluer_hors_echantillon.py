"""Score du compilateur sur cas_test_hors_echantillon.yaml (écrit à l'aveugle par un agent qui n'a vu ni le glossaire ni le compilateur).

Run (racine du dépôt) : uv run python v2/langage/evaluer_hors_echantillon.py
Un levier à sa valeur par défaut compte comme non réglé (convention du jeu de cas).
"""
import sys, yaml, importlib.util, collections
sys.path.insert(0,"v2/langage")
spec=importlib.util.spec_from_file_location("c","v2/langage/compilateur.py");C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
cas=yaml.safe_load(open("v2/langage/"+(sys.argv[1] if len(sys.argv)>1 else "cas_test_hors_echantillon.yaml")))
S=C.serveur();D={l["k"]:l["default"] for l in S.LEVIERS_UI}
def norm_lv(d):
    out={}
    for k,v in (d or {}).items():
        if isinstance(v,bool): v=int(v)
        if k in D and (v==D[k] or (isinstance(D[k],bool) and v==int(D[k]))): continue
        out[k]=round(float(v),3) if isinstance(v,(int,float)) else v
    return out
tot=collections.Counter(); ok=collections.Counter(); fld=collections.Counter(); fails=[]
for c in cas:
    r=C.compile(c["texte"]); a=c["attendu"]; cat=c.get("categorie","?"); tot[cat]+=1
    got={"leviers":norm_lv(r["leviers_valides"]),"profession":r["profession"],"territoire":r["territoire"] or "FR","non_modelise":bool(r["non_modelise"])}
    exp={"leviers":norm_lv(a.get("leviers")),"profession":a.get("profession"),"territoire":a.get("territoire") or "FR","non_modelise":bool(a.get("non_modelise"))}
    bad=[f for f in exp if got[f]!=exp[f]]
    for f in exp: fld[f]+= f not in bad
    if not bad: ok[cat]+=1
    else: fails.append((c["id"],cat,c["texte"],{f:(got[f],exp[f]) for f in bad}))
n=len(cas); print(f"exact {sum(ok.values())}/{n} = {sum(ok.values())/n:.0%}")
print({k:f"{ok[k]}/{tot[k]}" for k in tot}); print({f:f"{fld[f]}/{n}" for f in fld})
for f in fails: print("-",f)
