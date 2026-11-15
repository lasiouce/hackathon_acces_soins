---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: Les six protocoles du module de besoin (P-B1 à P-B6) sont-ils écrits, figés et horodatés hors de git avant tout calcul ?
headline: "6 protocoles gelés avant tout calcul ; manifeste SHA-256 f0936ab2be34 horodaté par deux autorités RFC 3161 (FreeTSA 02:17:19 UTC, DigiCert 02:17:20 UTC, le 2026-11-15) et soumis à OpenTimestamps (ancrage Bitcoin en attente) ; P-B6 : 4 régions traitées selon Légifrance, pas 6"
status: protocoles gelés (non lancés)
professions: [infirmiers, kines, dentistes, sages-femmes, pharmaciens]
hypothesis: H-B0, H-B1, H-B2, H-B3, H-B4, H-BT (dérivation du besoin, §6 et §8)
sources: [v2/docs/lab/derivations/2026-11-15-besoin-derivation.md, v2/docs/lab/derivations/2026-11-15-besoin-plan.md, Légifrance (arrêté du 10 mai 2017, NOR AFSS1713194A, versions initiale et consolidée, lues le 2026-11-15)]
tags: [validation, besoin, pre-registration, horodatage, axe3]
---

# Module de besoin : six protocoles pré-enregistrés et leur gel

> **Headline :** 6 protocoles gelés **avant tout calcul**. L'empreinte du
> manifeste, `f0936ab2…78ac2`, porte deux jetons RFC 3161, datés du
> 2026-11-15 à **02:17:19 UTC** (FreeTSA) et **02:17:20 UTC** (DigiCert). Un
> jeton OpenTimestamps est en attente d'ancrage Bitcoin.

## Question
Le plan (axe 3) exige que les tests d'abandon du besoin soient gelés, et que
l'antériorité du gel se prouve **hors de git**. Le rapport technique a montré
que git ne la prouvait pas pour 6 protocoles sur 12 (§ Validation,
intégrité). Ce rapport dit ce qui est gelé, où, et avec quelle preuve.

## Result

### Les six copies gelées
Dossier : `v2/validation/preregistered/`.

| Protocole | Fichier | SHA-256 | Professions | Multiplicité |
|---|---|---|---|---|
| P-B1 âge, M1 contre M0 | [2026-11-15-besoin-p-b1-age.md](../../../validation/preregistered/2026-11-15-besoin-p-b1-age.md) | `75480444fb11e88329818aa14514d0572ec894309b7cc3bea6aa2b6cc61bf4bb` | 5 | sans objet (pas d'inférence ; deux profils doivent conclure) |
| P-B2 saturation | [2026-11-15-besoin-p-b2-saturation.md](../../../validation/preregistered/2026-11-15-besoin-p-b2-saturation.md) | `5fa47d619d523822352a82ac5fe37e9689c3fbcb62ae850cce1c4edd012ef982` | 4 (pas de PH) | Bonferroni /4, IC 98,75 % |
| P-B3 pathologies, M3 contre M1 | [2026-11-15-besoin-p-b3-pathologies.md](../../../validation/preregistered/2026-11-15-besoin-p-b3-pathologies.md) | `5daa8aa6d330abba641e2902928aa7ceff599a14ca580ecb8b273149e0801e70` | 5 (indice), 4 (R²) | Bonferroni /4 sur le R² |
| P-B4 reproduction de l'APL 2024 | [2026-11-15-besoin-p-b4-apl.md](../../../validation/preregistered/2026-11-15-besoin-p-b4-apl.md) | `0d6824c812e7d3d5c8459eec88714d6612b8637d4235875aa88b40373a952a5c` | 4 (pas de PH) | Bonferroni /4, IC 98,75 % |
| P-B5 backtest 2016 → 2025 et GBM | [2026-11-15-besoin-p-b5-backtest.md](../../../validation/preregistered/2026-11-15-besoin-p-b5-backtest.md) | `62c983f6273c806569c688276b5e3b2e92a2a025e95fe580c358e81d9e275b89` | 4 (pas de PH) | Bonferroni /4, IC 98,75 % |
| P-B6 vaccination en officine | [2026-11-15-besoin-p-b6-grippe-officine.md](../../../validation/preregistered/2026-11-15-besoin-p-b6-grippe-officine.md) | `b826a14964c8f178b12477d54464db8792a45fc33d6ad93d63e1649836c2fc46` | PH | un seul test décisif, k = 1 |

Les empreintes ont été calculées par `shasum -a 256` le 2026-11-15 à 03:13 CET (m).

### Horodatage externe
Le manifeste `v2/validation/preregistered/horodatage/2026-11-15-besoin-SHA256SUMS`
liste les six empreintes. Son propre SHA-256 vaut
`f0936ab2be348dfeb8440c6ec1dc09acb0a7f6f1b1316ea021376acc39f78ac2` (m). Seuls
ces 32 octets sont partis à l'extérieur, avec l'accord de l'utilisateur·rice
donné dans la session.

| Témoin | Fichier | Heure attestée | État |
|---|---|---|---|
| RFC 3161, FreeTSA (freetsa.org) | `…SHA256SUMS.freetsa.tsr` (+ `.tsq`) | 2026-11-15 02:17:19 UTC | accordé ; l'empreinte du jeton égale celle du manifeste (lu par `openssl ts -reply -text`) |
| RFC 3161, DigiCert (timestamp.digicert.com) | `…SHA256SUMS.digicert.tsr` (+ `.tsq`) | 2026-11-15 02:17:20 UTC | accordé ; même contrôle |
| OpenTimestamps (4 calendriers publics) | `…SHA256SUMS.ots` | en attente | **non ancré** au moment du commit ; `ots upgrade` à lancer après quelques heures |
| git | commit `e9f0f6e` (copies + manifeste seuls), puis `d78be6e` (jetons) | 03:13:45 CET (commit) | témoin de bonne foi seulement |

**Heure de gel à citer : 2026-11-15 02:17:19 UTC** (jeton FreeTSA). C'est
l'heure du jeton, pas celle du commit.
- Les chaînes de certificats des autorités n'ont pas été vérifiées : il
  faudrait télécharger leurs certificats racines.
- Le contrôle fait porte sur l'empreinte contenue dans chaque jeton et sur
  le statut « Granted ».

Vérification :
```bash
shasum -a 256 -c v2/validation/preregistered/horodatage/2026-11-15-besoin-SHA256SUMS
```
(à lancer depuis `v2/validation/preregistered/`), puis
`openssl ts -verify -data … -in ….tsr -CAfile <certificat de l'autorité>`
et `ots verify ….ots`.

### P-B6 : 4 régions, pas 6 (désaccord levé)
Lu sur Légifrance le 2026-11-15 : l'arrêté du 10 mai 2017, NOR AFSS1713194A,
versions initiale et consolidée.

| Texte | Ce qu'il fait | En vigueur |
|---|---|---|
| Arrêté du 10/05/2017, art. 1 (version initiale) | 2 régions : Auvergne-Rhône-Alpes, Nouvelle-Aquitaine | 12/05/2017 |
| Arrêté du **8/06/2018**, art. 1 | 4 régions : + Hauts-de-France, Occitanie | 15/06/2018 → 26/04/2019 |
| Arrêté du 25/09/2018, art. 1 | modifie l'**art. 3** (population cible) et l'annexe, **pas la liste des régions** | 27/09/2018 |
| Arrêté du 23/04/2019, art. 3 | abroge l'arrêté de 2017 (généralisation) | 26/04/2019 |

- La passe de littérature attribuait l'extension régionale à l'arrêté du
  25/09/2018. C'est l'arrêté du **8 juin 2018** qui la fait.
- Aucun texte lu ne mentionne six régions. Le chiffre de la Cour des comptes
  n'est pas retenu, et l'origine de l'écart n'est pas établie.

## How
- **Données :** aucune donnée de recours ni d'offre lue. Textes lus :
  - la dérivation §6 et §8 ;
  - le plan, axe 3 ;
  - les protocoles N9 et N12 (format) ;
  - le rapport technique, `ch-validation.tex` § Intégrité et
    `ch-menaces.tex` ;
  - Légifrance.
- **Méthode :** chaque protocole fixe l'hypothèse, les données (jeu,
  millésime, grain), la statistique, le seuil, l'IC, la référence naïve, le
  placebo, la multiplicité et les menaces. Bootstrap B = 2 000, graine
  20261115. Gel par manifeste SHA-256 et deux jetons RFC 3161
  (`openssl ts -query -sha256 -cert`, envoi par `curl`), plus `ots stamp`.

## Écarts à la dérivation, déclarés dans les protocoles
- **P-B5** : 4 professions au lieu de 5, car la patientèle n'a pas de
  pharmaciens. La barre reste 3. La mention « actes si disponibles » est sans
  objet : aucune série d'actes départementale n'est ouverte.
- **P-B2** : pas de pharmaciens (déjà dans la dérivation) ; un cas dégénéré
  est ajouté (pas de pente en bas, donc rien à saturer).
- **P-B6** :
  - 12 zones métropolitaines, au lieu de « 13 zones » ;
  - fenêtre Open Medic 2014–2018 pour `m`, la généralisation de 2019-20 ne
    laissant aucun témoin ;
  - DAMIR jusqu'en 2019-20 pour `s(t)` seulement.
- **P-B4** : aucun paramètre réglé sur 2024 ; une variante à un scalaire
  calé sur 2022 est rapportée sans décider.

## ⚑ What could make it wrong
- **OpenTimestamps n'est pas encore ancré.** Si les calendriers
  n'aboutissent pas, il ne reste que les deux jetons RFC 3161 (suffisants à
  eux seuls).
- **Chaînes de certificats non vérifiées** : l'authenticité des jetons
  repose, pour l'instant, sur le statut et l'empreinte lus.
- **Seuils supposés** (P-B1, P-B3, P-B4 surtout) : ils sont figés, pas
  étalonnés.
- **Des faits de données restent à lire avant les passages**, sans que la
  règle change selon la réponse :
  - le département de la patientèle (exercice ou résidence) ;
  - la région d'Open Medic et ses tranches d'âge ;
  - le code DAMIR de l'injection en officine.
- **Le seuil de l'axe 5** (« ratio < 1 ⇒ non distinguable ») devait être gelé
  « avec ceux de l'axe 3 » selon le plan. Il n'est pas dans ce lot (ledger).

## → What it changes
- **Axe 4** peut croiser recours et offre à partir de l'heure du jeton,
  2026-11-15 02:17:19 UTC.
- **Axe 2** lance P-B1 à P-B3 après le gel. P-B1 vient en premier, selon le
  plan.
- **P-B6** : la liste des régions et les dates sont sourcées. La ligne du
  ledger « sourcer la liste des régions » est close.
- **Rapport technique** (§ Intégrité) : ce lot est le premier dont
  l'antériorité est opposable hors de git.

## ? Next
| Item | Cost |
|---|---|
| `ots upgrade` du jeton `.ots` après ancrage Bitcoin, puis commit | ~2 min Claude, quelques heures de monde |
| Vérifier les jetons RFC 3161 contre les certificats de FreeTSA et de DigiCert | ~10 min |
| Geler le seuil de lecture de l'axe 5 avec un jeton | ~15 min |
| Lancer P-B1 (dès que M1 existe) | ~30 min Claude |

## Addendum 2026-11-15 (04:18 CET) — amendement A1 et ancrage OpenTimestamps
- **Ancrage du premier gel.** `ots upgrade` a été lancé à 04:18 CET. Le jeton `…SHA256SUMS.ots` porte une
  attestation `BitcoinBlockHeaderAttestation(975880)` (lue par `ots info`). La vérification contre un nœud Bitcoin
  n'a pas été faite : il n'y a pas de nœud local.
- **Amendement A1**, écrit après le rapport d'ingestion de l'axe 4 :
  [2026-11-15-besoin-amendement-a1.md](../../../validation/preregistered/2026-11-15-besoin-amendement-a1.md).
  - SHA-256 du fichier : `c36cecd62b9156ba866e929fd7ae125fc4436f4eaa0403c55a17e4cd23384261`.
  - SHA-256 du manifeste `horodatage/2026-11-15-besoin-amendement-a1-SHA256SUMS` :
    `3be3705558930f38449eda56badd41b63f7921a1cbc86a8fc6ee891795cae3fd`.
  - Jetons RFC 3161 : FreeTSA à **2026-11-15 03:18:22 UTC**, DigiCert à 03:18:23 UTC, tous deux accordés, avec
    l'empreinte vérifiée. OpenTimestamps est soumis et en attente. Commit seul et poussé : `b10a005`.
- **Contenu de A1.** Il change des définitions et des sources, pas des règles de décision :
  - P-B2, P-B3 (B), P-B5 : recours = file active moyenne × effectif ameli ;
  - P-B5 : la sensibilité DAMIR 2016 est remplacée par les poids APL 2022 ;
  - P-B6 : `m` est inchangé (Open Medic) ; `s(t)` régional par DAMIR est abandonné au profit d'une série descriptive
    (Cour des comptes, Liard, IQVIA).
- **Hors de A1.** P-B1 et P-B4 avaient déjà été lancés par d'autres sessions : ils ne sont pas amendés. L'auteur a vu
  les intitulés de leurs commits, pas leurs fichiers de résultats.
- **Heure de gel à citer** : pour P-B2, P-B3, P-B5 et P-B6, c'est **03:18:22 UTC** (A1). Pour P-B1 et P-B4, c'est
  02:17:19 UTC.
