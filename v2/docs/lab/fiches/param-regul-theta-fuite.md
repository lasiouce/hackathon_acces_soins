---
type: fiche
axe: 1
id: param-regul-theta-fuite
parametre: "θ_p — part contraignante du plafond « entrées ≤ sorties » (1 = plafond strict, 0 = aucun effet)"
profession: infirmiers
module: régulation
valeur: "0,80 [0,74 ; 0,87] (IDE, 2012-2019, exploratoire)"
unite: "sans dimension, β_observé / β_plafond strict"
incertitude: "exploratoire : le test de tendances parallèles pré-enregistré échoue (p = 0,043) ; valeur transmise comme supposée par l'axe 3 ; SF, MK, CD : aucune estimation → reprendre 0,80 en défaut, avec une plage de 0,5 à 1 pour l'axe 5"
source: "Axe 3, N3 (v2/docs/lab/reports/2026-11-14-axe3-n3-leviers-did.md) et décision du 2026-11-14 « Axe 3, N3 lancé » ; données : Atlasanté zonage c987d0e2 (génération 2012), effectifs IDE libéraux par commune"
millesime: "2004-2019"
statut: supposé
date: 2026-11-14
---

# θ — le plafond de régulation fuit-il ?

**Mécanisme.**
- Le module `regulation` du jumeau impose E ≤ X dans les zones régulées.
- Les dérogations, le remplacement et l'exercice en bordure font qu'une
  partie des entrées passe quand même.
- θ mélange le plafond et le laisser-faire :
  E = θ · min(E_libre, X) + (1 − θ) · E_libre.

**Valeur.**
- 0,80 [0,74 ; 0,87] pour les IDE, *supposé* : estimation exploratoire de
  l'axe 3, non validée.
- Cohérence avec l'IRDES ([[param-ide-regul-effet-densite]]) : même
  direction, ordre de grandeur compatible (−25,57 / 100 000 face à −30 % de
  densité relative selon l'axe 3). Les unités diffèrent : à rapprocher.

**Mesure.**
- Second test pré-enregistré de l'axe 3 (borne de Rambachan et Roth,
  contrôle synthétique).
- Pour SF et MK, même protocole sur leurs zonages.
