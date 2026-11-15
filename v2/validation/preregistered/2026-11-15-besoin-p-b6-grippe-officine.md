---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: L'expérimentation de la vaccination antigrippale en officine (2017–2019) a-t-elle ajouté des vaccinations (m > 0) ou seulement déplacé des vaccinations existantes (m = 0) ? Quelle est la forme de la montée en charge s(t) ?
headline: "Protocole pré-enregistré, gelé avant tout calcul : 4 régions traitées (Légifrance, lu le 2026-11-15) et non 6 ; DiD à adoption échelonnée (Sun–Abraham), 12 zones métropolitaines, doses J07BB (Open Medic) 2014–2018 ; m = 0 retenu si l'IC 95 % (bootstrap sauvage par région) contient 0 ; s(t) ajusté, descriptif"
status: protocole gelé (non lancé)
professions: [pharmaciens]
hypothesis: H-BT (dérivation du besoin, §6 transferts) ; test P-B6 (§8)
sources: [Arrêté du 10 mai 2017 (NOR AFSS1713194A, JORF n° 110 du 11 mai 2017, texte n° 137), version consolidée (Légifrance), Open Medic 2014–2019 (Assurance maladie), Open DAMIR 2015-10 → 2020-02 (Assurance maladie), Insee estimations de population, Liard et coll. 2022]
tags: [validation, besoin, transferts, vaccination, DiD, pre-registration, P-B6]
---

# P-B6 — expérience naturelle : la vaccination antigrippale en officine (protocole pré-enregistré)

> **Headline :** gelé **avant** tout téléchargement de DAMIR pour ces mois
> et avant toute lecture d'Open Medic par région. Le désaccord « 4 ou 6
> régions » est levé par la lecture des textes : **4**.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Les régions traitées et les dates (sourcé, Légifrance lu le 2026-11-15)
- **Arrêté du 10 mai 2017** pris en application de l'article 66 de la LFSS
  2017 (NOR AFSS1713194A, JORF n° 110 du 11 mai 2017, texte n° 137),
  **version initiale**, article 1. L'expérimentation « est conduite dans les
  deux régions suivantes » : **Auvergne-Rhône-Alpes** et
  **Nouvelle-Aquitaine** (s).
- **Version consolidée**, article 1, en vigueur du **15 juin 2018** au
  **26 avril 2019**, « modifié par arrêté du 8 juin 2018 – art. 1 » : l'article
  porte sur « les quatre régions suivantes » : Auvergne-Rhône-Alpes,
  **Hauts-de-France**, Nouvelle-Aquitaine, **Occitanie** (s). C'est la
  version la plus étendue de l'article : aucune autre région n'y figure.
- **Arrêté du 25 septembre 2018** : il modifie l'**article 3** (population
  cible : les personnes majeures ciblées par les recommandations, et non plus
  seulement celles déjà vaccinées ni hors femmes enceintes) et l'annexe, en
  vigueur le **27 septembre 2018** (s). **Il ne modifie pas la liste des
  régions.** La passe de littérature lui attribuait l'extension régionale :
  c'est corrigé ici.
- **Arrêté du 23 avril 2019**, art. 3 : il abroge l'arrêté du 10 mai 2017 à
  compter du **26 avril 2019** (s). C'est la généralisation, avec le décret
  n° 2019-357 du 23 avril 2019 (cité par la passe de littérature, non relu
  ici).
- **« Six régions » (Cour des comptes, 2026)** : non retenu. Aucun texte lu
  ne mentionne six régions. L'origine de l'écart n'est pas établie.
- Début des campagnes : saison 2017-18 pour la première vague et 2018-19
  pour la seconde. L'entrée en vigueur au 6 octobre 2018 est citée par un
  communiqué de l'Ordre vu en résultat de recherche, non lu (h).

| Cohorte | Régions | Première saison traitée | Source |
|---|---|---|---|
| g = 2017 | Auvergne-Rhône-Alpes, Nouvelle-Aquitaine | 2017-18 | arrêté du 10/05/2017, art. 1 (s) |
| g = 2018 | Hauts-de-France, Occitanie | 2018-19 | arrêté du 8/06/2018, art. 1 (s) |
| g = 2019 | les 8 autres zones métropolitaines | 2019-20 (généralisation) | arrêté du 23/04/2019 (s) |

## Hypothèses
- **H-BT, part `m`** : l'autorisation en officine a augmenté le total des
  vaccinations antigrippales (`m > 0`). L'a priori publié est un `m` faible
  (Liard 2022, d'après la HAS : 46,1 % contre 46,0 % la première année (s)).
- **H-BT, part `s(t)`** : la part des vaccinations faites en officine suit
  `s(t) = s_∞ · (1 − e^{−(t − t₀)/τ})`.

## Unités
Les **12 zones métropolitaines** d'Open DAMIR depuis 2015 (13 régions,
PACA et Corse réunies) (s). Les DROM sont exclus : ils sont regroupés et
hors de l'expérimentation. Open Medic est agrégé aux mêmes 12 zones. 4 zones
sont traitées et 8 servent de témoins jusqu'en 2018.

## Données (jeu, millésime, grain)
- **Total des vaccinations (pour `m`)** : Open Medic (Assurance maladie),
  **doses de vaccin antigrippal délivrées**, ATC **J07BB**, nombre de boîtes,
  région du bénéficiaire, **annuel 2014–2018** (s). L'année civile t est
  rattachée à la saison t/t+1, la plupart des doses partant d'octobre à
  décembre (h).
- **Population** : Insee, estimations au 1ᵉʳ janvier, région, 2014–2018.
- **Actes en officine (pour `s(t)`)** : Open DAMIR, mois d'octobre à février,
  saisons **2015-16 à 2019-20**, `PSE_ACT_SNDS = 50` (pharmacie), région du
  bénéficiaire (`BEN_RES_REG`). Le ou les codes `PRS_NAT` de l'injection
  officinale sont fixés **au pilote, à partir de la nomenclature seule**,
  avant toute lecture des volumes par région ; le code 3360 (VGP) est le
  candidat (s). Sans code identifiable en 2017-18, la série `s(t)` vient de
  Liard 2022 (s) et l'ajustement n'est pas fait.

## Faisabilité (vérifiée au pilote, avant le calcul)
P-B6 est **non faisable**, et `m` reste « supposé » (défaut 0), si l'une de
ces conditions tient :
- moins de 4 régions traitées sont séparables dans les 12 zones, en DAMIR ou
  en Open Medic ;
- la région du bénéficiaire n'est pas celle du descriptif d'Open Medic
  (aujourd'hui déduite d'un avis d'anomalie, à lire avant).

## Statistique principale (`m`)
- `y_{r,t} = log(doses J07BB pour 1 000 habitants)`, région r, année t de
  2014 à 2018.
- Estimateur **Sun et Abraham (2021)**, à adoption échelonnée : effets fixes
  région et année, interactions cohorte × temps relatif. Les témoins sont
  les 8 zones non traitées avant 2019 ; la période de référence est e = −1.
- **ATT** = moyenne des effets post-traitement disponibles, pondérée par le
  nombre de régions × années : (g = 2017 ; e = 0, 1) et (g = 2018 ; e = 0).
- `m` en doses = `(e^{ATT} − 1)` × doses de référence des régions traitées ;
  rapporté, il alimente la valeur par défaut de `m`.

## IC et inférence
Douze grappes : la variance robuste par grappe n'est pas fiable.
- **IC 95 %** : bootstrap sauvage par grappe = région (poids de Webb,
  B = 9 999, graine 20261115), sous l'hypothèse nulle imposée pour la
  valeur p, sans imposition pour l'IC.
- **Permutation exacte** : les 66 × 45 = 2 970 façons de choisir 2 + 2
  régions traitées parmi 12 (d). La valeur p est bilatérale, sur l'ATT.

## Seuil de décision
- **`m = 0` retenu** si l'IC 95 % de l'ATT contient 0.
- **`m > 0` retenu** si l'IC 95 % est entièrement > 0 **et** si la valeur p
  de permutation est < 0,05. Si les deux ne concordent pas : « non tranché »,
  et `m` reste supposé (0).
- **`m < 0`** (IC entièrement < 0) : rapporté comme inattendu ; `m` reste
  supposé (0) et l'écart est examiné avant tout usage.

## Multiplicité
Un seul test décisif, sur une seule profession (pharmaciens) : Bonferroni à
k = 1, α = 0,05, déclaré. Les sorties secondaires ne décident rien.

## Tendances parallèles (contrôle déclaré)
Les coefficients d'avant traitement, e = −3 et −2 pour g = 2017, sont
rapportés avec leur IC. Si l'un d'eux exclut 0 à 95 %, le verdict sur `m`
reçoit la mention « tendances parallèles rejetées ». `m` reste alors
supposé, quel que soit l'ATT.

## `s(t)` (descriptif, aucun seuil)
- Part officinale : `s_{r,season} = actes officinaux DAMIR (oct.–févr.) /
  doses J07BB de l'année civile de début de saison`.
- Ajustement par moindres carrés non linéaires sur les trois cohortes
  (2017, 2018, 2019), en temps relatif, saisons jusqu'en 2019-20 ; `t₀` est
  la première saison traitée.
- IC de `s_∞` et `τ` : bootstrap des régions, B = 2 000, graine 20261115.
- Recoupement externe rapporté : parts officinales de 2019-20 selon Liard
  2022, soit 36,7 %, 35,7 % et 25,6 % selon la cohorte (s).

## Placebo
Ré-estimation de l'ATT sur le **0–19 ans** d'Open Medic, si la tranche
existe : les pharmaciens ne vaccinaient que les personnes majeures. Un
placebo dont l'IC exclut 0 fait passer le verdict en « non attribuable ».

## Rapporté, non décisif
- doses de la tranche d'âge la plus élevée publiée par Open Medic ;
- l'ATT sans la cohorte g = 2018 (dont la première saison coïncide avec
  l'élargissement de la population cible) ;
- l'ATT en montants plutôt qu'en boîtes.

## ⚑ Menaces écrites
- **Deux saisons seulement avant 2017** dans DAMIR (2015-16, 2016-17 : pas
  avant 2015, les 9 ZEAT ne recoupent pas les régions). Les tendances
  parallèles y sont peu testables. Pour les doses, Open Medic donne 3 années
  d'avant traitement (2014–2016), à confirmer au descriptif.
- **Régions non tirées au hasard.** Les pilotes ont été désignés par
  arrêté ; un choix lié aux tendances de vaccination biaiserait l'ATT.
- **Choc concomitant.** L'élargissement de la population cible (arrêté du
  25/09/2018, en vigueur le 27/09/2018) coïncide avec la première saison de
  g = 2018 et la deuxième de g = 2017. L'ATT mêle l'autorisation et
  l'élargissement.
- **Annuel contre saisonnier.** Open Medic est par année civile : la saison
  t/t+1 est attribuée à l'année t (h).
- **Intensité épidémique régionale.** Les effets fixes année n'absorbent que
  la part nationale.
- **Douze grappes, quatre traitées.** Puissance faible : un « `m = 0` » est
  une absence d'effet détectable, pas une preuve d'absence.
- **Doses délivrées et non administrées.** Une dose délivrée par l'officine
  et administrée ailleurs compte comme une vaccination.

## Règles de gel
Mêmes règles que P-B1.
