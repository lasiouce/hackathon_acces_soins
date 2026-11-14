---
type: fiche
axe: 1
id: param-ide-rendement-diplomes
parametre: "ρ_IDE — rendement de formation : diplômés(t+3) / inscrits en 1re année(t)"
profession: infirmiers
module: formation
valeur: "0,72 (entrée 2022 : 26 020 diplômés en 2025 / 36 218 inscrits en 1re année en 2022) ; 0,77 avec les seuls nouveaux inscrits (33 972)"
unite: "diplômés par inscrit en 1re année, décalage 3 ans"
incertitude: "0,81-0,85 sur les entrées 2009-2018, puis 0,76 (2019), 0,75 (2020), 0,71 (2021), 0,72 (2022) ; le dénominateur inclut les redoublants ; entrées directes au numérateur (2e année : 1 000 à 1 400 par an ; 2e + 3e : 1 400 à 2 100 par an, 2022-2025)"
source: "DREES, enquête Écoles, jeu 491, Séries longues 1966-2025, onglets Inscrits1ere_an et Diplomes_an — https://data.drees.solidarites-sante.gouv.fr/explore/dataset/491_la-formation-aux-professions-de-sante/ ; contrôle : ER 1266 (diplômés 2021 = 81 % des inscrits en 1re année 2018), communiqué DREES du 07/11/2023 (76 % pour 2022)"
millesime: "entrées 2008-2022, diplômés 2011-2025 (mise à jour du 29/10/2026)"
statut: mesuré
date: 2026-11-14
---

# ρ_IDE — rendement diplômés / entrants en IFSI

**Mécanisme.** C'est le paramètre que lit directement le module formation
du jumeau : diplômés(t+3) = ρ · inscrits en 1re année(t). ρ englobe abandon,
redoublement et passerelles. 1 − ρ n'est **pas** un taux d'abandon.

**Valeur.** *Dérivé* des séries DREES : 1 − ρ = 1 − diplômés(t+3) / inscrits 1A(t).
| Entrée t | 2009 | 2012 | 2015 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---|---|---|---|---|---|---|---|---|
| Inscrits 1A | 31 302 | 30 735 | 31 322 | 30 182 | 32 114 | 32 450 | 35 355 | 36 218 |
| Diplômés t+3 | 26 447 | 25 888 | 25 757 | 24 557 | 24 379 | 24 215 | 25 249 | 26 020 |
| 1 − ρ | 15,5 % | 15,8 % | 17,8 % | 18,6 % | 24,1 % | 25,4 % | 28,6 % | 28,2 % |
L'année 2008 est exclue : la note DREES dit que la méthode de comptage change *à partir de* 2008, ce qui n'explique pas l'anomalie de ρ(2008) ; celle-ci reste inexpliquée. *[Corrigé le 2026-11-14 après audit : [[2026-11-14-audit-sources]].]*
Contrôle : ER 1266 donne 81 % pour l'entrée 2018, nous trouvons 81,4 %.

**Mesure.**
- Recalcul annuel : script reproduit en annexe du rapport
  [[2026-11-14-axe1-hyperparametres]] (lecture de la série longue
  DREES, onglets `Inscrits1ere_an` et `Diplomes_an`).
- Les taux de passage en découlent (*dérivés*) :
  - 2e(t+1) / 1re(t) : de 0,94 à 0,96 jusqu'en 2018, puis 0,86 en 2021-2024 ;
  - diplômés(t+1) / 3e(t) : de 0,88 (2010) à 0,81 (2023-2024).
- ⚑ L'écart d'environ 28 % pour les entrées récentes est le chiffre le plus
  proche du « 30 % » qui circule. Mais c'est un écart cumulé sur 3 ans,
  calculé avec les redoublants au dénominateur : ce n'est **pas** un abandon
  annuel.
