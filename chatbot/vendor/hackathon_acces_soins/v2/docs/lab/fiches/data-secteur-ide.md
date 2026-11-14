---
parametre: N_prive_observe
profession: IDE
module: etat (secteur)
valeur: "277788 – 277788 (centrale 277788) en 2023"
unite: personnes
incertitude: "min / max = salariés des secteurs mixtes comptés tous publics / tous privés ; largeur 0 (0.0 % de l'effectif)"
source: "DREES/Insee BTS infirmières salariées 2013–2023 + DREES infirmières libérales SNDS 2012–2023"
millesime: "publication DREES 2026-07-02 ; FINESS 2026-05-04"
statut: mesuré
---

# Effectif « libéral » (= privé) observé — infirmiers

Série France entière. Par département : `v2/data/processed/secteur_split.parquet`
(`profession == 'infirmiers'`, `mode3 == 'tous'`). Par âge × sexe × secteur : `secteur_stock.parquet`.

| Année | Effectif total | Min | Centrale | Max |
|---|---|---|---|---|
| 2013 | 544 635 | 233 517 | 233 517 | 233 517 |
| 2014 | 554 912 | 239 433 | 239 433 | 239 433 |
| 2015 | 563 679 | 246 140 | 246 140 | 246 140 |
| 2016 | 575 194 | 248 670 | 248 670 | 248 670 |
| 2017 | 580 484 | 255 276 | 255 276 | 255 276 |
| 2018 | 584 909 | 258 958 | 258 958 | 258 958 |
| 2019 | 590 475 | 264 534 | 264 534 | 264 534 |
| 2020 | 599 419 | 269 632 | 269 632 | 269 632 |
| 2021 | 598 912 | 270 961 | 270 961 | 270 961 |
| 2022 | 599 866 | 274 037 | 274 037 | 274 037 |
| 2023 | 607 644 | 277 788 | 277 788 | 277 788 |

- Règle de classement et parts centrales : [rapport secteur](../reports/2026-11-14-axe4-secteur-public-prive.md),
  script `v2/data/build_secteur.py`.
- Contrôle : Σ des cellules détaillées = total France du fichier (écart ≤ 0,22 %).
