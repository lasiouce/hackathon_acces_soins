---
type: fiche
axe: 1
id: param-age-entree-exercice
parametre: "A0_p — âge moyen d'entrée en exercice (diplômés en France et à l'étranger)"
profession: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
module: installation
valeur: "diplômés en France : SF 24 ans · CD 26 · PH 27 (cycle court), 28 (DES biologie), 29 (DES pharmacie) ; diplômés à l'étranger : SF 28 · CD 28"
unite: "années (âge moyen au diplôme / à la 1re activité)"
incertitude: "±1 an ; millésime RPPS 2020 ; MK et IDE : pas d'âge publié, mais 99 % entrent l'année du diplôme (ER 1062, 1075) ; repère régional ARS Centre-Val de Loire 2023 : 1re activité CD médiane 29 ans, MK médiane 26 ans (petits effectifs)"
source: "DREES, Les Dossiers n° 76 (mars 2021), tableaux 12 et 13 — https://drees.solidarites-sante.gouv.fr/sites/default/files/2021-03/DD76.pdf ; DREES ER n° 1062 (IDE, 2018) et n° 1075 (MK, 2018), encadré 2"
millesime: "RPPS 2020 ; 2016"
statut: sourcé
date: 2026-11-14
---

# A0_p — âge d'entrée en exercice

**Mécanisme.** Les entrants arrivent dans l'état N[âge] à l'âge A0. Avec la
retraite, A0 fixe la durée de carrière (≈ 40 ans), donc le nombre d'années
pendant lesquelles un diplômé compte dans le stock.

**Valeur** (*citée*, DD76).
| Profession | Diplômés en France | Diplômés à l'étranger (flux annuel) | Autres paramètres d'entrée |
|---|---|---|---|
| Sages-femmes | 24 ans (F 24, H 26) | 28 ans (70 par an) | 78 % des entrantes en formation retrouvées en activité ; 34 % installées en libéral |
| Dentistes | 26 ans | 28 ans (665 par an) | délai nul pour 73 % ; 82 % en libéral |
| Pharmaciens | 27 (cycle court) · 28 (DES biologie) · 29 (DES pharmacie) | — | — |
| Kinés | n.d. | 1 175 par an (2016) | 1 % de fuite ; 99 % installés l'année du diplôme (ER 1075) |
| Infirmiers | n.d. | — | 2 % de fuite ; 99 % entrent l'année du diplôme (ER 1062) |

**Mesure.** Âge à la 1re inscription RPPS, sur le panel individuel
(annuaire santé, millésimes empilés). On peut aussi le dériver de nos stocks
par âge (`data/processed/stock.parquet`) : c'est la classe d'âge où le
solde des entrées culmine. Coût estimé : ~30 min.
