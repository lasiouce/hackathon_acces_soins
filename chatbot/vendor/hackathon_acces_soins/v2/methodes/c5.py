"""C5 : la région de formation (université -> ARS) prédit-elle la région d'installation ? (exploratoire)

Étudiants : DREES 990_drees_mmop2_f.xlsx, feuille Feuil1 (colonne ARS = correspondance université -> ARS,
reprise C5), DE années 2 à 6, moyenne 2020–2024. Entrées : flux net I des tranches d'entrée calibré sur le
périmètre privé (fenêtre 2019–2026), sommé par région. On compare deux prédicteurs de la part régionale
des entrées : la part des étudiants et la part du stock actuel. Si la part étudiante n'ajoute rien à la
part du stock, répartir les entrées par région de formation n'améliorera pas la prévision.
Lancer : PYTHONPATH=v2 uv run python -m methodes.c5"""
import numpy as np
import pandas as pd

from methodes.calibrage import dep_to_region, fit
from methodes.perimetres import prive

ARS = {"Auvergne-Rhône-Alpes": "84", "Ile-de-France": "11", "Grand Est": "44", "Occitanie": "76",
       "Nouvelle-Aquitaine": "75", "Bretagne": "53", "Pays de la Loire": "52", "Provence-Alpes-Côte d'Azur": "93",
       "Haut de France": "32", "Bourgogne-Franche-Comté": "27", "Normandie": "28", "Centre-Val de Loire": "24",
       "Antilles Guyane": "AG", "Océan Indien": "OI"}
DIPLOME = {"dentistes": "DE DOCTEUR EN CHIRURGIE DENTAIRE", "pharmaciens": "DE DOCTEUR EN PHARMACIE"}

f = pd.read_excel("data/raw/990_drees_mmop2_f.xlsx", sheet_name="Feuil1", engine="calamine")
f = f.assign(k=pd.to_numeric(f["année_dans_le_diplôme"], errors="coerce"), n=pd.to_numeric(f.Inscriptions, errors="coerce"))
reg = dep_to_region().replace({"01": "AG", "02": "AG", "03": "AG", "04": "OI", "06": "OI", "94": "93"})
t = prive()
rows = []
for p, dip in DIPLOME.items():
    st = (f[(f.type_de_diplome == dip) & f.k.between(2, 6)].groupby(["ARS", "ANNEE"]).n.sum()
          .groupby("ARS").mean().rename(index=ARS))
    tp = t[t.profession == p]
    c = fit(tp, (2019, 2026), shrink=200)
    inflow = pd.Series(c["inflow"].sum(1), index=c["cells"].dep).groupby(lambda d: reg.get(d)).sum()
    stock = tp[tp.year == 2026].groupby("dep").n.sum().groupby(lambda d: reg.get(d)).sum()
    d = pd.DataFrame({"etudiants": st, "entrees": inflow, "stock": stock}).dropna()
    sh = d / d.sum()
    for x in ("etudiants", "stock"):
        r = np.corrcoef(sh[x], sh.entrees)[0, 1]
        mae = (sh[x] - sh.entrees).abs().mean() * 100
        rows.append({"profession": p, "predicteur": x, "r": round(r, 3), "erreur_abs_moy_pts_part": round(mae, 2),
                     "regions": len(d)})
    sh.assign(profession=p).to_csv(f"v2/methodes/out/c5_{p}.csv")
out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv("v2/methodes/out/c5.csv", index=False)
