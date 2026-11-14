---
parametre: N_prive_observe
profession: MK
module: etat (secteur)
valeur: "98828 – 103986 (centrale 101951) en 2026"
unite: personnes
incertitude: "min / max = salariés des secteurs mixtes comptés tous publics / tous privés ; largeur 5158 (4.6 % de l'effectif)"
source: "DREES, démographie des professionnels de santé depuis 2012 (RPPS, ADELI 2012–2016) ; FINESS au 2026-05-04 pour les parts centrales"
millesime: "publication DREES 2026-07-02 ; FINESS 2026-05-04"
statut: mesuré
---

# Effectif « libéral » (= privé) observé — kines

Série France entière. Par département : `v2/data/processed/secteur_split.parquet`
(`profession == 'kines'`, `mode3 == 'tous'`). Par âge × sexe × secteur : `secteur_stock.parquet`.

| Année | Effectif total | Min | Centrale | Max |
|---|---|---|---|---|
| 2012 | 68 200 | 59 040 | 60 739 | 61 440 |
| 2013 | 70 289 | 61 004 | 62 712 | 63 426 |
| 2014 | 72 762 | 63 325 | 65 065 | 65 816 |
| 2015 | 75 151 | 65 711 | 67 507 | 68 297 |
| 2016 | 77 429 | 67 987 | 69 760 | 70 552 |
| 2017 | 84 599 | 73 870 | 76 170 | 77 646 |
| 2018 | 89 122 | 78 199 | 80 680 | 82 264 |
| 2019 | 89 126 | 78 559 | 81 082 | 82 680 |
| 2020 | 91 308 | 80 677 | 83 238 | 84 851 |
| 2021 | 94 779 | 83 792 | 86 445 | 88 125 |
| 2022 | 97 093 | 85 919 | 88 599 | 90 290 |
| 2023 | 100 383 | 89 068 | 91 817 | 93 550 |
| 2024 | 104 043 | 92 374 | 95 248 | 97 089 |
| 2025 | 107 803 | 95 719 | 98 708 | 100 640 |
| 2026 | 111 141 | 98 828 | 101 951 | 103 986 |

- Règle de classement et parts centrales : [rapport secteur](../reports/2026-11-14-axe4-secteur-public-prive.md),
  script `v2/data/build_secteur.py`.
- Contrôle : Σ des cellules détaillées = total France du fichier (écart ≤ 0,22 %).
