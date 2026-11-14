---
parametre: zonage_conventionnel
profession: CD
module: regulation
valeur: "97 géocodes en « remplacement seul » (millésime actuel)"
unite: liste de géocodes (commune COG 2026, arrondissement pour Paris / Lyon / Marseille) × statut
incertitude: "date des arrêtés ARS non servie par CartoSanté (régions possiblement à des générations différentes) ; historique = une seule génération (2012)"
source: "CartoSanté (Atlasanté) TJS zonage_conv, arm2026, sources CNAMTS – ARS ; Atlasanté uuid c987d0e2 (génération 2012)"
millesime: "extrait 2026-11-14 ; fiche Atlasanté 2014-10-22"
statut: mesuré
---

# Zonage conventionnel par commune — dentistes

Table : `v2/data/processed/zonage_commune.parquet` (`profession == 'dentistes'`). Colonnes `com`, `niveau`
(com / arm), `millesime`, `classe`, `libelle`, `statut` (remplacement_seul / incitation / autre), `regime`.

Nombre de géocodes par classe :

| Classe | 2012 (génération ARS, fiche 2014) | actuel (extrait 2026-11-14) |
|---|---|---|
| Intermédiaire | 24266 | 6975 |
| Non prioritaire | 0 | 97 |
| Non renseigné | 129 | 26 |
| Sous-dotée | 4029 | 2048 |
| Sur-dotée | 908 | 0 |
| Très dotée | 1574 | 1052 |
| Très sous-dotée | 5794 | 24721 |

Rapport : [zonage par commune](../reports/2026-11-14-axe4-zonage-commune.md). Script : `v2/data/build_zonage.py`.
