---
type: fiche
axe: 1
id: param-ide-regul-regle
parametre: "R_IDE — règle de conventionnement en zone sur-dotée (succession seule) et règle des deux tiers en périphérie"
profession: infirmiers
module: régulation
valeur: "en zone sur-dotée : entrées conventionnées ≤ cessations définitives (1 pour 1) ; en zone intermédiaire ou très dotée en périphérie : ≥ 2/3 de l'activité dans la zone d'installation"
unite: "règle (on/off par commune) ; part d'activité"
incertitude: "zones sur-dotées = 27,4 % de la population et 13,7 % des communes (zonage au 20/10/2026, dérivé) contre 28,4 % de cible nationale ; avenant 11 (signé le 31/03/2026, encadrement des remplaçants en zones denses) non vérifié ; dérogations (art. 3.4.2) non quantifiées"
source: "Avenant n° 6 à la convention nationale des infirmiers, signé le 29/03/2019, avis NOR SSAS1916881V, JORF n° 0135 du 13/06/2019, texte 128 — https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038599882 (texte intégral : https://bretagne.paps.sante.fr/media/62292/download), art. 3.4 et 3.4.4 ; zonage : data.gouv.fr, « Zonages des professionnels de santé libéraux » (Atlasanté/DataSanté), fichier t-zonages-com.csv — https://www.data.gouv.fr/datasets/zonages-des-professionnels-de-sante-liberaux"
millesime: "avenant 2019 ; zonage par commune mis à jour le 20/10/2026"
statut: sourcé
date: 2026-11-14
---

# R_IDE — régulation de l'installation des infirmiers

**Mécanisme.**
- En zone **sur-dotée**, le conventionnement n'est accordé qu'à une
  infirmière qui succède à une consœur cessant définitivement son activité
  dans la zone (art. 3.4).
- En zone **intermédiaire ou très dotée en périphérie** d'une zone
  sur-dotée, un nouvel installé doit réaliser les deux tiers de son
  activité dans sa zone d'installation (art. 3.4.4).
- Dans le jumeau, pour chaque commune c régulée :
  E_IDE,lib(c, t) ≤ X_IDE,lib(c, t).
- Le surplus va vers ψ ([[param-regul-report-entrants]]).

**Zones** (5 niveaux par bassin de vie ou pseudo-canton, indicateur APL ;
cibles nationales de l'avenant, art. 3.2.1) :
| Zone | Cible (population) |
|---|---|
| Très sous-dotée | 5 % |
| Sous-dotée | 9,5 % |
| Intermédiaire | 36,8 % |
| Très dotée | 20,4 % |
| Sur-dotée | 28,4 % |

- **Zonage observé.** Colonne `zide` du fichier par commune : 27,4 % de la
  population et 13,7 % des communes en zone sur-dotée (*dérivé*, 35 002
  communes, 68,9 M d'habitants). Convention de comptage : Paris, Lyon et Marseille sont comptées par arrondissement. Avec les seules communes, on obtient IDE 26,1 %, MK 24,4 %, CD 2,2 % (73 communes).
- **Historique.** Expérimentée en 2008-2009, généralisée en 2012 (IRDES
  QES 270, p. 2 et 5). *[Corrigé le 2026-11-14 après audit en texte intégral : voir [[2026-11-14-audit-sources]].]* L'effet
  mesuré sur 2006-2016 est dans [[param-ide-regul-effet-densite]].
- **Méthode du zonage.** Arrêté de méthodologie du 10/01/2020, cité par
  les ARS et non ouvert. Le zonage est arrêté par le DG de l'ARS
  (art. L.1434-4 CSP).

**Mesure et levier.**
- Levier : on/off par profession × liste de géocodes. Par défaut : le
  zonage du fichier data.gouv.
- Mesure de contrôle : nombre d'installations en zone sur-dotée / nombre
  de cessations dans ces zones, par an. Il doit être ≤ 1, hors dérogations.

**Géocodes (axe 4).** [[data-zonage-ide]] : liste des communes en « remplacement seul », extraite de CartoSanté. Le nombre concorde avec le fichier data.gouv (à ±10 communes près).
