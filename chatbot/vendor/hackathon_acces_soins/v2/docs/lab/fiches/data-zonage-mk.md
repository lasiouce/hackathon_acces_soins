---
parametre: zonage_conventionnel
profession: MK
module: regulation
valeur: "2836 géocodes en « remplacement seul » (millésime actuel)"
unite: liste de géocodes (commune COG 2026, arrondissement pour Paris / Lyon / Marseille) × statut
incertitude: "date des arrêtés ARS non servie par CartoSanté (régions possiblement à des générations différentes) ; historique = une seule génération (2012)"
source: "CartoSanté (Atlasanté) TJS zonage_conv, arm2026, sources CNAMTS – ARS ; Atlasanté uuid c987d0e2 (génération 2012)"
millesime: "extrait 2026-11-14 ; fiche Atlasanté 2014-10-22"
statut: mesuré
---

# Zonage conventionnel par commune — kines

Table : `v2/data/processed/zonage_commune.parquet` (`profession == 'kines'`). Colonnes `com`, `niveau`
(com / arm), `millesime`, `classe`, `libelle`, `statut` (remplacement_seul / incitation / autre), `regime`.

Nombre de géocodes par classe :

| Classe | 2012 (génération ARS, fiche 2014) | actuel (extrait 2026-11-14) |
|---|---|---|
| Intermédiaire | 25642 | 13237 |
| Non prioritaire | 0 | 2826 |
| Non renseigné | 129 | 2 |
| Sous-dotée | 3692 | 5949 |
| Sur-dotée | 547 | 10 |
| Très dotée | 845 | 4 |
| Très sous-dotée | 5845 | 12891 |

Rapport : [zonage par commune](../reports/2026-11-14-axe4-zonage-commune.md). Script : `v2/data/build_zonage.py`.
