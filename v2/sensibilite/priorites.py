"""Synthèse de la partie 2 : part de variance « décision » contre « connaissance », et priorisation de la recherche.

Part de la variance de N privé (Sobol par groupe, out/leviers_sobol_*.csv) :
  décision      S_déc  (premier ordre du groupe des leviers)
  connaissance  S_conn
  interaction   1 − S_déc − S_conn
Priorisation : pour chaque source d'incertitude, ST à 2050 (part de variance qu'elle porte, interactions
comprises), le moyen de la réduire et son prix (estimés, voir le rapport), et le gain attendu :
  gain = ST × fraction réductible   (fraction : 1 pour un choix d'estimation tranché par le banc, 0,75 pour une
                                     plage divisée par deux, effet linéaire, dérivé ; 0,5 pour une donnée
                                     dont on ne peut que resserrer l'encadrement, supposé)
Run (racine) : PYTHONPATH=v2:. uv run python -m sensibilite.priorites -> out/parts_variance.csv, out/priorites.csv
"""
from pathlib import Path

import pandas as pd

OUT = Path("v2/sensibilite/out")

# source -> (moyen, axe, prix, fraction réductible)   prix : estimations de temps Claude, supposées
SOURCES = {
    "part_privee": ("lire le secteur des salariés ambigus (FINESS, SAE, Annuaire Santé par personne)", "axe 4",
                    "~1–2 h", 0.5),
    "fenetre": ("trancher la fenêtre d'ajustement au banc N1 (erreur hors échantillon)", "axe 2/3", "~30 min machine", 1.0),
    "entrees": ("trancher la variante d'entrées au banc N1, avec la fenêtre (interaction)", "axe 2/3", "~30 min machine", 1.0),
    "shrink": ("shrinkage hiérarchique déjà adopté par l'axe 2 (A2)", "axe 2", "fait", 1.0),
    "filiere": ("relier le vivier aux entrées (lien_formation) et le valider au banc", "axe 2", "~1 h", 1.0),
    "fraction": ("âges fins dans les tranches (A1b de l'axe 2, adopté)", "axe 2", "~45 min", 0.75),
    "part_cumul": ("cumul emploi-retraite par caisse, millésime récent", "axe 1", "~30 min", 0.75),
    "theta": ("θ hors IDE : DiD sur le zonage SF/MK/CD (axe 3, N3)", "axe 3", "~1 h", 0.75),
    "repartition": ("destination des entrants bloqués : flux d'installation communaux (axe 4)", "axe 4", "~1 h", 0.5),
    "part_exemptee": ("part des spécialistes parmi les entrants dentistes (RPPS par spécialité)", "axe 1", "~20 min", 0.75),
}


def main():
    s = pd.concat([pd.read_csv(f) for f in sorted(OUT.glob("leviers_sobol_*.csv"))])
    g = s[s.groupe == "G"].pivot_table(index=["profession", "annee"], columns="facteur", values=["S1", "ST"])
    parts = pd.DataFrame({"S_decision": g["S1"]["[decision]"], "S_connaissance": g["S1"]["[connaissance]"],
                          "ST_decision": g["ST"]["[decision]"], "ST_connaissance": g["ST"]["[connaissance]"]})
    parts["interaction"] = 1 - parts.S_decision - parts.S_connaissance
    parts["decision_pese_plus"] = parts.S_decision > parts.S_connaissance
    parts.round(3).to_csv(OUT / "parts_variance.csv")
    print(parts.round(2).to_string())
    k = s[(s.groupe == "C") & (s.annee == 2050)]
    rows = []
    for _, r in k.iterrows():
        moyen, axe, prix, frac = SOURCES.get(r.facteur, ("?", "?", "?", 0.5))
        rows.append(dict(profession=r.profession, source=r.facteur, ST_2050=r.ST, ST_lo=r.ST_lo, ST_hi=r.ST_hi,
                         moyen=moyen, axe=axe, prix=prix, fraction_reductible=frac, gain=r.ST * frac))
    p = pd.DataFrame(rows).sort_values(["profession", "gain"], ascending=[True, False])
    p.round(3).to_csv(OUT / "priorites.csv", index=False)
    print(p[p.ST_2050 >= 0.02].round(2).to_string(index=False))
    d = s[(s.groupe == "D") & (s.annee == 2050)].pivot_table(index="facteur", columns="profession", values="ST")
    print("\nLeviers, ST à 2050 :\n", d.round(2).to_string())


if __name__ == "__main__":
    main()
