---
parametre: evenement
id: ev-mmop-2025-autre
profession: MMOP
module: donnée
valeur: "date d'effet 2025-09-01 ; flux autre ; type donnee"
unite: événement daté
incertitude: "fait et date lus sur la source"
source: "data/raw/990_drees_mmop2_2526.xlsx ; data/raw/Base inscrits 2ème cycle MOP.xlsx (fichiers d’équipe, DREES)"
millesime: "2025-2026"
statut: sourcé
---

# ev-mmop-2025-autre

Artefact de donnée, pas une réforme : le saut des inscrits 2025-26 en 2e année d'odontologie (2 083 contre ~1 550) vient d'une seule ligne, Université Paris Cité (683 contre 188-215 en 2020-2024 ; 193 en 3e année). Même gonflement à Paris Cité en médecine (2 113) et pharmacie (747). Le fichier compilé « Base inscrits 2ème cycle MOP » donne 188 à Paris Cité et 1 588 au national. Utiliser 1 588, ou remplacer la ligne Paris Cité par ~190.

Registre : `v2/data/events.csv`. Rapport : [registre d'événements](../reports/2026-11-14-axe4-registre-evenements.md).
