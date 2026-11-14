---
type: derivation
date: 2026-11-14
author: Claude (session axe 2)
question: Quelles méthodes interprétables peuvent prévoir l'effectif par département mieux que le stock-flux à taux locaux ?
status: 4 promues · 2 en attente (parked) · 1 tuée
---

# Axe 2 : quelles méthodes peuvent battre le stock-flux à taux locaux ?

**Dérivé :** 2026-11-14, en environ 10 min (une séance).
**Statut :** 4 ansätze promues au banc (A1a, A1b, A2, A3, plus leur
combinaison pré-spécifiée), 2 en attente (A5, A4), 1 tuée pour N1 (A6).

## Problème
- **Objectif.** Minimiser la MAPE par département à h = 5 (protocole N1,
  en %), à interprétabilité égale. Chaque paramètre doit avoir un nom, une
  unité, et un levier qui le touche.
- **Contrainte.** Recalcul < 2 s par scénario (supposé, profil). Aujourd'hui
  18 ms au département (mesuré, axe 0). Une méthode ne doit pas
  multiplier ce temps par plus de 10 sans mesure.
- **Variables libres :**
  - l'opérateur de vieillissement ;
  - la structure de partage entre territoires (le shrinkage) ;
  - la dépendance au temps de la rétention ;
  - la règle de répartition des entrées.

## Structure
- **Linéarité.** Sans le plancher à 0, le stock-flux est linéaire en N :
  N(t+1) = S·A·N(t) + I.
  - Toute méthode dont l'espérance obéit à la même récurrence (par exemple
    une microsimulation avec les mêmes taux) donne **la même prévision
    ponctuelle**.
  - Elle ne peut donc pas changer la MAPE, seulement la bande.
- **Absorption dans l'échantillon.** La rétention s est ajustée *après*
  l'opérateur de vieillissement A.
  - Une erreur sur A est donc compensée, dans la fenêtre, par s.
  - Elle ne réapparaît hors échantillon que si la structure par âge à
    l'intérieur des tranches change par rapport à la fenêtre, par exemple
    une génération nombreuse qui arrive dans les 60–64 ans.
  - Prédiction dérivée : le gain des âges fins est **petit à h = 5 sur les
    totaux**. Il est plus grand sur la part des 60 ans et plus et à long
    horizon.
- **Échelles de temps.**
  - Vieillissement : 5 ans par tranche.
  - Dérive de la rétention des seniors : environ 10 ans (+1 527 pharmaciens
    de plus de 65 ans en 2026, mesuré en v1).
  - Bruit d'échantillonnage d'un département : instantané, en 1/√N.
- **Où est l'erreur.** D'après K1, l'erreur par département est dominée par
  la répartition territoriale et par le niveau des entrées, pas par la
  structure par âge (cité, rapport K1). Prédiction : les shrinkages et les
  entrées l'emportent sur les âges fins.

## Cas limites
| Limite | Ce qui gagne | Conséquence |
|---|---|---|
| h → 0 | la persistance ; toute méthode qui part de l'état observé | toutes les ansätze partent de N(origine) : la limite est respectée |
| N_dép → ∞ | les taux locaux bruts | le shrinkage doit disparaître : (num + k·r)/(den + k) → num/den. Respecté |
| N_dép → 0 | les taux régionaux ou nationaux | le shrinkage à deux niveaux tire vers la région avant le national |
| fenêtre stationnaire en âge | vieillissement uniforme = âges fins | A1 ne gagne rien ; gain nul attendu pour les professions à pyramide plate |
| tendance de rétention nulle | A3 = référence | A3 ne perd rien si la pente est nulle ; risque de surextrapolation si h ≫ fenêtre |

## Isomorphisme
| Ici | Ailleurs | Statut |
|---|---|---|
| shrinkage des taux départementaux | estimation sur petits domaines (Fay-Herriot, Bayes empirique) | intuition |
| âges fins à partir de tranches | désagrégation de Sprague / Beers en démographie | claim (testé par un monde simulé) |
| rétention des seniors en tendance | Hippocrate : départs à la retraite en tendance | intuition |
| choix de l'installation | logit conditionnel de McFadden, équivalent à une régression de Poisson à effets fixes | claim (équivalence mathématique) |

**Où ça casse.**
- Fay-Herriot suppose une variance d'échantillonnage connue ; ici k = 200
  est fixé et non estimé.
- La désagrégation de Sprague suppose une densité lisse ; la tranche
  ouverte 65+ ne l'est pas.

## Ansätze
- **A0 (base).** Stock-flux à taux locaux, `twin_of(StockFlowLocal)`. Les
  références naïves sont la persistance et la tendance.
- **A1a, vieillissement non uniforme dans la tranche.** Chaque année, on
  désagrège chaque tranche en âges simples : densité linéaire par morceaux
  entre les milieux de tranches, masse conservée. On vieillit d'un an, puis
  on réagrège.
  - Le même opérateur sert à l'ajustement de s et à la projection, ce qui
    rend la méthode cohérente.
  - La fraction qui quitte une tranche dépend de la cellule et de l'année.
  - Paramètre touché par un levier : aucun nouveau. Les leviers de retraite
    agissent sur s, comme dans A0.
- **A1b, âges en années simples.** L'état est N[cellule, âge simple], de 20
  à 74 ans et plus. Il est désagrégé une fois à l'origine, puis vieillit
  exactement d'un an : les cohortes sont suivies.
  - s est ajusté par tranche, avec le même opérateur que A1a. Les entrées
    de la tranche sont réparties uniformément sur ses âges (supposé).
- **A2, shrinkage hiérarchique.**
  r_dép = (num + k·r_rég)/(den + k), avec
  r_rég = (num_rég + k·r_nat)/(den_rég + k), k = 200 aux deux niveaux.
  - k = 200 est repris de la v1 et de l'observatoire ; il n'est pas réglé
    sur le banc.
- **A3, rétention des 60 ans et plus en tendance.**
  - Pente nationale b (profession × sexe × tranche ≥ 60), par moindres
    carrés sur les ratios annuels de la fenêtre.
  - s(t) = min(1, s_cellule + λ·b·(t − t̄)), où t̄ est le milieu de la
    fenêtre.
  - **Levier : λ** (`methodes_sorties.tendance_60plus`, 1 = tendanciel,
    0 = stationnaire). Les leviers retraite et cumul agissent ensuite.
- **A123, combinaison pré-spécifiée.** A1a + A2 + A3.
- **A4, choix discret de l'installation.**
  - Avec des effets fixes départementaux, le logit reproduit exactement les
    parts observées. Il n'apporte donc rien à la prévision ponctuelle
    tant qu'aucun attribut ne varie dans le temps.
  - Sa valeur est d'être un mécanisme de levier : la régulation déplace
    l'utilité.
  - **En attente.** On le reprend dès qu'un attribut daté par département
    existe (population Insee 1975–2026, C2, axe 4).
- **A5, modèle bayésien hiérarchique ou espace-état.**
  - Au département avec N ≥ 30, la moyenne a posteriori ≈ le Bayes
    empirique d'A2.
  - Le gain porte sur la bande et sur les petites communes, donc relève du
    niveau N4, pas de N1. **En attente.**
- **A6, microsimulation individuelle.** Même espérance que A0 par
  linéarité. **Tuée pour N1** ; elle reste possible pour les bandes et
  pour des règles non linéaires, comme la régulation par commune.

## Kill tests
| Test | Discrimine | Résultat qui tue | Prix |
|---|---|---|---|
| Monde simulé à âges simples connus (cohortes inégales), ajusté sur tranches | A0 contre A1a/A1b | A1 ne réduit pas l'erreur sur les 60 ans et plus de plus de 1 point | ~10 min |
| Banc N1, Δ IC 95 % | toutes contre la meilleure naïve, et contre A0 (exploratoire) | borne basse > 0 contre la meilleure naïve | ~2 min machine |
| B4 : borne r ≤ 1,2 de l'observatoire sur nos données | emballement des entrées | croissance nationale projetée > 2 × l'observée | ~10 min |

## Pré-inscription (avant tout passage sur le banc, 2026-11-14 ~03:25)
- **Variantes confirmatoires**, inscrites dans `v2/validation/registry.py`
  avant le premier passage : `axe2_ages_interp` (A1a),
  `axe2_ages_simples` (A1b), `axe2_shrink_hier` (A2),
  `axe2_retention60` (A3) et `axe2_combine` (A123).
- **Diagnostic :** `axe2_obs_r12` (B4), marqué « diagnostic ». Il n'est pas
  candidat.
- **Périmètre confirmatoire : privé**, variante centrale
  (`jumeau.history.sector_table`). L'axe 4 a livré la séparation
  public / privé, donc le protocole N1 bascule sur le périmètre cible.
  - Exception, les infirmiers : l'axe 4 ne donne pas d'âge pour les
    salariés privés. On garde les infirmiers libéraux (RPPS), et c'est dit.
- **Périmètre secondaire : l'ancien** (`mode3 == liberal_mixte`), seulement
  pour la comparaison avec K1.
- **Multiplicité.** 5 variantes confirmatoires contre la même barre. On
  rapporte l'IC brut et on signale toute victoire qui ne tiendrait pas à
  α/5 (Bonferroni, IC à 99 %).
- **Prédictions écrites avant le banc (supposées) :**
  - |Δ(A1a ou A1b, A0)| < 0,3 point de MAPE ;
  - A2 améliore A0 de 0 à 0,3 point ;
  - A3 réduit le |biais national| pour PH et CD.

## Verdicts a priori
- A1a, A1b, A2, A3 et A123 : **promues** ; c'est le banc qui tranche.
- A4 : **en attente** (un attribut daté manque ; pas de gain ponctuel avec
  effets fixes).
- A5 : **en attente** (relève du niveau N4).
- A6 : **tuée pour N1** (linéarité).

## Passation
- Rapport : `v2/docs/lab/reports/2026-11-14-axe2-methodes.md`.
- Décisions et questions ouvertes : `v2/docs/lab/decisions.md` et
  `open.md`.
