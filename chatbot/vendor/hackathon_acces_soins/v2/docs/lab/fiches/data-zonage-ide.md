---
parametre: zonage_conventionnel
profession: IDE
module: regulation
valeur: "4786 géocodes en « remplacement seul » (millésime actuel)"
unite: liste de géocodes (commune COG 2026, arrondissement pour Paris / Lyon / Marseille) × statut
incertitude: "date des arrêtés ARS non servie par CartoSanté (régions possiblement à des générations différentes) ; historique = une seule génération (2012)"
source: "CartoSanté (Atlasanté) TJS zonage_conv, arm2026, sources CNAMTS – ARS ; Atlasanté uuid c987d0e2 (génération 2012)"
millesime: "extrait 2026-11-14 ; fiche Atlasanté 2014-10-22"
statut: mesuré
---

# Zonage conventionnel par commune — infirmiers

Table : `v2/data/processed/zonage_commune.parquet` (`profession == 'infirmiers'`). Colonnes `com`, `niveau`
(com / arm), `millesime`, `classe`, `libelle`, `statut` (remplacement_seul / incitation / autre), `regime`.

Nombre de géocodes par classe :

| Classe | 2012 (génération ARS, fiche 2014) | actuel (extrait 2026-11-14) |
|---|---|---|
| Intermédiaire | 24427 | 15676 |
| Non renseigné | 129 | 2 |
| Sous-dotée | 3014 | 4216 |
| Sur-dotée | 3135 | 4786 |
| Très dotée | 1672 | 8765 |
| Très sous-dotée | 4323 | 1474 |

Rapport : [zonage par commune](../reports/2026-11-14-axe4-zonage-commune.md). Script : `v2/data/build_zonage.py`.
