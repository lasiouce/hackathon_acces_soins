---
type: analysis
date: 2026-11-15
author: session besoin-cible-pharmaciens
question: M4 (2SFCA), avec les paramètres publiés de l'APL DREES V0 et une offre en officines, reproduit-il l'APL DREES 2013 aux pharmacies commune par commune, mieux que deux densités naïves ?
headline: "Protocole pré-enregistré, gelé avant tout calcul de M4 pharmaciens : succès si Spearman ≥ 0,90, erreur relative absolue médiane ≤ 15 % et gain ≥ 0,05 de Spearman sur la meilleure densité naïve (commune, bassin de vie), borne basse de l'IC 95 % du gain > 0 (bootstrap des départements) ; seuils repris de P-B4, supposés"
status: protocole gelé (non lancé)
professions: [pharmaciens]
hypothesis: H-B4 (dérivation du besoin, §6 M4), extension aux pharmaciens
sources: [APL DREES Méthode initiale V0 2010/2013 (jeu 530, Licence Ouverte 2.0, fichier pharmacies et Notice APL), BPE 2013 et 2010 (Insee, pharmacies), Insee RP 2011 et 2008 (populations municipales), OSRM sur OpenStreetMap (ODbL), BV2012 (Insee), Insee accès aux équipements (carreaux 200 m, Licence Ouverte 2.0)]
tags: [validation, besoin, 2SFCA, APL, pharmaciens, pre-registration, P-B4-PH]
---

# P-B4-PH — reproduction de l'APL DREES V0 aux pharmacies (cible externe)

> **Headline :** la seule APL publiée des pharmacies est celle de la méthode
> V0 (2010, 2013). Gelé avant tout calcul et avant la lecture des valeurs
> d'APL commune par commune.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé. Source :
[exploration](../../docs/lab/explorations/2026-11-15-besoin-cible-pharmaciens.md).

## Hypothèse
H-B4-PH : la mécanique M4 (2SFCA à paliers), avec les paramètres **publiés**
de la V0, reproduit l'APL V0 2013 aux pharmacies au grain communal. Le test
porte sur la mécanique, pas sur les paliers 2022+ utilisés en projection.

## Données (jeu, millésime, grain)
- **Cible** : colonne « APL 2013 (nouveau distancier) » du fichier
  `…aux pharmaciennes libérales.csv`, 36 747 lignes, commune (s).
- **Offre** `S_j` : **nombre d'officines** par commune, sans ETP (la V0
  compte « les effectifs d'officines » (s, Notice)). La DREES les prend dans
  le SNIIR-AM, non ouvert (s) : on prend la **BPE 2013 de l'Insee**, type
  « pharmacie » (Licence Ouverte), code lu dans la nomenclature 2013 au
  passage. Pour 2010 : BPE 2010.
- **Demande** : **population municipale du recensement 2011** (Insee) pour
  2013, RP 2008 pour 2010 (s, Notice). **Population brute** : la Notice ne
  décrit de pondération par âge que pour les médecins et ne publie pas les
  poids (EGB, non ouvert) (s).
- **Paliers** (Notice) (s) : poids 1 de 0 à 5 min, 0,3 de 5 à 10 min, 0,1 de
  10 à 15 min, 0 au-delà.
- **Temps d'accès** : OSRM sur OSM (axe 4), centre à centre. La DREES
  utilise Metric (Insee) pour 2013 et « APL 2010 (nouveau distancier) » (s). Repli à vol
  d'oiseau × 1,3 (h) : verdict marqué « repli », ne vaut pas reproduction.
- **Champ** : communes métropolitaines présentes dans la cible et dans le
  distancier, après passage du code 2013 au code courant par la table de
  passage Insee (communes fusionnées exclues si la table ne les apparie pas
  une à une).

## Statistiques
- `ρ_M4 = Spearman(M4, APL)` sur toutes les communes du champ ;
- `EM = médiane_i |M4_i − APL_i| / APL_i`, sur `APL_i > 0` ;
- **Références naïves** : (N1) officines de la commune / population ;
  (N2) idem au **bassin de vie 2012** ;
- `G = ρ_M4 − max(ρ_N1, ρ_N2)`.
- Unité : **officines pour 100 000 habitants** (d : la Notice l'écrit pour
  les ETP des autres professions) ; M4 est multiplié par 10⁵, aucun facteur
  calé sur la cible. Le Spearman n'en dépend pas.

## Seuil de décision
M4 est « la méthode de l'APL » pour les pharmacies si :
- `ρ_M4 ≥ 0,90` ;
- `EM ≤ 0,15` ;
- `G ≥ 0,05` et la borne basse de l'IC à 95 % de `G` est > 0.

Sinon M4 pharmaciens reste un **indice maison**. Seuils repris de P-B4,
supposés (h).

## Paramètres libres
Aucun. Pas de variante calée.

## IC
Bootstrap des départements, B = 2 000, graine 20261115, IC percentile pour
`ρ_M4`, `EM` et `G`.

## Multiplicité
Un seul test décisif (une profession, un millésime) : IC à 95 %. La
reproduction 2010 est rapportée, non décisive.

## Contrôle gratuit (bloquant)
Conservation `Σ_i P_i · A_i = Σ_j S_j` à 10⁻⁹ près en relatif.

## Placebo
Aucun (cible externe).

## Rapporté, non décisif
- APL 2010 (nouveau distancier) avec offre et population 2010 ;
- Spearman par taille de commune (< 1 000, 1 000–10 000, > 10 000) ;
- **contrôle du distancier** : temps OSRM du jumeau vers l'officine la plus
  proche contre le temps Insee (carreaux 200 m agrégés à la commune,
  pondérés par la population), Spearman et écart médian en minutes ;
- les 20 communes les plus écartées.

## ⚑ Menaces écrites
- **Paliers courts.** À 5 min, l'erreur du distancier pèse plus que pour
  P-B4 (10 min). Un échec peut venir d'OSRM/OSM contre le distancier DREES
  de 2013.
- **Paliers empruntés.** La DREES n'avait pas de flux de patients pour les
  pharmacies (s) : la cible n'est pas validée comme mesure d'accès, seulement
  comme calcul reproductible.
- **Offre 2013.** La BPE (Insee) n'est pas le SNIIR-AM de la DREES : écarts
  possibles (officines ouvertes ou fermées en cours d'année, antennes).
- **Population brute** : si la DREES a pondéré par âge pour les pharmacies,
  l'écart en vient en partie.
- **Géographie communale 2013** : fusions depuis, appariement imparfait.
- **Ancienneté.** Un succès sur 2013 ne dit rien des paramètres utilisés en
  projection 2050.
- **Seuils supposés**, non étalonnés.

## Règles de gel
Notice lue avant le gel (permis). Gel accordé par l'utilisateur·rice le
2026-11-15 (« Oui et oui », relayé par la session de dérivation) ; jetons
dans `horodatage/2026-11-15-besoin-p-b4-ph-SHA256SUMS*`. Mêmes règles que
P-B1. Les valeurs d'APL ne
sont lues commune par commune qu'après le jeton.
