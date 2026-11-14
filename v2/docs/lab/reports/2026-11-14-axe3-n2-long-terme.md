---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: Comment valider une projection à 2050 qu'aucun backtest ne peut atteindre ?
headline: "Protocole pré-enregistré, pas encore lancé : reproduire le tendanciel DREES n°76 en ratios N(t)/N(2020) à ±2 % en 2030 et ±3 % en 2050 (CD, SF, PH), et passer trois cas limites (h → 0 exact, N* = Q·C à 1 %, verrou du quota avant L)"
status: protocole gelé (non lancé)
professions: [sages-femmes, dentistes, pharmaciens]
hypothesis: axe 3 niveau 2
sources: [DREES Dossiers n°76 (2021) p.46, docs/lab/explorations/drees-projections-and-apl.md, docs/lab/derivations/workforce-projection-model.md]
tags: [validation, axe3, long-terme, 2050, pre-registration]
---

# Niveau 2 — long terme 2050 (protocole pré-enregistré)

> **Headline:** protocole **gelé, non lancé**. À 2050, on ne mesure pas une
> précision : on vérifie que le moteur (a) **reproduit le tendanciel
> DREES n°76** quand on lui donne les hypothèses de la DREES, à ±2 % en
> 2030 et ±3 % en 2050, et (b) **respecte trois cas limites analytiques**.
> Un échec bloque tout chiffre 2050.

## Question
Les données vont de 2012 à 2026 ; 2050 est 24 ans après. Aucune précision
ne peut être annoncée à 2050 (décision 2026-11-14). Que peut-on alors
falsifier ?

## Partie A — reproduction du tendanciel DD76

### Cible (citée, pas recalculée)
DREES, Dossiers n°76, mars 2021, p. 46 ; effectifs actifs < 70 ans, France
entière, au 1er janvier
([exploration](../../../../docs/lab/explorations/drees-projections-and-apl.md)).

| Profession | 2020 | 2030 | 2040 | 2050 | Forme |
|---|---|---|---|---|---|
| Chirurgiens-dentistes | 41 800 | 45 900 | 53 900 | 61 800 | croissance |
| Pharmaciens | 72 600 | (creux 71 000 en 2027) | 76 600 | 81 100 | creux puis reprise |
| Sages-femmes | 23 000 | 26 200 | 28 600 | 29 300 | plateau, maximum 29 400 en 2048 |

### Hypothèses DD76 à imposer au moteur (scénario `dd76_tendanciel`)
- **Périmètre DD76** : tous modes d'exercice, pas le « libéral ». La
  reproduction valide le **moteur**, pas la part privée.
- Origine 2020, données ≤ 2020 seulement.
- Taux de sortie et de transition : moyennes 2016–2020 (« comportements
  constants »), par âge × sexe.
- Entrées : quotas / numerus clausus et part de diplômés étrangers tenus à
  leur niveau 2016–2020, décalés de la durée des études.
- Pas d'autre levier.

### Comparaison
- **En ratios**, pas en niveaux : g(t) = N(t) / N(2020), pour neutraliser
  l'écart de périmètre (nos effectifs 2020 dépassent DD76 de +0,8 % à
  +2,5 %, qui inclut les ≥ 70 ans).
- Écart = g_nous(t) / g_DD76(t) − 1, en 2030, 2040 et 2050.
- **Tolérance (choisie, pas dérivée) : |écart| ≤ 2 % en 2030, ≤ 3 % en
  2040 et 2050.**
  - Pourquoi : la DREES publie qu'un quota ±20 % déplace l'effectif 2050
    de ±12 % (SF) à ±13 % (PH). Une erreur de reproduction de 3 % reste
    quatre fois plus petite que l'effet du levier le plus étudié : le levier
    reste lisible.
- **Forme :** pharmaciens, minimum entre 2024 et 2030 sous le niveau 2020 ;
  sages-femmes, croissance 2040→2050 < 1/3 de celle de 2030→2040.

### Ce qui falsifie
- Un écart hors tolérance, pour une profession → pas de chiffre 2050 pour
  elle. On décompose alors l'écart (entrées / sorties / vieillissement)
  avant toute correction.
- **Garde-fou contre l'ajustement :** on n'a pas le droit de régler un
  paramètre libre pour atteindre la cible. Seules les hypothèses ci-dessus
  sont imposées ; si le moteur ne reproduit pas, c'est un résultat.

### Repère connu
DD76 a sous-estimé les effectifs 2026 de 4 à 7 % en 6 ans
([exploration](../../../../docs/lab/explorations/drees-projections-and-apl.md), §
contrôle). La reproduction n'est donc pas une précision : c'est la preuve
que notre moteur et celui de la DREES disent la même chose sous les mêmes
hypothèses.

## Partie B — cas limites analytiques
Ils viennent de la
[dérivation](../../../../docs/lab/derivations/workforce-projection-model.md),
§ Limiting cases. Ils ne dépendent d'aucune donnée future.

| # | Cas | Test | Tolérance |
|---|---|---|---|
| L1 | h → 0 | `predict(origine)` = effectif observé à l'origine, par profession × territoire | écart relatif ≤ 1e-9 |
| L2 | h → ∞, scénario stationnaire (entrées Q constantes, taux constants) | (a) N(o + 200) / (Q · C) − 1, avec C = Σ_t N(t) d'une cohorte d'un entrant lancée dans un état vide ; (b) deux états initiaux (observé et observé × 0,5) donnent le même N(o + 200) | ≤ 1 % pour (a) et (b) |
| L3 | h < L (durée des études) | un quota +20 % à l'année t0 ne change pas N(t) pour t < t0 + L_p | écart relatif ≤ 1e-9 |
| L4 | conservation | Σ communes = département = national ; ΔN = entrées − sorties (+ plancher) | ≤ 1e-6 relatif |

L4 est déjà testé par l'axe 0 (`v2/jumeau/check.py`) ; on le reprend tel
quel.

**Ce qui falsifie :** un seul cas limite raté invalide le modèle pour les
affirmations à 2050. Par exemple, une rétention > 1 qui se capitalise
(le bogue K1) casse L2.

## How
- **Code :** [`v2/validation/limits.py`](../../../validation/limits.py).
  Il s'applique à tout estimateur qui expose `trajectory(until, scenario)`
  et accepte un scénario stationnaire. Vérifié sur un modèle jouet
  ([`selftest.py`](../../../validation/selftest.py)), pas encore sur le
  jumeau.
- **Partie A non lancée :** il faut un scénario `dd76_tendanciel` (entrées
  par la filière, taux 2016–2020), qui relève de l'axe 0 / axe 1.

## ⚑ What could make it wrong
- Reproduire DD76 ne prouve pas que DD76 avait raison ; on sait déjà qu'il
  sous-estimait de 4 à 7 % en 6 ans.
- La tolérance de 3 % est un **choix** fondé sur la taille d'un levier, pas
  une dérivation.
- Le passage du périmètre « tous modes » au « privé » n'est pas validé par
  la partie A ; il dépend de la séparation public / privé (axe 4).
- L2 suppose un scénario stationnaire. Avec retraite non stationnaire
  (cumul emploi-retraite, ROADMAP § 2), N* bouge ; on teste le moteur, pas
  le monde.

## → What it changes
- Aucun chiffre « libéral » 2050 n'est montré sans les parties A et B
  passées, et sans la bande de l'axe 5.
- Axe 0 : le jumeau doit permettre un scénario sans aucun module ajusté sur
  les données (taux imposés) ; sinon L2 n'est pas testable.

## ? Next
| Item | Cost |
|---|---|
| Lancer L1–L3 sur `TwinEstimator` dès que la composition par défaut est stable | ~15 min Claude |
| Construire le scénario `dd76_tendanciel` (entrées par quota décalées, taux 2016–2020) et lancer la partie A | ~1 h Claude |
| Ajouter infirmiers (ER n°1319, 2021→2050, +37 %) comme 4e cible, en ratios | ~20 min |

---

## Résultat partiel (ajouté après calcul, 2026-11-14) : partie A en entrées plates
`PYTHONPATH=v2 uv run --with scipy python -m validation.dd76` (~23 s) →
`v2/validation/out/dd76_results.json`.

**Écart à l'hypothèse du protocole.** Le protocole impose des entrées « par
quota, tenues au niveau 2016–2020, décalées de la durée des études ». Faute
de série ouverte des quotas 2016–2020 dans nos données, A a été lancé avec
les **entrées nettes moyennes 2016–2020, plates** (taux nationaux, tous
modes, origine 2020). C'est une version affaiblie, déclarée comme telle.

| Profession | Ratio 2030 nous / DD76 | 2040 | 2050 | Forme | Verdict |
|---|---|---|---|---|---|
| Dentistes | −3,3 % | −9,4 % | **−14,1 %** | — | échoue |
| Pharmaciens | — | −10,6 % | **−15,0 %** | creux en 2030 (−5 %) : passe | échoue |
| Sages-femmes | −7,9 % | −14,5 % | **−17,4 %** | plateau : passe | échoue |

**Exploratoire** (après avoir vu A) : la variante « entrées par la filière »
(`StockFlowLocalPipeline`, inscrits DREES 2020–2024) donne, en ratio 2050,
1,68 (CD) et 1,29 (PH), contre 1,48 et 1,12 pour DD76 : **elle dépasse
DD76 de 14 à 15 %**. DD76 se situe entre nos deux variantes. Attention : la
filière utilise des inscrits connus après 2020, donc une information future
pour une origine 2020.

**ER 1319 et dentistes :** voir le rapport [N7](2026-11-14-axe3-n7-addendum.md)
(D1 échoue, −25 % en 2050 ; D2 passe, résidu 16 %).

**Verdict N2-A :** échoue sous sa forme affaiblie. Aucun chiffre 2050 n'est
citable. Le moteur suit les entrées qu'on lui donne : à 2050, l'hypothèse
d'entrées domine tout (de −15 % à +15 % autour de DD76 selon la variante).

Cas limites L1–L3 sur le jumeau : non lancés cette nuit (ledger).
