---
type: analysis
date: 2026-11-14
author: Claude (session axe 3)
question: Les bandes d'incertitude du jumeau sont-elles calibrées, et l'estimateur bat-il les références naïves une fois l'incertitude comptée ?
headline: "Protocole pré-enregistré, pas encore lancé : CRPS sur log N à h = 5 (même critère bootstrap que N1), calibration jugée sur la couverture des intervalles à 50 % et 80 % (bandes 44–56 % et 75–85 %), et calibration par simulation (SBC) des paramètres ajustés sur les mondes de N5"
status: protocole gelé (non lancé)
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: axe 3 niveau 6 (ajout daté ; ne modifie ni N1 ni N5)
sources: [Gneiting & Raftery 2007 JASA 102(477) § 4.2 (lu), Gneiting, Balabdaoui & Raftery 2007 JRSS-B 69(2) (lu), Talts et al. 2018 arXiv 1804.06788 § 4.1 (lu), v2/docs/lab/explorations/2026-11-14-etat-de-lart-methodes.md § 3.6]
tags: [validation, axe3, crps, pit, sbc, pre-registration]
---

# Niveau 6 — prévision probabiliste : CRPS, PIT et calibration par simulation (protocole pré-enregistré)

> **Headline:** protocole **gelé, non lancé**. Il **s'ajoute** à N1 et N5
> sans les modifier (ceux-ci restent gelés). N1 juge un point ; N6 juge une
> distribution : est-elle nette, et surtout calibrée ?

## Question
Le jumeau affichera des bandes (axe 5, N4). Une bande « à 80 % » qui ne
contient la vérité que 60 % du temps est fausse, même si le point central
est bon. La MAPE de N1 ne le voit pas.

## Principe
Maximiser la netteté **sous contrainte de calibration** (Gneiting,
Balabdaoui & Raftery 2007). La calibration probabiliste revient à
l'uniformité des valeurs PIT, condition nécessaire mais pas suffisante
(même source). Le CRPS est un score propre (Gneiting & Raftery 2007,
§ 4.2), et il généralise l'erreur absolue.

## Le protocole

### Distribution prédictive
- **Estimateur qui rend des tirages** (bayésien, microsimulation, axe 5) :
  ses tirages, au moins 200 par cellule.
- **Estimateur ponctuel** (cas du stock-flux) : distribution **empirique
  passée**, construite de la même façon pour tous les estimateurs, y
  compris les naïfs :
  - erreurs relatives log(réel / prédit) du même estimateur, même
    profession, même h, sur les origines **dont la cible ≤ l'origine
    courante** (aucune information future) ;
  - distribution prédictive = prédit × exp(e), e tiré dans ces erreurs ;
  - minimum 20 erreurs passées, sinon la cellule est exclue et comptée.
- Données, grille, seuil N ≥ 30, départements : ceux de N1.

### Score principal : CRPS sur l'échelle log
- CRPS(F, y) = E|X − y| − ½ E|X − X′| (forme d'erreur, positive ; Gneiting
  & Raftery 2007, éq. 21 au signe près), calculé sur **log N** et log y.
- Pourquoi l'échelle log : on compare des départements de tailles très
  différentes. Diviser le CRPS par y le rendrait impropre (pondérer un
  score propre par une fonction de y, exploration § 3.6). Le passage au log
  transforme la variable, ce qui garde le score propre.
- Agrégation et critère **identiques à N1** : moyenne par cellule
  profession × origine, h = 5 ; Δ = CRPS(candidat) − CRPS(meilleure naïve
  probabiliste) ; bootstrap des départements (2 000, graine 20261114) ;
  **gagne** si la borne haute < 0.

### Calibration (PIT)
- PIT u = F(y) pour chaque cellule département × profession × origine,
  à h = 5.
- **Critère (sur la couverture, robuste à la corrélation entre
  départements) :**
  - intervalle central à 80 % : couverture observée dans **[75 ; 85] %** ;
  - intervalle central à 50 % : couverture dans **[44 ; 56] %**.
- Rapporté, non décisif : l'histogramme PIT en 10 classes, et le test du
  χ² (non décisif, parce que les départements d'une même origine ne sont
  pas indépendants).
- **Conséquence :** une bande qui échoue ne peut pas être affichée sous son
  niveau nominal. On affiche alors sa couverture mesurée (« bande
  couvrant 68 % des cas passés »).

### Calibration par simulation (SBC), sur les mondes de N5
- Talts et al. (2018), § 4.1 : si l'inférence est correcte, le rang du
  paramètre tiré a priori parmi L tirages a posteriori est uniforme sur
  {0, …, L}.
- **Paramètres :** les taux de rétention par tranche d'âge et l'entrée
  annuelle moyenne, dans un département de taille médiane.
- **Plan :** 200 mondes simulés (générateur N5, monde M3), paramètres vrais
  tirés dans les plages de l'axe 5 ; L = 99 tirages a posteriori, ou
  bootstrap paramétrique pour un estimateur non bayésien ; graine 20261114
  + numéro du monde.
- **Critère :** histogramme des rangs en 20 classes, test du χ² à 19 ddl
  (les mondes sont indépendants), **p ≥ 0,01** pour chaque paramètre, avec
  une correction de Bonferroni sur le nombre de paramètres.
- Un rang en U → incertitude sous-estimée ; en ∩ → surestimée ; asymétrique
  → biais.

## Ce qui falsifierait le protocole lui-même
- Moins de 20 erreurs passées pour la plupart des cellules (seulement
  15 années de données) : la distribution empirique serait trop pauvre.
  On le rapporte, et seules les cellules complètes sont jugées.
- Une couverture correcte en moyenne peut cacher une sous-couverture des
  petits départements. On la rapporte par tiers de taille, sans en faire
  un critère.

## How
- Code à écrire : `v2/validation/probabilistic.py`. Non lancé.
- La forme par échantillon du CRPS suffit (tirages) ; pas de loi supposée.

## ? Next
| Item | Cost |
|---|---|
| Écrire `probabilistic.py` (CRPS, PIT, couverture), tester sur données synthétiques | ~30 min Claude |
| Lancer sur la variante par défaut et les naïfs | ~10 min Claude + ~1 min machine |
| SBC, après le générateur N5 | ~45 min Claude + ~5 min machine |

---

## Résultat (ajouté après calcul, 2026-11-14)
`PYTHONPATH=v2 uv run --with scipy python -m validation.probabilistic` (~4 s)
→ `v2/validation/out/prob_*`. Erreurs du banc N1 produites par l'axe 2
(même code `validation.forecast`, `v2/methodes/out/erreurs_prive.parquet`,
`apc_erreurs.parquet`), périmètre privé.

**N6, bande empirique au même horizon** (h = 5 : origine 2021 seulement,
SF, CD, PH ; 279 cellules par estimateur, comme dérivé avant calcul) :

| Estimateur | CRPS log | Δ vs persistance [IC 95 %] | Couv. 50 % | Couv. 80 % |
|---|---|---|---|---|
| naive_persistance (meilleure naïve) | **0,0633** | — | 34,8 % | 66,0 % |
| naive_tendance | 0,0661 | +0,0029 égalité | 43,0 % | 70,3 % |
| jumeau_taux_locaux | 0,0731 | +0,0098 [+0,0037 ; +0,0161] **perd** | 32,3 % | 56,6 % |
| axe2_shrink_hier | 0,0726 | +0,0093 perd | 32,6 % | 55,6 % |
| axe2_apc (bande empirique) | 0,0691 | +0,0058 perd | 36,2 % | 68,1 % |

Aucune bande n'est calibrée : toutes sont **trop étroites**, et l'histogramme
PIT est chargé à droite (réel au-dessus de la bande) : les erreurs de
l'origine 2016 (cible 2021) étaient plus petites que celles de 2021 → 2026.

**Tirages propres de l'APC** (« estimateur qui rend des tirages ») : non
relancés cette nuit. L'axe 2 a déjà mesuré, avec 100 tirages et toutes les
origines, une couverture de **50 %** pour l'intervalle « 80 % » (rapport
axe 2, `apc_probabiliste`) : sa bande est elle aussi trop étroite.

**SBC** (200 mondes M3, L = 99, bootstrap de Poisson ; contrôle : le calcul
numpy reproduit `fit_rates` à 3·10⁻¹⁶) :

| Paramètre | p (χ², 19 ddl) | Rang moyen / L | Verdict (p ≥ 0,0017) |
|---|---|---|---|
| s40, s45, s50, s55, s60 | 0,54 ; 0,67 ; 0,94 ; 0,14 ; 0,64 | 0,49–0,53 | **passent** |
| entrées annuelles | **3·10⁻⁴⁶** | **0,22** | **échoue** |

Les taux de rétention sont estimés sans biais et le bootstrap de Poisson
mesure bien leur incertitude. **Les entrées sont biaisées vers le haut par le
bruit** (rang de la vérité bas : les tirages la dépassent) : même cause que
M3 dans N5.

**Verdict N6 :** aucune bande calibrée ; sur la seule origine jugeable, la
persistance a le meilleur CRPS ; les entrées du stock-flux échouent la SBC.
