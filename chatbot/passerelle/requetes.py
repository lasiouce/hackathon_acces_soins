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


# ------------------------------------------------------------------ vocabulaire des grandeurs (v2/docs/lab/lexicon.md)
# Un mot par plage, calculé ici et jamais par le modèle de langage ; seuils supposés, à changer avec lexicon.md.

def q_variation(pct: float | None) -> str | None:
    if pct is None:
        return None
    a, sens = abs(pct), ("hausse" if pct > 0 else "baisse")
    if a < 1:
        return "stable"
    return f"légère {sens}" if a < 5 else f"{sens} marquée" if a < 15 else f"forte {sens}"


def q_densite(pct: float | None) -> str | None:
    if pct is None:
        return None
    if pct < -25:
        return "nettement inférieure à la moyenne nationale"
    if pct < -10:
        return "inférieure à la moyenne nationale"
    if pct <= 10:
        return "proche de la moyenne nationale"
    return "supérieure à la moyenne nationale" if pct <= 25 else "nettement supérieure à la moyenne nationale"


def q_incertitude(demi_pct: float, horizon: int) -> str:
    m = "incertitude faible" if demi_pct < 5 else "incertitude modérée" if demi_pct <= 15 else "incertitude élevée"
    return m + (" (extrapolée)" if horizon > 10 else "")


def q_delai(ans: int) -> str:
    return "court terme" if ans < 3 else "moyen terme" if ans <= 6 else "long terme"


def _ligne(r: dict, y: int, dens_fr: float | None = None) -> dict:
    i = r["years"].index(y)
    v, lo, hi = PH().fourchette(r, y)
    b = r["base"][i]
    ecart_pct = round((r["scn"][i] / b - 1) * 100, 2) if b else None
    evo = round((r["scn"][i] / r["scn"][0] - 1) * 100, 1) if r["scn"][0] else None
    demi = round((hi - lo) / 2 / v * 100, 1) if v else 0.0
    q = {"evolution_depuis_origine": q_variation(evo), "ecart_au_tendanciel": q_variation(ecart_pct),
         "incertitude": q_incertitude(demi, y - r["origin"])}
    out = {"annee": y, "tendanciel": round(b), "scenario": round(r["scn"][i]),
           "ecart": round(r["scn"][i] - b), "ecart_pct": ecart_pct, "evolution_pct_depuis_origine": evo,
           "fourchette_scenario": [round(lo), round(hi)], "fourchette_demi_largeur_pct": demi,
           "densite_100k_tendanciel": _r1(r["dens_base"][i]), "densite_100k_scenario": _r1(r["dens_scn"][i]),
           "ecart_densite_100k": _r1(r["dens_scn"][i] - r["dens_base"][i]) if r["dens_scn"][i] and r["dens_base"][i] else None,
           "population": round(r["pop"][i]) if r["pop"][i] == r["pop"][i] else None}
    d = r["dens_scn"][i]
    if dens_fr and d and d == d:
        out["densite_100k_france_scenario"] = _r1(dens_fr)
        out["densite_ecart_a_la_france_pct"] = round((d / dens_fr - 1) * 100, 1)
        q["densite"] = q_densite(out["densite_ecart_a_la_france_pct"])
    out["qualificatifs"] = q
    return out


def _dens_fr(p: str, lv: dict, y: int) -> float | None:
    """Densité France au même réglage ; une hausse des places limitée à une région n'a pas de sens au niveau national :
    la référence nationale est alors calculée sans elle."""
    if lv.get("quotas_region"):
        lv = {**lv, "quotas_region": False, "quotas": 1.0}
    r = _answer(p, lv, "FR")
    x = r["dens_scn"][r["years"].index(y)]
    return x if x and x == x else None


def _r1(x):
    return None if x is None or x != x else round(x, 1)


_DELAI_ANS = {"etrangers": 2}   # « moyen : 1 à 3 ans » (LEVIERS_UI) ; quotas : durée des études + 1 ; autres : « rapide », 1 an


def _provenance(lv: dict, p: str | None = None) -> list[dict]:
    meta = {m["k"]: m for m in S().lever_meta()}
    d = {l["k"]: l["default"] for l in S().LEVIERS_UI}
    out = []
    for k, v in lv.items():
        if v == d[k]:
            continue
        ans = S().LAG[p] + 1 if k == "quotas" and p else _DELAI_ANS.get(k, 1)
        x = {"levier": k, "reglage": _fmt_levier(k, v), "statut": meta[k]["status"], "source": meta[k]["source"],
             "delai": meta[k]["delai"], "delai_ans": ans, "delai_qualificatif": q_delai(ans)}
        if k == "retraite" and v:      # montée de 3 mois par an (LEVIERS_UI) : le report complet est atteint après v / 0,25 ans
            x["effet_complet_apres_ans"] = int(round(v / 0.25))
        out.append(x)
    return out


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
        "annees": [_ligne(r, y, _dens_fr(p, lv, y)) for y in ys],
        f"ecart_par_flux_cumule_{ys[-1]}": flux,
        "provenance_leviers": _provenance(lv, p), **extra,
        **({"melange_de_politiques": m} if (m := _contributions(p, t, lv, ys[-1])) else {}),
        "fourchette_methode": f"scénario × (1 ± {r['k']:.4f} × années depuis {r['origin']}) : erreur de backtest extrapolée, ~8 cas sur 10",
        "perimetre": PERIMETRE, "calcul_ms": round((time.perf_counter() - t0) * 1000, 1),
        "_serie": {"annees": r["years"], "tendanciel": r["base"], "scenario": r["scn"], "k": r["k"],
                   "origine": r["origin"], "observe": r["obs"]},
    }


# Un levier de politique = un groupe de réglages (la hausse des places et sa restriction régionale vont ensemble).
_GROUPES = {"quotas": ("quotas", "quotas_region"), "etrangers": ("etrangers",), "regul": ("regul", "part_zones", "dest"),
            "retraite": ("retraite",), "cumul": ("cumul",), "precoces": ("precoces",)}


def _contributions(p: str, t: str, lv: dict, y: int) -> dict | None:
    """Mélange de politiques : effet de chaque levier seul, effet combiné, et interaction (combiné − somme des seuls).
    Tout est calculé par le jumeau, sur le même état de départ ; rien n'est additionné à la main."""
    d = {l["k"]: l["default"] for l in S().LEVIERS_UI}
    ctx = {k: lv[k] for k in ("pop_scen", "activite")}
    actifs = [g for g, ks in _GROUPES.items() if any(lv[k] != d[k] for k in ks) and lv[ks[0]] != d[ks[0]]]
    if len(actifs) < 2:
        return None
    base = _answer(p, leviers(ctx), t)
    i = base["years"].index(y)
    b = base["base"][i]
    tout = _answer(p, lv, t)["scn"][i] - b
    out, somme = [], 0.0
    for g in actifs:
        seul = leviers({**ctx, **{k: lv[k] for k in _GROUPES[g]}})
        e = _answer(p, seul, t)["scn"][i] - b
        somme += e
        out.append({"levier": "; ".join(resume_leviers(seul)), "ecart_seul": round(e),
                    "ecart_seul_pct": round(e / b * 100, 2) if b else None,
                    "qualificatif": q_variation(e / b * 100 if b else None),
                    "part_de_l_ecart_combine_pct": round(e / tout * 100, 1) if abs(tout) > 0.5 else None})
    out.sort(key=lambda x: -abs(x["ecart_seul"]))
    return {"annee": y, "leviers": out, "ecart_combine": round(tout), "somme_des_effets_seuls": round(somme),
            "interaction": round(tout - somme),
            "lecture": "écart au tendanciel de chaque levier seul, puis de tous ensemble ; l'interaction est la différence "
                       "entre l'effet combiné et la somme des effets seuls (la régulation, par exemple, peut absorber des entrées "
                       "supplémentaires)"}


# Réglages de référence pour comparer les leviers entre eux (supposés : des ordres de grandeur, pas des recommandations).
_REFERENCE = {"quotas": {"quotas": 1.2}, "etrangers": {"etrangers": 1.5}, "retraite": {"retraite": 2.0},
              "cumul": {"cumul": 1.5}, "precoces": {"precoces": 0.7}, "regul": {"regul": True}}


def effets_des_leviers(profession_: str, territoire_: str = "FR", annee: int = 2040) -> dict:
    """Chaque levier seul, à un réglage de référence, puis tous ensemble : écart au tendanciel à l'année demandée."""
    p, t = profession(profession_), territoire(territoire_)
    base = _answer(p, leviers({}), t)
    y = _annees([annee], base)[0]
    i = base["years"].index(y)
    b = base["base"][i]
    meta = {m["k"]: m for m in S().lever_meta()}
    rows = []
    for k, reg in _REFERENCE.items():
        lv = leviers(reg)
        r = _answer(p, lv, t)
        e = r["scn"][i] - b
        ans = S().LAG[p] + 1 if k == "quotas" else _DELAI_ANS.get(k, 1)
        rows.append({"levier": "; ".join(resume_leviers(lv)), "ecart": round(e), "ecart_pct": round(e / b * 100, 2) if b else None,
                     "qualificatif": q_variation(e / b * 100 if b else None), "delai_qualificatif": q_delai(ans),
                     "statut": meta[k]["status"], "source": meta[k]["source"]})
    rows.sort(key=lambda x: -abs(x["ecart"]))
    tous = leviers({k: v for reg in _REFERENCE.values() for k, v in reg.items()})
    e = _answer(p, tous, t)["scn"][i] - b
    return {"profession": S().PROFS[p], "territoire": nom_territoire(t), "code_territoire": t, "annee": y,
            "tendanciel": round(b), "leviers_seuls": rows,
            "tous_ensemble": {"ecart": round(e), "ecart_pct": round(e / b * 100, 2) if b else None,
                              "qualificatif": q_variation(e / b * 100 if b else None)},
            "methode": "réglages de référence supposés (ordres de grandeur dans les bornes, pas des recommandations) ; "
                       "classement par écart projeté au tendanciel ; le choix revient au décideur",
            "perimetre": PERIMETRE}


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
                     "leviers": resume_leviers(lv), **_ligne(r, ys[0], _dens_fr(p, lv, ys[0]))})
        series.append({"nom": rows[-1]["nom"], "annees": r["years"], "valeurs": r["scn"]})
    prov = {x["levier"]: x for sc in scenarios for x in _provenance(leviers(sc.get("leviers")), p)}
    return {"profession": S().PROFS[p], "territoire": nom_territoire(t), "code_territoire": t, "annee": annee, "scenarios": rows,
            "provenance_leviers": list(prov.values()), "perimetre": PERIMETRE, "_series": {"tendanciel": {"annees": r["years"], "valeurs": r["base"]}, "scenarios": series}}


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
        y = _annees([annee], r)[0]
        out.append({"valeur": v, "reglage": _fmt_levier(levier, lv[levier]), **_ligne(r, y, _dens_fr(p, lv, y))})
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
    dfr = _dens_fr(p, lv, annee)
    for d in deps:
        try:
            r = _answer(p, lv, "D" + d)
        except Exception:
            continue
        if annee not in r["years"]:
            raise ErreurOutil(f"année hors projection : {annee}")
        x = _ligne(r, annee, dfr)
        rows.append({"departement": str(g.loc[d, "dep_name"]), "code": d, **x})
    if critere not in ("densite_100k_scenario", "ecart_pct", "evolution_pct_depuis_origine", "scenario"):
        raise ErreurOutil("critère : densite_100k_scenario, ecart_pct, evolution_pct_depuis_origine ou scenario")
    rows = [r for r in rows if r.get(critere) is not None]
    rows.sort(key=lambda r: r[critere], reverse=(ordre == "decroissant"))
    return {"profession": srv.PROFS[p], "perimetre_classement": nom_territoire(terr), "annee": annee, "critere": critere,
            "leviers": resume_leviers(lv) or ["tendanciel"], "nb_departements": len(rows), "departements": rows[:max(1, min(n, 30))],
            "moyenne_simple_des_departements_densite": _r1(float(np.mean([r["densite_100k_scenario"] for r in rows if r["densite_100k_scenario"]]))) if rows else None,
            "densite_100k_france_scenario": _r1(dfr),
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


# Modèle servi (v2/prototype/server.py, Model : C1 par défaut, A0 par JUMEAU_MODELE=A0) ; chiffres mesurés, cités des articles.
MODELES = {
    "C1": {
        "nom": "Cohortes bayésiennes, entrées comprises (C1, axe 2)",
        "equation": "N(t+1) = rétention × vieillissement de N(t) + entrées, par profession × département × sexe × tranche d'âge de 5 ans ; rétention nette en âge-période-cohorte, entrées = niveau national (filtre de Kalman) × parts départementales",
        "estimation": "Bayes empirique, moyenne a posteriori ; fenêtre de 2012 (kinés 2017) à la dernière année ; effets département et région rétrécis ; secteur privé seulement, le salariat public garde les taux de A0",
        "leviers": "événements datés du jumeau (modules entrées, sorties, diplômés étrangers, régulation) appliqués aux taux de C1, au même état de départ ; état à 2 secteurs (libéral = privé, salarié)",
        "precision": "MAPE 7,73 % par département à 5 ans, secteur privé, contre 8,68 % pour A0 et 9,30 % pour la tendance linéaire (mesuré, article axe 2) ; gain plus faible sur les origines récentes (dentistes, pharmaciens)",
        "fourchette": "± pente de l'erreur nationale de C1 au banc × horizon × 1,6, environ 8 cas sur 10 (même méthode que A0) ; extrapolée au-delà d'environ 10 ans ; la bande probabiliste propre de C1 n'est calibrée qu'au département (77,6 %) et n'est pas publiée au national",
        "approximation": "rétention de C1 tenue à sa moyenne sur l'horizon : écart de −1,1 à +1,2 % sur le total privé national à 5 ans (mesuré) ; infirmiers : C1 mesuré au banc sur les libéraux, la carte sert la table privée de l'axe 4",
        "alternative": "A0, stock-flux à taux départementaux (MAPE 8,68 %) : servi si JUMEAU_MODELE=A0",
        "sources": "v2/papers/axe2-methodes/main.pdf ; v2/methodes/cohortes.py ; v2/methodes/c1_jumeau.py ; v2/jumeau/ ; v2/prototype/server.py (Model)",
    },
    "A0": {
        "nom": "Stock-flux à taux départementaux (A0, axe 2)",
        "equation": "N(t+1) = rétention × vieillissement de N(t) + entrées, par profession × département × sexe × tranche d'âge de 5 ans",
        "estimation": "rétention nette et entrées ajustées sur les 5 dernières années observées ; taux départementaux rétrécis vers le national (poids 200 personnes, supposé)",
        "leviers": "événements datés du jumeau (modules entrées, sorties, diplômés étrangers, régulation) appliqués au même état de départ ; état à 2 secteurs (libéral = privé, salarié)",
        "precision": "MAPE 8,68 % par département à 5 ans, secteur privé, contre 9,30 % pour la tendance linéaire (mesuré, article axe 2, tableau 1)",
        "fourchette": "± pente de l'erreur de backtest × horizon × 1,6, environ 8 cas sur 10 (facteur cité, non reproduit ; article axe 5) ; extrapolée au-delà d'environ 10 ans",
        "alternative": "C1, cohortes bayésiennes : MAPE 7,73 % au même banc, servi par défaut (JUMEAU_MODELE=C1)",
        "sources": "v2/papers/axe2-methodes/main.pdf ; v2/sante/estimators.py (StockFlowLocal) ; v2/jumeau/ ; v2/prototype/server.py (Model)",
    },
}
# Modèle servi : même variable que v2/prototype/server.py (MODELE_CHOIX), C1 par défaut.
MODELE = MODELES[os.environ.get("JUMEAU_MODELE", "C1").upper()]


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
        "modele_de_projection": MODELE,
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
