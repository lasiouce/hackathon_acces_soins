"""Vérification automatique : chaque nombre d'une réponse doit venir d'un résultat du modèle (ou de la question).

Un nombre est « rattaché » s'il est proche (écart relatif ≤ TOLERANCE, pour l'arrondi « environ 1 900 » de 1 930)
d'un nombre présent dans :
  - un résultat de la passerelle reçu dans la conversation (valeurs ET nombres écrits dans les textes, ex. sources) ;
  - les arguments envoyés à la passerelle, et les messages de l'utilisateur·rice ;
  - ou s'il est une année de la plage du modèle (2012 à 2050), ou un petit entier (≤ 10 : listes, « 2 ans »).
Un multiplicateur m (0,3 à 3) rattache aussi le pourcentage équivalent (1,2 -> 20 % et 120 %).
"""
from __future__ import annotations

import re

TOLERANCE = 0.06
ANNEES = (2012, 2050)
PETIT = 10

# « 1 930 », « 161 000 », « 1,5 », « -18,2 », « 0.72 » ; espaces fines et insécables acceptées comme séparateur de milliers
_NB = re.compile(r"(?<![\w.,])[-+−]?\d{1,3}(?:[   ]\d{3})+(?:[.,]\d+)?(?![\d])|(?<![\w.,])[-+−]?\d+(?:[.,]\d+)?(?![\d])")


def nombres(texte: str) -> list[tuple[float, str]]:
    out = []
    for m in _NB.finditer(texte or ""):
        brut = m.group(0)
        s = re.sub(r"[   ]", "", brut).replace("−", "-").replace(",", ".")
        try:
            out.append((float(s), brut.strip()))
        except ValueError:
            pass
    return out


def references(*objets) -> set[float]:
    """Tous les nombres contenus dans des objets JSON (valeurs et textes) et des chaînes."""
    refs: set[float] = set()

    def walk(x):
        if isinstance(x, bool) or x is None:
            return
        if isinstance(x, (int, float)):
            refs.add(float(x))
        elif isinstance(x, str):
            refs.update(v for v, _ in nombres(x))
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(k)
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    for o in objets:
        walk(o)
    for r in list(refs):
        if 0.3 <= r <= 3:
            refs.update({round((r - 1) * 100, 6), round(r * 100, 6)})
    return refs


def rattache(n: float, refs: set[float]) -> bool:
    a = abs(n)
    if float(a).is_integer() and (a <= PETIT or ANNEES[0] <= a <= ANNEES[1]):
        return True
    for r in refs:
        r = abs(r)
        if r == 0:
            if a == 0:
                return True
        elif abs(a - r) / r <= TOLERANCE:
            return True
    return False


def non_rattaches(texte: str, refs: set[float]) -> list[str]:
    """Nombres du texte qu'aucune référence n'explique (dans l'ordre, sans doublon)."""
    vus, out = set(), []
    for v, brut in nombres(texte):
        if not rattache(v, refs) and brut not in vus:
            vus.add(brut)
            out.append(brut)
    return out
