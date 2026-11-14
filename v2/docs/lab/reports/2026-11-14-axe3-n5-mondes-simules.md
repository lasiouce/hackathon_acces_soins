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

---

## Résultat (ajouté après calcul, 2026-11-14)
`PYTHONPATH=v2 uv run --with scipy python -m validation.worlds all` (~40 s)
→ `v2/validation/out/worlds_n5.csv`, `worlds_all.json`. Estimateur :
variante par défaut (stock-flux à taux locaux, v1, identique au jumeau).

**Deux précisions d'exécution, faites avant de lire les résultats** (le
protocole ne les fixait pas) : (1) M4 — la cohorte nombreuse a 55–60 ans **à
l'origine** (donc 44–49 ans au début de l'historique) ; (2) M4 est jugé à
h = 5, horizon où la cohorte est dans les 60 ans et plus.

| Monde | Prédiction | Mesuré (20 réplications) | Verdict |
|---|---|---|---|
| M1 équilibre | \|err. nat.\| ≤ 1 % à h = 15 | max 4·10⁻¹⁴ % | **passe** |
| M3 bruit de Poisson | \|err. nat.\| ≤ 1 % ; MAPE dép. ≈ plancher ±2 pts | 9 réplications sur 20 sous 1 % (moyenne +0,51 %, max 3,59 %) ; MAPE dép. h = 15 **10,2 %** contre plancher **5,7 %** | **échoue** (lecture stricte) |
| M2 cohorte creuse | documenté | −6,4 % national à h = 15 ; 60+ +41 % à h = 10 | — |
| M4 cohorte nombreuse | 60+ surestimés (≥ 16/20) | 60+ **sous**-estimés −34,5 % à h = 5 (0/20 positifs) ; national +3,0 % | **échoue** (signe contraire) |
| M5 entrées +3 %/an | sous-estimation ; \|écart à −12,4 %\| ≤ 3 pts | −19,8 % (20/20) ; écart 7,4 pts | signe **passe**, ampleur **échoue** |
| M6 saut des entrées | sous-estimation | −8,7 % (20/20) | **passe** |
| M7 report du départ | sous-estimation | −3,3 % (20/20) ; 60+ −37 % | **passe** |

**Lecture.**
- Le moteur est exact quand ses hypothèses tiennent sans bruit (M1).
- **Le bruit le biaise vers le haut** (M3) : `min(r, 1)` coupe le bruit vers
  le bas, et l'excédent au-dessus de 1 devient une entrée permanente. La SBC
  (rapport N6) le confirme sur les entrées.
- **Le même mécanisme lit le passage d'une cohorte comme des entrées** (M4) :
  la tranche qui reçoit la cohorte a r > 1, d'où une entrée fictive
  constante (national +3 %) et des 60+ mal placés. La prédiction de signe,
  reprise de l'observatoire, tombe ; l'axe 2 avait vu que ce biais n'a pas de
  signe fixe.
- Les entrées plates sous-estiment toute croissance des entrées, plus fort
  que l'observatoire ne l'annonçait (M5).

**Verdict N5 : échoue** (M3 et M4). Le moteur par défaut n'est pas sûr dès
que les données sont bruitées ou que la pyramide n'est pas stationnaire.
