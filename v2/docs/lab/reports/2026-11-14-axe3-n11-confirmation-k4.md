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

---

## Résultat (ajouté après calcul ; gel 08:50, SHA-256 `4bf54ad0587a`)
Soumissions de l'axe 2 (commit 2ed1f3a ; K4 inscrit avant passage) :
`n10_soumission_k4.parquet` (08:51:30) et
`n10_confirmation_k4_2021h4.parquet` (08:51:38). Jugement avec
`validation.grain.judge` ; étape 2 avec `H = 4`, `JUDGED = {2021}` →
`out/grain_axe2_k4_*`, `out/grain_ref_2021h4_couverture.csv`.

**Verdict : K4 n'est confirmé à aucun grain. Il échoue à l'étape 1 comme à
l'étape 2, pour les trois professions.**

### Étape 1 — N10 (2014–2020, h = 5)
| Profession | Commune | BV | EPCI |
|---|---|---|---|
| Dentistes | 72,5 % ; 5 classes hors bande | 73,6 % ; 5 | 73,5 % ; 6 |
| Infirmiers | 83,0 % ; 4 | 85,1 % ; 5 | 84,4 % ; 3 |
| Kinés | 76,3 % ; 2 | 76,8 % ; 3 | 76,0 % ; 3 |

K4 ne fait pas mieux que K3 (CD 5 / 3 / 3, IDE 3 / 5 / 3, MK 3 / 2 / 1) ;
pour les kinés à l'EPCI, il passe de 1 à 3 classes hors bande.

### Étape 2 — origine réservée 2021, h = 4
| Profession | Commune | BV | EPCI |
|---|---|---|---|
| Dentistes | 74,2 % ; 4 sur 6 classes hors bande | 74,6 % ; 4 sur 6 | 73,2 % ; 4 sur 7 |
| Infirmiers | 82,1 % ; 3 sur 8 | 87,8 % ; 6 sur 7 | 88,1 % ; 6 sur 6 |
| Kinés | 77,2 % ; 3 sur 7 | 76,5 % ; 4 sur 8 | 74,5 % ; 5 sur 8 |

Même forme qu'à l'étape 1 : **dentistes trop étroits** dans les grandes
classes (51 % à l'EPCI, 101–200), **infirmiers trop larges** (86–100 %).

### Références sur 2021, h = 4 (est-ce une période facile ?)
Classes calibrées / classes jugées : la **tendance** de l'unité passe
**8 sur 8 pour les kinés au BV** (7 sur 8 à l'EPCI) ; les autres
estimateurs et professions sont loin (IDE commune répartition-tendance 5 sur
8 ; CD au mieux 3 sur 6). Mais cette même tendance échouait N10 à
2014–2020 (kinés BV : 5 sur 8). **2021 → 2025 est une période facile pour
les kinés** : un passage sur cette seule origine n'aurait rien prouvé.

## → What it changes
- **Affichage : toujours au département** pour IDE, MK et CD.
- Les corrections de largeur par profession n'ont pas tenu. Le défaut est de
  forme : la largeur doit dépendre de la profession **et** de la taille
  (IDE trop larges, CD trop étroits dans les grandes unités), pas d'un
  facteur unique.
