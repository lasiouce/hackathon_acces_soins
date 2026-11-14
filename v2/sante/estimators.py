"""Estimation algorithms behind one interface.

Every estimator:
  fit(t, fit_years, origin)  t = stock table (profession, dep, sex, age_lo, year, n), years <= origin only
  predict(target)            -> Series of headcount per (profession, dep) for the target year
  assumptions                plain-words description shown in the UI
Add an estimator = add a class and register it in ESTIMATORS. The bench (sante.backtest) runs them all.
"""
import numpy as np
import pandas as pd

from sante.model import baseline, fit_rates, project
from sante.pipeline import scale


class Estimator:
    name = ""
    assumptions = ""

    def fit(self, t: pd.DataFrame, fit_years: tuple[int, int], origin: int) -> "Estimator":
        self.t, self.fit_years, self.origin = t, fit_years, origin
        self.totals = t.groupby(["profession", "dep", "year"]).n.sum().unstack("year")
        return self

    def predict(self, target: int) -> pd.Series:
        raise NotImplementedError


class Persistence(Estimator):
    name = "H0 persistence"
    assumptions = "Nothing changes: each territory keeps its last observed headcount."

    def predict(self, target):
        return baseline(self.totals, self.origin, target, self.fit_years, "persistence")


class LinearTrend(Estimator):
    name = "H0 linear trend"
    assumptions = "Each territory's headcount keeps its past linear trend (fit window); no ages, no levers."

    def predict(self, target):
        return baseline(self.totals, self.origin, target, self.fit_years, "trend")


class StockFlow(Estimator):
    """Annual cohort-component model on 5-year bands (sante.model)."""
    shrink: float | None = None
    inflow_trend = False
    inflow_recent: int | None = None
    pipeline = False

    def fit(self, t, fit_years, origin):
        super().fit(t, fit_years, origin)
        self.rates = fit_rates(t[t.year <= origin], fit_years, shrink=self.shrink,
                               inflow_trend=self.inflow_trend, inflow_recent=self.inflow_recent)
        self._cache = {}
        return self

    def predict(self, target):
        if target not in self._cache:
            p = project(self.t, self.origin, target - self.origin, self.rates,
                        inflow_scale=self._pipeline_scale if self.pipeline else None)
            self._cache[target] = p[p.year == target].groupby(["profession", "dep"]).n.sum()
        return self._cache[target]


class StockFlowNational(StockFlow):
    name = "H1 stock-flow, national rates"
    assumptions = ("Ageing by 5-year band; one net retention rate per profession × sex × age, "
                   "pooled nationally (capped at 1); entries = constant yearly flow, the fit-window average.")


class StockFlowLocal(StockFlow):
    name = "H1 stock-flow, local rates"
    shrink = 200
    assumptions = ("As national rates, but each département gets its own rates, "
                   "shrunk toward the national ones (prior weight 200 persons). Entries = constant yearly flow.")


class StockFlowLocalTrendEntries(StockFlowLocal):
    name = "H1 stock-flow, local rates, trending entries"
    inflow_trend = True
    assumptions = ("As local rates, but each département's yearly entries keep their past linear trend "
                   "(e.g. rising quotas) instead of staying flat.")


class StockFlowLocalPipeline(StockFlowLocal):
    name = "H1 stock-flow, local rates, pipeline entries"
    inflow_recent = 2
    pipeline = True
    assumptions = ("As local rates, but yearly entries start from the last 2 years' level and follow the size of "
                   "the student cohorts already in training (DREES enrolments: specialists DES year 4, dentists and "
                   "pharmacists DE years 2-6). Beyond the last known cohort the ratio is held. No pipeline data for "
                   "midwives, kinés, nurses: entries stay flat at the recent level.")

    def _pipeline_scale(self, cells, h):
        return np.array([scale(p, self.origin, h)[-1] for p in cells["profession"]])


class StockFlowLocalRecent(StockFlowLocal):
    name = "H1 stock-flow, local rates, recent entries"
    inflow_recent = 2
    assumptions = ("As local rates, but yearly entries are held at the last 2 years' level of the fit window "
                   "instead of its whole-window average.")


class NationalTimesTrendShares(StockFlowNational):
    name = "H1 national total x trend shares"
    assumptions = ("National total from the stock-flow model; each département's share of it "
                   "extrapolated by its past linear trend.")

    def predict(self, target):
        nat = super().predict(target).sum()
        shares = self.totals.div(self.totals.sum())
        sh = baseline(shares, self.origin, target, self.fit_years, "trend")
        return sh / sh.sum() * nat


# StockFlowLocalTrendEntries is benched but not registered: 17.8 % MAPE (noise in per-dép entry trends), see K1 report.
ESTIMATORS = [StockFlowNational, StockFlowLocal, StockFlowLocalRecent, StockFlowLocalPipeline, NationalTimesTrendShares, Persistence, LinearTrend]
