"""Sorties (retraite, décès, cessation, nettes des reprises) : N <- s · N, s = rétention nette annuelle.

s est ajusté par profession × territoire × sexe × âge (sante.model.fit_rates, plafonné à 1). Les leviers
agissent sur les taux de sortie e = 1 − s.

decalage_retraite Δ (ans) : levier retraite corrigé, repris de l'observatoire de l'équipe (B1, décision
« Reprise de l'observatoire ») ; il remplace le masque v1 `e[60–69] × (1 − Δ/5)`, qui touchait aussi la
tranche ouverte de façon permanente (séjour infini pour Δ ≥ 5, seconde revue) :
  tranches de 65 ans et plus   e' = e / (1 + λ e)     séjour moyen 1/e' = 1/e + λ dans une tranche ouverte.
                               Une seule tranche ≥ 65 (ouverte) : λ = Δ. Plusieurs (65–69, 70–74, 75+) : λ est
                               choisi par cellule pour que le temps espéré passé en 65+ par une personne qui
                               entre en 65–69 augmente de Δ exactement (chaîne de Markov : vieillissement f,
                               rétention s ; fonction sejour_65plus).
  60–64                        e' = e · max(0, 1 − Δ/5)    (20 % de sorties en moins par an de report)
  55–59                        e' = e · max(0, 1 − Δ/10)   (demi-effet)
  tranches à solde net positif (s plafonné à 1, e = 0) : inchangées.
La montée en charge (3 mois par an) se fait dans le scénario : evenement_retraite().
cumul_multiplicateur k : e[65+] × max(0, 1 − part_cumul_p · (k − 1)), part_cumul par profession (COR 2016).
multiplicateur_precoces m : e[âge < 60] × m (départs précoces ; effet d'une politique non chiffré, supposé).
Le chemin v1 (app/levers.perturb_retention) n'est plus reproduit pour ce levier : la v1 porte le défaut.
"""
import math

import numpy as np

from jumeau.history import SOURCE_RPPS, stock_flow_rates
from jumeau.module import Module, Param, Rate, par_profession, register
from jumeau.scenario import Event

# Part des cotisants libéraux en cumul emploi-retraite au 30/06/2015 (COR 2016, doc. 11, annexe 2 ; fiche axe 1
# param-cumul-emploi-retraite). MK et IDE non séparables (CARPIMKO). Spécialistes : médecins, DREES ER n° 1097 (2018).
PART_CUMUL = {"sages-femmes": 0.008, "dentistes": 0.047, "pharmaciens": 0.018, "kines": 0.015, "infirmiers": 0.015,
              "specialistes": 0.10}


def evenement_retraite(delta: float, decision: int, pas: float = 0.25, selector: dict | None = None,
                       source: str = "") -> list:
    """Report de Δ ans décidé l'année `decision`, monté de `pas` an par an à partir de decision + 1."""
    n = max(1, math.ceil(delta / pas - 1e-12))
    return [Event("sorties.decalage_retraite", decision + 1 + i, min(delta, pas * (i + 1)), "set",
                  end=None if i == n - 1 else decision + 1 + i, selector=selector or {}, source=source)
            for i in range(n)]


def sejour_65plus(s65: np.ndarray, f: float) -> np.ndarray:
    """Temps espéré (années de présence, année d'entrée comprise) dans les tranches ≥ 65 pour une personne qui entre
    dans la première d'entre elles. s65 : rétention [cellule, J] ; f : fraction de vieillissement (tranches fermées).
    Ordre du moteur : vieillissement puis rétention de la tranche d'arrivée."""
    n, J = s65.shape
    Q = np.zeros((n, J, J))
    for j in range(J):
        if j < J - 1:
            Q[:, j, j] = (1 - f) * s65[:, j]
            Q[:, j, j + 1] = f * s65[:, j + 1]
        else:
            Q[:, j, j] = s65[:, j]
    M = np.linalg.inv(np.eye(J)[None] - Q)
    return M[:, 0, :].sum(axis=1)


def lambda_65plus(s65: np.ndarray, delta: np.ndarray, f: float, iters: int = 60) -> np.ndarray:
    """λ par cellule tel que sejour_65plus(e/(1+λe)) = sejour_65plus(e) + Δ (bissection ; Δ = 0 ou séjour infini → 0)."""
    e = 1 - s65
    ok = (e[:, -1] > 0) & (delta > 0)
    lam = np.zeros(len(s65))
    if not ok.any():
        return lam
    target = sejour_65plus(s65[ok], f) + delta[ok]
    lo, hi = np.zeros(ok.sum()), np.maximum(delta[ok], 1.0) * 4
    T = lambda l: sejour_65plus(1 - e[ok] / (1 + l[:, None] * e[ok]), f)
    while (T(hi) < target).any():                      # élargir jusqu'à encadrer la cible
        hi = np.where(T(hi) < target, hi * 2, hi)
    for _ in range(iters):
        mid = (lo + hi) / 2
        below = T(mid) < target
        lo, hi = np.where(below, mid, lo), np.where(below, hi, mid)
    lam[ok] = (lo + hi) / 2
    return lam


@register
class Sorties(Module):
    name = "sorties"
    order = 20
    params = (
        Param("retention", None, "par an", SOURCE_RPPS, "fenêtre d'ajustement", "mesuré",
              "Rétention nette annuelle par cellule × âge, moindres carrés sur la fenêtre, plafonnée à 1.", (0.0, 1.0)),
        Param("decalage_retraite", 0.0, "années", "Loi n° 2023-270 ; LFSS 2026 ; mécanisme B1 de l'observatoire",
              "2023", "supposé", "Report de l'âge de départ ; séjour en 65+ allongé de Δ ans.", (0.0, 5.0), "retenir"),
        Param("cumul_multiplicateur", 1.0, "× part 2015", "COR 2016 (parts par profession) ; effet : hypothèse",
              "2015", "supposé", "Incitation au cumul emploi-retraite : sorties en 65+ × (1 − part · (k − 1)).",
              (0.0, 5.0), "retenir"),
        Param("part_cumul", PART_CUMUL, "part, par profession",
              "COR 2016, doc. 11, annexe 2 (CARCDSF, CAVP, CARPIMKO) ; médecins : DREES ER n° 1097",
              "30/06/2015 ; médecins 2018", "sourcé",
              "Part des libéraux en cumul emploi-retraite ; MK et IDE confondus (1,5 %).", (0.0, 1.0)),
        Param("multiplicateur_precoces", 1.0, "× taux de sortie avant 60 ans",
              "mécanisme : taux de sortie ajustés ; aucune source ne chiffre l'effet d'une politique (fiche "
              "param-cessation-par-age)", "—", "supposé",
              "Départs précoces (reconversions, cessations avant 60 ans) : e[âge < 60] × m.", (0.0, 3.0), "retenir"),
    )

    def fit(self, hist):
        self.hist = hist

    def step(self, state, ctx):
        s = ctx.param(self, "retention", base=stock_flow_rates(self.hist, state)[0])
        d, k = ctx.param(self, "decalage_retraite"), ctx.param(self, "cumul_multiplicateur")
        mp = ctx.param(self, "multiplicateur_precoces")
        if np.any(d != 0) or np.any(k != 1) or np.any(mp != 1):
            a = state.ages
            col = lambda v: np.reshape(v, (-1, 1)) if np.ndim(v) else v
            d = col(d)
            e = 1.0 - s
            old = a >= 65
            if old.sum() > 1 and np.any(d != 0):         # plusieurs tranches ≥ 65 : λ par cellule (séjour + Δ exact)
                f = float(np.atleast_1d(ctx.param_of("vieillissement", "fraction", 0.2))[0])
                dd = (np.broadcast_to(np.ravel(d), (len(s),)).astype(float) if np.size(d) > 1
                      else np.full(len(s), float(np.ravel(d)[0])))
                key = (id(s), s.shape, f, dd.tobytes())     # s ajusté est le même objet d'une année à l'autre
                cache = self.__dict__.setdefault("_lam", {})
                if key not in cache:
                    if len(cache) > 64:
                        cache.clear()
                    cache[key] = lambda_65plus(s[:, old], dd, f)[:, None]
                lam = cache[key]
            else:
                lam = d
            m6064, m5559 = (a >= 60) & (a < 65), (a >= 55) & (a < 60)     # colonnes seulement (coût ∝ tranches touchées)
            if np.any(d != 0):
                e[:, old] = e[:, old] / (1.0 + lam * e[:, old])
                e[:, m6064] = e[:, m6064] * np.maximum(0.0, 1.0 - d / 5.0)
                e[:, m5559] = e[:, m5559] * np.maximum(0.0, 1.0 - d / 10.0)
            if np.any(k != 1):
                part = col(par_profession(ctx.param(self, "part_cumul"), state.cells.profession))
                e[:, old] = e[:, old] * np.maximum(0.0, 1.0 - part * (col(k) - 1.0))
            if np.any(mp != 1):
                young = a < 60
                e[:, young] = np.minimum(1.0, e[:, young] * col(mp))
            s = 1.0 - e
        return [Rate(self.name, s, to="sorties")]
