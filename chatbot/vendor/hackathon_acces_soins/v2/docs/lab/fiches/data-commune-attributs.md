---
parametre: attributs_commune
profession: SF;CD;PH;MK;IDE
module: installation (logit, covariables)
valeur: "35 011 géocodes × 2012–2025 : population, parts 0–14 / 65+ / 80+, densité 7 niveaux, AAV, distance au pôle, officines, maisons et centres de santé, zonage, offre libérale, I_net"
unite: table commune × année
incertitude: "population 2024–25 = 2023 reportée ; âge interpolé entre RP 2012, 2017, 2023 ; distance à vol d'oiseau ; zonage sans date par région"
source: "Insee (séries de population, RP 2023 évolution et structure, grille de densité 2015–2024, AAV 2020, BV 2022, COG 2026), geo.api.gouv.fr, FINESS, CartoSanté"
millesime: "géographie 2026 ; RP 2023 mis en ligne le 25/06/2026"
statut: mesuré
---

# Attributs des communes pour le logit d'installation

Table `commune_attributs.parquet`, script `v2/data/build_attributs.py`. Contrôle : Σ population 2023 =
68 094 280 = population légale (geo.api, hors Mayotte et COM). Rapport : [flux communaux](../reports/2026-11-14-axe4-flux-communaux.md).
