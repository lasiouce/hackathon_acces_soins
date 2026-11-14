"""Chatbot du jumeau dans une application Streamlit.

Le composant n'importe ni le modèle ni le modèle de langage : il appelle l'API HTTP du chatbot (chat/server.py,
POST /api/chat). Les garde-fous (passerelle en lecture seule, vérification des nombres, périmètre) restent donc
entièrement côté chatbot, et l'application Streamlit n'a besoin d'aucune clé d'API.

Intégration dans une application existante (copier ce fichier à côté de l'application) :

    from chatbot_streamlit import afficher_chatbot
    afficher_chatbot()                                  # n'importe où dans une page

ou comme page dédiée : voir pages_exemple/1_Chatbot.py. Variable CHATBOT_URL (défaut http://localhost:8768).
Dépendances : streamlit (altair et requests sont fournis avec).
"""
from __future__ import annotations

import os
import uuid

import altair as alt
import pandas as pd
import requests
import streamlit as st

CHATBOT_URL = os.environ.get("CHATBOT_URL", "http://localhost:8768")
EXEMPLES = [
    "Combien de kinés libéraux dans le Puy-de-Dôme en 2035 si on augmente de 20 % les places en formation ?",
    "Comment augmenter de 20 % la densité des dentistes en Île-de-France en 2050 ?",
    "Combien de médecins généralistes à Lyon en 2035 ?",
]
BLEU, GRIS, SOMBRE = "#2457a6", "#8a93a3", "#1d2330"
VERIF = {"ok": "✓ Chaque nombre de cette réponse vient d'un résultat du modèle.",
         "corrigee": "✓ Réponse corrigée par la vérification automatique.",
         "bloquee": "⚠ Réponse bloquée par la vérification automatique."}


# ------------------------------------------------------------------ appels à l'API du chatbot

def _etat() -> dict:
    try:
        return requests.get(f"{CHATBOT_URL}/api/etat", timeout=5).json()
    except requests.RequestException:
        return {"mode": "injoignable"}


def _envoyer(sid: str, message: str) -> dict:
    try:
        r = requests.post(f"{CHATBOT_URL}/api/chat", json={"session": sid, "message": message}, timeout=180)
        return r.json()
    except requests.RequestException as e:
        return {"erreur": f"chatbot injoignable sur {CHATBOT_URL} ({type(e).__name__}) : lancer scripts/lancer.sh"}


def _reinitialiser(sid: str) -> None:
    try:
        requests.post(f"{CHATBOT_URL}/api/reset", json={"session": sid}, timeout=5)
    except requests.RequestException:
        pass


# ------------------------------------------------------------------ graphiques (données renvoyées par le chatbot)

def _graphique(g: dict) -> alt.Chart | None:
    t = g.get("type")
    if t == "projection":
        df = pd.DataFrame({"annee": g["annees"], "Tendanciel": g["tendanciel"], "Scénario": g["scenario"],
                           "bas": [b[0] for b in g["bande"]], "haut": [b[1] for b in g["bande"]]})
        obs = pd.DataFrame(g["observe"], columns=["annee", "Observé (RPPS)"])
        x = alt.X("annee:Q", title=None, axis=alt.Axis(format="d"))
        bande = alt.Chart(df).mark_area(opacity=0.18, color=BLEU).encode(x=x, y=alt.Y("bas:Q", title="professionnels"), y2="haut:Q")
        lignes = alt.Chart(df).transform_fold(["Tendanciel", "Scénario"], as_=["serie", "valeur"]).mark_line(strokeWidth=2.5).encode(
            x=x, y="valeur:Q", color=alt.Color("serie:N", scale=alt.Scale(domain=["Tendanciel", "Scénario"], range=[GRIS, BLEU]),
                                               legend=alt.Legend(title=None, orient="top")),
            strokeDash=alt.condition(alt.datum.serie == "Tendanciel", alt.value([5, 4]), alt.value([1, 0])),
            tooltip=["annee:Q", "serie:N", alt.Tooltip("valeur:Q", format=",.0f")])
        points = alt.Chart(obs).mark_line(point=True, color=SOMBRE).encode(x=x, y="Observé (RPPS):Q",
                                                                            tooltip=["annee:Q", alt.Tooltip("Observé (RPPS):Q", format=",.0f")])
        return (bande + lignes + points).properties(height=280)
    if t == "comparaison":
        rows = [{"annee": a, "scenario": "Tendanciel", "valeur": v} for a, v in zip(g["tendanciel"]["annees"], g["tendanciel"]["valeurs"])]
        for s in g["scenarios"]:
            rows += [{"annee": a, "scenario": s["nom"], "valeur": v} for a, v in zip(s["annees"], s["valeurs"])]
        return alt.Chart(pd.DataFrame(rows)).mark_line(strokeWidth=2.2).encode(
            x=alt.X("annee:Q", title=None, axis=alt.Axis(format="d")), y=alt.Y("valeur:Q", title="professionnels"),
            color=alt.Color("scenario:N", legend=alt.Legend(title=None, orient="top")),
            tooltip=["annee:Q", "scenario:N", alt.Tooltip("valeur:Q", format=",.0f")]).properties(height=280)
    if t == "barres":
        df = pd.DataFrame({"reglage": g["etiquettes"], "scenario": g["valeurs"], "bas": g["bas"], "haut": g["haut"]})
        x = alt.X("reglage:N", title=None, sort=None)
        return (alt.Chart(df).mark_bar(color=BLEU).encode(x=x, y=alt.Y("scenario:Q", title="professionnels"),
                                                           tooltip=["reglage", alt.Tooltip("scenario:Q", format=",.0f")])
                + alt.Chart(df).mark_rule(color=SOMBRE).encode(x=x, y="bas:Q", y2="haut:Q")).properties(height=260)
    if t == "objectif":
        df = pd.DataFrame({"levier": g["etiquettes"], "valeur": g["valeurs"],
                           "suffit": ["suffit seul" if x else "ne suffit pas" for x in g["suffit"]]})
        barres = alt.Chart(df).mark_bar().encode(
            y=alt.Y("levier:N", sort=None, title=None), x=alt.X("valeur:Q", title=None),
            color=alt.Color("suffit:N", scale=alt.Scale(domain=["suffit seul", "ne suffit pas"], range=[BLEU, "#b9c7e0"]),
                            legend=alt.Legend(title=None, orient="top")),
            tooltip=["levier", alt.Tooltip("valeur:Q", format=",.1f"), "suffit"])
        cible = alt.Chart(pd.DataFrame({"cible": [g["cible"]]})).mark_rule(color=SOMBRE, strokeDash=[4, 3]).encode(x="cible:Q")
        return (barres + cible).properties(height=max(160, 30 * len(df)))
    if t == "classement":
        df = pd.DataFrame({"departement": g["etiquettes"], "valeur": g["valeurs"]})
        return alt.Chart(df).mark_bar(color=BLEU).encode(
            y=alt.Y("departement:N", sort=None, title=None), x=alt.X("valeur:Q", title=g.get("sous_titre", "")),
            tooltip=["departement", alt.Tooltip("valeur:Q", format=",.1f")]).properties(height=max(160, 24 * len(df)))
    return None


def _afficher_reponse(r: dict) -> None:
    if r.get("erreur"):
        st.error(r["erreur"])
        return
    st.markdown(r.get("texte", ""))
    for g in (r.get("graphiques") or [])[:4]:
        ch = _graphique(g)
        if ch is not None:
            st.markdown(f"**{g['titre']}**  \n<small>{g.get('sous_titre', '')}</small>", unsafe_allow_html=True)
            st.altair_chart(ch, use_container_width=True)
    appels = r.get("appels") or []
    if appels:
        with st.expander(f"Calculs lancés sur le jumeau ({len(appels)})"):
            for a in appels:
                st.markdown(f"{'⚠ ' if a['erreur'] else ''}**{a['outil']}** · {a['resume']} · {a['ms']} ms")
                st.json(a["entree"], expanded=False)
    v = (r.get("verification") or {}).get("statut")
    if r.get("mode") == "llm" and v in VERIF:
        st.caption(VERIF[v])
    st.caption(("Interprété par IA" if r.get("mode") == "llm" else "Interprété par le glossaire")
               + (", calculé par le jumeau" if appels else ", aucun calcul lancé") + f" · {r.get('duree_s', '?')} s")


# ------------------------------------------------------------------ composant

def afficher_chatbot(cle: str = "jumeau", titre: str | None = "Dialoguer avec le jumeau") -> None:
    """Affiche le chatbot. `cle` isole l'historique si le composant apparaît plusieurs fois dans l'application."""
    ss = st.session_state
    ss.setdefault(f"{cle}_sid", str(uuid.uuid4()))
    ss.setdefault(f"{cle}_hist", [])
    sid, hist = ss[f"{cle}_sid"], ss[f"{cle}_hist"]

    if titre:
        st.subheader(titre)
    e = _etat()
    col1, col2 = st.columns([4, 1])
    with col1:
        if e.get("mode") in ("injoignable", "indisponible"):
            st.warning(f"Chatbot injoignable sur {CHATBOT_URL} : lancer `scripts/lancer.sh` dans le dépôt jumeau-chat.")
        else:
            mode = f"IA : {e.get('modele')}" if e.get("mode") == "llm" else "mode déterministe (sans clé d'API)"
            st.caption(f"{mode} · modèle {e.get('version_modele', {}).get('commit', '?')} · effectif libéral, par département, "
                       "jusqu'en 2050 · projection sous hypothèses, pas une prévision")
    with col2:
        if st.button("Nouvelle conversation", key=f"{cle}_reset"):
            _reinitialiser(sid)
            ss[f"{cle}_sid"], ss[f"{cle}_hist"] = str(uuid.uuid4()), []
            st.rerun()

    for role, contenu in hist:
        with st.chat_message(role):
            st.markdown(contenu) if role == "user" else _afficher_reponse(contenu)

    question = None
    if not hist:
        cols = st.columns(len(EXEMPLES))
        for c, ex in zip(cols, EXEMPLES):
            if c.button(ex, key=f"{cle}_ex_{hash(ex)}", use_container_width=True):
                question = ex
    question = st.chat_input("Ex. : combien de kinés libéraux dans le Puy-de-Dôme en 2035 si on forme 20 % de plus ?",
                             key=f"{cle}_input") or question
    if question:
        hist.append(("user", question))
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Le jumeau calcule…"):
                r = _envoyer(sid, question)
            _afficher_reponse(r)
        hist.append(("assistant", r))
