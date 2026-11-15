# Manifeste — module de besoin, axe 4 (données)

Généré par `uv run python v2/besoin/donnees/manifest.py`. Une ligne par table. Les tables ODbL ne sont pas
commitées (décision de licence ouverte, registre § Open) : les reconstruire avec leur commande.

| Table | Chemin | Lignes | SHA-256 (16) | Licence | Commitée | Source | Millésime | DOM | Contrôles (ok / total) | Commande |
|---|---|---:|---|---|---|---|---|---|---|---|
| `apl_commune.parquet` | `v2/data/processed/besoin/apl_commune.parquet` | 419232 | `6473426afae01b14` | Licence Ouverte 2.0 (Etalab) | oui | DREES, APL (jeu 530), fichiers par profession, modifié le 2026-07-22 | APL 2022, 2023, 2024 (pop. N−2) | inclus : 112 communes 971–974 ; Mayotte absente du champ DREES | 12 / 12 | `uv run python v2/besoin/donnees/apl.py` |
| `apl_parametres.parquet` | `v2/data/processed/besoin/apl_parametres.parquet` | 285 | `7ddce0e738652e5a` | Licence Ouverte 2.0 (Etalab) | oui | DREES, APL (jeu 530), fichiers par profession, modifié le 2026-07-22, onglet « Paramètres » | poids d'âge DCIR 2020–2022 (onglets 2022–2024) | sans objet | — | `uv run python v2/besoin/donnees/apl.py` |
| `damir_profils.parquet` | `v2/data/processed/besoin/damir_profils.parquet` | 256877 | `e521f90e746f9d53` | Licence Ouverte 2.0 (Etalab) | oui | Assurance maladie, Open DAMIR base complète, fichiers mensuels A{AAAAMM}.csv.gz (lus en flux) | flux 202501, 202502, 202503, 202504, 202505, 202506, 202507, 202508, 202509 | DOM regroupés en une zone (code 5), non séparables ; PACA et Corse fusionnées (93) ; 99 = inconnu | 1 / 1 | `uv run python v2/besoin/donnees/damir.py --fenetre && uv run python v2/besoin/donnees/damir.py --controle` |
| `damir_vaccination.parquet` | `v2/data/processed/besoin/damir_vaccination.parquet` | 40998 | `e49225e9b26da42a` | Licence Ouverte 2.0 (Etalab) | oui | Assurance maladie, Open DAMIR base complète, fichiers mensuels A{AAAAMM}.csv.gz (lus en flux) | flux 202501, 202502, 202503, 202504, 202505, 202506, 202507, 202508, 202509 | DOM regroupés en une zone (code 5), non séparables ; PACA et Corse fusionnées (93) ; 99 = inconnu | — | `uv run python v2/besoin/donnees/damir.py --fenetre && uv run python v2/besoin/donnees/damir.py --controle` |
| `distancier_vol_oiseau.parquet` | `v2/data/processed/besoin/distancier_vol_oiseau.parquet` | 9810510 | `9e421a3b713aff74` | Licence Ouverte 2.0 (Etalab) | oui | geo.api.gouv.fr, centres des communes et arrondissements (fichiers du 2026-11-14) | géographie 2026 | inclus (971–976), sans paire inter-territoires ; Mayotte hors champ APL | 2 / 2 | `uv run python v2/besoin/donnees/distancier.py` |
| `iqvia_campagne.parquet` | `v2/data/processed/besoin/iqvia_campagne.parquet` | 30 | `ba79d4b5e8175bb8` | Licence Ouverte 2.0 (Etalab) | oui | IQVIA France (Pharmastat), Vaccination Grippe 2021-2022 à 2026-2027, data.gouv.fr | saisons 2021-22 à 2026-27 ; série quotidienne 2020-21 reprise du fichier 2021-22 ; 2026-27 (en cours, au 2026-11-11) | national (France entière extrapolée ; périmètre DOM non documenté) | 12 / 12 | `uv run python v2/besoin/donnees/iqvia.py` |
| `iqvia_quotidien.parquet` | `v2/data/processed/besoin/iqvia_quotidien.parquet` | 3372 | `ea1934e032ca8074` | Licence Ouverte 2.0 (Etalab) | oui | IQVIA France (Pharmastat), Vaccination Grippe 2021-2022 à 2026-2027, data.gouv.fr | saisons 2021-22 à 2026-27 ; série quotidienne 2020-21 reprise du fichier 2021-22 ; 2026-27 (en cours, au 2026-11-11) | national (France entière extrapolée ; périmètre DOM non documenté) | — | `uv run python v2/besoin/donnees/iqvia.py` |
| `iqvia_regional.parquet` | `v2/data/processed/besoin/iqvia_regional.parquet` | 292 | `eeda13f9a209ddc9` | Licence Ouverte 2.0 (Etalab) | oui | IQVIA France (Pharmastat), Vaccination Grippe 2021-2022 à 2026-2027, data.gouv.fr | saisons 2021-22 à 2026-27 ; série quotidienne 2020-21 reprise du fichier 2021-22 ; 2026-27 (en cours, au 2026-11-11) | régions présentes : 11, 24, 27, 28, 32, 44, 52, 53, 75, 76, 84, 93, 94 (aucun DOM) | — | `uv run python v2/besoin/donnees/iqvia.py` |
| `medic_vaccins.parquet` | `v2/data/processed/besoin/medic_vaccins.parquet` | 11021 | `f6d9a9d5a8c2937e` | Licence Ouverte 2.0 (Etalab) | oui | Assurance maladie, Open Medic, bases complémentaires ATC4 | 2014–2025 (année civile de délivrance) | DOM regroupés (ben_reg 5), non séparables ; 0 et 99 = inconnu | 24 / 24 | `uv run python v2/besoin/donnees/medic.py` |
| `ameli_demographie.parquet` | `v2/data/odbl/besoin/ameli_demographie.parquet` | 3694080 | `f1ace4ca0b9d8df9` | Open Database License 1.0 | **non** | CNAM, data.ameli.fr, jeu « demographie-effectifs-et-les-densites » (export parquet de l'API Opendatasoft, lu le 2026-11-15) | 2010–2025 (au 31/12) | inclus : départements 971, 972, 973, 974, 976 (Mayotte comprise) ; région 99 = France entière | 80 / 80 | `uv run python v2/besoin/donnees/ameli.py` |
| `ameli_honoraires.parquet` | `v2/data/odbl/besoin/ameli_honoraires.parquet` | 1351680 | `686446037253db38` | Open Database License 1.0 | **non** | CNAM, data.ameli.fr, jeu « honoraires-detailles » (export parquet de l'API Opendatasoft, lu le 2026-11-15) | 2010–2025 | inclus : départements 971, 972, 973, 974, 976 (Mayotte comprise) ; région 99 = France entière | 74 / 80 | `uv run python v2/besoin/donnees/ameli.py` |
| `ameli_pathologies_depenses.parquet` | `v2/data/odbl/besoin/ameli_pathologies_depenses.parquet` | 24800 | `40a52bad4a18f98d` | Open Database License 1.0 | **non** | CNAM, data.ameli.fr, jeu « depenses » (export parquet de l'API Opendatasoft, lu le 2026-11-15) | 2015–2024 | national seulement (France entière) | 795 / 795 | `uv run python v2/besoin/donnees/ameli.py` |
| `ameli_pathologies_effectifs.parquet` | `v2/data/odbl/besoin/ameli_pathologies_effectifs.parquet` | 5796000 | `37af165b34b33c5c` | Open Database License 1.0 | **non** | CNAM, data.ameli.fr, jeu « effectifs » (export parquet de l'API Opendatasoft, lu le 2026-11-15) | 2015–2024 | inclus : départements 971, 972, 973, 974, 976 (Mayotte comprise) ; région 99 = France entière | 197 / 220 | `uv run python v2/besoin/donnees/ameli.py` |
| `ameli_patientele.parquet` | `v2/data/odbl/besoin/ameli_patientele.parquet` | 45120 | `84ea6baf69726ef7` | Open Database License 1.0 | **non** | CNAM, data.ameli.fr, jeu « patientele » (export parquet de l'API Opendatasoft, lu le 2026-11-15) | 2016–2025 | inclus : départements 971, 972, 973, 974, 976 (Mayotte comprise) ; région 99 = France entière | 50 / 50 | `uv run python v2/besoin/donnees/ameli.py` |
| `index.parquet` | `v2/data/processed/besoin/damir/index.parquet` | 9 | `100cd0320b255ca4` | Licence Ouverte 2.0 (Etalab) | oui | Assurance maladie, Open DAMIR base complète, fichiers mensuels A{AAAAMM}.csv.gz (lus en flux) | mois de flux lus : 202501, 202502, 202503, 202504, 202505, 202506, 202507, 202508, 202509 | DOM regroupés en une zone (code 5), non séparables ; PACA et Corse fusionnées (93) | 0 / 0 (+54 info) | `uv run python v2/besoin/donnees/damir.py --fenetre` |

## Open DAMIR : mois lus en flux

Licence Ouverte 2.0, agrégats commités dans `v2/data/processed/besoin/damir/` ; aucun CSV brut écrit.

| mois | octets_gz | lignes | lignes_agg | secondes | mo_par_s | gunzip | lu_le |
|---|---|---|---|---|---|---|---|
| 202501 | 973594858 | 36640259 | 919369 | 213.0 | 4.57 | 2 (octets écrits par curl -w dans le flux ; corrigé ensuite ; taille = Content-Length) | 2026-11-15T03:17:38 |
| 202502 | 923432287 | 34710236 | 876053 | 273.8 | 3.37 | 0  | 2026-11-15T03:23:41 |
| 202503 | 952744750 | 35881985 | 903183 | 260.7 | 3.66 | 0  | 2026-11-15T03:28:01 |
| 202504 | 871686208 | 32781300 | 850720 | 219.3 | 3.97 | 0  | 2026-11-15T03:31:41 |
| 202505 | 916087025 | 34167564 | 856395 | 245.8 | 3.73 | 0  | 2026-11-15T03:35:47 |
| 202506 | 924277069 | 34412402 | 870823 | 239.8 | 3.85 | 0  | 2026-11-15T03:39:47 |
| 202507 | 950402323 | 35467887 | 902527 | 243.8 | 3.9 | 0  | 2026-11-15T03:43:51 |
| 202508 | 815025319 | 30731153 | 823777 | 236.7 | 3.44 | 0  | 2026-11-15T03:47:48 |
| 202509 | 918531956 | 34321259 | 910763 | 228.6 | 4.02 | 0  | 2026-11-15T03:51:36 |

## Contrôles de totaux

1247 contrôles réussis sur 1276 (seuil 0,5 % sauf mention) ; détail dans `controles.csv`. Échecs :

- `ameli_honoraires.parquet` — honoraires (ensemble) SF 2010 : écart 1.90%
- `ameli_honoraires.parquet` — honoraires (ensemble) SF 2011 : écart 2.26%
- `ameli_honoraires.parquet` — honoraires (ensemble) SF 2012 : écart 2.07%
- `ameli_honoraires.parquet` — honoraires (ensemble) SF 2013 : écart 1.51%
- `ameli_honoraires.parquet` — honoraires (ensemble) SF 2014 : écart 0.76%
- `ameli_honoraires.parquet` — honoraires (ensemble) SF 2015 : écart 1.76%
- `ameli_pathologies_effectifs.parquet` — population cartographie 2015 : écart 1.40%
- `ameli_pathologies_effectifs.parquet` — population cartographie 2016 : écart 0.78%
- `ameli_pathologies_effectifs.parquet` — population cartographie 2017 : écart 0.72%
- `ameli_pathologies_effectifs.parquet` — population cartographie 2018 : écart 0.62%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2015 : écart 2.88%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2016 : écart 1.75%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2017 : écart 1.59%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2018 : écart 1.29%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2019 : écart 0.66%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2020 : écart 0.60%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2021 : écart 0.54%
- `ameli_pathologies_effectifs.parquet` — patients ALD_CAT_CAT 2022 : écart 0.52%
- `ameli_pathologies_effectifs.parquet` — patients CAN_CAT_CAT 2015 : écart 1.44%
- `ameli_pathologies_effectifs.parquet` — patients CAN_CAT_CAT 2016 : écart 0.52%
- `ameli_pathologies_effectifs.parquet` — patients DIA_CAT_CAT 2015 : écart 1.36%
- `ameli_pathologies_effectifs.parquet` — patients DIA_CAT_CAT 2016 : écart 0.50%
- `ameli_pathologies_effectifs.parquet` — patients IFL_CAT_CAT 2015 : écart 1.06%
- `ameli_pathologies_effectifs.parquet` — patients IRT_CAT_CAT 2015 : écart 1.20%
- `ameli_pathologies_effectifs.parquet` — patients IRV_CAT_CAT 2015 : écart 1.08%
- `ameli_pathologies_effectifs.parquet` — patients MCV_CAT_CAT 2015 : écart 1.38%
- `ameli_pathologies_effectifs.parquet` — patients NEU_CAT_CAT 2015 : écart 1.36%
- `ameli_pathologies_effectifs.parquet` — patients PSY_CAT_CAT 2015 : écart 0.96%
- `ameli_pathologies_effectifs.parquet` — patients RAR_CAT_CAT 2015 : écart 1.04%

Écart relatif maximal : 2.884% ; médian : 0.0000%.

Lignes d'information sans verdict : 54 (dans `controles.csv`, colonne `ok` vide).
