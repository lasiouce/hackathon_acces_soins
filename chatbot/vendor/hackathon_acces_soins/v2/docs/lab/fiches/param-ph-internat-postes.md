---
type: fiche
axe: 1
id: param-ph-internat-postes
parametre: "Q_PH,int — postes d'internat en pharmacie par DES (voie biologie / pharmacie hospitalière)"
profession: pharmaciens
module: filières
valeur: "rentrée 2025 : 266 biologie médicale + 480 pharmacie hospitalière = 746 postes ; 536 internes inscrits en 1re année en 2025-26"
unite: "postes offerts par an ; internes inscrits en 1re année"
incertitude: "postes ≠ postes pourvus (536 inscrits en 1re année pour 746 postes, écart non expliqué : périmètre et calendrier à vérifier) ; le fichier local masque probablement les petits effectifs (cellules vides, nombreux « 4 ») : en 2018, 497 postes pourvus sur 498 ouverts (CNG)"
source: "Arrêté du 6/12/2024, NOR MSAH2433194A, JORF du 7/12/2024, texte 28 (480 pharmacie hospitalière + 266 biologie médicale) ; Ordre national des pharmaciens, Synthèse Panorama 2024, p. 13-14 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/demographie-2024-synthese ; ONDPS/DREES 2016 (cité par P15 p. 9) ; données d'inscription DREES (fichier hackathon data/raw/Données pharma 2ème et 3ème cycle.xlsx, onglet Internat Pharma)"
millesime: "rentrées 2023-24 à 2025-26 ; 2005-2015 (répartition par filière : 2010-2015) ; années universitaires 2020-21 à 2025-26"
statut: sourcé
date: 2026-11-14
---

# Q_PH,int — internat en pharmacie

**Mécanisme.** L'internat est la seule voie vers la biologie médicale
(section G) et la pharmacie hospitalière (section H). Les postes ouverts
fixent donc, avec un délai de 4 ans, l'essentiel des flux φ_G et φ_H. Le
reste d'une promotion va vers l'officine (D, puis A) ou l'industrie (B).

**Valeur.**
- Postes 2023-24 / 2024-25 / 2025-26, *cités* (P24) :
  - biologie médicale : 228 / 253 / 266 ;
  - DES pharmacie hospitalière : 401 / 441 / 480.
- 2005-2015 : de 478 à 541 postes par an, soit 15 à 22 % du numerus
  clausus quatre ans plus tôt. Répartition sur 2010-2015 : pharmacie 59-62 %, biologie
  28-31 %, innovation pharmaceutique et recherche 9-10 % (*cité*).
- Internes en 1re année, *mesuré* dans le fichier local : 381 (2020-21),
  448, 450, 516, 550, 536 (2025-26).
- Rapporté aux étudiants de 6e année, environ 3 900 par an (même fichier) :
  - en postes ouverts, 746 / 3 901 ≈ 19 % d'une promotion (*dérivé*) ;
  - en inscrits de 1re année, 536 / 3 901 ≈ 14 % (*dérivé*), sans doute
    sous-estimé par le masquage du fichier. *[Corrigé le 2026-11-14 après audit : [[2026-11-14-audit-sources]].]*

**Mesure.**
- Arrêté annuel du CNG fixant les postes d'internat en pharmacie, par DES
  et par subdivision.
- Croiser avec les inscrits en 1re année d'internat, donnée DREES
  `data/raw/990_drees_mmop2_f.xlsx`, type `DES PHARMACIE`.
