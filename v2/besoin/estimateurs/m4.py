"""M4 : 2SFCA aux paramètres publiés par la DREES (famille de l'APL), composable avec un besoin d'entrée.

Dérivation du 2026-11-15, §6 M4 ; protocole gelé P-B4 (v2/validation/preregistered/2026-11-15-besoin-p-b4-apl.md).

  étape 1 (offre j)    R_j = S_j / Σ_k w(t_kj) · P_k^std
  étape 2 (commune i)  A_i = Σ_j w(t_ij) · R_j
  conservation         Σ_i P_i^std · A_i = Σ_j S_j   (dès que chaque j a Σ_k w P_k > 0 ; vérifiée par deux_etapes)

`w` : paliers de l'onglet « Paramètres » des fichiers APL 2024 (sourcé). `P^std` vient d'un besoin d'entrée : par
défaut les poids d'âge ω de l'APL **figés à une année de base** (décision du 2026-11-15 : la DREES les renormalise à
chaque millésime et ne voit pas le vieillissement ; figés, M4 se projette). Tout autre NeedEstimator peut servir
d'entrée (M4∘M1, M4∘M2…) : son B[p, commune, t] remplace P^std.

M4 ne change pas le besoin, il dit quelle part de l'offre chaque commune atteint : predict() rend le B d'entrée tel
quel (le module de couverture le lit comme les autres) et accessibilite() rend A, en ETP pour 100 000 unités de
besoin (habitants standardisés pour l'entrée par défaut ; femmes standardisées pour les SF).
Temps d'accès : vol d'oiseau × détour / vitesse (repli du protocole, supposé) tant qu'OSRM n'est pas installé.
"""
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy import sparse

from jumeau.module import Param

from besoin.couverture import SANS_COUVERTURE
from besoin.cube import Cube, Population
from besoin.interface import NeedEstimator, register

PARAMETRES = "v2/data/processed/besoin/apl_parametres.parquet"    # DREES 530, onglet « Paramètres » (LO 2.0)
DISTANCIER = "v2/data/processed/besoin/distancier_vol_oiseau.parquet"
OSRM = "v2/data/odbl/besoin/distancier_osrm.parquet"     # OSRM sur OSM (ODbL, non commité), colonne t_min
CODE = {"sages-femmes": "SF", "dentistes": "CD", "kines": "MK", "infirmiers": "IDE"}   # pas d'APL pharmaciens
PALIERS = {   # bornes hautes (min) et poids, onglet « Paramètres » APL 2024 (relus dans apl_parametres par paliers())
    "SF": ((10, 20, 30), (1.0, 2 / 3, 1 / 3)),
    "CD": ((10, 15, 20), (1.0, 2 / 3, 1 / 3)),
    "MK": ((10, 15, 20), (1.0, 2 / 3, 1 / 3)),
    "IDE": ((10, 15, 20), (1.0, 2 / 3, 1 / 3)),
}
OMEGA_ANNEE = {"SF": 2024, "CD": 2024, "IDE": 2024, "MK": 2023}  # fiche ω_a (axe 1) : pas de colonne MK 2024 publiée
PAR = 1e5


def paliers(code: str) -> tuple[tuple, tuple]:
    """Paliers publiés, relus dans la table de l'axe 4 et comparés à la constante (garde-fou de lecture)."""
    p = pd.read_parquet(PARAMETRES)
    p = p[(p.prof == code) & (p.bloc == "palier")]
    poids = tuple(p.valeur.to_numpy()[:-1])
    if not np.allclose(poids, PALIERS[code][1]) or p.valeur.to_numpy()[-1] != 0:
        raise ValueError(f"paliers {code} lus {tuple(p.valeur)} ≠ constante {PALIERS[code]}")
    return PALIERS[code]


def poids_distance(t_min: np.ndarray, code: str) -> np.ndarray:
    """w(t) en paliers : 1 jusqu'à la 1ʳᵉ borne (exclue), puis 2/3, 1/3, 0 au-delà de la dernière."""
    bornes, w = PALIERS[code]
    return np.select([t_min < b for b in bornes], w, 0.0)


def temps_repli(d_km: np.ndarray, detour: float = 1.3, vitesse: float = 50.0) -> np.ndarray:
    """Repli de P-B4 : t = détour × d / v, en minutes (détour 1,3 et 50 km/h, supposés)."""
    return detour * np.asarray(d_km, float) / vitesse * 60.0


@lru_cache(maxsize=2)
def _paires(path: str = DISTANCIER) -> pd.DataFrame:
    cols = ["com_i", "com_j", "t_min"] if path == OSRM else ["com_i", "com_j", "d_km"]
    return pd.read_parquet(path, columns=cols)


def matrice(communes: np.ndarray, code: str, detour=1.3, vitesse=50.0, paires: pd.DataFrame | None = None,
            distancier: str = DISTANCIER):
    """W[i, j] = w(t_ij) sur les communes données (creuse), depuis un distancier : temps routier `t_min` s'il est
    donné (OSRM), sinon vol d'oiseau `d_km` × détour / vitesse. W[i, j] porte t_ij ; R_j somme sur la colonne j."""
    d = _paires(distancier) if paires is None else paires
    pos = pd.Series(np.arange(len(communes)), index=pd.Index(communes))
    i = pos.reindex(d.com_i.to_numpy()).to_numpy()
    j = pos.reindex(d.com_j.to_numpy()).to_numpy()
    ok = ~(np.isnan(i) | np.isnan(j))
    t = d.t_min.to_numpy()[ok] if "t_min" in d else temps_repli(d.d_km.to_numpy()[ok], detour, vitesse)
    w = poids_distance(t, code)
    nz = w > 0
    n = len(communes)
    W = sparse.csr_matrix((w[nz], (i[ok][nz].astype(int), j[ok][nz].astype(int))), shape=(n, n))
    sans = np.flatnonzero(W.diagonal() == 0)       # commune absente du distancier : t_ii = 0, sans voisin connu
    if sans.size:
        W = W + sparse.csr_matrix((np.ones(sans.size), (sans, sans)), shape=(n, n))
    return W


def deux_etapes(W, S: np.ndarray, P: np.ndarray, tol: float = 1e-9) -> tuple[np.ndarray, np.ndarray, dict]:
    """(A, R, bilan). W[i, j] = w(t_ij) ; S offre par commune ; P besoin (P^std) par commune.
    Une offre sans aucun besoin accessible (Σ_k w P_k = 0) est perdue : elle est comptée dans le bilan et le contrôle
    de conservation porte sur l'offre placée. Le contrôle lève une erreur au-delà de `tol` (défaut de code)."""
    S, P = np.asarray(S, float), np.asarray(P, float)
    denom = W.T @ P                                    # Σ_k w(t_kj) P_k
    placee = denom > 0
    R = np.divide(S, denom, out=np.zeros_like(S), where=placee)
    A = W @ R
    tot = S[placee].sum()
    ecart = abs((P * A).sum() - tot) / tot if tot > 0 else 0.0
    bilan = dict(offre=float(S.sum()), offre_perdue=float(S[~placee].sum()), conservation_ecart_rel=float(ecart))
    if ecart > tol:
        raise AssertionError(f"conservation Σ P·A = Σ S violée : écart relatif {ecart:.3e} > {tol:g}")
    return A, R, bilan


def omega(code: str, annee: int | None = None) -> pd.Series:
    """Poids d'âge ω_a de l'APL, indexés par la borne basse de la tranche quinquennale (onglet « Paramètres »)."""
    p = pd.read_parquet(PARAMETRES)
    p = p[(p.prof == code) & (p.bloc == "poids_age") & (p.annee == (annee or OMEGA_ANNEE[code]))]
    lo = p.cle.str.extract(r"(\d+)")[0].astype(int).where(~p.cle.str.startswith("Moins"), 0)
    return pd.Series(p.valeur.to_numpy(), index=lo.to_numpy()).sort_index()


@register
class M4(NeedEstimator):
    name = "M4"
    norme = ("accessibilité potentielle localisée (2SFCA, paliers DREES) : l'offre en ETP rapportée au besoin qu'elle "
             "dessert à moins de 20 min (30 min pour les SF) ; le besoin vient d'un estimateur d'entrée, par défaut "
             "la population standardisée par les poids d'âge de l'APL figés à une année de base")
    assumptions = ("Chaque professionnel sert les habitants proches, avec un poids qui baisse par paliers avec le "
                   "temps de trajet. Le temps est approché par la distance à vol d'oiseau × 1,3 à 50 km/h. Le "
                   "besoin par âge est celui de l'APL, gelé à une année de base pour voir le vieillissement.")
    params = (
        Param("paliers", PALIERS, "min ; poids", "onglet « Paramètres » des fichiers APL 2024", "DREES 530, 2024",
              "sourcé", "convention « concertée » de la DREES, pas une estimation"),
        Param("omega", OMEGA_ANNEE, "année des poids d'âge", "onglet « Paramètres » APL (DCIR N−2)",
              "DREES 530, 2023–2024", "sourcé", "figés à l'année de base pour la projection (décision 2026-11-15)"),
        Param("detour", 1.3, "sans unité", "repli de P-B4 (vol d'oiseau)", "—", "supposé", bounds=(1.0, 2.0)),
        Param("vitesse", 50.0, "km/h", "repli de P-B4 (vol d'oiseau)", "—", "supposé", bounds=(30.0, 90.0)),
    )
    professions = tuple(CODE)

    def __init__(self, besoin: NeedEstimator | None = None, detour: float = 1.3, vitesse: float = 50.0):
        self.besoin, self.detour, self.vitesse = besoin, detour, vitesse

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "M4":
        super().fit(pop, etat, ref)
        if self.besoin is not None:
            self.besoin.fit(pop, etat, ref)
        return self

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        """B d'entrée : estimateur fourni, sinon Σ_a ω_a(base) · pop_a (femmes seules pour les SF)."""
        if self.besoin is not None:
            return self.besoin.predict(pop, etat, years)
        years = pop.years if years is None else np.asarray(list(years))
        yi = pop.years_index(years)
        sexes = list(pop.sexes)
        vals = []
        for p in self.professions:
            w = omega(CODE[p]).reindex(pop.ages, method="ffill").to_numpy()  # 95+ prend le ω de « 90 ans et plus »
            P = pop.P[:, yi]
            if p == "sages-femmes":
                P = P[:, :, [sexes.index(s) for s in sexes if str(s).upper().startswith("F")]]
            vals.append((P.sum(axis=2) * w).sum(axis=-1))
        return Cube(np.array(self.professions), pop.territories, years, np.stack(vals), pop.level,
                    unit="habitants standardisés (poids d'âge APL)")

    def accessibilite(self, S: Cube, B: Cube) -> tuple[Cube, list[dict]]:
        """A[p, commune, t] en ETP pour 100 000 unités de besoin, depuis l'offre S et le besoin B (communes)."""
        if S.level != "com" or B.level != "com":
            raise ValueError("M4 se calcule à la commune (agréger A ensuite par Σ B·A / Σ B, jamais par moyenne)")
        bad = sorted(set(S.professions) & SANS_COUVERTURE)
        if bad:
            raise ValueError(f"M4 de {bad} : interdit (O2)")
        com = np.union1d(S.territories, B.territories)
        out, bilans = np.zeros((len(S.professions), len(com), len(S.years))), []
        for a, p in enumerate(S.professions):
            W = matrice(com, CODE[p], self.detour, self.vitesse)
            for b, y in enumerate(S.years):
                s = pd.Series(S.values[a, :, b], S.territories).reindex(com, fill_value=0).to_numpy()
                P = pd.Series(B.values[B.p(p), :, B.y(y)], B.territories).reindex(com, fill_value=0).to_numpy()
                A, _, bilan = deux_etapes(W, s, P)
                out[a, :, b] = PAR * A
                bilans.append(dict(profession=p, year=int(y), **bilan))
        return Cube(S.professions, com, S.years, out, "com", unit="ETP pour 100 000 unités de besoin"), bilans
