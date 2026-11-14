"""Agent conversationnel qui interprète les sorties du jumeau pour un·e utilisateur·rice non technique.

Il explique, il ne calcule pas : chaque nombre vient d'un outil (outils.py -> serveur de la carte), et chaque réponse
passe deux garde-fous mesurés (garde_fous.py : ancrage des nombres, lexique neutre).

Clé : variable d'environnement ANTHROPIC_API_KEY, ou ligne ANTHROPIC_API_KEY=… d'un fichier .env local à la racine
(ignoré par git, jamais commité). La clé n'est ni affichée ni journalisée.
Modèle : AGENT_MODEL (défaut claude-opus-5-5) ; effort : AGENT_EFFORT (défaut medium).
Run (racine du dépôt, serveur de la carte lancé) :
    uv run python v2/agent/agent.py "Combien de kinés en Auvergne-Rhône-Alpes en 2035 si on forme 20 % de plus ?"
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import garde_fous  # noqa: E402
import outils  # noqa: E402

MODELE = os.environ.get("AGENT_MODEL", "claude-opus-5-5")
EFFORT = os.environ.get("AGENT_EFFORT", "medium")
TOURS_MAX = 8
PRIX = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0), "claude-haiku-5-5": (0.10, 0.50),
        "claude-fable-5-1": (10.0, 50.0)}      # $ par million de jetons (entrée, sortie), tarif public 2026-10

SYSTEME = """Tu aides des élu·es et des agents publics, sans formation technique, à lire les résultats d'un jumeau numérique de l'offre de soins libérale en France (sages-femmes, chirurgiens-dentistes, pharmaciens, masseurs-kinésithérapeutes, infirmiers ; 2026 à 2050). Tu expliques des résultats ; tu ne les produis pas.

Règle des nombres (absolue). Tu n'effectues aucun calcul : ni addition, ni soustraction, ni pourcentage, ni moyenne, ni conversion. Chaque nombre que tu écris est recopié d'une sortie d'outil de cette conversation, tel quel ou arrondi (13 240 peut devenir « environ 13 200 »). Si le nombre dont tu as besoin n'est dans aucune sortie, appelle l'outil qui le donne ; s'il n'existe pas, dis-le. Un contrôle automatique vérifie chaque nombre de ta réponse.

Ce qui n'est pas dans le modèle. Si la question porte sur ce que le modèle ne couvre pas (médecins généralistes ou spécialistes, transfert de tâches comme la vaccination en officine, communes, besoin ou demande de soins, années après 2050, autres professions), écris exactement « pas dans le modèle », puis dis ce que le modèle peut donner à la place (par exemple le département qui contient la commune). N'invente jamais un ordre de grandeur.

Ce qu'une bonne réponse contient, quand c'est pertinent :
- le chiffre principal, son année, son territoire, et sa fourchette (« probablement entre A et B », environ 8 cas sur 10) ; si la fourchette est extrapolée (au-delà d'environ 10 ans d'horizon), le dire ;
- le pourquoi : l'écart entre le scénario et la tendance, décomposé par flux (entrées, sorties…), tel que l'outil scenario le donne ;
- le délai avant effet (première année d'effet) ;
- le statut de chaque levier utilisé : effet sourcé ou supposé, avec sa source ;
- la limite qui compte pour la question (grain départemental, pas de module de besoin, « libéral » = secteur privé, tout employeur public exclu).

Langue : français simple, phrases courtes, 200 mots au plus. Puces avec « - », jamais de listes numérotées. Nombres en chiffres, format français (13 240 ; 3,2 %).

Lexique neutre : décrire et comparer, jamais juger. Interdit, même entre guillemets ou pour reprendre la question : désert, médiocre, mauvais, pénurie, manque, sur-doté, trop de, catastrophique, critique, alarmant, abandonnés, oubliés, bon ou mauvais élève, échec, il faut, on doit, prévision. Écris plutôt : densité inférieure (ou supérieure) à la moyenne nationale, écart, la densité diminue de X %, le scénario X conduit à…, projection sous hypothèses. Si on te demande un avis ou une recommandation, ne tranche pas : décris ce que chaque scénario conduit à.

Outils : `territoire` pour un code (R84, D63), `scenario` pour un territoire et des leviers, `carte` pour comparer des départements, `meta` pour les leviers, leurs sources et les limites, `interpreter` pour traduire une phrase de politique en leviers. Un contexte de la carte (profession, territoire, leviers affichés) peut accompagner la question : les questions « et si… », « pourquoi » s'y rapportent."""


def _cle_locale():
    """Charge ANTHROPIC_API_KEY depuis .env (racine du dépôt) si l'environnement ne la donne pas."""
    env = Path(__file__).resolve().parents[2] / ".env"
    if os.environ.get("ANTHROPIC_API_KEY") or not env.is_file():
        return
    for ligne in env.read_text().splitlines():
        k, _, v = ligne.partition("=")
        if k.strip() == "ANTHROPIC_API_KEY" and v.strip():
            os.environ["ANTHROPIC_API_KEY"] = v.strip().strip("'\"")


def disponible() -> tuple[bool, str]:
    _cle_locale()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False, ("Agent indisponible : la variable d'environnement ANTHROPIC_API_KEY n'est pas définie sur le serveur. "
                       "La carte reste utilisable.")
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False, "Agent indisponible : le paquet anthropic n'est pas installé (uv sync)."
    return True, f"Agent prêt ({MODELE})."


def _contexte_txt(ctx: dict | None) -> str:
    if not ctx:
        return ""
    return "Contexte de la carte : " + json.dumps(ctx, ensure_ascii=False)


def repondre(question: str, contexte: dict | None = None, historique: list | None = None) -> dict:
    """Une question (et l'historique texte des tours précédents) -> réponse, appels d'outils, garde-fous, coût."""
    ok, msg = disponible()
    if not ok:
        return {"erreur": msg}
    import anthropic
    client = anthropic.Anthropic()          # lit ANTHROPIC_API_KEY
    t0 = time.perf_counter()
    ctx = _contexte_txt(contexte)
    messages = [{"role": m["role"], "content": m["texte"]} for m in (historique or []) if m.get("texte")]
    messages.append({"role": "user", "content": (ctx + "\n\n" if ctx else "") + "Question : " + question})
    appels, use_in, use_out, use_cache = [], 0, 0, 0
    texte, arret = "", None
    for _ in range(TOURS_MAX):
        try:
            r = client.beta.messages.create(
                model=MODELE, max_tokens=16000, system=SYSTEME, tools=outils.SCHEMAS, messages=messages,
                output_config={"effort": EFFORT}, cache_control={"type": "ephemeral"},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default")
        except anthropic.AuthenticationError:
            return {"erreur": "Clé d'API refusée (ANTHROPIC_API_KEY)."}
        except anthropic.RateLimitError:
            return {"erreur": "Limite de débit de l'API atteinte ; réessayer dans une minute."}
        except anthropic.APIStatusError as e:
            return {"erreur": f"Erreur de l'API ({e.status_code})."}
        except anthropic.APIConnectionError:
            return {"erreur": "API injoignable (réseau)."}
        u = r.usage
        use_in += u.input_tokens + (u.cache_creation_input_tokens or 0)
        use_cache += u.cache_read_input_tokens or 0
        use_out += u.output_tokens
        arret = r.stop_reason
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            texte = "\n".join(b.text for b in r.content if b.type == "text").strip()
            break
        resultats = []
        for b in r.content:
            if b.type != "tool_use":
                continue
            sortie = outils.appeler(b.name, b.input if isinstance(b.input, dict) else {})
            appels.append({"outil": b.name, "entree": b.input, "sortie": sortie})
            resultats.append({"type": "tool_result", "tool_use_id": b.id,
                              "content": json.dumps(sortie, ensure_ascii=False),
                              **({"is_error": True} if "erreur" in sortie else {})})
        messages.append({"role": "user", "content": resultats})
    if arret == "refusal":
        texte = texte or "Je ne peux pas répondre à cette question."
    pin, pout = PRIX.get(MODELE, (0, 0))
    cout = (use_in * pin + use_cache * pin * 0.05 + use_out * pout) / 1e6
    return {
        "reponse": texte, "arret": arret, "modele": MODELE, "appels": appels,
        "ancrage": garde_fous.ancrage(texte, [a["sortie"] for a in appels], question, contexte),
        "lexique": garde_fous.lexique(texte),
        "jetons": {"entree": use_in, "cache_lu": use_cache, "sortie": use_out}, "cout_usd": round(cout, 4),
        "secondes": round(time.perf_counter() - t0, 1),
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Combien de kinés en Auvergne-Rhône-Alpes en 2035 si on forme 20 % de plus, et pourquoi ?"
    r = repondre(q)
    if "erreur" in r:
        sys.exit(r["erreur"])
    print(r["reponse"], "\n")
    print("outils :", ", ".join(f"{a['outil']}({json.dumps(a['entree'], ensure_ascii=False)})" for a in r["appels"]))
    print("ancrage :", r["ancrage"], "| lexique :", r["lexique"])
    print(f"{r['secondes']} s, {r['cout_usd']} $, jetons {r['jetons']}")
