"""APL DREES (jeu 530), millésimes 2022–2024 : APL et population standardisée par commune, paramètres publiés.

Run (racine du dépôt) : uv run python v2/besoin/donnees/apl.py   (≈ 30 s ; télécharge 5 xlsx, ~25 Mo, dans
v2/data/raw/besoin/apl/ s'ils manquent)

Source : DREES, « L'accessibilité potentielle localisée (APL) », data.drees.solidarites-sante.gouv.fr, jeu 530,
modifié le 2026-07-22, Licence Ouverte 2.0. Un fichier par profession (SF, CD, MK, IDE ; pas de pharmaciens) avec
un onglet par millésime et un onglet « Paramètres » (champ, bornes d'activité, paliers de distance, poids d'âge DCIR).
Champ géographique : France hors Mayotte, DOM inclus (codes 971–974).

Sorties (Licence Ouverte 2.0, commitées) : v2/data/processed/besoin/
  - apl_commune.parquet : com, prof, annee, apl (ETP pour 100 000 hab. standardisés), pop_std, pop_tot, pop_fem (SF) ;
  - apl_parametres.parquet : prof, bloc (palier | poids_age | texte), cle, annee, valeur, texte.
Contrôle : moyenne nationale Σ apl·pop_std / Σ pop_std contre l'« APL moyen France entière hors Mayotte » publié
dans « Indicateurs d'APL moyens par dixièmes de population » (même jeu), à 0,5 % près.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import CACHE, controle, ecrire  # noqa: E402

API = "https://data.drees.solidarites-sante.gouv.fr/api/datasets/1.0/530_l-accessibilite-potentielle-localisee-apl/attachments/{}/"
FICHIERS = {"SF": "indicateur_d_apl_aux_sages_femmes_xlsx", "CD": "indicateur_d_apl_aux_chirurgiens_dentistes_xlsx",
            "MK": "indicateur_d_apl_aux_kinesitherapeutes_xlsx", "IDE": "indicateur_d_apl_aux_infirmiers_xlsx"}
DIXIEMES = "indicateurs_d_apl_moyens_par_dixiemes_de_population_xlsx"
ONGLET_DIX = {"SF": "Sages-femmes", "CD": "Chirurgiens-dentistes", "MK": "Kinésithérapeutes", "IDE": "Infirmières"}
CMD = "uv run python v2/besoin/donnees/apl.py"


def fichier(ident: str) -> Path:
    p = CACHE / "apl" / f"{ident}.xlsx"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(urllib.request.urlopen(API.format(ident), timeout=120).read())
    return p


def lire_onglet(path: Path, onglet: str) -> tuple[pd.DataFrame, str]:
    v = pd.read_excel(path, sheet_name=onglet, engine="calamine", header=None, dtype=object)
    entete = int(v.index[v[0].astype(str).str.startswith("Code commune")][0])
    noms = ["com", "nom", "apl", "pop_std", "pop_tot"] + (["pop_fem"] if v.shape[1] > 5 else [])
    d = v.iloc[entete + 2:, :len(noms)].set_axis(noms, axis=1).dropna(subset=["com"])
    d["com"] = d["com"].astype(str).str.zfill(5)
    for c in noms[2:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    millesime = str(v.iloc[2, 0])  # « Millésime : AAAA », gardé tel quel (l'onglet 2023 annonce 2024, observé)
    return d.drop(columns="nom"), millesime


def parametres(path: Path, prof: str) -> pd.DataFrame:
    v = pd.read_excel(path, sheet_name="Paramètres", engine="calamine", header=None, dtype=object)
    rows, bloc = [], "texte"
    for i in range(len(v)):
        a = v.iloc[i, 0]
        if pd.isna(a):
            continue
        a = str(a).strip()
        if a.startswith("Temps de trajet"):
            bloc = "palier"
            continue
        if a.startswith("Tranche d'âge"):
            bloc, annees = "poids_age", [int(re.search(r"(\d{4})", str(x)).group(1)) for x in v.iloc[i, 1:].dropna()]
            continue
        if bloc == "palier" and re.search(r"minutes", a):
            rows.append({"prof": prof, "bloc": "palier", "cle": a, "annee": None, "valeur": float(v.iloc[i, 1]),
                         "texte": None})
            continue
        if bloc == "poids_age" and re.search(r"ans", a) and not a.startswith(("Sources", "Champ", "Note")):
            for j, an in enumerate(annees):
                rows.append({"prof": prof, "bloc": "poids_age", "cle": a, "annee": an,
                             "valeur": float(v.iloc[i, 1 + j]), "texte": None})
            continue
        bloc = "texte" if bloc != "palier" or not re.search(r"minutes", a) else bloc
        txt = " | ".join(str(x) for x in v.iloc[i].dropna())
        rows.append({"prof": prof, "bloc": "texte", "cle": f"ligne_{i}", "annee": None, "valeur": None, "texte": txt})
    return pd.DataFrame(rows)


def publie() -> pd.DataFrame:
    p = fichier(DIXIEMES)
    out = []
    for prof, onglet in ONGLET_DIX.items():
        v = pd.read_excel(p, sheet_name=onglet, engine="calamine", header=None)
        i = int(v.index[v[0].astype(str).str.strip() == "Année"][0])
        j = int(v.index[v[0].astype(str).str.startswith("France entière")][0])
        for k in range(1, v.shape[1]):
            out.append({"prof": prof, "annee": int(v.iloc[i, k]), "apl_moyen_publie": float(v.iloc[j, k])})
    return pd.DataFrame(out)


def main():
    tables, params, notes = [], [], []
    for prof, ident in FICHIERS.items():
        p = fichier(ident)
        for an in (2022, 2023, 2024):
            d, mil = lire_onglet(p, f"APL {an}")
            notes.append(f"{prof} onglet APL {an} : « {mil} »")
            tables.append(d.assign(prof=prof, annee=an))
        params.append(parametres(p, prof))
    apl = pd.concat(tables, ignore_index=True)[["com", "prof", "annee", "apl", "pop_std", "pop_tot", "pop_fem"]]
    par = pd.concat(params, ignore_index=True)
    ctl = []
    pub = publie()
    for r in pub.itertuples():
        d = apl[(apl.prof == r.prof) & (apl.annee == r.annee)].dropna(subset=["apl", "pop_std"])
        m = (d.apl * d.pop_std).sum() / d.pop_std.sum()
        ctl.append(controle(f"APL moyen {r.prof} {r.annee}", m, r.apl_moyen_publie,
                            source_publie="DREES 530, Indicateurs d'APL moyens par dixièmes, France hors Mayotte"))
    dom = apl.com.str.startswith("97")
    src = "DREES, APL (jeu 530), fichiers par profession, modifié le 2026-07-22"
    ecrire(apl, "apl_commune", licence="LO2", source=src, millesime="APL 2022, 2023, 2024 (pop. N−2)", commande=CMD,
           dom=f"inclus : {apl[dom].com.nunique()} communes 971–974 ; Mayotte absente du champ DREES",
           controles=ctl, notes="; ".join(sorted(set(notes))))
    ecrire(par, "apl_parametres", licence="LO2", source=src + ", onglet « Paramètres »",
           millesime="poids d'âge DCIR 2020–2022 (onglets 2022–2024)", commande=CMD, dom="sans objet")
    print(f"apl_commune : {len(apl):,} lignes ; apl_parametres : {len(par)} lignes")


if __name__ == "__main__":
    main()
