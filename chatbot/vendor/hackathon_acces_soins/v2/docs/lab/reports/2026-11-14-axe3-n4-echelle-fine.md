---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: En dessous de quelle taille de commune une projection ne doit-elle jamais être affichée sans sa bande ?
headline: "Protocole pré-enregistré, pas encore lancé : N_min = plus petite classe de taille où le P80 de l'erreur absolue à 5 ans ≤ 25 % (3 professions, ≥ 3 origines sur 4) ; prédiction dérivée du seul bruit de Poisson : N_min ≥ 16"
status: protocole gelé (non lancé)
professions: [infirmiers, kines, dentistes]
hypothesis: axe 3 niveau 4
sources: [CartoSanté TJS infi/kine/dent_popage 2004–2025 (data/processed/stock_commune.parquet)]
tags: [validation, axe3, commune, pre-registration]
---

# Niveau 4 — échelle fine (protocole pré-enregistré)

> **Headline:** protocole **gelé, non lancé**. On mesure l'erreur de
> projection communale à 5 ans par classe de taille, et on publie
> **N_min** : en dessous, une projection communale n'est jamais affichée
> sans sa bande (ou elle est agrégée à un groupe de communes).

## Question
Le DG d'ARS veut la commune (décision 2026-11-14). Mais une commune de
5 infirmiers a un bruit d'environ ±45 % (dérivé, 1/√5). Où passe la
frontière entre une projection lisible et une projection qui n'est que du
bruit ?

## Prédiction dérivée (avant les données)
- Bruit de Poisson seul : |erreur| ≈ 1/√N. Au P80 d'une loi normale,
  1,28/√N ≤ 25 % ⇒ **N ≥ 26** ; à la médiane (0,67/√N), N ≥ 7.
- On se fixe une borne basse plus prudente, **N_min ≥ 16** (1/√N ≤ 25 %).
- À cela s'ajoute la dérive (déménagements, installations) : on attend
  N_min entre 20 et 50.
- **Falsifiable :** si N_min mesuré < 16, l'erreur est plus petite que le
  bruit de Poisson. C'est suspect : effectifs lissés ou masqués par la
  source.

## Le protocole

### Données
- `data/processed/stock_commune.parquet` (CartoSanté, effectif libéral au
  31/12, sans sexe). Infirmiers, kinés, dentistes. SF et PH ne sont pas
  disponibles à la commune ; ils sont exclus et le rapport le dit.

### Fenêtres
- **Origines : 2014, 2016, 2018, 2020.** Horizon principal **h = 5**
  (cibles 2019, 2021, 2023, 2025). Rapporté aussi : h = 1, 3.
- Ajustement : les 6 années jusqu'à l'origine incluse.

### Estimateurs communaux
1. Persistance.
2. Tendance linéaire communale.
3. **Défaut : projection départementale × part communale tenue à son
   niveau de l'origine** (la règle de répartition prévue). La projection
   départementale vient de la variante par défaut du niveau 1 ; tant
   qu'elle n'est pas lancée, on utilise la **vraie** valeur départementale
   de la cible (oracle). Cela isole l'erreur de *répartition*, qui est
   celle que ce niveau mesure.
4. Tout estimateur qui renvoie `predict(target)` par commune.

### Classes de taille (N à l'origine)
{1–2, 3–5, 6–10, 11–20, 21–50, 51–100, 101–200, > 200}. Les communes à
N = 0 à l'origine sont comptées à part (erreur absolue en effectif, pas en
%).

### Métriques par classe
- **Principale : P80 de |erreur| en %**, à h = 5, pour l'estimateur par
  défaut.
- Rapportées : médiane, WAPE, biais signé ; nombre de communes ; et le
  plancher de Poisson 1,28/√N.

### Règle d'affichage (critère)
- **N_min = borne basse de la plus petite classe telle que, pour elle et
  toutes les classes au-dessus, P80 ≤ 25 %**, pour les trois professions,
  dans au moins 3 origines sur 4.
- Sous N_min : la projection est montrée **avec** sa bande empirique (P10–
  P90 de l'erreur de la classe), ou agrégée au groupe de communes.
- Le seuil de 25 % est **choisi** : au-delà, l'erreur dépasse l'écart entre
  deux classes de densité usuelles. À réviser avec l'axe 5.

### Calibration de la bande
- Bandes construites sur les origines 2014–2018, testées sur l'origine
  2020.
- Couverture nominale 80 % ; acceptée si la couverture observée est entre
  **75 et 85 %** dans chaque classe ≥ 3–5.

## Ce qui falsifierait le protocole lui-même
- L'erreur ne décroît pas avec N (non monotone sur ≥ 2 classes
  consécutives) : la taille n'est pas le bon critère. On testerait alors
  rural / urbain (grille de densité Insee) ou le taux de rotation.
- Les communes nouvelles (fusions depuis 2015) créent des sauts d'effectif
  qui ne sont pas des erreurs de projection : on exclut les communes dont
  l'effectif saute de plus de 3 fois l'écart de Poisson d'une année sur
  l'autre, et on rapporte combien.

## How
- **Code :** [`v2/validation/fine_scale.py`](../../../validation/fine_scale.py)
  (`size_errors(pred, actual, origin_n)`), testé sur données synthétiques
  ([`selftest.py`](../../../validation/selftest.py)).
- Non lancé : pas demandé dans cette session, et la projection
  départementale par défaut n'est pas encore figée.

## ⚑ What could make it wrong
- L'oracle départemental sous-estime l'erreur totale : il retire l'erreur
  départementale (≈ 8 % de MAPE à 5–8 ans, K1). L'erreur réelle combine les
  deux.
- CartoSanté a 92 cellules où les tranches d'âge ≠ le total (rapport du
  chargeur) : bruit de source **supposé** négligeable.
- Sans sexe à la commune, le module de sorties du jumeau ne peut pas être
  ajusté localement.

## → What it changes
- Axe 5 et couche application : sous N_min, aucune projection communale
  sans bande.
- Groupes de communes (question ouverte héritée de la v1) : N_min dit à
  partir de quelle taille un groupe devient affichable seul.

## ? Next
| Item | Cost |
|---|---|
| Lancer avec l'oracle départemental (répartition seule) | ~15 min Claude + ~1 min machine |
| Relancer avec la projection départementale par défaut du niveau 1 | ~10 min, après le niveau 1 |

---

## Résultat (ajouté le 2026-11-14, matin)
`PYTHONPATH=v2 uv run --with scipy python -m validation.fine_scale_run`
(~7 s) → `v2/validation/out/fine_*`.

**Exclusions (sauts > 3 écarts de Poisson)** : 2 651 / 134 790
commune-origine-horizons (IDE), 1 838 / 101 484 (MK), 916 / 73 305 (CD).

**P80 de |erreur| à h = 5, estimateur par défaut (oracle départemental ×
part tenue), en %** :

| Classe | CD 2014 | 2016 | 2018 | 2020 | IDE 2014 | 2016 | 2018 | 2020 | MK 2014 | 2016 | 2018 | 2020 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1–2 | 39,5 | 46,7 | 46,8 | 44,6 | 39,1 | 41,6 | 42,9 | 44,3 | 45,3 | 45,3 | 45,0 | 44,3 |
| 3–5 | 40,6 | 46,8 | 49,4 | 55,2 | 43,4 | 42,7 | 41,3 | 40,6 | 51,2 | 55,6 | 57,8 | 58,3 |
| 6–10 | 31,7 | 31,4 | 36,2 | 39,6 | 34,5 | 32,5 | 31,6 | 28,9 | 42,0 | 40,8 | 42,3 | 42,4 |
| 11–20 | 24,6 | 24,6 | 27,9 | 32,5 | 28,6 | 25,1 | 23,4 | 22,4 | 30,7 | 30,1 | 31,0 | 32,9 |
| 21–50 | 20,7 | 18,9 | 18,4 | 22,8 | 24,7 | 18,5 | 16,7 | 18,3 | 21,0 | 22,9 | 25,4 | 26,3 |
| 51–100 | 12,8 | 10,4 | 10,5 | 11,6 | 20,5 | 14,1 | 14,6 | 15,5 | 14,2 | 14,4 | 21,0 | 20,4 |
| 101–200 | 6,8 | 5,4 | 7,9 | 12,0 | 16,2 | 11,8 | 9,2 | 12,7 | 9,4 | 12,5 | 20,1 | 19,0 |
| > 200 | 6,9 | 6,4 | 4,3 | 6,8 | 4,7 | 7,8 | 10,3 | 14,3 | 6,0 | 5,8 | 12,2 | 15,2 |

N_min par profession × origine : CD 11 / 11 / 21 / 21 ; IDE 21 / 21 / 11 /
11 ; MK 21 / 21 / **51 / 51**.

**N_min (règle : 3 professions, ≥ 3 origines sur 4) = 51.** Il est fixé par
les kinés aux origines récentes (leur forte croissance). Pour CD et IDE
seuls, il serait de 21. La prédiction dérivée (N_min ≥ 16, attendu 20–50)
tient pour le plancher ; la valeur dépasse de peu la fourchette attendue.

Toutes classes et professions confondues, à h = 5 : le défaut bat la
persistance à partir de 11 professionnels (27,8 contre 29,1 %) ; la tendance
communale est la pire partout (91,7 % de P80 pour 1–2).

**Bande P10–P90 par classe** (calibrée sur 2014–2018, testée sur 2020) :
couverture dans [75 ; 85] % pour **14 classes sur 21** (classes ≥ 3) ; les
échecs sont surtout dans les grandes classes à peu de communes (> 100 :
55–70 %).

**Monotonie** : l'erreur décroît avec N, sauf une inversion entre 1–2 et 3–5
(une seule classe : le falsificateur, « ≥ 2 classes consécutives », ne joue
pas).

**Verdict N4 : N_min = 51.** Sous 51 professionnels, une projection
communale n'est pas affichée sans sa bande, ou elle est agrégée au groupe de
communes. ⚑ L'oracle retire l'erreur départementale (≈ 8 % de MAPE à 5 ans) :
l'erreur réelle est plus grande.
