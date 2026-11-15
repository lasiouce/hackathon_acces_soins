---
type: fiche
axe: 1
id: param-besoin-activite-etp
parametre: "q_p — activité d'un ETP (conversion du besoin en actes ou en honoraires vers des ETP-équivalents)"
profession: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
module: besoin (M1–M3 en ETP ; M4 offre S_j)
valeur: "convention APL : 1 ETP = activité libérale médiane de la profession ; la médiane elle-même n'est pas publiée (non mesurable en données ouvertes) ; bornes : IDE, CD 10 000 € d'honoraires sans dépassement ; MK nombre d'actes équivalent à 10 000 € ; SF 5ᵉ centile ; plafond 90ᵉ centile pour les quatre ; pharmaciens : aucune convention"
unite: "IDE, CD, SF : honoraires sans dépassement (€ / an) ; MK : actes / an"
incertitude: "convention, pas une mesure de temps de travail ; médiane inconnue ; un substitut ouvert (honoraires / effectif, data.ameli.fr) donne une moyenne, pas une médiane, et inclut les très petites activités"
source: "DREES, jeu 530 APL, fichiers xlsx IDE, MK, CD, SF, onglet « Paramètres », bloc « Comptabilisation de l'activité » et sa note ; Lisez-moi APL, p. 3, points 2 et 3 — https://data.drees.solidarites-sante.gouv.fr/explore/dataset/530_l-accessibilite-potentielle-localisee-apl/"
millesime: "méthode des fichiers 2022-2024 (racine du jeu) ; activité SNIIR-AM 2024 pour l'APL 2024"
statut: "convention sourcée ; valeur non mesurable"
date: 2026-11-15
---

# q_p — activité d'un ETP

**Rôle.** Le besoin M1 sort en actes (ou en euros) par an. Pour le comparer à un effectif, on divise par `q_p`,
l'activité d'un ETP. M4 (2SFCA) mesure aussi l'offre `S_j` en ETP. Dérivation §6 : « En ETP : `B₁ / q_p` ».

## Ce que publie la DREES (cité, onglet « Paramètres » de chaque fichier)

| Profession | Mesure de l'activité | Plancher (activité comptée 0) | Plafond (activité tronquée) |
|---|---|---|---|
| IDE | honoraires sans dépassement, SNIIR-AM | « Moins de 10 000 euros » | 90ᵉ centile d'honoraires remboursables |
| CD | honoraires sans dépassement, SNIIR-AM | « Moins de 10 000 euros » | 90ᵉ centile |
| SF | honoraires sans dépassement, SNIIR-AM | « En dessous du 5ème percentile » | 90ᵉ centile |
| MK | **nombre d'actes**, SNIIR-AM | actes « correspondant à moins de 10 000 euros d'honoraires remboursables » | 90ᵉ centile du nombre d'actes |

- **Convention ETP** (citée, IDE ; même texte pour les autres) : « par convention, on fixe la valeur d'1 ETP au niveau
  de l'activité médiane des infirmières libérales et l'ETP de chaque infirmière libérale et de chaque centre de santé
  est calculé en rapportant son activité à l'activité libérale médiane. »
- **Exceptions** (citées) : un libéral sans activité libérale l'année précédente reçoit 1 ETP ; pour les centres de
  santé, « les bornes d'activité ne sont pas appliquées ».
- **Champ du calcul de la médiane** (Lisez-moi p. 3, point 3) : hors Mayotte, hors cabinets fermés en fin d'année,
  hors activité nulle, hors libéraux sans activité libérale l'année précédente.
- **Champ des professionnels** : libéraux de 65 ans ou moins et salariés des centres de santé.

## Ce qui manque
- **La valeur de la médiane n'est publiée nulle part** dans le jeu 530 (ni onglet, ni Lisez-moi). Seul repère
  numérique, pour les médecins généralistes : « une activité correspondant à 1 ETP (ou 5 400 consultations, visites et
  téléconsultations [...]) » était attribuée « auparavant » aux primo-installés (Lisez-moi p. 3, point 2). C'est
  l'ancienne règle d'imputation, et elle ne concerne pas les cinq professions.
- **Pharmaciens** : pas d'APL, donc pas de convention d'ETP.

## Statut : convention sourcée, valeur non mesurable
- Le **choix d'unité** est sourcé : on suit la DREES, 1 ETP = activité libérale médiane, avec les mêmes bornes.
- La **valeur** de `q_p` n'est pas observable en données ouvertes. Conséquences :
  1. un **indice relatif** (`C = (N/B)/(N/B)₂₀₂₆`) ne dépend pas de `q_p`, qui s'élimine du rapport. M0 et M1 en indice
     n'en ont pas besoin ;
  2. une sortie en **ETP absolus** exige `q_p`. Substitut possible : honoraires sans dépassement totaux / effectif
     libéral (data.ameli.fr, « PS libéraux : honoraires », ODbL). C'est une **moyenne** sur tous les libéraux, pas la
     médiane du champ APL : à étiqueter « dérivé, substitut », ledger ;
  3. M4 (P-B4) : l'écart principal attendu dans la reproduction de l'APL vient de là (exploration besoin §3).
- Les seuils de 10 000 € et de 90ᵉ centile sont cités pour le **troncage**, pas comme valeur de `q_p`.
