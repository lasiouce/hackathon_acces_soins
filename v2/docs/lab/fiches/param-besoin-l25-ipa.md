---
type: fiche
axe: 1
id: param-besoin-l25-ipa
parametre: "Transfert L25 — accès direct aux infirmiers en pratique avancée (A = médecine générale ; B = IDE (IPA)) : a, k, s_∞, τ, m"
profession: [infirmiers]
module: besoin (opérateur de transfert)
valeur: "non mesurable pour les cinq paramètres de l'accès direct ; volume global d'actes IPA mesurable dans Open DAMIR (codes 1654 IEX, 3129 MIP, 3130 PAI), sans distinction de l'accès direct ; repère de stock : 3 973 IPA diplômés (Unipa, janv. 2026, presse) — diplômés, pas en exercice"
unite: "—"
incertitude: "aucun volume d'actes en accès direct publié ; expérimentation en CPTS ouverte le 1er déc. 2026 (presse), donc aucune donnée avant 2027 ; décrets non lus à la source"
source: "loi n° 2023-379 du 19 mai 2023, art. 1 (Légifrance, version consolidée, lue par un relais) ; décret n° 2025-55 du 20 janvier 2025 (connu par la FHF, texte non lu) ; décret n° 2026-985 et arrêté du 23 oct. 2026 (presse : santementale.fr, caducee.net n° 16996) ; recensement Unipa du 26 janv. 2026 (presse)"
millesime: "2023-2026"
statut: "non mesurable (accès direct) ; volume IPA global mesurable (axe 4)"
date: 2026-11-15
---

# L25 — IPA en accès direct

**Verdict : non mesurable** (`a`, `k`, `s_∞`, `τ`, `m`). Conforme à l'attendu du plan.

## Ce qui a été lu
- **Loi n° 2023-379, art. 1** (Légifrance, lu par un relais WebFetch, pas mot à mot) : accès direct des IPA dans les
  structures d'exercice coordonné ; expérimentation de 5 ans dans au plus 6 départements, dont 2 d'outre-mer ; rapport
  d'évaluation au moins 6 mois avant la fin.
- **Décret n° 2025-55 du 20 janvier 2025**, en vigueur le 22 janvier 2025 (FHF, source secondaire) : accès direct en
  établissement, centre de santé, maison de santé ; les IPA libéraux hors structure coordonnée en sont exclus.
- **Expérimentation en CPTS** : décret n° 2026-985 et arrêté du 23 octobre 2026 (presse ; JO non lu) ; six territoires
  (Loiret, Hérault, Val-d'Oise, Yonne, Martinique, Mayotte) ; début le 1er décembre 2026 ; collecte annuelle par les ARS.
- **Stock** : 3 973 IPA diplômés, toutes mentions (recensement Unipa, janvier 2026, cité par la presse). Ce sont des
  diplômés, pas des IPA en exercice libéral ; aucun effectif DREES ou ONI trouvé.
- **Codes IPA dans Open DAMIR** (descriptif 2024, `PRS_NAT`) : 1654 « FORFAIT IPA » (IEX), 3129 « PRATIQUE AVANCEE
  INFIRMIER MIP », 3130 « PRATIQUE AVANCEE INFIRMIER PAI ». Aucun code ni variable ne distingue l'**accès direct**
  (le parcours de soins `PRS_PDS_QCP` concerne les médecins). *[Corrigé après relecture : la première version disait
  « aucun code d'acte IPA ».]* Aucun volume publié par la Cnam.

## Par paramètre
| Paramètre | Statut | Raison |
|---|---|---|
| `a` | non mesurable | aucune source sur la part des consultations de MG relevant du périmètre IPA (suivi de pathologies chroniques stabilisées) |
| `k` | non mesurable | aucune durée comparée de consultation IPA et MG |
| `s_∞`, `τ` | non mesurables | aucun volume **en accès direct** ; l'expérimentation CPTS ne produit rien avant 2027. Le volume global d'actes IPA (codes 1654, 3129, 3130) se mesure dans DAMIR : c'est une borne haute de l'activité en accès direct, pas `s(t)` |
| `m` | non mesurable | rien de publié |

## Usage
Hors modèle, ou entièrement « supposé ». Point de reprise : rapport annuel des ARS sur l'expérimentation CPTS (2027 au
plus tôt). Série DAMIR des codes IPA (axe 4, ~0 coût de plus dans la lecture en flux) comme borne haute.
