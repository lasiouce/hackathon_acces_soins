---
type: fiche
axe: 1
id: param-cd-stock-specialistes
parametre: "Part des spécialistes qualifiés dans le stock de chirurgiens-dentistes (ODF, CO, MBD)"
profession: dentistes
module: filières
valeur: "2022 : ODF 2 465 (5,3 %) · CO 222 (0,5 %) · MBD 100 (0,2 %) · omnipraticiens 43 242 (94 %)"
unite: "praticiens en exercice ; part du total"
incertitude: "±2 % selon la source (RPPS au 01/10/2023, hexagone : ODF 2 398, CO 221, MBD 98) ; stock ODF stable (2 424 à 2 465 sur 2019-2022) ; flux de nouveaux ODF qualifiés non publié (plafond ≈ 50-52 postes par an)"
source: "Ordre national des chirurgiens-dentistes, rapports d'activité 2019 (p. 18), 2020 (p. 29), 2021 (p. 17), 2022 (p. 29) — https://www.ordre-chirurgiens-dentistes.fr/download/313005 (2022) ; ameli : ODF libéraux (data/processed/stock_ameli.parquet)"
millesime: "2019-2022 (Ordre) ; 01/10/2023 (RPPS) ; ameli 2010-2025"
statut: sourcé
date: 2026-11-14
---

# Stock de dentistes spécialistes

**Mécanisme.**
- Les spécialistes sont un sous-stock du stock dentaire.
- Les ODF sont presque tous libéraux. Ils sont exemptés de la régulation et
  ne sont pas interchangeables avec les omnipraticiens.
- Le stock ODF est stable : les entrées (≈ 50 DES par an, plus les
  qualifications par commission et les diplômes de l'UE) compensent à peu
  près les sorties.

**Valeur** (*citée*, Ordre).
| Année | ODF | CO | MBD | Omnipraticiens |
|---|---|---|---|---|
| 2019 | 2 441 | 181 | 80 | 40 888 |
| 2020 | 2 424 | 201 | 94 | 40 440 |
| 2021 | 2 462 | 212 | 102 | 42 584 |
| 2022 | 2 465 | 222 | 100 | 43 242 |

- ODF libéraux d'après ameli (*mesuré*, fichier local) : 2 005 en 2010,
  2 128 en 2018, 2 084 en 2025.
- ⚑ Ces totaux additionnent les départements : un praticien installé dans
  deux départements peut être compté deux fois.
- Le classeur DREES RPPS du dépôt n'a pas de dimension spécialité.

**Mesure.** Rapport d'activité annuel de l'Ordre (les éditions 2023 et 2024
n'ont pas été trouvées), ou RPPS individuel (savoir-faire / qualification).
