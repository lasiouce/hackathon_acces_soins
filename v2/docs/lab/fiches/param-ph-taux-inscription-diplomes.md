---
type: fiche
axe: 1
id: param-ph-taux-inscription-diplomes
parametre: "ε_PH — taux d'« évaporation » : diplômés en pharmacie qui ne s'inscrivent pas à l'Ordre dans les 3 ans"
profession: pharmaciens
module: abandon
valeur: "32,8 % (2015)"
unite: "1 − nouveaux inscrits diplômés depuis < 3 ans / numerus clausus de l'année t−6"
incertitude: "fort : 27,8 % en 2014, entre 10 et 26 % sur 2006-2013 ; aucune valeur récente vérifiée (une valeur de presse de 26 %, non datée, n'est pas retenue)"
source: "Ordre national des pharmaciens, Éléments démographiques 2016 (données 2015), p. 7 — https://www.ordre.pharmacien.fr/mediatheque/fichiers/les-autres-publications/reprise-ancien-site/elements-demographique-ancien-site/panorama-1er-janvier-2016/demographie-2015_brochure-vdef.pdf"
millesime: "2015"
statut: sourcé
relecture: "2026-11-15 : confirmé"
date: 2026-11-14
---

# ε_PH — diplômés non inscrits

**Mécanisme.** Les diplômés en pharmacie ne sont pas tous tenus de s'inscrire
à l'Ordre : une partie de l'industrie, de la recherche et des postes hors PUI
en est dispensée. Ils sortent du stock observé (RPPS = inscrits) sans sortir
nécessairement du secteur privé. ε relie les places de formation aux entrées
observées : E_PH(t) = (1 − ε) · NC(t−6), en ordre de grandeur.

**Valeur.** En 2015, 2 076 nouveaux inscrits pour un numerus clausus de 3 090
six ans plus tôt, soit 32,8 % d'« évaporation » (*cité*). Une enquête de 2015
auprès de 540 non-inscrits montre que 31 des 168 diplômés thésés occupaient
un poste sans obligation d'inscription (*cité*).

**Mesure.**
- Recalculer ε avec la série DREES des inscrits en 6e année (fichier local
  `data/raw/Données pharma 2ème et 3ème cycle.xlsx`, 2020-2026) et les
  primo-inscrits de l'Ordre (3 044 en 2025).
- Le PDF de l'Ordre *Projections démographiques 2050* annonce un « taux
  d'inscription des diplômés » calibré. Il n'a pas pu être ouvert : à reprendre.
- ⚑ Ce taux mélange abandon, non-inscription et décalage temporel. Pour le
  « libéral » v2, l'industrie non inscrite est du privé **non observé** :
  le stock privé réel est sous-estimé d'autant.

## Relecture en texte intégral (2026-11-15)

Verdict : **confirmé** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- 32,8 % = 2 076 inscrits diplômés depuis moins de 3 ans / 3 090 (numerus clausus de t − 6), confirmé (Éléments 2016, p. 6-7).
