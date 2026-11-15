---
type: fiche
axe: 1
id: param-ph-part-privee-etablissements
parametre: "s_H — part privée des pharmaciens de la section H (établissements de santé, PUI)"
profession: pharmaciens
module: transitions
valeur: "28,6 % des inscriptions H (2025 : 2 548 privé / 6 376 public) ; 30,0 % des postes en PUI (2 427 / 5 659 + 2 427)"
unite: "part des inscriptions (ou des postes) de la section H"
incertitude: "±2 points selon le dénominateur (inscriptions 8 924 > 8 106 personnes inscrites en H : multi-inscriptions) ; 2015 : 36 % hors emploi public"
source: "Ordre national des pharmaciens, Panorama 2025, dépliant — https://www.ordre.pharmacien.fr/mediatheque/fichiers/demographie-2025-depliant-fr%20 ; Synthèse 2024 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/demographie-2024-synthese ; Éléments démographiques 2016 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/les-autres-publications/reprise-ancien-site/elements-demographique-ancien-site/panorama-1er-janvier-2016/demographie-2015_brochure-vdef.pdf"
millesime: "au 1er janvier 2026 ; au 1er janvier 2025 ; 2015"
statut: sourcé
relecture: "2026-11-15 : corrigé (libellés, une ligne)"
date: 2026-11-14
---

# s_H — pharmacie hospitalière : part privée

**Mécanisme.** Les pharmaciens de PUI travaillent soit en clinique ou en
établissement privé, lucratif ou non (« libéral » v2), soit à l'hôpital public
(exclu). s_H ventile la section H et le flux φ_H.

**Valeur.** Les chiffres ci-dessous sont *cités* ; les parts sont *dérivées*.
| | 2015 | 2024 | 2025 |
|---|---|---|---|
| Inscriptions H, privé / public | 36 % / 64 % | 2 205 / 5 754 (27,7 %) | 2 548 / 6 376 (28,6 %) |
| Postes en PUI, privé / public | 2 377 / 4 202 (36,1 %) | 2 370 / 5 161 (31,5 %) | 2 427 / 5 659 (30,0 %) |

**Mesure.** Relever chaque année le tableau « H par type d'établissement ».
⚑ Une personne peut avoir plusieurs inscriptions : on prend la part, pas le
nombre. La part privée **baisse** d'environ 0,7 point/an depuis 2015
(*dérivé*) : une tendance plutôt qu'une constante.

**⚑ Conflit de sources (ouvert).** L'axe 4 trouve 17 % de privé pour les
pharmaciens hospitaliers (DREES : salariés d'ESPIC et du secteur lucratif),
contre 28,6 % ici (Ordre, inscriptions de la section H). Le ledger tranchera.
Les deux se défendent :
- l'Ordre compte des inscriptions, avec des doubles inscriptions ;
- la DREES compte des personnes et classe les ESPIC à part.

Défaut proposé pour le jumeau : la DREES, puisque le stock vient du RPPS
DREES. L'Ordre sert de borne haute.

## Relecture en texte intégral (2026-11-15)

Verdict : **corrigé (libellés, une ligne)** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- Valeurs confirmées : 2 548 / 6 376 = 28,6 % ; 2 427 / 8 086 = 30,0 % ; 2 370 / 5 161 (2024).
- **Unités** : 8 924 inscriptions (H et E-PUI, comptées par fonction) > 8 106 inscriptions H (principales et secondaires) > 7 817 personnes. « 8 106 personnes » est faux. Les sommes 2025 et 2024 ne se comparent pas (rupture de définition).
- « Postes en PUI » : ce sont des fonctions de pharmaciens exerçant en PUI ; un pharmacien peut en cumuler plusieurs.
- **Ligne 2015 « Inscriptions H 36 % / 64 % »** : doublon de la ligne PUI 2015 (2 377 / 4 202 = 36,1 %). Il n'existe pas de répartition des inscriptions H en 2015. Comparer sur la ligne PUI seule : 36,1 % → 31,5 % → 30,0 %, soit environ −0,6 point par an.
