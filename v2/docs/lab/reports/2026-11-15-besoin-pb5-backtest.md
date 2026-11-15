---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: Projeter le recours 2016 → 2025 par la seule structure d'âge (M1) bat-il la persistance du recours par habitant, et un GBM bat-il M1 ?
headline: "(passage non lancé : écarts au protocole écrits avant calcul)"
status: draft
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B1 ; protocole gelé P-B5 (v2/validation/preregistered/2026-11-15-besoin-p-b5-backtest.md) et amendement A1.3
sources: [patientèle et démographie data.ameli.fr (ODbL), estimations de population Insee (1975–2023), Omphale 2022, poids APL, effectifs du jumeau, grille de densité Insee 2016]
tags: [besoin, validation, P-B5, backtest, GBM]
---

# P-B5 — backtest du recours par la structure d'âge (passage)

> **Headline :** (à remplir après le passage)

## Écarts au protocole et à A1.3, écrits le 2026-11-15 avant tout calcul
Protocole gelé (RFC 3161, 02:17:19 UTC) ; A1 gelé à 03:18:22 UTC. Seuils, IC, Bonferroni et hyperparamètres du GBM
inchangés.

1. **Population.** Téléchargé avec l'accord de l'utilisateur·rice (2026-11-15) : Insee, « Estimation de population au
   1ᵉʳ janvier, par département, sexe et âge quinquennal », fichier `estim-pop-dep-sexe-aq-1975-2023.xls`
   (insee.fr, page 1893198, paru en janvier 2023, résultats provisoires arrêtés fin 2022 ; SHA-256
   `97a4caea25fd02a4…`), stocké dans `v2/data/raw/insee/` (ignoré par git). C'est le millésime le plus récent
   servi par la page le 2026-11-15 ; aucun fichier 1975–2024 ou 1975–2025 n'y est publié (adresses essayées : 500).
   - **2016 et 2021** : estimations Insee telles quelles.
   - **2025** : non publiée dans ce millésime. `pop(d,2025,a,s) = Insee(d,2023,a,s) × Omphale(d,2025,a,s) /
     Omphale(d,2023,a,s)` (Omphale 2022 central). Rapporté, non décisif : la même chaîne avec la cible **2023**
     (h = 7, Insee 2023 provisoire, sans Omphale).
2. **Densité libérale de 2016 (covariable du GBM).** Effectifs du jumeau (secteur privé). Les **kinés** n'ont pas
   2016 dans la table de secteur : on prend **2017**. Les IDE n'ont pas Mayotte : le GBM IDE travaille sans 976,
   comme M1 et la persistance (jointure).
3. **Densité des trois autres** : somme des effectifs du jumeau des trois autres professions de la patientèle, même
   année que (2), sur la population 2016.
4. **Communes denses ou intermédiaires** : grille de densité à 7 niveaux, géographie 2016 (Insee, fichier sur
   disque) ; niveaux 1 à 4 (grands centres urbains, centres urbains intermédiaires, ceintures urbaines, petites
   villes), qui forment « dense » et « intermédiaire » de la grille à 4 niveaux ; poids = population municipale 2014
   du fichier. Les cinq DROM y figurent (vérifié) ; département = deux premiers caractères du code commune (trois
   pour 97x).
5. **Validation croisée « une région laissée de côté »** : régions 2016 telles qu'elles sont, 13 métropolitaines et
   5 DROM, soit **18 plis** (le protocole dit « 13 plis » sans dire où vont les DROM ; même choix que P-B3).
6. **Recours** `R = file active × effectif ameli` (A1.1) pour 2016, 2021, 2025.
7. **Sensibilité P2** : poids APL colonne **2022** (DCIR 2020), pour les quatre professions (A1.3). Règle « dépendante
   du profil » appliquée à elle.
8. **Bootstrap** : départements tirés avec remise, MAPE recalculées sur les prédictions déjà faites (GBM non
   réentraîné), B = 2 000, graine 20261115, IC percentile bilatéral à 98,75 %.
9. **scikit-learn** : version installée au passage (`uv run --with scikit-learn`), inscrite dans les résultats.
