---
type: analysis
date: 2026-11-15
author: axe 2 (session c1-budget-erreur)
question: Où est l'erreur de C1 et de A2 au banc départemental à h = 5, et un modèle plus riche (gravitaire, agents, apprentissage) peut-il la réduire ?
headline: "MAPE C1 7,76 % [7,12 ; 8,40] : plancher de bruit poissonien 3,11 [2,89 ; 3,36] ; l'écart local des entrées (−2,60 [2,20 ; 3,05] si connu) et du milieu de carrière (−2,36 [2,00 ; 2,71]) dominent, le national pèse 0,49 ; l'écart local ne persiste pas d'une fenêtre à l'autre (r ≤ 0,24) — pas de modèle gravitaire ni à agents sans covariable qui l'explique"
status: final
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "L'erreur est dominée par un bruit imprévisible au département ; un modèle plus riche ne gagnerait rien."
sources: [v2/methodes/perimetres.py (prive), data/processed/stock.parquet, v2/data/processed/secteur_stock.parquet]
tags: [axe2, backtest, budget-erreur, mobilite]
---

# Budget d'erreur de C1 et A2 (banc N1, privé, h = 5)

> **Headline :** sur 2 056 couples département × cellule, la MAPE de C1 vaut 7,76 % (mesuré) [7,12 ; 8,40]. Un plancher
> de bruit poissonien en explique 3,11 points (dérivé). Le reste est surtout **local** : la répartition des entrées
> entre départements (gain de 2,60 points si elle était connue) et celle des cohortes de 35 à 59 ans (2,36 points).
> Le niveau national ne pèse que 0,49 point, la retraite 0,22. L'écart local ne persiste presque pas d'une fenêtre
> de 5 ans à la suivante (r = 0,02 à 0,24 (mesuré)) : l'historique des stocks ne peut pas l'apprendre.

## Question
Avant de choisir une méthode plus riche que les variantes stock-flux (qui tiennent toutes dans 0,4 point, `tab:prive`),
où est l'erreur ? Hypothèse à tester : elle est dominée par un bruit imprévisible au département.

## Plan (contrainte, test d'abandon)
- **Contrainte :** points de MAPE départementale à h = 5, sur le protocole N1 (SHA eb527ecb06a0), mêmes origines et
  cellules que `tab:prive`. Écart structurel entre variantes : 0,4 point (mesuré). Une composante ne justifie un modèle
  dédié que si (a) son gain réaliste (écart local réduit d'un quart) dépasse 0,4 point et (b) son écart local
  persiste d'une fenêtre à l'autre (r ≥ 0,3), sinon rien ne permet de l'apprendre.
- **Test d'abandon de l'hypothèse :** le plancher de bruit poissonien atteint au moins 50 % de la MAPE de C1. Verdict
  attendu avant passage : rejeté (plancher ≈ 3 à 4 points pour ≈ 8).
- Les critères (a) et (b), l'oracle partiel et le test de persistance ont été ajoutés **après** un premier passage
  (oracles complets et plancher seulement). Ils sont donc exploratoires.

## Méthode
Avec des tranches de 5 ans et h = 5, la tranche b à la cible vient exactement de la tranche b − 5 à l'origine. La
prévision du département se coupe en trois blocs selon l'âge à la cible :
- **Y**, moins de 35 ans : surtout des entrées (installations) ;
- **M**, 35 à 59 ans : cohortes en milieu de carrière (mobilité entre départements, sorties précoces) ;
- **R**, 60 ans et plus : retraites.

L'erreur relative signée est la somme exacte e = e_Y + e_M + e_R. Chaque e_k se coupe en une part **nationale**
(total national du bloc par sexe × tranche) et une part **locale** (répartition entre départements). Oracles, une
composante à la fois : bloc exact ; niveau national exact (répartition du modèle) ; total national exact ; écart
local réduit de 25 % ou 50 %.

Le **plancher de bruit** suppose des événements indépendants : Var(N_T) ≈ F, F = Σ |solde de cohorte|, et
E|N_T − E N_T| ≈ √(2F/π). F est une borne basse des flux bruts, donc ce plancher l'est aussi. Le surplus de
dispersion (cabinets de groupe, chocs locaux) est compté dans la part « locale ».

IC : bootstrap des départements, 2 000 tirages, graine 20261114, mêmes tirages que N1.

## Résultat

### Décomposition globale (points de MAPE, IC 95 %)
| | A2 shrinkage | C1 cohortes |
|---|---|---|
| MAPE h = 5 | 8,60 [7,80 ; 9,47] (mesuré) | 7,76 [7,12 ; 8,40] (mesuré) |
| Plancher de bruit poissonien | 3,11 [2,89 ; 3,36] (dérivé) | 3,11 [2,89 ; 3,36] (dérivé) |
| Part du plancher dans la MAPE | 36 % [34 ; 39] | 40 % [37 ; 43] |
| **Gain si le bloc était exact** | | |
| Y entrées (< 35 ans) | 2,94 [2,49 ; 3,44] | 2,84 [2,41 ; 3,26] |
| · dont répartition locale | 2,60 [2,16 ; 3,05] | 2,60 [2,20 ; 3,05] |
| · dont niveau national | 0,35 [0,03 ; 0,66] | 0,23 [0,03 ; 0,44] |
| M milieu de carrière (35–59) | 2,64 [2,13 ; 3,18] | 2,56 [2,23 ; 2,89] |
| · dont répartition locale (mobilité, borne haute) | 2,00 [1,58 ; 2,46] | 2,36 [2,00 ; 2,71] |
| · dont niveau national | 0,65 [0,44 ; 0,85] | 0,20 [0,09 ; 0,30] |
| R retraites (60+) | 0,23 [0,08 ; 0,40] | 0,22 [0,07 ; 0,37] |
| Total national exact (biais national) | 1,08 [0,67 ; 1,47] | 0,49 [0,20 ; 0,77] |
| **Gain réaliste : écart local réduit de 25 %** | | |
| Y | 0,76 [0,64 ; 0,88] | 0,70 [0,59 ; 0,82] |
| M | 0,63 [0,51 ; 0,77] | 0,71 [0,62 ; 0,80] |
| Écart local réduit de 50 % : Y / M | 1,37 / 1,18 | 1,29 / 1,30 |

Toutes les valeurs sont mesurées sur le banc, sauf le plancher (dérivé d'un modèle de Poisson).

Les gains ne s'additionnent pas : la MAPE est une valeur absolue, les erreurs des blocs se compensent en partie.
L'écart quadratique, lui, s'additionne.

**Parts de l'erreur quadratique (C1) (mesuré) :**
- Y local 45 %, M local 40 % ;
- Y national 6 %, M national 4 % ;
- R 6 %.

Le bruit poissonien fait 16 % de l'erreur quadratique de C1 (13 % pour A2). C'est moins que sa part en MAPE, car la
MAPE écrase les grandes erreurs.

### Persistance de l'écart local (fenêtres disjointes 2016 → 2021, 273 départements × profession)
| Bloc | r A2 (mesuré) | r C1 (mesuré) |
|---|---|---|
| Y entrées | 0,17 | 0,02 |
| M milieu de carrière | 0,24 | 0,22 |
| R retraites | −0,08 | 0,16 |

Erreur type ≈ 0,06 (dérivé). Un correcteur fondé sur l'écart passé du département réduirait l'écart local d'environ
1 − √(1 − r²), soit **3 % au plus** (dérivé). Une seule paire d'origines est disponible : les kinés n'en ont aucune.

### Selon la taille du département (C1)
| Effectif à l'origine | Couples | MAPE (mesuré) | Plancher (dérivé) |
|---|---|---|---|
| 30–99 | 327 | 14,04 | 6,29 |
| 100–299 | 660 | 7,60 | 3,42 |
| 300–999 | 795 | 5,26 | 1,92 |
| 1 000 et plus | 274 | 5,49 | 1,07 |

La pente log APE / log N vaut −0,27 (mesuré), contre −0,54 pour le plancher. Les petits départements sont dominés
par le bruit. Les grands plafonnent à 5,5 %, cinq fois le plancher : il y reste une erreur structurelle qui ne
décroît pas avec l'effectif (chocs locaux corrélés, et pour A2 le biais national).

### Par profession (C1, points de MAPE)
| Profession | MAPE | Plancher | Y local | M local | National total |
|---|---|---|---|---|---|
| Sages-femmes | 11,96 | 4,86 | 3,77 | 4,17 | 1,07 |
| Dentistes | 8,03 | 3,14 | 4,04 | 1,45 | 0,19 |
| Kinés | 6,51 | 1,93 | 2,57 | 1,38 | 0,34 |
| Infirmiers libéraux | 4,93 | 1,76 | 0,72 | 2,05 | 0,36 |
| Pharmaciens | 4,91 | 2,22 | 0,95 | 1,78 | 0,29 |

Toutes les valeurs sont mesurées, sauf le plancher (dérivé). Les IC sont dans `v2/methodes/out/budget_erreur.json`.

Le profil diffère selon la profession :
- **dentistes et kinés** : l'erreur est dans la répartition des installations ;
- **infirmiers et pharmaciens** : elle est dans le milieu de carrière ;
- **sages-femmes** : les deux, avec en plus un biais national encore net chez A2 (3,24 points, 1,07 chez C1).

## Verdict
1. **Hypothèse « bruit imprévisible dominant » : rejetée sous sa forme forte.** Le plancher poissonien fait 40 % de
   la MAPE de C1 (seuil : 50 %).
   - **Forme faible : tenue.** Ce qui reste est local, et ne se prévoit pas à partir de l'historique du département
     (r ≤ 0,24).
   - En pratique, avec les seules données de stock, l'erreur atteignable est proche de l'erreur actuelle. Seule une
     **covariable extérieure** (attractivité, zonage, ouverture de structures) peut réduire l'écart local.
2. **Composante la plus lourde : la répartition locale des entrées (Y local).**
   - Gain de 2,60 points au plus (oracle) ;
   - 0,70 point si un modèle en expliquait le quart de l'amplitude.
   - Elle est suivie de près par la répartition locale du milieu de carrière : 2,36 au plus, 0,71 réaliste.
3. **Mobilité entre départements, modèle gravitaire ou à agents : non justifié aujourd'hui.**
   - Le bloc M local borne leur gain à 2,0 à 2,4 points. Cette borne contient aussi les sorties précoces locales et
     11 à 17 % de bruit.
   - Critère (a) tenu : le gain réaliste vaut 0,6 à 0,7 point, au-dessus de 0,4.
   - Critère (b) non tenu : r = 0,22 à 0,24, sous 0,3.
   - Sans flux origine → destination ouverts, un modèle gravitaire n'est pas calable. Le modèle à agents était déjà
     tué a priori (décision « Axe 2 : dynamique des systèmes… », 2026-11-14).
   - Un réseau profond appris sur les mêmes panneaux de stock n'a rien à apprendre de plus : la persistance est trop
     faible.
4. **Le niveau national n'est plus le problème pour C1** (0,49 point, contre 1,08 pour A2). Une partie du gain de C1
   sur A2 vient de là : 0,59 point sur les 0,84 d'écart (dérivé).

## ⚑ Ce qui pourrait rendre ce résultat faux
- **Le plancher est une borne basse.** Il prend le solde net de chaque cohorte, pas les flux bruts : les entrées
  et sorties qui se compensent dans une même tranche n'y sont pas. Avec des flux bruts deux fois plus grands, il
  monterait vers 4,4 points (supposé), soit 57 % de la MAPE de C1. Le test d'abandon basculerait. Sans panel
  individuel, cette borne ne peut pas être resserrée.
- **Le découpage par âge est un proxy.** Les entrées après 35 ans (reconversions, passage du salariat au libéral)
  tombent dans le bloc M, qui mêle donc mobilité, sorties précoces et entrées tardives. La « mobilité » mesurée ici
  est une borne haute.
- **La persistance repose sur une seule paire d'origines** (2016 → 2021), sans les kinés. r ≈ 0,2 ± 0,06 ne
  distingue pas « faible » de « nul » pour Y avec C1.
- **Reproduction : 8,60 contre 8,57 publié pour A2, 7,76 contre 7,73 pour C1.** L'écart vient de la table privée
  des sages-femmes, modifiée depuis le banc (jusqu'à 4,5 personnes par département ; les quatre autres professions
  sont identiques à 0 près).
- **Oracle « national par sexe × tranche » :** il garde la répartition du modèle. Sa part « locale » mêle donc
  l'erreur de répartition et l'interaction avec le niveau.

## → Ce que ça change
- **Axe 2, choix de la méthode suivante :** pas de modèle gravitaire ni à agents. L'effort va vers des covariables
  de la répartition locale des entrées, avec un test de régression peu coûteux d'abord (voir ? Suite).
- **Axe 2 / C1 probabiliste** (session c1-intervalles) : 85 % de l'erreur quadratique (Y local + M local) est
  locale et peu persistante. Ce bruit est sur-dispersé par rapport à Poisson, d'un facteur MSE / bruit ≈ 6 (dérivé).
  Les intervalles de C1, trop étroits (PIT en U), doivent porter cette dispersion locale. C'est la piste qui
  rapporte le plus pour un coût faible.
- **Article axe 2 (`tab:prive`) :** ajouter une ligne « plancher de bruit 3,1 points ». Elle situe l'écart de
  0,4 point entre variantes.
- **Sages-femmes :** la table privée a changé depuis le banc. Relancer `methodes.banc` et `methodes.banc_cohortes`
  avant de citer de nouveau 8,57 et 7,73.

## ? Suite
| Question | Prix |
|---|---|
| Régresser l'écart local Y et M de C1 sur des covariables ouvertes : zonage conventionnel, densité pour 100 000 habitants, croissance de la population (Insee), âge moyen du stock, présence d'une école. Si R² ≥ 0,2 hors échantillon, un modèle de choix d'installation devient justifié | ~45 min Claude + ~1 min machine |
| Sur-dispersion de C1 : variance prédictive α·μ + β·μ² calée sur ces résidus, puis couverture à 80 % au banc N6 | ~30 min, à confier à la session c1-intervalles |
| Plancher sur flux bruts, avec un instantané Annuaire Santé apparié individuellement (2 dates) | ~1 h 30 Claude + téléchargement |
| Persistance sur plus de paires : origines décalées de 4 ans (fenêtres qui se chevauchent d'un an) | ~10 min |
| Relancer les bancs N1 et N6 sur la table privée actuelle (sages-femmes modifiées) | ~10 min machine |

## Reproduire
```bash
PYTHONPATH=v2 uv run --with scipy python -W ignore -m methodes.budget_erreur > v2/methodes/out/budget_erreur.log
```
- Durée : ≈ 6 min machine (mesuré), dont 22 ajustements de C1.
- Le cache des prévisions par âge est `v2/methodes/out/budget_erreurs.parquet`, ignoré par git. Supprimer ce
  fichier pour relancer l'ajustement.
- Sorties : `budget_erreur.json` et `budget_erreur.log`.
- Script : [`v2/methodes/budget_erreur.py`](../../../methodes/budget_erreur.py).
