"""Registre des variantes candidates au banc de prévision (axe 3, niveau 1).

Règle (protocole N1, SHA-256 eb527ecb06a0…) : une variante est confirmatoire seulement si elle est
inscrite ici, datée, AVANT son premier passage sur le banc. Une inscription postérieure est exploratoire.
Chaque entrée : nom -> (date d'inscription, statut, fabrique de l'estimateur, note).
"""


def _twin_local():
    from sante.estimators import StockFlowLocal
    from jumeau.estimators import twin_of
    return twin_of(StockFlowLocal)


def _persistence():
    from sante.estimators import Persistence
    return Persistence


def _trend():
    from sante.estimators import LinearTrend
    return LinearTrend


REGISTRY = {
    "naive_persistance": ("2026-11-14", "référence", _persistence, "référence naïve"),
    "naive_tendance": ("2026-11-14", "référence", _trend, "référence naïve"),
    "jumeau_taux_locaux": ("2026-11-14", "confirmatoire", _twin_local,
                           "variante par défaut : stock-flux taux locaux (poids 200), entrées plates, rétention ≤ 1"),
}


def get(name: str):
    return REGISTRY[name][2]()


# --- Inscriptions de l'axe 2 (session axe 2), 2026-11-14 03:25, AVANT tout passage sur le banc. ---
# Dérivation et prédictions écrites : v2/docs/lab/derivations/2026-11-14-axe2-methodes.md (SHA-256 1c324f5795b0).
# Périmètre confirmatoire : privé central (methodes.perimetres.prive) ; ancien périmètre en secondaire.
def _axe2(cls_name):
    def f():
        from methodes import estimators
        return getattr(estimators, cls_name)
    return f


REGISTRY.update({
    "axe2_ages_interp": ("2026-11-14", "confirmatoire", _axe2("AgesInterp"),
                         "A1a : vieillissement non uniforme dans la tranche (désagrégation linéaire chaque année)"),
    "axe2_ages_simples": ("2026-11-14", "confirmatoire", _axe2("AgesSimples"),
                          "A1b : état en âges simples, cohortes suivies"),
    "axe2_shrink_hier": ("2026-11-14", "confirmatoire", _axe2("ShrinkHier"),
                         "A2 : shrinkage dép -> région -> national, k = 200 aux deux niveaux"),
    "axe2_retention60": ("2026-11-14", "confirmatoire", _axe2("Retention60"),
                         "A3 : rétention des 60 ans et plus en tendance (pente nationale, λ = 1)"),
    "axe2_combine": ("2026-11-14", "confirmatoire", _axe2("Combine"), "A123 : A1a + A2 + A3, pré-spécifiée"),
    "axe2_obs_r12": ("2026-11-14", "diagnostic", _axe2("ObservatoireR12"),
                     "B4 : schéma de l'observatoire (r borné à [0,5 ; 1,2]) ; pas candidat"),
})


# --- Axe 2, étape 1 du programme (APC des sorties), inscrit 2026-11-14 03:58 AVANT tout passage sur le banc. ---
# Dérivation et prédictions : v2/docs/lab/derivations/2026-11-14-axe2-apc-sorties.md (SHA-256 a933da1958e2).
def _axe2_apc():
    from methodes.apc import APCEstimator
    return APCEstimator


REGISTRY["axe2_apc"] = ("2026-11-14", "confirmatoire", _axe2_apc,
                        "APC gaussien de la rétention nette (Bayes empirique), période prolongée à plat ; "
                        "périmètre privé ; CRPS et PIT à h = 5 en secondaire")


# --- Axe 2, étape 2 (cohortes bayésiennes, entrées probabilistes), inscrit 2026-11-14 04:41 AVANT le banc. ---
# Dérivation : v2/docs/lab/derivations/2026-11-14-axe2-cohortes-bayesiennes.md (SHA-256 b608b1ac0c69, version avec l'écart d'avant inscription).
# Écart signalé : un pilote (dentistes et sages-femmes, origine 2021) a vu les cibles 2026 avant cette inscription.
def _axe2_coh(cls_name):
    def f():
        from methodes import cohortes
        return getattr(cohortes, cls_name)
    return f


REGISTRY.update({
    "axe2_cohortes_c1": ("2026-11-14", "confirmatoire", _axe2_coh("CohortesEstimator"),
                         "C1 : APC des sorties + entrées en niveau local national × parts hiérarchiques, θ fixé ; "
                         "N1 (moyenne a posteriori) et N6 (200 tirages)"),
    "axe2_cohortes_c2": ("2026-11-14", "confirmatoire", _axe2_coh("CohortesLaplace"),
                         "C2 : comme C1, θ propagé par Laplace sur log θ"),
})


# --- C1-GBM (session c1-gbm), 2026-11-15 : apprentissage automatique global contre A2. ---
# Inscription et test d'abandon : v2/docs/lab/derivations/2026-11-15-c1-gbm-global.md (SHA-256 8e35043aecb2, commit 70f8bc9).
# Boîtes noires : classées « diagnostic » (plafond de précision), jamais présentées comme le modèle.
def _c1_global(cls_name):
    def f():
        from methodes import gbm
        return getattr(gbm, cls_name)
    return f


REGISTRY.update({
    "c1_gbm_global": ("2026-11-15", "diagnostic", _c1_global("GlobalGBM"),
                      "GBM global à un pas (profession × dép × sexe × âge), itéré ; lire GlobalGBM.panel avant usage"),
    "c1_mlp_global": ("2026-11-15", "diagnostic", _c1_global("GlobalMLP"), "MLP (32, 16), même panel et même itération"),
})
