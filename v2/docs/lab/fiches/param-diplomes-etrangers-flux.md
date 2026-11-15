---
type: fiche
axe: 1
id: param-diplomes-etrangers-flux
parametre: "M_p — flux annuel d'entrées en exercice de professionnels diplômés hors de France (UE/EEE et hors UE)"
profession: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
module: installation
valeur: "valeurs par défaut proposées : CD 1 300 / an · MK 2 200 / an · IDE 400 / an · PH 240 / an · SF 80 / an"
unite: "personnes par an, toutes origines hors France (définitions variables, voir le tableau)"
incertitude: "CD 665 à 1 313 · MK 1 175 à 2 528 · IDE 400 (borne haute 1 100 supposée) · PH 160 à 250 · SF 70 à 170 ; les sources mesurent des choses différentes (primo-inscription à l'Ordre, entrée en activité RPPS, autorisation, décision de reconnaissance UE) et leurs ratios sont inconnus ; flux hors UE (procédure d'autorisation d'exercice des lauréats) non cherchés"
source: "DREES Les Dossiers n° 76 (2021), tableau 13 ; DREES ER n° 1026 (2017), p. 3 ; DREES ER n° 1075 (2018), p. 2 ; DREES ER n° 1319 (2024), p. 2 et 4 ; CNOMK, Démographie 2024, p. 66 et 75 ; Ordre des pharmaciens, synthèse 2024 et dépliant 2025 ; Commission européenne, base des professions réglementées (décisions de reconnaissance, pays d'accueil France) — https://ec.europa.eu/growth/tools-databases/regprof/ ; QE AN n° 15512 (2024) et n° 4281 (2025)"
millesime: "2013-2025 selon la profession"
statut: sourcé
relecture: "2026-11-15 : valeurs du code confirmées ; étiquettes corrigées"
date: 2026-11-14
---

# M_p — diplômés étrangers : flux annuel

**Mécanisme.**
- Une part des entrants n'est pas formée en France. Ce flux s'ajoute aux
  diplômés français et ne dépend pas des quotas de formation.
- Pour les dentistes et les kinés, il pèse autant que la filière
  française : 24,4 % des CD et 32,5 % des MK actifs n'ont pas de diplôme
  d'État français (stock, [[data-diplomes-hors-france]]).
- Leviers : reconnaissance des diplômes UE (directive 2005/36/CE), procédure
  d'autorisation d'exercice pour les diplômés hors UE, accords
  bilatéraux.

**Valeurs trouvées.** Statut : P = source primaire ouverte, S = source
secondaire.
| Prof. | Flux | Années | Définition | Source |
|---|---|---|---|---|
| CD | 308 / 391 / 501 / 500 | 2013-2016 | primo-inscrits à l'Ordre diplômés à l'étranger (Roumanie 46 % des inscrits 2015) | P : ER 1026, p. 3 |
| CD | 665 | moyenne 2016-2020 | entrées en activité (RPPS) | P : DD76, tab. 13 |
| CD | 892 / 1 323 / 1 309 | 2020-2022 | décisions positives de reconnaissance UE | P : base UE |
| CD | 1 313, dont 19 hors UE | 2022 | nouveaux inscrits à l'Ordre | S : QE 15512 et 4281 (chiffres de l'Ordre, sans réponse du ministère) |
| MK | 1 175 (environ 1 200 par an depuis 2008) | 2015 | primo-inscrits ARS diplômés à l'étranger (33 %) | P : ER 1075, p. 2 |
| MK | 2 320 / 1 662 / 488 | 2020-2022 | décisions positives UE (2022 paraît incomplet) | P : base UE |
| MK | 2 528 autorisations pour 3 321 demandes | 2023 | autorisations d'exercice et cartes professionnelles européennes | P : CNOMK 2024, p. 75 |
| MK | +2 212 par an, net | 2020 → 2024 | hausse du stock de diplômés hors France (23 728 → 32 574) | P : CNOMK 2024, p. 66 ; *dérivé* |
| IDE | 400 | 2021 | infirmières étrangères venant exercer chaque année (hypothèse de projection) | P : ER 1319, p. 2 et 4 |
| IDE | 1 559 / 895 / 1 097 / 1 093 | 2013, 2015, 2016, 2020 | décisions positives UE | P : base UE (2021-2022 quasi nuls, non déclarés) |
| PH | 160 | moyenne 2016-2020 | entrées en activité (RPPS) | P : DD76, tab. 13 |
| PH | ≈ 237 et ≈ 247 | 2024, 2025 | 8,1 % des primo-inscrits (2 927 et 3 044) | P : Ordre ; nombres *dérivés* |
| SF | 70 | moyenne 2016-2020 | entrées en activité (RPPS) | P : DD76, tab. 13 |
| SF | 152 à 179 | 2013, 2014, 2020-2022 | décisions positives UE | P : base UE |

**Valeurs par défaut proposées.**
- **CD : 1 300 par an**, *sourcé* (Ordre 2022, recoupé par 1 309
  décisions UE). Variante basse : 665 (DD76).
- **MK : 2 200 par an**, *dérivé* (autorisations 2023 et hausse nette du
  stock). Plage : 1 700 à 2 500.
- **IDE : 400 par an**, *sourcé* (hypothèse DREES), confiance faible.
  Plage : 400 à 1 100.
- **PH : 240 par an**, *dérivé* (2024-2025), environ 93 % UE/EEE/Suisse.
- **SF : 80 par an**, *dérivé*. Plage : 70 à 170, presque 100 % UE.

**⚑ Points de vigilance.**
- Une décision de reconnaissance ouvre un droit d'exercer ; ce n'est pas
  une entrée en activité. Elle sur-estime donc le flux.
- La base UE ne couvre que les diplômes UE/EEE/Suisse. Les années
  2009-2012, 2017-2019 et 2023-2024 n'y sont pas déclarées par la France.
- Le flux vers le libéral demande en plus une part libérale : 60 % pour les
  CD et 70 % pour les SF (DD76), 67 % pour les CD en 2016 (ER 1026).

**Comment compléter.**
- Arrêtés du CNG sur la procédure d'autorisation d'exercice (lauréats hors
  UE) pour CD, PH et SF : ~30 min.
- Série de l'Ordre des dentistes après 2022 : rapports d'activité.

## Relecture en texte intégral (2026-11-15)

Verdict : **valeurs du code confirmées ; étiquettes corrigées** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- **CD 1 300** : *dérivé*, pas *sourcé*. C'est l'arrondi de 1 313 (QE AN 15512, texte de la question, 2022 : 1 294 UE + 19 hors UE) et de 1 333 (rapport ONCD 2022, p. 27). Les deux portent sur les primo-inscrits à l'Ordre diplômés hors France, tous modes d'exercice. Les 1 309 reconnaissances UE (base RegProf) n'ont pas pu être vérifiées : base illisible.
- **MK 2 200** : arrondi de +2 212 par an net (dérivé : (32 574 − 23 728) / 4, CNOMK p. 66), sous les 2 528 autorisations de 2023 (p. 75). La borne basse 1 700 est *supposée*.
- **MK, ER 1075** : 1 240 primo-entrants en 2008, puis « stable autour de 1 200 » (p. 2). « Depuis 2008 » est une lecture.
- **IDE** : l'ER 1319 ne donne que 400 (p. 2, 4, 5). La borne 1 100 est une graduation d'axe : plage haute *supposée*. L'ER donne aussi une sensibilité (×9 pour garder la densité standardisée, p. 5).
- **PH 240** : arrondi de 242, moyenne de ≈ 237 (2024 : 8,1 % × 2 927 = 237,1) et ≈ 247 (2025). Lire ≈ 237 au lieu de ≈ 238. Les 8,1 % portent sur les primo-inscrits de toutes sections.
- **CD, Roumanie 46 %** : vaut pour les inscrits de 2015 seulement (ER 1026, p. 3).
- **Variante basse** : CD 665 et SF 70 viennent de DD76, tableau 13 ; MK 1 175 de l'ER 1075, p. 2-3. Libellé corrigé dans `etrangers.py`.
- **Âge d'entrée** : ER 1075 donne 26 ans pour les MK (même tranche 25-29 que 28 ans, effet nul, *mesuré*). Pour les PH, DD76 donne 31 ans. Pour les CD, les sources se contredisent (DD76 : 28 ; ER 1026 : 32). Non repris : voir open.md.
