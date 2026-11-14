"""Comparison bench: every estimator in sante.estimators.ESTIMATORS on the same windows and metric.

Run: uv run python -m sante.backtest   -> artifacts/s01_backtest/{results.csv, errors_by_dep.parquet}
Error = absolute % error on each département's total headcount (sexes and ages summed).
MAPE over départements with >= MIN_N professionals at origin; WAPE = sum|err| / sum(actual).
"""
from pathlib import Path

import pandas as pd

from sante.estimators import ESTIMATORS
from sante.model import stock_table

OUT = Path("artifacts/s01_backtest")
MIN_N = 30
# (profession, fit window, origin, targets). Origin 2021 rows exist because the student pipeline starts in 2020.
DESIGN = [
    ("specialistes", (2012, 2018), 2018, [2023, 2026]),
    ("dentistes", (2012, 2018), 2018, [2023, 2026]),
    ("pharmaciens", (2012, 2018), 2018, [2023, 2026]),
    ("sages-femmes", (2012, 2018), 2018, [2023, 2026]),
    ("infirmiers-liberaux", (2012, 2018), 2018, [2023]),
    ("infirmiers-salaries", (2013, 2018), 2018, [2023]),
    ("kines", (2017, 2021), 2021, [2026]),
    ("specialistes", (2015, 2021), 2021, [2026]),
    ("dentistes", (2015, 2021), 2021, [2026]),
    ("pharmaciens", (2015, 2021), 2021, [2026]),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, per_dep = [], []
    for prof, fit, origin, targets in DESIGN:
        t = stock_table([prof])
        totals = t.groupby(["profession", "dep", "year"]).n.sum().unstack("year")
        keep = totals[origin] >= MIN_N
        fitted = [E().fit(t, fit, origin) for E in ESTIMATORS]
        for target in targets:
            actual = totals[target]
            for est in fitted:
                pred = est.predict(target).reindex(actual.index)
                err = (pred - actual)[keep]
                ape = (err.abs() / actual[keep]) * 100
                rows.append({"profession": prof, "origin": origin, "target": target, "horizon": target - origin,
                             "model": est.name, "n_dep": int(keep.sum()), "MAPE_%": ape.mean(),
                             "median_APE_%": ape.median(), "WAPE_%": 100 * err.abs().sum() / actual[keep].sum(),
                             "national_err_%": 100 * (pred[keep].sum() / actual[keep].sum() - 1)})
                per_dep.append(pd.DataFrame({"target": target, "model": est.name,
                                             "actual": actual[keep], "pred": pred[keep]}).reset_index())
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "results.csv", index=False)
    pd.concat(per_dep).to_parquet(OUT / "errors_by_dep.parquet", index=False)
    print(res.pivot_table(index=["profession", "origin", "horizon"], columns="model", values="MAPE_%").round(2).to_string())


if __name__ == "__main__":
    main()
