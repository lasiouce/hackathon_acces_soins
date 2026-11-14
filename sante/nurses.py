"""Salaried nurses: département x age x sex stock from DREES/BTS marginal tables, by raking.

Run: uv run python -m sante.nurses
Output
  stock_nurses_salaried.parquet  same columns as stock.parquet, profession='infirmiers-salaries', source='BTS'
Source: DREES "Infirmières salariées" (BTS Insee, 2013-2023, published 2025-03-25, updated 2026-07-02).
The file gives age, sex, sector and specialty as separate marginals per département (one detailed
dimension per row, the others 'Ensemble'); only France entière crosses sex x age. The joint age x sex per
département is estimated by iterative proportional fitting (IPF) on the age and sex marginals, seeded with
the age x sex structure of liberal nurses (SNDS) in the same département and year. Sector is not crossed
with age or sex, so it is not allocated here: mode3 = 'salarie'.
"""
import unicodedata

import numpy as np
import pandas as pd

from sante.load import OUT, RAW, age_bounds, code_label, dep_code, is_total

BTS = RAW / "drees" / "infirmieres_salariees_bts_2013_2023.xlsx"
SNDS = RAW / "drees" / "infirmieres_liberales_snds_2012_2023.xlsx"
SEXES = ["H", "F"]
TOL = 1e-3  # max relative marginal error accepted (0.1 %)


def read(path) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_excel(path, sheet_name="Effectifs", engine="calamine")
    df.columns = [unicodedata.normalize("NFC", str(c)).strip() for c in df.columns]
    df = df[[c for c in df.columns if not c.startswith("Unnamed")]]
    df = df.rename(columns={"Région": "region", "Département": "departement", "Secteur d'activité": "secteur",
                            "Spécialité": "specialite", "Sexe": "sexe", "Tranche d'âge": "tranche_age"})
    years = [c for c in df.columns if c.startswith("effectif_")]
    return df, years


def margins() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """BTS -> (age marginal, sex marginal, total) per dep x year in long form, plus the national sex x age joint."""
    df, years = read(BTS)
    tot = df[["secteur", "specialite", "sexe", "tranche_age"]].apply(lambda c: c.map(is_total))
    # the marginals are not crossed: at most one detailed dimension per row, except France sex x age
    n_det = (~tot).sum(axis=1)
    france = df["departement"].str.startswith("00-France")
    assert (n_det <= 1).all() or (n_det[n_det > 1].index.isin(df.index[france])).all(), "unexpected crossed rows"

    deps = df[~df["departement"].astype(str).str.startswith("00")]
    t = tot.loc[deps.index]
    keys = deps["departement"].map(code_label)
    deps = deps.assign(dep=[dep_code(c) for c, _ in keys], dep_name=[n for _, n in keys],
                       region=deps["region"].map(lambda s: code_label(s)[0].zfill(2)))
    long = lambda d, ids: d.melt(id_vars=ids, value_vars=years, var_name="year", value_name="n").assign(
        year=lambda x: x["year"].str.slice(-4).astype(int), n=lambda x: x["n"].astype(float))
    other = t[["secteur", "specialite"]].all(axis=1)
    age = long(deps[other & t["sexe"] & ~t["tranche_age"]], ["dep", "dep_name", "region", "tranche_age"])
    sex = long(deps[other & ~t["sexe"] & t["tranche_age"]], ["dep", "sexe"])
    total = long(deps[t.all(axis=1)], ["dep"])
    age["age_band"] = age["tranche_age"].map(lambda s: code_label(s)[1])
    sex["sex"] = sex["sexe"].map(lambda s: {"1": "H", "2": "F"}[code_label(s)[0]])

    nat = df[france & ~tot["sexe"] & ~tot["tranche_age"]]
    nat = long(nat, ["sexe", "tranche_age"])
    nat["age_band"] = nat["tranche_age"].map(lambda s: code_label(s)[1])
    nat["sex"] = nat["sexe"].map(lambda s: {"1": "H", "2": "F"}[code_label(s)[0]])
    return age, sex[["dep", "year", "sex", "n"]], total, nat[["year", "age_band", "sex", "n"]]


def liberal_seed() -> pd.DataFrame:
    """SNDS liberal nurses: sex x age joint per dep x year (France = dep '00'). Absent rows are zero cells."""
    df, years = read(SNDS)
    t = df[["sexe", "tranche_age"]].apply(lambda c: c.map(is_total))
    # dep '00' rows are France (region '00') or a region total: keep France only
    df = df[~t.any(axis=1) & ~(df["departement"].str.startswith("00") & ~df["region"].str.startswith("00"))]
    out = df.melt(id_vars=["departement", "sexe", "tranche_age"], value_vars=years, var_name="year", value_name="n")
    return pd.DataFrame({
        "dep": out["departement"].map(lambda s: dep_code(code_label(s)[0])),
        "year": out["year"].str.slice(-4).astype(int),
        "age_lo": out["tranche_age"].map(lambda s: age_bounds(code_label(s)[1])[0]),
        "sex": out["sexe"].map(lambda s: {"1": "H", "2": "F"}[code_label(s)[0]]),
        "n": out["n"].fillna(0).astype(float),
    })


def rake(seed: np.ndarray, rows: np.ndarray, cols: np.ndarray, iters: int = 500) -> np.ndarray:
    """IPF of a 2-D seed to row and column marginals (rows rescaled to the column total if they disagree)."""
    x = seed.astype(float).copy()
    rows = rows * cols.sum() / rows.sum()
    for _ in range(iters):
        r = x.sum(1)
        x *= np.divide(rows, r, out=np.zeros_like(r), where=r > 0)[:, None]
        c = x.sum(0)
        x *= np.divide(cols, c, out=np.zeros_like(c), where=c > 0)[None, :]
        if np.abs(x.sum(1) - rows).max() <= 1e-9 * rows.sum():
            break
    return x


def max_rel_err(x: np.ndarray, rows: np.ndarray, cols: np.ndarray) -> float:
    e = np.concatenate([np.abs(x.sum(1) - rows) / np.maximum(rows, 1), np.abs(x.sum(0) - cols) / np.maximum(cols, 1)])
    return float(e.max())


def main() -> None:
    age, sex, total, nat = margins()
    bands = age.drop_duplicates("age_band")[["age_band"]].copy()
    bands["age_lo"] = bands["age_band"].map(lambda s: age_bounds(s)[0])
    bands = bands.sort_values("age_lo").reset_index(drop=True)
    los = bands["age_lo"].tolist()

    lib = liberal_seed().pivot_table(index=["dep", "year", "age_lo"], columns="sex", values="n", aggfunc="sum",
                                     fill_value=0)
    lib_dy = set(lib.index.droplevel("age_lo"))
    natj = nat.assign(age_lo=nat["age_band"].map(lambda s: age_bounds(s)[0])).pivot_table(
        index=["year", "age_lo"], columns="sex", values="n", aggfunc="sum")[SEXES]

    # national backtest: rake the national liberal joint to the national salaried marginals, compare to the truth
    print("national backtest, |cell error| as % of total (liberal seed vs independence):")
    for y in sorted(natj.index.get_level_values(0).unique()):
        truth = natj.loc[y].reindex(los).to_numpy()
        r, c = truth.sum(1), truth.sum(0)
        s = lib.loc[("00", y)].reindex(los, fill_value=0)[SEXES].to_numpy()
        fit, ind = rake(s, r, c), np.outer(r, c) / c.sum()
        print(f"  {y}: liberal seed {100 * np.abs(fit - truth).sum() / truth.sum() / 2:.2f} %  "
              f"independence {100 * np.abs(ind - truth).sum() / truth.sum() / 2:.2f} %")

    a = age.pivot_table(index=["dep", "year"], columns="age_band", values="n", aggfunc="sum")[bands["age_band"]]
    s = sex.pivot_table(index=["dep", "year"], columns="sex", values="n", aggfunc="sum")[SEXES]
    tt = total.set_index(["dep", "year"])["n"]
    meta = age.drop_duplicates("dep").set_index("dep")[["dep_name", "region"]]

    rows, stats = [], []
    for (dep, y) in a.index:
        # the published age and sex marginals disagree by up to ~0.2 % (source rounding): both are scaled to
        # the file's own total before raking, and the raw gaps are reported
        ra_raw, cs_raw, tot_dy = a.loc[(dep, y)].to_numpy(), s.loc[(dep, y)].to_numpy(), tt.loc[(dep, y)]
        ra, cs = ra_raw * tot_dy / ra_raw.sum(), cs_raw * tot_dy / cs_raw.sum()
        nat_seed = natj.loc[y].reindex(los).to_numpy()
        fallback = (dep, y) not in lib_dy
        seed = nat_seed if fallback else lib.loc[(dep, y)].reindex(los, fill_value=0)[SEXES].to_numpy()
        # cells empty in the liberal seed but needed by a salaried marginal: borrow the national salaried shape
        seed = seed / seed.sum() + 1e-3 * nat_seed / nat_seed.sum()
        x = rake(seed, ra, cs)
        ind = np.outer(ra, cs) / cs.sum()
        alt = rake(nat_seed, ra, cs)  # sensitivity: national salaried joint as the seed
        stats.append({"dep": dep, "year": y, "fallback": fallback, "err": max_rel_err(x, ra, cs),
                      "err_raw": max_rel_err(x, ra_raw, cs_raw), "tvd_vs_natseed": np.abs(x - alt).sum() / x.sum() / 2,
                      "age_vs_sex_gap": abs(ra_raw.sum() / cs_raw.sum() - 1), "total_gap": abs(cs_raw.sum() / tot_dy - 1),
                      "tvd_vs_indep": np.abs(x - ind).sum() / x.sum() / 2, "total": cs.sum()})
        for i, lo in enumerate(los):
            for j, sx in enumerate(SEXES):
                rows.append((y, dep, i, sx, x[i, j]))

    out = pd.DataFrame(rows, columns=["year", "dep", "i", "sex", "n"])
    out = out.join(bands, on="i").drop(columns="i").join(meta, on="dep")
    out["age_hi"] = pd.array([age_bounds(b)[1] for b in out["age_band"]], dtype="Int64")
    out = out.assign(profession="infirmiers-salaries", source="BTS", mode="Salarié", mode3="salarie", specialty="")
    out = out[["profession", "source", "year", "dep", "dep_name", "region", "mode", "age_band", "sex",
               "specialty", "n", "mode3", "age_lo", "age_hi"]]
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT / "stock_nurses_salaried.parquet", index=False)

    st = pd.DataFrame(stats)
    w = lambda col: (st[col] * st["total"]).sum() / st["total"].sum()
    print(f"rows={len(out):,}  dép={out.dep.nunique()}  years={out.year.min()}-{out.year.max()}  "
          f"seed fallbacks={int(st.fallback.sum())}")
    print(f"max marginal error after raking: {100 * st.err.max():.6f} % of each harmonised marginal cell "
          f"(tolerance {100 * TOL:.1f} %); vs raw published cells: {100 * st.err_raw.max():.4f} %")
    print(f"max |age total / sex total - 1|: {100 * st.age_vs_sex_gap.max():.4f} %  "
          f"max |sex total / file total - 1|: {100 * st.total_gap.max():.4f} %")
    print(f"distance to independence product (share of cells moved): mean {100 * w('tvd_vs_indep'):.2f} %  "
          f"max {100 * st.tvd_vs_indep.max():.2f} % ({st.loc[st.tvd_vs_indep.idxmax(), ['dep', 'year']].tolist()})")
    print(f"distance to the national-salaried-seed variant: mean {100 * w('tvd_vs_natseed'):.2f} %  "
          f"max {100 * st.tvd_vs_natseed.max():.2f} %")
    nat_dep = out.groupby("year")["n"].sum()
    for y in nat_dep.index:
        print(f"  {y}: France total {nat_dep[y]:,.0f}  national file total {natj.loc[y].to_numpy().sum():,.0f}")
    assert not st.isna().any().any() and np.isclose(nat_dep, natj.groupby(level=0).sum().sum(axis=1), rtol=1e-4).all()
    assert st.err.max() < TOL, "raked cells miss a marginal by more than 0.1 %"


if __name__ == "__main__":
    main()
