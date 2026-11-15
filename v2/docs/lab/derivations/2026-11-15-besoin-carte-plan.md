---
date: 2026-11-15
type: plan
status: plan, accord attendu — rien n'est branché
author: session besoin-axe0-interface
---

# Besoin → carte : vue « couverture » et levier L23 de bout en bout (plan)

**Portée en une ligne.** Brancher `besoin.sortie.besoin_api` dans `v2/prototype-carte/` : une vue « couverture »
(C indexé 2026) et le levier L23 (vaccination en officine), de l'API à l'assistant, avec l'affichage O2.
**Hors périmètre.** Nouveaux estimateurs (M1–M4 : plan par axes), commune en vue couverture tant que l'offre
communale ne passe pas le banc, MG ou spécialistes en sortie (O2), toute table ODbL dans la réponse servie en
attendant la décision de licence (seules des œuvres produites sortent, cf.
[brouillon licences](../reports/2026-11-15-licences-brouillon.md)).

**ETA (temps Claude, non calibré) : ~75 min (55–110)**, hors attente d'accord et hors machine (OSRM occupe la machine :
aucun calcul lourd ; la mesure de latence est légère, n = 30 requêtes locales).

## État de départ (lu dans le dépôt)

- `besoin_api(etat, estimateur="M0", transferts=(l23(),), ref=2026, level=…)` renvoie `besoin`, `couverture`,
  `couverture_base`, `transferts`, `hypotheses` (`v2/besoin/sortie.py`). Non branchée.
- Seul **M0** est construit (`v2/besoin/estimateurs/m0.py`) ; M1/M3/M4 promus par la dérivation, non construits.
- `l23()` (`v2/besoin/transferts.py`) : a, k, τ supposés ; s∞ et τ **mesurés** sur la série nationale par P-B6
  (s∞ 0,74, τ 2,4 ans) mais pas encore reportés dans `L23_PARAMS` (s_inf 0,6, τ 3,0 en placeholder) ; μ = 0
  (supposé, P-B6 non attribuable).
- La carte lit `/api/carte` (toutes les années en un appel, département) et la fiche (`exportCard`) ; l'assistant
  passe par `/api/interpret` et `/api/agent` (`_scenario_carte` compile les appels en leviers).

## Étapes

| # | Étape | Fichiers | ETA Claude |
|---|---|---|---|
| 0 | Reporter s∞ 0,74 et τ 2,4 (P-B6) dans `L23_PARAMS`, statut « mesuré (national) » ; a, k, μ restent « supposé » | `v2/besoin/transferts.py` | 5 min |
| 1 | `GET /api/couverture?prof=…&terr=…&leviers…&l23=0|1` : appelle `besoin_api` sur les états déjà calculés par `carte()` (aucun second passage du jumeau), renvoie C[terr][année] base et scénario, la fourchette, le bloc `transferts`, les `hypotheses`. Cache mémoire par (prof, leviers) | `v2/prototype-carte/server.py` | 20 min |
| 2 | Vue « couverture » : bouton dans `#var` à côté de effectif / densité ; échelle divergente centrée sur 1 (= 2026) ; légende « indice de couverture, base 2026 = 1 » | `index.html` | 15 min |
| 3 | Levier L23 : case dans la famille « transferts de tâches » ; `parse_levers` l'accepte (`l23=1`, `l23_a`, `l23_k` en mode expert, bornes des fiches d'hyperparamètres) | `server.py`, `v2/prototype/server.py` (parse), `index.html` | 10 min |
| 4 | Fiche et export : ligne « Indice de couverture 2035 / 2050 » (pharmaciens), ligne O2 « Actes de MG libérés : X ETP-équivalents (national) », paramètres avec statut ; l'export PNG/CSV reprend les mêmes lignes et la mention de source | `index.html` (`loadCard`, `exportCard`) | 10 min |
| 5 | Assistant : `_scenario_carte` reconnaît L23 (« pharmaciens vaccinent », « vaccination en officine ») et pose `l23=1` ; le chatbot reçoit `transferts` et `hypotheses` dans son contexte, jamais une couverture MG | `server.py`, `v2/langage/` (lexique d'intentions), `chatbot/` (gabarit) | 10 min |
| 6 | Tests et mesure : tests d'API (O2, bornes, forme), mesure de latence, passage du lexique | `v2/prototype-carte/tests/`, `v2/besoin/tests/` | 10 min |

## Fourchette entre estimateurs

- Aujourd'hui un seul estimateur (M0) : **pas de fourchette de modèle** ; la bande affichée est celle de l'offre
  (tirages du jumeau), étiquetée comme telle.
- Dès que ≥ 2 estimateurs survivent au backtest (M1/M3/M4 contre la référence naïve, plan par axes), l'API renvoie
  `couverture_min`, `couverture_max` sur les survivants et l'estimateur central. On l'affiche **si le choix du modèle
  pèse** : règle proposée, écart (max − min) / central > 5 % sur le territoire affiché en 2050 ; sinon une ligne
  « les estimateurs concordent à ± x % ». Seuil de 5 % : supposé, à confirmer (≈ 5 min de décision).
- Aucun chiffre unique présenté comme « la » couverture : la fiche nomme l'estimateur et sa norme.

## Affichage O2

- Les professions de `SANS_COUVERTURE` (MG, spécialistes) **n'ont jamais de vue couverture** : le bouton est grisé si
  la profession choisie n'est pas une des cinq sorties ; l'API renvoie 400 (`couverture.aligne` lève déjà).
- La MG n'apparaît que dans une ligne : « Actes de MG libérés par L23 : X ETP-équivalents, France entière » (et la
  part reçue par les pharmaciens). Pas de carte, pas d'indice, pas de « besoin MG couvert ».

## Critères d'acceptation (vérifiables)

1. **Latence** : `/api/couverture` < 150 ms au 95ᵉ centile, n ≥ 30 requêtes, département, leviers variés, cache
   froid exclu et déclaré ; mesuré par un script commité, résultat dans le rapport (mesuré, pas estimé).
2. **Bout en bout L23** : `l23=1` change C des pharmaciens dans l'API, la carte, la fiche, l'export et la réponse
   de l'assistant, et ces cinq valeurs sont identiques à 1e-9 près (test automatique sur un département).
3. **Neutre à L23=0** : C scénario = C base quand aucun levier ni L23 (écart ≤ 1e-12) ; C = 1 partout en 2026.
4. **O2** : test qui demande `prof=medecine-generale` et `prof=specialistes` → 400 ; aucune chaîne « couverture »
   associée à MG dans le HTML rendu ni dans la réponse de l'agent (recherche textuelle).
5. **Statut des paramètres** : chaque nombre de L23 affiché porte son statut (mesuré / supposé) et sa source.
6. **Lexique neutre** : tous les nouveaux libellés passent `_lexique()` / `v2/docs/lab/lexicon.md` (zéro terme
   interdit : « désert », « pénurie critique », « médiocre » …) ; formulations type « couverture moindre qu'en
   2026 », « couverture supérieure à 2026 ».
7. **Licence** : aucune valeur issue d'une table ODbL n'est servie tant que la décision est ouverte (M0 n'en lit
   pas ; à revérifier pour M3/M4).

## Ce qui pourrait rendre ce plan faux

- Le jumeau ne renvoie pas les `State` par année depuis `carte()` : il faudrait un second passage → latence à
  remesurer (risque sur le critère 1).
- a et k de L23 sont des placeholders : l'effet affiché est illustratif ; la fiche doit le dire.

## Décisions demandées

- Accord pour brancher (ce plan) ; seuil de 5 % pour montrer la fourchette de modèle.
