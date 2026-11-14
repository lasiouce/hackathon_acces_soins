"""Synthèse : classement des facteurs, fourchettes à 2050 (deux composantes séparées), priorités pour l'axe 1.

Run (racine), après run.py et backtest.py : PYTHONPATH=v2:. uv run python -m sensibilite.resume
Écrit v2/sensibilite/out/{classement,fourchettes}.csv et affiche les tableaux du rapport (markdown).
"""
import pandas as pd

OUT = "v2/sensibilite/out/"
SEUIL = 0.05        # ST < 5 % de la variance : ne déplace pas la sortie (choix, voir rapport)


def md(df: pd.DataFrame, index: bool = True) -> str:
    """Tableau markdown sans dépendance (tabulate absent)."""
    df = df.reset_index() if index else df
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join("" if pd.isna(v) else str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def main():
    s = pd.read_csv(OUT + "sobol.csv")
    m = pd.read_csv(OUT + "morris.csv")
    d = pd.read_csv(OUT + "dist.csv")
    b = pd.read_csv(OUT + "backtest_fourchette.csv")
    c = s.merge(m[["profession", "famille", "annee", "facteur", "mu_star_pct", "mu_pct"]])
    c["rang"] = c.groupby(["profession", "famille", "annee"]).ST.rank(ascending=False, method="first").astype(int)
    c["ci_large"] = (c.ST_hi - c.ST_lo) > c.ST.clip(lower=1e-9)
    c.sort_values(["famille", "profession", "annee", "rang"]).to_csv(OUT + "classement.csv", index=False)

    pd.set_option("display.width", 250)
    for fam in ("tout", "incertitude"):
        print(f"\n### Famille « {fam} » : ST [IC 95 %] par profession et horizon (facteurs avec ST ≥ {SEUIL:.0%} au moins une fois)")
        x = c[c.famille == fam]
        keep = x.groupby(["profession", "facteur"]).ST.transform("max") >= SEUIL
        x = x[keep].assign(v=lambda z: z.apply(lambda r: f"{r.ST:.2f} [{r.ST_lo:.2f}–{r.ST_hi:.2f}]", axis=1))
        print(md(x.pivot_table(index=["profession", "facteur"], columns="annee", values="v", aggfunc="first")))
        print("\nS1 (premier ordre) :")
        print(md(x.pivot_table(index=["profession", "facteur"], columns="annee", values="S1").round(2)))
        print("\nMorris μ* (% de Y réf., pas de 2/3 de la plage) :")
        y = c[c.famille == fam].pivot_table(index=["profession", "facteur"], columns="annee", values="mu_star_pct").round(2)
        print(md(y))

    # Fourchettes à 2050 : (a) propagation (famille incertitude, P5–P95) ; (b) backtest extrapolé (A3)
    a = d[d.famille == "incertitude"][["profession", "annee", "y_ref", "p05", "p50", "p95", "cv_pct"]]
    f = a.merge(b[["profession", "annee", "h", "h_max_observe", "demi_largeur_nat_pct", "biais_moyen_h5_pct"]])
    f["a_bas_pct"] = 100 * (f.p05 / f.y_ref - 1)
    f["a_haut_pct"] = 100 * (f.p95 / f.y_ref - 1)
    f["b_bas"] = f.y_ref * (1 - f.demi_largeur_nat_pct / 100)
    f["b_haut"] = f.y_ref * (1 + f.demi_largeur_nat_pct / 100)
    f.to_csv(OUT + "fourchettes.csv", index=False)
    print("\n### Fourchettes")
    print(md(f.round(1), index=False))


if __name__ == "__main__":
    main()
