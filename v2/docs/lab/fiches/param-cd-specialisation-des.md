---
type: fiche
axe: 1
id: param-cd-specialisation-des
parametre: "σ_CD,s — part d'une promotion d'odontologie qui entre dans un DES (ODF, chirurgie orale, médecine bucco-dentaire)"
profession: dentistes
module: filières
valeur: "≈ 9,2 % d'une promotion (2024 : 121 postes / 1 322 places en 2e année 4 ans plus tôt) ; répartition 2024-25 : ODF 52 (43 %), CO 25 (21 %), MBD 44 (36 %)"
unite: "postes de DES / places en 2e année (t−4) ; part par DES"
incertitude: "dérivé (décalage de 4 ans supposé) ; postes ouverts ≠ pourvus (MBD 2018 : 36 / 42) ; ventilation par DES manquante pour 2012-2017 et 2020-2023 ; 2026-27 : 51 / 39 / 50 = 140 (source secondaire) ; réforme proposée (IGAS-IGÉSR 2025 : 5 DES de 4 ans)"
source: "Arrêté du 15/05/2024, NOR TSSH2411796A, JORF n° 115 du 18/05/2024, texte 18 — https://cng.sante.fr/sites/default/files/media/2024-05/Arr%C3%AAt%C3%A9%20du%2015_mai_2024_offres%20de%20postes%20Odonto%20National%202024-2025.pdf ; arrêté du 20/02/2023, NOR SPRH2304784A, JORF n° 47 du 24/02/2023 ; CNG, Statistiques 2018 Internats, tableaux 20 et 23 — https://cng.sante.fr/sites/default/files/media/2022-03/2018_Internats.pdf ; places en 2e année : L'Étudiant (15/05/2020), QE AN n° 13528 (16e législature)"
millesime: "postes 2008-2024 (détail par DES : 2018, 2023, 2024)"
statut: sourcé
date: 2026-11-14
---

# σ_CD — spécialisation en odontologie

**Mécanisme.**
- En fin de 5e année, une petite part de chaque promotion entre à
  l'internat, dans un DES de 3 ans (4 ans pour la chirurgie orale).
- Le reste exerce comme omnipraticien.
- σ sépare deux sorties du module formation :
  - les spécialistes, **exemptés** de la régulation
    ([[param-cd-regul-regle]]) ;
  - les omnipraticiens, régulés.
- Le levier est le nombre de postes de DES.

**Valeur.** Postes au concours national, hors postes à titre européen :
| Année | ODF | CO | MBD | Total | Statut |
|---|---|---|---|---|---|
| 2008-2011 (ancien internat) | – | – | – | 40-45 | cité (CNG) |
| 2012 / 2014 / 2016 / 2017 | ? | ? | ? | 91 / 110 / 109 / 111 | cité (CNG) |
| 2018 | 52 | 16 | 42 (36 pourvus) | 110 | cité (CNG, tab. 20) |
| 2023-24 | 52 | 24 | 44 | 120 | cité (arrêté) |
| 2024-25 | 52 | 25 | 44 | 121 | cité (arrêté) |
| 2026-27 | 51 | 39 | 50 | 140 | secondaire (presse) |

- Part d'une promotion (*dérivée*) : 9,1 % (2023), 9,2 % (2024), 9,7 %
  (2026).
- Contrôle local : 110 à 123 internes en 1re année sur 2020-2026
  (*mesuré*, `data/raw/Données odontologie 2ème et 3ème cycle.xlsx`). Le
  fichier n'a pas de détail par DES.

**Mesure.**
- Arrêté annuel du CNG (JORF).
- Pour la série 2019-2022 et 2025, Légifrance bloque le téléchargement
  automatique : à relever à la main (ledger).
