---
type: analysis
date: 2026-11-15
author: session besoin-axe1-fiches (4 lecteurs web Sonnet ; relecture : 4 lecteurs Haiku, 2 vérificateurs Sonnet)
question: Quelles valeurs sourcées, supposées ou non mesurables portent les hyperparamètres du module de besoin (axe 1 du plan) ?
headline: "25 paramètres en 9 fiches : 8 sourcés (dont s_∞ = 0,70 et τ = 2,8 ans de la vaccination en officine, dérivés du SNDS), 2 partiels, 1 supposé (k de L23, plage [0,25 ; 1]), 14 non mesurables ; relecture : 142 affirmations, 105 confirmées, 12 écarts retenus et corrigés"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "attendu du plan : L23 a et s(t) sourcés, k supposé ; tension / diabète et L25 non mesurables ; L27 partiel"
sources: [DREES APL jeu 530 (xlsx 2022-2024, Lisez-moi), Open DAMIR descriptif 2024, Cour des comptes 2026 vaccination (texte + open data G9/G10), IQVIA data.gouv 2022-23 à 2025-26, HAS 2018 vaccination, Liard 2022, Buchan 2017, DREES ER 1381, loi 2023-379, sante.fr, Babatunde 2020, Ojha 2014, CSP R. 2122-1 à -3 et L. 2122-1, HAS 2016 suivi de grossesse, ameli 2026]
tags: [besoin, axe1, hyperparametres, transferts, relecture]
---

# Besoin de soins, axe 1 : fiches d'hyperparamètres

> **Headline :** 25 paramètres répartis en 9 fiches : **8 sourcés**, 2 partiels, 1 supposé et 14 non mesurables. Les
> parts annuelles de la Cour des comptes donnent pour la vaccination en officine **`s_∞` = 0,70 [0,63 ; 0,77]** et
> **`τ` = 2,8 ans [1,6 ; 3,7]** (dérivé). Le résultat suit l'attendu du plan. Il y a un écart : le volume global
> d'actes IPA est mesurable dans DAMIR, mais pas l'accès direct.

## Question
Le plan du module de besoin ([axe 1](../derivations/2026-11-15-besoin-plan.md)) demande une fiche par paramètre. Chaque
fiche porte une valeur, une source primaire lue, un millésime et une incertitude, ou bien l'étiquette « supposé » ou
« non mesurable ». Ces fiches sont un prérequis de l'axe 2 (méthodes). Registre : [[decisions]], entrées du 2026-11-15.

## Résultat

| Fiche | Paramètre | Valeur | Statut |
|---|---|---|---|
| [[param-besoin-poids-age-apl]] | `ω_a(p)`, 19 tranches, IDE · MK · CD · SF | ex. IDE 2024 : 0,06 / 4,50 (80-84) / 15,51 (90+) ; **MK : pas de colonne 2024** (repli 2023) | **mesuré** (lu dans les fichiers ; 209 cellules recontrôlées par script) |
| [[param-besoin-profil-damir]] | `r̄(p)` et profil PH | variables et filtres DAMIR ; 8 tranches, 80 ans et + ouvert ; 13 régions | méthode **sourcée** ; valeur : axe 4 |
| [[param-besoin-activite-etp]] | `q_p` | convention : 1 ETP = activité libérale médiane ; bornes 10 000 € / 5ᵉ et 90ᵉ centiles | convention sourcée ; **valeur non mesurable** (médiane non publiée) |
| [[param-besoin-l23-vaccination]] | `a` | 2018 : médicaux 70,7 %, IDE 29,3 % des injections | **sourcé** (répartition) ; part en temps de MG : dénominateur à l'axe 4 |
| | `s_∞`, `τ` | 0,70 [0,63 ; 0,77] ; 2,8 ans [1,6 ; 3,7] ; part PH 27,6 % (2019) → 64,4 % (2024) | **dérivé** (ajustement, eqm 3,1 points) |
| | `m` | défaut 0, plage [0 ; +5 %] (HAS 2018 : +0,1 contre −0,2 point ; Buchan : RP 1,05) | **partiel** |
| | `k` | plage [0,25 ; 1] | **supposé** |
| [[param-besoin-tension-diabete]] | `a`, `k`, `s_∞`, `τ`, `m` | — (autorisation en juillet 2026, aucun tarif, aucun code) | **non mesurable** ×5 |
| [[param-besoin-l25-ipa]] | `a`, `k`, `s_∞`, `τ`, `m` | — ; volume IPA global mesurable (codes DAMIR 1654, 3129, 3130), accès direct non distinguable | **non mesurable** ×5 |
| [[param-besoin-l27-kine]] | `k` ; `m` ; `a`, `s_∞`, `τ` | `k` = 0 par construction ; `m` ≤ 0 (signe seulement) ; plafond de 8 séances | 1 sourcé, 1 partiel, 3 non mesurables |
| [[param-besoin-b-mg-source]] | `B_MG` (O2) | `PSE_SPE_SNDS = 1`, liste de `PRS_NAT` ; interdit d'indice de couverture MG rappelé | méthode **sourcée** ; valeur : axe 4 |
| [[param-besoin-n-grossesse]] | `n_grossesse` | **10** contacts réglementaires (7 examens + EPP + EPNP + examen postnatal) ; 10 ou 11 avec la HAS ; + 7 séances (ameli) | **sourcé** (CSP lu dans une reproduction) |

**Décompte.**
- **8 sourcés :**
  - `ω_a` ;
  - `r̄` et `B_MG` (méthode sourcée, valeur à venir de l'axe 4) ;
  - `n_grossesse` ;
  - pour L23 : `a`, `s_∞` et `τ` (ces deux derniers dérivés) ;
  - pour L27 : `k` (par construction).
- **2 partiels :** `m` de L23 et `m` de L27.
- **1 supposé :** `k` de L23.
- **14 non mesurables :** `q_p`, les 5 paramètres de tension / diabète, les 5 de L25, et `a`, `s_∞`, `τ` de L27.

**Relecture contradictoire** (même procédure que le
[2026-11-15](2026-11-15-axe1-relecture-sources.md)).

| Étape | Résultat |
|---|---|
| 4 lecteurs Haiku | 142 affirmations : 105 confirmées, 17 écarts, 17 introuvables, 3 inaccessibles |
| 2 vérificateurs Sonnet (sur les 37 non confirmées) | 12 retenus, 4 reformulés, 3 trouvés, 1 réfuté, 1 confirmé introuvable, 16 non vérifiables (pages bloquées) |
| Contrôle des faux confirmés (11 tirés au hasard) | 11 confirmés, 0 faux |

**Corrections faites dans les fiches** (chacune est marquée *[corrigé après relecture]*) :
1. **L25 : des codes IPA existent dans DAMIR** (1654 IEX, 3129 MIP, 3130 PAI). Le volume global d'actes IPA est donc
   mesurable. L'accès direct, lui, ne se distingue par aucun code : le verdict « non mesurable » tient pour l'accès
   direct seulement.
2. **L23, borne basse de `k` :** 0,32 → **0,25**. Le tarif de 7,56 € pour une injection sur prescription d'un tiers
   (Cour p. 48) avait été omis.
3. **`ω_a`, stabilité :** les écarts 11,9 / 9,3 / 8,9 % portent sur la paire 2022 → 2024, pas sur un millésime au
   suivant. D'un millésime au suivant, ils valent IDE 7,9 %, CD 6,5 %, MK 5,9 % et SF 5,4 %.
4. **APL IDE :** l'onglet « APL 2023 » porte les étiquettes de 2024 mais les populations de 2021 (constat ajouté).
5. **`n_grossesse` recommandé :** 11 → **10 ou 11**. La HAS range l'entretien prénatal dans les séances de
   préparation, et un double compte avec la consultation précoce reste possible. Pages HAS corrigées.
6. **5 400 consultations :** c'est l'**ancienne** règle d'imputation de l'APL pour les MG primo-installés
   (« auparavant »), pas une valeur de `q_MG`.
7. **Libellés :**
   - les codes 1111 C et 1211 V sont génériques ;
   - HAS 2018 : validée en juillet, mise en ligne le 8 août ;
   - recoupement IQVIA : à 6 près, et non à 5 ;
   - date de l'EPP obligatoire : amendement d'octobre 2019, version du 1er mai 2020 ;
   - L27 : chiffres de Babatunde ajoutés (études isolées).

**Écart réfuté par la session :** selon le vérificateur, les 19 min de l'ER 1381 seraient en p. 1. La phrase citée est
bien en p. 2 du PDF ; la p. 1 la met seulement en exergue.

## Comment
- **Sources :**
  - fichiers APL et Lisez-moi téléchargés depuis l'API DREES (Opendatasoft) ;
  - archive open data de la Cour (18 Ko, CSV G9 et G10) ;
  - notes des quatre lecteurs web : [`sources/`](2026-11-15-besoin-axe1-fiches/sources/).
  Aucune donnée brute n'est commitée.
- **`s(t)` :** [`fit_s_t.py`](2026-11-15-besoin-axe1-fiches/fit_s_t.py) ajuste
  `s(t) = s_∞ (1 − e^{−(t−t₀)/τ})` sur la part officinale de 2019 à 2024, par grille, pour t₀ ∈ {2017,75 ; 2018 ;
  2018,5 ; 2019}. Lancement : `python3 -I fit_s_t.py G10.csv`.
- **Relecture :**
  - consignes : [`consigne-lecteur.md`](2026-11-15-besoin-axe1-fiches/consigne-lecteur.md) et
    [`consigne-verificateur.md`](2026-11-15-besoin-axe1-fiches/consigne-verificateur.md) ;
  - JSON : [`lecteurs/`](2026-11-15-besoin-axe1-fiches/lecteurs/) et
    [`verificateurs/`](2026-11-15-besoin-axe1-fiches/verificateurs/).

## ⚑ Ce qui pourrait fausser le résultat
- **La série SNDS de la Cour compte 0 injection en officine en 2018**, alors que l'expérimentation en comptait environ
  160 000 en 2017-18 (HAS p. 32). On ignore si l'année est civile ou de campagne, et quel code d'acte est retenu. Or
  `s_∞` et `τ` dépendent de t₀ : la plage va de 0,63 à 0,77 et de 1,6 à 3,7 ans.
- **Rapprochement des fractions de la Cour :** le texte parle de « une sur deux » puis de « moins d'une sur quatre »
  pour les médicaux. Nos parts ne retrouvent ces fractions que si la catégorie « aucun acte ou consultation » est
  comptée avec les médecins. C'est notre lecture, pas celle de la Cour.
- **Textes lus indirectement :**
  - Légifrance bloque les robots : le CSP a été lu sur doctrine.fr ;
  - les décrets de 2024 à 2026 (kiné, IPA) et la loi n° 2026-668 ne sont connus que par la presse ;
  - Liard 2022 a été lu par un relais, Buchan 2017 en résumé seulement.
- **16 affirmations restent non vérifiables** (pages bloquées : ameli, caducee, Légifrance). Elles sont surtout dans
  les fiches non mesurables, où elles ne portent aucune valeur.

## → Ce que ça change
- **Axe 2 (méthodes) :**
  - M1 peut être codé avec `ω_a` (MK : repli sur 2023) ;
  - le module de transferts n'a de paramètres sourcés que pour L23. Tension / diabète et L25 restent hors modèle ou
    entièrement supposés ; L27 se code avec `k = 0` et `a`, `s` supposés.
- **Axe 3, P-B6 :**
  - l'expérimentation compte **4 régions**, pas 6 : la Cour se contredit avec l'arrêté du 8 juin 2018 et la HAS. Le
    protocole doit être gelé sur 4 régions ;
  - `s_∞` et `τ` dérivés ici servent de valeurs a priori, pas de mesure de P-B6.
- **Axe 4 (données) :**
  - lire en flux les codes IPA (1654, 3129, 3130) et VAX (1959) ;
  - récupérer les poids MK 2022 par régression sur la population standardisée communale.
- **M3 sages-femmes :** `n_grossesse` = 10 par défaut. La part assurée par les SF reste à mesurer dans DAMIR.

## ? Suite
| Point | Prix |
|---|---|
| Récupérer les poids MK 2022 : régression de la population standardisée APL 2024 sur les populations communales par âge (Insee 2022) | ~20 min Claude |
| Définir l'année et le code de la série G10 (2018 = 0 en officine) : lire la note méthodologique de la Cour ou le SNDS VGP 2018 dans DAMIR | ~15 min + DAMIR 2018 (machine) |
| Série DAMIR des actes IPA (1654, 3129, 3130) 2019-2025, borne haute de L25 | ~0 de plus dans la lecture en flux de l'axe 4 |
| Lire au JO les décrets 2024-618, 2025-55, 2026-985 et la loi 2026-668 (navigateur, Légifrance) | ~20 min |
| Trancher le double compte EPP / consultation précoce (HAS 2016) et le nombre de séances (7 ou 8) | ~15 min |
| Courbe de Bass contre exponentielle pour `s(t)` : départager quand on aura plus de saisons, ou par région avec DAMIR | ~30 min après l'axe 4 |
