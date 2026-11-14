---
parametre: part_privee_secteur_mixte
profession: SF;CD;PH;MK
module: etat (secteur)
valeur: "centres de santé 0,798 ; dont dentaires 0,963 ; PMI 0,070 ; EHPAD 0,558 ; handicap médicalisé 0,866"
unite: fraction d'établissements à statut juridique privé
incertitude: "part en établissements, pas en salariés (non mesuré) ; bornes 0 et 1 conservées dans secteur_split"
source: "FINESS, extraction établissements (etalab-cs1100502) et entités juridiques (cs1100501), data.gouv.fr"
millesime: "2026-05-04 (mis en ligne 2026-05-12)"
statut: mesuré
---

# Part privée des secteurs mixtes (FINESS)

Statut juridique FINESS de l'entité juridique : 01–39 public ; 40–46 organismes de sécurité sociale, comptés
publics ; 47–99 privé (mutuelles, associations, fondations, sociétés).

| Proxy | Établissements | Part privée |
|---|---|---|
| centre_sante | 3395 | 0.798 |
| pmi | 1435 | 0.070 |
| ehpad | 7399 | 0.558 |
| handicap | 6008 | 0.866 |
| medico_social | 13407 | 0.696 |
| centre_sante_dentaire | 1299 | 0.963 |

Catégories : centre de santé 124 ; PMI et planification 223, 228 ; EHPAD 500 ; handicap médicalisé 182, 183,
186, 190, 255, 437, 448. « Dentaires » = raison sociale contenant « DENT ». Script : `v2/data/build_secteur.py`.
