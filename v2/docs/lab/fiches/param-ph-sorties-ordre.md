---
type: fiche
axe: 1
id: param-ph-sorties-ordre
parametre: "X_PH — radiations annuelles de pharmaciens sans réinscription, et vieillissement (part des 60 ans et plus)"
profession: pharmaciens
module: sorties
valeur: "3 902 radiations sans réinscription en 2024 ; 18,4 % de 60 ans et plus (2024), contre 13,6 % en 2014 ; 4 502 inscrits de 66 ans et plus (≈ 6,0 %)"
unite: "personnes par an ; part des inscrits"
incertitude: "radiation ≠ cessation (changement de pays, non-réinscription d'industriels) ; repère régional ARS CVL 2023 : arrêt des titulaires à 61,1 ans en moyenne (médiane 63), des adjoints à 45,8 ans (médiane 41), petits effectifs"
source: "Ordre national des pharmaciens, Synthèse Panorama 2024, p. 4 et 8-9 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/demographie-2024-synthese"
millesime: "au 1er janvier 2025 (données 2024)"
statut: sourcé
date: 2026-11-14
---

# X_PH — sorties de pharmaciens

**Mécanisme.**
- Les sorties de l'Ordre (radiations sans réinscription) sont le flux de
  sortie observé.
- La part croissante des 60 ans et plus (+4,8 points en 10 ans) montre que
  les sorties sont **reportées**. C'est cohérent avec le +1 527 pharmaciens
  de plus de 65 ans mesuré par la v1 (ROADMAP § 2) : la retraite n'est pas
  stationnaire.
- Les adjoints cessent jeunes (âge médian 41 ans, repère régional). C'est
  probablement une sortie de la section D vers d'autres sections ou
  activités, pas une retraite.

**Valeur.** 3 902 radiations en 2024, pour 3 044 primo-inscrits en 2025
(*cité*). Le solde est positif, porté par les réinscriptions et les
retours.

**Mesure.** Chaque Panorama, p. 8. Il faut le croiser avec les sorties
apparentes RPPS par âge ([[param-cessation-par-age]]).
