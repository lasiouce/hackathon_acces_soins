---
type: analysis
date: 2026-11-15
author: session besoin-v2-m1-m3
question: Projeter le recours 2016 → 2025 par la seule structure d'âge (M1) bat-il la persistance du recours par habitant, et un GBM bat-il M1 ?
headline: "P-B5 : H-B1 retenue (M1 bat la persistance pour 3 professions sur 4 : IDE −8,1 pts de MAPE, MK −3,3, CD −1,0 ; SF +1,6, perd), même verdict sous P2 ; le GBM passe la règle pour IDE (−1,9 pt), CD (−3,2) et SF (−45,8), pas pour MK ; son gain suit la croissance de l'offre, pas l'âge (diagnostic a posteriori)"
status: passage fait ; GBM servi comme prédicteur du recours seulement (décision du 2026-11-15)
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B1 ; protocole gelé P-B5 (v2/validation/preregistered/2026-11-15-besoin-p-b5-backtest.md) et amendement A1.3
sources: [patientèle et démographie data.ameli.fr (ODbL), estimations de population Insee (1975–2023), Omphale 2022, poids APL, effectifs du jumeau, grille de densité Insee 2016]
tags: [besoin, validation, P-B5, backtest, GBM]
---

# P-B5 — backtest du recours par la structure d'âge (passage)

> **Headline :** projeter le recours 2016 → 2025 par la seule structure d'âge **bat la persistance** du recours par
> habitant pour les infirmiers (MAPE 7,7 % contre 15,8 %), les kinés (10,8 contre 14,1) et les dentistes (9,4 contre
> 10,4), IC à 98,75 % sous 0 : **H-B1 est retenue**, sous P1 et sous P2. Les sages-femmes perdent (66,6 contre 65,0) :
> leur recours a crû avec l'offre (effectif libéral : +54 % en médiane départementale), ce que ni l'âge ni la population ne voient.
> Le **GBM** bat M1 au-delà de l'IC pour IDE, CD et SF ; par la règle gelée, il **qualifie** pour ces trois
> professions. Sa mise en service comme estimateur de besoin est **soumise à décision** (§ What it changes).

## Écarts au protocole et à A1.3, écrits le 2026-11-15 avant tout calcul
Protocole gelé (RFC 3161, 02:17:19 UTC) ; A1 gelé à 03:18:22 UTC. Seuils, IC, Bonferroni et hyperparamètres du GBM
inchangés.

1. **Population.** Téléchargé avec l'accord de l'utilisateur·rice (2026-11-15) : Insee, « Estimation de population au
   1ᵉʳ janvier, par département, sexe et âge quinquennal », fichier `estim-pop-dep-sexe-aq-1975-2023.xls`
   (insee.fr, page 1893198, paru en janvier 2023, résultats provisoires arrêtés fin 2022 ; SHA-256
   `97a4caea25fd02a4…`), stocké dans `v2/data/raw/insee/` (ignoré par git). C'est le millésime le plus récent
   servi par la page le 2026-11-15 ; aucun fichier 1975–2024 ou 1975–2025 n'y est publié (adresses essayées : 500).
   - **2016 et 2021** : estimations Insee telles quelles.
   - **2025** : non publiée dans ce millésime. `pop(d,2025,a,s) = Insee(d,2023,a,s) × Omphale(d,2025,a,s) /
     Omphale(d,2023,a,s)` (Omphale 2022 central). Rapporté, non décisif : la même chaîne avec la cible **2023**
     (h = 7, Insee 2023 provisoire, sans Omphale).
2. **Densité libérale de 2016 (covariable du GBM).** Effectifs du jumeau (secteur privé). Les **kinés** n'ont pas
   2016 dans la table de secteur : on prend **2017**. Les IDE n'ont pas Mayotte : le GBM IDE travaille sans 976,
   comme M1 et la persistance (jointure).
3. **Densité des trois autres** : somme des effectifs du jumeau des trois autres professions de la patientèle, même
   année que (2), sur la population 2016.
4. **Communes denses ou intermédiaires** : grille de densité à 7 niveaux, géographie 2016 (Insee, fichier sur
   disque) ; niveaux 1 à 4 (grands centres urbains, centres urbains intermédiaires, ceintures urbaines, petites
   villes), qui forment « dense » et « intermédiaire » de la grille à 4 niveaux ; poids = population municipale 2014
   du fichier. Les cinq DROM y figurent (vérifié) ; département = deux premiers caractères du code commune (trois
   pour 97x).
5. **Validation croisée « une région laissée de côté »** : régions 2016 telles qu'elles sont, 13 métropolitaines et
   5 DROM, soit **18 plis** (le protocole dit « 13 plis » sans dire où vont les DROM ; même choix que P-B3).
6. **Recours** `R = file active × effectif ameli` (A1.1) pour 2016, 2021, 2025.
7. **Sensibilité P2** : poids APL colonne **2022** (DCIR 2020), pour les quatre professions (A1.3). Règle « dépendante
   du profil » appliquée à elle.
8. **Bootstrap** : départements tirés avec remise, MAPE recalculées sur les prédictions déjà faites (GBM non
   réentraîné), B = 2 000, graine 20261115, IC percentile bilatéral à 98,75 %.
9. **scikit-learn** : version installée au passage (`uv run --with scikit-learn`), inscrite dans les résultats.

## Question
H-B1 ([protocole](../../../validation/preregistered/2026-11-15-besoin-p-b5-backtest.md), A1.3) : la structure d'âge
seule (M1) prédit-elle le recours départemental à 9 ans mieux que la persistance du recours par habitant ? Un GBM sur
covariables ouvertes bat-il M1 au-delà de l'IC (règle de C1-GBM) ?

## Result
Cible 2025 depuis 2016 (h = 9), 101 départements, 18 plis régionaux. MAPE en points (**mesuré**) ; seuils supposés
au gel. IC à 98,75 % (bootstrap des départements, B = 2 000).

| Profession | MAPE persistance | MAPE M1 | Δ₁ [IC] | M1 | MAPE GBM | Δ_GBM [IC] | GBM |
|---|---:|---:|---|---|---:|---|---|
| infirmiers | 15,79 | 7,72 | −8,07 [−9,22 ; −6,71] | **gagne** | 5,81 | −1,91 [−3,28 ; −0,53] | **qualifie** |
| kinés | 14,11 | 10,79 | −3,32 [−4,42 ; −2,13] | **gagne** | 9,84 | −0,95 [−2,89 ; +0,88] | n'entre pas |
| dentistes | 10,37 | 9,38 | −0,99 [−1,38 ; −0,56] | **gagne** | 6,20 | −3,19 [−4,95 ; −1,35] | **qualifie** |
| sages-femmes | 65,00 | 66,57 | +1,57 [+1,35 ; +1,79] | **perd** | 20,73 | −45,84 [−51,34 ; −39,28] | **qualifie** |

- **H-B1 : retenue** (3 gagnées, 1 perdue). **Sous P2** (poids APL colonne 2022) : Δ₁ = −8,06 / −3,43 / −0,90 /
  +1,64, mêmes verdicts ⇒ H-B1 retenue, **pas dépendante du profil**.
- Rapporté, non décisif :

| Profession | h = 5 (2021) : pers / M1 | cible 2023 (Insee seul) : pers / M1 | pondéré par la pop. : pers / M1 / GBM | hors 75, 92–94 : pers / M1 / GBM |
|---|---|---|---|---|
| infirmiers | 38,56 / 34,41 | 17,56 / 10,67 | 14,8 / 6,5 / 5,4 | 15,87 / 7,79 / 5,84 |
| kinés | 7,35 / 7,98 | 9,82 / 8,63 | 14,1 / 10,4 / 9,7 | 13,65 / 10,34 / 9,56 |
| dentistes | 5,02 / 5,13 | 7,55 / 7,07 | 11,0 / 9,8 / 5,3 | 10,37 / 9,38 / 6,26 |
| sages-femmes | 48,61 / 49,93 | 59,21 / 60,57 | 64,5 / 65,8 / 16,8 | 65,30 / 66,89 / 20,53 |

  À h = 5, M1 perd pour MK et CD (de 0,6 et 0,1 point) et gagne à h = 9 : le protocole demande de le dire. L'année
  2021 est perturbée par le COVID (IDE : MAPE 34–39 %).
- La cible 2023 (Insee seul, sans le raccord Omphale de l'écart 1) donne les mêmes signes que 2025.

**Diagnostic a posteriori (non décisif, écrit après le passage,
[`pb5_diag.py`](../../../besoin/validation/pb5_diag.py)).** D'où vient le gain du GBM ?
- Sans les deux covariables de densité, sa MAPE reste 6,47 (IDE), 10,53 (MK), 6,97 (CD), 20,58 (SF) : la densité
  initiale n'est pas la source du gain.
- Sa cible, `log R(2025)/R̂_M1`, corrèle à la croissance de l'effectif libéral ameli 2016 → 2025 : 0,57 (IDE),
  0,71 (MK), 0,64 (CD), 0,54 (SF). Le GBM apprend le **rattrapage du recours là où l'offre a crû** (par quelle covariable : non mesuré, l'importance
  des variables n'a pas été calculée), c'est-à-dire une composante d'offre, pas de besoin.

## How
- **Données :** patientèle et démographie data.ameli.fr (ODbL) 2016, 2021, 2023, 2025 ; estimations de population
  Insee 2016, 2021, 2023 (téléchargées, écart 1) ; Omphale pour le raccord 2023 → 2025 ; poids APL ; effectifs du
  jumeau (densités) ; grille de densité 2016.
- **Méthode :** [`pb5.py`](../../../besoin/validation/pb5.py). Commit du passage : `dd66519` (écarts commités avant
  le lancement, même commit). scikit-learn 1.9.1, hyperparamètres gelés.
  Commande : `PYTHONPATH=v2 uv run --with scikit-learn --with xlrd --with openpyxl python -m besoin.validation.pb5`.

## ⚑ What could make it wrong
- **Regard en avant** : P1 (DCIR 2022) et même P2 (DCIR 2020) sont dans la fenêtre ; aucun profil antérieur à 2016.
  Même verdict sous les deux.
- **Population 2025 raccordée** (Insee 2023 × croissance Omphale) ; la cible 2023 sans raccord va dans le même sens.
- **R = file active × effectif** : la MAPE contient la croissance de l'offre (menace A1.3), ce qui explique la
  défaite de M1 chez les SF et le gain du GBM.
- **Patientèle** : patients uniques, département déduit (P-B2).
- 101 départements, 18 plis : le GBM est jugé sur ~95 points d'apprentissage par pli.

## → What it changes
- **H-B1 retenue** : M1 est un meilleur prédicteur du recours à 9 ans que la population brute pour IDE, MK, CD.
  Pour les SF, ni M1 ni M0 ne suivent le recours, qui suit l'offre.
- **GBM : qualifie pour IDE, CD, SF par la règle gelée, mais pas mis en service ici — décision demandée.** Raisons :
  1. le diagnostic montre que son gain est le rattrapage lié à la croissance de l'offre ; servi comme besoin, il
     rendrait B dépendant de l'offre, contraire à la norme d'un estimateur de besoin (dérivation §2, cas limite
     « offre nulle ») ;
  2. il est appris pour h = 9 depuis 2016 ; une projection à 2050 (h = 24 depuis 2026) l'extrapole hors de sa
     validation.
  Écrit au registre sous `## Open / not yet decided`, avec la recommandation de le garder comme prédicteur du
  **recours** (diagnostic), pas comme estimateur du besoin.
  **Tranché le 2026-11-15 (option a)** : servi comme prédicteur du recours seulement, à h = 9, pour IDE, CD et SF
  ([`gbm_recours.py`](../../../besoin/estimateurs/gbm_recours.py)) ; hors du registre des besoins (test L4).
  Premier passage 2025 → 2034 (**mesuré**, somme nationale) : GBM / M1 = 1,008 (IDE), 1,114 (CD), **2,484 (SF)**.
  Pour les SF, le GBM prolonge le rattrapage 2016 → 2025 (recours ×2,5 en 9 ans au-delà de l'âge) : c'est la
  croissance passée de l'offre extrapolée, à lire comme telle, pas comme une prévision de besoin.

## ? Next
| Item | Cost |
|---|---|
| Backtest SF avec un terme d'offre explicite (recours = besoin × φ(A)), pour séparer âge et offre | ~30 min Claude |
