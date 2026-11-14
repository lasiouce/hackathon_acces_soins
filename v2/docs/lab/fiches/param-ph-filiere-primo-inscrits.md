---
type: fiche
axe: 1
id: param-ph-filiere-primo-inscrits
parametre: "φ_PH,f — répartition des primo-inscrits à l'Ordre par section (filière d'entrée)"
profession: pharmaciens
module: filières
valeur: "2025 : A 1,2 % · B 8,6 % · C 0,4 % · D 71,0 % · E 3,5 % · G 5,7 % · H 9,5 % (N = 3 044)"
unite: "part des primo-inscrits de l'année (somme = 1)"
incertitude: "±1,5 point par section entre 2015, 2024 et 2025 (D : 66 → 71 %, H : 14 → 9,5 %) ; φ décrit la section d'inscription, pas l'employeur"
source: "Ordre national des pharmaciens (CNOP, traitement EY), Panorama 2025, dépliant, p. 2 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/demographie-2025-depliant-fr%20 ; Synthèse Panorama 2024, p. 2 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/demographie-2024-synthese ; Éléments démographiques 2016, p. 10 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/les-autres-publications/reprise-ancien-site/elements-demographique-ancien-site/panorama-1er-janvier-2016/demographie-2015_brochure-vdef.pdf"
millesime: "au 1er janvier 2026 (Panorama 2025) ; au 1er janvier 2025 ; données 2015"
statut: sourcé
date: 2026-11-14
---

# φ_PH,f — filière d'entrée des nouveaux pharmaciens

**Mécanisme.** Un diplômé qui s'inscrit à l'Ordre entre dans une section.
Les sections sont A (titulaire d'officine), B (industrie), C (distribution
en gros), D (adjoint d'officine et autres), E (outre-mer), G (biologie
médicale) ou H (établissements de santé). Le vecteur φ ventile le flux
d'entrée E_PH(t) entre ces filières.
Ensuite, la règle « privé » de la v2 s'applique : A, B, C et D sont privés,
G et H sont partagés (voir [[param-ph-part-privee-biologie]] et
[[param-ph-part-privee-etablissements]]).

| Section | 2015 (P15 p10) | 2024 (P24 p2) | 2025 (P25 p2) |
|---|---|---|---|
| A titulaires | 1 % | 30 (1,0 %) | 37 (1,2 %) |
| B industrie | 9 % (+2 % « BC ») | 260 (8,9 %) | 263 (8,6 %) |
| C distribution | 1 % | 30 (1,0 %) | 13 (0,4 %) |
| D adjoints et autres | 66 % | 1 987 (67,9 %) | 2 162 (71,0 %) |
| E outre-mer | — | 138 (4,7 %) | 107 (3,5 %) |
| G biologie | 7 % | 174 (5,9 %) | 172 (5,7 %) |
| H établissements | 14 % | 308 (10,5 %) | 290 (9,5 %) |
| **Total** | **2 324** | **2 927** | **3 044** |

*Cité* (publications de l'Ordre). Les parts 2015 sont arrondies dans la
source. Parmi les primo-inscrits, 8,1 % sont diplômés à l'étranger, en 2024
comme en 2025 (cité).

**Mesure.**
- Relever chaque année le camembert « primo-inscrits par section » du
  Panorama de l'Ordre.
- ⚑ L'extraction texte du PDF met les étiquettes dans le désordre (A et B
  inversés). Il faut lire le graphique, ou utiliser les nombres absolus.
- **Falsification.** Si φ_D 2026 sort de [0,66 ; 0,75], la série n'est pas
  stationnaire et φ doit suivre une tendance.

**Limites.**
- Un pharmacien qui n'est **pas inscrit** (une partie de l'industrie et de
  la recherche) n'entre pas dans φ_B (voir [[param-ph-taux-inscription-diplomes]]).
- On compte des inscriptions principales. Un « nouvel inscrit dans la
  section » peut aussi venir d'une autre section : par exemple 2 318 en D
  en 2024, contre 1 987 primo-inscrits.
