---
type: fiche
axe: 1
id: param-besoin-l27-kine
parametre: "Transfert L27 — accès direct aux masseurs-kinésithérapeutes (A = médecine générale, consultation prescriptrice ; B = MK) : a, k, s_∞, τ, m"
profession: [kines]
module: besoin (opérateur de transfert)
valeur: "k = 0 côté MK par construction (l'acte de MK ne change pas) ; plafond réglementaire de 8 séances sans diagnostic médical ; a, s_∞, τ : non mesurables ; m : signe seulement (≤ 0 sur le recours au MG, revues de littérature), pas de valeur"
unite: "k : sans dimension ; plafond : séances par patient"
incertitude: "aucun volume de séances en accès direct ni nombre de MK inscrits à l'expérimentation publiés ; décret et arrêté non lus à la source ; littérature étrangère sans chiffre de consultations de MG évitées"
source: "loi n° 2023-379 du 19 mai 2023, art. 3 (Légifrance, version en vigueur, lue par un relais) ; sante.fr « L'accès direct aux masseurs-kinésithérapeutes » ; Vidal actualité n° 31418 ; décret n° 2024-618 et arrêté du 6 juin 2025 (non lus à la source) ; Babatunde et coll. 2020, PLoS ONE 15(7):e0235364, doi:10.1371/journal.pone.0235364 (PMC7337346, lu en partie) ; Ojha et coll. 2014, Phys Ther 94(1):14-30, doi:10.2522/ptj.20130096 (résumé)"
millesime: "2023-2026"
statut: "partiel : k par construction, plafond sourcé ; a, s_∞, τ non mesurables ; m signe seulement"
date: 2026-11-15
---

# L27 — accès direct au kinésithérapeute

**Verdict : partiel**, comme attendu au plan.

## Mécanisme (dérivation §6)
L'acte de MK ne change pas : seule disparaît la consultation de MG qui le prescrivait. Côté MK, `k = 0` par
construction (pas de temps de MK ajouté par unité de temps de MG libérée). Le besoin de MG baisse de `s · a · B_MG`, où
`a` = part des consultations de MG qui servent à prescrire de la kinésithérapie.

## Ce qui a été lu
- **Loi n° 2023-379, art. 3** (Légifrance, relais) : exercice « sans prescription médicale » dans les structures
  d'exercice coordonné ; expérimentation de 5 ans ; la version en vigueur dit « au plus vingt départements » (6 dans
  le texte promulgué).
- **sante.fr** (site public, lu) : sans diagnostic médical préalable, **huit séances** au plus par patient, puis
  réorientation vers le médecin traitant ; expérimentation jusqu'au 31 décembre 2029 ; accès direct en exercice
  coordonné en vigueur depuis le 22 août 2023.
- **Arrêté du 6 juin 2025** : 20 départements (liste concordante entre sante.fr et Vidal : Aude, Deux-Sèvres,
  Côtes-d'Armor, Gers, Haute-Corse, Haut-Rhin, Isère, Loiret, Martinique, Mayotte, Meurthe-et-Moselle, Nord,
  La Réunion, Rhône, Seine-Maritime, Tarn, Var, Vendée, Yonne, Yvelines). Date du JO incohérente dans la presse
  (8 ou 11 juin). Texte non lu à la source.
- **Volumes** : « ni volume de séances réalisées, ni nombre de kinésithérapeutes inscrits » publiés (caducee.net
  n° 16941, presse, paraphrase du relais).
- **Littérature.** Babatunde 2020 (revue systématique, lue en partie) : « In most studies direct access patients were
  reported to have lower healthcare utilisation » ; coûts plus bas de 10 à 20 % et renvois pour le même trouble plus bas de 2 % et 10 %, chacun dans une ou deux études
  isolées, hors France ; aucun nombre de consultations de MG évitées. Ojha 2014 (revue,
  résumé) : moins de séances, d'imagerie et de consultations non kiné, sans valeur chiffrée dans le résumé.

## Par paramètre
| Paramètre | Valeur | Statut | Raison |
|---|---|---|---|
| `k` | 0 (côté MK) | **par construction** | l'acte transféré est la prescription, qui n'a pas d'équivalent chez le MK |
| plafond | 8 séances par patient sans diagnostic | **sourcé** (sante.fr) | borne du périmètre, pas un volume |
| `a` | — | **non mesurable** | part des consultations de MG à motif de prescription de kinésithérapie : non publiée ; DAMIR ne relie pas une consultation à la prescription qui en sort |
| `s_∞`, `τ` | — | **non mesurables** | aucun volume en accès direct ; pas de code distinct dans DAMIR |
| `m` | signe : ≤ 0 sur le recours au MG | **partiel** (signe sourcé, pas de valeur) | Babatunde 2020, Ojha 2014 |

## Usage
Exposable seulement avec `a` et `s` **supposés** et étiquetés ; `k = 0` est structurel. Point de reprise : rapport
d'évaluation de l'expérimentation (au plus tard mi-2029), ou séries départementales de séances de MK (patientèle
data.ameli.fr) comparées entre les 20 départements et les autres (différence de différences, à pré-enregistrer).
