"""Boucle de l'agent avec un faux modèle de langage (réponses scénarisées) et une vraie passerelle."""
from types import SimpleNamespace as NS

import pytest

from chat import agent as A


def tu(i, name, inp):
    return NS(type="tool_use", id=i, name=name, input=inp)


def tx(t):
    return NS(type="text", text=t)


def rep(*content, stop="end_turn"):
    return NS(stop_reason=stop, content=list(content))


@pytest.fixture
def faux(monkeypatch, passerelle):
    vus = []

    def installer(*script):
        class M:
            def create(self, **kw):
                vus.append(kw)
                return script[len(vus) - 1]
        monkeypatch.setattr(A, "_client", lambda: NS(beta=NS(messages=M())))
        return vus
    return installer


PROJ = {"profession": "kines", "territoire": "Puy-de-Dôme", "leviers": {"quotas": 1.2}, "annees": [2050]}


def test_reponse_rattachee(faux):
    vus = faux(rep(tu("a", "projeter", PROJ), stop="tool_use"),
               rep(tx("En 2050, environ 1 930 kinés libéraux dans le Puy-de-Dôme, entre 1 400 et 2 500 (tendanciel 1 730).")))
    r = A.Conversation("llm").envoyer("kinés Puy-de-Dôme +20 % places")
    assert r["verification"]["statut"] == "ok"
    assert [g["type"] for g in r["graphiques"]] == ["projection"]
    contenu = vus[1]["messages"][2]["content"][0]["content"]
    assert "_serie" not in contenu                      # séries brutes réservées aux graphiques
    sysp = vus[0]["system"][0]["text"]
    assert A.HORS in sysp and "hors_perimetre" in sysp and "medecins" in sysp


def test_nombre_invente_corrige(faux):
    vus = faux(rep(tu("a", "projeter", PROJ), stop="tool_use"),
               rep(tx("Environ 1 930 kinés en 2050 ; la DREES en compte 92 000 en France.")),
               rep(tx("En 2050, environ 1 930 kinés libéraux dans le Puy-de-Dôme, entre 1 400 et 2 500.")))
    c = A.Conversation("llm")
    r = c.envoyer("kinés Puy-de-Dôme +20 % places")
    assert r["verification"] == {"statut": "corrigee", "non_rattaches": ["92 000"]}
    assert "92 000" not in r["texte"]
    assert "Vérification automatique" in c.messages[-2]["content"] and c.messages[-2]["role"] == "user"


def test_nombre_invente_bloque(faux):
    faux(rep(tx("Il y aura 4 200 médecins généralistes à Lyon en 2035.")),
         rep(tx("Je maintiens : 4 200 médecins.")))
    r = A.Conversation("llm").envoyer("Combien de médecins à Lyon en 2035 ?")
    assert r["verification"]["statut"] == "bloquee"
    assert "4 200" in r["verification"]["non_rattaches"] and "Réponse retenue" in r["texte"]


def test_hors_perimetre_sans_nombre(faux):
    faux(rep(tu("p", "perimetre", {}), stop="tool_use"),
         rep(tx(f"{A.HORS} : médecine générale hors périmètre ; spécialités prévues en phase 2.")))
    r = A.Conversation("llm").envoyer("Combien de généralistes à Lyon ?")
    assert r["verification"]["statut"] == "ok" and r["texte"].startswith(A.HORS)


def test_erreur_d_outil_renvoyee_au_modele(faux):
    vus = faux(rep(tu("a", "projeter", {"profession": "kines", "leviers": {"quotas": 3}}), stop="tool_use"),
               rep(tx("Le modèle accepte au plus +50 % de places (borne 1,5).")))
    r = A.Conversation("llm").envoyer("tripler les places de kinés")
    tr = vus[1]["messages"][2]["content"][0]
    assert tr["is_error"] is True and "hors bornes" in tr["content"]
    assert r["appels"][0]["erreur"] and r["verification"]["statut"] == "ok"


def test_mode_deterministe_hors_perimetre(passerelle):
    r = A.Conversation("deterministe").envoyer("Combien de médecins généralistes à Lyon en 2035 ?")
    assert r["texte"].startswith(f"**{A.HORS}")
    r = A.Conversation("deterministe").envoyer("kinés en France en 2070")
    assert A.HORS in r["texte"]


def test_mode_deterministe_projection_et_contexte(passerelle):
    c = A.Conversation("deterministe")
    r = c.envoyer("Combien de kinés dans le Puy-de-Dôme si on augmente de 20 % les quotas ?")
    assert "1 930" in r["texte"] and "Puy-de-Dôme" in r["texte"] and "En 2050" in r["texte"]
    assert "En 2035" in c.envoyer("Et en 2035 ?")["texte"]
    r = c.envoyer("Et si on recule la retraite de 2 ans ?")
    assert "Puy-de-Dôme" in r["texte"]
    r = c.envoyer("les infirmiers à Lyon")
    assert A.LIMITE in r["texte"]                       # ville ramenée au département


def test_cle_refusee_bascule_sans_ia(monkeypatch, passerelle):
    import anthropic
    import httpx2

    class M:
        def create(self, **kw):
            req = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
            raise anthropic.AuthenticationError("invalid x-api-key", response=httpx2.Response(401, request=req), body=None)
    monkeypatch.setattr(A, "_client", lambda: NS(beta=NS(messages=M())))
    c = A.Conversation("llm")
    r = c.envoyer("Combien de kinés dans le Puy-de-Dôme si on augmente de 20 % les quotas ?")
    assert r["mode"] == "deterministe" and "Clé d'API refusée" in r["texte"] and "1 930" in r["texte"]
    assert c.mode == "deterministe" and c.messages == []


def test_objectif_deterministe(passerelle):
    r = A.Conversation("deterministe").envoyer("comment augmenter de 20% la densité des dentistes en ile de France en 2050")
    t = r["texte"]
    assert "Objectif compris" in t and "Île-de-France" in t and "tendanciel" in t
    assert "Leviers qui suffisent seuls" in t and "Places en formation : +35 %" in t
    assert "ne suffisent pas" in t and r["appels"][0]["outil"] == "atteindre"
    assert [g["type"] for g in r["graphiques"]] == ["objectif"]


def test_quantite_non_comprise_signalee(passerelle):
    r = A.Conversation("deterministe").envoyer("améliorer de 15 % l'attractivité des kinés en Bretagne")
    assert r["texte"].startswith("**Je n'ai pas reconnu de levier")
