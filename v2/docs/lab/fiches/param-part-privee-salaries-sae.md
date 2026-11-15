---
type: fiche
axe: 1
id: param-part-privee-salaries-sae
parametre: "s_p,hosp — part privée (privé lucratif + non lucratif) des salariés des établissements de santé, par profession"
profession: [sages-femmes, pharmaciens, kines, dentistes]
module: transitions
valeur: "2025 : SF 19,8 % · PH 29,4 % (hors biologie 32,6 %, biologistes 11,6 %) · MK 44,3 % · CD 2,2 %"
unite: "part des salariés au 31/12 (personnes, un contrat par établissement)"
incertitude: "±1 point en ETP (SF 18,4 %) ; stable sur 2023-2025 (SF 20,4 → 19,8 %) ; multi-employeurs comptés plusieurs fois ; champ : établissements de santé seulement (ni PMI, ni centres de santé, ni médico-social) ; bases statistiques avec imputation de la non-réponse"
source: "DREES, Statistique annuelle des établissements de santé (SAE), Bases statistiques 2023-2025, bordereaux Q23 (EFFPNM, ETPPNM ; N2800 sages-femmes, N2410 kinés) et Q20 (EFFSAL, ETPSAL ; M3050, M3012 pharmaciens, M3030 odontologie), statut juridique ID.STJR — https://data.drees.solidarites-sante.gouv.fr/explore/dataset/708_bases-statistiques-sae/"
millesime: "PMI 31/12/2024 ; SAE 2025 (personnel au 31/12/2025), mise à jour du 2026-11-04 ; 2023 et 2024"
statut: mesuré
relecture: "2026-11-15 : confirmé (codes)"
date: 2026-11-14
---

# s_hosp — part privée des salariés hospitaliers (SAE)

**Mécanisme.**
- Le « libéral » v2 est le secteur privé, lucratif ou non. Un salarié
  d'établissement de santé y entre s'il travaille en clinique ou en
  établissement privé non lucratif ; il en sort s'il est à l'hôpital public.
- s_hosp donne la répartition au sein des salariés hospitaliers, d'après une
  source indépendante du RPPS.

**Valeur** (*mesurée* par le script ci-dessous ; statut 1 = public,
2 = privé lucratif, 3 = privé non lucratif).
| Profession | Public | PNL | PL | Part privée (personnes) | Part privée (ETP) |
|---|---|---|---|---|---|
| Sages-femmes | 13 737 | 1 337 | 2 052 | 19,8 % | 18,4 % |
| Pharmaciens | 6 327 | 1 340 | 1 299 | 29,4 % | 27,9 % |
| – dont hors biologie | 5 126 | 1 200 | 1 281 | 32,6 % | 30,4 % |
| – dont biologistes | 1 201 | 140 | 18 | 11,6 % | 12,4 % |
| Kinés | 7 619 | 3 721 | 2 341 | 44,3 % | 44,4 % |
| Dentistes (odontologie) | 1 892 | 42 | 1 | 2,2 % | 1,4 % |

**Recoupement avec le RPPS du projet**, secteurs hospitaliers au 1/1/2026
(`secteur_stock.parquet`, *mesuré*) :
| Profession | RPPS | SAE 2025 | Lecture |
|---|---|---|---|
| Sages-femmes | 17,4 % | 19,8 % | cohérent |
| Kinés | 44,4 % | 44,3 % | concordent |
| Pharmaciens | 17,4 % | 29,4 % | **écart** |
| Dentistes | 3,4 % | 2,2 % | effectifs faibles |

- Pour les pharmaciens, la SAE rejoint l'Ordre (28,6 %, voir
  [[param-ph-part-privee-etablissements]]). Le RPPS les place nettement plus
  bas. La question reste ouverte au ledger.

**Ce que ça change (priorité 1 de l'axe 5).**
- L'hôpital n'est **pas** la source de l'incertitude sur les sages-femmes :
  RPPS et SAE y concordent à environ 2 points près.
- Il reste à trancher les secteurs « Prévention » et « Autre secteur » du
  RPPS (PMI, centres de santé), que la SAE ne couvre pas.

## Sages-femmes hors hôpital : la catégorie « Prévention » correspond à la PMI

**Ce que contiennent les 2 601 sages-femmes ambiguës.** Ce sont toutes des
« autre salarié » du RPPS 2026 (*mesuré*, `secteur_stock.parquet`). Le
reste se répartit en 12 059 privées sûres et 11 768 à l'hôpital public.
| Secteur DREES | Effectif | Poids dans l'écart min–max | Part privée centrale actuelle (axe 4) |
|---|---|---|---|
| Prévention | 1 329 | 51,1 % | 0,070 (FINESS) |
| Autre secteur | 796 | 30,6 % | 0,5 (supposée) |
| Centre de santé, maison de santé | 300 | 11,5 % | 0,798 |
| Établissement sanitaire et social | 176 | 6,8 % | 0,696 |

**Rapprochement avec la PMI.**
- *Cité* : sages-femmes des services départementaux de PMI = 1 423 personnes
  et 1 195,4 ETP au 31/12/2024 (1 392 en 2022, 1 395 en 2023). Source :
  DREES, *Le personnel des services départementaux de PMI – Séries longues
  2010-2024*, feuilles `EFF_SF` et `ETP_SF`, ligne « TOTAL estimé France
  entière ».
  https://data.drees.solidarites-sante.gouv.fr/explore/dataset/la-protection-maternelle-et-infantile-pmi-activite-et-personnels/
- *Mesuré* : le RPPS compte 1 383 sages-femmes en « Prévention »
  (1 329 ambiguës + 54 libérales ou mixtes). L'écart avec la PMI est de 3 %
  (*dérivé*).
- La PMI est un service départemental, donc un **employeur public**.

**Proposition à l'axe 4** (décision qui lui revient, ses fichiers).
- Classer « Prévention » en public pour les sages-femmes, borne min = borne
  max ≈ 0.
- L'écart min–max passe alors de 2 601 à **1 272** (−51 %, *dérivé*). La
  fourchette « libérale » 2026 serait 12 059 – 13 331.
- Le prochain point à documenter est « Autre secteur » (796 sages-femmes,
  63 % du résidu, part supposée à 0,5).

**Recoupement pour l'hôpital.** DREES, *Effectifs salariés hospitaliers –
séries longues* (SIASP + BTS, personnes au 31/12), 2024 : 19,3 % de
sages-femmes salariées dans le privé (*mesuré*). La SAE donne 20,1 % en 2024
et le RPPS 17,4 % en 2026 : les trois sources concordent.

**Reproduire.**
- Télécharger l'archive `SAE 2025 Bases statistiques - formats SAS-CSV.7z`
  (31 Mo) depuis la page du jeu 708.
- L'extraire avec `bsdtar -xf … --include "*Bases CSV/Q2*" --include "*Bases CSV/ID_*"`.
- Lancer `python3 -I part_privee_sae.py "<dossier Bases CSV>" 2025`.

```python
"""Part privée des salariés des établissements de santé, SAE bases statistiques (DREES).
Usage: python -I part_privee_sae.py <dossier 'Bases CSV'> <annee>
Q23 (PNM + sages-femmes): EFFPNM = effectif salarié au 31/12 (CDI+CDD+titulaires), ETPPNM = ETP moyens annuels.
Q20 (personnel médical):  EFFSAL = effectif salarié au 31/12 (temps plein + partiel), ETPSAL = ETP moyens annuels.
Statut: ID.STJR 1 public, 2 privé lucratif, 3 privé non lucratif."""
import sys, pathlib, pandas as pd
d, an = pathlib.Path(sys.argv[1]), sys.argv[2]
def rd(b):
    f = d / f"{b}_{an}r.csv"
    try: x = pd.read_csv(f, sep=";", dtype=str, low_memory=False, encoding="utf-8")
    except UnicodeDecodeError: x = pd.read_csv(f, sep=";", dtype=str, low_memory=False, encoding="latin-1")
    x.columns = [c.upper() for c in x.columns]
    for c in x.columns:
        if c.startswith(("EFF", "ETP")) or c == "STJR": x[c] = pd.to_numeric(x[c].str.replace(",", "."), errors="coerce")
    return x
idt = rd("ID")[["FI", "STJR"]].drop_duplicates("FI")
STAT = {1: "public", 3: "PNL", 2: "PL"}
CODES = {("Q23", "N2800"): "sages-femmes", ("Q23", "N2410"): "kines",
         ("Q20", "M3050"): "pharmaciens (hors bio)", ("Q20", "M3012"): "pharmaciens biologistes",
         ("Q20", "M3030"): "odontologie (dentistes)"}
VARS = {"Q23": ("EFFPNM", "ETPPNM"), "Q20": ("EFFSAL", "ETPSAL")}
out = []
for bor in ("Q23", "Q20"):
    q = rd(bor)
    assert not q.duplicated(["FI", "PERSO"]).any(), f"doublons FI×PERSO dans {bor}"
    q = q.merge(idt, on="FI", how="left")
    miss = q["STJR"].isna().sum()
    eff, etp = VARS[bor]
    for (b, code), lab in CODES.items():
        if b != bor: continue
        s = q[q.PERSO == code]
        for var in (eff, etp):
            g = s.groupby("STJR")[var].sum().rename(index=lambda k: STAT.get(int(k), k))
            r = {"annee": an, "profession": lab, "code": code, "bordereau": bor, "variable": var,
                 "public": g.get("public", 0), "PNL": g.get("PNL", 0), "PL": g.get("PL", 0),
                 "n_etab_>0": int((s[var] > 0).sum()), "lignes_sans_statut": int(miss)}
            r["total"] = r["public"] + r["PNL"] + r["PL"]
            r["part_privee"] = (r["PNL"] + r["PL"]) / r["total"] if r["total"] else float("nan")
            out.append(r)
df = pd.DataFrame(out)
pd.set_option("display.width", 250)
print("FI de", " ".join(sorted(CODES and {b for b,_ in CODES})), "absents de ID:", {b: int((~rd(b).FI.isin(idt.FI)).sum()) for b in ("Q20","Q23")})
print(df.round(3).to_string(index=False))
```

## Relecture en texte intégral (2026-11-15)

Verdict : **confirmé (codes)** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- Codes vérifiés dans la nomenclature et le guide SAE 2025 : N2800 sages-femmes, N2410 kinés, M3030 odontologie, M3012 biologistes, M3050 pharmaciens hors biologie ; STJR 1 / 2 / 3 = public / privé lucratif / privé non lucratif. Les noms de colonnes EFFPNM, ETPPNM, EFFSAL et ETPSAL n'apparaissent que dans les en-têtes des CSV. Parts non recalculées (*mesuré* par notre code).
