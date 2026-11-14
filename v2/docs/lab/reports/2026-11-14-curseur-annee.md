---
type: analysis
date: 2026-11-14
author: équipe
question: La carte peut-elle montrer chaque année de 2026 à 2050, et non seulement 2050 ?
headline: Curseur 2026 → 2050 sans recalcul au déplacement ; /api/carte ≈ 100 ms pour 25 années, 78 ko ; 2050 inchangé
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis:
sources: [DREES RPPS 2012-2026, Insee Omphale 2022]
tags: [carte, interface]
---

# Curseur d'année sur la carte

> **Headline:** toutes les années 2026 → 2050 en un appel (~100 ms, 78 ko) ; bouger le curseur ne relance pas le jumeau ; 2050 identique à avant.

## Question
Lire la projection à 2030, 2035, 2045… sur la carte. Décision : [curseur d'année](../decisions.md).

## Result
| Contrôle | Résultat |
|---|---|
| `/api/carte` kinés / infirmiers, toutes années | 106 ms / 98 ms, 78 ko |
| France, kinés, tendance | 2030 : 114 711 · 2035 : 129 244 · 2050 : 160 783 |
| Puy-de-Dôme, kinés, 2050 | 1 731 (identique avant/après) |
| Places +20 %, kinés (délai 5 ans) | effet 0 jusqu'en 2031, +1 088 en 2032, +4 351 en 2035, +20 665 en 2050 |
| Fourchette Puy-de-Dôme | 2030 : 1 169–1 284 · 2035 : 1 249–1 544 · 2050 : 1 244–2 219 |
| Lien `#…&y=2035` rechargé | curseur à 2035 |
| Outil agent `carte(annee=2035)` | France 129 244 (= carte) ; 2051 refusé « pas dans le modèle » |

## How
- **Data:** aucune nouvelle ; trajectoires du jumeau v2 déjà annuelles.
- **Method:** `carte()` (`v2/prototype-carte/server.py`) boucle sur les années ; le front lit la valeur à l'année du curseur (`derive`, `setYear` dans `index.html`).

## ⚑ What could make it wrong
- Le curseur peut donner l'impression que chaque année est aussi fiable : la fourchette s'élargit avec l'horizon et reste affichée.
- Vérifié sans rendu WebGL (panneau du navigateur masqué) : la coloration elle-même n'a pas été vue à l'écran.

## → What it changes
- Démo : « combien de kinés en 2035 » se lit directement sur la carte et dans la fiche.

## ? Next
| Item | Cost |
|---|---|
| UAT du curseur avec un·e élu·e (lecture des années proches vs lointaines) | 30 min |
