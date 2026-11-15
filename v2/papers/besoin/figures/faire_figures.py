"""Figures de l'article du module de besoin, à partir des sorties commitées (aucun calcul de modèle).

Run (racine du dépôt) : uv run --with matplotlib python v2/papers/besoin/figures/faire_figures.py
Sources : v2/sensibilite/besoin/out/resultats.json et ratio_dep.csv (axe 5) ; v2/besoin/validation/out/pb6.json (P-B6).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
NOMS = {"sages-femmes": "Sages-femmes", "dentistes": "Dentistes", "pharmaciens": "Pharmaciens",
        "kines": "Kinés", "infirmiers": "Infirmiers"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

# 1. C national en 2050 par estimateur
r = json.loads((ROOT / "v2/sensibilite/besoin/out/resultats.json").read_text())
est = ["M0", "M1", "M2a", "M3"]
fig, ax = plt.subplots(figsize=(6.4, 2.8))
x = np.arange(len(NOMS))
for k, e in enumerate(est):
    v = [r[p]["annees"]["2050"]["C_FR_par_estimateur"].get(e, np.nan) for p in NOMS]
    ax.bar(x + (k - 1.5) * 0.19, v, 0.19, label=e, color=["#bdbdbd", "#3b6ea5", "#7fa7cf", "#c9d9ea"][k])
ax.axhline(1, color="black", lw=0.6)
ax.set_xticks(x, NOMS.values())
ax.set_ylabel("C en 2050 (2026 = 1)")
ax.legend(ncol=4, frameon=False, loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "c2050_estimateurs.pdf")

# 2. Ratio R par département (quotas × 1,2, 2050)
d = pd.read_csv(ROOT / "v2/sensibilite/besoin/out/ratio_dep.csv")
d = d[d.politique == "quotas x1,2"]
fig, ax = plt.subplots(figsize=(6.4, 2.6))
data = [np.log10(d[d.profession == p].R.replace(0, np.nan).dropna()) for p in NOMS]
ax.boxplot(data, tick_labels=list(NOMS.values()), showfliers=False)
ax.axhline(0, color="black", lw=0.6, ls="--")
ax.set_ylabel("log10 R (politique / choix\ndu modèle), par département")
fig.tight_layout()
fig.savefig(OUT / "ratio_dep.pdf")

# 3. Montée en charge de la vaccination en officine
s = json.loads((ROOT / "v2/besoin/validation/out/pb6.json").read_text())["s_t"]
pts = [(int(c["campagne"][:4]), c["s"]) for c in s["serie"] if c["s"] == c["s"]]
a = s["ajustement"]
t = np.linspace(2019, 2032, 200)
fig, ax = plt.subplots(figsize=(4.6, 2.6))
ax.plot(t, a["s_inf"] * (1 - np.exp(-(t - 2019) / a["tau"])), color="#3b6ea5", label="ajustement (t₀ = 2019)")
ax.scatter(*zip(*pts), color="black", s=14, zorder=3, label="IQVIA ÷ Open Medic")
ax.axhline(a["s_inf"], color="#3b6ea5", lw=0.6, ls=":")
ax.set_ylim(0, 0.85)
ax.set_xlabel("année de début de campagne")
ax.set_ylabel("part officinale s(t)")
ax.legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig(OUT / "s_t_vaccination.pdf")
print("ok")
