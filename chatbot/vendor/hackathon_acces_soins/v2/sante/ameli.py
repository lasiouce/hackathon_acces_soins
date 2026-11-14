"""Loader: ameli "Professionnels de santé libéraux : effectif et densité" -> data/processed/stock_ameli.parquet

Run (racine du dépôt): PYTHONPATH=v2 uv run python -m sante.ameli
Source: data.ameli.fr dataset demographie-effectifs-et-les-densites (modified 2026-10-28), export where effectif > 0.
Output keeps detailed cells only (no 'Tout âge' / 'tout sexe' / 'Ensemble des ...' aggregates), same columns
as stock.parquet where they apply: profession, specialty, source, year, dep, dep_name, region, mode, mode3,
age_band, age_lo, age_hi, sex, n, density_ameli. 'âge inconnu' / 'sexe inconnu' are kept as their own rows.
"""
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/ameli/demographie_effectifs_densites_nonzero.parquet")
OUT = Path("data/processed/stock_ameli.parquet")

# ameli profession label -> (our profession, specialty)
PROF = {
    "Infirmiers": ("infirmiers-liberaux", ""),
    "Masseurs-kinésithérapeutes": ("kines", ""),
    "Sages-femmes": ("sages-femmes", ""),
    "Chirurgiens-dentistes (hors spécialistes d'orthopédie dento-faciale - ODF)": ("dentistes", "omnipraticien"),
    "Chirurgiens-dentistes spécialistes d'orthopédie dento-faciale (ODF)": ("dentistes", "ODF"),
}
SKIP = ("Ensemble", "Médecins généralistes", "Orthophonistes", "Orthoptistes", "Pédicures-podologues")


def main() -> None:
    d = pd.read_parquet(RAW)
    d = d[(d.libelle_classe_age != "Tout âge") & (d.libelle_sexe != "tout sexe") & (d.departement != "999")]
    d = d[~d.profession_sante.str.startswith(SKIP)]
    prof = d.profession_sante.map(lambda p: PROF.get(p, ("specialistes", p)))
    ages = d.classe_age.str.extract(r"(\d+)\D*(\d*)")
    lo = pd.to_numeric(ages[0], errors="coerce")
    hi = pd.to_numeric(ages[1], errors="coerce")
    young = d.libelle_classe_age.str.startswith("moins")
    out = pd.DataFrame({
        "profession": [p for p, _ in prof], "specialty": [s for _, s in prof], "source": "AMELI",
        "year": pd.to_datetime(d.annee).dt.year,
        "dep": d.departement.values, "dep_name": d.libelle_departement.values, "region": d.region.values,
        "mode": "Libéral", "mode3": "liberal_mixte",
        "age_band": d.libelle_classe_age.values,
        "age_lo": lo.where(~young, 0).astype("Int64").values,
        "age_hi": hi.where(~young, lo - 1).astype("Int64").values,
        "sex": d.libelle_sexe.map({"hommes": "H", "femmes": "F", "sexe inconnu": "?"}).values,
        "n": d.effectif.astype(float).values, "density_ameli": d.densite.values,
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)
    print(f"rows={len(out):,} years={out.year.min()}-{out.year.max()} dép={out.dep.nunique()} "
          f"specialties={out[out.profession == 'specialistes'].specialty.nunique()}")
    print(out.groupby(["profession", "year"]).n.sum().unstack().iloc[:, [0, 8, -1]].round())


if __name__ == "__main__":
    main()
