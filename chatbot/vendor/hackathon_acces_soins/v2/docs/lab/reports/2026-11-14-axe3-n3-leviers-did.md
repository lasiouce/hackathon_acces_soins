---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: La régulation de l'installation infirmière en zone « sur-dotée » a-t-elle freiné l'effectif libéral, et le module « remplacement seul » du jumeau en reproduit-il la taille ?
headline: "IDE : effet −30 % [−34 ; −26] de la régulation en zone sur-dotée sur 2012–2019, mais le test pré-enregistré de tendances parallèles échoue (p = 0,043 < 0,10), donc levier NON validé selon le protocole ; kinés : la pente s'inverse à l'annulation de 2014 (+3,1 pts/an [1,1 ; 5,1]), prédiction pré-enregistrée confirmée"
status: done (protocole gelé, puis lancé)
professions: [infirmiers, kines, dentistes]
hypothesis: axe 3 niveau 3 ; module jumeau `regulation`
sources: [CartoSanté TJS infi/kine/dent_popage 2004–2025 (data/processed/stock_commune.parquet, extrait 2026-11-13), Atlasanté « France – Zonages conventionnels des ARS » uuid c987d0e2-e99c-4a11-a3a4-aa81de6aa416 (génération 2012, métadonnées 2014-10-22, extrait 2026-11-14), avenants 1 (2009) et 3 (2011) de la convention infirmière, CE 17 mars 2014 n° 357594]
tags: [validation, axe3, levier, did, pre-registration, zonage]
---

# Niveau 3 — effet des leviers par expérience naturelle (protocole pré-enregistré)

> **Headline:**
> - **Infirmiers (E1) : levier non validé selon le protocole.** L'effet est
>   fort, −30 % d'effectif libéral en zone sur-dotée vs intermédiaire
>   (IC 95 % [−34 ; −26], 59 départements). Mais le test de tendances
>   parallèles, fixé à p ≥ 0,10, donne **p = 0,043**. Les trois placebos
>   passent.
> - **Kinés (E2) : prédiction confirmée.** La pente relative de la zone
>   sur-dotée est de −2,4 pts/an pendant la régulation (2011–2014), puis
>   remonte après l'annulation par le Conseil d'État : écart des pentes
>   **+3,1 pts/an [1,1 ; 5,1]**. Tendances parallèles : p = 0,24.
>
> Le protocole (sections jusqu'à « How ») a été gelé avant le premier
> calcul. Tout ce qui précède « Résultat » a été écrit, et son empreinte
> SHA-256 notée dans [decisions.md](../decisions.md), **avant** le premier
> calcul sur les effectifs.

## Question
Un backtest ne valide pas un levier : l'historique n'a pas fait varier le
paramètre. Une expérience naturelle, si. Le levier testé est la
**régulation conventionnelle de l'installation** (module
`v2/jumeau/modules/regulation.py` : en zone régulée, entrées ≤ sorties).

## L'expérience naturelle
- **E1 — infirmiers (principale).**
  - Avenant 1 à la convention infirmière (JO du 18 octobre 2009, mesures
    appliquées dès avril 2009) : zonage en 5 classes ; en zone
    « sur-dotée », conventionnement seulement en remplacement d'un départ.
  - Avenant 3 (arrêté du 25 novembre 2011) et arrêté du 21 décembre 2011
    sur la méthode de zonage : **nouveau zonage**, appliqué en 2012.
  - Sources : questions écrites AN (13e législature), instruction
    DGOS/R2/DSS/2012/07 du 4 janvier 2012, presse professionnelle, relevées
    par recherche le 2026-11-14 ; **textes primaires non relus**
    (ledger).
- **E2 — kinés (secondaire, marche / arrêt).** Avenant 3 kiné (arrêté du
  10 janvier 2012) : même régulation en zone sur-dotée. **Annulée** par le
  Conseil d'État le 17 mars 2014 (n° 357594). Rétablie par l'avenant 5
  (2018) sur un nouveau zonage.
- **Pourquoi c'est une expérience :** le statut de la zone vient d'un seuil
  de densité calculé par l'ARS, pas du choix des infirmiers ; la date est
  fixée par la convention.

## Données
- **Résultat Y :** effectif libéral actif au 31/12 par commune, toutes
  tranches d'âge, CartoSanté (`infi_popage`, 2004–2025 ; `kine_popage`,
  2005–2025 ; `dent_popage`, 2006–2025), source FNPS/SNDS.
- **Traitement :** classe de zonage par commune, champs `z_infi`, `z_kine`,
  `z_dent` du jeu Atlasanté uuid c987d0e2 (36 700 communes, anciennes
  régions, donc antérieur à 2016 ; métadonnées 2014). Codes : 1 très
  sous-doté, 2 sous-doté, 3 intermédiaire, 4 très doté, 5 sur-doté,
  9 non défini.
  - Vérification du codage, sans regarder les effectifs : Montpellier,
    Toulon, Brest, Marseille sont en `z_infi` = 5 ; Paris, Saint-Denis,
    Lille en 3.
- **Appariement :** par code commune (COG 2026 côté CartoSanté, COG ~2012
  côté zonage). Commune sans classe → exclue. Classe 9 → exclue. On
  rapporte la part des infirmiers 2008 appariés. Marseille est absente de
  CartoSanté (rapport du chargeur).

## Le protocole (E1)

### Unité et échantillon
- **Cellule = département × classe de zone.** Y_{d,z,t} = Σ des communes
  appariées. Agréger évite le bruit des petites communes (≈ 1/√N) et suit
  l'échelle à laquelle l'ARS a défini le zonage (bassins de vie).
- **Traitée :** z = 5. **Témoin :** z = 3 (intermédiaire, ni aide ni
  contrainte).
- Un département entre s'il a une cellule traitée **et** une cellule témoin
  avec **Y ≥ 10 en 2008**.

### Fenêtres
- **Avant :** 2004–2008 (aucune régulation). **Année de référence : 2008.**
- **Transition, exclue de l'estimation principale :** 2009–2011 (régulation
  de 1re génération, sur un zonage qu'on n'a pas).
- **Après :** 2012–2019. On s'arrête en 2019 : nouveau zonage infirmier
  issu de l'avenant 6 (2019) et COVID en 2020 (date du nouveau zonage
  **supposée**, ledger).

### Estimateur
Avec deux classes par département et des effets fixes département × année,
la DiD se réduit à une différence lisible :
- D_{d,t} = log Y_{d,5,t} − log Y_{d,3,t}.
- **Étude d'événement :** β_k = moyenne_d (D_{d,k} − D_{d,2008}), pour
  k = 2004…2019.
- **Estimation principale :** β = moyenne_d [ moyenne_{t ∈ 2012–2019} D_{d,t}
  − moyenne_{t ∈ 2004–2008} D_{d,t} ], non pondérée (chaque département
  pèse autant).
- **Inférence :** grappes = départements. SE = écart-type entre
  départements / √G ; IC 95 % par la loi de Student à G − 1 degrés de
  liberté.
- **Variante rapportée (non décisive) :** pondérée par Y_{d,5,2008}.

### Tests (ordre fixé)
| # | Test | Passe si | Sinon |
|---|---|---|---|
| T1 | **Tendances parallèles** : (β_2004, …, β_2007) = 0, test de Hotelling T² entre départements → F(4, G − 4) | p ≥ 0,10 | **design invalide** : pas de validation du levier |
| T2 | **Placebo de date** : faux traitement en 2006 sur 2004–2008 seulement (après = 2006–2008, avant = 2004–2005) | IC 95 % contient 0 | design invalide |
| T3 | **Placebo de profession** : même traitement `z_infi` = 5 vs 3, sur les **dentistes** (pas de régulation de leur installation avant 2025, **supposé**, ledger), avant = 2006–2008 | pas (même signe que β_IDE **et** \|β_dent\| ≥ ½ \|β_IDE\|) | effet non attribuable à la régulation |
| T4 | **Placebo de retour à la moyenne** : zone 4 (très dotée, non régulée) vs 3, infirmiers | pas (même signe **et** \|β_4\| ≥ ½ \|β_IDE\|) | effet de convergence, pas de régulation |
| T5 | **Effet** : β_IDE | IC 95 % < 0 | « effet non détecté », borne = IC |

Signe attendu : β < 0. Ordre de grandeur publié : −3 % d'effectif en zone
sur-dotée entre avril 2009 et janvier 2010 (bilan de l'avenant 1, cité par
la presse ; non vérifié).

### Test du mécanisme du jumeau (le levier « de bout en bout »)
Le module `regulation` impose entrées ≤ sorties en zone régulée. Un plafond
**parfaitement contraignant** depuis 2009 garde l'effectif traité au plus à
son niveau de 2008. Contre-factuel : la zone 5 aurait crû comme la zone 3
du même département.
- Effet prédit par le module : β_mod = moyenne_d moyenne_{t ∈ 2012–2019}
  min(0, −(log Y_{d,3,t} − log Y_{d,3,2008})).
- Effet observé, même référence : β_obs = moyenne_d moyenne_{t ∈ 2012–2019}
  (D_{d,t} − D_{d,2008}).
- **θ = β_obs / β_mod**, « part contraignante » du plafond. IC par bootstrap
  des départements (2 000 tirages, graine 20261114).
- **Verdict :**
  - IC de θ contient 1 → le module « plafond strict » **survit** ;
  - IC dans ]0, 1[ → module **remplacé** par un plafond qui fuit, de
    paramètre θ (fiche axe 1) ;
  - IC contient 0 → régulation sans effet détectable.
- Condition : T1 à T4 passés. Sinon θ n'est pas interprété.

## Protocole E2 (kinés, secondaire)
Mêmes cellules et règles, `z_kine` = 5 vs 3, effectif kiné, référence 2011,
avant 2005–2011.
- **Marche :** 2012–2014. **Arrêt :** 2015–2017. On s'arrête en 2017
  (avenant 5 en 2018, autre zonage).
- **Prédiction pré-enregistrée :** pente de D en marche (régression de
  D_{d,t} − D_{d,2011} sur t, 2011–2014) < 0, et pente en arrêt (2014–2017)
  > pente en marche.
- Tendances parallèles : Hotelling sur 2005–2010 vs 2011, p ≥ 0,10.

## Ce qui falsifierait le protocole lui-même
- Le jeu Atlasanté ne serait pas le zonage 2012 (par exemple une révision
  de 2014 construite sur des densités post-2012). Le traitement serait alors
  en partie choisi sur le résultat. Indice à contrôler : anciennes régions
  et métadonnées 2014 → compatible avec 2012–2014, pas prouvé.
- L'exclusion de 2009–2011 cache un effet déjà présent. L'étude d'événement
  le montre ; on le rapporte sans changer l'estimation principale.

## How
- **Code :** [`v2/validation/did.py`](../../../validation/did.py) ;
  données brutes du zonage dans `v2/validation/raw/`.
- **Commande :** `uv run --with scipy python -m validation.did`
  depuis `v2/`.
- **Sorties :** `v2/validation/out/did_*.csv` et `did_results.json`.

---

## Résultat (ajouté après le gel, 2026-11-14 03:0x)

Commande réelle : `PYTHONPATH=v2 uv run --with scipy python -m validation.did`
depuis la racine du dépôt (le « How » ci-dessus disait « depuis `v2/` » :
détail d'exécution, pas un choix de protocole). Machine : ~3 s.
Sorties : `v2/validation/out/did_results.json` et `did_*_event_study*.csv`.

### Appariement
- Infirmiers 2008 : 9 800 communes sur 9 801, 57 366 infirmiers sur
  57 369 appariés au zonage ; aucun en classe 9.
- Dentistes 2008 : 33 787 sur 33 793. Kinés 2011 : 51 804 sur 51 813.

### E1 — infirmiers, z_infi 5 vs 3 (G = 59 départements)
| Test | Résultat | Seuil | Verdict |
|---|---|---|---|
| T1 tendances parallèles (Hotelling, 2004–2007 vs 2008) | F(4, 55) = 2,65, **p = 0,043** | p ≥ 0,10 | **échoue** |
| T2 placebo de date 2006 | +1,4 % [−0,7 ; +3,4] | IC contient 0 | passe |
| T3 placebo dentistes (G = 43) | +1,7 % [−1,3 ; +4,7] | pas même signe ≥ ½ | passe |
| T4 placebo zone 4 vs 3 (G = 42) | −4,2 % [−9,6 ; +1,3] | pas même signe ≥ ½ \|β\| = 15 % | passe |
| **T5 effet** (2012–2019 vs 2004–2008) | **−30,3 % [−34,1 ; −26,4]** (log-points ×100) | IC < 0 | effet détecté |
| Pondéré par l'effectif 2008 (non décisif) | −37,9 % [−48,9 ; −26,9] | — | — |
| Transition 2009–2011 (rapporté) | −1,1 % [−3,9 ; +1,8] | — | — |
| Zone 1 (incitations) vs 3 (rapporté) | **+11,3 % [+5,9 ; +16,6]** | — | — |

**Verdict du protocole : design invalide (T1), levier non validé.** θ
n'est donc pas interprété au sens du protocole. Sa valeur, pour mémoire :
**θ = 0,80 [0,74 ; 0,87]** (β_obs = −32,4 %, β_mod = −40,5 %).

Étude d'événement (β_k = écart de D à 2008, en log-points) :

| 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| −0,030 | −0,028 | −0,022 | −0,025 | 0 | −0,011 | −0,029 | −0,059 | −0,102 | −0,186 | −0,242 | −0,319 | −0,366 | −0,419 | −0,456 | −0,501 |

Lecture : les quatre années d'avant sont **au même niveau** entre elles
(−0,022 à −0,030) ; c'est **2008** qui dépasse de ~3 points. T1 rejette
donc un saut en 2008, pas une tendance. Ensuite, l'écart se creuse de 5 à
8 points par an à partir de 2011–2012, sans plateau jusqu'en 2019.

### Exploratoire (hors protocole, écrit après avoir vu T1)
`v2/validation/did_explore.py` → `out/did_explore.json`. **Ne valide rien.**
- Tendance pré-période linéaire extrapolée : +0,64 pt/an (la zone
  sur-dotée montait *plus* vite avant). Corrigé : **−36,4 %**. La violation
  va dans le sens contraire de l'effet : l'estimation principale serait
  plutôt prudente.
- Borne de Rambachan & Roth (2023), « relative magnitudes », M̄ = 1 :
  intervalle **[−52,7 % ; −7,9 %]**. Le signe tient même si les violations
  après 2008 sont aussi fortes que la plus forte d'avant.

### E2 — kinés, z_kine 5 vs 3 (G = 26–29)
| Test | Résultat | Prédiction | Verdict |
|---|---|---|---|
| Tendances parallèles (2005–2010 vs 2011) | F(6, 20) = 1,47, p = 0,24 | p ≥ 0,10 | passe |
| Pente en marche 2011–2014 | **−2,4 pts/an [−3,5 ; −1,2]** | < 0 | confirmée |
| Pente en arrêt 2014–2017 | +0,7 pt/an [−0,7 ; +2,1] | > pente en marche | — |
| Écart des pentes | **+3,1 pts/an [+1,1 ; +5,1]** | > 0 | **confirmée** |

Étude d'événement kinés (réf. 2011) : 2005 −0,095 ; 2008 −0,002 ; 2012
−0,026 ; 2014 −0,070 ; 2017 −0,044. La zone sur-dotée décroche pendant les
deux ans et demi de régulation, puis cesse de décrocher.

## ⚑ What could make it wrong
- **Le verdict IDE tient à un seuil.** p = 0,043 contre 0,10. Le seuil était
  fixé d'avance ; on ne le change pas après coup. Un nouveau protocole
  (par exemple la borne de Rambachan & Roth fixée d'avance) peut être
  pré-enregistré et lancé : ce serait un *second* test, déclaré comme tel.
- **Zone 4 décroche aussi** (−9 % en 2019, −4,2 % en moyenne) : une partie
  de l'effet IDE (jusqu'à ~1/7) peut être un retour à la moyenne des zones
  denses, pas la régulation. T4 passe, mais l'effet n'est pas nul.
- **Le zonage n'est pas daté avec certitude** (métadonnées 2014, anciennes
  régions). S'il s'agit d'une révision 2014 fondée sur des densités
  post-2012, le traitement est en partie choisi sur le résultat.
- **Kinés : la zone 5 ne compte que 547 communes** et G = 26–29 ; le
  pré-2008 montre une remontée (−9,5 % en 2005) que Hotelling, peu
  puissant à G = 26, ne rejette pas.
- Les classes de zonage et la date d'application viennent de sources
  secondaires (presse, questions écrites) ; textes primaires non relus.

## → What it changes
- **Module `regulation` du jumeau (axe 0) :** pas encore validé de bout en
  bout. L'indice exploratoire θ ≈ 0,8 suggère un plafond **qui fuit** (la
  zone sur-dotée a continué de croître un peu), pas un plafond strict.
  À transmettre à l'axe 1 comme paramètre *supposé* (fiche), pas mesuré.
- **Kinés :** la régulation a un effet détectable et réversible sur la
  pente. C'est le premier levier dont une prédiction pré-enregistrée passe ;
  ce n'est pas encore une validation du module (θ n'était pas
  pré-enregistré pour E2).
- **Zone 1 (incitations) :** +11 % en relatif. Le levier L21 (aides à
  l'installation) a donc un ordre de grandeur mesurable, hors protocole.

## ? Next
| Item | Cost |
|---|---|
| Pré-enregistrer puis lancer un 2e test IDE : borne Rambachan & Roth M̄ fixé d'avance, ou contrôle synthétique | ~30 min Claude |
| Pré-enregistrer θ pour E2 (kinés) et le lancer : premier module validé de bout en bout si l'IC contient 1 | ~15 min |
| Dater le jeu Atlasanté c987d0e2 (comparer à un arrêté ARS 2012 publié, une région) | ~30 min |
| Lire les textes primaires (avenants 1 et 3 IDE, arrêté du 21/12/2011) pour les dates d'effet | ~30 min |

---

## Second test (2026-11-14, nuit) : au grain communal
Pré-enregistré dans [N7](2026-11-14-axe3-n7-addendum.md) § A, avant calcul.
Comparaison dans les bassins de vie 2022 : T1 **p = 0,025** et placebo de date
**+2,6 % [+0,1 ; +5,1]** → design toujours invalide ; effet −32,2 %
[−37,2 ; −27,3]. Kinés : tendances p = 0,059 (échoue), écart des pentes
+3,3 pts/an [+0,8 ; +5,8].
