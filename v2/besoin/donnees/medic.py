"""Open Medic (Assurance maladie, inter-régimes) : vaccins (ATC4 J07*, dont J07BB antigrippaux), 2014–2025.

Run (racine du dépôt) : uv run python v2/besoin/donnees/medic.py   (≈ 1 min ; 24 fichiers ATC4, ~8 Mo, dans
v2/data/raw/besoin/medic/ s'ils manquent). Le serveur n'accepte qu'un téléchargement à la fois par session : ne
pas lancer pendant une lecture d'Open DAMIR (« Limite de téléchargements atteinte », observé le 2026-11-15).

Source : Open Medic, bases complémentaires ATC4 (`NB_AAAA_atc4_age_sexe_reg` et `NB_AAAA_atc4`), lien à jeton sur
`open-data-assurance-maladie.ameli.fr/medicaments/download2.php?Dir_Rep=AAAA_ATC4`, Licence Ouverte 2.0.
Descriptif lu (xls « descriptif des variables de la série Open Medic », consulté le 2026-11-15) :
  - BEN_REG = **région de résidence du bénéficiaire** (confirme l'hypothèse de l'exploration), 13 zones,
    DOM regroupés en un code 5, 0 et 99 = inconnu ;
  - AGE : 0 (0–19 ans), 20 (20–59), 60 (60 ans et plus), 99 inconnu ; SEXE 1, 2, 9 ;
  - REM montant remboursé, BSE base de remboursement, BOITES boîtes délivrées, NBC nombre de consommants (bases NB_).
Année civile de délivrance (pas de saison) : une campagne d'octobre à février chevauche deux années.

Sortie (Licence Ouverte 2.0, commitée) : v2/data/processed/besoin/medic_vaccins.parquet
(annee, atc4, l_atc4, age, sexe, ben_reg, nbc, rem, bse, boites).
Contrôle : Σ régions × âges × sexes des boîtes et du remboursé J07BB = total national publié (`NB_AAAA_atc4`).
"""
from __future__ import annotations

import io
import re
import sys
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import CACHE, controle, ecrire  # noqa: E402

BASE = "https://open-data-assurance-maladie.ameli.fr/medicaments/"
CMD = "uv run python v2/besoin/donnees/medic.py"
ANNEES = range(2014, 2026)


def fichier(annee: int, nom: str) -> Path:
    p = CACHE / "medic" / f"{nom}.CSV.gz"
    if not p.exists():
        html = urllib.request.urlopen(BASE + f"download2.php?Dir_Rep={annee}_ATC4", timeout=60).read().decode()
        m = re.search(r'href="\./(download_file\.php\?token=[0-9a-f]+&file=[^"]*/' + nom + r'\.CSV\.gz)"', html, re.I)
        if not m:
            raise SystemExit(f"pas de lien pour {nom}")
        b = urllib.request.urlopen(BASE + m.group(1), timeout=300).read()
        if b[:2] != b"\x1f\x8b":
            raise SystemExit(f"{nom} : réponse non gzip ({b[:120]!r}) — téléchargement en cours ailleurs ?")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
    return p


def lire(p: Path) -> pd.DataFrame:
    d = pd.read_csv(p, sep=";", dtype=str, encoding="latin-1", compression="gzip")
    d.columns = [c.strip().lower() for c in d.columns]
    for c in ["nbc", "rem", "bse", "boites"]:
        d[c] = pd.to_numeric(d[c].str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
                             errors="coerce")
    return d


def main():
    parts, ctl = [], []
    for a in ANNEES:
        d = lire(fichier(a, f"NB_{a}_atc4_age_sexe_reg"))
        d = d[d.atc4.str.startswith("J07")].assign(annee=a)
        n = lire(fichier(a, f"NB_{a}_atc4"))
        n = n[n.atc4 == "J07BB"]
        g = d[d.atc4 == "J07BB"]
        for v in ["boites", "rem"]:
            ctl.append(controle(f"J07BB {v} {a}", g[v].sum(), n[v].sum(),
                                source_publie=f"Open Medic NB_{a}_atc4 (national)"))
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    d = d.rename(columns={"ben_reg": "ben_reg"})[["annee", "atc4", "l_atc4", "age", "sexe", "ben_reg", "nbc", "rem",
                                                  "bse", "boites"]]
    for c in ["age", "sexe", "ben_reg"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int16")
    ecrire(d, "medic_vaccins", licence="LO2", source="Assurance maladie, Open Medic, bases complémentaires ATC4",
           millesime=f"{min(ANNEES)}–{max(ANNEES)} (année civile de délivrance)", commande=CMD, controles=ctl,
           dom="DOM regroupés (ben_reg 5), non séparables ; 0 et 99 = inconnu")
    print(f"medic_vaccins : {len(d):,} lignes")


if __name__ == "__main__":
    main()
