---
date: 2026-11-15
statut: plan, non construit (en attente d'accord de l'utilisateur·rice)
remplace: "2026-11-14-module-besoin.md (gardé ; ses critères sont repris et corrigés ici, §9)"
headline: "Le besoin n'est identifié par le recours que sous une hypothèse de saturation ; un test de forme (recours standardisé contre accessibilité) décide si M2 vit ; M1 est le socle, M3 le recoupement, M4 (2SFCA) un indice spatial qui compose avec les autres"
tags: [besoin, recours, identification, 2SFCA, APL, transferts-de-taches]
---

# Comment représenter le besoin de soins quand on n'observe que le recours ?

**Dérivé :** 2026-11-15. **Temps passé :** ~1 h de Claude (mesuré au journal `eta.py`).
**Statut :** 4 promus en hypothèse (M0 baseline, M1, M3, M4), 1 promu sous condition (M2, tué si pas de
saturation), transferts promus ; 0 tué à ce stade (les tests d'abandon sont écrits, pas lancés).
**Données :** vérifiées le 2026-11-15 en ligne, voir l'exploration
[2026-11-15-besoin-sources](../explorations/2026-11-15-besoin-sources.md). Toute affirmation sur un jeu de données
renvoie à ce rapport.

Provenance des nombres : (m) mesuré, (s) sourcé, (d) dérivé, (h) supposé.

---

## 1. Problème (objectif · contrainte · variables libres)

- **Objectif.** Pour chaque profession p ∈ {SF, CD, PH, MK, IDE}, territoire T (commune → national) et année
  t ≤ 2050, produire une grandeur `B(p,T,t)` en **unités de temps professionnel** (ETP-équivalents) telle que
  l'indice `C = offre / B`, indexé à 2026, réponde à la question du sujet : *« combien, et pour quelle couverture, si
  la politique X ? »*. Le critère est double, comme dans le profil :
  1. **utilité pour la décision** : un transfert de tâches et le vieillissement changent C de façon lisible et
     sourcée ;
  2. **précision au backtest** : la projection du recours à 5–9 ans (2016 → 2025) bat la référence naïve
     « recours par habitant constant » (MAPE départementale, en points).
- **Contrainte qui lie.** Données **ouvertes** seulement. Le grain des données de recours ouvertes (région ou
  département, pas la commune : exploration §1) est la vraie contrainte, plus que le temps de calcul
  (< 5 ms ajoutées au département, < 150 ms au 95ᵉ centile pour la carte, budget hérité (h)).
- **Variables libres** (y compris celles qui ressemblent à des données) :
  - la **norme** qui définit le besoin (recours observé, recours non contraint, recommandation clinique) : c'est un
    choix, pas une mesure ; il doit être déclaré et chaque estimateur en porte un ;
  - l'unité (actes, patients, ETP) ;
  - la fonction de décroissance avec la distance et le rayon (M4) ;
  - les paramètres de transfert `s, a, k` (et `m`, §6) ;
  - **le périmètre de la médecine générale** comme source de transfert (§7, décision de l'équipe).

## 2. Le problème central : censure et identification

### 2.1 Formalisation
Pour une cellule i = (commune de résidence, âge, sexe) et une profession p :

- `B_ip` : besoin latent, en actes requis par an selon une norme N.
- `A_ip` : accessibilité de l'offre de p depuis i (densité, temps d'accès, APL).
- `R_ip` : recours observé, actes remboursés (ou patients uniques).

Modèle structurel général :

    R_ip = B_ip · φ_p(A_ip) + D_p(A_ip) + ε_ip ,   0 < φ ≤ 1 ,  D ≥ 0

- `φ` est la part du besoin satisfaite (rationnement par l'accès : distance, délais, renoncement).
- `D` est la demande induite par l'offre (Evans 1974 ; « loi de Roemer » ; (s) à citer après lecture,
  non lue ici).
- La **censure** : on n'observe jamais B, seulement le produit `B·φ(A)` plus `D(A)`. C'est une censure
  multiplicative, de type frontière stochastique (`R = B·e^{−u}`, `u ≥ 0` = besoin non satisfait), et non une censure
  à seuil de type Tobit.

### 2.2 Pourquoi ce n'est pas identifié sans hypothèse
Avec `D = 0` : pour toute fonction `h(i) > 0`, le couple `(B·h, φ/h)` produit exactement le même R.
Le niveau du besoin et la forme du rationnement ne sont donc pas séparables à partir de (R, A) seuls (d).
Il faut au moins une des trois restrictions suivantes, et chacune est une hypothèse testable ou au moins réfutable :

| Restriction | Énoncé | Ce qu'elle identifie | Comment elle peut échouer |
|---|---|---|---|
| **R1. Indépendance conditionnelle** | `B ⟂ A \| X` (X = âge, sexe, morbidité, défaveur sociale) | la pente de R en A, donc φ à une constante près | tri : les professionnels s'installent là où le besoin est fort (causalité inverse) ou faible (attractivité) ; N9 mesure un effet nul de la densité sur les installations, ce qui ne dit rien du besoin |
| **R2. Saturation** | `φ(A) → 1` quand `A → ∞`, et `D` borné | le niveau : `B ≈ lim R(A)` au plateau | si R croît encore avec A chez les mieux dotés : demande induite ou rationnement partout, **M2 tombe** |
| **R3. Exclusion** | une variable Z déplace A sans toucher B (zonage conventionnel, choc de régulation, distance historique à une école) | φ par variable instrumentale ou différence de différences | Z corrélée au besoin ; instruments faibles (l'axe 3 a déjà vu deux DiD IDE échouer) |

Une **quatrième voie** évite le problème au lieu de le résoudre : définir B par une norme externe à l'offre
(**M3**, prévalence × actes recommandés). Elle remplace l'identification par une hypothèse de norme, déclarée.

### 2.3 Conséquence pratique
- Prendre `R` pour `B` (M1) est **biaisé vers le bas là où A est faible**, exactement là où la question se pose.
  L'indice de couverture `C = offre/B` y est alors trop optimiste : c'est la circularité notée au rapport technique
  (§ Module de besoin).
- Le sens du biais est connu, sa taille non. Le test de forme du §8 (P-B2) le mesure.
- **Ce que l'indexation à 2026 sauve.** `C(T,t)/C(T,2026)` élimine tout biais **multiplicatif constant par
  territoire** (`h(T)` fixe) : il s'annule au rapport. Il reste le biais qui **change avec le temps** : si A baisse,
  φ baisse et R sous-estime davantage. Pour la question « couverture 2035 vs aujourd'hui », M1 indexé est donc
  défendable tant que A ne bouge pas beaucoup ; il ne l'est pas pour comparer deux territoires en niveau (d).

## 3. Structure

- **Invariances.**
  - *Additivité spatiale* : B (en actes ou ETP) est additif sur les territoires ; `C` ne l'est pas (rapport). Toute
    agrégation de C se fait par la somme des numérateurs et des dénominateurs, jamais par la moyenne des C.
    Contrainte structurelle, coût nul.
  - *Échelle de population* : `B(λ·pop) = λ·B` pour M0–M3 (homogène de degré 1). M4 ne l'est qu'en
    l'absence d'effet de bord (les communes voisines comptent).
  - *Conservation de l'offre en 2SFCA* : `Σ_i P_i·A_i = Σ_j S_j` exactement, quels que soient les poids
    (démonstration : intervertir les sommes, les deux étapes utilisent le même `w_ij`) (d). Test gratuit.
  - *Conservation du besoin sous transfert* : `ΣB' − ΣB = s·a·B_A·(k − 1)` (+ `m`, §6) (d).
- **Échelles de temps.** Vieillissement : décennies (Omphale) ; changement de pratique (recours par âge) :
  ~5–10 ans (h) ; montée en charge d'un transfert : 1–5 saisons (vaccination grippale en officine : à mesurer, §6) ;
  saison épidémique : mois. Ces échelles sont séparées : on peut traiter le besoin comme quasi statique entre deux
  années et le vieillissement comme une dérive lente. Le grain mensuel d'Open DAMIR n'apporte rien sauf pour la
  vaccination (saisonnière).
- **Connu vs appris.**
  - *Exact* : la population par âge et sexe projetée (Omphale 2022, déjà chargée : `data/processed/population.parquet`,
    département × sexe × âge quinquennal × année, 3 scénarios, (m)) ; la géométrie des communes
    (`v2/data/raw/insee/geoapi_communes_centre.json`) ; l'identité comptable des transferts.
  - *Estimé* : les profils `r(p, âge, sexe)` ; la forme de φ ; les paramètres de transfert.
  - *Choisi* : la norme.
- **Où est le coût.** Pas dans le calcul (des produits matrice × vecteur). Il est dans **l'ingestion** (Open DAMIR :
  gros fichiers mensuels, exploration §1) et dans **l'identification** (M2). Le distancier communal est le seul
  poste de calcul lourd (≈ 35 000 communes ; une matrice complète fait ~1,2 × 10⁹ paires, (d) ; on ne garde que les
  paires à moins de 30–45 min, (h)).

## 4. Cas limites (chaque ansatz doit les reproduire)

| Limite | Ce qui gagne | Implication |
|---|---|---|
| Profil de recours plat en âge (`r(a) = r̄`) | M1 = M0 | M1 doit redonner `C = densité/densité₂₀₂₆` à 10⁻⁹ près |
| Population figée par âge (pas de vieillissement) | M1 indexé = M0 indexé | l'apport de M1 est **entièrement** le vieillissement relatif entre territoires |
| Offre infinie partout (`A → ∞`) | R = B (si R2) | M2 = M1 calé sur les territoires saturés |
| Offre nulle quelque part | R = 0 mais B > 0 | M1 donne B = 0 : **faux** ; M2 et M3 restent positifs. Tout ansatz qui renvoie B = 0 en zone sans offre est rejeté pour ces zones |
| Rayon 2SFCA → 0 | M4 = densité de la commune | test de cohérence (le point de départ d'APL) |
| Rayon 2SFCA → ∞ | M4 = densité nationale, uniforme | idem |
| Agrégation croissante | M4 → densité standardisée du territoire | DREES le dit de l'APL (archive v1, exploration APL) ; test : à la région, M4 ≈ M1 |
| `s = 0` | aucun transfert | effectifs et densités identiques au commit de référence |
| `k = 1`, `m = 0` | besoin total conservé | test d'identité à 10⁻⁶ |
| `k → 0` | l'acte ne coûte rien à B | le transfert ne fait que libérer A ; plafond de l'effet |
| `s·a → 1` | A perd tout l'acte | borne : `B'(A) ≥ 0` doit tenir, `s·a ≤ 1` est une contrainte du levier |

Interpolation qui tombe : à vieillissement donné, l'écart M1/M0 sur l'indice est
`ΔC/C = 1 − [Σ_a w_a(T,2026)·r_a / Σ_a w_a(T,t)·r_a]`, avec `w_a` la part de la tranche a dans T. Il ne dépend que
du **déplacement de la pyramide** pondéré par le profil. Si le profil est plat sur les tranches qui bougent, M1
n'apporte rien : c'est ce que le test d'abandon P-B1 mesure, et ce qu'il doit mesurer sur `C`, pas sur `B`
(correction du plan du 2026-11-14, §9).

## 5. Isomorphismes

| Ici | Là | Étiquette |
|---|---|---|
| R = B·φ(A), φ ≤ 1 | frontière stochastique de production (Aigner–Lovell–Schmidt 1977) : sortie = frontière × inefficacité | **claim** (M2 en dépend) |
| besoin non satisfait | renoncement aux soins (enquêtes EHIS / ESPS, IRDES) | intuition (pas de grain territorial ouvert, probablement) |
| standardisation par âge du besoin | densité standardisée DREES (DD76, ER1319) et population standardisée de l'APL | **claim** (déjà utilisée par la DREES, à reproduire) |
| 2SFCA | modèle gravitaire de Huff / Hansen ; dans ce dépôt, rien : le budget d'erreur a rejeté le gravitaire **pour la mobilité des professionnels**, pas pour l'accès des patients | intuition |
| transfert de tâches | substitution de facteurs avec rendement relatif k (économie de la production) | intuition |
| montée en charge du transfert | diffusion d'une innovation (courbe logistique de Bass) | **claim** (forme de `s(t)`, à mesurer sur la grippe en officine) |
| besoin de SF par naissance | modèle à composantes : naissances (Omphale, fécondité) × actes par grossesse | **claim** (le levier fécondité existe déjà) |

**Où ça casse.**
- La frontière stochastique suppose `u ≥ 0` indépendant de la frontière ; la demande induite viole précisément ça
  (u négatif là où l'offre est forte).
- L'APL n'est pas un modèle de besoin : elle **prend** un besoin (population standardisée par l'âge) et le croise avec
  l'offre et la distance. M4 compose donc avec M1/M2/M3 ; ce n'est pas un concurrent.
- Pour les pharmaciens, le recours (délivrances) est une **demande dérivée** des prescriptions : la densité des
  pharmaciens ne le contraint presque pas, la densité des prescripteurs si. φ y dépend d'une autre profession.
- Pour les kinés et les IDE, le recours dépend aussi de la prescription médicale (avant accès direct) : même remarque,
  et c'est par là que la médecine générale entre (§7).

## 6. Ansätze

Notations : `pop(T,t,a,s)` Omphale (département) ou recensement + ventilation (commune) ; `r(p,a,s)` actes par
habitant et par an ; `q_p` actes par ETP et par an (activité), pour passer en ETP-équivalents.

### M0 — proportionnel à la population (baseline, déjà en place)
- `B₀(p,T,t) = r̄_p · pop(T,t)`.
- Exploite : l'homogénéité de degré 1. Reproduit tous les cas limites sauf « offre nulle » (il donne B > 0, ce qui
  est juste) et ignore le vieillissement.
- Coût : nul, c'est la densité pour 100 000 de la carte.
- **Hypothèse falsifiable H-B0** : la structure par âge n'explique pas la variation du recours par habitant entre
  départements au-delà de 2 points. Testée par P-B1 et P-B5.

### M1 — recours standardisé par âge et sexe
- `B₁(p,T,t) = Σ_{a,s} pop(T,t,a,s) · r(p,a,s)`, avec `r` national d'une année de référence, constant ensuite
  (dérive du recours L31 hors périmètre, levier possible plus tard).
- **Deux sources pour `r`, vérifiées le 2026-11-15** (exploration §1 et §3) :
  - *forme relative* `ω_a = r_a / r̄` : les **poids de standardisation publiés dans les fichiers APL** de la DREES
    (DCIR 2020–2022, 19 tranches quinquennales jusqu'à 90+, (s)) pour IDE, MK, CD, SF (SF : femmes seules). Exemple
    IDE 2024 : 0,06 avant 5 ans, 4,50 à 80–84 ans, 15,51 à 90+ (s). C'est le profil le plus fin disponible ;
  - *niveau et pharmaciens* : Open DAMIR (actes `PRS_NAT` par `PSE_ACT_SNDS` = 19, 21, 24, 26, 50), région
    seulement, tranches décennales fermées à **80+** (s). Le plafond 80+ écrase le profil IDE (4,50 → 15,51 entre
    80–84 et 90+) : DAMIR ne sert donc pas à la forme pour IDE et MK.
- En ETP : `B₁ / q_p`. Indice `C₁ = [N(p,T,t)/B₁(p,T,t)] / [N(p,T,2026)/B₁(p,T,2026)]`.
- Variante M1-dép : `r` estimé par région (le grain des données ouvertes), puis appliqué aux départements de la région.
- Exploite : Omphale déjà chargé, les deux premiers cas limites.
- Rate : le cas « offre nulle » (biais vers le bas, §2.3) si `r` est local ; avec `r` **national**, le biais est
  dilué mais pas nul.
- Coût : ~1 h (profils) + < 1 ms de calcul (d).
- **Hypothèse H-B1** : projeter le recours 2016 → 2025 par la seule structure d'âge bat la persistance du recours par
  habitant (MAPE départementale), pour au moins 3 professions sur 5. Test P-B5.
- **Test d'abandon P-B1** (déjà au plan de la veille, corrigé) : si `|C₁/C₀ − 1| < 2 %` en 2050 dans plus de 90 %
  des départements **et** si le rang des départements est stable (Spearman ≥ 0,98), la pondération par l'âge est
  abandonnée pour cette profession.

### M2 — recours non contraint (frontière ou saturation)
- Estimer `R_std(T) = R(T)/B₁(T)` (recours standardisé par l'âge, indice 1 = moyenne nationale) contre
  `A(T)` (densité, ou M4) sur les territoires, puis ajuster deux formes concurrentes :
  - **saturation** : `R_std = ρ_max · A/(A + K)` (Michaelis–Menten) ou linéaire par morceaux avec plateau ;
  - **sans plateau** : `R_std = α + β·log A`.
- Si la saturation gagne, `B₂ = ρ_max · B₁` (le besoin est le recours des territoires saturés) et `φ(A) = A/(A+K)`
  donne le **besoin non satisfait** `B₂ − R` par territoire.
- Variante frontière : SFA sur les territoires, `log R_std = log f(X) − u`, `u ≥ 0` demi-normale.
- Exploite : R2 (saturation). Reproduit « offre nulle » (B₂ > 0) et « offre infinie » (B₂ = R).
- Coût : ~1 h 30 une fois les données au département.
- **Hypothèse H-B2** : il existe un plateau : l'élasticité du recours standardisé à l'accessibilité dans le quintile
  le mieux doté est inférieure à la moitié de celle du quintile le moins doté, IC 95 % à l'appui.
- **Test d'abandon (P-B2)** : si l'élasticité du quintile supérieur est ≥ 0,5 × celle du quintile inférieur, ou si
  la forme log-linéaire gagne au critère pré-enregistré (ΔAIC < 2 en faveur de la saturation), **M2 tombe** pour
  la profession : le recours y suit l'offre sans saturation (demande induite ou rationnement généralisé), et le plafond
  `ρ_max` n'est pas identifié. Placebo : la même régression sur la densité d'une **autre** profession doit donner une
  pente nulle (sinon c'est l'attractivité générale du territoire, comme en N9).
- Grain : le test exige au moins le département (101 points) ; Open DAMIR n'a que 13 zones (s), insuffisant (d).
  **Seule source départementale vérifiée** : la patientèle ameli (patients uniques par profession et département,
  2016–2025, ODbL, sans pharmaciens (s), déjà dans `v2/data/raw/patientele.xlsx`). C'est une marge **extensive**
  (patients, pas actes), et le département est vraisemblablement celui **d'exercice** (à vérifier dans le descriptif) :
  la fuite inter-départementale est une menace écrite du protocole. Compléments possibles : honoraires par
  département (`honoraires-detailles`, montants seulement (s)) divisés par un prix moyen régional d'acte (DAMIR).
- **Pharmaciens : M2 non applicable.** Leur recours est une demande dérivée des prescriptions (§5) ; ils n'ont pas
  de patientèle ouverte. Ils restent en M1.

### M3 — épidémiologique (prévalence × actes par cas)
- `B₃(p,T,t) = Σ_{g} Σ_{a,s} pop(T,t,a,s) · prev(g,a,s) · n(p,g)` + un terme hors pathologie (`r₀(p,a,s)`, soins
  courants, prévention).
  - `prev(g,a,s)` : jeu `effectifs` de la cartographie des pathologies (data.ameli.fr, ODbL) : **département** ×
    tranche quinquennale jusqu'à 95+ × sexe × 61 groupes fins, 2015–2024 (s) ; cellules < 11 patients masquées (s).
  - `n(p,g)` : actes de p par patient du groupe g. Deux voies : (i) **observée** = jeu `depenses` (**national**
    seulement : montant et nombre de recourants par poste — soins infirmiers, kinésithérapie, sages-femmes, dentaires,
    médicaments — et par pathologie, sans âge (s)), divisé par le prix moyen de l'acte tiré d'Open DAMIR (montant /
    quantité, par région) ; même censure que le recours, mais mesurée nationalement et par pathologie, ce qui la dilue ;
    (ii) **norme** = recommandation HAS ou texte réglementaire (exemple : nombre d'examens prénataux obligatoires,
    Code de la santé publique, à citer après lecture, non lu ici).
  - La construction (i) est la nôtre, pas une méthode publiée (exploration §2).
  - Pour les SF : `B₃(SF) = naissances(T,t) × n_grossesse + femmes(15–49) × n_suivi` ; les naissances viennent
    d'Omphale (levier fécondité existant).
- Exploite : il est indépendant de l'offre **si** `n` vient d'une norme ; il voit le territoire par la prévalence
  locale (vieillissement **et** morbidité).
- Rate : la voie (i) hérite de la censure ; la voie (ii) suppose que la norme est le besoin.
- Coût : ~2 h (jointure des groupes, prix moyens) ; projection de la prévalence = profils par âge constants (h).
- **Hypothèse H-B3** : la composante pathologie explique une part de la variation départementale du recours
  standardisé que l'âge seul n'explique pas (R² additionnel ≥ 0,1 hors échantillon (h)).
- **Test d'abandon (P-B3)** : si `C₃` et `C₁` (indexés 2026) diffèrent de moins de 2 % dans 90 % des départements en
  2050, M3 n'apporte rien au-dessus de M1 pour l'indice ; on le garde comme **recoupement du niveau** de M2
  (triangulation : `|B₃/B₂ − 1|` est rapporté, pas optimisé).

### M4 — spatial (2SFCA, famille de l'APL DREES)
- Étape 1 (par point d'offre j) : `R_j = S_j / Σ_k w(d_kj) · P_k^std`, avec `S_j` l'offre en ETP (effectif × activité
  bornée) et `P_k^std = Σ_a pop_k,a · ω_a` la population standardisée (les poids `ω_a` viennent de M1, M2 ou M3).
- Étape 2 (par commune i) : `A_i = Σ_j w(d_ij) · R_j`.
- `w` : **paliers publiés par la DREES** (onglet « Paramètres » des fichiers APL 2024, (s)) : poids 1 sous 10 min,
  2/3 de 10 à 15, 1/3 de 15 à 20, 0 au-delà pour CD, MK, IDE ; pour les SF, 1 / 2/3 / 1/3 sur 0–10 / 10–20 / 20–30 min.
  Temps d'accès : distancier Metric de l'Insee (s), **non publié comme matrice** ; on le reconstruit par OSRM sur
  OpenStreetMap (même moteur, ODbL) (exploration §4).
- `S_j` : la DREES convertit l'activité de chaque professionnel (honoraires SNIIR-AM, actes pour les MK) en ETP
  (1 ETP = activité médiane ; bornes au 5ᵉ centile ou à 10 000 € et au 90ᵉ centile ; ≤ 65 ans) (s). Cette activité
  individuelle **n'est pas ouverte** : notre `S_j` est l'effectif ≤ 65 ans × un ETP moyen départemental (honoraires
  ameli par département / médiane nationale, (h)). C'est la principale source d'écart attendue à l'APL.
- Décalages : l'APL de l'année N utilise la population N−2 et l'activité N−2 (s). La cible 2024 se reproduit donc
  avec l'état 2022.
- Exploite : la conservation `Σ_i P_i A_i = Σ_j S_j` (test gratuit), les limites de rayon.
- C'est un **indice d'accessibilité** qui prend un besoin en entrée : on écrit M4∘M1, M4∘M2, M4∘M3. Il ne se
  projette en 2050 qu'en projetant `S_j` à la commune, ce que le jumeau sait faire mais n'affiche pas (projection
  communale non confirmée, N11–N12) : à la commune, M4 est donc **descriptif pour 2026** et projeté seulement à titre
  de scénario.
- Coût : distancier (exploration §4 ; repli : distance à vol d'oiseau entre centres de communes, déjà sur disque,
  avec un facteur de détour (h)) + ~2 h.
- **Hypothèse H-B4 (cible externe)** : M4∘M1, avec les paramètres publiés ou calés sur le millésime 2022, reproduit
  l'APL DREES 2024 commune par commune pour IDE, MK, SF et CD : Spearman ≥ 0,90 et erreur absolue médiane ≤ 15 % (h,
  seuils à geler), et bat les deux références naïves (densité de la commune ; densité du bassin de vie) de ≥ 0,05 en
  Spearman.
- **Test d'abandon (P-B4)** : sous ces seuils, M4 n'est pas « la méthode de l'APL » et ne peut pas être présenté
  comme tel ; il reste un indice maison, étiqueté.

### Transferts de tâches (s · a, coefficient k)
Un transfert τ d'un acte de la profession A vers la profession B, actif à partir de la date de décision t₀ :

    B'_A(t) = B_A(t) · (1 − s(t)·a)
    B'_B(t) = B_B(t) + s(t)·a·B_A(t)·k + m(t)
    ΣB' − ΣB = s(t)·a·B_A(t)·(k − 1) + m(t)

- `a` : part du besoin de A (en temps) qui porte sur l'acte. Sourçable comme *actes de A de ce type × durée / temps
  total de A* (Open DAMIR par nature de prestation, exploration).
- `k = t_B / t_A` : rapport des durées de l'acte chez B et chez A (temps de B par unité de temps de A libérée).
- `s(t)` : **part effectivement transférée**, pas une décision. Le levier politique est l'autorisation (date t₀,
  périmètre de l'acte) ; `s(t)` suit une montée en charge, forme proposée `s(t) = s_∞ · (1 − e^{−(t−t₀)/τ})`, avec
  `s_∞` et `τ` **mesurés** sur l'historique de la vaccination antigrippale en officine (exploration §5), puis
  transposés aux autres actes (h, étiqueté).
- `m(t)` : **expansion** du recours (des patients qui n'auraient pas eu l'acte du tout). Il n'est pas dans la forme
  de la veille ; il est ajouté parce qu'un transfert vers une profession plus accessible augmente le recours total
  (c'est l'objectif même de la vaccination en officine). Valeur par défaut 0, étiquetée ; mesurable par la
  différence de différences P-B6.
- Effectifs : **inchangés** (pas de rétroaction ; N9). La sortie d'un transfert est un **double indice** : couverture
  de A (monte) et couverture de B (baisse si B ne s'ajuste pas). C'est la réponse honnête à la question du sujet :
  « à Clermont-Ferrand en 2035, si les pharmaciens vaccinent, l'effectif des spécialistes ne change pas dans le
  modèle ; la couverture de telle profession bouge de x %, celle des pharmaciens de −y % ».
- Contraintes : `0 ≤ s·a ≤ 1` ; `k > 0` ; un transfert n'a de sens que si A ou B est dans le modèle (§7).
- **Hypothèse H-BT** : la généralisation de la vaccination antigrippale en officine a déplacé des vaccinations
  (substitution, `s > 0`) **et** en a ajouté (`m > 0`). Test P-B6.

**Transferts visés** (leviers du catalogue v1 et du pitch), avec ce que les données vérifiées permettent
(exploration §5–§6) :
| Levier | A (source) | B (cible) | `a` | `s(t)` | `k` | Calculable ? |
|---|---|---|---|---|---|---|
| L23 vaccination antigrippale en officine | MG, IDE | PH | parts par vaccinateur, Cour des comptes 2026 (SNDS) : PH un peu moins d'1/3 en 2019-20 → près de 2/3 en 2024-25 ; médecins 1/2 → moins d'1/4 ; IDE 1/5 → 1/10 (s) | **mesurable** : actes VGP par saison (IQVIA, national, 5,65 M → 6,63 M → 8,02 M de 2023-24 à 2025-26 (s)) ; Open DAMIR code 3360 (VGP) par région × mois × âge depuis 2009 (s) | aucune durée officielle ; consultation de MG 19 min (DREES ER 1381, 2025, déclaratif (s)) ; temps officinal non sourcé (h) | **oui** pour `s(t)` et `a` ; `k` supposé |
| prise de tension, dépistage du diabète en officine | MG | PH | aucune donnée de volume ; dépistage glycémique limité aux semaines de campagne (s, presse) | aucune série (non mesurable) | idem | **non** : levier « supposé » de bout en bout, ou « pas dans le modèle » |
| L25 IPA en accès direct | MG | IDE (IPA) | aucun volume (décret 2025-55 ; 3 973 IPA diplômés, UNIPA, presse (s)) | non mesurable | non sourcé | **non** aujourd'hui |
| L27 accès direct au kiné | MG (prescription) | MK | aucun volume ; expérimentation dans 16 départements, 5 ans (presse (s)) | non mesurable | sans objet (l'acte de MK ne change pas ; seule la consultation de MG prescriptrice disparaît) | **partiel** : `k` = 0 côté MK par construction, `a` = consultations de MG évitées, non sourcé |

**Conséquence.** Un seul transfert, la vaccination en officine, a aujourd'hui `a` et `s(t)` mesurés. C'est celui de la
question du sujet. Les trois autres sont calculables seulement avec des valeurs supposées et étiquetées ; le plan
(axe 1) dit pour chacun « supposé » ou « non mesurable », jamais une valeur inventée.

Les quatre transferts du pitch prennent des actes **à la médecine générale**. Sans elle, aucun n'est calculable du côté
source ; seule la part IDE/SF de la vaccination l'est.

## 7. Question de périmètre (soumise, non tranchée) : la médecine générale comme source

**Le constat.** Le sujet exclut la médecine générale. Les transferts annoncés vers les pharmaciens (vaccination,
tension, diabète), vers les IPA et vers les kinés prennent surtout des actes aux médecins généralistes. Le profil du
laboratoire (`docs/lab/profile.md`, règles maison) dit déjà : « GPs may appear only as context, for example when demand
shifts from GPs to pharmacists. They are never a projected output. » Le texte penche donc pour l'option 2, mais aucune
entrée de `decisions.md` ne l'a actée pour le module de besoin.

| Option | Ce qu'on modélise pour la MG | Leviers calculables | Coût | Risque |
|---|---|---|---|---|
| **O1. Hors modèle** | rien | seulement les transferts entre les 5 professions (part IDE/SF de L23) | 0 | la question type du sujet reste sans réponse ; L23 partiel, L25, L27 et tension/diabète restent « pas dans le modèle » |
| **O2. Source seulement** (avis) | `B_MG` par M1 (recours standardisé, Open DAMIR, même code que pour les 5) ; **aucune offre MG projetée** ; on rapporte « actes de MG transférés » et le temps MG libéré, jamais une couverture MG | les quatre transferts, côté cible | ~30 min de plus (une profession de plus dans les profils) | lecture abusive « le modèle dit qu'il manque des MG » : interdite par construction (pas de C pour la MG) |
| **O3. Source + couverture contextuelle** | O2 + l'offre MG **publiée** par la DREES (projection officielle des médecins), lue telle quelle, sans modèle propre | idem, plus un indice MG en contexte | ~1 h, dépend de la disponibilité d'une projection départementale | glisse vers une sortie MG ; la DREES ne projette pas sous nos scénarios, donc l'indice est incohérent avec le jumeau |
| **O4. MG pleinement modélisée** | offre + besoin | tous | plusieurs heures | contraire au sujet |

**Avis.** **O2.** Elle est la seule qui rend calculables les leviers du pitch sans projeter la médecine générale. Elle
est déjà conforme au texte du profil. Elle coûte une profession de plus dans les profils de M1, rien d'autre. La règle
d'affichage qui la protège est simple : **aucun indice de couverture pour la MG, jamais**, seulement « x actes / y ETP
de MG libérés ». O3 peut venir plus tard comme contexte, sur demande. La même règle vaut pour les spécialistes
(source en phase 1, sortie en phase 2), ce qui rend le traitement symétrique.

## 8. Tests d'abandon et protocoles (à pré-enregistrer)

| Test | Discrimine | Résultat qui tue | Prix (temps Claude, (h)) |
|---|---|---|---|
| **P-B1** M1 vs M0 sur l'indice 2050, par département, IDE MK SF CD PH | M0 vs M1 | `\|C₁/C₀−1\|` < 2 % dans > 90 % des dép. **et** Spearman ≥ 0,98 → pondération par âge abandonnée pour la profession | 30 min |
| **P-B2** forme du recours standardisé contre l'accessibilité (dép.), placebo autre profession | M1 vs M2 | élasticité du quintile haut ≥ 0,5 × quintile bas, ou ΔAIC < 2 → M2 tué | 1 h |
| **P-B3** M3 vs M1 sur l'indice ; triangulation niveau M3 / M2 | M1 vs M3 | même règle que P-B1 → M3 réduit au recoupement | 1 h (après ingestion) |
| **P-B4** reproduction de l'APL DREES 2024 (cible externe) | M4 vs naïf | Spearman < 0,90 ou erreur médiane > 15 % ou gain < 0,05 sur les références naïves | 2 h (après distancier) |
| **P-B5** backtest du recours 2016 → 2025 par la structure d'âge (patientèle ameli, actes si disponibles) | M1 vs persistance du recours par habitant | MAPE de M1 ≥ MAPE de la persistance pour ≥ 3 professions sur 5 → H-B1 rejetée | 45 min |
| **P-B6** expérience naturelle : expérimentation de la vaccination antigrippale en officine dans six régions à partir de 2017 (Cour des comptes 2026 (s) ; liste et dates des régions à sourcer par l'arrêté), généralisée ensuite. Différence de différences, région × saison, 2014–2019 : actes VGP (DAMIR 3360) pour `s(t)`, **doses de vaccin antigrippal délivrées** (Open Medic, ATC J07BB, région du bénéficiaire, annuel (s)) pour le total | `m = 0` vs `m > 0` ; forme de `s(t)` | effet sur le total des doses nul (IC 95 % contient 0) → `m = 0` retenu ; < 4 régions traitées identifiables, ou zones DAMIR (9 ZEAT avant 2015 (s)) incompatibles avec les régions traitées → P-B6 non faisable, `m` reste « supposé » | 1 h 30 + téléchargement DAMIR 2014–2019 (~70 Go compressés (d)) |

**Gel hors de git.** Le rapport technique (§ Validation, intégrité) a montré que git ne prouve pas l'antériorité du
gel (historique réécrit, copie et résultat dans le même commit pour 6 protocoles sur 12). Procédure proposée pour ces
six protocoles :
1. copie gelée dans `v2/validation/preregistered/`, empreinte SHA-256 inscrite ;
2. **horodatage externe de l'empreinte**, au moment du gel, par OpenTimestamps (`ots stamp`, ancrage Bitcoin, jeton
   `.ots` commité) **et** un jeton RFC 3161 d'une autorité d'horodatage publique (`openssl ts -query` → TSA),
   jeton `.tsr` commité ;
3. le calcul n'est lancé qu'après réception du jeton ; le rapport cite l'heure du jeton, pas celle du commit.

Ce qui part à l'extérieur est **une empreinte de 32 octets**, pas le protocole. C'est tout de même une action tournée
vers l'extérieur : accord à demander au moment du gel.

## 9. Ce que cette dérivation change dans le plan du 2026-11-14

Le plan de la veille ([2026-11-14-module-besoin](2026-11-14-module-besoin.md)) **survit comme M1 + transferts**, avec
cinq corrections :
1. **Test d'abandon sur C, pas sur B.** Le plan compare « B pondéré » à « B proportionnel » ; or l'indice est indexé à
   2026 et le vieillissement national s'y annule en partie. Le test doit porter sur `C₁/C₀` et sur le rang.
2. **Circularité reconnue.** M1 est biaisé vers le bas là où l'offre manque ; l'indexation à 2026 n'efface que la part
   constante du biais (§2.3). M2 et M3 sont là pour la mesurer.
3. **Grain.** Les profils `r(p,âge)` ne sont pas départementaux en Open DAMIR (exploration §1) ; M1 est national ou
   régional, appliqué au département. Le plan disait « Open DAMIR » sans grain.
4. **`m`** (expansion du recours) est ajouté ; la conservation devient `(k−1)·s·a·B_A + m`.
5. **`s` n'est pas le levier.** Le levier est l'autorisation datée ; `s(t)` est une montée en charge mesurée.

Il reste un **incumbent externe** : l'observatoire de l'équipe (dépôt Hackathon-Evolution-soin) calcule déjà un
besoin pondéré par l'âge, par département, jusqu'en 2040 (decisions.md § Open, « Articulation avec l'observatoire »).
M1 doit le reproduire ou expliquer l'écart (prix : ~20 min, lecture de son code).

## 10. Verdicts

| Ansatz | Statut | Pourquoi |
|---|---|---|
| M0 | **promu (baseline)** | déjà en place ; tout autre ansatz doit le battre sur P-B1 / P-B5 |
| M1 | **promu, H-B1** | socle ; données au moins nationales par âge ; biais connu en signe |
| M2 | **promu sous condition, H-B2** | tué par P-B2 s'il n'y a pas de plateau |
| M3 | **promu, H-B3** | seul ansatz indépendant de l'offre (voie norme) ; utile au moins comme recoupement |
| M4 | **promu, H-B4** | cible externe (APL) disponible pour 4 professions sur 5 ; pas pour les pharmaciens |
| Transferts | **promus, H-BT** | identité comptable sûre ; `s(t)` et `m` mesurables sur la grippe en officine si les données le permettent |

## 11. Hand-offs
- Exploration des données : [2026-11-15-besoin-sources](../explorations/2026-11-15-besoin-sources.md).
- Registre : décision « Dérivation du besoin » ; question ouverte « médecine générale comme source » en § Open.
- Ledger : P-B1 à P-B6 avec leur prix ; lecture du code de l'observatoire.
- Plan par axes : [plan de construction](2026-11-15-besoin-plan.md).
