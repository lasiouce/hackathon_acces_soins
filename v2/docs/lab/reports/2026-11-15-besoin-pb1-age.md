---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: La pondération par l'âge (M1) change-t-elle l'indice de couverture de 2050 assez pour être gardée, par rapport à la population brute (M0) ?
headline: "P-B1 (P1 seul, sans Open DAMIR) : âge retenu pour IDE (S₁ = 0 %, ρ = 0,835), MK (0 %, 0,984) et SF (1 %, 0,989) ; dentistes en attente de P2 (S₁ = 93,1 %, ρ = 0,998, P1 conclut à l'abandon) ; pharmaciens sans verdict"
status: passage fait (P1) ; P2 en attente de l'axe 4
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B0 ; protocole gelé P-B1 (v2/validation/preregistered/2026-11-15-besoin-p-b1-age.md)
sources: [Omphale 2022 (Insee), poids APL DREES (DCIR 2021–2022), projection C1 du jumeau]
tags: [besoin, validation, P-B1]
---

# P-B1 — M1 contre M0 sur l'indice de couverture 2050 (passage)

> **Headline :** sous le profil APL (P1), l'âge change l'indice de couverture 2050 de plus de 2 % dans **tous** les
> départements pour les IDE et les MK, et dans 99 % pour les SF : **M1 est retenu** pour ces trois professions, et
> P2 ne peut pas le renverser. Pour les **dentistes**, P1 conclut à l'abandon (93,1 % des départements sous 2 %,
> ρ = 0,998) : verdict **en attente de P2** (Open DAMIR). **Pharmaciens** : aucun verdict (P2 seul, absent).

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

## Question
Le protocole gelé [P-B1](../../../validation/preregistered/2026-11-15-besoin-p-b1-age.md) teste H-B0 : la
structure par âge ne déplace pas l'indice de couverture indexé à 2026 de plus de 2 % dans la plupart des
départements. Il décide si M1 vaut son coût par rapport à M0, profession par profession
([dérivation §6, M1](../derivations/2026-11-15-besoin-derivation.md)).

## Result
Décisif : 2050, scénario Omphale central, profil P1 (poids APL). Seuils gelés : abandon si `S₁ > 0,90` et `ρ ≥ 0,98`.
Tous les nombres sont **mesurés** (calcul déterministe), sauf les seuils (supposés au gel).

| Profession | n dép. | S₁ (part \|C₁/C₀ − 1\| < 2 %) | ρ Spearman | médiane C₁/C₀ − 1 | P1 | Verdict |
|---|---:|---:|---:|---:|---|---|
| infirmiers | 100 | 0,000 | 0,8350 | −28,4 % | maintien | **M1 retenu** |
| kinés | 101 | 0,000 | 0,9838 | −14,1 % | maintien | **M1 retenu** |
| sages-femmes | 101 | 0,010 | 0,9886 | +6,1 % | maintien | **M1 retenu** |
| dentistes | 101 | 0,931 | 0,9976 | 0,0 % | abandon | **en attente de P2** |
| pharmaciens | — | — | — | — | (pas de P1) | **aucun verdict** (P2 seul, Open DAMIR en attente) |

Distribution de `C₁/C₀ − 1` en 2050 (min · Q1 · médiane · Q3 · max) et les départements les plus écartés :
- IDE : −50,7 % · −30,3 % · −28,4 % · −26,3 % · −19,5 % ; 971, 972, 974, 973, 05.
- MK : −30,7 % · −15,9 % · −14,1 % · −12,7 % · −9,2 % ; 972, 971, 05, 974, 27.
- SF : +2,0 % · +4,5 % · +6,1 % · +8,1 % · +21,7 % ; 971, 972, 24, 05, 2A.
- CD : −3,4 % · −0,6 % · 0,0 % · +0,6 % · +2,0 % ; 976, 971, 74, 973, 01.

Rapporté, non décisif :

| Profession | Omphale bas : S₁ / ρ | Omphale haut : S₁ / ρ | Central 2035 : S₁ / ρ |
|---|---|---|---|
| infirmiers | 0,000 / 0,922 | 0,000 / 0,890 | 0,000 / 0,870 |
| kinés | 0,000 / 0,985 | 0,000 / 0,982 | 0,000 / 0,987 |
| sages-femmes | 0,119 / 0,985 | 0,010 / 0,991 | 0,564 / 0,972 |
| dentistes | 0,545 / 0,998 | 0,584 / 0,997 | 0,980 / 0,997 |

Lecture des dentistes : le verdict « abandon » sous P1 tient au scénario central. Sous les scénarios bas et haut,
S₁ tombe à 55–58 % (le décalage de la pyramide nationale y fait passer la médiane de l'écart à −1,7 % et +1,9 %),
mais ρ reste ≥ 0,997 : l'âge déplace le **niveau** national de l'indice des dentistes, pas le **classement** des
départements. Ces lignes ne sont pas décisives (protocole) et ne changent pas le verdict.

Ce que mesure `C₁/C₀` : le rapport n'est pas normalisé au national. Il contient le vieillissement **national**
pondéré par le profil (IDE : −28 % en médiane), pas seulement l'écart entre départements. C'est la statistique
gelée ; le rang (ρ) isole la part territoriale.

## How
- **Données :** Omphale 2022 (Insee, `data/processed/population.parquet`, 3 scénarios) ; poids APL DREES (jeu 530,
  `v2/data/processed/besoin/apl_parametres.parquet`, colonne 2024 = DCIR 2022, MK colonne 2023 = DCIR 2021) ;
  effectifs : trajectoire C1 servie (`v2/prototype/server.py`, `Model`), secteur privé.
- **Méthode :** [`v2/besoin/validation/pb1.py`](../../../besoin/validation/pb1.py), estimateur
  [`m1.py`](../../../besoin/estimateurs/m1.py). Commit du passage : `404d251` (jumeau et M1 à ce commit).
  Commande : `PYTHONPATH=v2 uv run python -m besoin.validation.pb1` → `v2/artifacts/besoin_pb1/results.json`.
- **Contrôle indépendant :** `C₁/C₀ − 1` recalculé par un chemin pandas direct sur le parquet Omphale et les poids
  (IDE, dép. 05 : −0,3583 ; 971 : −0,5072) : identique au passage.
- **Cas limite :** profil plat ⇒ C(M1) = C(M0), écart max 0 (test L1 de `besoin.tests`, 8/8).

## ⚑ What could make it wrong
- **P2 absent.** Le verdict des dentistes dépend de P2. Le protocole note que P2 écrase le profil à 80+, ce qui le
  biaise **vers l'abandon** : un abandon confirmé par P2 serait donc attendu, mais il faut le passage.
- **Seuils supposés** (2 %, 0,98), sans étalonnage externe. Les dentistes sont près du seuil (93,1 % contre 90 %).
- **Poids datés et figés** (DCIR 2021–2022) ; dérive du recours par âge hors périmètre (L31).
- **Champ CD différent** (trois régimes extrapolés) : les poids CD ne sont pas strictement comparables aux autres.
- **N déterministe** (écart 2) : la sensibilité de ρ aux tirages de C1 n'est pas mesurée.
- **Circularité** : M1 hérite de la censure du recours ; P-B1 ne la teste pas (P-B2, P-B3).

## → What it changes
- **M1 est le dénominateur servi** pour IDE, MK et SF. Le module n'est pas réduit à M0 : la suite (M2, M3) est
  construite.
- Dentistes : M1 reste calculé, servi sous réserve du verdict P2 ; si P2 conclut aussi à l'abandon, M0 suffit pour
  eux.
- Pharmaciens : ni M1 ni verdict tant que l'axe 4 n'a pas livré le profil DAMIR.

## ? Next
| Item | Cost |
|---|---|
| P-B1 sous P2 (profil DAMIR) : dentistes et pharmaciens, dès la fin de l'axe 4 | ~15 min Claude |
| Sensibilité de ρ aux tirages de C1 (non décisive) | ~20 min Claude |
