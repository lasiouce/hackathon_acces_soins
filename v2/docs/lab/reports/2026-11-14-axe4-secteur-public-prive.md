---
type: analysis
date: 2026-11-14
author: Claude (session axe 4)
question: Peut-on séparer public et privé dans les salariés RPPS / BTS, et de combien la fourchette « libéral » (= privé) se resserre-t-elle ?
headline: "Sages-femmes « libéral » 2026 : 12 059 – 14 660 (centrale 12 912), contre 12 475 – 26 428 ; largeur −81 %. Pharmaciens 60 005 – 67 219, dentistes 40 784 – 47 894, kinés 98 828 – 103 986 ; infirmiers 2023 : 277 788, sans ambiguïté"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: définition « libéral = privé » (decisions.md, 2026-11-14)
sources: [DREES démographie des professionnels de santé depuis 2012 (2026-07-02), DREES/Insee BTS infirmières salariées 2013–2023 (2026-07-02), FINESS établissements et entités juridiques au 2026-05-04]
tags: [data, axe4, secteur, public-prive]
---

# Axe 4 — Séparer public et privé

> **Headline :** la séparation était déjà dans les fichiers DREES sur disque : ils croisent dép × **secteur
> d'activité** × mode × âge × sexe, et le loader v1 gardait le secteur à « Ensemble ». La sortie « libéral »
> (= privé) 2026 passe, pour les sages-femmes, de 12 475 – 26 428 à **12 059 – 14 660** (centrale 12 912). Les
> infirmiers (BTS) sont séparés sans ambiguïté : **277 788** privés en 2023.

> **Mise à jour du 2026-11-14 (soir).** SF salariées en « Prévention » (PMI) classées publiques, d'après la DREES
> (1 423 SF en PMI au 31/12/2024, mesure axe 1) : fourchette SF 2026 **12 059 – 13 331 (centrale 12 819)**,
> largeur 1 272. Pharmaciens hospitaliers : variante SAE à +1 116 privés (voir
> [flux communaux](2026-11-14-axe4-flux-communaux.md) et decisions.md). Les tableaux ci-dessous restent ceux du
> premier calcul.

## Question
Sans séparation public / privé chez les salariés, la sortie « libéral » 2026 n'était connue qu'en fourchette
([decisions.md](../decisions.md), « Libéral = secteur privé »). Toutes les sorties du jumeau en dépendent.

## Result

**Sortie « libéral » (= privé, tout employeur public exclu), France entière, dernière année** — mesuré :

| Profession | Année | Effectif total | Ancienne fourchette | **Min** | **Centrale** | **Max** | Largeur avant → après |
|---|---|---|---|---|---|---|---|
| Sages-femmes | 2026 | 26 428 | 12 475 – 26 428 | 12 059 | 12 912 | 14 660 | 13 953 → 2 601 (−81 %) |
| Pharmaciens | 2026 | 75 335 | 65 344 – 75 335 | 60 005 | 63 612 | 67 219 | 9 991 → 7 214 (−28 %) |
| Dentistes | 2026 | 48 690 | 48 143 – 48 690 | 40 784 | 47 349 | 47 894 | 547 → 7 110 (voir ⚑) |
| Kinés | 2026 | 111 141 | 98 348 – 111 237 | 98 828 | 101 951 | 103 986 | 12 889 → 5 158 (−60 %) |
| Infirmiers | 2023 | 607 644 | — | 277 788 | 277 788 | 277 788 | 0 |

- Infirmiers : 98 854 libéraux (SNDS) + 178 934 salariés privés (BTS : hôpital privé 94 347, médico-social
  privé 40 050, autre privé 44 537).
- **Les anciennes bornes basses n'étaient pas des minima.** Elles comptaient tout « autre salarié » comme
  privé, PMI et centres municipaux compris. D'où un minimum qui baisse (SF, PH) et, pour les dentistes, une
  fourchette qui s'élargit : 6 694 dentistes salariés de centres de santé sont maintenant comptés ambigus,
  96 % privés au centre.

**D'où vient l'ambiguïté restante, 2026** (salariés de secteurs mixtes) :

| Profession | Secteur | Effectif | Part privée centrale | Source de la part |
|---|---|---|---|---|
| Pharmaciens | Autre secteur | 5 805 | 0,50 | supposée |
| Pharmaciens | Prévention et établissement de santé | 1 409 | 0,50 | supposée |
| Dentistes | Centre de santé | 6 694 | 0,963 | FINESS, centres « dentaires » (1 299 étab.) |
| Kinés | Autre secteur | 2 524 | 0,50 | supposée |
| Kinés | Établissement sanitaire et social | 2 200 | 0,696 | FINESS, EHPAD + handicap médicalisé (13 407) |
| Sages-femmes | Prévention (PMI…) | 1 329 | 0,070 | FINESS, PMI + planification (1 435) |
| Sages-femmes | Autre secteur | 796 | 0,50 | supposée |

- Parts FINESS mesurées (statut juridique ≥ 47 = privé ; 40–46 sécurité sociale compté public) : centres de
  santé 0,798 · dont dentaires 0,963 · PMI / planification 0,070 · EHPAD 0,558 · handicap médicalisé 0,866.

**Séries** : la fourchette est disponible pour chaque année 2012–2026 (ADELI 2012–2016 pour les kinés,
2013–2023 pour les infirmiers salariés) et chaque département. Largeur médiane par département, dernière
année : 4 % (kinés) à 9 % (SF, CD, PH) de l'effectif.

**Contrôle contre un total connu** (`secteur_checks.csv`) : Σ des cellules dép × secteur × mode × âge × sexe =
total France du fichier, à 0 % près pour SF, CD, PH et kinés ADELI ; 0,22 % au plus pour les kinés RPPS
(2017–2018), et ≤ 0,009 % pour le BTS. L'écart kinés est **dans le fichier source** : en 2017, Σ des secteurs
= 84 599 contre 84 521 pour « Ensemble ».

**Recoupement avec l'Ordre des pharmaciens** (chiffres cités par les fiches de l'axe 1, non recalculés) :
- biologistes privés : Ordre section G 3 750 (2025) ; DREES secteur « Laboratoire » 3 373 (2026). Même ordre
  de grandeur ; l'écart de 10 % peut venir des biologistes classés ailleurs par la DREES.
- pharmaciens d'établissement privés : Ordre 28,6 % des inscriptions section H (2 548 / 8 924) ; DREES 17 %
  des salariés hospitaliers (1 659 en ESPIC ou lucratif sur 9 991). L'Ordre
  compte des inscriptions (multi-inscriptions) et des PUI hors hôpital ; **non réconcilié** (open.md).

## How
- **Data :** `data/raw/drees/*_rpps_2012_2026.xlsx`, `kinesitherapeutes_adeli_2012_2016.xlsx`,
  `infirmieres_salariees_bts_2013_2023.xlsx` (DREES, 2026-07-02) ; infirmiers libéraux via
  `data/processed/stock.parquet` (SNDS, v1) ; FINESS `etalab-cs1100502` (35,8 Mo) et `cs1100501` (11,9 Mo),
  au 2026-05-04, dans `v2/data/raw/finess/`.
- **Method :** [`v2/data/build_secteur.py`](../../../data/build_secteur.py) — table `SECTEUR`. Libéral et mixte →
  privé ; salariés classés par secteur ; secteurs mixtes : bornes 0 et 1, centre = part FINESS ou 0,5.
- **Run :** `uv run python v2/data/build_secteur.py` (≈ 12 s). Sorties : `v2/data/processed/secteur_stock.parquet`
  (899 250 lignes, dép × secteur × mode × âge × sexe × année), `secteur_split.parquet`
  (profession × année × dép + `FR` × mode3 + `tous`), `secteur_checks.csv`, `secteur_finess_shares.csv`.

## ⚑ What could make it wrong
- **Le secteur est celui de l'activité la plus récente**, pas de l'activité principale (Lisez-moi DREES). Un
  salarié avec un poste public plus ancien et un poste privé plus récent est compté privé.
- **Les parts FINESS comptent des établissements, pas des salariés.** Un grand EHPAD public pèse comme un
  petit privé. Non mesuré ; c'est la principale réserve sur les centrales.
- **Trois parts à 0,5 sont supposées** (« autre secteur », et « prévention et établissement de santé » pour
  les pharmaciens) : 5 805 + 1 409 pharmaciens portent l'essentiel de la fourchette PH.
- **Libéral et mixte comptés privés même en « Hôpital public »** (31 SF libérales, 226 mixtes en 2026), comme
  le veut la décision ; un mixte dont l'activité la plus récente est publique reste compté privé.
- **Infirmiers : double compte possible** entre SNDS (libéraux) et BTS (salariés) pour qui cumule les deux.
  Non mesuré. Le BTS a une rupture de série en 2022 (rapport v1 sur les infirmiers salariés).
- Les parts FINESS (2026) sont appliquées à toutes les années.

## → What it changes
- **Jumeau (axe 0) :** `secteur_stock.parquet` donne directement l'état `N[profession, secteur ∈ {prive,
  public, ambigu}, dép, âge, sexe, t]`, observé 2012–2026. Il remplace le proxy « privé = libéral + mixte »
  de `v2/jumeau/check.py` et donne au secteur public des taux propres (ligne d'open.md « Dynamique du
  secteur public »).
- **Banc (K1, filière) :** à relancer sur `part_prive_central`, avec min et max en bande.
- **decisions.md :** la table « Conséquence mesurée » de la décision « libéral = privé » est remplacée par
  celle-ci (entrée Axe 4 du 2026-11-14).
- Fiches : `data-secteur-sf`, `-cd`, `-ph`, `-mk`, `-ide`, `data-finess-parts-privees`.

## ? Next
| Item | Cost |
|---|---|
| Ventiler « autre secteur » des pharmaciens (5 805) : sections de l'Ordre (B industrie, C distribution, D adjoints, G biologie, H hôpital), comparer aux secteurs DREES | ~1 h |
| Pondérer les parts FINESS par effectifs salariés (SAE / Insee Base Tous Salariés par catégorie juridique) | ~1 h 30 |
| Mesurer le double compte infirmiers SNDS × BTS (DREES publie-t-il le recouvrement ?) | ~30 min |
| Brancher `secteur_stock.parquet` dans l'état du jumeau (session axe 0) | ~30 min, axe 0 |
