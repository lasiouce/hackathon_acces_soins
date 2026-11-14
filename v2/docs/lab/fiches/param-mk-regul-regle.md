---
type: fiche
axe: 1
id: param-mk-regul-regle
parametre: "R_MK — conventionnement des kinés en zone « non prioritaire » seulement en succession d'une cessation"
profession: kines
module: régulation
valeur: "en zone non prioritaire : entrées conventionnées ≤ cessations définitives (1 pour 1 ; cédant ≥ 1 200 actes l'année précédente ; successeur désigné sous 2 ans)"
unite: "règle (on/off par commune)"
incertitude: "zones non prioritaires = 26,5 % de la population et 8,1 % des communes (zonage au 20/10/2026, dérivé) contre une cible de 30 % ; écart avec le mémoire EHESP (3,6 % des communes) non expliqué ; 14 communes encore classées sur-dotée ou très dotée (reliquats d'anciens arrêtés)"
source: "Avenant n° 7 à la convention nationale des masseurs-kinésithérapeutes, conclu le 13/07/2023, arrêté d'approbation du 21/08/2023, NOR SPRS2322893A, JO du 25/08/2023, texte 28, art. 1.2.1 et annexe 3 — https://bretagne.paps.sante.fr/media/41875/download ; Conseil d'État, 17/07/2024, n° 488665 (recours rejetés) — https://www.conseil-etat.fr/fr/arianeweb/CE/decision/2024-07-17/488665 ; zonage : data.gouv.fr, « Zonages des professionnels de santé libéraux » (Atlasanté/DataSanté), fichier t-zonages-com.csv — https://www.data.gouv.fr/datasets/zonages-des-professionnels-de-sante-liberaux"
millesime: "avenant 2023 ; zonage par commune mis à jour le 20/10/2026"
statut: sourcé
date: 2026-11-14
---

# R_MK — régulation de l'installation des kinés

**Mécanisme.**
- En zone **non prioritaire**, le conventionnement ne vaut que pour la
  « succession d'un confrère cessant définitivement son activité »
  (art. 1.2.1).
- Le cédant doit avoir réalisé au moins 1 200 actes l'année précédente ;
  le successeur doit être désigné dans les 2 ans.
- La règle vaut aussi pour l'exercice exclusif à domicile.
- Dans le jumeau : E_MK,lib(c, t) ≤ X_MK,lib,actifs(c, t).

**Zones** (4 niveaux, annexe 3 ; marge ARS de ±2,5 %).
| Zone | Cible (population) |
|---|---|
| Très sous-dotée | 15 % |
| Sous-dotée | 15 % |
| Intermédiaire | 40 % |
| Non prioritaire | 30 % |

- Zonage observé (colonne `zmk`) : 26,5 % de la population, 8,1 % des
  communes en zone non prioritaire (*dérivé*).
- Méthode : arrêté du 20/03/2024, qui modifie celui du 24/09/2018.

**Historique.** Une régulation de 2012 a été annulée par le Conseil d'État
en 2014. Celle de 2023 a été validée par le Conseil d'État (17/07/2024).
Obligation d'exercice associée : [[param-mk-obligation-exercice]].

**Géocodes (axe 4).** [[data-zonage-mk]] : liste des communes en « remplacement seul », extraite de CartoSanté. Le nombre concorde avec le fichier data.gouv (à ±10 communes près).
