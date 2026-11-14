---
type: fiche
axe: 1
id: param-ide-abandon-promotion
parametre: "a_IDE — taux d'interruption d'études sur l'ensemble de la scolarité (par promotion)"
profession: infirmiers
module: abandon
valeur: "25,0 % (promotion diplômée en 2025, toutes interruptions) ; 11,9 % d'interruptions définitives (promotion 2024)"
unite: "part d'une promotion (cumul sur 3 ans)"
incertitude: "large : 10,4 % (2014) → 25,0 % (2025) ; changement de définition en 2022 (on passe des interruptions sans report à toutes les interruptions) puis de questionnaire en 2025 ; promotion théorique, pas de suivi individuel"
source: "DREES, enquête Écoles, jeu « La formation aux professions de santé » (491), Séries longues 1966-2025, onglet Interruptions_promo — https://data.drees.solidarites-sante.gouv.fr/explore/dataset/491_la-formation-aux-professions-de-sante/ ; DREES Études et Résultats n° 1266 (mai 2023) — https://drees.solidarites-sante.gouv.fr/sites/default/files/2023-05/ER1266.pdf"
millesime: "série 2014-2025, mise à jour du 29/10/2026"
statut: sourcé
date: 2026-11-14
---

# a_IDE — interruption des études infirmières, par promotion

**Mécanisme.** Une part de chaque cohorte entrée en IFSI ne sort pas
diplômée. Le flux de diplômés est donc E_IDE(t) = (1 − a) · entrants(t−3),
à corriger des redoublements. a est le levier « réduire l'abandon »
(accompagnement, sélection, bourses).

**Valeur.** Taux d'interruption, en %, repérés par l'année de diplôme de la
promotion (*cité*, données DREES) :
| Promotion (diplôme) | 2014 | 2016 | 2018 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| Toutes interruptions | 10,4 | 11,2 | 11,3 | 12,0 | 13,5 | 18,3 | 20,2 | 23,0 | 25,0 |
| Définitives seulement | — | — | — | — | — | 16,9 | 15,1 | 11,9 | n.d. |

- L'ER 1266 donne 14 % d'abandon pour la promotion entrée en 2018 ; 39 % des
  abandons ont lieu en 1re année (*cité*).
- **« 30 % d'abandon »** : non retrouvé dans une source primaire. Le
  chiffre vient d'une réponse ministérielle à la question orale AN n° 101
  (11/01/2023), qui n'en donne pas la source. Il ne concorde avec aucune
  série DREES. **Non retenu.**

**Mesure.**
- Lire l'onglet `Interruptions_promo` à chaque mise à jour annuelle.
- Pour le modèle, préférer le rendement diplômés / entrants
  ([[param-ide-rendement-diplomes]]) : il intègre redoublements, reports et
  passerelles.
- ⚑ Les interruptions « provisoires » reviennent en partie : les notes sont
  conservées 3 ans (arrêté du 21/04/2007). Toutes interruptions = borne
  haute ; définitives = borne basse.
