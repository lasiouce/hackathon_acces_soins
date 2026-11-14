---
type: fiche
axe: 1
id: param-cd-regul-regle
parametre: "R_CD — conventionnement des dentistes en zone « non prioritaire » seulement en succession"
profession: dentistes
module: régulation
valeur: "en zone non prioritaire : entrées conventionnées ≤ cessations (1 pour 1 ; cédant ≥ 2 jours par semaine ; successeur désigné sous 1 an) ; effet au plus tôt le 01/01/2025"
unite: "règle (on/off par commune)"
incertitude: "zones non prioritaires = 4,8 % de la population et 0,3 % des communes (zonage au 20/10/2026, dérivé ; cible : 5 %) ; transposition aux centres de santé dentaires non vérifiée ; spécialistes (ODF, CO, MBD) exemptés"
source: "Convention nationale des chirurgiens-dentistes, signée le 21/07/2023, arrêté du 23/08/2023, NOR SPRS2323014A, JO du 25/08/2023, texte 30, art. 33.1 et 35 — https://bretagne.paps.sante.fr/media/42626/download ; guide de zonage ARS PACA (mise en place au 01/01/2025) — https://www.paca.ars.sante.fr/media/139787/download ; zonage : data.gouv.fr, « Zonages des professionnels de santé libéraux » (Atlasanté/DataSanté), fichier t-zonages-com.csv — https://www.data.gouv.fr/datasets/zonages-des-professionnels-de-sante-liberaux"
millesime: "convention 2023, effet au 01/01/2025 ; zonage par commune mis à jour le 20/10/2026"
statut: sourcé
date: 2026-11-14
---

# R_CD — régulation de l'installation des dentistes

**Mécanisme.**
- En zone **non prioritaire**, le conventionnement n'est accordé qu'au
  successeur désigné d'un dentiste qui cesse son activité (art. 35).
- Le cédant doit avoir au moins 2 jours d'activité par semaine ; le
  successeur doit être désigné dans un délai d'1 an.
- Dans le jumeau : E_CD,omni,lib(c, t) ≤ X_CD,lib(c, t) pour c non
  prioritaire.
- **Les spécialistes en sont exemptés** (MBD, CO, ODF ; art. 35.5).

**Zones** (5 niveaux par territoire de vie-santé, art. 33.1).
| Zone | Cible (population) |
|---|---|
| Très sous-dotée | 30 % |
| Sous-dotée | 15 % |
| Intermédiaire | 35 % |
| Très dotée | 15 % |
| Non prioritaire | 5 % |

- Zonage observé (colonne `zdent`) : 4,8 % de la population, 0,3 % des
  communes en zone non prioritaire (*dérivé*).
- Méthode : arrêté du 20/03/2024.

**Pas d'obligation d'exercice de 2 ans pour les dentistes**, contrairement
à la note de cadrage (voir [[param-mk-obligation-exercice]]).
L'effet est dans [[param-cd-regul-effet]].

**Géocodes (axe 4).** [[data-zonage-cd]] : liste des communes en « remplacement seul », extraite de CartoSanté. Le nombre concorde avec le fichier data.gouv (à ±10 communes près).
