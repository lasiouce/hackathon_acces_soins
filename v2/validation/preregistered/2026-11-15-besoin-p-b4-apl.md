---
type: analysis
date: 2026-11-15
author: session besoin axe 3
question: M4 (2SFCA paramétré comme la DREES, composé avec M1) reproduit-il l'APL DREES 2024 commune par commune, mieux que deux densités naïves ?
headline: "Protocole pré-enregistré, gelé avant tout calcul de M4 : succès si Spearman ≥ 0,90, erreur relative absolue médiane ≤ 15 % et gain ≥ 0,05 de Spearman sur la meilleure des deux densités naïves (commune, bassin de vie), borne basse de l'IC 98,75 % du gain > 0 (bootstrap des départements) ; paramètres publiés seulement ; seuils supposés"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes, sages-femmes]
hypothesis: H-B4 (dérivation du besoin, §6 M4) ; test d'abandon P-B4 (§8)
sources: [APL DREES millésimes 2022–2024 (fichiers communaux, onglet Paramètres), Insee populations communales 2022, effectifs libéraux du jumeau au 31/12/2022, OSRM sur OpenStreetMap (ODbL), BV2022 (Insee)]
tags: [validation, besoin, 2SFCA, APL, pre-registration, P-B4]
---

# P-B4 — reproduction de l'APL DREES 2024 (cible externe, protocole pré-enregistré)

> **Headline :** une cible externe que nous ne contrôlons pas. Gelé avant
> l'écriture de M4 et avant la lecture des valeurs d'APL 2024 commune par
> commune.

Provenance des nombres : (s) sourcé, (d) dérivé, (h) supposé.

## Hypothèse
H-B4 : M4∘M1, avec les seuls paramètres **publiés** par la DREES, reproduit
l'APL 2024 au grain communal pour IDE, MK, SF et CD. Les pharmaciens n'ont pas
d'APL (s) et ne sont pas testés.

## Données (jeu, millésime, grain)
- **Cible** : APL DREES **millésime 2024**, commune, par profession (s).
  Celle des SF porte sur les femmes.
- **Entrées, état 2022** (l'APL de l'année N utilise la population et
  l'activité de N−2 (s)) :
  - **population communale 2022** par âge (Insee, recensement : populations
    par commune, sexe et âge quinquennal ; millésime inscrit au passage) ;
  - **poids d'âge** ω de l'onglet « Paramètres » des fichiers APL 2024 (s) ;
  - **offre** `S_j` : effectif libéral de 65 ans au plus par commune au
    31/12/2022 (jumeau, état historique), × ETP moyen départemental. Cet ETP
    vaut honoraires ameli par département divisés par la médiane nationale
    (h ; l'activité individuelle de la DREES n'est pas ouverte).
- **Paliers de distance** publiés (s), à prendre dans l'onglet
  « Paramètres » :

  | Professions | Poids 1 | Poids 2/3 | Poids 1/3 | Poids 0 |
  |---|---|---|---|---|
  | CD, MK, IDE | moins de 10 min | 10 à 15 min | 15 à 20 min | au-delà de 20 min |
  | SF | 0 à 10 min | 10 à 20 min | 20 à 30 min | au-delà de 30 min |

- **Temps d'accès** : OSRM sur l'extrait OpenStreetMap France (axe 4), en
  voiture, entre centres de communes. **Repli** si le distancier n'est pas
  prêt : distance à vol d'oiseau × facteur de détour **1,3** (h) à 50 km/h
  (h). Un verdict obtenu en repli porte la mention « repli » et ne vaut pas
  reproduction.
- **Champ** : communes de France métropolitaine présentes dans l'APL 2024 et
  dans le distancier. Les DROM sont hors champ si l'extrait OSM est
  métropolitain (axe 4).

## Statistiques (par profession)
- `ρ_M4 = Spearman(M4, APL)` sur toutes les communes du champ ;
- `EM = médiane_i |M4_i − APL_i| / APL_i`, sur les communes où `APL_i > 0` ;
- **Références naïves** :
  - (N1) densité de la commune, `S_i / P_i^std` (0 si pas d'offre) ;
  - (N2) densité du **bassin de vie 2022** de la commune, `Σ_BV S / Σ_BV P^std`.
- `G = ρ_M4 − max(ρ_N1, ρ_N2)`.

## Seuil de décision (par profession)
M4 est « **la méthode de l'APL** » pour la profession si les trois conditions
tiennent :
- `ρ_M4 ≥ 0,90` ;
- `EM ≤ 0,15` ;
- `G ≥ 0,05`, et la borne basse de l'IC à 98,75 % de `G` est > 0.

Sinon M4 reste un **indice maison**, étiqueté comme tel, et n'est jamais
présenté comme l'APL. Les seuils sont supposés (h) et figés ici.

## Paramètres libres : aucun dans le passage principal
Aucun paramètre n'est réglé sur l'APL 2024. **Variante secondaire, rapportée
et non décisive** : un seul scalaire multiplie l'ETP. Il est calé pour
minimiser `EM` sur l'APL **2022** (entrées 2020), puis appliqué tel quel à
2024.

## IC
Bootstrap **des départements** : on tire des départements entiers avec
remise et on garde toutes leurs communes. Le calcul de M4 n'est pas refait :
on rééchantillonne les communes déjà calculées. B = 2 000, graine 20261115,
IC percentile pour `ρ_M4`, `EM` et `G`.

## Multiplicité
Bonferroni sur les **4 professions** : IC à **98,75 %**.

## Contrôle gratuit (bloquant)
Conservation : `Σ_i P_i^std · A_i = Σ_j S_j` à 10⁻⁹ près en valeur relative.
Si elle échoue, le passage s'arrête : c'est un défaut de code, pas un
résultat.

## Placebo
Aucun (la cible est externe).

## Rapporté, non décisif
- Spearman par tranche de taille de commune (moins de 1 000, 1 000 à 10 000,
  plus de 10 000 habitants) ;
- reproduction du millésime 2023 avec les entrées 2021 ;
- les 20 communes les plus écartées.

## ⚑ Menaces écrites
- **Seuils supposés.** 0,90, 15 % et 0,05 n'ont pas d'étalonnage externe
  (h). Aucune reproduction ouverte de l'APL n'a été trouvée pour s'y
  comparer (passe de littérature).
- **ETP non ouvert.** `S_j` approxime l'activité individuelle par une
  moyenne départementale (h). C'est la principale source d'écart attendue :
  un échec peut venir de là plutôt que de la méthode.
- **Distancier.** OSRM sur OSM n'est pas le distancier Metric de l'Insee
  utilisé par la DREES (même moteur, réseau et date différents) ; le repli à
  vol d'oiseau est plus grossier encore.
- **Effectifs du jumeau.** Ils viennent de la base CartoSanté/RPPS. La DREES
  part du SNIIR-AM : le champ des libéraux actifs peut différer.
- **Corrélation spatiale.** Les communes voisines partagent leur offre : le
  bootstrap par département en tient compte en partie, pas entièrement.

## Règles de gel
Mêmes règles que P-B1. Les valeurs d'APL 2024 ne sont lues commune par
commune qu'après le jeton. Lire les onglets « Paramètres » et « Lisez-moi »
est permis avant le jeton.
