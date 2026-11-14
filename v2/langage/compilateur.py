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


def _direction(c: str) -> str | None:
    D = glossaire()["directions"]
    hits = [(s, "hausse") for s, _, _ in _find(c, D["hausse"])] + [(s, "baisse") for s, _, _ in _find(c, D["baisse"])]
    if re.search(r"(?:^|\s)\+\s*\d", c):
        hits.append((c.index("+"), "hausse"))
    if re.search(r"(?:^|\s)-\s*\d", c):
        hits.append((c.index("-"), "baisse"))
    return min(hits)[1] if hits else None


def quantite(c: str) -> dict | None:
    """Une quantité dans une proposition : {'type': 'facteur'|'pct'|'ans', 'v': float, 'brut': str}."""
    D = glossaire()["directions"]
    mots = "|".join(glossaire()["nombres"])
    # pourcentages
    m = re.search(rf"{NUM}\s*(?:%|pour ?cent|points?\b)", c)
    if m:
        p = _nombre(m.group(1))
        d = _direction(c)
        if d is None:
            return {"type": "pct_sans_sens", "v": p, "brut": m.group(0)}
        return {"type": "facteur", "v": 1 + p / 100 if d == "hausse" else 1 - p / 100, "brut": m.group(0) + f" ({d})"}
    # années / mois
    m = re.search(rf"(?<![a-z0-9])({NUM[1:-1]}|{mots})\s*(ans?|annees?|mois)(?![a-z])", c)
    if m:
        n = _nombre(m.group(1))
        if n is not None:
            v = n / 12 if m.group(2) == "mois" else n
            d = _direction(c)
            return {"type": "ans", "v": -v if d == "baisse" else v, "brut": m.group(0)}
    # multiplicateurs « x 1,5 », « 1,5 fois »
    m = re.search(rf"(?:(?<![a-z])x|×)\s*{NUM}|{NUM}\s*fois", c)
    if m:
        return {"type": "facteur", "v": _nombre(m.group(1) or m.group(2)), "brut": m.group(0)}
    # formules
    f = _find(c, D["facteurs"])
    if f:
        terme = f[0][2]
        v = float(D["facteurs"][terme])
        if terme == "de moitie" and _direction(c) == "hausse":
            v = 1.5
        return {"type": "facteur", "v": v, "brut": terme}
    return None


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

    # profession
    profs = detecter_profession(t)
    if profs:
        res["profession"] = profs[0]
        if len(profs) > 1:
            res["avertissements"].append(
                f"Plusieurs professions citées ({', '.join(profs)}) : le scénario porte sur une seule ; "
                f"« {profs[0]} » retenue, relancer pour les autres.")
    elif profession:
        res["profession"] = profession
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
    clauses = [c.strip() for c in re.split(r"(?<!\d)[,.](?!\d)|(?<=\d)[,.](?!\d)|[;:?!]|\s(?:et|puis|ainsi que|mais)\s", t) if c.strip()]
    for c in clauses:
        hits = _find(c, all_terms)
        reste = c
        for s, e, _ in sorted(hits, reverse=True):
            reste = reste[:s] + " " * (e - s) + reste[e:]
        q = quantite(reste)
        leviers_c = list(dict.fromkeys(all_terms[h[2]] for h in hits))
        if not leviers_c and q and en_attente:
            leviers_c, en_attente = [en_attente], None
        if _find(c, G["directions"]["plafonner"]) and not q:
            res["non_compris"].append(f"{c} (plafonnement sans valeur chiffrée : non traduit)")
            continue
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
        m = re.search(rf"{NUM}\s*(?:%|pour ?cent)\s*des zones", t)
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
    if "quotas" in brut and _find(t, G["leviers"]["quotas_region"]["termes"]):
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
        x = round(x, 4)
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
