---
type: fiche
axe: 1
id: param-cumul-emploi-retraite
parametre: "c_p — part des cotisants libéraux en cumul emploi-retraite"
profession: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
module: sorties
valeur: "SF 0,8 % (42 / 5 185) · CD 4,7 % (1 742 / 37 330) · PH 1,8 % (560 / 31 445) · MK + IDE 1,5 % (2 960 / 190 979, non séparables)"
unite: "part des cotisants de la caisse (libéraux)"
incertitude: "millésime ancien (30/06/2015) ; libéraux seulement (la CAVP sous-estime les pharmaciens salariés) ; la CARPIMKO mélange IDE, MK, podologues et orthophonistes ; parts dérivées des nombres cités"
source: "Conseil d'orientation des retraites, séance 2016, document n° 11, annexe 2 (données des caisses CARCDSF, CAVP, CARPIMKO) — https://www.cor-retraites.fr/sites/default/files/2019-06/doc-3265.pdf"
millesime: "30/06/2015"
statut: sourcé
relecture: "2026-11-15 : confirmé (valeurs) ; libellé corrigé"
date: 2026-11-14
---

# c_p — cumul emploi-retraite

**Mécanisme.**
- Un professionnel qui liquide sa retraite peut continuer d'exercer.
- c_p mesure ce stock « au-delà de la retraite ». Un levier
  (plafonnement, incitation) agit dessus.
- La DREES l'inclut dans le champ des actifs (< 70 ans).

**Valeur** (*citée* ; parts *dérivées*).
- Dentistes : la part la plus élevée (4,7 %).
- Sages-femmes : très faible (0,8 %).
- Repère médecins (phase 2) : environ 10 % des libéraux, qui cessent
  définitivement à 69,5 ans en moyenne (ER 1097, 2018).
- Repère régime CNAVPL, génération 1953 : âge moyen à la liquidation
  64,4 ans ; 20 % des départs entre 66 et 70 ans (DREES, *Retraités et
  retraites* 2025, fiche 16).

**Mesure.** Rapports annuels des caisses (CARCDSF, CAVP, CARPIMKO) ou mise
à jour du COR. Coût estimé : ~30 min pour un millésime récent.

## Relecture en texte intégral (2026-11-15)

Verdict : **confirmé (valeurs) ; libellé corrigé** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- Valeurs confirmées (COR 2016, doc. 11, annexe 2, au 30/06/2015) : 42 / 5 185, 1 742 / 37 330, 560 / 31 445, 2 960 / 190 979.
- **Libellé** : la CARPIMKO couvre MK, IDE, pédicures-podologues, orthophonistes et orthoptistes. Appliquer 1,5 % aux MK et aux IDE séparément est *supposé* (écart de dénominateur ≤ 0,2 point).
- Spécialistes (phase 2), 0,10 : l'ER 1097 donne « près de 10 % » de tous les médecins libéraux ou mixtes au 01/01/2018 ; la CARMF donne 8,6 % en 2015 (COR). L'application aux seuls spécialistes est *supposée*.
