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


# ------------------------------------------------------------------ qualificatifs (vocabulaire de v2/docs/lab/lexicon.md)
# Les mots de grandeur sont calculés par la passerelle ; la réponse ne peut employer que ceux des résultats reçus.
_VOCAB = sorted([
    "nettement inférieure à la moyenne nationale", "inférieure à la moyenne nationale", "proche de la moyenne nationale",
    "nettement supérieure à la moyenne nationale", "supérieure à la moyenne nationale",
    "forte hausse", "forte baisse", "hausse marquée", "baisse marquée", "légère hausse", "légère baisse", "stable",
    "incertitude faible", "incertitude modérée", "incertitude élevée", "court terme", "moyen terme", "long terme",
], key=len, reverse=True)
_HORS_VOCAB = re.compile(r"\b(modestes?|significati(?:f|ve|fs|ves)|considérables?|spectaculaires?|massi(?:f|ve|fs|ves)|"
                         r"sensibles?|sensiblement|nettes? (?:hausse|baisse)s?|importantes? (?:hausse|baisse)s?|"
                         r"faibles? (?:hausse|baisse)s?)\b", re.I)


def qualificatifs(objet) -> set[str]:
    """Tous les qualificatifs (champs « qualificatifs » et « delai_qualificatif ») d'un résultat de la passerelle."""
    out: set[str] = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "qualificatifs" and isinstance(v, dict):
                    out.update(str(t).replace(" (extrapolée)", "") for t in v.values() if t)
                elif k == "delai_qualificatif" and v:
                    out.add(str(v))
                else:
                    walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    walk(objet)
    return out


def qualifs_non_rattaches(texte: str, permis: set[str]) -> list[str]:
    """Qualificatifs du vocabulaire absents des résultats reçus, et adjectifs de grandeur hors vocabulaire."""
    t, out = (texte or "").lower(), []
    for mot in _VOCAB:                      # du plus long au plus court : « nettement inférieure… » avant « inférieure… »
        if mot in t:
            if mot not in permis:
                out.append(f"« {mot} »")
            t = t.replace(mot, " ")
    out += [f"« {m.group(0)} » (hors vocabulaire)" for m in _HORS_VOCAB.finditer(t)]
    return list(dict.fromkeys(out))
