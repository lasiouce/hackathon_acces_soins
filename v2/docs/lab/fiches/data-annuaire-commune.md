---
parametre: N_prive_commune_instantane
profession: SF;CD;PH;MK;IDE
module: etat (commune)
valeur: "privés au 2026-11-13 : PH 61 882 · SF 11 612 · CD 48 489 · MK 96 177 · IDE 228 598 (ambigus 203 à 40 678)"
unite: personnes (une personne à k activités compte 1/k par commune)
incertitude: "instantané sans âge ; activités sans commune : 0,4 % (PH) à 11,5 % (CD) ; écart médian par dép. à la centrale DREES 2026 : −3,2 % (PH) à −14,6 % (IDE)"
source: "ANS, Annuaire Santé — extractions des données en libre accès (RPPS), data.gouv.fr, PS_LibreAcces_202611131942.zip ; FINESS entités juridiques au 2026-05-04"
millesime: "2026-11-13"
statut: mesuré
---

# Effectif privé par commune — Annuaire Santé (instantané)

Table `v2/data/processed/annuaire_commune.parquet` : profession × commune (arrondissements PLM) × sexe (civilité)
× mode × statut (prive / public / ambigu) × origine du diplôme. Script `v2/data/build_annuaire.py`.
Seule source communale ouverte pour les pharmaciens et les sages-femmes. Aucune donnée nominative en sortie.
Rapport : [grain communal](../reports/2026-11-14-axe4-grain-communal.md).
