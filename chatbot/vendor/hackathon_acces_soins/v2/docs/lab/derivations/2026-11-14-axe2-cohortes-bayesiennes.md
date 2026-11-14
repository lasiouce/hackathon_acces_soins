---
type: derivation
date: 2026-11-14
author: axe 2
question: Comment rendre probabiliste toute l'identité des cohortes (rétention et entrées), avec des a priori hiérarchiques par territoire, pour obtenir une bande calibrée ?
status: 2 promues (C1 θ fixé, C2 θ propagé) · 2 en attente (commune, logit) · 1 tuée (MCMC complet)
---

# Étape 2 du programme : cohortes par composantes en bayésien hiérarchique, entrées comprises

**Dérivé :** 2026-11-14, environ 15 minutes. **Point de départ :**
l'[étape 1](../reports/2026-11-14-axe2-apc-sorties.md). L'APC égale le
stock-flux, mais sa bande couvre 50 % au lieu de 80 % : les entrées n'y sont
pas incertaines, et θ est fixé.

## Problème
- **Objectif.**
  - Une distribution prédictive de N[dép, h = 5] calibrée : couverture de
    l'intervalle à 80 % dans [75 ; 85] %, et de l'intervalle à 50 % dans
    [44 ; 56] % (protocole N6, gelé).
  - Un CRPS sur log N inférieur à celui de la meilleure naïve
    probabiliste.
  - Sans dégrader la MAPE de N1, aujourd'hui 8,68 % pour A0.
- **Contraintes.**
  - Les équations tiennent sur une page ; chaque paramètre a un a priori
    écrit, une source et un sens.
  - Recalcul < 2 s.
  - Outils numpy et scipy.
- **Variables libres :**
  - le modèle des entrées ;
  - la façon de propager θ ;
  - le grain.

## Structure
- **Identité comptable par cellule (dép × sexe × tranche).** On écrit
  N(a, τ) = s·B(a, τ−1) + E(a, τ), avec B l'exposé après vieillissement
  d'un an.
  - Dans les tranches où la rétention nationale est ≤ 1, s vient de l'APC
    (étape 1) et E = 0.
  - Dans les autres tranches (les plus jeunes), s vient de A0 et le flux
    net E est modélisé.
- **Où est l'erreur.**
  - Par département, elle vient surtout des entrées (K1 ; ablation de
    l'axe 2).
  - Au national, elle vient du niveau des entrées : biais de A0 de +1,5 %
    à h = 5, mesuré.
  - Il y a donc deux sources à modéliser : le **niveau national** des
    entrées, qui varie dans le temps, et la **répartition** entre
    départements, qui varie dans l'espace.
- **Échelles de temps.**
  - Le niveau national des entrées bouge avec les quotas, en 5 à 10 ans.
  - La répartition bouge lentement (C5 : la part du stock prédit la part
    des entrées, r = 0,996).
  - Le bruit annuel par département est rapide.

## Modèle des entrées (une page)
Pour chaque profession × sexe × tranche d'entrée a, et pour chaque
département d et année τ :

    e_{d,τ} = N(a,τ) − s_d·B(a,τ−1)                  (flux net observé, comme A0)
    M_τ = Σ_d e_{d,τ}                                (total national)
    M_τ = L_τ + u_τ,  L_τ = L_{τ−1} + v_τ            (niveau local : u ~ N(0, σ_u²), v ~ N(0, σ_v²))
    e_{d,τ} = π_d · M_τ · (1 + δ_{rég(d)} + ζ_d) + ε_{d,τ}
    δ ~ N(0, τ_r²),  ζ ~ N(0, τ_d²),  ε ~ N(0, σ_ε² · π_d·κ + ω_e²),  κ = moyenne de |M_τ|

| Paramètre | Sens | A priori ou estimation | Source |
|---|---|---|---|
| π_d | part du département dans le stock de la tranche à l'origine | **fixé** (observé) | RPPS, axe 4 (privé) |
| L_τ, σ_u, σ_v | niveau national des entrées et ses deux variances | filtre de Kalman ; σ par maximum de vraisemblance, communs aux sexes et tranches d'une profession ; variances absolues ∝ κ = moyenne de \|M\| (u ~ N(0, σ_u²κ), v ~ N(0, σ_v²κ)) | RPPS |
| δ, ζ | écart de la région, puis du département, au prorata du stock | a priori normaux centrés ; τ_r, τ_d par Bayes empirique (comme l'APC) | RPPS |
| σ_ε, ω_e | bruit annuel (de type Poisson, plus des chocs) | Bayes empirique | RPPS |

**Prévision.**
- M_{T+h} ~ N(L_{T|T}, P_{T|T} + h·σ_v² + σ_u²) : le niveau local est
  prolongé à plat, avec une variance qui croît avec h.
- (δ, ζ) sont tirés dans leur loi a posteriori ; ε est un bruit annuel
  indépendant.
- **Point :** L_{T|T}, une moyenne pondérée vers les années récentes. A0
  prend la moyenne simple de la fenêtre.

**Leviers.**
- Le multiplicateur des entrées (`methodes_entrees.multiplicateur` ; quotas
  × m) multiplie M.
- La régulation déplacerait δ et ζ ; elle n'est pas branchée ici, puisque le
  logit d'installation est l'étape 3.

## Propagation de θ (Laplace)
- Pour l'APC et pour les entrées, on fait une approximation de Laplace sur
  log θ : la hessienne numérique de −log p(y | θ) au mode θ̂ donne
  log θ ~ N(log θ̂, H⁻¹).
- Chaque tirage k prend θ_k, puis β_k | θ_k, y, en reprenant la loi
  gaussienne exacte.
- On mesure le gain de couverture entre C1 (θ fixé) et C2 (θ propagé).

## Cas limites
| Limite | Ce qui se passe |
|---|---|
| σ_v → 0 | le niveau est constant ; L_{T\|T} = moyenne de la fenêtre, comme A0 en ponctuel |
| σ_u → 0 | le niveau suit la dernière année (entrées « récentes ») |
| τ_d, τ_r → 0 | les entrées sont réparties au prorata du stock (C5) |
| h → 0 | l'état est observé ; la bande ne contient que le bruit d'un an |

## Ansätze et verdicts
- **C1, θ fixé : promue.** APC (étape 1) pour les sorties, et le modèle des
  entrées ci-dessus.
- **C2, θ propagé (Laplace) : promue.**
- **Grain commune ⊂ dép ⊂ région : en attente.**
  - L'axe 4 recommande de projeter les dentistes et les sages-femmes au
    département, et les infirmiers à l'EPCI ou au bassin de vie.
  - Les protocoles N1 et N6 jugent au département.
  - La commune vient avec N4, comme un prolongement du même schéma :
    π_commune dans le département.
- **Logit conditionnel : en attente** (étape 3).
- **MCMC complet (PyMC ou NumPyro) : tuée pour cette étape.**
  - Le modèle est gaussien sachant θ, avec 6 + 4 + 2 hyperparamètres.
  - La loi de Laplace sur log θ suffit à propager θ.
  - La calibration par simulation dira si elle est insuffisante. Si oui,
    on rouvre le MCMC.

## Kill tests (pré-écrits)
| Test | Résultat qui tue | Prix |
|---|---|---|
| Calibration par simulation : 5 professions × 2 sexes × 200 jeux, θ ré-estimé, rangs de π(60+, T), w, η à h = 5, et du niveau d'entrées L_T | χ² à 19 ddl, p < 0,01/k (Bonferroni) | ~3 h machine |
| N6 : couverture à 80 % et à 50 % au département, h = 5 | hors de [75 ; 85] % ou de [44 ; 56] % | inclus dans le banc |
| N6 : CRPS(log N) contre la meilleure naïve probabiliste | borne basse de Δ > 0 | inclus |
| N1 : MAPE contre A0 | borne basse de Δ > 0 (pire) | inclus |

## Prédictions écrites avant le banc (supposées)
- **Couverture à 80 % au département, h = 5, toutes origines :**
  - C1 entre 60 et 80 % (était 50 % pour l'APC seule) ;
  - C2 de 0 à 5 points au-dessus de C1.
- **MAPE N1 :** \|Δ(C, A0)\| < 0,3 pt.
- **CRPS N6 (origine 2021 seulement, SF, CD, PH) :** C bat la meilleure
  naïve probabiliste chez au moins 2 professions sur 3.

## Écart avant inscription (2026-11-14, 04:40)
- **Ce qui a changé.** Un pilote a montré que des variances communes **en
  relatif** à la moyenne explosaient : σ_u ≈ 1,3 et σ_v ≈ 1,2 pour les
  sages-femmes.
  - Les séries d'entrées proches de zéro (tranches de 35 ans et plus)
    dictaient la variance des grandes séries.
  - La correction : des variances absolues proportionnelles à κ = moyenne
    de |M| (forme de Poisson).
- **Ce que le pilote a vu.** Il a aussi vu les cibles 2026 de l'origine
  2021 pour les dentistes et les sages-femmes, et leur couverture.
- **Pourquoi l'inscription garde sa valeur, avec ce point signalé.**
  - La correction est motivée par le diagnostic des paramètres, pas par
    les cibles.
  - Pour ces deux cellules, le banc reste partiellement contaminé.
