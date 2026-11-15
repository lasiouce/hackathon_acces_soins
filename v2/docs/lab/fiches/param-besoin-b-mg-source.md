---
type: fiche
axe: 1
id: param-besoin-b-mg-source
parametre: "B_MG — besoin de médecine générale, calculé par M1 comme source des transferts seulement (décision O2)"
profession: [medecine-generale (source seulement)]
module: besoin (opérateur de transfert, côté A)
valeur: "fiche de source et de méthode : valeurs à produire par l'axe 4 ; MG = PSE_SPE_SNDS 1 ; prestations repérées : 1110 G, 1109 GS, 1111 C (générique), 1210 VG, 1209 VGS, 1211 V (générique), 1192 TCG ; repère d'activité : ~4 800 actes par MG et par an (DREES ER 1381, déclaratif)"
unite: "actes de MG par habitant et par an ; sortie : actes et ETP de MG libérés"
incertitude: "liste des PRS_NAT « consultation de MG » à arrêter (axe 4) ; spécialité 1 = MG comme exécutant, pas les généralistes à exercice particulier ; mêmes limites de grain que DAMIR (13 régions, 80 et +)"
source: "Open DAMIR, descriptif des variables 2024 (onglet « MOD OPEN DAMIR », PSE_SPE_SNDS et PRS_NAT) ; DREES, Études et Résultats n° 1381 (août 2026), p. 2-3 ; registre v2/docs/lab/decisions.md, entrée du 2026-11-15 « médecine générale comme source seulement (O2) »"
millesime: "DAMIR 2009-2025 ; panel DREES 2025-26"
statut: "méthode sourcée ; valeur à mesurer (axe 4)"
date: 2026-11-15
---

# B_MG — la médecine générale comme source des transferts

## Interdit (rappel de la décision O2, 2026-11-15)
- La MG entre **comme profession source des transferts seulement**. `B_MG` est calculé par M1.
- **Aucune offre de MG projetée, aucun indice de couverture MG**, nulle part : API, carte, rapport.
- **Affichage autorisé :** « actes de MG transférés » et « ETP de MG libérés ». Jamais un rapport offre / besoin de MG.
- Même règle pour les spécialistes tant qu'ils sont en phase 2.

## Source
- **Exécutant MG** : `PSE_SPE_SNDS = 1` « MEDECINE GENERALE » (descriptif DAMIR 2024). Les codes 22 et 23 n'existent
  pas dans `PSE_SPE_SNDS`.
- **Prestations** (`PRS_NAT`, relevées dans le descriptif) : 1110 consultation de médecine générale (G), 1109 GS,
  1111 C (code générique, filtrer par `PSE_SPE_SNDS = 1`), 1210 visite (VG), 1209 VGS, 1211 V, 1192 téléconsultation de généraliste (TCG). Le descriptif contient aussi
  1959 « ADMINISTRATION VACCIN » (VAX), sans indication de l'exécutant ; la Cour des comptes compare l'acte officinal à
  la consultation de MG à 30 € (p. 45) et ne dit pas que le médecin n'a pas d'acte propre. Le code de l'injection
  antigrippale chez le MG reste à établir (axe 4).
- **Repère d'activité** (DREES ER 1381, p. 3, déclaratif, MG libéraux de plus de 200 patients médecin traitant) :
  ~4 800 consultations, visites et téléconsultations par médecin en 2025 ; consultation de 19 min (p. 2 ; mis en exergue p. 1). Pour
  convertir des actes libérés en ETP de MG : `ETP = actes / q_MG`. Le Lisez-moi APL (p. 3, point 2) cite 5 400 consultations,
  visites et téléconsultations comme activité attribuée « auparavant » aux MG primo-installés : c'est une **ancienne**
  convention, abandonnée, pas une valeur de `q_MG` *[corrigé après relecture]*. `q_MG` est donc non mesuré ici.

## Méthode
Identique à [[param-besoin-profil-damir]] avec `PSE_SPE_SNDS = 1` et la liste de `PRS_NAT` ci-dessus : `r(MG, a)` sur
8 tranches, région × année ; `B_MG(T, t) = Σ_a pop(T, t, a) · r(MG, a)`.

## Usage
`B_MG` alimente le terme `B_A` des transferts L23 (part médicale), tension / diabète, L25 et L27. Seule L23 a un
`a` sourcé ([[param-besoin-l23-vaccination]]).
