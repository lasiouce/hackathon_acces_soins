---
parametre: zonage_conventionnel
profession: SF
module: regulation
valeur: "1471 géocodes en « remplacement seul » (millésime actuel)"
unite: liste de géocodes (commune COG 2026, arrondissement pour Paris / Lyon / Marseille) × statut
incertitude: "date des arrêtés ARS non servie par CartoSanté (régions possiblement à des générations différentes) ; historique = une seule génération (2012), absente pour les SF"
source: "CartoSanté (Atlasanté) TJS zonage_conv, arm2026, sources CNAMTS – ARS ; Atlasanté uuid c987d0e2 (génération 2012)"
millesime: "extrait 2026-11-14 ; fiche Atlasanté 2014-10-22"
statut: mesuré
---

# Zonage conventionnel par commune — sages-femmes

Table : `v2/data/processed/zonage_commune.parquet` (`profession == 'sages-femmes'`). Colonnes `com`, `niveau`
(com / arm), `millesime`, `classe`, `libelle`, `statut` (remplacement_seul / incitation / autre), `regime`.

Nombre de géocodes par classe :

| Classe | actuel (extrait 2026-11-14) |
|---|---|
| Intermédiaire | 19608 |
| Non renseigné | 24 |
| Sous-dotée | 5588 |
| Sur-dotée | 1471 |
| Très dotée | 1954 |
| Très sous-dotée | 6274 |

Rapport : [zonage par commune](../reports/2026-11-14-axe4-zonage-commune.md). Script : `v2/data/build_zonage.py`.
