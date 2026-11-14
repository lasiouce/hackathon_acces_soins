"""Vérifie le code de validation sur données SYNTHÉTIQUES seulement (aucun effectif réel n'est lu).

Run : PYTHONPATH=v2 uv run --with scipy python -m validation.selftest
"""
import numpy as np
import pandas as pd

from validation import fine_scale, forecast, limits


class Persist:
    def fit(self, t, fit_years, origin):
        self.tot = t.groupby(["profession", "dep", "year"]).n.sum().unstack("year")
        self.origin = origin
        return self

    def predict(self, target):
        return self.tot[self.origin]


class Oracle(Persist):
    """Connaît la vraie croissance de 2 %/an : doit gagner contre la persistance."""
    def predict(self, target):
        return self.tot[self.origin] * 1.02 ** (target - self.origin)


def synthetic(seed=0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    deps = [f"{i:02d}" for i in range(1, 61)]
    base = rng.uniform(50, 2000, len(deps))
    rows = [("p", d, "F", 30, y, b * 1.02 ** (y - 2012) * rng.normal(1, 0.01))
            for d, b in zip(deps, base) for y in range(2012, 2027)]
    return pd.DataFrame(rows, columns=["profession", "dep", "sex", "age_lo", "year", "n"])


def main() -> None:
    t = synthetic()
    grid = forecast.design(t)
    assert grid[0][2] == 2016 and all(o + 1 <= 2026 for _, _, o, _ in grid)
    e = forecast.bench({"naive_persistance": Persist, "naive_tendance": Persist, "oracle": Oracle}, t, grid)
    v = forecast.verdict(e, "oracle")
    assert v["issue"] == "gagne", v
    v2 = forecast.verdict(e, "naive_tendance")
    assert v2["issue"] == "égalité", v2

    # L1 : la persistance colle à l'état observé
    est = Persist().fit(t, (2012, 2020), 2020)
    obs = t[t.year == 2020].groupby(["profession", "dep"]).n.sum()
    assert limits.l1_persistence(est, obs, 2020)["passe"]

    # L2 : modèle jouet à 40 âges, survie 0,97, sortie à 40 ; Q = 100
    s = np.full(40, 0.97)

    def no_entry(n):
        m = np.zeros_like(n)
        m[1:] = n[:-1] * s[:-1]
        return m

    def step(n):
        m = no_entry(n)
        m[0] += 100.0
        return m
    r = limits.l2_equilibrium(step, no_entry, 100.0, np.full(40, 30.0))
    assert r["passe"], r

    # L3 : choc de quota qui n'agit qu'après L = 5 ans
    yrs = pd.Index(range(2026, 2051))
    base = pd.Series(1000.0, yrs)
    shock = base.where(yrs < 2031, base * 1.2)
    assert limits.l3_quota_lock(base, shock, 2026, 5)["passe"]
    assert not limits.l3_quota_lock(base, shock, 2026, 6)["passe"]

    # N4 : erreur de Poisson pure -> N_min proche de 26 (dérivé : 1,28/√N ≤ 25 %)
    rng = np.random.default_rng(1)
    n0 = pd.Series(rng.integers(1, 400, 20000)).astype(float)
    actual = pd.Series(rng.poisson(n0)).astype(float)
    tab = fine_scale.size_errors(n0, actual, n0)
    nm = fine_scale.n_min(tab)
    assert 11 <= nm <= 51, (nm, tab)
    dep_of = pd.Series(["a", "a", "b"])
    so = fine_scale.share_out(pd.Series({"a": 20.0, "b": 5.0}), pd.Series([1.0, 3.0, 2.0]), dep_of)
    assert np.allclose(so.to_numpy(), [5, 15, 5])
    print("selftest OK :", {"N1": v["issue"], "L2": round(r["ecart_QC"], 4), "N4_N_min_poisson": nm})


if __name__ == "__main__":
    main()
