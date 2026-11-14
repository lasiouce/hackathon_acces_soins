---
parametre: N_prive_observe
profession: SF
module: etat (secteur)
valeur: "12059 – 14660 (centrale 12912) en 2026"
unite: personnes
incertitude: "min / max = salariés des secteurs mixtes comptés tous publics / tous privés ; largeur 2601 (9.8 % de l'effectif)"
source: "DREES, démographie des professionnels de santé depuis 2012 (RPPS) ; FINESS au 2026-05-04 pour les parts centrales"
millesime: "publication DREES 2026-07-02 ; FINESS 2026-05-04"
statut: mesuré
---

# Effectif « libéral » (= privé) observé — sages-femmes

Série France entière. Par département : `v2/data/processed/secteur_split.parquet`
(`profession == 'sages-femmes'`, `mode3 == 'tous'`). Par âge × sexe × secteur : `secteur_stock.parquet`.

| Année | Effectif total | Min | Centrale | Max |
|---|---|---|---|---|
| 2012 | 19 552 | 6 839 | 7 309 | 8 337 |
| 2013 | 20 322 | 7 675 | 7 980 | 9 015 |
| 2014 | 20 960 | 8 127 | 8 459 | 9 568 |
| 2015 | 21 604 | 8 704 | 9 020 | 10 184 |
| 2016 | 22 299 | 9 338 | 9 656 | 10 864 |
| 2017 | 22 724 | 9 760 | 10 075 | 11 296 |
| 2018 | 22 824 | 10 024 | 10 356 | 11 614 |
| 2019 | 22 956 | 10 255 | 10 607 | 11 898 |
| 2020 | 23 175 | 10 524 | 10 929 | 12 254 |
| 2021 | 23 541 | 10 707 | 11 239 | 12 692 |
| 2022 | 23 764 | 10 962 | 11 527 | 13 047 |
| 2023 | 24 354 | 11 238 | 11 857 | 13 400 |
| 2024 | 25 404 | 11 510 | 12 233 | 13 878 |
| 2025 | 25 760 | 11 706 | 12 500 | 14 214 |
| 2026 | 26 428 | 12 059 | 12 912 | 14 660 |

- Règle de classement et parts centrales : [rapport secteur](../reports/2026-11-14-axe4-secteur-public-prive.md),
  script `v2/data/build_secteur.py`.
- Contrôle : Σ des cellules détaillées = total France du fichier (écart ≤ 0,22 %).
