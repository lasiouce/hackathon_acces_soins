"""C1 (cohortes bayésiennes, étape 2) servi par le jumeau : surcharges des taux de base de la composition des leviers.

C1 n'ajoute aucun module. Sa moyenne a posteriori remplace la rétention et les entrées ajustées de A0 pour les
cellules du secteur privé, au point où le jumeau calcule ses taux de base (`jumeau.history.stock_flow_rates`, mis en
cache sur l'historique) : `install` remplace ce cache par un cache qui applique C1 à chaque calcul. Les tableaux de
`params` (`sorties.retention`, `entrees.flux`) ne conviennent pas : la régulation ajoute des cellules (secteur des
entrants bloqués) à l'état, et un tableau figé n'a plus la bonne taille. Les cellules ajoutées le sont à la fin
(`State.ensure_sector`), donc les indices des cellules privées d'origine restent valides :
  - tous les leviers (quotas, diplômés étrangers, retraite, cumul, départs précoces, régulation) gardent leur
    mécanisme et s'appliquent aux taux de C1 ; même état de départ, même registre de flux ;
  - le secteur public garde les taux de A0 (C1 n'est ajusté que sur le privé) ;
  - la rétention de C1 varie un peu avec l'horizon (effet de cohorte) ; elle est tenue à sa moyenne sur
    l'horizon de projection (approximation ; écart au total privé national mesuré par ecart_constante).
Fenêtre d'ajustement : celle du banc N1 de C1 (2012 → origine ; kinés 2017 → origine).
Taux précalculés : v2/methodes/out/c1_taux/<profession>.npz, repérés par l'empreinte SHA-256 de la table privée.
Au service, ils évitent scipy (absent de l'environnement du chatbot) et l'ajustement (10 à 20 s par profession) ;
une table qui change déclenche un nouvel ajustement (scipy requis), puis réécrit le fichier.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from jumeau.state import AXES

PENTE = Path("v2/methodes/out/c1_pente.json")
TAUX = Path("v2/methodes/out/c1_taux")


def fit_window(prof, t, o):
    return (max(2017, int(t.year.min())) if prof == "kines" else int(t.year.min()), o)


def ecart_constante(est, prof: str, year: int) -> float:
    """Écart relatif du total privé national à `year` : C1 servi (rétention tenue constante) / C1 à rétention
    variable (methodes.cohortes, même table privée, même fenêtre) − 1."""
    from jumeau.scenario import Scenario
    from methodes.cohortes import CohortesEstimator
    t = est.hist.table
    tp = t[t.sector == "prive"].drop(columns="sector").groupby(["profession", "dep", "sex", "age_lo", "year"],
                                                               as_index=False).n.sum()
    o = est.state.year
    ref = CohortesEstimator().fit(tp, fit_window(prof, tp, o), o).predict(year).sum()
    st = est.trajectory(year, Scenario(modules=est.scenario.composition)).states[year]
    served = st.N[(st.cells.sector == "prive").to_numpy()].sum()
    return float(served / ref - 1)


class C1Cache(dict):
    """Cache de jumeau.history.stock_flow_rates qui applique les taux de C1 aux cellules privées d'origine."""

    def __init__(self, idx, s_c, i_c):
        super().__init__()
        self.idx, self.s_c, self.i_c = idx, s_c, i_c

    def __setitem__(self, key, value):
        if isinstance(key, tuple) and key and key[0] == "rates":
            S, I, P = (np.array(v, copy=True) for v in value)
            S[self.idx], I[self.idx], P[self.idx] = np.clip(self.s_c, 0.0, 1.0), self.i_c, 0.0
            value = (S, I, P)
        super().__setitem__(key, value)


def taux(tp, prof: str, o: int, until: int):
    """(cellules, s, I) de C1 pour la table privée tp : lus dans TAUX si l'empreinte correspond, sinon ajustés."""
    cle = hashlib.sha256(pd.util.hash_pandas_object(tp.sort_values(list(tp.columns)), index=False).values.tobytes()
                         + f"{o}|{until}".encode()).hexdigest()[:16]
    f = TAUX / f"{prof}.npz"
    if f.exists():
        z = np.load(f, allow_pickle=False)
        if str(z["cle"]) == cle:
            cells = pd.DataFrame({c: z[c].astype(str) for c in ("profession", "dep", "sex")})
            return cells, z["s"], z["i"]
    from methodes.cohortes import Cohortes                          # scipy requis seulement ici
    m = Cohortes(tp, fit_window(prof, tp, o), S=2)
    s_c = np.mean([m.rates(h)[0] for h in range(1, max(until - o, 1) + 1)], axis=0)
    i_c = m.rates(1)[1]
    TAUX.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, cle=cle, s=s_c, i=i_c, **{c: np.asarray(m.cells[c].astype(str).tolist(), dtype="U") for c in ("profession", "dep", "sex")})
    return m.cells[["profession", "dep", "sex"]].astype(str), s_c, i_c


def install(est, prof: str, until: int) -> None:
    """Branche C1 sur un TwinEstimator ajusté (avant toute trajectoire) : taux privés de C1, public de A0."""
    t = est.hist.table
    tp = t[t.sector == "prive"].drop(columns="sector").groupby(["profession", "dep", "sex", "age_lo", "year"],
                                                               as_index=False).n.sum()
    cells, s_c, i_c = taux(tp, prof, est.state.year, until)
    idx = est.state.index(cells.rename(columns={"dep": "territory"}).assign(sector="prive")[AXES])
    ok = idx >= 0
    est.hist._cache = C1Cache(idx[ok], s_c[ok], i_c[ok])
    est._mods, est._traj = {}, {}


def pente(prof: str) -> float:
    """Pente |erreur nationale| / horizon × 1,6 de C1, mesurée au banc N1 (méthode de Model.error_slope)."""
    d = json.loads(PENTE.read_text())
    return float(d[prof])


def calcule_pente():
    """Écrit v2/methodes/out/c1_pente.json à partir des erreurs du banc de l'étape 2 (coh_erreurs.parquet)."""
    e = pd.read_parquet("v2/methodes/out/coh_erreurs.parquet")
    e = e[e.model == "axe2_cohortes_c1"]
    nat = e.groupby(["profession", "origin", "h"]).apply(lambda g: abs(g.pred.sum() / g.actual.sum() - 1)).reset_index(name="e")
    out = {}
    for p, g in nat.groupby("profession"):
        h, err = g.h.to_numpy(float), g.e.to_numpy()
        out["infirmiers" if p == "infirmiers-liberaux" else p] = float(1.6 * (h * err).sum() / (h ** 2).sum())
    PENTE.write_text(json.dumps(out, indent=1))
    return out
