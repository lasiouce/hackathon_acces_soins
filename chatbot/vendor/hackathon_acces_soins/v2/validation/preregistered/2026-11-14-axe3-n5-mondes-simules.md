---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: Un estimateur retrouve-t-il une vérité connue quand on simule un monde qui respecte (ou viole) ses hypothèses ?
headline: "Protocole pré-enregistré, pas encore lancé : 7 mondes simulés à vérité connue (repris de l'observatoire, A1) ; dans un monde qui respecte ses hypothèses, un estimateur doit tenir |erreur nationale| ≤ 1 % à 15 ans ; dans un monde qui les viole, le signe du biais est prédit d'avance"
status: protocole gelé (non lancé)
professions: [synthétique]
hypothesis: axe 3 niveau 5 (ajouté après le gel des niveaux 1 à 4)
sources: [docs/lab/reports/2026-11-14-reprise-observatoire.md (A1, A2), observatoire de l'équipe docs/AUDIT_PROJECTIONS.md § 2.2 (cité, non reproduit)]
tags: [validation, axe3, mondes-simules, pre-registration]
---

# Niveau 5 — mondes simulés à vérité connue (protocole pré-enregistré)

> **Headline:** protocole **gelé, non lancé**. Il est ajouté le 2026-11-14
> **après** le gel des niveaux 1 à 4 et le lancement du niveau 3, mais
> **avant** tout calcul sur un monde simulé. Il teste ce qu'aucun backtest
> ne peut séparer : une erreur vient-elle du modèle ou des données ?

## Question
Sur données réelles, une erreur mêle trois choses : le modèle est faux, les
données sont bruitées, le monde a changé. Dans un monde simulé, la vérité
est connue. On isole donc la première.

## Origine
Reprise de l'élément A1 de l'observatoire de l'équipe
([reprise](2026-11-14-reprise-observatoire.md)). Ses résultats (A2) sont
**cités, non reproduits**. Ils servent ici de prédictions à tester.

## Le générateur
- **30 départements**, taille initiale tirée en log-uniforme entre 30 et
  4 000 professionnels.
- **Âges simples** de 25 à 69 ans, deux sexes. Sorties par âge connues :
  hasard de 0,5 %/an avant 55 ans, puis rampe jusqu'à 100 % à 70 ans.
  Entrées à 25–34 ans.
- **Agrégation comme le RPPS** : tranches de 5 ans × sexe × département,
  comptes entiers (tirage de Poisson dans le monde « bruit »).
- **Historique** : 12 ans (estimation) ; **projection** : 15 ans.
- **20 réplications** par monde, graine 20261114 + numéro de réplication.

## Les 7 mondes
| # | Monde | Hypothèse violée pour un stock-flux à entrées plates et âges uniformes dans la tranche | Prédiction pré-enregistrée pour la variante par défaut (N1) |
|---|---|---|---|
| M1 | Équilibre (pyramide stationnaire) | aucune | \|erreur nationale\| ≤ 1 % à h = 15 |
| M2 | Pyramide non stationnaire (cohorte creuse) | âges uniformes dans la tranche | signe : erreur ≠ 0, documentée ; sans seuil |
| M3 | M1 + bruit de Poisson | aucune | \|erreur nationale\| ≤ 1 % ; MAPE dép. ≈ plancher de Poisson ±2 pts |
| M4 | Cohorte nombreuse de 55–60 ans | âges uniformes dans la tranche | **surestimation** des 60+ (l'observatoire cite +8 à +19 %) |
| M5 | Entrées +3 %/an | entrées plates | **sous-estimation** nationale à h = 15 (l'observatoire cite −12,4 %) ; on prédit \|écart à −12,4 %\| ≤ 3 pts |
| M6 | Saut des entrées +40 % en milieu d'historique | entrées = moyenne de la fenêtre | sous-estimation |
| M7 | Report de l'âge de départ pendant l'historique | taux de sortie stationnaires | surestimation des sorties futures → sous-estimation |

## Critère
- **Passe** : M1 et M3 au seuil (mondes qui respectent les hypothèses), et le
  signe prédit observé dans M4–M7 sur au moins 16 réplications sur 20.
- **Échoue** : M1 ou M3 hors seuil (le moteur est faux même quand ses
  hypothèses tiennent), ou un signe contraire à la prédiction (le mécanisme
  du biais est mal compris).
- Chaque estimateur inscrit au registre N1 doit déclarer, **avant** son
  passage, quels mondes respectent ses hypothèses.

## Ce qui falsifierait le protocole lui-même
- Le générateur et l'estimateur partagent un code ou une hypothèse cachée
  (même vieillissement par tranche, par exemple) : le test passerait par
  construction. D'où les âges simples dans le générateur. Les deux revues
  adversariales du jumeau ont trouvé ce défaut dans ses critères
  d'acceptation.

## How
- Code à écrire : `v2/validation/worlds.py`. Non lancé.

## ? Next
| Item | Cost |
|---|---|
| Écrire le générateur et lancer M1–M7 sur la variante par défaut | ~1 h Claude + ~2 min machine |
