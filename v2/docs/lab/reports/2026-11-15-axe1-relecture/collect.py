import json, glob, sys, collections
S = sys.argv[1]
rows = []
for f in sorted(glob.glob(S + "/out/r*.json")):
    try: d = json.load(open(f))
    except Exception as e: print("BAD", f, e); continue
    src = f.rsplit("/",1)[1][:-5]
    for c in d.get("claims", []):
        rows.append((src, d.get("acces",""), c))
cnt = collections.Counter(c.get("verdict") for _,_,c in rows)
print(len(rows), dict(cnt))
for src, acc, c in rows:
    if c.get("verdict") == "ecart":
        print(f"\n[{src}] {c.get('fiche')} | {c.get('type_ecart')} | {c.get('affirmation','')[:150]}\n  fiche: {str(c.get('valeur_fiche'))[:120]}\n  source: {str(c.get('valeur_source'))[:160]}\n  « {str(c.get('citation'))[:200]} » ({c.get('page')})\n  note: {str(c.get('note'))[:250]}")
