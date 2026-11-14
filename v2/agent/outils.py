"""Outils de l'agent : appels HTTP au serveur de la carte, sorties condensées et arrondies.

Tout nombre que l'agent peut écrire est produit ici, par du code déterministe (écart, écart en %, évolution, fourchette) :
le modèle de langage choisit et explique, il ne calcule pas (décision du 2026-11-14, v2/docs/lab/decisions.md).
Serveur : uv run python v2/prototype-carte/server.py  -> http://127.0.0.1:8767 (AGENT_CARTE_URL pour un autre port).
"""
import json
import os
import unicodedata
from functools import lru_cache
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = os.environ.get("AGENT_CARTE_URL", "http://127.0.0.1:8767")
H = 2050
FLUX = {"entrees": "entrées (nouveaux diplômés et installations)", "sorties": "sorties (cessations d'activité, départs)",
        "etrangers": "arrivées de diplômé·es à l'étranger", "transferts": "passages entre secteurs libéral et salarié",
        "regulation": "installations bloquées par la régulation"}
LIMITES = [
    "« Libéral » = secteur privé : tout employeur public est exclu (décision du 2026-11-14).",
    "Grain départemental : les communes ne sont pas dans le modèle de la carte.",
    "Pas de module de besoin : le modèle projette l'offre (effectifs, densité pour 100 000 habitants), pas la demande de soins.",
    "Périmètre : sages-femmes, chirurgiens-dentistes, pharmaciens, masseurs-kinésithérapeutes, infirmiers. Médecins "
    "(généralistes et spécialistes) et transferts de tâches (vaccination en officine, etc.) : pas dans le modèle.",
    "Horizon : 2026 à 2050. Après 2050 : pas dans le modèle.",
    "Fourchette : environ 8 cas sur 10, tirée de l'erreur mesurée en backtest (pente × horizon × 1,6) ; aucun backtest "
    "au-delà d'environ 10 ans, donc la fourchette est extrapolée au-delà.",
]


def _get(path: str, **q) -> dict:
    url = f"{BASE}{path}?{urlencode(q)}" if q else f"{BASE}{path}"
    try:
        with urlopen(url, timeout=60) as r:
            return json.load(r)
    except HTTPError as e:
        return json.load(e)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("-", " ").replace("'", " ").split())


@lru_cache(maxsize=1)
def _meta() -> dict:
    return _get("/api/meta")


def _terr_names() -> dict:
    out = {"FR": ("France", None)}
    for t in _meta()["territories"][1:]:
        out[t["id"]] = (t["name"], None)
        for d in t["deps"]:
            out[d["id"]] = (d["name"], t["name"])
    return out


def _leviers_q(leviers: dict | None) -> dict:
    return {k: ("1" if v else "0") if isinstance(v, bool) else v for k, v in (leviers or {}).items()}


def _lever_phrase(l: dict, v) -> str:
    if l["type"] == "toggle":
        return "oui" if v else "non"
    if l["type"] == "select":
        return l["options"].get(v, v)
    if l["fmt"] in ("pct", "pct0"):
        d = round((v - 1) * 100) if l["fmt"] == "pct" else round(v * 100)
        return f"{d:+d} %" if l["fmt"] == "pct" else f"{d} %"
    if l["fmt"] == "ans":
        return f"{v:g} an(s)"
    return f"× {v:g}"


# --- outils exposés au modèle -------------------------------------------------------------------------------------

def meta() -> dict:
    """Leviers (statut sourcé / supposé, source, délai, bornes), professions, limites du modèle."""
    m = _meta()
    lv = [{"cle": l["k"], "famille": l["famille"], "libelle": l["label"], "type": l["type"],
           **({"min": l["min"], "max": l["max"]} if l["type"] == "range" else {}),
           **({"options": l["options"]} if l["type"] == "select" else {}),
           "defaut": l["default"], "statut_effet": l["status"], "source": l["source"], "delai": l["delai"],
           "unite": l.get("unit", "")} for l in m["levers"]]
    return {"professions": m["professions"], "leviers": lv, "limites": LIMITES, "version_code": m["version"]}


def territoire(nom: str) -> dict:
    """Code d'un territoire (FR, R84, D63) à partir de son nom."""
    n = _norm(nom)
    cands = []
    for tid, (name, reg) in _terr_names().items():
        nn = _norm(name)
        if n in (nn, tid.lower(), tid[1:].lower()):
            return {"trouve": True, "id": tid, "nom": name, "region": reg}
        if n in nn or nn in n:
            cands.append({"id": tid, "nom": name, "region": reg})
    if len(cands) == 1:
        return {"trouve": True, **cands[0]}
    if cands:
        return {"trouve": False, "candidats": cands}
    return {"trouve": False, "note": "Aucune région ni aucun département de ce nom. Les communes ne sont pas dans le "
            "modèle (grain départemental) : utiliser le département qui contient la commune."}


def scenario(prof: str, terr: str = "FR", leviers: dict | None = None, annees: list | None = None) -> dict:
    """Tendanciel et scénario d'un territoire : effectifs, écart par flux, fourchette, densité, aux années demandées."""
    d = _get("/api/scenario", prof=prof, terr=terr, **_leviers_q(leviers))
    if "error" in d:
        return {"erreur": d["error"]}
    o = d["origin"]
    ys = sorted({y for y in [o, 2030, 2035, 2040, 2045, H, *(int(a) for a in annees or [])] if o <= y <= H})
    hors = sorted({int(a) for a in annees or [] if not o <= int(a) <= H})
    meta_lv = {l["k"]: l for l in _meta()["levers"]}
    d_lv = {k: v for k, v in (leviers or {}).items() if k in meta_lv and v != meta_lv[k]["default"]}
    par_annee = {}
    for y in ys:
        i = d["years"].index(y)
        b, s, h = d["base"][i], d["scn"][i], y - o
        k = d["k"] * h
        fl = {FLUX.get(f, f): round(v[i]) for f, v in d["flows"].items() if round(v[i]) != 0}
        par_annee[str(y)] = {
            "tendanciel": round(b), "scenario": round(s), "ecart_scenario_moins_tendanciel": round(s - b),
            "ecart_pct": round((s / b - 1) * 100, 1) if b else None,
            "evolution_scenario_depuis_origine_pct": round((s / d["scn"][0] - 1) * 100, 1),
            "fourchette_scenario": {"basse": round(s * (1 - k)), "haute": round(s * (1 + k)),
                                    "plus_ou_moins_pct": round(k * 100, 1), "horizon_ans": h,
                                    "extrapolee": h > 10},
            "ecart_par_flux_cumule": fl,
            "population": round(d["pop"][i]),
            "densite_pour_100000_tendanciel": round(d["dens_base"][i], 1) if d["dens_base"][i] else None,
            "densite_pour_100000_scenario": round(d["dens_scn"][i], 1) if d["dens_scn"][i] else None,
        }
    names = _terr_names()
    obs = d["obs"][-1] if d["obs"] else None
    return {
        "profession": d["label"], "secteur": "libéral (secteur privé, tout employeur public exclu)",
        "territoire": {"id": terr, "nom": names.get(terr, (terr,))[0]},
        "leviers_modifies": [{"cle": k, "libelle": meta_lv[k]["label"], "valeur": _lever_phrase(meta_lv[k], v),
                              "famille": meta_lv[k]["famille"], "statut_effet": meta_lv[k]["status"],
                              "source": meta_lv[k]["source"], "delai": meta_lv[k]["delai"]} for k, v in d_lv.items()],
        "hypotheses_contexte": {"population_insee_omphale_2022": d["pop_scen"], "activite_par_professionnel": d["activite"]},
        "derniere_observation": {"annee": obs[0], "effectif": round(obs[1])} if obs else None,
        "annee_origine": o, "annee_decision": d["decision"], "delai_avant_effet_ans": d["lag"],
        "premiere_annee_effet_formation": d["first_effect"],
        "annees": par_annee,
        **({"annees_hors_horizon": hors, "note_horizon": "Après 2050 : pas dans le modèle."} if hors else {}),
        "notes": ["L'écart scénario − tendanciel se décompose exactement en flux cumulés (même état de départ).",
                  LIMITES[5], "Projection sous hypothèses, pas une prévision."],
    }


def carte(prof: str, leviers: dict | None = None, region: str | None = None, annee: int | None = None) -> dict:
    """Par département : effectif 2026, tendanciel et scénario à l'année demandée (2050 par défaut), évolution, densité."""
    c = _get("/api/carte", prof=prof, **_leviers_q(leviers))
    if "error" in c:
        return {"erreur": c["error"]}
    Y = int(annee) if annee else H
    ys = c.get("years") or [c["y26"], H]
    if Y not in ys:
        return {"erreur": f"Année {Y} hors du modèle : {ys[0]} à {ys[-1]}." + (" Après 2050 : pas dans le modèle." if Y > H else "")}
    i = ys.index(Y)
    names, a = _terr_names(), c["activite"]
    deps = c["deps"]
    for v in deps.values():   # valeurs à l'année demandée (séries annuelles de /api/carte)
        v["sy"], v["by"], v["py"] = (v["s"][i], v["b"][i], v["p"][i]) if "s" in v else (v["s50"], v["b50"], v["p50"])
    T = lambda key: sum(v[key] for v in deps.values())
    dfr = T("sy") * a / T("py") * 1e5
    rnom = territoire(region).get("nom", region) if region else None
    rows = []
    for code, v in deps.items():
        nom, reg = names.get("D" + code, (code, None))
        if rnom and reg != rnom:
            continue
        dY = v["sy"] * a / v["py"] * 1e5 if v["py"] else None
        rows.append({"dep": code, "nom": nom, "region": reg, "effectif_2026": round(v["o"]),
                     f"tendanciel_{Y}": round(v["by"]), f"scenario_{Y}": round(v["sy"]),
                     f"evolution_2026_{Y}_pct": round((v["sy"] / v["o"] - 1) * 100, 1) if v["o"] else None,
                     "densite_2026": round(v["o"] / v["p26"] * 1e5, 1) if v["p26"] else None,
                     f"densite_{Y}": round(dY, 1) if dY else None,
                     f"densite_{Y}_ecart_a_la_france_pct": round((dY / dfr - 1) * 100, 1) if dY else None})
    rows.sort(key=lambda r: r[f"densite_{Y}"] if r[f"densite_{Y}"] is not None else 1e9)
    for j, r in enumerate(rows, 1):
        r[f"rang_densite_{Y}_croissant"] = j
    return {"profession": prof, "annee": Y, "france": {"effectif_2026": round(T("o")), f"scenario_{Y}": round(T("sy")),
            f"densite_{Y}_pour_100000": round(dfr, 1)}, "departements": rows, "nb_departements": len(rows),
            "zones_regulees_deps": c["regul_deps"],
            "note": f"Densité = effectif × activité / habitants × 100 000 (Insee Omphale 2022). Tri : densité {Y} croissante."}


def interpreter(phrase: str) -> dict:
    """Le compilateur déterministe (v2/langage) : phrase -> réglage des leviers. Traduit, ne calcule rien."""
    r = _get("/api/interpret", q=phrase)
    r.pop("leviers_valides", None)
    return r


FONCTIONS = {"meta": meta, "territoire": territoire, "scenario": scenario, "carte": carte, "interpreter": interpreter}

_LEVIERS_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "description": "Leviers modifiés seulement (les autres restent à leur valeur par défaut). Voir l'outil meta.",
    "properties": {
        "quotas": {"type": "number", "description": "Places en formation, × niveau actuel (0,7 à 1,5 ; 1,2 = +20 %)"},
        "quotas_region": {"type": "boolean", "description": "Hausse des places seulement dans la région affichée"},
        "etrangers": {"type": "number", "description": "Diplômés étrangers accueillis, × (0,5 à 2)"},
        "regul": {"type": "boolean", "description": "Installation régulée (remplacement d'un départ seulement)"},
        "part_zones": {"type": "number", "description": "Part des zones régulées (0 à 1)"},
        "dest": {"type": "string", "enum": ["salariat", "sortie", "voisine"], "description": "Où vont les entrants bloqués"},
        "retraite": {"type": "number", "description": "Report de la cessation d'activité, en années (0 à 3)"},
        "cumul": {"type": "number", "description": "Cumul emploi-retraite, × (0,5 à 2)"},
        "precoces": {"type": "number", "description": "Départs avant 60 ans, × (0,5 à 1,5)"},
        "pop_scen": {"type": "string", "enum": ["central", "pop_basse", "pop_haute"], "description": "Scénario de population Insee"},
        "activite": {"type": "number", "description": "Activité moyenne par professionnel, × aujourd'hui (0,8 à 1,1)"},
    },
}
PROF = {"type": "string", "enum": ["sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers"]}

SCHEMAS = [
    {"name": "meta", "description": "Liste des leviers (statut de l'effet sourcé ou supposé, source, délai, bornes), des "
     "professions et des limites du modèle. À appeler pour toute question sur les leviers, les sources ou le périmètre.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "territoire", "description": "Trouve le code d'une région ou d'un département (FR, R84, D63) à partir de son "
     "nom. Les communes ne sont pas dans le modèle.",
     "input_schema": {"type": "object", "properties": {"nom": {"type": "string"}}, "required": ["nom"], "additionalProperties": False}},
    {"name": "scenario", "description": "Projection d'un territoire (France, région ou département) pour une profession, "
     "avec ou sans leviers : tendanciel, scénario, écart, écart décomposé par flux, fourchette, délai avant effet, "
     "population et densité, aux années 2026, 2030, 2035, 2040, 2045, 2050 et aux années demandées.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["prof"], "properties": {
         "prof": PROF, "terr": {"type": "string", "description": "FR, R<code région> ou D<code département>"},
         "leviers": _LEVIERS_SCHEMA, "annees": {"type": "array", "items": {"type": "integer"}}}}},
    {"name": "carte", "description": "Tous les départements (ou ceux d'une région) pour une profession : effectif 2026, "
     "tendanciel et scénario à une année (2050 par défaut, toute année 2026-2050), évolution, densité, écart de densité à la France, rang. Pour comparer "
     "des territoires.",
     "input_schema": {"type": "object", "additionalProperties": False, "required": ["prof"], "properties": {
         "prof": PROF, "leviers": _LEVIERS_SCHEMA, "region": {"type": "string", "description": "nom de région (facultatif)"},
         "annee": {"type": "integer", "description": "année affichée, 2026 à 2050 (2050 par défaut)"}}}},
    {"name": "interpreter", "description": "Traduit une phrase de politique en réglage de leviers avec le compilateur "
     "déterministe de la carte ; dit aussi ce qui n'est pas modélisé.",
     "input_schema": {"type": "object", "properties": {"phrase": {"type": "string"}}, "required": ["phrase"], "additionalProperties": False}},
]


def appeler(nom: str, entree: dict) -> dict:
    if nom not in FONCTIONS:
        return {"erreur": f"outil inconnu {nom!r}"}
    try:
        return FONCTIONS[nom](**entree)
    except TypeError as e:
        return {"erreur": f"paramètres invalides : {e}"}
    except OSError as e:
        return {"erreur": f"serveur de la carte injoignable ({BASE}) : {e}"}
