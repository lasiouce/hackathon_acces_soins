---
type: analysis
date: 2026-11-14
author: session axe 3
question: Comment confirmer hors des origines 2014–2020 une variante communale (K4) qui aura vu le jugement N10 de K3 ?
headline: "Protocole pré-enregistré : K4 passe d'abord N10 tel quel (2014–2020, h = 5), puis une confirmation sur l'origine réservée 2021, h = 4 (cible 2025), jugée avec les mêmes critères et comparée aux références ; confirmation définitive par un dépôt communal 2027"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes]
hypothesis: axe 3, N11 ; décision « Chantier projection communale fiable »
sources: [protocole N10 (SHA-256 d86d27c7a750), proposition de l'axe 2 (origine 2021, h = 4)]
tags: [validation, axe3, commune, calibration, pre-registration, hors-echantillon]
---

# N11 — confirmation de K4 hors des origines 2014–2020 (protocole pré-enregistré)

> **Headline:** gelé avant que K4 existe. Il fixe la règle avant que l'axe 2
> lance quoi que ce soit.

## Pourquoi
Le jugement N10 de K3 a montré où les bandes échouent (IDE trop larges, CD
trop étroites). Une K4 corrigée en connaissance de cause risque de
sur-ajuster ces origines. Il faut un test qu'elle n'a pas vu.

## Étapes
1. **N10 tel quel** : K4 soumise sur 2014–2020, h = 5, jugée par
   `validation.grain.judge`. Résultat rapporté, mais **pas suffisant** seul.
2. **Origine réservée : 2021, h = 4 (cible 2025)**, proposée par l'axe 2,
   qui déclare n'avoir jamais calculé 2021 → 2025 pour un modèle communal.
   - Même format de soumission, fichier séparé.
   - Mêmes unités, même exclusion des sauts (fenêtre 2016–2025), mêmes
     classes, même seuil (≥ 30 unités par classe).
   - **Fiable** à un grain si toutes les classes jugées sont dans
     [75 ; 85] %.
   - **Références jugées sur la même origine** (persistance, tendance,
     répartition-tendance, bandes empiriques par classe tirées des erreurs à
     h = 4 des origines dont la cible ≤ 2021) : pour savoir si 2021 → 2025 est
     une période « facile ».
3. **Verdict K4 à un grain = « confirmé »** seulement s'il passe à la fois
   l'étape 1 et l'étape 2 à ce grain. Passer l'étape 1 seule : « non
   confirmé ».
4. **Confirmation définitive** : dépôt communal de K4, origine 2026 →
   2027 et 2028, avec empreinte, scoré à la publication des données
   CartoSanté 2027.

## Limite annoncée
L'année cible 2025 a déjà été vue comme cible de l'origine 2020 (2020 → 2025,
dans N10). L'origine 2021 partage 4 années sur 5 avec cette fenêtre. L'étape
2 n'est donc pas indépendante ; c'est une confirmation **partielle**. Seul le
dépôt 2027 est vraiment hors échantillon.

## How
- `validation.grain.judge` (étape 1) ; étape 2 : `judge` avec `JUDGED = {2021}`
  et `H = 4`, et les références recalculées à h = 4.
