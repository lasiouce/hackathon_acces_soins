---
parametre: N_prive_observe
profession: CD
module: etat (secteur)
valeur: "40784 – 47894 (centrale 47349) en 2026"
unite: personnes
incertitude: "min / max = salariés des secteurs mixtes comptés tous publics / tous privés ; largeur 7110 (14.6 % de l'effectif)"
source: "DREES, démographie des professionnels de santé depuis 2012 (RPPS) ; FINESS au 2026-05-04 pour les parts centrales"
millesime: "publication DREES 2026-07-02 ; FINESS 2026-05-04"
statut: mesuré
---

# Effectif « libéral » (= privé) observé — dentistes

Série France entière. Par département : `v2/data/processed/secteur_split.parquet`
(`profession == 'dentistes'`, `mode3 == 'tous'`). Par âge × sexe × secteur : `secteur_stock.parquet`.

| Année | Effectif total | Min | Centrale | Max |
|---|---|---|---|---|
| 2012 | 40 488 | 37 212 | 39 810 | 40 193 |
| 2013 | 40 745 | 37 358 | 40 066 | 40 425 |
| 2014 | 41 221 | 37 621 | 40 489 | 40 848 |
| 2015 | 41 290 | 37 331 | 40 360 | 40 743 |
| 2016 | 41 584 | 37 497 | 40 657 | 41 057 |
| 2017 | 41 980 | 37 655 | 41 036 | 41 432 |
| 2018 | 42 051 | 37 521 | 41 060 | 41 468 |
| 2019 | 42 143 | 37 346 | 41 142 | 41 554 |
| 2020 | 42 843 | 37 607 | 41 822 | 42 242 |
| 2021 | 43 134 | 37 478 | 42 086 | 42 529 |
| 2022 | 44 154 | 37 850 | 43 083 | 43 533 |
| 2023 | 45 249 | 38 267 | 44 053 | 44 575 |
| 2024 | 45 779 | 38 267 | 44 542 | 45 074 |
| 2025 | 47 636 | 39 778 | 46 323 | 46 858 |
| 2026 | 48 690 | 40 784 | 47 349 | 47 894 |

- Règle de classement et parts centrales : [rapport secteur](../reports/2026-11-14-axe4-secteur-public-prive.md),
  script `v2/data/build_secteur.py`.
- Contrôle : Σ des cellules détaillées = total France du fichier (écart ≤ 0,22 %).
