---
type: analysis
date: 2026-11-14
author: Claude
question: Les critères d'acceptation du jumeau (axe 0) prouvent-ils ce qu'ils annoncent ?
headline: "Non, pas encore. 6 défauts confirmés (4 bloquants, 2 importants) sur 6 soumis à réfutation, plus 3 non vérifiés. L'écart 0,0 de la reproduction tient ; les critères plug-in, levier, agrégation et conservation sont en partie vrais par construction"
status: done
professions: [all]
hypothesis: axe 0
sources: [v2/jumeau (2026-11-14), v2/artifacts/a0_jumeau]
tags: [revue, axe0, jumeau, validation]
---

# Revue adversariale du jumeau (axe 0)

> **Headline :** 6 défauts confirmés sur 6 soumis à réfutation : 4 bloquants
> et 2 importants. Les axes 2 et 5 ne s'appuient pas sur le contrat avant
> que les bloquants soient corrigés.

## Question
Le jumeau annonce quatre critères remplis : reproduction du stock-flux v1
(écart 0,0), agrégation commune → national exacte, plug-in ajoutable sans
toucher aux autres fichiers, 18 ms par scénario. Ces critères
peuvent-ils échouer ?

## Méthode
- Un workflow de 9 agents, qui n'ont modifié aucun fichier. Trois angles
  de revue :
  - les tests peuvent-ils échouer ;
  - la justesse du modèle (conservation, régulation, agrégation) ;
  - le contrat de modules comme socle des autres axes.
- Chaque angle a rendu ses 3 défauts les plus graves. Les 2 premiers ont
  été soumis à un agent chargé de les **réfuter** en lisant et en exécutant
  le code.
- Tous les défauts soumis ont été reproduits. Les chiffres ci-dessous sont
  mesurés par les agents (scripts dans `/private/tmp`, non conservés dans le
  dépôt).

## Résultats

| # | Gravité | Défaut | Où | Preuve (mesurée) |
|---|---|---|---|---|
| 1 | **bloquant** | `TwinEstimator.trajectory(until, scenario)` ignore `scenario.modules` : les modules sont construits une seule fois au `fit`. Un plug-in, ou la régulation, passé par la voie du banc (`twin_of`) n'est pas exécuté, et aucune erreur ne s'affiche. Le test plug-in contourne cette voie, et son contrôle « aucun fichier modifié » ne peut pas échouer (le module factice est écrit dans un dossier temporaire). | `v2/jumeau/estimators.py:26,32-34`, `check.py:90-95,123` | dentistes, régulation dans 10 dép. : écart avec le tendanciel en 2030 = **0,0** |
| 2 | **bloquant** | Le secteur public n'a aucune sortie (s = 1, I = 0, faute d'historique). Les entrants bloqués par la régulation y vieillissent sans jamais partir, si bien que bloquer des installations **crée** des professionnels. Le registre reste équilibré ; la démographie est fausse. | `v2/jumeau/history.py:38-39`, `modules/regulation.py:36,43` | kinés, régulation dans 5 dép., 2026–2050 : **+822** personnes au total en 2050 |
| 3 | **bloquant** | Les interactions entre modules sont implicites. La régulation lit `ctx.deltas["entrees"]` et `["sorties"]` par des noms codés en dur. Aucun module ne déclare ce qu'il consomme ou produit, et seul l'entier `order` fixe l'ordre d'exécution. Si un module est absent ou renommé (méthode de l'axe 2), le résultat est faux sans erreur. | `modules/regulation.py:39-40`, `engine.py:72-74` | sans `sorties`, tous les entrants des zones régulées sont bloqués |
| 4 | **bloquant** | Le scénario n'est pas validé : une clé mal orthographiée (`sorties.decalage_retaite`) est ignorée et donne le tendanciel. Il n'est pas non plus sérialisable : pas de `to_dict`/`from_dict`, pas de version. | `scenario.py:46-47`, `engine.py:31-34` | le levier mal orthographié produit exactement le tendanciel |
| 5 | important | Le test de levier compare la v1 à une copie d'elle-même (`sorties.py` recopie `perturb_retention`). Le levier **quotas**, non testé, démarre un an plus tôt que la v1 : la docstring de `entrees.py` dit o + L_p, la v1 applique o + L_p + 1. | `modules/entrees.py:5`, `check.py:72-88,194` | dentistes, quotas ×1,1 : 83 751 contre 83 525 en 2050 (**+226**) |
| 6 | important | L'agrégation exacte est circulaire : la somme des communes CartoSanté est comparée à des regroupements de ces mêmes lignes. L'écart avec le RPPS départemental n'est pas mesuré. Marseille manque, et seules 3 professions existent à la commune. | `check.py:145-148`, `state.py:74-79` | 2025, kinés : CartoSanté 84 946 contre RPPS 89 766 (**−5,4 %**, dont −2 084 dans le dép. 13) |

**Non soumis à réfutation (plafond de 2 par angle), à vérifier :**
- Le critère de conservation est une identité : le registre stocke
  N(t+1) − N(t). Le résidu de 3·10⁻¹¹ ne mesure que l'arrondi
  (`check.py:179`, `engine.py:90-98`).
- Le vieillissement est codé en dur à 1/5 par an. C'est faux pour les
  tranches communales CartoSanté : 0-39, 40-49, 60+
  (`modules/vieillissement.py:9`).
- `run()` n'est pas reproductible : l'état de `Formation._intake` persiste
  d'un run à l'autre, et le contexte ne fournit ni graine ni RNG pour une
  microsimulation (`modules/formation.py:39`).

## ⚑ Ce qui pourrait rendre ce rapport faux
- Les agents ont relu le code tel qu'il était à la fin du tour de l'axe 0.
  Une correction faite entre-temps peut en périmer une partie.
- Les 3 constats non vérifiés n'ont pas été soumis à réfutation.
- Ne sont pas remis en cause : la reproduction du stock-flux v1 (écart 0,0
  par cellule × âge jusqu'en 2050), qu'aucun agent n'a contestée, et la
  mesure de 18 ms, contrôlée seulement en passant.

## → Ce que ça change
- **Les axes 2 et 5 attendent** que les défauts bloquants 1 à 4 soient
  corrigés. Ils seraient construits sur un contrat qui accepte en silence
  des modules ignorés, des clés fausses et des flux mal câblés.
- **Les critères d'acceptation de l'axe 0 sont à réécrire** pour pouvoir
  échouer :
  - plug-in testé par `twin_of` ;
  - levier quotas comparé à la v1 ;
  - agrégation comparée au RPPS ;
  - conservation démographique (une contrainte qui ne fait que déplacer des
    flux laisse le total inchangé).
- **L'axe 3** gagne un cas d'école : un test qui passe par construction.

## ? Pour la suite
| Point | Coût |
|---|---|
| Corriger les défauts 1 à 4 et réécrire les critères (session de l'axe 0) | ~1–2 h, temps Claude |
| Vérifier les 3 constats non soumis à réfutation | ~10 min (workflow, 3 agents) |
| Relancer cette revue après les corrections | ~3 min machine, 9 agents |
