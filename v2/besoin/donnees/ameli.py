"""data.ameli.fr (CNAM, API Opendatasoft) : pathologies (effectifs, dépenses), patientèle, honoraires, démographie.

Run (racine du dépôt) : uv run python v2/besoin/donnees/ameli.py   (≈ 1 min ; télécharge 5 exports parquet, ~70 Mo,
dans v2/data/raw/besoin/ameli/ s'ils manquent)

**Licence : ODbL 1.0** pour les cinq jeux (métadonnées de l'API, lues le 2026-11-15). La décision de licence des
tables dérivées est ouverte (registre § Open) : les sorties vont dans `v2/data/odbl/besoin/`, **ignoré par git** ;
seuls ce script et le manifeste sont commités. Reconstruire = relancer ce script.

Descriptifs lus (champ `description` des métadonnées de l'API) :
  - effectifs (« Data pathologies », modifié le 2026-10-28) : patients pris en charge, tous régimes, par pathologie
    (3 niveaux), classe d'âge quinquennale, sexe, région et département, 2015–2024 ; population de référence =
    population de la cartographie (67,6 M de bénéficiaires en 2024) ; cellules < 11 patients masquées (NS) ;
  - depenses (modifié le 2026-07-06) : dépenses remboursées par pathologie × poste (31 postes niveau 2),
    **national seulement**, 2015–2024 ; type_somme Partiel (poste) / Total ;
  - patientele (modifié le 2026-10-28) : **nombre moyen** de patients uniques par professionnel (file active
    moyenne), pas un total ; professionnels libéraux actifs au 31/12, ≥ 1 € d'honoraires, métropole et 5 DROM
    (Mayotte comprise) ; NS si < 5 professionnels. Le département est celui des professionnels (l'indicateur est
    une moyenne par professionnel, rangée selon son lieu d'exercice) : déduit du libellé, la page « Méthode » du
    site n'a pas été lue. Pas de pharmaciens ;
  - honoraires-detailles (modifié le 2026-10-12) : montants d'honoraires sans dépassement par type (actes,
    forfaits, déplacements) et dépassements, total et moyen (APE), département ; pas de nombre d'actes ;
  - demographie-effectifs-et-les-densites (modifié le 2026-10-28) : effectifs libéraux par département × âge ×
    sexe, et densités ; grain départemental confirmé.
  - depenses-par-poste : écarté, c'est le jeu « risques professionnels » (AT/MP du régime général), hors sujet.
Codes : département « 999 » = total de la région de la ligne ; région « 99 » et département « 999 » = France
entière (observé le 2026-11-15 : compter les « 999 » comme national double le total). Colonnes `*_ns` : valeur
masquée à la source.

Sorties (ODbL, non commitées) : v2/data/odbl/besoin/ameli_{pathologies_effectifs, pathologies_depenses, patientele,
honoraires, demographie}.parquet. Contrôles : Σ départements = ligne nationale, par profession (ou pathologie) et
par année ; pour la patientèle (moyenne), Σ_dép moyenne × effectif / Σ effectif = moyenne nationale.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import CACHE, controle, ecrire  # noqa: E402

API = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets/{}/exports/parquet"
CMD = "uv run python v2/besoin/donnees/ameli.py"
SRC = "CNAM, data.ameli.fr, jeu « {} » (export parquet de l'API Opendatasoft, lu le 2026-11-15)"
PROF = {"Sages-femmes": "SF", "Ensemble des chirurgiens-dentistes": "CD", "Masseurs-kinésithérapeutes": "MK",
        "Infirmiers": "IDE", "Ensemble des médecins généralistes": "MG"}
DOM = "inclus : départements 971, 972, 973, 974, 976 (Mayotte comprise) ; région 99 = France entière"


def brut(jeu: str) -> pd.DataFrame:
    p = CACHE / "ameli" / f"{jeu}.parquet"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(urllib.request.urlopen(API.format(jeu), timeout=900).read())
    d = pd.read_parquet(p)
    d.columns = [c.lstrip("﻿") for c in d.columns]
    d["annee"] = pd.to_datetime(d["annee"]).dt.year.astype("int16")
    return d


def num(s: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Valeur numérique et masque « NS » (secret statistique) ; « NC » (non calculé) devient NaN sans masque."""
    t = s.astype("string").str.strip()
    return pd.to_numeric(t.str.replace(",", ".", regex=False), errors="coerce"), t.eq("NS")


def par_dep(d: pd.DataFrame, cles: list[str], val: str, nom: str, src: str) -> list[dict]:
    """Σ départements (hors 999) contre la ligne France entière (région 99), pour chaque combinaison de `cles`."""
    dep = d[d.departement != "999"].groupby(cles)[val].sum()
    nat = d[d.region.astype(str) == "99"].groupby(cles)[val].sum()
    j = pd.concat([dep.rename("dep"), nat.rename("nat")], axis=1).dropna()
    return [controle(f"{nom} {' '.join(map(str, k if isinstance(k, tuple) else (k,)))}", r.dep, r.nat,
                     source_publie=src) for k, r in j.iterrows() if r.nat]


def demographie() -> pd.DataFrame:
    d = brut("demographie-effectifs-et-les-densites")
    d = d[["annee", "profession_sante", "region", "departement", "classe_age", "libelle_sexe", "effectif", "densite"]]
    d = d.assign(prof=d.profession_sante.map(PROF))
    tot = d[(d.classe_age == "tout_age") & (d.libelle_sexe == "tout sexe") & d.prof.notna()]
    ctl = par_dep(tot, ["prof", "annee"], "effectif", "effectifs libéraux", "data.ameli.fr, ligne 999")
    ecrire(d, "ameli_demographie", licence="ODbL", source=SRC.format("demographie-effectifs-et-les-densites"),
           millesime=f"{d.annee.min()}–{d.annee.max()} (au 31/12)", commande=CMD, dom=DOM, controles=ctl)
    return d


def patientele(demo: pd.DataFrame):
    d = brut("patientele")
    v, ns = num(d.nombre_patients_uniques)
    d = d.assign(prof=d.profession_sante.map(PROF), patients_uniques_moy=v, patients_uniques_ns=ns)
    d = d[["annee", "profession_sante", "prof", "region", "departement", "patients_uniques_moy", "patients_uniques_ns"]]
    eff = demo[(demo.classe_age == "tout_age") & (demo.libelle_sexe == "tout sexe")][
        ["annee", "profession_sante", "region", "departement", "effectif"]]
    j = d[d.prof.notna()].merge(eff, on=["annee", "profession_sante", "region", "departement"], how="left")
    ctl = []
    for (p, a), g in j.groupby(["prof", "annee"]):
        dep = g[(g.departement != "999") & g.patients_uniques_moy.notna()]
        nat = g[g.region == "99"].patients_uniques_moy
        if len(nat) and dep.effectif.sum():
            ctl.append(controle(f"patientèle moyenne {p} {a}", (dep.patients_uniques_moy * dep.effectif).sum()
                                / dep.effectif.sum(), nat.iloc[0],
                                source_publie="data.ameli.fr patientèle, ligne 999 ; poids = effectifs (démographie)"))
    ecrire(d, "ameli_patientele", licence="ODbL", source=SRC.format("patientele"),
           millesime=f"{d.annee.min()}–{d.annee.max()}", commande=CMD, dom=DOM, controles=ctl,
           notes="moyenne par professionnel (file active moyenne), pas un total ; total ≈ moyenne × effectif")


def honoraires():
    d = brut("honoraires-detailles")
    keep = ["annee", "profession_sante", "region", "departement", "honoraires_ordre_niv_1", "type_honoraires_niveau_1",
            "honoraires_ordre_niv_2", "type_honoraires_niveau_2", "honoraires_ordre_niv_3", "type_honoraires_niveau_3",
            "montant_honoraires", "montant_honoraires_moyens"]
    d = d[keep].assign(prof=d.profession_sante.map(PROF))
    ens = d[(d.honoraires_ordre_niv_1 == 6) & d.prof.notna()]
    ctl = par_dep(ens, ["prof", "annee"], "montant_honoraires", "honoraires (ensemble)", "data.ameli.fr, ligne 999")
    ecrire(d, "ameli_honoraires", licence="ODbL", source=SRC.format("honoraires-detailles"),
           millesime=f"{d.annee.min()}–{d.annee.max()}", commande=CMD, dom=DOM, controles=ctl,
           notes="montants en euros, sans nombre d'actes ; ordre 6 = ensemble des honoraires")


def pathologies():
    d = brut("effectifs")
    keep = ["annee", "patho_niv1", "patho_niv2", "patho_niv3", "top", "cla_age_5", "sexe", "region", "dept", "ntop",
            "npop", "prev", "niveau_prioritaire"]
    d = d[keep].rename(columns={"dept": "departement"})
    for c in ["ntop", "npop", "prev"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["ntop_ns"] = d.ntop.isna() & d.npop.notna()
    tot = d[(d.cla_age_5 == "tsage") & (d.sexe.astype(str) == "9")]
    # le contrôle de l'axe 4 : Σ départements = France entière ; NS (< 11) et l'arrondi apparent à la dizaine
    # rendent l'égalité approximative pour les petites pathologies : on contrôle la population et les 17 groupes
    # de niveau 1 (top se terminant par _CAT_CAT), et on rapporte la distribution des écarts sur toutes les lignes.
    ctl = par_dep(tot[tot.top == tot.top.iloc[0]], ["annee"], "npop", "population cartographie",
                  "data.ameli.fr effectifs, ligne 999")
    niv1 = tot[tot.top.str.endswith("_CAT_CAT")]
    ctl += par_dep(niv1, ["top", "annee"], "ntop", "patients", "data.ameli.fr effectifs, ligne 999")
    # Σ départements = Σ régions (lignes 999 hors région 99) : l'écart au national vient des bénéficiaires sans
    # région attribuée (0,3 % en 2024, 1,4 % en 2015, mesuré le 2026-11-15), pas de la lecture
    reg = tot[(tot.departement == "999") & (tot.region.astype(str) != "99")]
    dep = tot[tot.departement != "999"]
    for k in ["npop"]:
        for a in sorted(tot.annee.unique()):
            r = reg[(reg.annee == a) & (reg.top == tot.top.iloc[0])][k].sum()
            ctl.append(controle(f"population cartographie Σ dép. = Σ régions {a}",
                                dep[(dep.annee == a) & (dep.top == tot.top.iloc[0])][k].sum(), r,
                                source_publie="data.ameli.fr effectifs, lignes régionales (999)"))
    for (t, a), g in niv1.groupby(["top", "annee"]):
        r = g[(g.departement == "999") & (g.region.astype(str) != "99")].ntop.sum()
        ctl.append(controle(f"patients {t} Σ dép. = Σ régions {a}", g[g.departement != "999"].ntop.sum(), r,
                            source_publie="data.ameli.fr effectifs, lignes régionales (999)"))
    src = SRC.format("effectifs")
    ecrire(d, "ameli_pathologies_effectifs", licence="ODbL", source=src, millesime=f"{d.annee.min()}–{d.annee.max()}",
           commande=CMD, dom=DOM, controles=ctl,
           notes="cla_age_5 'tsage' = tous âges ; sexe 9 = tous ; NS si < 11 patients (ntop_ns)")
    e = brut("depenses")
    keep = ["annee", "patho_niv1", "patho_niv2", "patho_niv3", "top", "dep_niv_1", "dep_niv_2", "montant", "ntop",
            "n_recourant_au_poste", "montant_moy", "type_somme", "niveau_prioritaire"]
    e = e[keep]
    ctl = []
    for (t, a), g in e.groupby(["top", "annee"]):
        tot_ = g[g.dep_niv_2 == "Total des dépenses remboursées"].montant
        part = g[(g.type_somme == "Partiel")].montant.sum()
        if len(tot_) and tot_.iloc[0]:
            ctl.append(controle(f"dépenses Σ postes {t} {a}", part, tot_.iloc[0], seuil=0.005,
                                source_publie="data.ameli.fr dépenses, ligne « Total des dépenses remboursées »"))
    ecrire(e, "ameli_pathologies_depenses", licence="ODbL", source=SRC.format("depenses"),
           millesime=f"{e.annee.min()}–{e.annee.max()}", commande=CMD, dom="national seulement (France entière)",
           controles=ctl, notes="montants en euros ; pas d'actes ; ni âge ni sexe")


def main():
    demo = demographie()
    patientele(demo)
    honoraires()
    pathologies()


if __name__ == "__main__":
    main()
