---
type: fiche
axe: 1
id: param-ide-abandon-1a
parametre: "a_IDE,1 — taux d'interruption en 1re année d'IFSI"
profession: infirmiers
module: abandon
valeur: "12,0 % (2025, toutes interruptions)"
unite: "part des inscrits en 1re année, par an"
incertitude: "3,3 % (2011) → 10,0 % (2021) → 13,1-13,5 % (2022-2024 : 5,0-5,8 % définitives + 7,3-8,5 % provisoires) → 12,0 % (2025, questionnaire modifié)"
source: "DREES, enquête Écoles, jeu 491, Séries longues 1966-2025, onglet Interruptions_1A ; fichier annuel 2025, tableau 1E — https://data.drees.solidarites-sante.gouv.fr/explore/dataset/491_la-formation-aux-professions-de-sante/"
millesime: "série 2011-2025, mise à jour du 29/10/2026"
statut: sourcé
relecture: "2026-11-15 : confirmé (valeur) ; libellés corrigés"
date: 2026-11-14
---

# a_IDE,1 — interruption en 1re année

**Mécanisme.** L'abandon est concentré en 1re année : 39 % des abandons
d'une promotion selon l'ER 1266. Il a quadruplé entre 2011 et 2022, avec un
saut au passage à Parcoursup (2019). Un levier sur l'orientation ou
l'accompagnement agit d'abord ici.

**Valeur.**
- Taux d'interruption, *cités* : 3,3 % (2011), 4,6 (2016), 6,4 (2019), 7,6
  (2020), 10,0 (2021), 13,1 (2022), 13,5 (2023), 13,5 (2024), 12,0 (2025).
- En 2025, 4 694 interruptions en 1re année, dont 1 155 pour changement de
  formation et 2 036 pour raisons personnelles (*cité*).

**Mesure.** Onglet `Interruptions_1A` de la série longue, chaque année.
Rupture en 2022 : on passe des seules interruptions sans report à toutes
les interruptions.
**Falsification.** Si la valeur 2026 sort de [10 ; 15 %], le palier
2022-2025 n'est pas stable.

## Relecture en texte intégral (2026-11-15)

Verdict : **confirmé (valeur) ; libellés corrigés** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- 12,0 % (2025) et la série 2011-2025 confirmés (491, onglet Interruptions_1A).
- **Dénominateur** : interruptions de l'année N / (inscrits S1 de N + moyenne des inscrits S2 de N et N − 1) (*cité*, encadré méthode).
- « Quadruplé entre 2011 et 2022 » : l'ER 1266 dit « trois fois » entre 2011 et 2021 (3 % → 10 %). Le 13,1 % de 2022 franchit la rupture de définition (toutes interruptions).
- Parcoursup : l'ER le cite à propos des effectifs seulement, pas comme cause de l'abandon. Le « saut de 2019 » est *supposé*.
- 4 694 / 1 155 / 2 036 (fichier annuel 2025, tableau 1E) : non relus, fichier annuel non ouvert.
