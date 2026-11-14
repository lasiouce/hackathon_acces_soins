"""Gabarits de phrases pour l'élu·e, remplis à partir d'une réponse de /api/scenario (Model.answer).

Aucun nombre n'est calculé hors de la réponse, sauf l'arrondi d'affichage et la fourchette, qui
reprend exactement la règle de v2/prototype/index.html : scn × (1 ± k × (année − origine)).
Le vocabulaire suit docs/lab/lexicon.md : « projection », fourchette, pas de jugement.
"""
from __future__ import annotations

import math

NOMS_PROF = {"sages-femmes": ("sage-femme libérale", "sages-femmes libérales"),
             "dentistes": ("chirurgien-dentiste libéral", "chirurgiens-dentistes libéraux"),
             "pharmaciens": ("pharmacien libéral", "pharmaciens libéraux"),
             "kines": ("kiné libéral", "kinés libéraux"),
             "infirmiers": ("infirmier libéral", "infirmiers libéraux")}


def arrondi(x: float, chiffres: int = 3) -> int:
    """Arrondi lisible : `chiffres` chiffres significatifs (1 929,7 -> 1 930 ; 2 473 -> 2 500 avec 2)."""
    if x <= 0:
        return 0
    p = max(int(math.floor(math.log10(x))) - chiffres + 1, 0)
    return int(round(x, -p))


def nombre(x: float, chiffres: int = 3) -> str:
    return f"{arrondi(x, chiffres):,}".replace(",", " ")


def nom_territoire(terr: str) -> str:
    """« dans le Puy-de-Dôme », « en Auvergne-Rhône-Alpes », « en France » (noms lus dans le serveur)."""
    if terr in (None, "", "FR"):
        return "en France"
    from compilateur import serveur  # import tardif : charge le jumeau
    S = serveur()
    if terr.startswith("R"):
        return f"en {S.REGIONS.get(terr[1:], terr)}"
    nom = S.geo().loc[terr[1:], "dep_name"]
    article = "l’" if nom[0] in "AEIOUYÉÈ" else "le "
    return f"dans {article}{nom}"


def fourchette(r: dict, annee: int) -> tuple[float, float, float]:
    j = r["years"].index(annee)
    v = r["scn"][j]
    h = annee - r["origin"]
    return v, v * (1 - r["k"] * h), v * (1 + r["k"] * h)


def phrase_niveau(r: dict, terr: str = "FR", annee: int | None = None, lieu: str | None = None) -> str:
    annee = annee or r["years"][-1]
    v, lo, hi = fourchette(r, annee)
    nom = NOMS_PROF.get(r["prof"], (r["label"], r["label"]))[1]
    lieu = lieu or nom_territoire(terr)
    return (f"En {annee}, environ {nombre(v)} {nom} {lieu}, probablement entre "
            f"{nombre(lo, 2)} et {nombre(hi, 2)}.")


def phrase_ecart(r: dict, annee: int | None = None) -> str:
    annee = annee or r["years"][-1]
    j = r["years"].index(annee)
    g = r["scn"][j] - r["base"][j]
    if abs(g) < 0.5:
        return f"En {annee}, le scénario ne change pas l'effectif projeté par rapport à la tendance."
    sens = "de plus" if g > 0 else "de moins"
    return (f"Par rapport à la tendance, le scénario conduit à environ {nombre(abs(g), 2)} professionnels "
            f"{sens} en {annee} ({nombre(r['base'][j])} sans le scénario).")


def phrase_delai(r: dict) -> str:
    """Délai d'effet : first_effect de la réponse ; on vérifie dans la série que rien ne bouge avant."""
    j0 = next((j for j, (b, s) in enumerate(zip(r["base"], r["scn"])) if abs(s - b) >= 0.5), None)
    if j0 is None:
        return "Aucun effet visible sur la période projetée."
    an = r["years"][j0]
    if an >= r["first_effect"] and an > r["decision"] + 1:
        return f"Rien ne change avant {an}, le temps de former les étudiants."
    return f"L'effet commence dès {an}."


def phrase_complete(r: dict, terr: str = "FR", annee: int | None = None, lieu: str | None = None) -> str:
    """Exemple : « En 2050, environ 1 930 kinés libéraux dans le Puy-de-Dôme, probablement entre 1 400 et
    2 500 ; rien ne change avant 2032, le temps de former les étudiants. »"""
    base = phrase_niveau(r, terr, annee, lieu).rstrip(".")
    d = phrase_delai(r)
    return f"{base} ; {d[0].lower()}{d[1:]}"


def phrases(r: dict, terr: str = "FR", annee: int | None = None, lieu: str | None = None) -> list[str]:
    return [phrase_complete(r, terr, annee, lieu), phrase_ecart(r, annee),
            "Projection sous hypothèses : la fourchette reprend l'erreur passée du modèle, extrapolée au-delà "
            "de l'horizon testé."]


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from compilateur import compile, serveur
    texte = " ".join(sys.argv[1:]) or "Augmenter de 20 % le numerus apertus des kinés dans le Puy-de-Dôme"
    c = compile(texte)
    S = serveur()
    r = S.model(c["profession"] or "kines").answer(c["leviers_valides"], c["territoire"])
    print("\n".join(c["compris"]))
    print("\n".join(phrases(r, c["territoire"])))
