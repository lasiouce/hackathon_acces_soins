"""Distancier de repli : distance à vol d'oiseau entre centres de communes, temps routier approché (M4, en attendant OSRM).

Run (racine du dépôt) : uv run python v2/besoin/donnees/distancier.py [rayon_km]   (≈ 10 s ; rayon 35 km par défaut)

Source : geo.api.gouv.fr, centres des communes et des arrondissements municipaux (Paris, Lyon, Marseille), fichiers
`geoapi_communes_centre.json` et `geoapi_arm_centre.json` de v2/data/raw/insee/ (téléchargés le 2026-11-14),
Licence Ouverte 2.0. Le « centre » est le point fourni par l'API, pas forcément la mairie ni le barycentre de la
population (non documenté ici).

Méthode : distance du grand cercle (rayon terrestre 6 371 km) ; paires i ≠ j à moins de `rayon_km`, plus la paire
(i, i) à 0. Le temps est **supposé** : t = détour × d / v, avec détour = 1,3 et v = 60 km/h (deux valeurs supposées,
non mesurées, ni sourcées ici) ; M4 doit les traiter comme des hyperparamètres, `d_km` est la seule colonne mesurée.
Rayon 35 km : à détour 1,3 et 60 km/h, couvre 21 min de route, au-delà du dernier palier non nul de l'APL pour CD,
MK et IDE (20 min) mais pas pour les SF (30 min, soit ~23 km à vol d'oiseau sous ces hypothèses : couvert).
Pas de téléchargement OSM/OSRM (4,8 Go) sans l'accord de l'utilisateur·rice.
DOM : inclus, sans paire inter-îles (le rayon les sépare de fait) ; Mayotte présente dans geo.api mais hors APL.

Sortie : v2/data/processed/besoin/distancier_vol_oiseau.parquet (com_i, com_j, d_km, t_min_suppose), Licence
Ouverte 2.0, **non commitée** (volumineuse, régénérable en quelques secondes ; ignorée par .gitignore).
Contrôles : symétrie, part des communes de l'APL 2024 présentes dans le distancier.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import OUT_LO, ecrire, raw_dir  # noqa: E402

R_TERRE = 6371.0
DETOUR, VITESSE = 1.3, 60.0  # supposés
CMD = "uv run python v2/besoin/donnees/distancier.py"


def centres() -> pd.DataFrame:
    rows = []
    for f, arm in [("geoapi_communes_centre.json", False), ("geoapi_arm_centre.json", True)]:
        for x in json.loads((raw_dir() / "insee" / f).read_text(encoding="utf-8")):
            lon, lat = x["centre"]["coordinates"]
            rows.append((x["code"], lon, lat, arm))
    return pd.DataFrame(rows, columns=["com", "lon", "lat", "arrondissement"])


def main(rayon_km: float = 35.0):
    c = centres()
    lo, la = np.radians(c.lon.to_numpy()), np.radians(c.lat.to_numpy())
    xyz = np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
    corde = 2 * np.sin(rayon_km / R_TERRE / 2)
    p = cKDTree(xyz).query_pairs(corde, output_type="ndarray")
    p = np.r_[p, p[:, ::-1], np.c_[np.arange(len(c)), np.arange(len(c))]]
    ch = np.linalg.norm(xyz[p[:, 0]] - xyz[p[:, 1]], axis=1)
    d = 2 * R_TERRE * np.arcsin(np.clip(ch / 2, 0, 1))
    codes = c.com.to_numpy()
    out = pd.DataFrame({"com_i": codes[p[:, 0]], "com_j": codes[p[:, 1]], "d_km": d.astype("float32"),
                        "t_min_suppose": (DETOUR * d / VITESSE * 60).astype("float32")})
    out = out.sort_values(["com_i", "d_km"], ignore_index=True)
    sym = len(out) == len(out.merge(out[["com_i", "com_j"]].rename(columns={"com_i": "com_j", "com_j": "com_i"})))
    ctl = [{"controle": "symétrie i→j = j→i", "ok": bool(sym)}]
    apl = OUT_LO / "apl_commune.parquet"
    if apl.exists():
        a = pd.read_parquet(apl, columns=["com", "annee"])
        a = set(a[a.annee == 2024].com)
        part = len(a & set(codes)) / len(a)
        ctl.append({"controle": "communes APL 2024 présentes", "reconstruit": part, "publie": 1.0,
                    "ecart_rel": 1 - part, "seuil": 0.005, "ok": bool(1 - part <= 0.005),
                    "source_publie": "apl_commune.parquet (DREES 530)", "absentes": sorted(a - set(codes))[:20]})
    print(f"{len(c):,} centres, {len(out):,} paires à ≤ {rayon_km} km ; {ctl}")
    ecrire(out, "distancier_vol_oiseau", licence="LO2",
           source="geo.api.gouv.fr, centres des communes et arrondissements (fichiers du 2026-11-14)",
           millesime="géographie 2026", commande=CMD, controles=ctl,
           dom="inclus (971–976), sans paire inter-territoires ; Mayotte hors champ APL",
           notes=f"rayon {rayon_km} km ; t_min_suppose = {DETOUR} × d / {VITESSE} km/h (supposé) ; "
                 "communes et arrondissements PLM tous deux présents")


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 35.0)
