"""Fourchettes 2050 par département et carte de leur largeur relative.

Deux composantes, jamais additionnées :
  (a) propagation de la connaissance (leviers.py : 500 tirages, décisions au statu quo) : (P95 − P5) / N tendanciel
  (b) backtest extrapolé (méthode A3) au département : pente de l'APE ∝ h par département (banc N1, défaut
      twin_of(StockFlowLocal), table privée de leviers.table), × 1,6 × h(2050), en demi-largeur
Seuil « assez sûr pour décider » (dérivé) : la largeur (a) est plus petite que deux fois l'effet national à 2050
de quotas × 1,2 (mesuré ici, par profession). Le levier le plus fort se distingue alors de la bande de connaissance.
Carte : fond départemental v1 (app/assets/departements-avec-outre-mer.geojson), hexagone seulement ; SVG pour le
rapport, TikZ pour le prétirage (pdfLaTeX n'inclut pas de SVG).

Run (racine) : PYTHONPATH=<instantané>:v2:. uv run python -m sensibilite.carte backtest   # pentes par département
               PYTHONPATH=<instantané>:v2:. uv run python -m sensibilite.carte carte      # après leviers.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from sante import estimators as V1
from jumeau.estimators import twin_of
from sensibilite.facteurs import PROFS
from sensibilite.leviers import Model, _u, table
from validation.forecast import bench, design

OUT = Path("v2/sensibilite/out")
FIG = Path("v2/docs/lab/figures")
PAPER = Path("v2/papers/axe5-sensibilite/figures")
K_A3 = 1.6
# rampe séquentielle bleue (skill dataviz, palette de référence), classes ordinales : pas plus clair que 250
CLASSES = [("#86b6ef", "assez sûr"), ("#3987e5", "limite"), ("#1c5cab", "incertain"), ("#0d366b", "très incertain")]
NOM = {"sages-femmes": "Sages-femmes", "dentistes": "Dentistes", "pharmaciens": "Pharmaciens", "kines": "Kinés",
       "infirmiers": "Infirmiers"}


def backtest_dep():
    rows = []
    for p in PROFS:
        t = table(p, "central").drop(columns="sector")
        e = bench({"twin": twin_of(V1.StockFlowLocal)}, t, design(t))
        e = e[e.n_origin >= 30]
        for d, g in e.groupby("territory"):
            h, a = g.h.to_numpy(float), g.ape.to_numpy()
            rows.append(dict(profession=p, dep=d, pente_pct_par_an=(h * a).sum() / (h ** 2).sum(), n_cas=len(g),
                             h_max=int(g.h.max())))
        print(p, "fait", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "backtest_dep.csv", index=False)


def effet_quotas() -> dict:
    """Effet national à 2050 de quotas × 1,2 (décisions au statu quo sinon), en % du tendanciel."""
    out = {}
    for p in PROFS:
        m = Model(p)
        u = np.array([_u(f) for f in m.f])
        base = m(u)[-1]
        u[[f.name for f in m.f].index("quotas")] = 1.0 - 1e-12
        out[p] = 100 * (m(u)[-1] / base - 1)
    return out


def classe(w, seuil):
    return 0 if w < seuil else 1 if w < 2 * seuil else 2 if w < 4 * seuil else 3


def geometries():
    g = json.load(open("app/assets/departements-avec-outre-mer.geojson"))
    out = {}
    for f in g["features"]:
        code = f["properties"]["code"]
        if code.startswith("97"):
            continue
        geo = f["geometry"]
        polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
        rings = []
        for poly in polys:
            ring = np.array(poly[0])
            step = max(1, len(ring) // 60)                     # simplification : ≤ 60 sommets par anneau
            r = ring[::step]
            if len(r) >= 4:
                rings.append(r)
        out[code] = rings
    return out


def project(r):
    c = math.cos(math.radians(46.5))
    return np.c_[(r[:, 0] + 5.5) * c, 51.5 - r[:, 1]]          # degrés -> unités planes, nord en haut


def carte():
    a = pd.concat([pd.read_csv(f, dtype={"dep": str}) for f in sorted(OUT.glob("fourchettes_dep_*.csv"))])
    b = pd.read_csv(OUT / "backtest_dep.csv", dtype={"dep": str})
    q = effet_quotas()
    d = a.merge(b, on=["profession", "dep"], how="left")
    d["h"] = 2050 - d.profession.map(lambda p: int(table(p, "central").year.max()))
    d["b_demi_largeur_pct"] = K_A3 * d.pente_pct_par_an * d.h
    d["effet_quotas_pct"] = d.profession.map(q)
    d["seuil_pct"] = 2 * d.effet_quotas_pct.abs()
    d["classe"] = [classe(w, s) for w, s in zip(d.largeur_rel_pct, d.seuil_pct)]
    d.to_csv(OUT / "fourchettes_dep.csv", index=False)
    s = d.groupby("profession").agg(seuil=("seuil_pct", "first"), assez_sur=("classe", lambda x: int((x == 0).sum())),
                                    n=("dep", "size"), mediane_a=("largeur_rel_pct", "median"),
                                    mediane_b=("b_demi_largeur_pct", "median"))
    print(s.round(1).to_string())
    geo = geometries()
    pts = np.vstack([project(r) for rs in geo.values() for r in rs])
    W, H = pts[:, 0].max(), pts[:, 1].max()
    svg, tikz = _svg(d, geo, W, H, s), _tikz(d, geo, W, H)
    FIG.mkdir(parents=True, exist_ok=True)
    PAPER.mkdir(parents=True, exist_ok=True)
    (FIG / "2026-11-14-axe5-fourchettes-dep.svg").write_text(svg)
    (PAPER / "carte_dep.tex").write_text(tikz)


def _svg(d, geo, W, H, s):
    sc, pw, ph = 40.0, None, None
    pw, ph = W * sc + 20, H * sc + 50
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {pw * 3:.0f} {ph * 2 + 60:.0f}" '
           'font-family="system-ui, sans-serif" font-size="14">',
           '<rect width="100%" height="100%" fill="#ffffff"/>']
    for i, p in enumerate(PROFS):
        ox, oy = (i % 3) * pw, (i // 3) * ph
        dd = d[d.profession == p].set_index("dep")
        out.append(f'<text x="{ox + 10:.0f}" y="{oy + 22:.0f}" fill="#1f1f1d" font-weight="600">{NOM[p]} — '
                   f'seuil {s.loc[p, "seuil"]:.0f} %</text>')
        for code, rings in geo.items():
            c = CLASSES[int(dd.loc[code, "classe"])][0] if code in dd.index else "#e4e3df"
            tip = (f"{code} : largeur {dd.loc[code, 'largeur_rel_pct']:.0f} %" if code in dd.index else f"{code} : sans donnée")
            for r in rings:
                xy = project(r) * sc
                path = "M" + "L".join(f"{x + ox + 10:.1f},{y + oy + 35:.1f}" for x, y in xy) + "Z"
                out.append(f'<path d="{path}" fill="{c}" stroke="#ffffff" stroke-width="0.8"><title>{tip}</title></path>')
    lx, ly = 2 * pw + 20, ph + 40
    out.append(f'<text x="{lx}" y="{ly}" fill="#1f1f1d" font-weight="600">Largeur P5–P95 à 2050 (connaissance)</text>')
    lab = ["< seuil", "1 à 2 × seuil", "2 à 4 × seuil", "> 4 × seuil"]
    for j, (c, nm) in enumerate(CLASSES):
        out.append(f'<rect x="{lx}" y="{ly + 14 + 26 * j}" width="18" height="18" rx="3" fill="{c}"/>'
                   f'<text x="{lx + 26}" y="{ly + 28 + 26 * j}" fill="#4a4a46">{nm} ({lab[j]})</text>')
    out.append(f'<text x="{lx}" y="{ly + 134}" fill="#4a4a46">seuil = 2 × effet national de quotas × 1,2</text>')
    out.append(f'<text x="{lx}" y="{ly + 154}" fill="#4a4a46">gris : sans donnée ; aucun backtest à 2050</text>')
    out.append("</svg>")
    return "\n".join(out)


def _tikz(d, geo, W, H):
    sc = 0.62                                                   # cm par unité : ≈ 5 cm de large par carte
    lines = ["% Généré par v2/sensibilite/carte.py ; classes : largeur P5–P95 (connaissance) / seuil",
             "\\begin{tikzpicture}[x=1cm,y=-1cm,line width=0.15pt]"]
    for j, (c, _) in enumerate(CLASSES):
        lines.append(f"\\definecolor{{cl{j}}}{{HTML}}{{{c[1:]}}}")
    lines.append("\\definecolor{clna}{HTML}{E4E3DF}")
    for i, p in enumerate(PROFS):
        ox, oy = (i % 3) * (W * sc + 0.6), (i // 3) * (H * sc + 1.0)
        dd = d[d.profession == p].set_index("dep")
        lines.append(f"\\node[anchor=west,font=\\footnotesize\\bfseries] at ({ox:.2f},{oy - 0.3:.2f}) {{{NOM[p]}}};")
        for code, rings in geo.items():
            c = f"cl{int(dd.loc[code, 'classe'])}" if code in dd.index else "clna"
            for r in rings:
                xy = project(r) * sc
                lines.append(f"\\fill[{c},draw=white] " + " -- ".join(f"({x + ox:.2f},{y + oy:.2f})" for x, y in xy)
                             + " -- cycle;")
    lx, ly = 2 * (W * sc + 0.6), H * sc + 1.3
    lab = ["assez sûr ($<$ seuil)", "limite (1--2$\\times$)", "incertain (2--4$\\times$)", "très incertain ($>4\\times$)"]
    for j in range(4):
        lines.append(f"\\fill[cl{j}] ({lx:.2f},{ly + 0.5 * j:.2f}) rectangle ++(0.3,0.3);"
                     f"\\node[anchor=west,font=\\scriptsize] at ({lx + 0.35:.2f},{ly + 0.5 * j + 0.15:.2f}) {{{lab[j]}}};")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)


if __name__ == "__main__":
    {"backtest": backtest_dep, "carte": carte}[sys.argv[1]]()
