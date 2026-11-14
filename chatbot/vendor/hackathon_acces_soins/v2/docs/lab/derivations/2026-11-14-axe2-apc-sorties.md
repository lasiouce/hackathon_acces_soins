---
type: derivation
date: 2026-11-14
author: Claude (session axe 2)
question: Comment modéliser les sorties en âge-période-cohorte bayésien quand on n'observe que des stocks par tranche de 5 ans ?
status: 1 promue (APC gaussien sur la rétention nette) · 1 tuée (Poisson sur sorties reconstruites)
---

# Étape 1 du programme de l'axe 2 : sorties en âge-période-cohorte (APC) bayésien

**Dérivé :** 2026-11-14, environ 10 minutes. **Statut :** une ansatz promue, une
tuée.

## Problème
- **Objectif.** Une rétention nette par cellule × tranche × année, avec une
  incertitude propagée et un effet de période qu'un levier peut déplacer,
  pour une MAPE dép. à h = 5 (protocole N1) au moins égale à celle du
  stock-flux à taux locaux (A0, 8,68 %), et une prévision probabiliste
  calibrée (CRPS, PIT).
- **Contraintes.**
  - Un statisticien vérifie le modèle en une demi-journée.
  - Le recalcul reste sous 2 s.
  - Outils installables par uv, sans compilateur exotique.
- **Variables libres :**
  - la vraisemblance ;
  - la décomposition âge / période / cohorte ;
  - les a priori ;
  - l'estimation des hyperparamètres.

## Ce qu'on observe vraiment (identification)
- Le RPPS donne des **stocks** N[dép, sexe, tranche de 5 ans, année], pas
  les cessations.
- La seule quantité observable est le ratio de cohorte
  r = N(a, t+1) / A(N(t))(a), où A est le vieillissement d'un an. Ce ratio
  mélange les flux suivants :
  - décès et cessations ;
  - reprises d'activité ;
  - changements de mode ou de secteur ;
  - **déménagements entre départements**.
- r peut dépasser 1 : dans un département, D = A(N) − N(t+1) est **négatif**
  dans 27 à 47 % des cellules de 35 ans et plus (mesuré pour B4,
  [rapport](../reports/2026-11-14-axe2-methodes.md)).

### Option 1 : Poisson sur des sorties reconstruites D — **tuée**
- La loi de Poisson exige D ≥ 0.
- Tronquer D à 0, ou séparer entrées et sorties, invente une donnée qu'on
  n'a pas : on ne connaît que le solde.
- Le modèle aurait l'air d'un modèle de cessations alors qu'il n'en
  observe aucune.

### Option 2 : gaussien sur le log de la rétention nette — **promue**
- On pose y = log((N(a, t+1) + ½) / (A(N(t))(a) + ½)).
  - La variance d'échantillonnage est approximativement binomiale :
    Var ≈ (1 − r)/(r·B), qui décroît en 1/B (B = effectif exposé).
  - Elle est modélisée par σ_e²/B + ω², avec ω² pour les déménagements et
    les chocs.
- Le paramètre s'interprète comme une **rétention nette**, ce qui est
  honnête : pas des cessations.
- Le modèle est linéaire et gaussien conditionnellement aux
  hyperparamètres.
  - La loi a posteriori est donc **exacte et gaussienne** (un champ
    gaussien de Markov), sans MCMC.
  - Elle se vérifie par une simple algèbre linéaire : il suffit de numpy
    et scipy.

### Ce qu'on ne peut pas identifier
- **Âge, période et cohorte sont liés linéairement** : cohorte = période −
  âge. Seules les courbures sont identifiées ; la répartition des
  tendances linéaires entre les trois effets est fixée par les a priori.
- **Avec 14 transitions annuelles et 9 tranches de 5 ans, l'effet cohorte
  est faiblement contraint** (dérivé).
  - Une tranche contient 5 générations, donc chaque observation moyenne la
    cohorte sur 5 années de naissance.
  - Une génération ne traverse que 2 à 3 tranches dans la fenêtre.
  - On le mesure par le rapport entre l'écart-type a posteriori et
    l'écart-type a priori de l'effet cohorte. Proche de 1, la donnée n'a
    rien appris.
- La **projection** d'une marche aléatoire d'ordre 1 est plate, avec une
  variance qui croît linéairement.
  - On ne prolonge **pas** la pente. A3, qui prolongeait la pente de la
    rétention des 60 ans et plus, a échoué au banc (+0,33 pt).
  - L'ordre 1 est donc pré-spécifié. L'ordre 2, qui prolongerait la pente,
    est rejeté a priori.

## Modèle (une page)
Pour chaque profession × sexe, et pour chaque observation i = (dép d,
tranche a, année d'arrivée τ), restreinte aux tranches où la rétention
nationale de la fenêtre est ≤ 1 :

    y_i ~ N(η_i, σ_e² / B_i + ω²)
    η_i = μ_a + π_{g(a), τ} + γ_{τ − a} + v_{rég(d), a} + w_{d, a}

- μ_a ~ N(0, 10²) : niveau par tranche.
- π_{g,τ} : effet de période, une marche aléatoire d'ordre 1 par groupe
  d'âge g (< 35 ans, 35–59 ans, ≥ 60 ans), avec π_{g,1} ~ N(0, 1) et des
  incréments N(0, σ_π²).
- γ_κ : effet de cohorte, une marche aléatoire d'ordre 1 sur κ = τ − âge
  bas de la tranche (en années), avec des incréments N(0, σ_γ²).
- v_{r,a} ~ N(0, τ_r²) : écart région × tranche.
- w_{d,a} ~ N(0, τ_d²) : écart département × tranche.
  - C'est la version estimée du shrinkage A2 : la force du rétrécissement
    vient des données au lieu de k = 200.
- **Hyperparamètres** θ = (σ_π, σ_γ, τ_r, τ_d, σ_e, ω).
  - Ils sont estimés par maximum de la vraisemblance marginale (Bayes
    empirique de type II), et la loi a posteriori des effets est exacte
    sachant θ̂.
  - Limite assumée : l'incertitude sur θ n'est pas propagée.
- **Prévision.**
  - On prolonge π_{g,τ} = π_{g,T} + Σ ε, ε ~ N(0, σ_π²).
  - Une cohorte nouvelle prolonge la marche de la dernière cohorte vue.
  - s = min(1, exp(η)) : le plafond est le même que dans A0, et les
    entrées absolues I de A0 restent inchangées.
- **Prévision probabiliste.** On fait S = 100 tirages des effets a
  posteriori, des innovations futures et du bruit annuel, puis on projette
  chaque tirage dans le jumeau.
- **Levier.** `apc_sorties.periode_60plus` est un décalage additif du log de
  la rétention des ≥ 60 ans, à partir d'une date. C'est l'effet d'une
  réforme des retraites ou du cumul emploi-retraite, exprimé comme un choc
  de période.

## Limites et cas limites
| Limite | Ce qui se passe |
|---|---|
| σ_π → 0 | la période est constante, et l'on retrouve la rétention moyenne de la fenêtre, comme A0 avec un shrinkage estimé |
| B → ∞ | la donnée domine, et w_{d,a} rejoint le ratio local |
| τ_d → 0 | taux régionaux (proche de A2 avec k → ∞ au département) |
| h → 0 | l'état observé est conservé (la limite h = 1 de N1 doit passer) |

## Kill tests (pré-écrits)
| Test | Résultat qui tue | Prix |
|---|---|---|
| Calibration par simulation : 100 jeux simulés avec θ connu, rang de π_{60+,T} et de γ parmi les tirages a posteriori | rangs non uniformes (KS p < 0,01) avec θ connu : erreur de code | ~5 min machine |
| Contrôle prédictif a posteriori : couverture à 90 % de y dans l'échantillon | couverture < 80 % ou > 98 % | ~1 min |
| Banc N1 (MAPE h = 5), inscrit avant passage | borne basse de Δ contre la meilleure naïve > 0 ; contre A0, rapporté (exploratoire) | ~5 min machine |
| CRPS relatif et PIT à h = 5 | PIT nettement non uniforme ; couverture à 80 % hors de [70 ; 90] % | inclus |

## Prédictions écrites avant le banc (supposées)
- **MAPE h = 5 :** |Δ(APC, A0)| < 0,3 pt.
  - Le gain éventuel vient de l'effet de période récent : la dernière
    valeur, au lieu de la moyenne de la fenêtre.
  - Le risque vient du même endroit.
- **Effet cohorte :** il apprend peu ; sd a posteriori / sd a priori > 0,7
  pour la majorité des cohortes.
- **Couverture à 80 % des intervalles prédictifs dép. à h = 5 :** sous la
  valeur nominale, entre 55 et 80 %. L'incertitude sur θ et les ruptures
  ne sont pas modélisées.
