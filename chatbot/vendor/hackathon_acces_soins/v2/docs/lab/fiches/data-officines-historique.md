---
parametre: officines_commune_flux
profession: PH
module: installation (officines)
valeur: "20 083 officines fin 2025 (23 241 en 2004) ; 2025 : 10 ouvertures, 251 fermetures"
unite: établissements FINESS cat. 620, état au 31/12
incertitude: "fin 2024 : 20 324 contre 20 242 (Ordre, 1/1/2025), +0,4 % ; transfert sous nouveau numéro = fermeture + ouverture ; 99,9 % rattachées au COG 2026"
source: "FINESS, extraction des établissements, historique 2004–2025 (data.gouv.fr) ; Insee, événements des communes depuis 1943 (COG 2026)"
millesime: "2026-01-08 (historique) ; COG 2026"
statut: mesuré
---

# Officines, maisons et centres de santé par commune, 2004–2025

Tables `finess_commune_annee.parquet` (officines, maisons de santé 603 dès 2012, centres de santé 124 dès 2014) et
`officines_flux_commune.parquet` (ouvertures, fermetures, transferts). Script `v2/data/build_finess_histo.py`.
Rapport : [flux communaux](../reports/2026-11-14-axe4-flux-communaux.md).
