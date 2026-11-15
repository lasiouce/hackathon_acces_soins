"""C1-GBM : apprentissage automatique global (toutes professions × départements × âges à la fois), concurrent de A2.

Inscription avant banc : v2/docs/lab/derivations/2026-11-15-c1-gbm-global.md (SHA-256 8e35043aecb2).
Modèle à un pas, itéré jusqu'à la cible (un modèle direct à h = 5 n'a pas de données sans fuite aux origines 2016-2017).
  unité    cellule profession × dép × sexe × tranche d'âge
  base     b = 0,8 n(a) + 0,2 n(a−1) (tranche ouverte 65+ : n + 0,2 n(a−1)), sans apprentissage
  cible    y = (n(a, t+1) − b(t)) / N(dép, t) : contribution de la cellule à la croissance relative du département
  GBM      HistGradientBoostingRegressor, réglages fixés a priori (aucun réglage sur le banc)
  MLP      MLPRegressor (32, 16), arrêt précoce sur 10 % des lignes d'entraînement
Interface Estimator : fit(t, fit_years, origin) / predict(target). Le banc ne passe qu'une profession ; le modèle global lit
le panel complet (GlobalEstimator.panel, posé par le lanceur) **coupé à l'origine**, et le cache par origine.
"""
import numpy as np
import pandas as pd

from methodes.calibrage import dep_to_region
from sante.estimators import Estimator

BANDS = (0, 25, 30, 35, 40, 45, 50, 55, 60, 65)
PROFS = ("dentistes", "infirmiers-liberaux", "kines", "pharmaciens", "sages-femmes")
FEATURES = ["prof", "sex", "band", "region", "logN", "share", "share_prev", "base_share", "y_lag1", "y_lag2",
            "ratio_lag1", "g1", "g2", "g3", "gnat1", "s60", "s35", "logpop", "pop60", "density"]
CATS = ["prof", "sex", "region"]
GBM_PARAMS = dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=50, l2_regularization=1.0,
                  early_stopping=False, random_state=0)
MLP_PARAMS = dict(hidden_layer_sizes=(32, 16), alpha=1e-3, early_stopping=True, validation_fraction=0.1,
                  max_iter=500, random_state=0)


def population() -> pd.DataFrame:
    """INSEE (data/processed/population.parquet, scénario central, 2018+) : dep × année -> pop, part 60+."""
    p = pd.read_parquet("data/processed/population.parquet")
    p = p[p.scenario == "central"]
    g = p.groupby(["dep", "year"])
    return pd.DataFrame({"pop": g["pop"].sum(), "pop60": p[p.age_lo >= 60].groupby(["dep", "year"])["pop"].sum()
                         / g["pop"].sum()}).reset_index()


class Panel:
    """Matrice dense cellules × années (NaN = non observé) ; les colonnes > origine sont effacées à la construction."""

    def __init__(self, t: pd.DataFrame, pop: pd.DataFrame, origin: int, last: int):
        assert (t.year <= origin).all() and (pop.year <= origin).all(), "fuite : données postérieures à l'origine"
        self.origin = origin
        self.years = np.arange(int(t.year.min()), last + 1)
        w = (t.groupby(["profession", "dep", "sex", "age_lo", "year"]).n.sum().unstack("year")
             .reindex(columns=self.years))
        idx = pd.MultiIndex.from_product([PROFS, sorted(t.dep.unique()), ["F", "H"], BANDS],
                                         names=["profession", "dep", "sex", "age_lo"])
        w = w.reindex(idx)
        # une année observée pour une profession = cellules absentes à 0 ; non observée = NaN
        seen = t.groupby(["profession", "year"]).size().unstack().reindex(index=list(PROFS), columns=self.years).notna()
        m = w.to_numpy(float)
        rows = w.index.to_frame(index=False)
        obs = seen.loc[rows.profession].to_numpy()
        m[obs & np.isnan(m)] = 0.0
        m[~obs] = np.nan
        self.n = m
        self.rows = rows
        self.prof = rows.profession.map({p: i for i, p in enumerate(PROFS)}).to_numpy()
        self.sex = (rows.sex == "H").to_numpy(int)
        self.band = rows.age_lo.map({b: i for i, b in enumerate(BANDS)}).to_numpy()
        reg = dep_to_region()
        self.region = rows.dep.map(reg).map({r: i for i, r in enumerate(sorted(reg.unique()))}).fillna(-1).to_numpy()
        self.grp, self.grp_keys = pd.factorize(pd.MultiIndex.from_frame(rows[["profession", "dep"]]))
        # voisin d'âge (tranche précédente, même sexe) : lignes consécutives par construction de idx
        self.prev = np.where(self.band > 0, np.arange(len(rows)) - 1, -1)
        # population figée à l'origine au-delà de celle-ci
        pw = pop.set_index(["dep", "year"])
        cols = [min(y, origin) for y in self.years]
        deps = rows.dep.to_numpy()
        self.pop = np.stack([pw["pop"].reindex(pd.MultiIndex.from_arrays([deps, np.full(len(deps), y)])).to_numpy()
                             for y in cols], 1)
        self.pop60 = np.stack([pw["pop60"].reindex(pd.MultiIndex.from_arrays([deps, np.full(len(deps), y)]))
                               .to_numpy() for y in cols], 1)

    def col(self, year: int) -> int:
        return int(year - self.years[0])

    def _N(self, j):
        if j < 0:
            return np.full(len(self.rows), np.nan)
        s = np.bincount(self.grp, weights=np.nan_to_num(self.n[:, j]), minlength=len(self.grp_keys))
        s[np.bincount(self.grp, weights=np.isnan(self.n[:, j]), minlength=len(self.grp_keys)) > 0] = np.nan
        return s[self.grp]

    def _base(self, j):
        if j < 0:
            return np.full(len(self.rows), np.nan)
        v = self.n[:, j]
        prev = np.where(self.prev >= 0, v[np.maximum(self.prev, 0)], 0.0)
        own = np.where(self.band == len(BANDS) - 1, 1.0, 0.8)
        return own * v + 0.2 * prev

    def _nat(self, j):
        if j < 0:
            return np.full(len(self.rows), np.nan)
        s = np.bincount(self.prof, weights=np.nan_to_num(self.n[:, j]), minlength=len(PROFS))
        s[np.bincount(self.prof, weights=np.isnan(self.n[:, j]), minlength=len(PROFS)) > 0] = np.nan
        return s[self.prof]

    def _y(self, j):
        """Cible à l'année de colonne j (de j à j+1)."""
        if j < 0:
            return np.full(len(self.rows), np.nan)
        return (self.n[:, j + 1] - self._base(j)) / self._N(j)

    def features(self, j: int) -> pd.DataFrame:
        n, N = self.n[:, j], self._N(j)
        N1, N2, N3 = self._N(j - 1), self._N(j - 2), self._N(j - 3)
        old = np.bincount(self.grp, weights=np.nan_to_num(n) * (self.band >= BANDS.index(60)),
                          minlength=len(self.grp_keys))[self.grp]
        young = np.bincount(self.grp, weights=np.nan_to_num(n) * (self.band <= BANDS.index(30)),
                            minlength=len(self.grp_keys))[self.grp]
        prevn = np.where(self.prev >= 0, n[np.maximum(self.prev, 0)], np.nan)
        with np.errstate(divide="ignore", invalid="ignore"):
            f = {"prof": self.prof, "sex": self.sex, "band": self.band, "region": self.region,
                 "logN": np.log1p(N), "share": n / N, "share_prev": prevn / N, "base_share": self._base(j) / N,
                 "y_lag1": self._y(j - 1), "y_lag2": self._y(j - 2),
                 "ratio_lag1": np.clip(n / (self._base(j - 1) + 1.0), 0, 5),
                 "g1": N / N1 - 1, "g2": np.sqrt(N / N2) - 1, "g3": np.cbrt(N / N3) - 1,
                 "gnat1": self._nat(j) / self._nat(j - 1) - 1, "s60": old / N, "s35": young / N,
                 "logpop": np.log(self.pop[:, j]), "pop60": self.pop60[:, j], "density": 1e5 * N / self.pop[:, j]}
        return pd.DataFrame(f)

    def training(self):
        """Lignes (t -> t+1) avec t+1 ≤ origine, cible et N observés ; poids 1 par département × année."""
        X, y, w, yr = [], [], [], []
        for j in range(0, self.col(self.origin)):
            target = self._y(j)
            ok = ~np.isnan(target) & (self._N(j) > 0)
            if not ok.any():
                continue
            cnt = np.bincount(self.grp[ok], minlength=len(self.grp_keys))[self.grp[ok]]
            X.append(self.features(j)[ok]), y.append(target[ok]), w.append(1.0 / cnt)
            yr.append(np.full(ok.sum(), self.years[j] + 1))
        yr = np.concatenate(yr)
        assert yr.max() <= self.origin, "fuite : cible postérieure à l'origine"
        return pd.concat(X, ignore_index=True), np.concatenate(y), np.concatenate(w), yr

    def roll(self, model, last: int):
        """Itère le modèle de l'origine à `last` ; renvoie {année: Series (profession, dep)}."""
        out = {}
        for year in range(self.origin, last):
            j = self.col(year)
            pred = model(self.features(j))
            nxt = np.maximum(self._base(j) + pred * self._N(j), 0.0)
            self.n[:, j + 1] = np.where(np.isnan(self.n[:, j]), np.nan, nxt)
            tot = np.bincount(self.grp, weights=np.nan_to_num(self.n[:, j + 1]), minlength=len(self.grp_keys))
            out[year + 1] = pd.Series(tot, index=self.grp_keys)
        return out


def _gbm(X, y, w, feats):
    from sklearn.ensemble import HistGradientBoostingRegressor
    m = HistGradientBoostingRegressor(categorical_features=[feats.index(c) for c in CATS], **GBM_PARAMS)
    m.fit(X[feats].to_numpy(), y, sample_weight=w)
    return lambda F: m.predict(F[feats].to_numpy())


def _mlp(X, y, w, feats):
    from sklearn.neural_network import MLPRegressor
    num = [c for c in feats if c not in CATS]
    mu, sd = X[num].mean(), X[num].std().replace(0, 1)
    levels = {c: sorted(X[c].unique()) for c in CATS}

    def design(F):
        Z = ((F[num] - mu) / sd)
        miss = Z.isna().astype(float).add_suffix("_na")
        cat = pd.concat([pd.get_dummies(pd.Categorical(F[c], categories=levels[c]), prefix=c, dtype=float)
                         for c in CATS], axis=1)
        return np.hstack([Z.fillna(0).to_numpy(), miss.to_numpy(), cat.to_numpy()])

    # MLPRegressor n'accepte pas de poids : on rééchantillonne au prorata (graine fixe), ce qui revient au même en espérance
    rng = np.random.default_rng(0)
    pick = rng.choice(len(y), size=len(y), p=w / w.sum())
    sy = y.std()
    m = MLPRegressor(**MLP_PARAMS).fit(design(X.iloc[pick]), y[pick] / sy)
    return lambda F: m.predict(design(F)) * sy


class GlobalEstimator(Estimator):
    panel: pd.DataFrame | None = None       # posé par le lanceur : table complète (toutes professions)
    pop: pd.DataFrame | None = None
    learner = staticmethod(_gbm)
    _cache: dict = {}

    def fit(self, t, fit_years, origin):
        assert t.year.max() <= origin, "fuite : le banc a passé des années postérieures à l'origine"
        super().fit(t, fit_years, origin)
        key = (type(self).__name__, origin, id(self.panel), id(self.pop))
        if key not in self._cache:
            p = self.panel[self.panel.year <= origin]
            pop = (self.pop if self.pop is not None else population())
            pop = pop[pop.year <= origin]
            last = int(self.panel.year.max())
            pan = Panel(p, pop, origin, last)
            X, y, w, _ = pan.training()
            # avant 2018 la population n'est pas observée : variable entièrement manquante -> retirée à cette origine
            feats = [c for c in FEATURES if X[c].notna().any()]
            self._cache[key] = pan.roll(self.learner(X, y, w, feats), last)
        self.paths = self._cache[key]
        return self

    def predict(self, target):
        return self.paths[target]


class GlobalGBM(GlobalEstimator):
    name = "C1 GBM global"
    assumptions = ("Gradient boosting appris sur toutes les professions, départements et tranches d'âge à la fois : "
                   "croissance d'une année à l'autre de chaque cellule, itérée jusqu'à la cible. Boîte noire, diagnostic.")


class GlobalMLP(GlobalEstimator):
    name = "C1 MLP global"
    learner = staticmethod(_mlp)
    assumptions = "Comme C1 GBM, avec un petit réseau de neurones (32, 16). Boîte noire, diagnostic."
