"""Vivier réel en formation : inscrits en 1re année et diplômés par an, DREES jeu 491 (enquête Écoles).

Source : DREES, « La formation aux professions de santé », Séries longues 1966-2025 (onglets Inscrits1ere_an
et Diplomes_an), téléchargée le 2026-11-14 depuis data.drees.solidarites-sante.gouv.fr (121 774 octets) dans
data/raw/drees/491_formation_series_longues_1966_2025.xlsx. Champ : France métropolitaine et DROM.
Professions couvertes ici : infirmiers (IFSI), kinés (IFMK), sages-femmes (écoles de maïeutique).

Durée en école L (années d'inscription entre la 1re année d'école et le diplôme) : IDE 3, MK 4, SF 4
(réglementation : IFMK en 4 ans depuis 2015 après une année universitaire ; maïeutique : 4 années en école
après la 1re année commune). Vérifiée par le rendement ρ(t) = diplômés(t) / inscrits 1re année(t − L) et par
l'erreur de reconstitution des diplômés (fit_report).
"""
from functools import lru_cache

import numpy as np
import pandas as pd

FICHIER = "data/raw/drees/491_formation_series_longues_1966_2025.xlsx"
LIGNES = {"infirmiers": "Infirmiers diplômés d'État", "kines": "Kinésithérapeutes", "sages-femmes": "Sages-femmes"}
DUREE_ECOLE = {"infirmiers": 3, "kines": 4, "sages-femmes": 4}


def _serie(sheet: str) -> pd.DataFrame:
    d = pd.read_excel(FICHIER, sheet_name=sheet, header=None, engine="calamine")
    years = pd.to_numeric(d.iloc[4].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
    lab = d.iloc[:, 1].map(lambda v: str(v).strip())
    rows = []
    for prof, label in LIGNES.items():
        i = d.index[lab == label]
        if len(i) == 0:
            raise ValueError(f"{sheet} : ligne {label!r} introuvable")
        vals = pd.to_numeric(d.iloc[i[0]], errors="coerce")
        rows += [(prof, int(y), float(v)) for y, v in zip(years, vals) if pd.notna(y) and pd.notna(v)]
    return pd.DataFrame(rows, columns=["profession", "year", "n"])


@lru_cache
def ecoles() -> pd.DataFrame:
    """profession × année : inscrits en 1re année et diplômés (DREES 491)."""
    a = _serie("Inscrits1ere_an").rename(columns={"n": "inscrits1"})
    b = _serie("Diplomes_an").rename(columns={"n": "diplomes"})
    return a.merge(b, on=["profession", "year"], how="outer").sort_values(["profession", "year"]).reset_index(drop=True)


def rendement(prof: str, L: int | None = None) -> pd.Series:
    """ρ(t) = diplômés(t) / inscrits en 1re année(t − L), par année de diplôme."""
    L = DUREE_ECOLE[prof] if L is None else L
    e = ecoles()[lambda x: x.profession == prof].set_index("year")
    entrants = pd.Series(e.inscrits1.reindex(e.index - L).to_numpy(), index=e.index)
    return (e.diplomes / entrants).dropna()


def fit_report(L_range=range(2, 7), years=(2015, 2025)) -> pd.DataFrame:
    """Pour chaque profession et L : coefficient de variation de ρ sur les années de diplôme (un L juste rend ρ
    stable). Mesure de la cohérence de L, pas un ajustement."""
    out = []
    for prof in LIGNES:
        for L in L_range:
            r = rendement(prof, L)
            r = r[(r.index >= years[0]) & (r.index <= years[1])]
            out.append(dict(profession=prof, L=L, rho_moyen=float(r.mean()), cv=float(r.std() / r.mean()), n=len(r)))
    return pd.DataFrame(out)


def abandon_annuel(prof: str, years=(2023, 2025)) -> float:
    """Abandon annuel équivalent 1 − ρ^(1/L), ρ moyen des dernières années de diplôme (dérivé de mesures)."""
    L = DUREE_ECOLE[prof]
    r = rendement(prof, L)
    rho = float(r[(r.index >= years[0]) & (r.index <= years[1])].mean())
    return 1 - min(rho, 1.0) ** (1 / L)


def pool_ecoles(origin: int, professions=None, abandon=None) -> pd.Series:
    """Vivier à l'origine, (profession, année d'école k) → inscrits : la cohorte entrée en origin − k + 1, réduite
    de l'abandon annuel (abandon_annuel) pour chaque année déjà passée. Professions = clés de l'état qui
    commencent par une profession couverte (« infirmiers-liberaux » reçoit le vivier IDE)."""
    e = ecoles().set_index(["profession", "year"]).inscrits1
    rows = {}
    for state_prof in (professions or list(LIGNES)):
        base = next((p for p in LIGNES if state_prof == p or state_prof.startswith(p + "-")), None)
        if base is None:
            continue
        L = DUREE_ECOLE[base]
        a = abandon_annuel(base) if abandon is None else float(abandon[state_prof])
        for k in range(1, L + 1):
            y = origin - k + 1
            if (base, y) not in e.index or np.isnan(e[(base, y)]):
                raise ValueError(f"vivier {base} : inscrits en 1re année {y} absents de la série 491")
            rows[(state_prof, k)] = float(e[(base, y)]) * (1 - a) ** (k - 1)
    if not rows:
        return pd.Series([], index=pd.MultiIndex.from_tuples([], names=["profession", "k"]), dtype=float)
    return pd.Series(rows, dtype=float).rename_axis(["profession", "k"])


def diplomes_observes(prof: str, years) -> float:
    """Moyenne des diplômés observés sur des années (dénominateur du mode « vivier » de lien_formation)."""
    base = next(p for p in LIGNES if prof == p or prof.startswith(p + "-"))
    e = ecoles()[lambda x: x.profession == base].set_index("year").diplomes
    return float(e.reindex(list(years)).mean())
