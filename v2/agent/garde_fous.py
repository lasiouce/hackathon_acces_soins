"""Garde-fous mesurés de l'agent : ancrage des nombres et lexique neutre.

Ancrage : chaque nombre écrit dans la réponse doit se retrouver dans une sortie d'outil de la conversation (ou dans la
question, ou dans le contexte de la carte), à la précision affichée : 13 240 ancre « 13 240 », « 13 200 » (arrondi à la
centaine) et « 13 mille » non ; 3,24 ancre « 3,2 ». Le signe est ignoré (« −524 » et « 524 »).
Lexique : termes de jugement de v2/docs/lab/lexicon.md (colonne « Avoid ») ; décrire et comparer, jamais juger.
"""
import json
import re

# 13 240 / 13 240,5 / 1,2 / 2035 / 0.5 ; espaces fines et insécables acceptées entre groupes de trois chiffres
NB = re.compile(r"(?<![\w.,])(\d{1,3}(?:[   ]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?)(?![\d])")
LISTE = re.compile(r"^\s*\d+[.)]\s", re.M)


def nombres(texte: str) -> list[tuple[str, float, int]]:
    """(forme écrite, valeur, nombre de décimales) de chaque nombre du texte, numéros de liste exclus."""
    texte = LISTE.sub(" ", texte)
    out = []
    for m in NB.finditer(texte):
        s = m.group(1)
        t = re.sub(r"[   ]", "", s).replace(",", ".")
        dec = len(t.split(".")[1]) if "." in t else 0
        out.append((s, float(t), dec))
    return out


def _sources(objs) -> set[float]:
    vals: set[float] = set()

    def walk(o):
        if isinstance(o, bool) or o is None:
            return
        if isinstance(o, (int, float)):
            vals.add(abs(float(o)))
        elif isinstance(o, str):
            vals.update(v for _, v, _ in nombres(o))
        elif isinstance(o, dict):
            for k, v in o.items():
                walk(k)
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
    walk(objs)
    return vals


def _ancre(v: float, dec: int, src: set[float]) -> bool:
    tol = 0.5 * 10 ** -dec + 1e-9
    if any(abs(s - v) <= tol for s in src):
        return True
    if dec == 0 and v >= 100:          # arrondi à la dizaine, à la centaine, au millier : « environ 13 200 »
        for z in (1, 2, 3):
            if v % 10 ** z == 0 and any(abs(s - v) <= 0.5 * 10 ** z for s in src if s >= 10 ** z):
                return True
    return False


def ancrage(reponse: str, sorties: list, question: str = "", contexte=None) -> dict:
    src = _sources([sorties, question, contexte])
    ns = nombres(reponse)
    non = [s for s, v, d in ns if not _ancre(v, d, src)]
    return {"nombres": len(ns), "non_ancres": non, "ok": not non}


INTERDITS = [
    r"d[ée]serts?", r"m[ée]diocres?", r"mauvais(?:es?)?", r"p[ée]nuries?", r"manques?", r"sur-?dot[ée]e?s?", r"trop de",
    r"catastroph\w*", r"critiques?", r"alarm\w*", r"abandonn[ée]e?s", r"oubli[ée]e?s", r"bons? [ée]l[èe]ves?",
    r"[ée]checs?", r"il faut", r"on doit", r"pr[ée]visions?", r"va arriver",
]
_LEX = re.compile(r"(?<!\w)(" + "|".join(INTERDITS) + r")(?!\w)", re.I)


def lexique(reponse: str) -> dict:
    hits = sorted({m.group(0).lower() for m in _LEX.finditer(reponse)})
    return {"termes": hits, "ok": not hits}


if __name__ == "__main__":
    out = [{"x": 13239.96, "pct": 3.2, "t": "8 cas sur 10"}]
    r = "Environ 13 240 kinés (13 200), +3,2 %, 8 cas sur 10.\n1. premier point\nmais 999 inventé"
    print(json.dumps(ancrage(r, out), ensure_ascii=False))
    print(lexique("Ce n'est pas un désert médical ; il faut former. Les abandons en formation."))
