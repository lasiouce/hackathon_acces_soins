"""Opérateur de transfert de tâches (dérivation du 2026-11-15, §6), appliqué au besoin seulement.

Un transfert d'un acte de A (source) vers B (cible), autorisé à la date t₀ :
  s(t)    = max(0, s_∞ · (1 − e^{−(t − t₀)/τ}) − s_déjà)   pour t ≥ t₀, 0 avant     (montée en charge, pas une décision)
            s_déjà : part déjà atteinte à l'année de base, déjà dans la demande de base (0 par défaut ; L23 : P1-4)
  B'_A    = B_A · (1 − s·a)
  B'_B    = B_B + s·a·B_A·k + m,   m = μ · s·a·B_A·k                 (expansion du recours, μ = 0 par défaut)
  ΣB' − ΣB = s·a·B_A·(k − 1) + m                                      (conservation, testée à 10⁻⁶)
Contraintes : 0 ≤ s·a ≤ 1 à toute date, k > 0, τ > 0, μ ≥ 0 ; la cible n'est jamais dans SANS_COUVERTURE (O2 : la
médecine générale et les spécialistes sont des sources seulement).

Les effectifs ne sont jamais lus ni écrits ici : un transfert change B, donc C, pas l'offre (pas de rétroaction, N9).
"""
from dataclasses import dataclass, replace

import numpy as np

from jumeau.module import Param

from besoin.couverture import SANS_COUVERTURE
from besoin.cube import Cube

PLACEHOLDER = "placeholder en attendant les fiches de l'axe 1"


@dataclass(frozen=True)
class Transfert:
    name: str
    source: str
    cible: str
    a: float          # part du besoin de A (en temps) qui porte sur l'acte
    k: float          # t_B / t_A : temps de B par unité de temps de A libérée
    s_inf: float      # part transférée à terme
    tau: float        # années
    t0: int           # date d'autorisation
    mu: float = 0.0   # expansion : actes ajoutés par acte transféré, en temps de B
    s_deja: float = 0.0   # part déjà atteinte à l'année de base (incluse dans la demande de base) : seul le reste agit

    def __post_init__(self):
        if self.cible in SANS_COUVERTURE:
            raise ValueError(f"{self.name} : cible {self.cible!r} interdite (O2 : source seulement)")
        if self.source == self.cible:
            raise ValueError(f"{self.name} : source = cible")
        if not (self.k > 0 and self.tau > 0 and self.mu >= 0):
            raise ValueError(f"{self.name} : k > 0, τ > 0 et μ ≥ 0 exigés (k={self.k}, τ={self.tau}, μ={self.mu})")
        if not (0 <= self.s_inf * self.a <= 1 and 0 <= self.s_inf and 0 <= self.a):
            raise ValueError(f"{self.name} : 0 ≤ s·a ≤ 1 exigé (s_∞·a = {self.s_inf * self.a:.4g})")

    def s(self, years) -> np.ndarray:
        h = np.asarray(years, dtype=float) - self.t0
        s = np.where(h >= 0, self.s_inf * (1 - np.exp(-np.maximum(h, 0) / self.tau)), 0.0)
        return np.maximum(s - self.s_deja, 0.0) if self.s_deja else s


def appliquer(B: Cube, transferts=()) -> tuple[Cube, list[dict]]:
    """B' et le détail par transfert (temps libéré chez A, ajouté chez B, expansion m), dans l'ordre donné.
    Sans transfert, ou avec s ≡ 0, B' a les mêmes valeurs que B, bit à bit."""
    if not transferts:
        return B, []
    V = B.values.copy()
    detail = []
    for tr in transferts:
        i, j = B.p(tr.source), B.p(tr.cible)
        sa = tr.s(B.years) * tr.a                                   # [année], 0 ≤ s·a ≤ 1 par construction
        libere = V[i] * sa[None, :]                                 # s·a·B_A [territoire, année]
        recu = libere * tr.k
        m = tr.mu * recu
        V[i] = V[i] * (1 - sa[None, :])
        V[j] = V[j] + recu + m
        detail.append(dict(transfert=tr.name, source=tr.source, cible=tr.cible, libere=libere, recu=recu, m=m))
    return replace(B, values=V), detail


# L23, vaccination antigrippale en officine : s_∞ et τ mesurés par P-B6 (registre 2026-11-15) ; a, k, μ supposés.
L23_PARAMS = (
    Param("a", 0.01, "part du temps de MG", "répartition des injections sourcée (Cour des comptes 2026, G10.csv : "
          "médicaux 70,7 % en 2018) ; part en temps de MG : dénominateur non lu, valeur supposée (fiche L23)", "2018",
          "supposé"),
    Param("k", 1.0, "t_PH / t_MG", "plage [0,25 ; 1] de la fiche L23 ; aucune durée officielle trouvée (ledger)", "—",
          "supposé"),
    Param("s_inf", 0.74, "part", "P-B6 (série nationale) : part officinale, IQVIA ÷ Open Medic, 2021-22 à 2024-25 (± 0,07)",
          "2025", "mesuré"),
    Param("tau", 2.4, "années", "P-B6 : même ajustement (± 0,5 an)", "2025", "mesuré"),
    Param("mu", 0.0, "actes ajoutés / acte transféré", "P-B6 : effet non attribuable (ATT +0,73 %, placebo en échec), tenu à 0", "2025", "supposé"),
)


L23_T0 = 2019     # généralisation de la vaccination en officine ; origine de l'ajustement de s(t) dans P-B6 (mesuré)


def l23(ref: int = 2026, **override) -> Transfert:
    """L23 sur la courbe mesurée (t₀ = 2019) ; seule la part au-delà de celle atteinte à l'année de base `ref` agit
    (décision P1-4 du 2026-11-15 : la demande de base contient déjà l'officine). ref ≤ 2019 : courbe entière."""
    v = {p.name: p.value for p in L23_PARAMS} | override
    deja = float(v["s_inf"] * (1 - np.exp(-(ref - L23_T0) / v["tau"]))) if ref > L23_T0 else 0.0
    return Transfert("L23 vaccination en officine", "medecine-generale", "pharmaciens", v["a"], v["k"], v["s_inf"],
                     v["tau"], L23_T0, v["mu"], s_deja=deja)
