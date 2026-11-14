"""Requêtes en LECTURE SEULE sur le jumeau numérique (dépôt hackathon_acces_soins, épinglé en sous-module).

C'est le SEUL module du dépôt qui importe le code du modèle. Il ne fait qu'appeler `Model.answer` et lire des
fichiers de résultats ; il n'écrit rien, n'exécute rien d'autre, et n'expose ni chemin ni attribut arbitraire.
Le processus du chatbot n'importe jamais ce module : il passe par passerelle/server.py (HTTP, GET seulement).

Chemin du modèle : variable JUMEAU_REPO (défaut : vendor/hackathon_acces_soins).
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

REPO = Path(os.environ.get("JUMEAU_REPO", Path(__file__).resolve().parents[1] / "vendor" / "hackathon_acces_soins")).resolve()
V2 = REPO / "v2"


def version_modele() -> dict:
    """Commit du modèle et état « modifié / propre » : chaque réponse est rattachée à une version exacte."""
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, timeout=5).stdout.strip()
        sale = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO, capture_output=True,
                              text=True, timeout=5).stdout.strip()
    except Exception:
        sha, sale = "", ""
    return {"commit": sha[:12] or "?", "code_modifie_localement": bool(sale), "chemin": str(REPO.name)}


@lru_cache(maxsize=1)
def S():
    """Serveur du prototype V1 importé sans le lancer (fait le chdir vers la racine du dépôt)."""
    spec = importlib.util.spec_from_file_location("proto_v1", V2 / "prototype" / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@lru_cache(maxsize=1)
def NL():
    """Compilateur déterministe de v2/langage, branché sur le même module serveur (pas de second jumeau)."""
    spec = importlib.util.spec_from_file_location("compilateur", V2 / "langage" / "compilateur.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.serveur = S
    return mod


@lru_cache(maxsize=1)
def PH():
    sys.modules.setdefault("compilateur", NL())   # phrases.py fait « from compilateur import serveur » : même instance
    spec = importlib.util.spec_from_file_location("phrases", V2 / "langage" / "phrases.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ErreurOutil(ValueError):
    """Erreur renvoyée au modèle de langage (tool_result is_error) pour qu'il corrige son appel."""


# ------------------------------------------------------------------ résolution des entrées

def profession(p: str) -> str:
    srv = S()
    if p in srv.PROFS:
        return p
    found = NL().detecter_profession(NL().norm(p))
    if found:
        return found[0]
    raise ErreurOutil(f"profession inconnue {p!r} ; valeurs : {', '.join(srv.PROFS)} "
                      "(la médecine générale et les spécialistes sont hors périmètre de la phase 1)")


def territoire(t: str | None) -> str:
    """Code serveur (FR, R84, D63) à partir d'un code ou d'un nom (région, département, ville du glossaire, sigle)."""
    srv = S()
    t = (t or "FR").strip()
    g = srv.geo()
    if t == "FR" or (t[:1] == "R" and t[1:] in srv.REGIONS) or (t[:1] == "D" and t[1:] in g.index):
        return t
    if t in g.index:                       # « 63 »
        return "D" + t
    n = NL().norm(t)
    for forme, code, _ in NL()._territoires():
        if forme == n:
            return code
    found, _ = NL().detecter_territoire(n)
    if found:
        return found[0][1]
    cand = [nom for nom in list(srv.REGIONS.values()) + list(g.dep_name) if n[:4] in NL().norm(str(nom))][:6]
    raise ErreurOutil(f"territoire non reconnu {t!r}" + (f" ; voulez-vous dire : {', '.join(cand)} ?" if cand else
                      " ; donner une région, un département (nom ou numéro) ou « France »"))


def nom_territoire(code: str) -> str:
    srv = S()
    if code == "FR":
        return "France"
    if code.startswith("R"):
        return srv.REGIONS.get(code[1:], code)
    return str(srv.geo().loc[code[1:], "dep_name"])


def leviers(lv: dict | None) -> dict:
    """Réglage validé par parse_levers (mêmes bornes que l'écran de décision) ; erreur explicite sinon."""
    srv = S()
    lv = lv or {}
    inconnus = set(lv) - set(srv.UI)
    if inconnus:
        raise ErreurOutil(f"leviers inconnus : {sorted(inconnus)} ; leviers disponibles : {sorted(srv.UI)}")
    q = {k: ("1" if v is True else "0" if v is False else str(v)) for k, v in lv.items()}
    out, err = srv.parse_levers(q)
    if err:
        raise ErreurOutil(err)
    return out


def _fmt_levier(k: str, v) -> str:
    l = S().UI[k]
    if l["type"] == "toggle":
        return f"{l['label']} : {'oui' if v else 'non'}"
    if l["type"] == "select":
        return f"{l['label']} : {l['options'][v]}"
    f = l.get("fmt")
    s = {"pct": f"{(v - 1) * 100:+.0f} %", "pct0": f"{v * 100:.0f} %", "x": f"× {v:g}", "ans": f"+{v:g} an(s)"}.get(f, f"{v:g}")
    s = s.replace(".", ",")                    # décimales à la française
    return f"{l['label']} : {s}"


def resume_leviers(lv: dict) -> list[str]:
    d = {l["k"]: l["default"] for l in S().LEVIERS_UI}
    return [_fmt_levier(k, v) for k, v in lv.items() if v != d[k] and not (isinstance(d[k], int) and bool(v) == bool(d[k]) and S().UI[k]["type"] == "toggle")]


# ------------------------------------------------------------------ calcul (toujours le jumeau)

_CACHE: dict = {}


def _answer(prof: str, lv: dict, terr: str) -> dict:
    key = (prof, terr, json.dumps(lv, sort_keys=True))
    if key not in _CACHE:
        _CACHE[key] = S().model(prof).answer(lv, terr)
        if len(_CACHE) > 256:
            _CACHE.pop(next(iter(_CACHE)))
    return _CACHE[key]


def _annees(annees, r) -> list[int]:
    ys = sorted({int(a) for a in (annees or [2030, 2035, 2040, 2050])})
    bad = [a for a in ys if a < r["origin"] or a > S().H]
    if bad:
        raise ErreurOutil(f"années hors de la projection [{r['origin']} ; {S().H}] : {bad}")
    return ys


def _ligne(r: dict, y: int) -> dict:
    i = r["years"].index(y)
    v, lo, hi = PH().fourchette(r, y)
    b = r["base"][i]
    return {"annee": y, "tendanciel": round(b), "scenario": round(r["scn"][i]),
            "ecart": round(r["scn"][i] - b), "ecart_pct": round((r["scn"][i] / b - 1) * 100, 2) if b else None,
            "fourchette_scenario": [round(lo), round(hi)],
            "densite_100k_tendanciel": _r1(r["dens_base"][i]), "densite_100k_scenario": _r1(r["dens_scn"][i]),
            "population": round(r["pop"][i]) if r["pop"][i] == r["pop"][i] else None}


def _r1(x):
    return None if x is None or x != x else round(x, 1)


def _provenance(lv: dict) -> list[dict]:
    meta = {m["k"]: m for m in S().lever_meta()}
    d = {l["k"]: l["default"] for l in S().LEVIERS_UI}
    return [{"levier": k, "reglage": _fmt_levier(k, v), "statut": meta[k]["status"], "source": meta[k]["source"],
             "delai": meta[k]["delai"]} for k, v in lv.items() if v != d[k]]


PERIMETRE = ("Effectif « libéral » = secteur privé (lucratif ou non), tout employeur public exclu. Grain : département. "
             "Projection sous hypothèses, pas une prévision ; aucun backtest au-delà d'environ 10 ans.")


def projeter(profession_: str, territoire_: str = "FR", leviers_: dict | None = None, annees: list[int] | None = None) -> dict:
    p, t, lv = profession(profession_), territoire(territoire_), leviers(leviers_)
    t0 = time.perf_counter()
    r = _answer(p, lv, t)
    ys = _annees(annees, r)
    flux = {f: round(v[r["years"].index(ys[-1])]) for f, v in r["flows"].items()}
    extra = {}
    if lv["regul"]:
        g, zs = S().geo(), r["regul_deps"]
        deps = [t[1:]] if t.startswith("D") else list(g.index[g.region == t[1:]]) if t.startswith("R") else list(g.index)
        n = int(round(lv["part_zones"] * len(zs)))
        extra["regulation"] = {"departements_regules_dans_territoire": [str(g.loc[d, "dep_name"]) for d in zs[:n] if d in deps],
                               "regle": "un département est régulé si ≥ 50 % de ses communes sont en « remplacement seul » "
                                        "(zonage actuel) ; ailleurs la régulation est sans effet au grain départemental"}
    return {
        "profession": r["label"], "territoire": nom_territoire(t), "code_territoire": t,
        "origine": r["origin"], "observe_origine": round(r["base"][0]),
        "leviers": resume_leviers(lv) or ["aucun levier : scénario tendanciel"],
        "premier_effet": r["first_effect"] if lv["quotas"] != 1 else None,
        "annees": [_ligne(r, y) for y in ys],
        f"ecart_par_flux_cumule_{ys[-1]}": flux,
        "provenance_leviers": _provenance(lv), **extra,
        "fourchette_methode": f"scénario × (1 ± {r['k']:.4f} × années depuis {r['origin']}) : erreur de backtest extrapolée, ~8 cas sur 10",
        "perimetre": PERIMETRE, "calcul_ms": round((time.perf_counter() - t0) * 1000, 1),
        "_serie": {"annees": r["years"], "tendanciel": r["base"], "scenario": r["scn"], "k": r["k"],
                   "origine": r["origin"], "observe": r["obs"]},
    }


def comparer(profession_: str, territoire_: str, scenarios: list[dict], annee: int = 2050) -> dict:
    if not scenarios or len(scenarios) > 6:
        raise ErreurOutil("donner de 1 à 6 scénarios")
    p, t = profession(profession_), territoire(territoire_)
    rows, series = [], []
    for s in scenarios:
        lv = leviers(s.get("leviers"))
        r = _answer(p, lv, t)
        ys = _annees([annee], r)
        rows.append({"nom": s.get("nom") or ", ".join(resume_leviers(lv)) or "tendanciel",
                     "leviers": resume_leviers(lv), **_ligne(r, ys[0])})
        series.append({"nom": rows[-1]["nom"], "annees": r["years"], "valeurs": r["scn"]})
    return {"profession": S().PROFS[p], "territoire": nom_territoire(t), "annee": annee, "scenarios": rows,
            "perimetre": PERIMETRE, "_series": {"tendanciel": {"annees": r["years"], "valeurs": r["base"]}, "scenarios": series}}


def balayer(profession_: str, territoire_: str, levier: str, valeurs: list, annee: int = 2050,
            autres_leviers: dict | None = None) -> dict:
    p, t = profession(profession_), territoire(territoire_)
    if levier not in S().UI or S().UI[levier]["type"] not in ("range", "toggle", "select"):
        raise ErreurOutil(f"levier inconnu {levier!r}")
    if not valeurs or len(valeurs) > 9:
        raise ErreurOutil("donner de 1 à 9 valeurs")
    out = []
    for v in valeurs:
        lv = leviers({**(autres_leviers or {}), levier: v})
        r = _answer(p, lv, t)
        out.append({"valeur": v, "reglage": _fmt_levier(levier, lv[levier]), **_ligne(r, _annees([annee], r)[0])})
    return {"profession": S().PROFS[p], "territoire": nom_territoire(t), "levier": S().UI[levier]["label"],
            "annee": annee, "points": out, "perimetre": PERIMETRE}


def classer(profession_: str, region: str | None = None, leviers_: dict | None = None, annee: int = 2050,
            critere: str = "densite_100k_scenario", n: int = 10, ordre: str = "croissant") -> dict:
    """Départements d'une région (ou de France) classés ; densités Insee Omphale (scénario choisi)."""
    srv, p, lv = S(), profession(profession_), leviers(leviers_)
    g = srv.geo()
    terr = territoire(region) if region else "FR"
    if terr.startswith("D"):
        terr = "R" + g.loc[terr[1:], "region"]
    deps = list(g.index) if terr == "FR" else list(g.index[g.region == terr[1:]])
    rows = []
    for d in deps:
        try:
            r = _answer(p, lv, "D" + d)
        except Exception:
            continue
        if annee not in r["years"]:
            raise ErreurOutil(f"année hors projection : {annee}")
        x = _ligne(r, annee)
        x["evolution_pct_depuis_origine"] = round((x["scenario"] / r["base"][0] - 1) * 100, 1) if r["base"][0] else None
        rows.append({"departement": str(g.loc[d, "dep_name"]), "code": d, **x})
    if critere not in ("densite_100k_scenario", "ecart_pct", "evolution_pct_depuis_origine", "scenario"):
        raise ErreurOutil("critère : densite_100k_scenario, ecart_pct, evolution_pct_depuis_origine ou scenario")
    rows = [r for r in rows if r.get(critere) is not None]
    rows.sort(key=lambda r: r[critere], reverse=(ordre == "decroissant"))
    return {"profession": srv.PROFS[p], "perimetre_classement": nom_territoire(terr), "annee": annee, "critere": critere,
            "leviers": resume_leviers(lv) or ["tendanciel"], "nb_departements": len(rows), "departements": rows[:max(1, min(n, 30))],
            "moyenne_densite_scenario": _r1(float(np.mean([r["densite_100k_scenario"] for r in rows if r["densite_100k_scenario"]]))) if rows else None,
            "perimetre": PERIMETRE}


def decrire_leviers() -> dict:  # noqa: D103
    G = NL().glossaire()
    return {"leviers": [{k: m.get(k) for k in ("k", "famille", "label", "type", "min", "max", "step", "default", "options",
                                                 "delai", "status", "source", "unit")} for m in S().lever_meta()],
            "non_modelise": [{"id": k, "libelle": v["libelle"], "raison": v["raison"]} for k, v in G["non_modelises"].items()],
            "professions": S().PROFS, "delai_formation_ans": S().LAG, "annee_decision": S().DECISION, "horizon": S().H}


@lru_cache(maxsize=1)
def _classement():
    f = V2 / "sensibilite" / "out" / "classement.csv"
    return list(csv.DictReader(f.open(encoding="utf-8"))) if f.exists() else []


def incertitude(profession_: str, annee: int = 2050) -> dict:
    p = profession(profession_)
    rows = [r for r in _classement() if r["profession"] == p and int(r["annee"]) == int(annee)]
    if not rows:
        raise ErreurOutil(f"pas d'indice de Sobol pour {p} en {annee} (années : 2030, 2040, 2050)")
    fam = {}
    for r in rows:
        fam.setdefault(r["famille"], []).append({"facteur": r["facteur"], "ST": round(float(r["ST"]), 2),
                                                  "ST_IC95": [round(float(r["ST_lo"]), 2), round(float(r["ST_hi"]), 2)],
                                                  "mu_star_pct": round(float(r["mu_star_pct"]), 1)})
    for v in fam.values():
        v.sort(key=lambda x: -x["ST"])
    return {"profession": S().PROFS[p], "annee": annee, "methode": "Morris puis Sobol (axe 5), sortie nationale, secteur privé",
            "familles": {"incertitude": "choix d'estimation et données (hors leviers)", "tout": "facteurs + leviers"},
            "indices": {k: v[:6] for k, v in fam.items()}}


def interpreter(texte: str) -> dict:
    r = NL().compile(texte)
    return {k: r[k] for k in ("leviers", "profession", "territoire", "compris", "non_modelise", "non_compris",
                               "avertissements", "reformulations")}




# Ce que le modèle ne sait PAS faire, d'après sa documentation (synthèse du 2026-11-14, README, ROADMAP).
# Le glossaire du modèle (non_modelises) complète cette liste pour les politiques publiques.
HORS_PERIMETRE = [
    {"id": "medecins", "sujet": "Médecins généralistes et médecins spécialistes",
     "raison": "Médecine générale hors périmètre ; spécialités (cardiologie, dermatologie, ophtalmologie) prévues en phase 2, non construites."},
    {"id": "autres_professions", "sujet": "Autres professions (orthophonistes, aides-soignants, psychologues…)",
     "raison": "Le modèle couvre cinq professions seulement."},
    {"id": "secteur_public", "sujet": "Effectifs salariés du public (hôpital public, PMI, centres de santé municipaux…)",
     "raison": "La sortie est l'effectif « libéral » au sens du secteur privé ; le public n'est pas une sortie publiée."},
    {"id": "commune", "sujet": "Projection à la commune, au quartier, à l'EPCI ou au bassin de vie",
     "raison": "Le grain servi est le département ; une ville est ramenée à son département. La commune est en cours (≈ 6,8 s par scénario)."},
    {"id": "horizon", "sujet": "Années après 2050 ; passé avant les données (2012)",
     "raison": "Projection de l'origine (2026 ; 2023 pour les infirmiers) à 2050 ; historique observé depuis 2012."},
    {"id": "besoin", "sujet": "Besoin ou demande de soins, délais d'attente, patients par professionnel, « combien en manque »",
     "raison": "Aucun module de besoin : le modèle projette l'offre (effectifs), pas la demande. Décision ouverte de l'équipe."},
    {"id": "activite_reelle", "sujet": "Temps de travail, équivalents temps plein, volume de soins",
     "raison": "L'activité par professionnel est une hypothèse supposée (curseur), pas une donnée mesurée."},
    {"id": "couts", "sujet": "Coûts, budget, rentabilité d'une politique",
     "raison": "Le modèle ne contient aucune donnée de coût."},
    {"id": "causalite", "sujet": "Causes (« pourquoi les kinés partent ») hors des leviers modélisés",
     "raison": "Le modèle décompose l'écart par flux (entrées, sorties, régulation) ; il n'estime pas les motivations individuelles."},
    {"id": "autres_pays", "sujet": "Autres pays", "raison": "France seulement (métropole et DROM)."},
    {"id": "prevision_exacte", "sujet": "Un chiffre exact, certain ou une prévision",
     "raison": "Projection sous hypothèses, toujours avec une fourchette ; aucun backtest au-delà d'environ 10 ans."},
    {"id": "jugement", "sujet": "Recommandation ou jugement de valeur (« la meilleure politique », « le pire département »)",
     "raison": "Le modèle décrit et compare ; le choix revient au décideur (lexique neutre du projet)."},
]


def perimetre() -> dict:
    G = NL().glossaire()
    srv = S()
    return {
        "couvert": {
            "professions": srv.PROFS,
            "sortie": "effectif « libéral » = secteur privé (lucratif ou non), tout employeur public exclu",
            "grain": "France, région, département",
            "annees": {"historique_observe": "2012 à l'origine", "projection": f"origine (2026 ; infirmiers 2023) à {srv.H}"},
            "questions": ["effectif projeté et sa fourchette", "effet d'un ou plusieurs leviers (écart au tendanciel, par flux)",
                          "comparaison de scénarios", "sensibilité d'un levier sur une plage", "classement de départements (densité, écart, évolution)",
                          "paramètres qui pèsent le plus sur l'incertitude (Sobol)", "délai d'effet et niveau de preuve des leviers"],
            "leviers": [m["label"] for m in srv.LEVIERS_UI],
        },
        "hors_perimetre": HORS_PERIMETRE,
        "politiques_non_modelisees": [{"id": k, "libelle": v["libelle"], "raison": v["raison"]} for k, v in G["non_modelises"].items()],
        "version_modele": version_modele(),
    }


# ------------------------------------------------------------------ objectif -> leviers (problème inverse)

# Leviers de politique testés, dans le sens qui augmente l'effectif, sur la grille de pas du modèle (LEVIERS_UI).
# Exclus : activite et pop_scen (hypothèses de contexte, pas des politiques) ; regul (ne peut que déplacer ou retirer).
_GRILLES = [("quotas", {}, [round(1 + 0.05 * i, 2) for i in range(1, 11)]),
            ("quotas", {"quotas_region": True}, [round(1 + 0.05 * i, 2) for i in range(1, 11)]),
            ("etrangers", {}, [round(1 + 0.1 * i, 1) for i in range(1, 11)]),
            ("retraite", {}, [0.5 * i for i in range(1, 7)]),
            ("cumul", {}, [round(1 + 0.1 * i, 1) for i in range(1, 11)]),
            ("precoces", {}, [round(1 - 0.1 * i, 1) for i in range(1, 6)])]
_MAX = {"quotas": 1.5, "etrangers": 2.0, "retraite": 3.0, "cumul": 2.0, "precoces": 0.5}


def atteindre(profession_: str, territoire_: str, hausse_pct: float, annee: int = 2050, grandeur: str = "densite",
              reference: str = "tendanciel") -> dict:
    """Pour atteindre +hausse_pct % de `grandeur` en `annee` (par rapport au tendanciel de la même année, ou à
    l'origine), quelle valeur de chaque levier faut-il, seul, dans ses bornes ? Et tous les leviers au maximum ?
    Recherche par dichotomie sur la grille de pas de chaque levier (effet supposé monotone, vérifié aux extrémités)."""
    p, t = profession(profession_), territoire(territoire_)
    cle = "densite_100k_scenario" if grandeur == "densite" else "scenario"
    base = _answer(p, leviers({}), t)
    y = _annees([annee], base)[0]
    lb = _ligne(base, y)
    ref = (lb[cle] if reference == "tendanciel" else
           (_r1(base["dens_base"][0]) if grandeur == "densite" else round(base["base"][0])))
    if ref is None:
        raise ErreurOutil("densité indisponible pour ce territoire (population manquante)")
    cible = ref * (1 + hausse_pct / 100)

    def valeur(lv):
        r = _answer(p, leviers(lv), t)
        return _ligne(r, y)

    out = []
    for k, extra, grille in _GRILLES:
        if extra.get("quotas_region") and t == "FR":
            continue
        suf = " (région seulement)" if extra else ""
        lab = S().UI[k]["label"] + suf
        haut = valeur({k: grille[-1], **extra})
        if haut[cle] < cible:
            out.append({"levier": lab, "suffit_seul": False, "valeur_max": _fmt_levier(k, grille[-1]) + suf,
                        "atteint_au_max": haut[cle], "ecart_a_la_cible_pct": round((haut[cle] / cible - 1) * 100, 1)})
            continue
        lo, hi, best = 0, len(grille) - 1, (grille[-1], haut)
        while lo <= hi:
            m = (lo + hi) // 2
            v = valeur({k: grille[m], **extra})
            if v[cle] >= cible:
                best, hi = (grille[m], v), m - 1
            else:
                lo = m + 1
        out.append({"levier": lab, "suffit_seul": True, "reglage_necessaire": _fmt_levier(k, best[0]) + suf,
                    "valeur_obtenue": best[1][cle], "fourchette_effectif": best[1]["fourchette_scenario"],
                    "delai": S().UI[k]["delai"]})
    tout = valeur(dict(_MAX))
    meta = {m["k"]: m for m in S().lever_meta()}
    return {
        "profession": S().PROFS[p], "territoire": nom_territoire(t), "annee": y,
        "objectif": f"+{hausse_pct:g} % de {'densité pour 100 000 habitants' if grandeur == 'densite' else 'effectif'} "
                    f"par rapport {'au tendanciel ' + str(y) if reference == 'tendanciel' else 'à ' + str(base['origin'])}",
        "reference": ref, "cible": round(cible, 1),
        "tendanciel_annee": {"effectif": lb["tendanciel"], "densite_100k": lb["densite_100k_tendanciel"]},
        "origine": {"annee": base["origin"], "effectif": round(base["base"][0]), "densite_100k": _r1(base["dens_base"][0])},
        "leviers_seuls": out,
        "tous_leviers_au_maximum": {"valeur": tout[cle], "atteint": tout[cle] >= cible,
                                    "reglage": resume_leviers(leviers(dict(_MAX)))},
        "statut_des_leviers": {meta[k]["label"]: meta[k]["status"] for k in _MAX},
        "methode": "chaque levier testé seul sur sa grille de pas, dans ses bornes ; aucune combinaison optimisée, "
                   "sauf « tous au maximum » ; densité à population Insee Omphale centrale et activité constante ; "
                   "seuls les leviers du modèle sont testés (d'autres politiques peuvent exister hors du modèle)",
        "perimetre": PERIMETRE,
    }
