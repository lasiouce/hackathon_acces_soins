---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: La pondération par l'âge (M1) change-t-elle l'indice de couverture de 2050 assez pour être gardée, par rapport à la population brute (M0) ?
headline: "(passage non lancé : écarts au protocole écrits avant calcul)"
status: draft
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B0 ; protocole gelé P-B1 (v2/validation/preregistered/2026-11-15-besoin-p-b1-age.md)
sources: [Omphale 2022 (Insee), poids APL DREES (DCIR 2021–2022), projection C1 du jumeau]
tags: [besoin, validation, P-B1]
---

# P-B1 — M1 contre M0 sur l'indice de couverture 2050 (passage)

> **Headline :** (à remplir après le passage)

## Écarts au protocole, écrits le 2026-11-15 avant tout calcul de M1
Le protocole est gelé (jetons RFC 3161 FreeTSA 02:17:19 UTC et DigiCert 02:17:20 UTC, le 2026-11-15). Ces choix
sont écrits et commités **avant** le passage ; aucun seuil n'est touché.

1. **P2 (profil Open DAMIR) absent.** La fenêtre DAMIR de l'axe 4 tourne encore. Règle appliquée : le protocole
   n'abandonne l'âge que si P1 **et** P2 concluent à l'abandon. Donc :
   - P1 conclut « retenu » ⇒ verdict **définitif « retenu »** (P2 ne peut pas le renverser) ;
   - P1 conclut « abandon » ⇒ verdict **en attente de P2** ;
   - pharmaciens (P2 seul) : **aucun verdict**, en attente de l'axe 4.
2. **Effectifs N.** « Projection servie du jumeau (C1, médiane des tirages) » : le service (`v2/prototype/server.py`,
   `Model`, C1 installé par `methodes.c1_jumeau.install`) sert une **trajectoire centrale déterministe**, pas une
   médiane de tirages. On prend celle-là : c'est ce qui est servi. Seul ρ dépend de N ; `C₁/C₀` n'en dépend pas.
3. **Tranches d'âge.** Omphale a 20 tranches (… 90–94, 95+), l'APL 19 (… 90+). Les tranches 90–94 et 95+ prennent
   toutes deux le poids « 90 et plus ».
4. **Colonnes de poids.** IDE, CD, SF : colonne 2024 (DCIR 2022) ; MK : colonne 2023 (DCIR 2021), faute de colonne
   2024 publiée (décision axe 1 du 2026-11-15, fiche `param-besoin-poids-age-apl`).
5. **Départements.** Jointure Omphale × jumeau ; un département où `C` n'est pas fini (effectif nul en 2026) n'a
   pas de valeur et sort de la jointure. Le nombre retiré est rapporté.
6. **Spearman** : `scipy.stats.spearmanr` si présent, sinon rangs moyens (égalités) puis Pearson des rangs ; même
   définition.
