---
type: analysis
date: 2026-11-14
author: session axe 3
question: Ajouts datés au protocole de validation (N3 au grain communal, stabilité N1, référence probabiliste naïve, réconciliation DREES 2050), fixés avant calcul
headline: "Protocole additionnel gelé avant calcul : (A) DiD dans les bassins de vie 2022 ; (B) verdict N1 par origine 2016, 2018 et 2021 ; (C) bandes « pente d'erreur » à armes égales pour tous les estimateurs ; (D) cible ER 1319 et décomposition de Shapley de l'écart des dentistes"
status: protocole gelé (non lancé)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 3, addendum N7 (ne modifie aucun protocole antérieur)
sources: [v2/data/processed/commune_stock.parquet et commune_geo.parquet (axe 4), zonage Atlasanté c987d0e2, DREES DD76, DREES ER 1319 (2024)]
tags: [validation, axe3, pre-registration, addendum]
---

# N7 — addendum au protocole de validation (pré-enregistré)

> **Headline:** quatre ajouts, gelés avant tout calcul qui les concerne. Les
> protocoles N1 à N6 restent inchangés et sont lancés tels quels. Écrit le
> 2026-11-14 vers 04:40, **après** le résultat de N3 au département (T1
> échoue) : l'ajout A est donc un **second test**, déclaré comme tel.

## A. N3 au grain communal, dans les bassins de vie (E1c, E2c)

**Pourquoi.** Au département, les tendances parallèles échouent (p = 0,043).
Comparer des communes sur-dotées à des communes intermédiaires **du même
bassin de vie** (BV 2022, Insee, via `commune_geo.parquet`) compare des
voisines qui partagent le même marché local. Dans 53 % des 1 707 BV, le
zonage 2012 des IDE varie à l'intérieur du BV (dérivé, compté avant tout
calcul d'effet).

**Données.** `v2/data/processed/commune_stock.parquet` (CartoSanté, avec les
arrondissements de Marseille), zonage 2012 `zonage_commune.parquet`
(millésime « 2012 »), BV de `commune_geo.parquet`. Appariement par code
commune ; communes sans BV ou sans classe exclues et comptées.

**Unité.** Cellule = BV × classe de zone, Y = somme des communes. Un BV entre
s'il a une cellule traitée et une cellule témoin avec **Y ≥ 5 l'année de
référence**.

**Estimateur.** D_{b,t} = log Y_{b,5,t} − log Y_{b,3,t} ; mêmes β_k, β et
fenêtres que N3 (avant 2004–2008, référence 2008, transition 2009–2011
exclue, après 2012–2019). Moyenne non pondérée sur les BV.

**Inférence.** Grappes = **départements** (les BV d'un même département
partagent l'ARS qui a fixé le zonage). Variance robuste par grappe (CR1),
Student à G − 1 ddl. Test des tendances : Wald robuste par grappe sur
(β_2004…β_2007), converti en F(q, G − q) par le facteur (G − q)/(q(G − 1)).

**Tests et seuils.** Identiques à N3 : T1 p ≥ 0,10 ; T2 placebo de date
2006 ; T3 placebo dentistes (z_infi, même BV) ; T4 zone 4 vs 3 dans le BV ;
T5 effet ; θ interprété seulement si T1–T4 passent.

**Kinés (E2c).** `z_kine` 5 vs 3 dans le BV, référence 2011, mêmes
prédictions de pente que E2 (marche 2011–2014 < 0 ; arrêt 2014–2017 >
marche).

**Menace annoncée d'avance : débordement.** Un entrant bloqué en zone 5 peut
s'installer dans la commune voisine en zone 3 du même BV. Le témoin est
alors gonflé, et β surestime l'effet sur l'effectif total : c'est un effet
**sur la répartition**, borne haute de l'effet sur le total. On le dira.

**Ce qui falsifie.** Comme N3. Si E1c passe T1 alors qu'E1 l'échouait, on
rapporte les deux ; le second ne « remplace » pas le premier.

## B. Stabilité de N1 entre origines

- Mêmes données, métrique, seuil et bootstrap que N1 ; **tous les
  estimateurs du registre** (`v2/validation/registry.py` à 04:40) ;
  périmètre privé (`methodes.perimetres.prive`) en principal, ancien en
  secondaire.
- Verdict de N1 calculé **séparément** pour les origines **2016, 2018 et
  2021** à h = 5 (cibles 2021, 2023, 2026). Kinés : 2021 seulement ;
  infirmiers libéraux : 2016 et 2018.
- **Classement stable** si, pour chaque estimateur, le signe de Δ
  (vs meilleure naïve de l'origine) est le même aux trois origines. On
  rapporte aussi le τ de Kendall entre les classements des estimateurs,
  par paire d'origines.
- Ce n'est pas un nouveau critère de victoire : le verdict poolé de N1 reste
  celui qui compte. B dit seulement s'il tient origine par origine.

## C. Référence probabiliste « pente d'erreur », à armes égales

- Pour **chaque** estimateur (naïfs compris), à l'origine o : erreurs log
  e = log(réel/prédit) de toutes les paires (origine o′ ≥ 2016, horizon h′)
  avec o′ + h′ ≤ o, même profession. Pente s = racine de la moyenne de
  (e/h′)², sur au moins 20 erreurs.
- Distribution prédictive : log N ~ Normale(log prédit, (s·h)²).
- Score : CRPS gaussien en forme fermée (Gneiting & Raftery 2007) sur log N,
  à h = 5, origines 2017 à 2021 ; agrégation et critère bootstrap de N1.
  Couverture à 50 et 80 % avec les bandes de N6.
- La **référence naïve probabiliste** est la persistance munie de cette
  bande. N6 (bande empirique au même horizon) est lancé aussi, tel quel.

## D. N2 : cible ER 1319 et réconciliation des dentistes

- **Cible ajoutée :** DREES ER 1319 (2024), scénario tendanciel, infirmiers
  « libéraux », 2021 → 2030, 2040, 2050, en ratios N(t)/N(2021), même
  tolérance que N2 (±2 % en 2030, ±3 % en 2040 et 2050). Notre moteur :
  infirmiers libéraux RPPS, origine 2021, taux et entrées moyens 2017–2021.
  Le champ diffère (ER 1319 : infirmiers en emploi, SNDS/BTS) ; on le dira.
- **Réconciliation des dentistes à 2050.** Écart entre notre projection
  « privé, origine 2026, variante par défaut » et DD76 (tous modes, origine
  2020). Trois facteurs, basculés un à un : (1) **périmètre** tous modes →
  privé ; (2) **origine et fenêtre** 2020 / 2016–2020 → 2026 / défaut ;
  (3) **niveau des entrées** moyenne de fenêtre → moyenne des 2 dernières
  années (saut 2025–2026). Contribution de chaque facteur = **valeur de
  Shapley** (moyenne sur les 6 ordres de bascule), pour ne pas dépendre de
  l'ordre.
- Ce qui falsifie : une part inexpliquée (interaction résiduelle) > 25 % de
  l'écart dit que les trois facteurs ne suffisent pas.

## How
- Code : `v2/validation/did_commune.py` (A), `stability.py` (B),
  `probabilistic.py` (N6 et C), `worlds.py` (N5 et SBC), `dd76.py` (N2 et D).
- Graine 20261114 partout ; machine > 30 s en arrière-plan avec k/N.
