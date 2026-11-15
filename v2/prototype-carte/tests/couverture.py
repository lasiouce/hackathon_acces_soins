"""Critères du branchement besoin → carte (plan v2/docs/lab/derivations/2026-11-15-besoin-carte-plan.md).

Run (serveur de la carte lancé) : uv run python v2/prototype-carte/tests/couverture.py [http://127.0.0.1:8767]
  -> v2/artifacts/besoin_carte/results.json ; code de sortie 1 si un critère échoue.

  K1 O2         prof=medecine-generale et prof=specialistes -> 400 ; aucune clé de couverture MG ni spécialistes
  K2 neutre     sans levier ni L23 : C scénario = C tendanciel (≤ 1e-12) ; C = 1 partout en 2026 ; écart = 0
  K3 L23 = 0    l23=0 avec leviers d'offre : couverture identique au tendanciel du même scénario sans L23
  K4 L23 = 1    C des pharmaciens change ; ETP de MG libérés > 0 ; chaque paramètre porte statut et source
  K5 latence    /api/couverture, 95ᵉ centile < 150 ms, n ≥ 30, leviers variés ; cache froid exclu et déclaré
  K6 lexique    aucun terme interdit dans index.html (lexicon.md)
  K7 transfert  transfert hypothétique (tr_*) : MG → PH aux paramètres de L23, a divisé par le facteur de niveau
                (niveau MG mesuré, ameli 2025, contre celui de M1 que garde L23) = l23=1 (≤ 1e-9) ; tr_a=0 ⇒ écart 0 ;
                cible MG, spécialistes ou hors des 5 ⇒ 400 ; source MG ou spécialistes ⇒ 200, étiqueté « hypothèse de
                l'utilisateur » ; p95 < 150 ms à chaud
"""
import json
import math
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8767"
OUT = Path("v2/artifacts/besoin_carte")
R: dict = {}


def get(q: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"{BASE}/api/couverture?{q}", timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def keys(o, acc=None):
    acc = set() if acc is None else acc
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(str(k))
            keys(v, acc)
    elif isinstance(o, list):
        for v in o:
            keys(v, acc)
    return acc


def diff(a, b) -> float:
    return max((abs(x - y) for x, y in zip(a, b) if x is not None and y is not None), default=0.0)


def k1():
    codes = {p: get(f"prof={p}")[0] for p in ("medecine-generale", "specialistes")}
    _, r = get("prof=pharmaciens&l23=1")
    ks = keys({k: v for k, v in r.items() if k != "l23"} | {"couv": r["deps"]})
    bad = [k for k in ks if k in ("medecine-generale", "specialistes")]
    cles = list(r) + list(r["fr"])
    ok = all(c == 400 for c in codes.values()) and not bad and r["prof"] == "pharmaciens"
    R["K1_O2"] = dict(ok=ok, codes=codes, cles_couverture=cles, mg_hors_transferts=bad)


def k2():
    worst, c26 = 0.0, 0.0
    for p in ("sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers"):
        _, r = get(f"prof={p}")
        for d in list(r["deps"].values()) + [r["fr"]]:
            worst = max(worst, diff(d["cs"], d["cb"]), max(abs(e) for e in d["ecart"] if e is not None))
            c26 = max(c26, abs(d["cs"][0] - 1) if d["cs"][0] is not None else 0)
    R["K2_neutre"] = dict(ok=worst <= 1e-12 and c26 <= 1e-12, ecart_max=worst, ecart_2026_max=c26)


def k3():
    _, a = get("prof=pharmaciens&quotas=1.3&retraite=2&l23=0")
    _, b = get("prof=pharmaciens&quotas=1.3&retraite=2")
    _, t = get("prof=pharmaciens")
    w = max(diff(a["deps"][d]["cs"], b["deps"][d]["cs"]) for d in a["deps"])
    moved = max(diff(a["deps"][d]["cs"], t["deps"][d]["cs"]) for d in a["deps"])
    R["K3_l23_zero"] = dict(ok=w <= 1e-12 and a["l23"] is None and moved > 1e-4, ecart_l23_0_vs_sans=w,
                            effet_leviers_offre=moved)


def k4():
    _, a = get("prof=pharmaciens&l23=1")
    _, b = get("prof=pharmaciens")
    w = diff(a["fr"]["cs"], b["fr"]["cs"])
    tr = a["l23"]["transferts"][0]
    stat = all(p.get("status") in ("mesuré", "sourcé", "supposé") and p.get("source") for p in a["l23"]["params"])
    R["K4_l23"] = dict(ok=w > 1e-4 and tr["etp_liberes_source"][-1] > 0 and tr["source"] == "medecine-generale" and stat,
                       ecart_C_fr=w, C_fr_2050=[b["fr"]["cs"][-1], a["fr"]["cs"][-1]],
                       etp_mg_liberes_2050=tr["etp_liberes_source"][-1], actes_mg_liberes_2050=tr["actes_mg_liberes"][-1],
                       params={p["name"]: [p["value"], p["status"]] for p in a["l23"]["params"]})


def k5():
    profs = ("sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers")
    qs = [f"prof={p}&quotas={q}&l23={l}" for p in profs for q in (1, 1.15) for l in (0, 1)]
    froid = []
    for q in qs:          # cache froid : premier passage de chaque combinaison (jumeau + carte), exclu et déclaré
        t = time.perf_counter()
        get(q)
        froid.append((time.perf_counter() - t) * 1000)
    froid = sorted(froid)
    ms = []
    for i in range(3):
        for q in qs:
            t = time.perf_counter()
            c, _ = get(q)
            ms.append((time.perf_counter() - t) * 1000)
    ms.sort()
    p95 = ms[math.ceil(0.95 * len(ms)) - 1]
    R["K5_latence"] = dict(ok=p95 < 150 and len(ms) >= 30, n=len(ms), p50_ms=round(ms[len(ms) // 2], 1),
                           p95_ms=round(p95, 1), max_ms=round(ms[-1], 1), froid_ms=dict(n=len(froid), p50=round(froid[len(froid) // 2], 1), max=round(froid[-1], 1)),
                           note="cache chaud (besoin précalculé au démarrage, trajectoire par jeu de leviers en cache) ; "
                                "premier passage d'un jeu de leviers exclu")


def k7():
    _, l = get("prof=pharmaciens&l23=1")
    _, t0_ = get("prof=pharmaciens&tr_src=medecine-generale&tr_cible=pharmaciens&tr_a=0.01")
    f = t0_["transfert_hypothetique"]["besoin_source"]["facteur_niveau"]
    _, t = get(f"prof=pharmaciens&tr_src=medecine-generale&tr_cible=pharmaciens&tr_a={0.01 / f!r}&tr_k=1&tr_sinf=0.74&tr_tau=2.4&tr_t0=2026")
    egal = max(diff(l["deps"][d]["cs"], t["deps"][d]["cs"]) for d in l["deps"])
    _, z = get("prof=infirmiers&tr_src=medecine-generale&tr_cible=infirmiers&tr_a=0")
    nul = max(max(abs(e) for e in d["ecart"] if e is not None) for d in list(z["deps"].values()) + [z["fr"]])
    refus = {c: get(f"prof=infirmiers&tr_src=infirmiers&tr_cible={c}")[0] for c in ("medecine-generale", "specialistes", "orthophonistes")}
    acc = {s: get(f"prof=infirmiers&tr_src={s}&tr_cible=infirmiers&tr_sinf=0.1") for s in ("medecine-generale", "specialistes")}
    lab = all(c == 200 and r["transfert_hypothetique"]["statut"] == "hypothèse de l'utilisateur" and r["fr"]["ecart"][-1] < 0
              for c, r in acc.values())
    qs = [f"prof=infirmiers&tr_src=medecine-generale&tr_cible=infirmiers&tr_a={a}&tr_sinf={s}" for a in (0.05, 0.1, 0.2) for s in (0.1, 1)]
    for q in qs:
        get(q)                 # cache froid exclu
    ms = []
    for _ in range(5):
        for q in qs:
            t0 = time.perf_counter()
            get(q)
            ms.append((time.perf_counter() - t0) * 1000)
    ms.sort()
    p95 = ms[math.ceil(0.95 * len(ms)) - 1]
    R["K7_transfert_hypothetique"] = dict(ok=egal <= 1e-9 and nul <= 1e-12 and all(c == 400 for c in refus.values()) and lab
                                          and p95 < 150, ecart_generique_vs_l23=egal, facteur_niveau_mg=f, ecart_a_nul=nul, codes_cible_interdite=refus,
                                          ecart_fr_2050={s: r["fr"]["ecart"][-1] for s, (_, r) in acc.items()}, n=len(ms),
                                          p95_ms=round(p95, 1))


def k6():
    html = Path("v2/prototype-carte/index.html").read_text().lower()
    interdits = ("désert", "pénurie critique", "médiocre", "sinistré", "catastroph", "% du besoin couvert")
    found = [t for t in interdits if t in html]
    R["K6_lexique"] = dict(ok=not found, termes_trouves=found)


if __name__ == "__main__":
    for f in (k1, k2, k3, k4, k5, k6, k7):
        try:
            f()
        except Exception as e:
            R[f.__name__] = dict(ok=False, erreur=f"{type(e).__name__}: {e}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))
    for k, v in R.items():
        print(("OK  " if v["ok"] else "ÉCHEC ") + k, {a: b for a, b in v.items() if a not in ("ok", "params", "cles_couverture")})
    sys.exit(0 if all(v["ok"] for v in R.values()) else 1)
