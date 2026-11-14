---
type: fiche
axe: 1
id: param-ide-regul-effet-densite
parametre: "β_IDE — effet de la régulation du conventionnement en zone sur-dotée sur la densité d'infirmiers libéraux"
profession: infirmiers
module: régulation
valeur: "−25,57 IDEL pour 100 000 hab. (zones sur-dotées comparées aux zones intermédiaires, après 2012) ; −18,8 chez les moins de 40 ans"
unite: "écart de densité (IDEL / 100 000 hab.), différence de différences"
incertitude: "p < 0,001, intervalle non relevé ; borne haute de l'effet net national, car les zones témoins (intermédiaires) reçoivent probablement le report ; zonage de 2011, données 2006-2016 : rien de chiffré après l'avenant 6 (2019)"
source: "IRDES, Questions d'économie de la santé n° 270 (2022), Duchaine, Chevillard, Mousquès, p. 5 — https://www.irdes.fr/recherche/questions-d-economie-de-la-sante/270-inegalites-territoriales-de-repartition-des-infirmieres-liberales.pdf"
millesime: "données 2006-2016, publication 2022"
statut: sourcé
date: 2026-11-14
---

# β_IDE — effet mesuré de la régulation infirmière

**Mécanisme.**
- Depuis la généralisation de 2012 (expérimentation dès 2008-2009), une infirmière libérale ne peut se conventionner en zone
  sur-dotée qu'en succédant à un départ.
- Le flux d'installation y est donc plafonné par les sorties.
- β mesure ce que ce plafond a changé à la densité, par rapport à des zones
  comparables non régulées.

**Valeur** (*citée*, différence de différences avec appariement exact :
396 zones traitées et 454 témoins, p. 4 ; effets p. 5). *[Corrigé le 2026-11-14 après audit en texte intégral : voir [[2026-11-14-audit-sources]].]*
| Contraste | Effet | Signif. |
|---|---|---|
| Sur-dotées comparées aux intermédiaires, IDEL total | −25,57 / 100 000 hab. | p < 0,001 |
| Sur-dotées comparées aux intermédiaires, IDEL < 40 ans | −18,8 / 100 000 hab. | p < 0,001 |
| Très sous-dotées comparées aux intermédiaires (incitations), total / < 40 ans | +4,31 / +4,25 | p < 0,01 / p < 0,001 |
| Sur-dotées comparées aux intermédiaires, actes AMI / AIS par hab. | −0,66 / −0,35 | p < 0,001 |

L'écart de densité entre zones très sous-dotées et zones sur-dotées a
été réduit « de moitié » entre 2006 et 2016 (*cité*, descriptif).

Repères avant/après, *secondaires* (point d'information Cnam du 05/04/2012,
connu seulement par la presse) :
- zones sur-dotées : effectifs IDEL −3 % sur 2008-2011 (−263 ou −283 selon
  la reprise) ;
- zones très sous-dotées : +33,5 % (de 1 056 à 1 410), contre +15,6 %
  au niveau national.

**Mesure et usage dans le jumeau.**
- La règle « entrées ≤ sorties » se code directement (voir la fiche texte
  [[param-ide-regul-regle]]). β ne doit **pas** s'y ajouter : il sert de
  **test de validation** (axe 3, niveau 3).
- Le jumeau, rejoué sur 2006-2016 avec le zonage de 2011, doit reproduire un
  écart de l'ordre de −25 / 100 000 entre zones sur-dotées et intermédiaires.
  S'il trouve 0 ou plus de −50, le module régulation est falsifié.
- ⚑ Les témoins absorbent le report. On ne peut donc pas lire −25,57 comme
  « −25,57 installations perdues au niveau national ».

**Mesure propre au projet (axe 3, N3).** −30 % [−34 ; −26] de densité
relative, zones sur-dotées comparées aux intermédiaires, 2012-2019. Le
module n'est **pas validé** : le test de tendances parallèles échoue,
p = 0,043. Voir [[param-regul-theta-fuite]].
