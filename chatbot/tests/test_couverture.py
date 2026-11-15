"""Couverture (module de besoin) : levier L23 de bout en bout dans l'assistant, et interdit MG (règle O2)."""
import re

import pytest

from chat import agent as A
from chat import client as C

MG = re.compile(r"m[ée]decin|g[ée]n[ée]raliste|sp[ée]cialiste|\bMG\b", re.I)


def test_interpreter_l23_avec_date(passerelle):
    r, err = C.requete("interpreter_phrase", {"texte": "Généraliser la vaccination en officine à partir de 2028 dans le Rhône."})
    assert err is None
    assert [(x["id"], x["t0"], x["cible"]) for x in r["transferts"]] == [("L23", 2028, "pharmaciens")]
    assert r["profession"] == "pharmaciens" and r["territoire"] == "D69"


@pytest.mark.parametrize("texte,id_", [("Accès direct aux infirmiers en pratique avancée dans l'Hérault.", "ipa"),
                                       ("Accès direct au kinésithérapeute sans ordonnance en Occitanie.", "acces_direct"),
                                       ("Les pharmaciens prennent la tension et dépistent le diabète.", "tension_diabete")])
def test_transferts_non_mesurables_restent_hors_modele(passerelle, texte, id_):
    r, _ = C.requete("interpreter_phrase", {"texte": texte})
    assert r["transferts"] == []
    x = next(x for x in r["non_modelise"] if x["id"] == id_)
    assert "non mesurable" in x["raison"] and "Effectif inchangé" in x["raison"]


def test_couverture_l23_ecart_au_tendanciel(passerelle):
    r, err = C.requete("couverture", {"profession": "pharmaciens", "territoire": "Puy-de-Dôme", "l23": True, "annees": [2035]})
    assert err is None
    a = r["annees"][0]
    assert a["indice_scenario"] < a["indice_tendanciel"] and a["ecart_tendanciel_pct"] < 0
    assert "fourchette_estimateurs" not in a                      # pharmaciens : estimateur servi seul
    assert r["reference"] == 2026 and "inchangé" in r["effectif"]
    assert r["transferts"][0]["cible"] == "pharmaciens" and r["transferts"][0]["actes_mg_liberes_france"] > 0


def test_couverture_fourchette_kines(passerelle):
    r, _ = C.requete("couverture", {"profession": "kines", "territoire": "FR", "l23": False, "annees": [2050]})
    lo, hi = r["annees"][0]["fourchette_estimateurs"]
    assert lo < r["annees"][0]["indice_scenario"] < hi


@pytest.mark.parametrize("prof", ["medecine-generale", "specialistes", "generalistes"])
def test_couverture_mg_refusee(passerelle, prof):
    r, err = C.requete("couverture", {"profession": prof, "territoire": "FR"})
    assert r is None and err                                       # schéma (5 professions) ou règle O2


def test_deterministe_l23_effectif_inchange_et_couverture(passerelle):
    out = A.Conversation(mode="deterministe").envoyer(
        "Si les pharmaciens peuvent vacciner, combien de pharmaciens à Clermont-Ferrand en 2035 ?")
    t = out["texte"]
    assert "effectif inchangé dans le modèle" in t and "Couverture des pharmaciens" in t
    assert "Hors du périmètre du modèle : Vaccination" not in t and "vaccinations en moins pour eux" in t
    assert "libérés" not in t and "ETP" not in t
    assert "besoin couvert" not in t.replace("part du besoin couverte", "")
    autres = [x for x in t.split("\n\n") if not x.startswith("Si les pharmaciens vaccinent davantage")]
    assert not MG.search("\n".join(autres))                       # la MG n'apparaît que comme source du transfert
    assert not re.search(r"couverture des m[ée]decins", t, re.I)
    assert [x["outil"] for x in out["appels"]] == ["projeter", "couverture"]


def test_deterministe_couverture_mg_jamais(passerelle):
    out = A.Conversation(mode="deterministe").envoyer("Quelle couverture pour les médecins généralistes en 2035 ?")
    assert out["texte"].startswith(f"**{A.HORS}") and out["appels"] == []    # aucun indice demandé ni montré
    assert not re.search(r"\d,\d\d", out["texte"])


def test_prompt_interdit_mg_et_vocabulaire(passerelle):
    s = A.systeme(C.requete("perimetre", {})[0])
    assert "Jamais de couverture, de besoin ni d'indice" in s and "Effectif inchangé dans le modèle" in s
    assert any(h["id"] == "couverture_medecins" for h in C.requete("perimetre", {})[0]["hors_perimetre"])


def test_intention_couverture_sans_l23_fourchette(passerelle):
    out = A.Conversation(mode="deterministe").envoyer("Quelle couverture des kinés en Auvergne-Rhône-Alpes en 2050 ?")
    assert out["appels"][-1]["outil"] == "couverture" and out["appels"][-1]["entree"]["l23"] is False
    assert "l'indice au scénario va de" in out["texte"]


def test_couverture_mg_dit_o2(passerelle):
    t = A.Conversation(mode="deterministe").envoyer("couverture des médecins généralistes en 2035")["texte"]
    assert "O2" in t and t.startswith(f"**{A.HORS}")
