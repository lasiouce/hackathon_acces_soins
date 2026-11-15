---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: Comment appliquer P-B2, P-B3, P-B5 et P-B6 aux données réellement ingérées par l'axe 4, sans toucher à leurs règles de décision ?
headline: "Amendement A1, gelé avant tout passage de P-B2, P-B3, P-B5 et P-B6 : recours = file active moyenne × effectif ameli ; P-B5 sans profil DAMIR 2016 (non lu) ; P-B6 : m inchangé sur Open Medic, s(t) régional par DAMIR abandonné (DAMIR arrêté à 9 mois) ; P-B1 et P-B4 déjà lancés, non amendés"
status: amendement gelé (protocoles non lancés)
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: amendement des protocoles gelés le 2026-11-15 à 02:17:19 UTC (manifeste f0936ab2be34)
sources: [v2/docs/lab/reports/2026-11-15-besoin-axe4-donnees.md (branche claude/besoin-axe4-donnees-b06395, commit 51a9e30), message de l'axe 4 à l'axe 3 (2026-11-15)]
tags: [validation, besoin, pre-registration, amendement]
---

# Amendement A1 aux protocoles P-B2, P-B3, P-B5 et P-B6

> **Headline :** l'axe 4 a ingéré les données après le gel. Trois constats
> changent la **définition** de variables ou la **disponibilité** de
> sources ; aucun ne change une règle de décision, un seuil ou une
> correction de multiplicité. Les copies gelées ne sont pas modifiées.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Ce que l'auteur a vu avant d'écrire A1
- Le rapport d'ingestion de l'axe 4 (contrôles de totaux, descriptifs lus).
  Il ne contient **aucune** relation recours × offre.
- Les intitulés de commit des autres sessions, dont celui du passage de P-B1
  (« âge retenu pour IDE, MK, SF ») et celui du passage de P-B4 (sans
  chiffre). Aucun fichier de résultats de P-B1 ni de P-B4 n'a été ouvert.
- Aucun résultat de P-B2, P-B3, P-B5 ou P-B6 : à l'écriture de A1, ils n'ont
  pas été lancés (journal git des branches du besoin, lu le 2026-11-15).

## Hors champ de A1
- **P-B1 et P-B4** ont déjà été lancés par d'autres sessions. Leurs écarts
  au protocole sont écrits dans leurs rapports de passage (selon les
  intitulés de commit) et ne sont pas rouverts ici.
- Le distancier de repli de l'axe 4 utilise 60 km/h, alors que P-B4 en gèle
  50 km/h (h). Ce point appartient au rapport de passage de P-B4.

## A1.1 — P-B2 : définition du recours
**Constat (axe 4, descriptif lu).** Le jeu « patientèle » de data.ameli.fr
donne le **nombre moyen de patients uniques par professionnel** (file
active moyenne), pas un total. Le département est celui des professionnels,
déduit du libellé ; la page « Méthode » n'a pas été lue.

**Amendement.**
- `R(p,d,t) = file active moyenne(p,d,t) × effectif(p,d,t)`, où l'effectif
  vient du jeu data.ameli.fr `demographie-effectifs-et-les-densites` : même
  profession, même département, même année. C'est le dénominateur du même
  producteur.
- **L'accessibilité `A` reste celle du protocole gelé**, calculée sur les
  effectifs libéraux du **jumeau**. Elle est mesurée indépendamment, si bien
  qu'une erreur de mesure de l'effectif ameli ne passe pas des deux côtés de
  la régression.
- Codes data.ameli.fr : les lignes « département 999 » (totaux régionaux) et
  « région 99 » (France) sont exclues des 101 points.

**Rapporté, non décisif.** La même spline, avec `A` calculée sur l'effectif
ameli. Comme `log R_std = log(file active) + log A_ameli`, la pente y est
biaisée vers 1 par l'erreur commune (d). Elle est étiquetée comme telle.

**Menaces ajoutées.**
- `R` compte des **paires patient × professionnel**. Un patient vu par deux
  infirmiers du même département compte deux fois. La marge extensive est
  donc moins nette qu'écrit dans le protocole.
- Le département des professionnels soutient l'hypothèse « département
  d'exercice ». C'est une déduction, pas une lecture : la menace écrite de
  fuite de patientèle reste entière.

## A1.2 — P-B3, test (B)
P-B3 (B) reprend `R_std` de P-B2 : il hérite de A1.1, sans autre changement.
- Le prix moyen par acte de la voie (i) se calcule sur **Open DAMIR de
  janvier à septembre 2025** (9 mois lus), et non sur l'année 2025 entière
  (DAMIR arrêté par décision de l'utilisateur·rice, faute de temps).
- Menace ajoutée : la saisonnalité d'octobre à décembre manque, surtout pour
  les actes de vaccination.

## A1.3 — P-B5
- **Recours** : défini comme en A1.1, pour 2016, 2021 et 2025.
- **Sensibilité P2 (Open DAMIR 2016) : non faisable.** 2016 n'a pas été lu.
  Elle est remplacée par les poids d'âge du **plus ancien millésime APL
  disponible** (fichier 2022), qui regardent le moins en avant. La menace de
  regard en avant reste : aucun profil antérieur à 2016 n'est disponible.
  La règle « H-B1 dépendante du profil si les deux verdicts diffèrent »
  s'applique à cette sensibilité.
- **Menace ajoutée.** Le total `R` croît avec l'effectif (`R = file active ×
  N`). Ni la persistance ni M1 ne voient la croissance de l'offre de 2016 à
  2025 : l'erreur des deux contient la croissance de N. Le test compare deux
  prédicteurs également aveugles à l'offre, ce qui est voulu (M1 est un
  besoin), mais la MAPE ne mesure pas seulement l'âge.

## A1.4 — P-B6
**Constats (axe 4).**
- Open DAMIR est arrêté à 9 mois sur 49 (2025-01 à 2025-09), par décision de
  l'utilisateur·rice : les saisons 2015-16 à 2019-20 **ne sont pas lues**.
- Pour Open Medic, le descriptif a été lu :
  - `BEN_REG` est la région de **résidence** ;
  - l'âge compte 3 tranches (0–19, 20–59, 60+) ;
  - les années civiles 2014–2025 sont présentes ;
  - DOM et Corse sont regroupés ;
  - les contrôles contre le total national passent, 24 sur 24 (s).

**Amendement.**
- **`m`, inchangé.** La différence de différences annuelle sur Open Medic
  2014–2018 était déjà le test décisif du protocole gelé. Les conditions de
  faisabilité sont levées (12 zones métropolitaines, résidence, 2014
  présent). Elles seront constatées au passage, sans lire les volumes avant.
- **Placebo** : tranche 0–19 ans. **Tranche « la plus élevée »** : 60 ans et
  plus.
- **`s(t)` régional par DAMIR : abandonné** (données non lues). Il est
  remplacé, à titre **descriptif seulement** et sans seuil, par :
  - la part nationale des pharmaciens selon la Cour des comptes (s) ;
  - les parts par cohorte de 2019-20 selon Liard 2022 (s) ;
  - la série IQVIA (actes en officine, 2020-21 → 2026-27, panel extrapolé)
    rapportée aux boîtes J07BB d'Open Medic de l'année civile de début de
    campagne, par région si `iqvia_regional` est au grain régional, sinon
    au national.
- L'ajustement `s(t) = s_∞ (1 − e^{−(t−t₀)/τ})` se fait sur la série
  nationale s'il existe au moins 3 points, sans IC par région. Sinon il n'est
  pas fait.
- La menace « deux saisons seulement avant 2017 (DAMIR) » devient sans
  objet. Restent : l'année civile contre la campagne, 3 années avant
  traitement pour la cohorte 2017, et 12 grappes.

## Règles de gel
- A1 est figé ; son empreinte SHA-256 est inscrite dans le rapport
  `2026-11-15-besoin-axe3-protocoles` (addendum) et dans le manifeste
  `horodatage/2026-11-15-besoin-amendement-a1-SHA256SUMS`.
- P-B2, P-B3, P-B5 et P-B6 ne sont lancés qu'après le jeton de A1, ou, à
  défaut, après le commit poussé de A1 seul. Le rapport de passage cite
  l'heure qui s'applique.
