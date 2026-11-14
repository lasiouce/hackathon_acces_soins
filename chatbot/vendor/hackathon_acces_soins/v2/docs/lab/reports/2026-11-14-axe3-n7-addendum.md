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

---

## Résultat (ajouté après calcul, 2026-11-14, 04:40–05:00)

Le texte au-dessus de cette ligne est le protocole gelé (copie immuable :
`v2/validation/preregistered/`, SHA-256 `06ba47b91647`).

### A. N3 au grain communal, dans les bassins de vie — second test, design toujours invalide
`PYTHONPATH=v2 uv run --with scipy python -m validation.did_commune` (~5 s) →
`v2/validation/out/didc_*`.

**E1c, infirmiers** : 135 BV, 60 départements (grappes). Appariement en 2008 :
57 369 infirmiers, 3 sans classe de zone.

| Test | Résultat | Seuil | Verdict |
|---|---|---|---|
| T1 tendances (Wald robuste, F(4, 56)) | F = 3,02, **p = 0,025** | p ≥ 0,10 | **échoue** |
| T2 placebo de date 2006 | **+2,6 % [+0,1 ; +5,1]** | IC contient 0 | **échoue** |
| T3 placebo dentistes (61 BV) | +0,6 % [−4,7 ; +5,9] | pas même signe ≥ ½ | passe |
| T4 zone 4 vs 3 (62 BV) | −10,3 % [−19,5 ; −1,1] | < ½ \|β\| = 16 % | passe (de justesse) |
| **T5 effet** | **−32,2 % [−37,2 ; −27,3]** | IC < 0 | détecté |
| Zone 1 (incitations) vs 3, rapporté | +12,8 % [+3,3 ; +22,2] | — | — |
| θ (non interprété) | 0,84 [0,75 ; 0,92] | — | — |

Étude d'événement (réf. 2008, log-points) : 2004 −0,048 ; 2005 −0,046 ;
2006 −0,031 ; 2007 −0,032 ; 2011 −0,049 ; 2013 −0,185 ; 2015 −0,338 ;
2017 −0,465 ; 2019 −0,561. **Au sein des BV, la zone sur-dotée gagnait
environ 1 point par an sur sa voisine intermédiaire avant 2008, puis
décroche de 6 à 8 points par an après 2011.** La pré-tendance va dans le
sens contraire de l'effet.

**Verdict : design invalide (T1 et T2). Levier IDE toujours non validé.**

**E2c, kinés** (51 BV, 29 départements) : tendances F(6, 20) = 2,48,
**p = 0,059** → échoue (au département : p = 0,24). Pente en marche
−4,1 pts/an [−5,9 ; −2,4] ; en arrêt −0,8 [−2,9 ; +1,2] ; écart des pentes
**+3,3 pts/an [+0,8 ; +5,8]**, même signe qu'au département. Au grain du BV,
la prédiction tient, mais le test de tendances n'est plus passé.

### B. Stabilité de N1 entre origines (h = 5)
`… -m validation.stability prive|ancien` (~80 s chacun ; l'APC prend 73 s)
→ `out/stab_*`.

**Périmètre privé (principal).** Δ MAPE vs meilleure naïve [IC 95 %] :

| Estimateur | 2016 | 2018 | 2021 | Signe |
|---|---|---|---|---|
| jumeau_taux_locaux (défaut) | +0,10 [−0,35 ; +0,57] égal. | −0,22 [−1,40 ; +0,94] égal. | **−1,22 [−1,85 ; −0,59] gagne** | instable |
| axe2_shrink_hier | −0,16 égal. | −0,43 égal. | −1,08 gagne | stable |
| axe2_apc | −0,06 égal. | −0,16 égal. | −0,96 gagne | stable |
| axe2_ages_simples | +0,36 égal. | −0,34 égal. | −1,21 gagne | instable |
| axe2_ages_interp | **+0,53 perd** | −0,21 égal. | −1,32 gagne | instable |
| axe2_retention60 | **+1,05 perd** | +0,17 égal. | −1,25 gagne | instable |
| axe2_combine | **+0,79 perd** | −0,46 égal. | −1,15 gagne | instable |
| axe2_obs_r12 (diagnostic) | −0,55 gagne | −0,48 égal. | −1,27 gagne | stable |

τ de Kendall entre classements : 0,29 (2016–2018), **0,07 (2016–2021)**,
0,24 (2018–2021).

**Ancien périmètre (secondaire).** Défaut : −0,13 égal. (2016), −1,07 gagne
(2018), −1,70 gagne (2021) → signe stable ; τ = 0,42 / 0,29 / 0,60.

**Lecture.** Au privé, **la victoire poolée du défaut (N1, axe 2) repose sur
l'origine 2021** ; aux origines 2016 et 2018, c'est l'égalité avec la
naïve. Le classement entre estimateurs est presque aléatoire d'une origine à
l'autre (τ ≤ 0,29). La clause « classement instable » de N1 joue : la
précision par département est « sur l'origine 2021, meilleure que la
tendance ; ailleurs, égale ».

### C. Prévision probabiliste (N6 et N7-C) → `out/prob_*`
Voir le rapport N6 pour N6. Bande « pente d'erreur » (N7-C), h = 5,
origines 2017–2021, SF, CD, PH, IDE (kinés exclus faute d'erreurs passées),
1 581 cellules par estimateur :

| Estimateur | CRPS log | Δ vs tendance [IC 95 %] | Couv. 50 % | Couv. 80 % |
|---|---|---|---|---|
| jumeau_taux_locaux | 0,0722 | −0,0061 [−0,0078 ; −0,0044] gagne | 79,4 % | 95,7 % |
| axe2_shrink_hier | 0,0716 | −0,0068 gagne | 79,7 % | 95,8 % |
| axe2_apc | 0,0726 | −0,0058 gagne | 79,2 % | 95,5 % |
| naive_persistance | 0,0789 | +0,0006 égalité | 76,6 % | 97,2 % |
| naive_tendance | 0,0784 | — | 78,8 % | 95,1 % |

Tous les estimateurs à modèle **gagnent** contre la référence naïve
probabiliste. **Aucune bande n'est calibrée : elles sont trop larges**
(intervalle « 80 % » couvrant ~96 %, « 50 % » couvrant ~79 %). Une erreur
qui croît linéairement avec h surestime l'erreur à 5 ans.

### D. N2 : ER 1319 et réconciliation des dentistes → `out/dd76_results.json`
**D1, ER 1319 (infirmiers libéraux).** Point de départ identique : 98 631 en
2021 (RPPS et ER 1319). Ratios N(t)/N(2021) : nous 1,154 / 1,263 / 1,313 en
2030 / 2040 / 2050 ; ER 1319 1,298 / 1,567 / 1,754. Écart **−11,1 % / −19,4 %
/ −25,2 %** → **échoue**. Mais l'observé départage déjà en partie :
RPPS 2023 = 98 854 ; ER 1319 = 104 724 (+5,9 %) ; nous (entrées plates
2017–2021) = 102 439 (+3,6 %). Les deux surestiment 2023 ; la DREES
davantage.

**D2, dentistes 2050.** Notre cible « privé, origine 2026, entrées des
2 dernières années » donne **81 491** ; la variante par défaut (entrées =
moyenne de la fenêtre) **61 964** ; DD76 **61 800**. Écart cible − DD76 =
**+19 691**. Valeurs de Shapley : origine et fenêtre **+13 056**, entrées
récentes **+11 658**, périmètre **−1 877** ; résidu (notre configuration de
base − DD76) −3 145, soit **16 %** de l'écart → **passe** (≤ 25 %).
Le jeune effectif privé (< 35 ans) passe de 9 009 en 2018 à 15 725 en 2026
(+75 %) : tenir le niveau 2025–2026 des entrées pour 24 ans fait l'essentiel
de l'écart, avec la fenêtre 2012–2026 qui contient cette hausse.

## ⚑ What could make it wrong
- A est un **second** test sur le même levier : la protection du
  pré-enregistrement est entamée (deux essais). Il échoue de toute façon.
- A : un débordement des entrants bloqués vers la zone 3 voisine gonfle le
  témoin ; β est alors une borne haute de l'effet sur le total.
- B : l'IC par origine ignore toujours la corrélation entre départements
  voisins.
- C : la bande « pente » est un choix de forme (linéaire en h) ; une forme en
  √h pourrait être calibrée. Ce serait un nouveau protocole.
- D2 : la grille de Shapley utilise le stock-flux à taux locaux pour les
  8 configurations ; le résidu inclut l'écart de moteur à DD76 (A échoue).

## ? Next
| Item | Cost |
|---|---|
| Pré-enregistrer une bande en √h (ou empirique par h) et la tester (N8) | ~30 min |
| N3 : contrôle synthétique par BV, pré-enregistré (3e test, déclaré) | ~1 h |
| D2 : décision de l'utilisateur·rice sur le niveau d'entrées de référence (moyenne de fenêtre ou 2 dernières années) | temps humain |
