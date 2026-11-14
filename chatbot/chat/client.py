"""Seul accès du chatbot au modèle : des requêtes GET vers la passerelle (passerelle/server.py).

Le chatbot n'importe aucun code du modèle et n'a aucun outil d'écriture, de fichier ou de commande : le modèle de
langage ne peut que choisir une requête de la liste blanche et ses arguments, validés par la passerelle.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from urllib.parse import quote

URL = os.environ.get("PASSERELLE_URL", "http://127.0.0.1:8770")


class PasserelleInjoignable(RuntimeError):
    pass


def _get(chemin: str, timeout: float = 60) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(URL + chemin, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except json.JSONDecodeError:
            return e.code, {"erreur": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        raise PasserelleInjoignable(f"passerelle injoignable sur {URL} : lancer « uv run python -m passerelle.server »") from e


def sante() -> dict:
    return _get("/v1/sante", 5)[1]


def outils() -> list[dict]:
    return _get("/v1/outils", 10)[1]["outils"]


def requete(nom: str, args: dict) -> tuple[dict | None, str | None]:
    """(résultat, None) ou (None, message d'erreur à renvoyer au modèle de langage)."""
    code, j = _get(f"/v1/requete/{quote(nom, safe='')}?args={quote(json.dumps(args, ensure_ascii=False))}")
    if code == 200:
        return j["resultat"], None
    return None, j.get("erreur", f"HTTP {code}")
