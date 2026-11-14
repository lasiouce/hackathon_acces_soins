---
parametre: N_prive_observe
profession: SF
module: etat (secteur)
valeur: "12059 – 13331 (centrale 12819) en 2026"
unite: personnes
incertitude: "min / max = salariés des secteurs mixtes comptés tous publics / tous privés ; largeur 1272 (4,8 % de l'effectif) ; « Prévention » classée publique (PMI) depuis le 2026-11-14"
source: "DREES, démographie des professionnels de santé depuis 2012 (RPPS) ; FINESS au 2026-05-04 pour les parts centrales"
millesime: "publication DREES 2026-07-02 ; FINESS 2026-05-04"
statut: mesuré
---

# Effectif « libéral » (= privé) observé — sages-femmes

Série France entière. Par département : `v2/data/processed/secteur_split.parquet`
(`profession == 'sages-femmes'`, `mode3 == 'tous'`). Par âge × sexe × secteur : `secteur_stock.parquet`.

| Année | Effectif total | Min | Centrale | Max |
|---|---|---|---|---|
| 2012 | 19 552 | 6 839 | 7 249 | 7 472 |
| 2013 | 20 322 | 7 675 | 7 914 | 8 064 |
| 2014 | 20 960 | 8 127 | 8 388 | 8 548 |
| 2015 | 21 604 | 8 704 | 8 945 | 9 097 |
| 2016 | 22 299 | 9 338 | 9 577 | 9 728 |
| 2017 | 22 724 | 9 760 | 9 994 | 10 140 |
| 2018 | 22 824 | 10 024 | 10 273 | 10 425 |
| 2019 | 22 956 | 10 255 | 10 522 | 10 685 |
| 2020 | 23 175 | 10 524 | 10 843 | 11 031 |
| 2021 | 23 541 | 10 707 | 11 152 | 11 452 |
| 2022 | 23 764 | 10 962 | 11 438 | 11 767 |
| 2023 | 24 354 | 11 238 | 11 768 | 12 122 |
| 2024 | 25 404 | 11 510 | 12 142 | 12 572 |
| 2025 | 25 760 | 11 706 | 12 407 | 12 885 |
| 2026 | 26 428 | 12 059 | 12 819 | 13 331 |

- Règle de classement et parts centrales : [rapport secteur](../reports/2026-11-14-axe4-secteur-public-prive.md),
  script `v2/data/build_secteur.py`.
- Contrôle : Σ des cellules détaillées = total France du fichier (écart ≤ 0,22 %).

- **2026-11-14 :** « Prévention » (PMI) classée publique, d'après la DREES (1 423 SF en PMI au 31/12/2024). Tableau ci-dessus à jour.
