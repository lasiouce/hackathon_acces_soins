---
type: fiche
axe: 1
id: param-besoin-tension-diabete
parametre: "Transfert — prise de tension et dépistage du diabète en officine (A = médecine générale ; B = pharmaciens) : a, k, s_∞, τ, m"
profession: [pharmaciens]
module: besoin (opérateur de transfert)
valeur: "non mesurable pour les cinq paramètres"
unite: "—"
incertitude: "aucun acte facturable connu au 2026-11-15 : pas de série de volumes, donc ni s(t) ni m ; texte d'autorisation de 2026 connu seulement par la presse"
source: "presse professionnelle (caducee.net n° 16957, sept. 2026 ; Le Quotidien du pharmacien) citant la loi n° 2026-668 du 27 juillet 2026 ; texte au JO non lu ; descriptif Open DAMIR 2024 (aucun code d'acte de mesure de tension ni de glycémie relevé)"
millesime: "2026"
statut: non mesurable
date: 2026-11-15
---

# Prise de tension et dépistage du diabète en officine

**Verdict : non mesurable** (`a`, `k`, `s_∞`, `τ`, `m`). Conforme à l'attendu du plan (axe 1) et à l'exploration du
2026-11-15.

## Ce qui a été lu
- **Autorisation de la mesure de tension.** Loi n° 2026-668 du 27 juillet 2026 (« stratégie nationale de lutte contre
  les maladies cardio-neuro-vasculaires ») : le pharmacien d'officine peut « mesurer la pression artérielle de patients
  dans une démarche de prévention des risques cardio-neuro-vasculaires » (caducee.net n° 16957, **presse citant le
  texte** ; JO non lu, article du CSP non confirmé).
- **Rémunération : non fixée.** La FSPF demande 15 € par mesure (même article, revendication, pas un tarif). Sans tarif,
  pas d'acte facturé, donc pas de volume dans le SNDS ni dans Open DAMIR.
- **Glycémie capillaire.** Selon un extrait du Quotidien du pharmacien (mai 2026, non lu en entier) : les tests « ne
  peuvent être réalisés » dans l'attente d'une négociation avec l'Assurance maladie. L'avenant n° 2 à la convention
  pharmaceutique (signé le 7 avril 2026 selon la presse) prévoit des négociations ; texte non lu (lien peps.sante.gouv.fr
  inaccessible).
- **Volumes ponctuels.** Expérimentation ARS PACA de 2011 (35 officines, forfait de 10 dépistages par mois, presse) ;
  campagne Giphar « près de 14 000 dépistages » (titre de presse, année inconnue, non lu). Ce sont des campagnes, pas
  une série de diffusion : elles ne donnent ni `s(t)` ni `a`.
- **Open DAMIR.** Le descriptif 2024 (onglet `PRS_NAT`) ne contient aucun code de mesure de tension ou de glycémie en
  officine parmi les codes relevés (3360 VGP, 3415 RVA, 3359 TROD angine…) : relevé partiel, à confirmer sur la liste
  complète.

## Par paramètre
| Paramètre | Statut | Raison |
|---|---|---|
| `a` | non mesurable | la part des consultations de MG consacrée à une mesure de tension ou à un dépistage glycémique n'est publiée nulle part (lecture faite) ; DAMIR ne code pas le motif de consultation |
| `k` | non mesurable | aucune durée d'acte en officine ni chez le MG |
| `s_∞`, `τ` | non mesurables | pas d'acte facturable, donc pas de série ; transposer L23 serait « supposé (transposé) » |
| `m` | non mesurable | rien sur les actes ajoutés |

## Usage
Le levier reste **hors modèle** ou, s'il est exposé, entièrement **supposé** : chaque valeur affichée porte l'étiquette
« supposé », et la sortie dit qu'aucune donnée ne l'appuie. Reprendre la fiche quand un tarif sera publié (code d'acte
dans DAMIR).
