---
type: fiche
axe: 1
id: param-sf-regul-regle
parametre: "R_SF — conventionnement des sages-femmes en zone sur-dotée seulement après une cessation"
profession: sages-femmes
module: régulation
valeur: "en zone sur-dotée : entrées conventionnées ≤ cessations d'activité conventionnée (1 pour 1)"
unite: "règle (on/off par commune)"
incertitude: "zones sur-dotées = 12,2 % de la population et 4,2 % des communes (zonage au 20/10/2026, dérivé) contre 12,5 % de la population féminine dans l'avenant 4 ; origine 2012 (avenant 1) vue seulement en source secondaire ; avenant 7 (2023) non lu au JO ; dérogations larges, non quantifiées"
source: "Avenant n° 4 à la convention nationale des sages-femmes, signé le 29/05/2018, avis NOR SSAS1822073V, JORF n° 0183 du 10/08/2018, texte 100, art. 3.3 — https://www.legifrance.gouv.fr/jorf/id/JORFSCTA000037306865 ; avenant 7 (signé le 11/07/2023, JO du 25/08/2023), d'après l'ONSSF — https://onssf.org/images/flash-info/pdf/2023/aout-2023-avenant-7-3.pdf ; zonage : data.gouv.fr, « Zonages des professionnels de santé libéraux » (Atlasanté/DataSanté), fichier t-zonages-com.csv — https://www.data.gouv.fr/datasets/zonages-des-professionnels-de-sante-liberaux"
millesime: "avenant 2018 (règle reconduite en 2023) ; zonage par commune mis à jour le 20/10/2026"
statut: sourcé
relecture: "2026-11-15 : corrigé (mécanisme omis)"
date: 2026-11-14
---

# R_SF — régulation de l'installation des sages-femmes

**Mécanisme.**
- En zone sur-dotée, le conventionnement est accordé « uniquement si une
  autre sage-femme a préalablement mis fin » à son activité conventionnée
  dans la zone (avenant 4, art. 3.3.2).
- Dans le jumeau : E_SF,lib(c, t) ≤ X_SF,lib(c, t) pour c sur-dotée.

**Dérogations** (art. 3.3.3).
- Motifs de vie personnelle.
- Accompagnement global de la grossesse.
- Réduction d'activité d'au moins 50 % pendant 2 ans.
- Les échographistes sont exclues de la régulation.

Ces dérogations rendent la contrainte « molle » : un taux de dérogation est
à paramétrer. Il n'est **pas mesuré** (ledger).

**Zones.**
- 5 niveaux.
- Zonage observé (colonne `zsf`) : sur-dotées = 12,2 % de la population,
  4,2 % des communes (*dérivé*). Convention de comptage : Paris, Lyon et Marseille sont comptées par arrondissement. Avec les seules communes, on obtient IDE 26,1 %, MK 24,4 %, CD 2,2 % (73 communes).
- Méthode : arrêté du 17/10/2019, modifié le 26/03/2024 (cités par les ARS).
- Le zonage est arrêté par le DG de l'ARS, pour 2 ans au plus.

**Historique.** Un dispositif existe depuis 2012 (avenant signé le
09/01/2012, source secondaire : Banque des Territoires). La règle est
reconduite en substance par l'avenant 7, applicable le 22/02/2024 selon
l'ONSSF.

**Géocodes (axe 4).** [[data-zonage-sf]] : liste des communes en « remplacement seul », extraite de CartoSanté. Le nombre concorde avec le fichier data.gouv (à ±10 communes près).

## Relecture en texte intégral (2026-11-15)

Verdict : **corrigé (mécanisme omis)** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- Règle générale 1 pour 1 confirmée (art. 3.3.2 c). **Ajout** : pour les entrées dérogatoires au titre de la vie personnelle ou d'une réduction d'activité ≥ 50 % (art. 3.3.3 a et b), la cessation suivante n'ouvre pas de nouveau conventionnement, sauf successeur désigné. Pour la grossesse (3.3.3 c et d), elle en ouvre un. Texte lu dans la reproduction JO (bretagne.paps), Légifrance étant bloqué. « Depuis 2012 » : ONSSF.
