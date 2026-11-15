"""Distancier routier : temps en voiture entre centres de communes métropolitaines, par OSRM sur OpenStreetMap (M4).

Préparation (une fois, hors Python ; extrait et graphe dans v2/data/raw/osm/ du dépôt principal, non versionnés) :
    curl -L -o france-latest.osm.pbf https://download.geofabrik.de/europe/france-latest.osm.pbf   (≈ 4,8 Go)
    (extrait du miroir download.openstreetmap.fr, plus rapide que Geofabrik ; même donnée OSM)
    osmium tags-filter france-latest.osm.pbf w/highway w/route=ferry r/type=restriction -o routes.osm.pbf
    osmium extract -b -5.4,41.2,9.8,51.2 -s complete_ways routes.osm.pbf -o metro.osm.pbf
    osmium tags-filter metro.osm.pbf w/highway=motorway,motorway_link,trunk,trunk_link,primary,primary_link,\
      secondary,secondary_link,tertiary,tertiary_link,unclassified,residential,living_street,road \
      w/route=ferry r/type=restriction -o voiture.osm.pbf
    osrm-extract -p $(brew --prefix osrm-backend)/share/osrm/profiles/car.lua -t 4 voiture.osm.pbf   (≈ 18 min, 19 Go)
    osrm-contract -t 8 voiture.osrm      (CH : tables bien plus rapides qu'en MLD, même plus court chemin)
    osrm-routed --algorithm ch --max-table-size 10000 --max-header-size 2000000 -t 8 -i 127.0.0.1 -p 5055 voiture.osrm
Run (serveur lancé) : uv run python v2/besoin/donnees/distancier_osrm.py [rayon_km]

Méthode : pour chaque commune i, un appel `table` (source i, destinations = communes à moins de `rayon_km` à vol
d'oiseau, 50 km par défaut), durée et distance routières. On garde les paires à 30 min au plus (dernier palier non
nul de l'APL, SF) et (i, i) à 0. Centres : ceux de geo.api.gouv.fr (comme le distancier à vol d'oiseau), accrochés par
OSRM à la route la plus proche. Profil voiture d'OSRM par défaut (vitesses supposées par type de voie, sans trafic) :
ce n'est pas le distancier Metric de l'Insee utilisé par la DREES (même moteur, réseau et date différents).
Rayon 50 km : sur un pilote de 300 communes, aucune paire à 30 min au plus au-delà de 46,1 km à vol d'oiseau.

Sortie : v2/data/odbl/besoin/distancier_osrm.parquet (com_i, com_j, t_min, d_route_km), **ODbL** (dérivée d'OSM),
non commitée (règle d'attente du 2026-11-15). Contrôles : symétrie approchée, part des communes APL 2024 présentes,
part des paires non routables.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import OUT_LO, ecrire, raw_dir  # noqa: E402
from distancier import R_TERRE, centres  # noqa: E402

URL = "http://127.0.0.1:5055"
T_MAX = 30.0
CMD = "uv run python v2/besoin/donnees/distancier_osrm.py   (serveur osrm-routed lancé, voir l'en-tête)"


def table(src: np.ndarray, dst: np.ndarray, lonlat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Durées (min) et distances (km) routières [source, destination], un appel `table` plusieurs-à-plusieurs."""
    pts = np.r_[src, dst]
    coords = ";".join(f"{lonlat[k, 0]:.6f},{lonlat[k, 1]:.6f}" for k in pts)
    s = ";".join(map(str, range(len(src))))
    d = ";".join(map(str, range(len(src), len(pts))))
    q = f"{URL}/table/v1/driving/{coords}?sources={s}&destinations={d}&annotations=duration,distance"
    for essai in range(3):
        try:
            with urllib.request.urlopen(q, timeout=300) as r:
                x = json.loads(r.read())
            break
        except Exception:
            if essai == 2:
                raise
            time.sleep(1)
    dur = np.array([[np.nan if v is None else v for v in row] for row in x["durations"]], float)
    dist = np.array([[np.nan if v is None else v for v in row] for row in x["distances"]], float)
    return dur / 60.0, dist / 1000.0


def main(rayon_km: float = 50.0, limite: int | None = None, tuile_deg: tuple = (0.2, 0.15)):
    """Un appel par tuile de ~16 km (sources = communes de la tuile, destinations = union de leurs voisines) : CH
    calcule une table plusieurs-à-plusieurs bien plus vite qu'autant d'appels un-à-plusieurs ; mêmes plus courts
    chemins. Chaque source ne garde que ses propres voisines à moins de `rayon_km` à vol d'oiseau."""
    c = centres()
    c = c[~c.com.str.startswith("97")].reset_index(drop=True)
    lonlat = c[["lon", "lat"]].to_numpy()
    lo, la = np.radians(lonlat[:, 0]), np.radians(lonlat[:, 1])
    xyz = np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
    tree = cKDTree(xyz)
    corde = 2 * np.sin(rayon_km / R_TERRE / 2)
    voisins = tree.query_ball_point(xyz, corde)
    n = len(c) if limite is None else limite
    cle = (np.floor(lonlat[:n, 0] / tuile_deg[0]).astype(int) * 10000 + np.floor(lonlat[:n, 1] / tuile_deg[1]).astype(int))
    tuiles = [np.flatnonzero(cle == k) for k in np.unique(cle)]
    t0 = time.time()

    def une(src):
        dst = np.unique(np.concatenate([voisins[i] for i in src]))
        dur, dist = table(src, dst, lonlat)
        pos = {j: k for k, j in enumerate(dst)}
        out = []
        for a, i in enumerate(src):
            js = np.array([j for j in voisins[i] if j != i], int)
            k = np.array([pos[j] for j in js], int)
            out.append((i, js, dur[a, k] if len(k) else np.array([]), dist[a, k] if len(k) else np.array([])))
        return out

    rows, nan, fait = [], 0, 0
    with ThreadPoolExecutor(4) as ex:
        for res in ex.map(une, tuiles):
            for i, js, t, d in res:
                nan += int(np.isnan(t).sum())
                keep = t <= T_MAX
                rows.append(pd.DataFrame({"i": i, "j": np.r_[i, js[keep]], "t_min": np.r_[0.0, t[keep]],
                                          "d_route_km": np.r_[0.0, d[keep]]}))
            fait += len(res)
            if fait // 2000 != (fait - len(res)) // 2000:
                print(f"{fait}/{n} communes, {time.time() - t0:.0f} s", flush=True)
    p = pd.concat(rows, ignore_index=True)
    codes = c.com.to_numpy()
    out = pd.DataFrame({"com_i": codes[p.i], "com_j": codes[p.j], "t_min": p.t_min.astype("float32"),
                        "d_route_km": p.d_route_km.astype("float32")})
    paires = sum(len(v) - 1 for v in voisins[:n])
    ctl = [{"controle": "paires non routables (durée nulle d'OSRM)", "reconstruit": nan / max(paires, 1),
            "publie": 0.0, "ecart_rel": nan / max(paires, 1), "seuil": 0.005, "ok": bool(nan / max(paires, 1) <= 0.005)}]
    if limite is None:
        r = out.merge(out, left_on=["com_i", "com_j"], right_on=["com_j", "com_i"], suffixes=("", "_r"))
        asym = float(np.median(np.abs(r.t_min - r.t_min_r)[r.com_i != r.com_j]))
        ctl.append({"controle": "asymétrie médiane |t_ij − t_ji| (min, sens uniques)", "reconstruit": asym,
                    "ok": bool(asym < 2.0)})
        a = pd.read_parquet(OUT_LO / "apl_commune.parquet", columns=["com", "annee"])
        a = {x for x in a[a.annee == 2024].com if not x.startswith("97")}
        part = len(a & set(codes)) / len(a)
        ctl.append({"controle": "communes APL 2024 métropolitaines présentes", "reconstruit": part, "publie": 1.0,
                    "ecart_rel": 1 - part, "seuil": 0.005, "ok": bool(1 - part <= 0.005)})
    lu = (raw_dir() / "osm" / "LU_LE")
    print(f"{n:,} communes, {len(out):,} paires à ≤ {T_MAX} min, {time.time() - t0:.0f} s ; {ctl}")
    if limite is not None:
        return out
    ecrire(out, "distancier_osrm", licence="ODbL",
           source="OpenStreetMap (Geofabrik france-latest.osm.pbf), OSRM (profil car.lua, CH) ; centres geo.api.gouv.fr",
           millesime=f"extrait OSM lu le {lu.read_text().strip() if lu.exists() else '?'}", commande=CMD,
           controles=ctl, dom="hors champ (extrait métropolitain)",
           notes=f"rayon de recherche {rayon_km} km à vol d'oiseau ; paires gardées à t ≤ {T_MAX} min ; (i, i) à 0")
    return out


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 50.0)
