"""Chemins, écriture des tables et contrôles de totaux, communs aux modules d'ingestion du besoin (axe 4).

Deux dossiers de sortie, selon la licence de la source :
  - Licence Ouverte 2.0 (Open DAMIR, Open Medic, APL DREES, IQVIA, geo.api.gouv.fr) : `v2/data/processed/besoin/`,
    commité ;
  - ODbL (jeux data.ameli.fr) : `v2/data/odbl/besoin/`, ignoré par git tant que la décision de licence est ouverte
    (registre § Open, « Licence des tables dérivées de jeux ODbL »). Seuls le script et le manifeste sont commités.
Chaque table écrite laisse une fiche `<nom>.meta.json` (source, millésime, licence, commande, contrôles) que
`manifest.py` rassemble dans `v2/besoin/donnees/MANIFEST.md`.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT_LO = ROOT / "v2" / "data" / "processed" / "besoin"
OUT_ODBL = ROOT / "v2" / "data" / "odbl" / "besoin"
CACHE = ROOT / "v2" / "data" / "raw" / "besoin"  # téléchargements non versionnés (v2/data/raw/ est ignoré)
LICENCES = {"LO2": "Licence Ouverte 2.0 (Etalab)", "ODbL": "Open Database License 1.0"}


def raw_dir() -> Path:
    """Données brutes du dépôt : `SANTE_RAW`, sinon `v2/data/raw/` du dépôt, sinon celui du dépôt principal
    (une copie de travail git n'a pas les données brutes, non versionnées)."""
    if os.environ.get("SANTE_RAW"):
        return Path(os.environ["SANTE_RAW"])
    p = ROOT / "v2" / "data" / "raw"
    if (p / "insee").exists():
        return p
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    return (ROOT / common).resolve().parent / "v2" / "data" / "raw"


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def ecrire(df: pd.DataFrame, nom: str, *, licence: str, source: str, millesime: str, commande: str,
           dom: str, controles: list[dict] | None = None, notes: str = "") -> Path:
    """Écrit `df` en parquet dans le dossier de sa licence, avec sa fiche de manifeste."""
    assert licence in LICENCES, licence
    out = (OUT_ODBL if licence == "ODbL" else OUT_LO) / f"{nom}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    meta = {"table": out.name, "chemin": str(out.relative_to(ROOT)), "lignes": int(len(df)),
            "colonnes": list(map(str, df.columns)), "sha256_16": sha16(out), "licence": LICENCES[licence],
            "commite": licence != "ODbL", "source": source, "millesime": millesime, "commande": commande,
            "dom": dom, "controles": controles or [], "notes": notes,
            "ecrit_le": dt.datetime.now().isoformat(timespec="seconds")}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def controle(nom: str, reconstruit: float, publie: float, seuil: float = 0.005, source_publie: str = "") -> dict:
    """Écart relatif |reconstruit − publié| / publié, comparé au seuil (0,5 % par défaut, critère de l'axe 4)."""
    ecart = abs(reconstruit - publie) / abs(publie) if publie else float("nan")
    r = {"controle": nom, "reconstruit": float(reconstruit), "publie": float(publie), "ecart_rel": ecart,
         "seuil": seuil, "ok": bool(ecart <= seuil), "source_publie": source_publie}
    print(f"  [{'ok' if r['ok'] else 'ÉCHEC'}] {nom} : {reconstruit:,.0f} vs {publie:,.0f} ({ecart:.4%})")
    return r
