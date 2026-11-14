"""Loader: CartoSanté (Atlasanté) liberal stock by commune x age band -> data/processed/stock_commune.parquet

Run (racine du dépôt): PYTHONPATH=v2 uv run python -m sante.cartosante
Source: OGC TJS https://cartosante.atlasante.fr/GC_tjs.php, datasets {infi,kine,dent}_popage, attribute eft
(liberal professionals active at 31/12, producer FNPS/SNDS). Raw XML is cached in data/raw/cartosante/ with
the extraction date; delete it to refresh.
GetData rows carry only the territory key and the value: year and age band are implicit by position
(years ascending x age bands in DescribeData order); territories with a partial series are dropped. Two checks guard that inference:
  1. per commune-year, the age bands sum to the 'Total' band;
  2. communes summed to département equal the département GetData (same order inference, separate pull).
Output columns: profession, source, year, com, dep, age_band, age_lo, age_hi, n.
"""
import datetime as dt
import re
import subprocess
from pathlib import Path

import pandas as pd

TJS = "https://cartosante.atlasante.fr/GC_tjs.php"
RAW = Path("data/raw/cartosante")
OUT = Path("data/processed/stock_commune.parquet")
# sf_popage is left out: its GetData rows do not follow the year x age grid (bands never sum to the total).
DATASETS = {"infi_popage": "infirmiers-liberaux", "kine_popage": "kines", "dent_popage": "dentistes"}
DROPPED: list[dict] = []


def fetch(request: str, framework: str, dataset: str, extra: str = "") -> str:
    path = RAW / f"{request}_{framework}_{dataset}.xml"
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        url = (f"{TJS}?SERVICE=TJS&VERSION=1.0&REQUEST={request}"
               f"&FrameworkURI=http%3A%2F%2Finsee.fr%2Fcog%2F{framework}&DatasetURI={dataset}{extra}")
        subprocess.run(["curl", "-sSf", "--compressed", "--max-time", "300", "-o", str(path), url], check=True)
        (RAW / "EXTRACTED").write_text(dt.date.today().isoformat())
    return path.read_text()


def band(title: str) -> tuple[int, int | None]:
    """'Moins de 30 ans' -> (0, 29), '30 à 39 ans' -> (30, 39), '60 ans et plus' -> (60, None)."""
    x = [int(v) for v in re.findall(r"\d+", title)]
    return (0, x[0] - 1) if title.startswith("Moins") else (x[0], x[1] if len(x) > 1 else None)


def axes(dataset: str) -> tuple[list[int], list[str], dict[str, str]]:
    """Year and age-band modalities, in the order GetData rows enumerate them, plus band code -> title."""
    t = fetch("DescribeData", "dep", dataset)
    cols = dict(re.findall(r'<Column name="(annee|age|age_\w+)"[^>]*purpose="(?:TemporalValue|NonSpatialIdentifier)">(.*?)</Column>', t, re.S))
    years = sorted(int(y) for y in re.findall(r"<Identifier>(\d{4})</Identifier>", cols["annee"]))
    age_col = next(k for k in cols if k.startswith("age"))  # "age", or "age_sf" for midwives
    titles = dict(re.findall(r"<Identifier>([^<]*)</Identifier><Title>([^<]*)</Title>", cols[age_col]))
    return years, list(titles), titles


def get_data(framework: str, dataset: str) -> pd.DataFrame:
    years, ages, titles = axes(dataset)
    rows = re.findall(r"<Row><K>([^<]*)</K><V>([^<]*)</V></Row>", fetch("GetData", framework, dataset, "&Attributes=eft"))
    d = pd.DataFrame(rows, columns=["code", "n"])
    d["i"] = d.groupby("code").cumcount()
    # Territories with a partial series (communes created/merged, some DROM) can't be placed by position: drop them.
    per = d.groupby("code").size()
    short = per[per != len(years) * len(ages)]
    DROPPED.append({"dataset": dataset, "framework": framework, "dropped": len(short),
                    "dropped_codes": ",".join(short.index[:8]), "kept": len(per) - len(short)})
    d = d[~d.code.isin(short.index)]
    d["year"] = [years[i // len(ages)] for i in d.i]
    d["age"] = [ages[i % len(ages)] for i in d.i]
    d["age_band"] = d.age.map(titles)
    d["n"] = pd.to_numeric(d.n, errors="coerce")
    return d.drop(columns="i")


def dep_of(com: pd.Series) -> pd.Series:
    return com.str[:3].where(com.str.startswith("97"), com.str[:2])


def main() -> None:
    parts, checks = [], []
    for ds, prof in DATASETS.items():
        c = get_data("com2026", ds)
        wide = c.pivot_table(index=["code", "year"], columns="age", values="n", aggfunc="sum")
        bands = wide.drop(columns="0").sum(axis=1, min_count=1)
        gap1 = (bands - wide["0"]).abs().max()
        c["dep"] = dep_of(c.code)
        tot = c[c.age == "0"].groupby(["dep", "year"]).n.sum()
        d = get_data("dep", ds)
        dtot = d[d.age == "0"].set_index(["code", "year"]).n.rename_axis(["dep", "year"])
        j = pd.concat([tot.rename("com_sum"), dtot.rename("dep")], axis=1).dropna()
        gap2 = (j.com_sum - j.dep).abs().max()
        checks.append({"dataset": ds, "communes": c.code.nunique(), "years": f"{c.year.min()}-{c.year.max()}",
                       "max|bands-total|": gap1, "max|Σcom-dep|": gap2,
                       "France_last": int(d[(d.age == '0') & (d.year == d.year.max()) & (d.code.str.len() <= 3)].n.sum())})
        c = c[c.age != "0"]
        parts.append(pd.DataFrame({
            "profession": prof, "source": "CARTOSANTE", "year": c.year.values, "com": c.code.values,
            "dep": c.dep.values, "age_band": c.age_band.values,
            "age_lo": [band(b)[0] for b in c.age_band], "age_hi": pd.array([band(b)[1] for b in c.age_band], dtype="Int64"),
            "n": c.n.values}))
    out = pd.concat(parts, ignore_index=True)
    out = out[out.n.fillna(0) > 0]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)
    print(f"rows={len(out):,} extracted={(RAW / 'EXTRACTED').read_text()}")
    print(pd.DataFrame(checks).to_string(index=False))
    print(pd.DataFrame(DROPPED).to_string(index=False))


if __name__ == "__main__":
    main()
