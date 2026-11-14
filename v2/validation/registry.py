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
