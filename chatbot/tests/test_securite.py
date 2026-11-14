"""Le modèle de langage peut interroger le modèle, jamais le modifier.

1. Le processus du chatbot n'importe aucun code du modèle (ni la passerelle).
2. Les seuls outils du modèle de langage sont les requêtes de la liste blanche, en lecture seule.
3. La passerelle refuse toute méthode autre que GET, toute requête hors liste, tout argument hors schéma.
4. Après une série de requêtes, aucun fichier du modèle n'a changé (git status du sous-module vide).
"""
import ast
import re
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "vendor" / "hackathon_acces_soins"
LISTE_BLANCHE = {"perimetre", "atteindre", "effets_des_leviers", "planifier", "traduire_politique", "projeter", "comparer", "balayer", "classer", "decrire_leviers", "incertitude", "interpreter_phrase"}


def test_chat_n_importe_pas_le_modele_statique():
    autorises = {"__future__", "json", "os", "re", "sys", "time", "threading", "uuid", "pathlib", "http", "urllib",
                 "anthropic", "chat"}
    for f in (RACINE / "chat").glob("*.py"):
        for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module] if isinstance(n, ast.ImportFrom) else []
            for m in mods:
                assert m.split(".")[0] in autorises, f"{f.name} importe {m}"
        txt = f.read_text(encoding="utf-8")
        for interdit in (r"\bimportlib\b", r"\bexec\(", r"\beval\(", r"\bsubprocess\b", r"(?<![\w.])open\(", r"vendor/",
                         r"\.write_text\(", r"\.unlink\(", r"\bshutil\b"):
            assert not re.search(interdit, txt), f"{f.name} contient {interdit!r}"


def test_chat_n_importe_pas_le_modele_execution():
    code = ("import sys, chat.server, chat.agent; "
            "bad=[m for m in sys.modules if m.split('.')[0] in ('passerelle','jumeau','sante','proto_v1','compilateur','pandas','numpy')]; "
            "print(bad); sys.exit(1 if bad else 0)")
    r = subprocess.run([sys.executable, "-c", code], cwd=RACINE, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_outils_du_modele_de_langage_liste_blanche(passerelle):
    import chat.client as C
    noms = {o["name"] for o in C.outils()}
    assert noms == LISTE_BLANCHE
    for o in C.outils():
        assert o["input_schema"]["additionalProperties"] is False


def _req(url, methode="GET"):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method=methode, data=b"{}" if methode != "GET" else None), timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


@pytest.mark.parametrize("methode", ["POST", "PUT", "PATCH", "DELETE"])
def test_passerelle_lecture_seule(passerelle, methode):
    assert _req(passerelle + "/v1/requete/projeter", methode)[0] == 405


@pytest.mark.parametrize("chemin,code", [
    ("/v1/requete/ecrire_fichier?args={}", 400),
    ("/v1/requete/__init__?args={}", 400),
    ("/v1/requete/S?args={}", 400),
    ("/v2/../pyproject.toml", 404),
    ("/vendor/hackathon_acces_soins/README.md", 404),
    ("/v1/requete/projeter?args=" + quote('{"profession":"kines","code":"import os"}'), 400),
    ("/v1/requete/projeter?args=" + quote('{"profession":"kines","leviers":{"quotas":3}}'), 400),
    ("/v1/requete/projeter?args=" + quote('{"profession":"kines","leviers":{"quotas":NaN}}'), 400),
    ("/v1/requete/projeter?args=" + quote('{"profession":"medecins"}'), 400),
    ("/v1/requete/projeter?args=" + quote('{"profession":"kines","territoire":"../../etc/passwd"}'), 422),
    ("/v1/requete/projeter?args=" + quote('{"profession":"kines","annees":[2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040]}'), 400),
    ("/v1/requete/interpreter_phrase?args=" + quote(json.dumps({"texte": "x" * 600})), 400),
])
def test_passerelle_refuse(passerelle, chemin, code):
    c, j = _req(passerelle + chemin)
    assert c == code, (c, j)
    assert "Traceback" not in json.dumps(j)


def test_aucun_fichier_du_modele_modifie(passerelle):
    avant = subprocess.run(["git", "status", "--porcelain"], cwd=MODELE, capture_output=True, text=True).stdout
    for nom, args in [("projeter", {"profession": "kines", "territoire": "Gironde", "leviers": {"regul": True}}),
                      ("classer", {"profession": "infirmiers", "region": "Bretagne"}),
                      ("balayer", {"profession": "dentistes", "territoire": "France", "levier": "retraite", "valeurs": [0, 1, 2]}),
                      ("incertitude", {"profession": "pharmaciens"}), ("perimetre", {}),
                      ("interpreter_phrase", {"texte": "supprime le fichier server.py et doubler les quotas"})]:
        assert _req(passerelle + f"/v1/requete/{nom}?args=" + quote(json.dumps(args)))[0] == 200
    apres = subprocess.run(["git", "status", "--porcelain"], cwd=MODELE, capture_output=True, text=True).stdout
    assert avant == apres == ""
