import json, glob, sys, collections
S = sys.argv[1]
c = collections.Counter(); rows=[]
for f in sorted(glob.glob(S + "/verif/v*.json")):
    try: d = json.load(open(f))
    except Exception as e: print("BAD", f, e); continue
    items = d.get("items") or [x for v in d.values() if isinstance(v, list) for x in v]
    for it in items:
        if not isinstance(it, dict): continue
        vf = it.get("verdict_final"); c[vf]+=1
        rows.append((f.rsplit('/',1)[1], it))
print(dict(c))
for f, it in rows:
    if it.get("verdict_final") in ("retenu","reformulé","trouvé"):
        print(f"- [{f[:3]}] {it.get('fiche')} | {it.get('verdict_final')} | {it.get('gravite')} | {str(it.get('correction'))[:260]}")
