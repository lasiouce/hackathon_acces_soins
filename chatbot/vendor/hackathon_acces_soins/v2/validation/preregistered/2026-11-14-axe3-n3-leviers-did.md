---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: La régulation de l'installation infirmière en zone « sur-dotée » a-t-elle freiné l'effectif libéral, et le module « remplacement seul » du jumeau en reproduit-il la taille ?
headline: "Protocole pré-enregistré ; résultats en section Résultat (ajoutée après le gel)"
status: protocole gelé ; lancé pour les IDE
professions: [infirmiers, kines, dentistes]
hypothesis: axe 3 niveau 3 ; module jumeau `regulation`
sources: [CartoSanté TJS infi/kine/dent_popage 2004–2025 (data/processed/stock_commune.parquet, extrait 2026-11-13), Atlasanté « France – Zonages conventionnels des ARS » uuid c987d0e2-e99c-4a11-a3a4-aa81de6aa416 (génération 2012, métadonnées 2014-10-22, extrait 2026-11-14), avenants 1 (2009) et 3 (2011) de la convention infirmière, CE 17 mars 2014 n° 357594]
tags: [validation, axe3, levier, did, pre-registration, zonage]
---

# Niveau 3 — effet des leviers par expérience naturelle (protocole pré-enregistré)

> **Headline:** voir la section **Résultat**, ajoutée après le gel du
> protocole. Tout ce qui précède « Résultat » a été écrit, et son empreinte
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
