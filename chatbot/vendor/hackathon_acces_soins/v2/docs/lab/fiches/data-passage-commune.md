---
parametre: passage_commune
profession: SF;CD;PH;MK;IDE
module: etat (territoire)
valeur: "39 227 codes sources → géocode du jumeau → EPCI → bassin de vie 2022 → dép. → région (COG 2026)"
unite: table de correspondance
incertitude: "fusions par fermeture transitive des événements Insee ; sans EPCI : COM hors champ et 4 communes insulaires"
source: "Insee COG 2026 (événements depuis 1943), Insee BV2022 au 01/01/2026, geo.api.gouv.fr (EPCI)"
millesime: "COG 2026"
statut: mesuré
---

# Table de passage commune → EPCI → bassin de vie → département

Table `passage_commune.parquet`, script `v2/data/build_passage.py`. Rapport : [projection communale](../reports/2026-11-14-axe4-projection-communale.md).
