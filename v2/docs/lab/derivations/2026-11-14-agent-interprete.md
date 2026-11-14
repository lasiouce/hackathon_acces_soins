---
date: 2026-11-14
statut: plan, construit le même jour (voir decisions.md)
headline: "Un agent à outils explique les sorties du jumeau ; il ne calcule rien, et chaque nombre de sa réponse est vérifié contre les sorties d'outils"
---

# Agent qui interprète les résultats du jumeau : plan

**ETA (temps Claude) :** ~60 min (40–100), fin ≈ 14:40, hors attente de la clé d'API et hors temps machine de
l'évaluation (~20 questions × ~30 s ≈ 10 min). Facteur de correction de `eta.py stats` : ×1,7 à ×6 sur des *runs* ;
aucun historique pour ce genre de travail, donc **non calibré**.

**Portée en une ligne :** un·e utilisateur·rice non technique pose une question en français dans la carte ; l'agent
appelle les endpoints du serveur de la carte et explique la réponse (écart par flux, délai, fourchette, statut des
leviers, limites), sans produire lui-même un seul nombre.

## Contrainte, en unités
- **Ancrage :** 100 % des nombres d'une réponse se retrouvent, arrondi compris, dans les sorties d'outils de la
  conversation (ou la question). Mesuré par réponse et par nombre.
- **Lexique :** 0 terme de jugement du lexique (`lexicon.md`) par réponse. Mesuré.
- **Latence :** < 30 s par question (au-delà, l'élu·e décroche ; la carte reste utilisable pendant l'attente).
- **Coût :** < 0,20 $ par question (Opus 5.5 : 4 $ / 20 $ par million de jetons ; ~30 k jetons d'entrée en 3 tours
  d'outils + 1 k en sortie ≈ 0,14 $, **dérivé**, à mesurer).

## Alternative la moins chère, dérivée avant de relire l'existant
**Gabarit déterministe** : le résumé de la carte (`levState`) écrit déjà « 2050 : +N par rapport à la tendance, entre A et
B ». On pourrait l'étendre en phrases à trous : écart par flux, délai, statut. Coût nul, ancrage 100 % par construction.
Ce qu'il ne sait pas faire : **répondre à une question libre** (« pourquoi l'effet ne se voit qu'en 2032 ? », « qu'est-ce
qui est supposé là-dedans ? », « et pour les infirmiers ? »), choisir les bons chiffres, dire « pas dans le modèle » sur
une question hors périmètre. C'est précisément la demande.

**Verdict.** L'agent est retenu, **avec le gabarit comme sol** : les outils renvoient des digests déjà arrondis et déjà
dérivés (écart, écart en %, évolution depuis l'origine, fourchette), écrits par du code déterministe. Le modèle ne fait que
choisir et expliquer. Un test d'ancrage automatique vérifie chaque réponse ; une réponse non ancrée est signalée dans
le panneau (pas masquée).

**Ce qui prouverait que c'est faux :** taux d'ancrage < 90 % des réponses sur le jeu de 20 questions malgré les digests
(le modèle calcule quand même) → repli sur le gabarit déterministe pour les chiffres, le modèle n'écrivant que le texte.

## Forme
- `v2/agent/outils.py` : 5 outils, appels HTTP au serveur de la carte (port 8767) : `meta`, `territoire` (nom → code),
  `scenario`, `carte`, `interpreter`. Chaque sortie est un digest arrondi : pas de liste de 25 années × 12 décimales.
- `v2/agent/agent.py` : boucle d'outils manuelle (SDK `anthropic`), modèle `claude-opus-5-5` par défaut
  (`AGENT_MODEL`), effort `medium` (`AGENT_EFFORT`). Clé lue dans `ANTHROPIC_API_KEY`, jamais écrite.
- `v2/agent/garde_fous.py` : ancrage (nombres de la réponse ⊂ nombres des sorties d'outils et de la question, à la
  précision affichée) et lexique (termes interdits de `lexicon.md`).
- `v2/agent/questions.yaml` : 22 questions écrites **avant le code** ; `v2/agent/evaluer.py` mesure les taux.
- Carte : `POST /api/agent` (le serveur garde la clé), `GET /api/agent/etat` ; panneau « Questions » dans `index.html`.

## Hors périmètre
Pas de calcul par le modèle ; pas de réglage automatique des leviers de la carte par l'agent (il peut proposer, la
phrase existante garde son écran de confirmation) ; pas de mémoire entre sessions ; pas de module de besoin.

## Critères d'acceptation
1. « Combien de kinés en Auvergne-Rhône-Alpes en 2035 si on forme 20 % de plus, et pourquoi ? » : chiffres tous ancrés,
   décomposition par flux (entrées, sorties), délai d'effet, fourchette.
2. Taux d'ancrage et de lexique mesurés sur ≥ 20 questions, consignés dans `v2/agent/score.txt` et `decisions.md`.
3. Sans clé : la carte fonctionne, le panneau dit pourquoi l'agent est indisponible.
4. La clé n'apparaît dans aucun fichier du dépôt, aucun log, aucune réponse HTTP.
