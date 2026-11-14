---
type: derivation
date: 2026-11-14
author: axe 2
question: La dynamique des systèmes (boucles de rétroaction), les modèles à agents ou un modèle multi-états de Markov apportent-ils quelque chose au jumeau, et à quelle condition ?
status: 1 promue (multi-états privé ↔ public) · 2 en attente (une boucle SD, ABM après le logit) · 1 tuée (ABM à règles calées)
---

# Dynamique des systèmes, modèles à agents, multi-états : que peut-on vérifier ?

**Dérivé :** 2026-11-14, environ 20 minutes. Question de l'utilisateur·rice :
« y a-t-il d'autres modèles comme les ABM, les systèmes dynamiques et les
boucles de rétroaction ? »

## Problème
- **Objectif.** Une famille de modèles n'entre dans le jumeau que si elle
  apporte au moins l'un des trois gains suivants, chacun mesurable :
  - une **prévision meilleure** : N1, MAPE dép. à h = 5, contre C1
    (7,73 %) et A0 (8,68 %) ;
  - une **bande mieux calibrée** : N6, couverture à 80 % dans [75 ; 85] %,
    et la calibration par simulation qui réussit ;
  - un **levier qui n'existe pas sans elle**, avec un mécanisme estimé, pas
    supposé.
- **Contraintes.**
  - Boîte blanche : chaque paramètre a un sens, une source et un a priori.
  - Recalcul < 2 s.
  - Toute boucle respecte trois contraintes, notées K :
    - K-cons, la conservation du total national ;
    - une réallocation bornée par le flux d'entrants (≈ 3 %/an) ;
    - K-osc, le test d'oscillation (décision « Tests des boucles de
      rétroaction »).
- **Ce qu'on observe.**
  - Des stocks par département × sexe × tranche de 5 ans × année
    (RPPS 2012–2026).
  - Une histoire communale sur 5 tranches d'âge, sans sexe (CartoSanté,
    IDE, MK, CD).
  - Un instantané individuel sans historique (Annuaire Santé, 2026).
  - **Aucune trajectoire individuelle.**

## Structure commune
- **Les trois familles ont la même identité comptable** :
  N(t+1) = s·A(N(t)) + E. Elles diffèrent par **ce qui fait varier s et E** :
  - **dynamique des systèmes** : l'état agrégé lui-même, la boucle ;
  - **modèle à agents** : des règles individuelles, sommées ;
  - **multi-états** : des probabilités de transition entre états (privé,
    public, sortie).
- **Linéarité (dérivée à l'étape 1).** Si les taux ne dépendent pas de
  l'état, une microsimulation ou un modèle à agents a **la même espérance**
  que le stock-flux.
  - Le gain en prévision ponctuelle ne peut donc venir que d'une
    **non-linéarité** : une boucle, un seuil (régulation « remplacement
    seul »), une interaction entre agents.
- **Identification.** Avec des stocks agrégés, un paramètre de
  comportement n'est estimable que s'il laisse une trace dans les stocks.
  - Une boucle laisse une trace : une pente entre territoires et années.
    C'est ce que N9 teste.
  - Une règle individuelle sans données individuelles n'en laisse aucune
    qui lui soit propre.

## Ce qui est déjà mesuré (axe 3, N9)
| Boucle | Résultat | Conséquence |
|---|---|---|
| B2, densité → installations des moins de 40 ans (IDE, MK, CD, bassin de vie) | **nulle** ; la densité des autres professions pèse autant ou plus : c'est de l'attractivité générale | pas de boucle de saturation ; l'attractivité générale entre comme covariable du logit d'installation (étape 3) |
| B1, densité → rétention des 45–54 ans à 5 ans (département) | **confirmée pour les infirmiers libéraux seuls** : +0,11 [+0,05 ; +0,18], soit ≈ +8 % de rétention quand la densité double | une seule boucle candidate, corrélationnelle ; l'utilisateur·rice doit trancher |

## Ansätze

### D1. Une couche de dynamique des systèmes, réduite aux boucles mesurées : **en attente**
- **Forme.** Dans `cohortes`, pour les infirmiers libéraux seulement :
  log s_{d,45–54}(t) = log s_{d,45–54} + β·log(densité_d(t)/densité_d(t₀)),
  avec β ~ N(0,11 ; 0,03²), issu de N9.
  - La densité est celle de l'état simulé : c'est ce qui fait la boucle.
- **Ce qu'elle apporte.** Une rétroaction : si la densité baisse, la
  rétention baisse, et le manque s'aggrave. C'est le scénario de stress.
- **Ce qu'elle n'apporte pas.**
  - A priori, pas de gain N1. Sur 5 ans, la densité infirmière d'un
    département bouge d'environ 10 % (+2,35 %/an au national, mesuré à
    l'axe 2). L'effet vaut donc β × Δlog(densité) ≈ 0,11 × 0,1 ≈ 1 % de
    rétention, sur la seule tranche 45–54 ans (dérivé).
- **Pourquoi elle attend.** Décision de l'utilisateur·rice : B1 est
  corrélationnel. La décision de l'axe 3 dit déjà « scénario de stress
  étiqueté supposé, jamais dans le tendanciel ».
- **Kill test pré-écrit.**
  - K-osc : simuler 2026 → 2050 avec β au bord de son IC (0,18) et un choc
    de −20 % de densité. Une oscillation, ou une divergence de plus de
    5 %/an, tue la forme. Prix : ~15 min.
  - N1 en variante exploratoire : |Δ MAPE| > 0,3 pt serait suspect, parce
    que l'effet dérivé est minuscule. Prix : ~10 min machine.

### D2. Modèle à agents à règles calées : **tuée**
- **Forme.** Chaque professionnel s'installe, part ou déménage selon des
  règles (seuils de densité, distance, âge), calées pour reproduire les
  stocks.
- **Ce qui la tue.** L'identification. Avec des stocks agrégés, les règles
  ont plus de degrés de liberté que les stocks n'en contraignent.
  - Plusieurs jeux de règles reproduisent le même historique et divergent
    en projection.
  - Le calage choisit l'un d'eux sans que les données tranchent : c'est
    une **boîte noire par calibration**, que la feuille de route exclut.
- **Ce qui la ressusciterait.** Un panel individuel ouvert : un RPPS
  individuel daté, ou des archives successives de l'Annuaire Santé,
  au moins 3 instantanés.

### D3. Modèle à agents à règles estimées : **en attente**, après le logit d'installation (étape 3)
- **Forme.** Les agents choisissent leur commune d'installation avec les
  probabilités du logit conditionnel estimé (coefficients β connus avec
  leur loi a posteriori). La régulation « remplacement seul » devient un
  ensemble de choix qui se ferme quand une commune est pleine.
- **Ce qu'elle apporte.** Le seul endroit où l'agent change le résultat :
  la **non-linéarité de la régulation par commune**. Une commune fermée
  renvoie l'entrant vers la commune suivante, et l'effet dépend de l'ordre
  et de la congestion. Un stock-flux agrégé ne peut pas l'exprimer
  exactement.
- **Coût.**
  - De l'ordre de 10⁴ entrants par an au national pour les 5 professions
    (dérivé des entrées des tranches jeunes de C1).
  - 25 ans × 200 tirages ≈ 5·10⁷ choix. Vectorisés, c'est quelques
    secondes. Il faut le mesurer avant de l'admettre sous le budget de
    2 s, et à défaut le réserver aux scénarios précalculés.
- **Kill test pré-écrit.** Sur le zonage observé, la différence de
  différences de N3 doit être reproduite. L'effet de la régulation des
  kinés est connu ; l'agent doit retrouver son signe et son ordre de
  grandeur. Un signe contraire tue la forme. Prix : ~2 h après le logit.

### D4. Multi-états de Markov privé ↔ public ↔ sortie : **promue**
- **Forme.** Une matrice de transition annuelle P par tranche × sexe ×
  département, entre trois états : privé, public, sortie.
  - Les transitions privé → public et public → privé sont des **flux nets
    estimables**, parce que l'axe 4 sépare les deux stocks pour les
    CD, PH, SF et MK.
  - A priori hiérarchique comme dans C1 : département ⊂ région.
- **Ce qu'elle apporte.**
  - Le levier « un entrant bloqué en zone régulée part vers le public » a
    aujourd'hui un taux supposé. Il aurait un taux estimé.
  - La conservation privé + public est vérifiable : C4 du jumeau.
- **Limite d'identification.** Avec des stocks seulement, on n'identifie
  que les transitions **nettes**. Le privé → public et le public → privé
  bruts ne se séparent pas (même argument que les sorties nettes, étape 1).
- **Kill test pré-écrit.** N1 sur le **total privé** (la sortie du projet).
  Si le multi-états fait pire que C1 de plus de 0,3 pt, ou si les flux
  nets estimés changent de signe d'une origine à l'autre pour plus de la
  moitié des cellules, la forme est tuée. Prix : ~3 h Claude + ~1 h
  machine.

## Verdicts
| Famille | Statut | Condition |
|---|---|---|
| D1 dynamique des systèmes (boucle B1, IDE) | en attente | accord de l'utilisateur·rice ; scénario de stress seulement |
| D2 modèle à agents à règles calées | **tuée** | identification : pas de données individuelles |
| D3 modèle à agents à règles estimées (logit) | en attente | après l'étape 3 ; reproduire N3 |
| D4 multi-états privé ↔ public | **promue** | après le traitement bayésien complet des variances (dette de l'étape 2) |

## Ordre proposé
1. Traitement bayésien complet des variances (la calibration par
   simulation de l'étape 2 échoue).
2. Logit d'installation, avec l'attractivité générale comme covariable
   (étape 3).
3. Multi-états privé ↔ public (D4).
4. Modèle à agents à règles estimées (D3), pour la régulation par commune.
5. Boucle B1 (D1) en scénario de stress, si l'utilisateur·rice la
   valide.
