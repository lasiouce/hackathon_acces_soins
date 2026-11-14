---
parametre: N_prive_observe
profession: PH
module: etat (secteur)
valeur: "60005 – 67219 (centrale 63612) en 2026"
unite: personnes
incertitude: "min / max = salariés des secteurs mixtes comptés tous publics / tous privés ; largeur 7214 (9.6 % de l'effectif)"
source: "DREES, démographie des professionnels de santé depuis 2012 (RPPS) ; FINESS au 2026-05-04 pour les parts centrales"
millesime: "publication DREES 2026-07-02 ; FINESS 2026-05-04"
statut: mesuré
---

# Effectif « libéral » (= privé) observé — pharmaciens

Série France entière. Par département : `v2/data/processed/secteur_split.parquet`
(`profession == 'pharmaciens'`, `mode3 == 'tous'`). Par âge × sexe × secteur : `secteur_stock.parquet`.

| Année | Effectif total | Min | Centrale | Max |
|---|---|---|---|---|
| 2012 | 72 658 | 61 376 | 63 936 | 66 497 |
| 2013 | 73 599 | 61 501 | 64 372 | 67 242 |
| 2014 | 73 799 | 61 626 | 64 432 | 67 237 |
| 2015 | 74 334 | 62 006 | 64 806 | 67 605 |
| 2016 | 74 484 | 61 755 | 64 704 | 67 654 |
| 2017 | 74 232 | 61 830 | 64 554 | 67 277 |
| 2018 | 73 756 | 61 748 | 64 234 | 66 721 |
| 2019 | 73 628 | 61 522 | 64 014 | 66 507 |
| 2020 | 73 788 | 61 314 | 63 951 | 66 588 |
| 2021 | 73 427 | 60 919 | 63 494 | 66 070 |
| 2022 | 73 574 | 60 376 | 63 176 | 65 976 |
| 2023 | 73 381 | 59 975 | 62 848 | 65 721 |
| 2024 | 74 227 | 60 054 | 63 228 | 66 402 |
| 2025 | 74 554 | 59 736 | 63 169 | 66 602 |
| 2026 | 75 335 | 60 005 | 63 612 | 67 219 |

- Règle de classement et parts centrales : [rapport secteur](../reports/2026-11-14-axe4-secteur-public-prive.md),
  script `v2/data/build_secteur.py`.
- Contrôle : Σ des cellules détaillées = total France du fichier (écart ≤ 0,22 %).
