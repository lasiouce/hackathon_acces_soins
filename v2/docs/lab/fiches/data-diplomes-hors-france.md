---
parametre: part_actifs_sans_DE_francais
profession: SF;CD;PH;MK;IDE
module: entrees (diplômés étrangers)
valeur: "CD 24,4 % · MK 32,5 % · SF 9,7 % · PH 3,5 % · IDE 2,6 % (dont UE / EEE : CD 21,9 %, MK 32,3 %)"
unite: part des professionnels actifs (stock), nov. 2026
incertitude: "stock, pas flux ; « pas de DE français » inclut quelques autorisations et diplômes anciens ; par commune disponible"
source: "ANS, Annuaire Santé, fichier PS_LibreAcces_Dipl_AutExerc (type de diplôme obtenu), extraction 2026-11-13"
millesime: "2026-11-13"
statut: mesuré
---

# Part des actifs sans diplôme d'État français

Origine du diplôme par personne : `fr` si un diplôme d'État français, sinon `ue` (UE / EEE), sinon `autre`.
Colonne `diplome` de `annuaire_commune.parquet`. Ordre de grandeur pour le flux « diplômés étrangers » de la
filière, jusqu'ici supposé. Rapport : [grain communal](../reports/2026-11-14-axe4-grain-communal.md).
