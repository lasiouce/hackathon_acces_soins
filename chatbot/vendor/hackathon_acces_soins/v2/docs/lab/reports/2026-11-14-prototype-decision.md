---
type: analysis
date: 2026-11-14
author: Claude
question: Peut-on construire un écran d'aide à la décision fluide, en direction A, branché sur le vrai jumeau ?
headline: "Oui. Le prototype tourne sur localhost:8766 : un scénario est recalculé en 3 à 32 ms par le jumeau et en 50 à 120 ms aller-retour. L'écart au tendanciel est décomposé exactement par flux. Exemple : kinés, quotas +20 % et régulation → +8 645 en France en 2050 (+5,4 %)"
status: draft
professions: [sages-femmes, dentistes, pharmaciens, kines]
hypothesis: couche personas (exigences « fluide, vraie aide à la décision »)
sources: [jumeau v2, v2/data/processed/secteur_stock.parquet, v2/data/processed/zonage_commune.parquet]
tags: [prototype, interface, direction-A]
---

# Prototype de l'écran de décision (direction A)

> **Mise à jour du 2026-11-14 (après les trois revues et le branchement des
> leviers).** Les chiffres ci-dessous ont été mesurés **avant** les
> corrections du jumeau.
> - Kinés, quotas +20 % : le jumeau corrigé donne +19 110 (+11,9 %) en
>   2050, et non +8 645. L'ancien chiffre combinait les quotas et la
>   régulation, alors un levier biaisé.
> - L'écran expose maintenant 9 leviers en 4 familles : voir l'entrée
>   « Prototype : 9 leviers » de `decisions.md`.
> - Exemple vérifié : kinés, quotas +20 %, étrangers ×1,5, retraite +1 an
>   et régulation vers le salariat → +25 007 (+15,6 %).

> **Headline :** l'écran est branché sur le jumeau. Le jumeau recalcule un
> scénario en 3 à 32 ms, et la page se met à jour en 50 à 120 ms
> aller-retour (mesuré dans le navigateur, au département). L'écart
> scénario − tendanciel est décomposé exactement par flux : la somme des
> flux égale l'écart.

## Ce qu'il fait
Lancement : `uv run python v2/prototype/server.py`, puis
http://localhost:8766 (entrée `decision` de `.claude/launch.json`).

L'écran répond aux 6 critères d'interface inscrits dans `decisions.md` :
1. **Le titre donne l'écart au tendanciel**, en effectif et en %, pour le
   territoire choisi.
2. **Décomposition par flux** (entrées, sorties, régulation, plancher), à
   l'année cliquée sur le graphique. La somme est exacte, car le tendanciel
   et le scénario partent du même état.
3. **Délai d'effet** : une ligne « premiers diplômés en plus » sur le
   graphique et une note sous chaque levier. Quotas : origine + durée des
   études + 1.
4. **Fluidité.** Curseurs regroupés à chaque image, requêtes en vol
   annulées, courbes interpolées en 220 ms, matrice réordonnée avec des
   lignes animées, fil d'Ariane France › région › département. Pas de
   rechargement de page.
5. **Fourchette en hachures**, avec la mention « extrapolée, aucun backtest
   au-delà d'environ 10 ans ».
6. **Matrice ordonnable** département × année, en deux modes : écart au
   tendanciel, ou évolution depuis l'origine. Deux gammes neutres, pétrole
   et bistre, jamais rouge ni vert. Un clic sur une ligne ouvre ce
   territoire.

## Mesures (navigateur intégré, fenêtre de 800 px)
| Cas | Jumeau | Aller-retour | Résultat 2050 |
|---|---|---|---|
| Kinés, France, tendanciel | 3,2–3,7 ms | 109–117 ms | ≈ 160 783 (101 946 en 2026) |
| Kinés, France, quotas +20 %, régulation | 25,4 ms | 97 ms | +8 645 (+5,4 %) : entrées +20 665, régulation −11 493, sorties −537 |
| Kinés, Puy-de-Dôme, mêmes leviers | 32,1 ms | 48 ms | +198 (+11,5 %) |

## ⚑ Ce qui pourrait le rendre faux
- **Les chiffres viennent du jumeau tel qu'il est.** Ses corrections n'ont
  pas été revues de façon indépendante. Le levier retraite garde l'anomalie
  connue de la tranche 65+, signalée dans l'écran.
- **Dentistes : le tendanciel 2050 vaut ≈ 76 400 dans le privé.** Le
  Dossier DREES n°76 donne 61 800 tous modes, avec une autre définition et
  un autre millésime. Notre modèle prolonge le saut récent des entrées.
  À trancher par l'axe 3 (niveau 2) avant toute présentation.
- **Fourchette.** Elle est calculée comme pente × horizon × 1,6 sur le total
  national privé, avec les origines o−9 … o−3. Elle est appliquée telle
  quelle aux départements, ce qui la sous-estime probablement à l'échelle
  locale.
- **Régulation approchée au département.** Un département est régulé si
  au moins 50 % de ses communes sont en « remplacement seul » (kinés :
  13, 2A, 34, 66, 67, 971). Ce n'est pas encore le zonage communal.
- **Infirmiers absents** : la table public / privé n'a ni âge ni sexe.
- **Pas d'échelle communale** : environ 3 s par scénario, ce qui
  demanderait un précalcul.

## → Ce que ça change
- C'est une base concrète pour la couche personas. Les jetons de la
  direction A sont dans `:root` de `v2/prototype/index.html`, à sortir dans
  `design/tokens.json` pour Figma (question ouverte).
- Le serveur montre qu'on peut atteindre la fluidité **sans dupliquer le
  moteur en TypeScript**, contrairement à l'observatoire de l'équipe.

## ? Pour la suite
| Point | Coût |
|---|---|
| Revue adversariale indépendante du jumeau, avant de citer un chiffre | ~3 min machine |
| Tokens W3C + modes Figma (A, B, C) | ~45 min |
| Infirmiers : table public / privé par âge × sexe (axe 4) | ~1 h |
| Échelle communale par précalcul d'une grille de scénarios | ~2 h |
| Fiche territoire exportable (PDF) | ~45 min |
