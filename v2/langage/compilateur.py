"""Compilateur de politiques en langage naturel -> réglages des leviers du prototype.

Déterministe, sans modèle de langage : un glossaire relisible (glossaire.yaml) et des règles
écrites ici. Il TRADUIT du texte en leviers ; il ne calcule jamais d'effectif.

Usage (racine du dépôt) :
    uv run python v2/langage/compilateur.py "Augmenter de 20 % le numerus apertus des kinés dans le Puy-de-Dôme"
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def serveur():
    """Importe v2/prototype/server.py sans lancer le serveur (comme v2/prototype-carte/server.py)."""
    spec = importlib.util.spec_from_file_location("proto_v1", HERE.parent / "prototype" / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)   # fait le chdir vers la racine (geo() lit des chemins relatifs)
    return mod


@lru_cache(maxsize=1)
def glossaire() -> dict:
    return yaml.safe_load((HERE / "glossaire.yaml").read_text(encoding="utf-8"))


def norm(s: str) -> str:
    """Minuscules, sans accents ; apostrophes et tirets -> espace ; espaces simples."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("œ", "oe").replace("’", " ").replace("'", " ").replace("‑", " ")
    s = re.sub(r"(?<=[a-z])-(?=[a-z])", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _rx(term: str) -> re.Pattern:
    t = re.escape(norm(term))
    return re.compile(rf"(?<![a-z0-9]){t}(?![a-z0-9])")


def _find(text: str, terms) -> list[tuple[int, int, str]]:
    """Occurrences (début, fin, terme), termes les plus longs d'abord, sans chevauchement."""
    hits, used = [], []
    for t in sorted(set(terms), key=lambda x: -len(norm(x))):
        for m in _rx(t).finditer(text):
            if not any(m.start() < e and s < m.end() for s, e in used):
                hits.append((m.start(), m.end(), t))
                used.append((m.start(), m.end()))
    return sorted(hits)


# ---------------------------------------------------------------- territoire, profession

@lru_cache(maxsize=1)
def _territoires() -> list[tuple[str, str, bool]]:
    """(forme normalisée, code serveur, exige une préposition avant)."""
    S, G = serveur(), glossaire()
    out = []
    for code, nom in S.REGIONS.items():
        out.append((norm(nom), "R" + code, False))
    g = S.geo()
    for dep, row in g.iterrows():
        if dep in ("999", "20"):
            continue
        out.append((norm(row.dep_name), "D" + dep, True))
    for ville, dep in G["villes"].items():
        out.append((norm(ville), "D" + dep, False))
    for code, formes in G.get("sigles", {}).items():
        for f in formes:
            out.append((f, code, False))
    for code, formes in G.get("gentiles", {}).items():      # « les kinés lyonnais » -> D69 ; variantes en e, s, es, ne, nes
        for f in formes:
            for v in {f, f + "e", f + "s", f + "es"} | ({f + "ne", f + "nes"} if f.endswith("en") else set()):
                out.append((v, code, False))
    out.append(("france", "FR", False))
    out.append(("national", "FR", False))
    return sorted(out, key=lambda x: -len(x[0]))


PREP = r"(?:dans|en|du|de|des|le|la|les|l|pour|sur|a)\s"


def detecter_territoire(t: str):
    used, found = [], []
    for forme, code, prep in _territoires():
        pat = rf"(?<![a-z0-9]){re.escape(forme)}(?![a-z0-9])"
        for m in re.finditer(pat, t):
            if any(m.start() < e and s < m.end() for s, e in used):
                continue
            if prep and not re.search(rf"(?:^|\s){PREP}$", t[:m.start()]):
                continue
            used.append((m.start(), m.end()))
            found.append((m.start(), code, forme))
    return sorted(found), used


def detecter_profession(t: str):
    syn = {s: p for p, l in glossaire()["professions"].items() for s in l}
    hits = _find(t, syn)
    profs = []
    for _, _, s in hits:
        if syn[s] not in profs:
            profs.append(syn[s])
    return profs


# ---------------------------------------------------------------- quantités

NUM = r"(\d+(?:[.,]\d+)?|\d{1,3}(?: \d{3})+)"


def _nombre(tok: str) -> float | None:
    tok = tok.replace(" ", "").replace(",", ".")
    try:
        return float(tok)
    except ValueError:
        return glossaire()["nombres"].get(tok)


def _direction(c: str, pos: int | None = None) -> str | None:
    """Sens hausse / baisse. Avec pos (position de la quantité), le mot de sens le plus proche l'emporte,
    à égalité celui qui suit (« 30 % … en moins ») ; sinon le premier de la proposition."""
    D = glossaire()["directions"]
    hits = [(s, "hausse") for s, _, _ in _find(c, D["hausse"])] + [(s, "baisse") for s, _, _ in _find(c, D["baisse"])]
    for sens, racines in D.get("racines", {}).items():   # formes conjuguées : « augmentait », « allongeons »…
        hits += [(m.start(), sens) for m in re.finditer(rf"(?<![a-z])(?:{'|'.join(racines)})[a-z]*", c)]
    if re.search(r"(?:^|[\s(])\+\s*\d", c):
        hits.append((c.index("+"), "hausse"))
    if re.search(r"(?:^|[\s(])-\s*\d", c):
        hits.append((c.index("-"), "baisse"))
    if not hits:
        return None
    if pos is None:
        return min(hits)[1]
    # un comparatif placé après la quantité (« 30 % de … en moins ») l'emporte sur le verbe qui la précède
    post = [(m.start(), "hausse" if m.group(1) == "plus" else "baisse")
            for m in re.finditer(r"(?<![a-z])(?:en|de) (plus|moins)(?![a-z])", c) if m.start() > pos]
    if post:
        return min(post)[1]
    return min(hits, key=lambda h: (abs(h[0] - pos), h[0] < pos))[1]


def quantite(c: str, sorte: str | None = None) -> dict | None:
    """Une quantité dans une proposition : {'type': 'facteur'|'pct'|'ans', 'v': float, 'brut': str}.

    sorte = 'ans' (levier en années) ou 'facteur' (levier multiplicateur) : on ne cherche que ce type,
    pour qu'« avant 60 ans » ne passe pas pour une durée quand le levier est un multiplicateur."""
    if sorte == "facteur":
        q = quantite(c)
        return q if q and q["type"] != "ans" else _quantite_facteur(c)
    if sorte == "ans":
        q = quantite(c)
        return q if q and q["type"] == "ans" else None
    D = glossaire()["directions"]
    mots = "|".join(sorted(glossaire()["nombres"], key=len, reverse=True))
    # pourcentages
    m = re.search(rf"{NUM}\s*(?:%|pour ?cent|points?\b)", c)
    if m:
        p = _nombre(m.group(1))
        d = _direction(c, m.start())
        if d is None:
            return {"type": "pct_sans_sens", "v": p, "brut": m.group(0)}
        return {"type": "facteur", "v": 1 + p / 100 if d == "hausse" else 1 - p / 100, "brut": m.group(0) + f" ({d})"}
    # années / mois
    m = re.search(rf"(?<![a-z0-9])({NUM[1:-1]}|{mots})\s*(ans?|annees?|mois)(?![a-z])", c)
    if m:
        n = _nombre(m.group(1))
        if n is not None:
            v = n / 12 if m.group(2) == "mois" else n
            d = _direction(c, m.start())
            return {"type": "ans", "v": -v if d == "baisse" else v, "brut": m.group(0)}
    return _quantite_facteur(c)


def _quantite_facteur(c: str) -> dict | None:
    D = glossaire()["directions"]
    mots = "|".join(sorted(glossaire()["nombres"], key=len, reverse=True))
    # multiplicateurs « x 1,5 », « 1,5 fois », « trois fois plus / moins »
    m = re.search(rf"(?:(?<![a-z])x|×)\s*{NUM}|(?<![a-z0-9])({NUM[1:-1]}|{mots})\s*fois(?:\s+(plus|moins))?", c)
    if m:
        n = _nombre(m.group(1) or m.group(2))
        if n:
            return {"type": "facteur", "v": 1 / n if m.group(3) == "moins" else n, "brut": m.group(0)}
    # verbes multiplicateurs conjugués : « doublait », « triplerait » ; « diviser par quatre »
    m = re.search(rf"(?<![a-z])divis[a-z]* par ({NUM[1:-1]}|{mots})(?![a-z0-9])", c)
    if m:
        n = _nombre(m.group(1))
        if n:
            return {"type": "facteur", "v": 1 / n, "brut": m.group(0)}
    m = re.search(r"(?<![a-z])(doubl|tripl|quadrupl)[a-z]*", c)
    if m:
        return {"type": "facteur", "v": {"doubl": 2.0, "tripl": 3.0, "quadrupl": 4.0}[m.group(1)], "brut": m.group(0)}
    # fractions avec un sens : « un bon tiers de plus », « un quart de moins »
    d = _direction(c)
    if d and not _find(c, D["facteurs"]):
        for terme, f in sorted(glossaire()["fractions"].items(), key=lambda x: -len(x[0])):
            if _rx(terme).search(c) and not re.search(rf"{terme} (?:des )?zones", c):
                return {"type": "facteur", "v": 1 + f if d == "hausse" else 1 - f, "brut": f"{terme} ({d})"}
    # formules
    f = _find(c, D["facteurs"])
    if f:
        terme = f[0][2]
        v = float(D["facteurs"][terme])
        if terme == "de moitie" and _direction(c) == "hausse":
            v = 1.5
        return {"type": "facteur", "v": v, "brut": terme}
    return None


# ---------------------------------------------------------------- transfert hypothétique

def _original(texte: str, n: str) -> str:
    """Passage de `texte` dont la forme normalisée est `n` (pour réafficher l'acte avec ses accents) ; n si absent."""
    out, idx = [], []
    for i, c in enumerate(texte):
        for x in norm(c) or " ":
            if x == " " and (not out or out[-1] == " "):
                continue
            out.append(x)
            idx.append(i)
    j = "".join(out).find(n)
    return texte[idx[j]:idx[j + len(n) - 1] + 1] if j >= 0 and n else n


def transfert_hypothetique(t: str, texte: str = "") -> tuple[dict | None, tuple[int, int] | None]:
    """« X prennent en charge / font p % de <acte> de Y » -> transfert hypothétique (forme de L23, paramètres de
    l'utilisateur·rice) et son empan dans t. Cible : l'une des 5 ; source : MG, spécialistes ou l'une des 5."""
    S, G = serveur(), glossaire()
    H = G["transferts_hypothetiques"]
    syn5 = {s: p for p, l in G["professions"].items() for s in l}
    src_syn = {s: p for p, l in H["sources"].items() for s in l} | syn5
    alt = "|".join(re.escape(s) for s in sorted(src_syn, key=len, reverse=True))
    m = re.search(rf"{NUM}\s*(?:%|pour ?cent)\s+(?:(?:de la|de l|des|du|de|d)\s+)?(?P<acte>.{{0,80}}?)\s+"
                  rf"(?:de la|de l|des|du|de|d|aux|chez les)\s+(?P<src>{alt})(?![a-z])", t)
    if not m:
        return None, None
    avant = [h for h in _find(t[:m.start()], syn5)]
    if not avant:
        return None, None
    c0, c1, terme = avant[-1]                              # profession la plus proche avant la part
    if not re.search(rf"(?<![a-z])(?:{'|'.join(H['verbes'])})[a-z]*", t[c1:m.start()]):
        return None, None
    src, cib = src_syn[m.group("src")], syn5[terme]
    if src == cib:
        return None, None
    p = _nombre(m.group(1))
    if p is None or not 0 < p <= 100:
        return None, None
    acte = _original(texte, m.group("acte").strip()) if texte else m.group("acte").strip()
    demande = bool(re.match(rf"(?:la |l |le )?(?:{'|'.join(H['mots_demande'])})(?![a-z])", norm(acte)))
    y = re.search(r"(?:a partir de|des|depuis)\s+(?:l an |janvier |septembre )?(20\d\d)(?!\d)", t)
    t0 = int(y.group(1)) if y and 2026 <= int(y.group(1)) <= S.H else None
    lib_src = H["libelles_sources"].get(src) or S.PROFS[src].lower()
    api = {"tr_src": src, "tr_cible": cib, ("tr_a" if demande else "tr_sinf"): round(p / 100, 4)}
    if t0:
        api["tr_t0"] = t0
    bal = ([round(min(0.5, k * p / 100), 4) for k in H["balayage_demande"]] if demande else list(H["balayage_acte"]))
    trh = {"id": "hypothetique", "source": src, "cible": cib, "mode": "demande" if demande else "acte", "p": p,
           "acte": acte, "t0": t0 or 2026,
           "libelle": f"Les {S.PROFS[cib].lower()} prennent en charge {p:g} % {'de la demande' if demande else 'des ' + acte} "
                      f"des {lib_src}".replace(".", ","),
           "parametres_api": api, "balayage": {"tr_a": bal}, "statut": "hypothèse de l'utilisateur", "repere": m.group(0)}
    return trh, (c0, m.end())


# ---------------------------------------------------------------- compilation

def _fmt(l: dict, v) -> str:
    if l["fmt"] in ("pct",):
        return f"{(v - 1) * 100:+.0f} %"
    if l["fmt"] == "pct0":
        return f"{v * 100:.0f} %"
    if l["fmt"] == "x":
        return f"× {v:g}".replace(".", ",")
    if l["fmt"] == "ans":
        return f"+{v:g} an{'s' if v > 1 else ''}".replace(".", ",")
    return str(v)


def compile(texte: str, profession: str | None = None, territoire: str | None = None) -> dict:  # noqa: A001
    S, G = serveur(), glossaire()
    UI = S.UI
    t = norm(texte)
    mots_n = "|".join(sorted(G["nombres"], key=len, reverse=True))
    t = re.sub(rf"(?<![a-z0-9])(\d+|{mots_n})\s+ans?\s+et\s+demie?(?![a-z])",
               lambda m: f"{(_nombre(m.group(1)) or 0) + 0.5:g} ans", t)          # « un an et demi » -> « 1.5 ans »
    t = re.sub(r"(?<![a-z0-9])(?:un )?demi an(?:nee)?(?![a-z])", "0.5 ans", t)
    t = re.sub(r"emploi et (?:la )?retraite", "emploi retraite", t)
    # deux âges : « à 67 ans au lieu de 65.5 », « passer de 62 à 64 ans » -> écart en années
    def _ecart(a, b, m):
        a, b = _nombre(a), _nombre(b)
        return f"{a - b:g} ans de plus" if a and b and 50 <= min(a, b) and max(a, b) <= 80 else m.group(0)
    t = re.sub(rf"(?<![a-z])(?:a|vers) {NUM} ans au lieu de {NUM}(?: ans)?", lambda m: _ecart(m.group(1), m.group(2), m), t)
    t = re.sub(rf"(?<![a-z])de {NUM} (?:ans )?a {NUM} ans", lambda m: _ecart(m.group(2), m.group(1), m), t)                       # ne pas couper sur ce « et »
    t = re.sub(rf"multipli[a-z]* par {NUM}", lambda m: f"x {m.group(1)}", t)
    res = {"texte": texte, "leviers": {}, "profession": None, "territoire": None, "compris": [],
           "non_modelise": [], "non_compris": [], "reformulations": [], "avertissements": []}

    # neutralisation du lexique
    for e in G["neutralisation"]:
        if _rx(e["terme"]).search(t):
            res["reformulations"].append({"terme": e["terme"], "neutre": e["neutre"]})

    # politiques non modélisées
    for k, e in G["non_modelises"].items():
        h = _find(t, e["termes"])
        if h:
            res["non_modelise"].append({"id": k, "libelle": e["libelle"], "raison": e["raison"],
                                        "source": e.get("source"), "repere": h[0][2]})

    # transferts de tâches calculés par le module de besoin (L23) : date = année qui suit le terme dans sa proposition
    res["transferts"] = []
    for k, e in G.get("transferts_besoin", {}).items():
        for c in re.split(r"[,;:?!.]|\s(?:et|puis|ainsi que|mais)\s", t):
            h = _find(c, e["termes"])
            if not h or any(x["id"] == k for x in res["transferts"]):
                continue
            if re.search(r"(?:^|\s)(?:pas de|pas d|ne pas|ne peuvent pas|ne peut pas|sans|interdire|supprimer)\s", c[:h[0][0]]):
                res["compris"].append(f"{e['libelle']} : explicitement écarté.")
                continue
            y = re.search(r"(?:a partir de|des|en|depuis|au|d ici)\s+(?:l an |janvier |septembre )?(20\d\d)(?!\d)", c[h[0][1]:])
            y = y or re.search(r"(?:a partir de|des)\s+(20\d\d)(?!\d)", t)
            t0 = int(y.group(1)) if y else e["t0_defaut"]
            if not 2019 <= t0 <= S.H:
                res["avertissements"].append(f"{e['libelle']} : date {t0} hors de 2019–{S.H}, {e['t0_defaut']} retenu.")
                t0 = e["t0_defaut"]
            res["transferts"].append({"id": k, "libelle": e["libelle"], "t0": t0, "source": e["source_tache"], "cible": e["cible"],
                                      "parametres_api": {e["parametre_api"]: 1, f"{e['parametre_api']}_t0": t0},
                                      "statut": e["statut"], "fiche": e["fiche"], "repere": h[0][2]})
            res["compris"].append(f"{e['libelle']} à partir de {t0} : effectif inchangé dans le modèle ; agit sur le besoin "
                                  f"et l'indice de couverture des {e['cible']} (base 2026).")

    # transfert de tâches hypothétique (« X prennent en charge p % de <acte> de Y ») : hypothèse de l'utilisateur·rice
    trh, span = transfert_hypothetique(t, texte)
    res["transferts_hypothetiques"] = [trh] if trh else []
    if trh:
        res["non_modelise"] = [x for x in res["non_modelise"]            # la MG ou les spécialistes n'y sont que source
                               if not (x["id"] in ("quatrieme_annee_mg", "medecins_specialistes")
                                       and _rx(x["repere"]).search(t[span[0]:span[1]]))]
        res["compris"].append(f"{trh['libelle']} : transfert hypothétique (paramètres de l'utilisateur·rice), effectif "
                              f"inchangé dans le modèle ; agit sur l'indice de couverture des {trh['cible']}.")
    # O2 : refus seulement si la MG ou les spécialistes sont la cible de l'indice
    res["o2_cible"] = bool(re.search(r"couverture (?:pour |de |des |du |de la )?(?:les |la )?(?:medecins?|generalistes?|specialistes?|"
                                     r"medecine generale|cardiolog|dermatolog|ophtalmolog)", t))

    # profession
    profs = detecter_profession(t)
    if trh:      # profession de l'indice : « couverture des X » si cité, sinon la cible ; la source n'est pas une seconde profession
        m = re.search(r"couverture (?:pour |de |des |du )?(?:les )?(.{0,40})", t)
        dem = detecter_profession(m.group(1)) if m else []
        p0 = dem[0] if dem and dem[0] in (trh["cible"], trh["source"]) else trh["cible"]
        profs = [p0] + [p for p in profs if p not in (p0, trh["source"], trh["cible"])]
    m = re.search(r"combien d(?:e |es | )(.+)", t)
    if m and len(profs) > 1:
        demandee = detecter_profession(m.group(1))
        if demandee:
            profs = [demandee[0]] + [p for p in profs if p != demandee[0]]
    if profs:
        res["profession"] = profs[0]
        if len(profs) > 1:
            res["avertissements"].append(
                f"Plusieurs professions citées ({', '.join(profs)}) : le scénario porte sur une seule ; "
                f"« {profs[0]} » retenue, relancer pour les autres.")
    elif profession:
        res["profession"] = profession
    elif res["transferts"]:
        res["profession"] = res["transferts"][0]["cible"]
    if res["profession"] and res["profession"] not in S.PROFS:
        res["avertissements"].append(f"profession inconnue du serveur : {res['profession']!r}")
        res["profession"] = None

    # territoire
    terrs, terr_spans = detecter_territoire(t)
    codes = list(dict.fromkeys(c for _, c, _ in terrs))
    if codes:
        res["territoire"] = codes[0]
        if len(codes) > 1:
            res["avertissements"].append(f"Plusieurs territoires cités ({', '.join(codes)}) : « {codes[0]} » retenu.")
    else:
        res["territoire"] = territoire or "FR"

    # leviers, proposition par proposition
    lever_terms = {k: v["termes"] for k, v in G["leviers"].items() if k in ("quotas", "etrangers", "regul", "retraite", "cumul", "precoces")}
    all_terms = {s: k for k, l in lever_terms.items() for s in l}
    brut: dict = {}
    en_attente = None
    t_lev = t if not trh else t[:span[0]] + " " * (span[1] - span[0]) + t[span[1]:]     # le transfert n'est pas un levier
    clauses = [c.strip() for c in re.split(r"(?<!\d)[,.](?!\d)|(?<=\d)[,.](?!\d)|[;:?!]|\s(?:et|puis|ainsi que|mais)\s", t_lev) if c.strip()]
    for c in clauses:
        hits = _find(c, all_terms)
        reste = c
        for s, e, _ in sorted(hits, reverse=True):
            reste = reste[:s] + " " * (e - s) + reste[e:]
        q = quantite(reste, "facteur") or quantite(reste, "ans")
        leviers_c = list(dict.fromkeys(all_terms[h[2]] for h in hits))
        if "etrangers" in leviers_c and "quotas" in leviers_c:   # « étudiants formés en Belgique » : le diplôme étranger l'emporte
            leviers_c.remove("quotas")
        if not leviers_c and q and en_attente:
            leviers_c, en_attente = [en_attente], None
        if _find(c, G["directions"]["plafonner"]) and not q:
            res["non_compris"].append(f"{c} (plafonnement sans valeur chiffrée : non traduit)")
            continue
        if not leviers_c and trh and not re.sub(r"(?<![a-z])(?:si|et|les|le|la|l|des|de|du|d|que|qu|alors|quelle|quel)(?![a-z])", "", c).strip():
            continue                                               # reste de la phrase autour du transfert masqué
        if not leviers_c:
            utile = (_find(c, [s for l in G["professions"].values() for s in l])
                     or any(_rx(f).search(c) for _, _, f in terrs)
                     or any(_find(c, e["termes"]) for e in G["non_modelises"].values())
                     or any(_rx(e["terme"]).search(c) for e in G["neutralisation"]))
            if not utile:
                res["non_compris"].append(c)
            elif q and q["type"] != "ans":
                res["non_compris"].append(f"{c} (quantité sans levier reconnu)")
            continue
        for k in leviers_c:
            l = UI[k]
            if l["type"] == "toggle":
                if re.search(r"(?:^|\s)(?:pas de|pas d|ne pas|n est pas|plus de|sans|aucune?|ni|renoncer a|abandonner|supprimer)\s", c):
                    res["compris"].append(f"{l['label']} : explicitement écarté (reste au défaut).")
                    continue
                brut[k] = 1
                continue
            q = quantite(reste, "ans" if l["fmt"] == "ans" else "facteur") or q
            if q is None:
                en_attente = k
                res["non_compris"].append(f"{c} (« {l['label']} » sans ampleur chiffrée : levier laissé au défaut)")
                continue
            if q["type"] == "pct_sans_sens":
                res["non_compris"].append(f"{c} ({q['brut']} sans sens hausse ou baisse)")
                continue
            if l["fmt"] == "ans":
                if q["type"] != "ans":
                    res["non_compris"].append(f"{c} (le report de la retraite s'exprime en années)")
                    continue
                brut[k] = (q["v"], q["brut"])
            else:
                if q["type"] == "ans":
                    res["non_compris"].append(f"{c} (« {l['label']} » s'exprime en % ou en multiplicateur)")
                    continue
                brut[k] = (q["v"], q["brut"])
            if en_attente == k:
                en_attente = None

    # régulation : part des zones, destination, quotas régionaux
    if brut.get("regul"):
        m = re.search(rf"{NUM}\s*(?:%|pour ?cent)\s*des (?:zones|territoires|communes|secteurs)", t)
        frac = {"la moitie": 0.5, "un tiers": 1 / 3, "le tiers": 1 / 3, "un quart": 0.25, "le quart": 0.25,
                "toutes les": 1.0, "deux tiers": 2 / 3, "trois quarts": 0.75}
        if m:
            brut["part_zones"] = (_nombre(m.group(1)) / 100, m.group(0))
        else:
            for f, v in frac.items():
                if re.search(rf"{f} (?:des )?zones", t):
                    brut["part_zones"] = (v, f + " des zones")
                    break
        for opt, termes in G["leviers"]["dest"]["options"].items():
            if _find(t, termes):
                brut["dest"] = opt
                break
    reg_hits = [h for h in _find(t, G["leviers"]["quotas_region"]["termes"])
                if not re.search(r"(?:pas|non|sans|ni)\s+(?:\S+\s+)?$", t[:h[0]])]          # « pas réservée à la région »
    if "quotas" in brut and (reg_hits
                             or (res["territoire"] != "FR" and re.search(r"(?<![a-z])(?<!pas )(?:seulement|uniquement|exclusivement)(?![a-z])", t))):
        brut["quotas_region"] = 1
        if res["territoire"] == "FR":
            res["avertissements"].append("Quotas « seulement dans la région » sans région ni département cité : le serveur refusera ce scénario.")

    # bornes
    lv = {}
    for k, v in brut.items():
        l = UI[k]
        if l["type"] != "range":
            lv[k] = v
            continue
        x, src = v
        x = round(round(x / l["step"]) * l["step"], 4) if l.get("step") else round(x, 4)   # au pas du levier
        if not l["min"] <= x <= l["max"]:
            b = min(max(x, l["min"]), l["max"])
            res["avertissements"].append(f"{l['label']} : {_fmt(l, x)} ramené à la borne {_fmt(l, b)}.")
            x = b
        lv[k] = x

    # validation finale par le serveur
    q = {k: str(v) for k, v in lv.items()}
    valide, err = S.parse_levers(q)
    if err:
        res["avertissements"].append(f"refusé par parse_levers : {err}")
        lv, valide = {}, S.parse_levers({})[0]
    res["leviers"] = lv
    res["leviers_valides"] = valide

    # ce qui a été compris
    for k, v in lv.items():
        l = UI[k]
        if l["type"] == "toggle":
            res["compris"].append(f"{l['label']} : activé ({l['famille']}).")
        elif l["type"] == "select":
            res["compris"].append(f"{l['label']} {l['options'][v]}.")
        else:
            res["compris"].append(f"{l['label']} : {_fmt(l, v)} ({l['famille']}, effet {l['delai']}).")
    if res["profession"]:
        res["compris"].append(f"Profession : {S.PROFS[res['profession']]} (secteur libéral).")
    else:
        res["avertissements"].append("Aucune profession reconnue : à choisir.")
    res["compris"].append(f"Territoire : {res['territoire']}.")
    if not lv:
        res["compris"].append("Aucun levier réglé : projection tendancielle.")
    return res


if __name__ == "__main__":
    print(json.dumps(compile(" ".join(sys.argv[1:])), ensure_ascii=False, indent=2))
