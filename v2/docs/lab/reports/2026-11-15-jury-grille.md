---
type: analysis
date: 2026-11-15
author: recette jury (agents)
question: Quelle note le projet obtiendrait-il selon la grille du jury, et quelles corrections rapportent le plus de points par heure ?
headline: "64/100 (fourchette 54–74) : pertinence 6,5, IA 7,0, prototype 6,5, faisabilité 5,5, pitch 6,5 ; la note de conformité (RGPD, AIPD, 2017/745) rapporte le plus de points, ~3 pts pour 45 min"
status: draft
professions: [sages-femmes, dentistes, pharmaciens, kines]
hypothesis: Le projet satisfait la grille du jury (pertinence 25, IA 20, prototype 20, faisabilité 20, pitch 15)
sources: [README.md, v2/, v2/prototype-carte/, v2/video/out/]
tags: [jury, recette, evaluation]
---

# Évaluation selon la grille du jury

> **Headline :** 64/100, fourchette 54 à 74. Le jumeau est réel, mesuré et honnête. Les points perdus viennent surtout de la faisabilité réglementaire (aucune note RGPD ou dispositif médical, aucune licence) et du pitch (deck désaligné du README).

## Question
Quelle note le projet obtiendrait-il selon la grille du jury, et quelles corrections rapportent le plus de points par heure de temps Claude ?

## How
- **Méthode :** 5 jurés simulés, un par critère : décideur d'ARS, spécialiste ML/IA, ingénieur produit, juriste RGPD avec un spécialiste des données de santé, coach de pitch. Chaque note est revérifiée par 2 vérificateurs adverses, l'un qui cherche une note trop généreuse, l'autre une note trop sévère. Note retenue = médiane des trois.
- **Banc :** main au commit 82780ea (8d8df4a après merge). Instance dédiée de la carte sur le port 8794, Chrome for Testing en headless. Le port 8767 n'a pas été touché.
- **Sorties brutes :** dans `/private/tmp/claude-501/jury/`, hors dépôt. Captures dans [`figures/jury/`](../figures/jury/).

## ⚑ What could make it wrong
- Les notes sont des **estimations** d'agents, appuyées sur des preuves. Seules les mesures (latences, recette 35/37, compilateur 21/30) sont mesurées.
- La première passe de `recette.mjs` s'est figée sur `map.once('idle')` et a été arrêtée à la main. Le résultat 35/37 vient d'une relance.
- Un vrai jury pondère à l'oral. La note du pitch dépend de la présentation en direct.


**Headline : 64/100 (fourchette 54 à 74).** Le jumeau est réel, mesuré et honnête. La note baisse surtout pour trois raisons : rien n'est écrit sur la réglementation, le deck contredit le README, et l'exemple phare du sujet (la vaccination en officine) ne change aucun chiffre.

### 1. Notes par critère

| Critère | Poids | Juré | Vérif. 1 | Vérif. 2 | Retenue /10 | Fourchette /10 | Points /100 (bas–haut) |
|---|---|---|---|---|---|---|---|
| Pertinence et impact | 25 | 6,5 | 6,0 | 6,9 | **6,5** | 5,5–7,5 | **16,25** (13,75–18,75) |
| Innovation et IA | 20 | 7,0 | 6,5 | 7,5 | **7,0** | 6,0–8,0 | **14,0** (12,0–16,0) |
| Qualité du prototype | 20 | 6,5 | 6,0 | 6,8 | **6,5** | 5,5–7,5 | **13,0** (11,0–15,0) |
| Faisabilité (RGPD, réglementaire) | 20 | 5,5 | 5,0 | 5,75 | **5,5** | 4,5–6,5 | **11,0** (9,0–13,0) |
| Pitch | 15 | 6,5 | 6,0 | 6,8 | **6,5** | 5,5–7,5 | **9,75** (8,25–11,25) |

Pour la note retenue, j'ai pris la médiane des trois notes, arrondie à 0,5. Pour la fourchette, j'ai pris la médiane des trois bornes basses et celle des trois bornes hautes, arrondies à 0,5.

### 2. Score pondéré

**64,0 / 100**, fourchette **54,0 à 74,0**. Le calcul est dérivé des notes ci-dessus. Les notes elles-mêmes sont des estimations des jurés, appuyées sur des preuves.

### 3. Détail par critère

#### Pertinence et impact (×25) : 6,5

**Preuves clés**
- L'API répond à la question du sujet (/api/interpret puis /api/scenario, pharmaciens, D63) : 738 en 2026 et 781 en 2035. C'est mesuré, dans /private/tmp/claude-501/jury/pertinence/interpret.json.
- La vaccination en officine est classée « non modélisé », avec la raison expliquée.
- Le backtest bat les références naïves. La MAPE de C1 est de 7,73 %, contre 8,68 % pour A0, 9,30 % pour la tendance et 9,92 % pour la persistance. L'IC du delta est [-1,51 ; -0,47]. C'est sourcé dans v2/docs/lab/reports/2026-11-14-axe2-cohortes-bayesiennes.md (l.40-45), sans relance.
- La reproduction de DD76 échoue partout. L'écart à 2050 est de -14,07 % pour les dentistes, -15,02 % pour les pharmaciens et -17,39 % pour les sages-femmes, et de -25,2 % pour ER1319. C'est mesuré dans v2/validation/out/dd76_results.json. Le README n'en parle pas : grep ne renvoie rien.

**Forces**
- Le besoin est posé du point de vue du décideur (README l.80-82).
- Un levier hors modèle est nommé comme tel au lieu d'être inventé.
- Le backtest est pré-enregistré.
- Le lexique est neutre : 0 terme interdit dans index.html.

**Faiblesses**
- L'exemple phare (la vaccination) n'a aucun effet chiffré.
- La pharmacie nationale évolue en sens inverse de DD76 : ratio 2050/2020 de 0,949 contre 1,117.
- La bande à 80 % ne couvre que 73,5 %, et le CRPS est à égalité avec la référence naïve. L'argument d'incertitude n'est donc pas démontré.
- L'affichage s'arrête au département (README l.178).

**Réfuté par les vérificateurs**
- Le « lien profond cassé » n'en est pas un. La carte lit le fragment #p=…&t=…&y=… (index.html l.521-526), pas les paramètres ?query.
- « 1 levier sourcé sur 9 » est faux : /api/meta donne 2 leviers sourcés sur 11 (regul et pop_scen).
- L'échec DD76 était prévu par un protocole qui interdit le réglage (axe3-n2, l.41-70). C'est de la rigueur. Le seul défaut est de ne pas l'avoir publié.

#### Innovation et IA (×20) : 7,0

**Preuves clés**
- L'agent (v2/agent/agent.py) ne calcule rien lui-même : tous les nombres passent par outils.py.
- Les 5 réponses sur 5 testées correspondent à l'API (r1 à r5, api_verif.txt).
- Le coût est de 0,035 à 0,05 $ et la latence de 7 à 10 s par réponse (mesuré).
- Compilateur, jeu 6 à l'aveugle : 21/30 = 70 %, relancé deux fois.
- Le jeu 5 donne aujourd'hui 30/30. Il est contaminé, donc le chiffre de 77 % est historique.
- score_chatbot.txt : 311/313 nombres ancrés, 9 réponses corrigées sur 22, 0 bloquée, et 13/22 réponses relayées vers la carte (sourcé).

**Forces**
- L'ancrage et le lexique sont vérifiés par du code, avec une boucle de correction.
- Les pièges et les fausses prémisses sont bien gérés : -60 % est rejeté, le chiffre mesuré est -14,4 %.
- Le protocole à l'aveugle est honnête.

**Faiblesses**
- Le compilateur est à base de règles et plafonne autour de 70 % ; il réussit 2 pièges sur 4.
- Le garde-fou signale « 100 000 » comme non ancré, ce qui crée des faux positifs.
- L'agent combine outils et LLM de façon standard.
- Aucun jeu neuf n'est prévu pour évaluer la future étape LLM.
- evaluer_hors_echantillon.py plante s'il est lancé depuis v2/langage (FileNotFoundError).

**Réfuté par les vérificateurs**
- Aucune preuve centrale n'est réfutée.
- Le juré compte les cohortes bayésiennes parmi les originalités IA tout en les jugeant classiques. Ce n'est pas cohérent : elles relèvent des statistiques, pas du critère IA.

#### Qualité du prototype (×20) : 6,5

**Preuves clés**
- recette.mjs passe 35 contrôles sur 37 (/private/tmp/claude-501/jury/proto/recette3.txt). R25 (bouton A+) et R37 (107 % contre 36,6 %) échouent.
- jumeau.check affiche « échecs : aucun » avec EXIT 0. C15 donne 1,31 s pour 5 professions à la commune (check.txt).
- Un clone neuf sans data/raw démarre, et /geo renvoie 639 007 B.
- La latence de /api/carte est d'environ 55 ms selon la relance des vérificateurs, et non de 127 à 152 ms.

**Forces**
- Une carte DSFR complète : onglets, export CSV, leviers avec délai, statut et source (carte-ordinateur.png).
- Un moteur auto-vérifié qui garde la trace de ses régressions.

**Faiblesses**
- À 390 px, la page déborde et la carte reste vide (mobile.png).
- La capture mobile de recette.mjs bloque sur map.once('idle'), sans timeout (l.430-433).
- numerus=abc est accepté en silence.
- La carte reste vide plusieurs secondes au premier chargement.
- check.txt se contredit : 1,31 s pour C15, mais environ 3,6 s extrapolées sur la ligne T.
- Il n'y a pas de tests pytest.

**Réfuté par les vérificateurs**
- « terr=ZZZZ renvoie la France » est faux. terr n'a aucun effet sur /api/carte, quel que soit le code. Le paramètre est mort, mais aucun chiffre faux n'est montré.
- La latence de 127 à 152 ms ne se reproduit pas.

#### Faisabilité (×20) : 5,5

**Preuves clés**
- manifest --check renvoie OK : uniquement des données ouvertes. L'historique git est propre.
- open.md l.82 (seuil statistique) et l.84 (AIPD) sont toujours « open ».
- grep sur « 2017/745 » et « dispositif médical » donne 0 occurrence.
- Il n'y a pas de fichier LICENSE.
- Les CGU du DSFR le réservent à l'administration (dsfr/LICENSE.md l.1).
- L'agent appelle l'API Anthropic avec un en-tête bêta (agent.py l.92-95).
- Une seule condition de signature sur 8 est remplie (rapport produit).

**Forces**
- Les données ouvertes sont vérifiées par un contrôle automatique.
- Chaque paramètre a une fiche avec sa source et son millésime ; 469 citations ont été auditées.
- Le modèle de commun EUPL avec prestations aux ARS est crédible.
- Les manques ont un prix dans le ledger.

**Faiblesses**
- Il n'y a ni AIPD ni note de non-applicabilité.
- Rien ne place l'outil hors du règlement sur les dispositifs médicaux.
- Le code n'a pas de licence.
- Le DSFR et la Marianne sont utilisés hors .gouv.fr.
- L'assistant dépend d'un tiers américain, sans analyse de transfert.
- Il n'y a ni porteur ni ARS pilote.
- Les données communales existent en double (chatbot/vendor).

**Réfuté par les vérificateurs**
- L'échec sur le secret statistique est surpondéré. petits_effectifs.parquet ne contient ni âge ni sexe, seulement des effectifs CartoSanté déjà publics.
- Le raisonnement RGPD et la souveraineté sont bien écrits, en quelques lignes, dans le rapport produit (l.102-106).

#### Pitch (×15) : 6,5

**Preuves clés**
- pitch-v2.mp4 dure 60,0 s en 1920×1080 (mesuré avec cv2). Les planches sont dans v2/docs/lab/figures/jury/pitch/.
- Le deck v2/docs/lab/presentations/2026-11-14-pitch.md fait 90 lignes et le README 308 (wc).
- Le chiffre +19 110 kinés (+11,9 %) est le même dans la vidéo et dans le deck.
- La démo sur 8794 répond 200 en 0,003 à 0,006 s.

**Forces**
- Un seul fil narratif : un levier, un département, trois horizons.
- L'incertitude est toujours visible.
- Le deck ouvre sur un constat chiffré, environ 80 000 infirmiers manquants selon ER1319 (l.12-16), et chaque section est minutée.

**Faiblesses**
- Aucune vidéo ne pose le problème.
- Le deck contredit le README. Il dit « seul le levier quotas est citable » (l.69) et donne un Δ MAPE de -0,11 pt, alors que les écarts réels sont de -0,95 pt et -1,57 pt.
- La réponse dure n°1 dit la régulation « bloquée », alors que c'est un levier actif.
- Le deck se termine sur une diapo interne, « Decisions needed ».
- Le deck promet la commune.

**Réfuté par les vérificateurs**
- « Le problème n'est pas posé » ne vaut que pour les vidéos. Le deck et le README (l.76-82, à un clic depuis le sommaire) le posent.
- Deux numéros de ligne du juré étaient décalés.

### 4. Corrections dédoublonnées, classées par points sur 100 par heure Claude

| Rang | Correction | Critère | Gain /100 | Coût (h Claude) | Ratio (pts/h) |
|---|---|---|---|---|---|
| 1 | Retirer la diapo « Decisions needed » du deck | Pitch | 0,30 | 0,05 | 6,0 |
| 2 | Note de conformité : hors article 9 du RGPD, non-applicabilité de l'AIPD à faire valider par un DPO, hors règlement 2017/745 | Faisabilité | 3,00 | 0,75 | 4,0 |
| 3 | Fichiers LICENSE (EUPL-1.2) et NOTICE des licences tierces | Faisabilité | 1,00 | 0,25 | 4,0 |
| 4 | Mettre le deck à jour : Δ de -0,95 et -1,57 pt, statut des 11 leviers, réponses dures n°1 et n°2 | Pitch | 1,05 | 0,30 | 3,5 |
| 5 | Note sur l'assistant IA : données envoyées, mode sans clé, piste d'hébergement UE ou SecNumCloud | Faisabilité | 1,50 | 0,50 | 3,0 |
| 6 | Seuil n<11 dans l'API et les exports, sur les deux copies (v2 et chatbot/vendor), avec un test | Faisabilité | 2,00 | 0,75 | 2,7 |
| 7 | Publier l'écart à DD76 et ER1319 dans le README et sur la fiche : périmètre, et inversion de tendance en pharmacie | Pertinence | 1,25 | 0,50 | 2,5 |
| 8 | Résumé de 10 lignes en tête du README : enjeu chiffré, capture, lien vidéo | Pitch | 0,75 | 0,30 | 2,5 |
| 9 | Carton problème et carton demande dans la vidéo V2 | Pitch | 1,20 | 0,50 | 2,4 |
| 10 | Nouveau jeu 7 à l'aveugle et recalcul du chiffre cité | IA | 1,00 | 0,50 | 2,0 |
| 11 | Liste blanche des constantes d'unité (100 000) dans le garde-fou d'ancrage | IA | 0,60 | 0,30 | 2,0 |
| 12 | Valider ou supprimer terr, et rejeter les leviers non numériques | Prototype | 0,60 | 0,30 | 2,0 |
| 13 | Passer de 3 à 15 questions dures dans le deck | Pitch | 0,75 | 0,40 | 1,9 |
| 14 | Documenter le format du lien (#) et lire aussi ?query, avec un scénario « Clermont 2035 » prêt | Pertinence | 0,50 | 0,30 | 1,7 |
| 15 | Corriger le taux de 107 % pour faire passer R37, et retirer ou réimplémenter R25 | Prototype et pertinence | 1,50 | 1,00 | 1,5 |
| 16 | Masquer 2050 pour les professions hors tolérance N2 (vérifier d'abord la règle) | Pertinence | 0,75 | 0,50 | 1,5 |
| 17 | Persona nommé avec une décision réelle (un DG d'ARS et l'ouverture d'un IFMK) | Pitch | 0,45 | 0,30 | 1,5 |
| 18 | Repli LLM à sortie JSON contrainte pour le compilateur, mesuré sur le jeu 7 | IA | 2,00 | 1,50 | 1,3 |
| 19 | Corriger la mise en page mobile et ajouter un timeout sur idle dans recette.mjs | Prototype | 2,00 | 1,50 | 1,3 |
| 20 | Relancer evaluer_chatbot avec au moins 10 pièges et une matrice de confusion | IA | 0,60 | 0,50 | 1,2 |
| 21 | Précalculer le scénario national pour éviter la carte vide au premier chargement | Prototype | 0,80 | 0,70 | 1,1 |
| 22 | Aligner l'affichage des lignes C15 et T de check.txt | Prototype | 0,40 | 0,35 | 1,1 |
| 23 | Mode « hors État » : retirer Marianne et le bloc-marque hors .gouv.fr | Faisabilité | 1,00 | 1,00 | 1,0 |
| 24 | Deux ou trois leviers de plus rattachés à une élasticité publiée | Pertinence | 1,75 | 2,00 | 0,9 |
| 25 | Petit pytest sur les cas limites de l'API, et sortie au fil de l'eau dans recette.mjs | Prototype | 0,60 | 0,70 | 0,9 |
| 26 | Indicateur de besoin (densité pour les 75 ans et plus, Insee) pour donner un effet aux transferts de tâches | Pertinence | 2,50 | 3,00 | 0,8 |
| 27 | Script de reconstruction de bout en bout avec empreintes de contrôle | Faisabilité | 1,00 | 1,50 | 0,7 |

Pour les corrections notées différemment par le juré et ses vérificateurs, j'ai pris la valeur médiane ou celle du vérificateur. Les gains sont estimés et ne s'additionnent pas toujours, puisqu'une note est plafonnée à 10. Les rangs 1 à 9 coûtent environ 3,9 h Claude pour un gain d'environ 12 points sur 100 (estimé).

### 5. Les 15 questions dures

| # | Question | Réponse que permet le dépôt | État |
|---|---|---|---|
| 1 | Faites-vous mieux qu'une extrapolation ? | Oui, de peu : une MAPE de 7,73 % contre 9,30 % pour la tendance et 8,68 % pour le stock-flux (README l.207). L'apport, c'est le scénario. Le deck donne encore un Δ faux de -0,11 pt. | Répondue, deck à corriger |
| 2 | Comment validez-vous à 2050 ? | On ne peut pas valider directement. On s'appuie sur la reproduction de DD76, qui échoue mais selon un protocole pré-enregistré, et sur des fourchettes marquées « extrapolée » (README l.211-213). | Partielle |
| 3 | Le sujet demande la commune. | Les modèles K3 à K5 ont échoué à la validation, donc l'affichage s'arrête au département (README l.178 et 289). | Partielle |
| 4 | Votre « libéral » est-il comparable à ameli ou au RPPS ? | Non : il couvre tout le secteur privé (README l.86-90). | Répondue |
| 5 | Comment séparez-vous public et privé ? | Par estimation, avec une fourchette (sages-femmes 2026 : 12 059 à 14 660). | Répondue |
| 6 | D'où vient +19 110 ? | De kines_quotas120.json, décomposé par flux (deck l.30). | Répondue |
| 7 | Quels leviers sont fiables ? | Le deck dit le levier quotas seul ; l'API compte 2 leviers sourcés sur 11. | **Sans réponse cohérente** |
| 8 | Qui l'utilise et qui paie ? | Un commun EUPL, puis des prestations aux ARS sous 60 k€. Aucun client n'a été interrogé. | **Sans preuve** |
| 9 | Qui maintient l'outil en 2027 ? | Personne pour l'instant : c'est la demande du pitch. | **Sans réponse** |
| 10 | En quoi êtes-vous différents de CartoSanté ou de la DREES ? | Eux décrivent le présent ou projettent au niveau national ; l'outil simule une politique par territoire (deck l.19-23). | Répondue |
| 11 | L'IA invente-t-elle des chiffres ? | Non : 311/313 nombres ancrés, et 5 réponses sur 5 vérifiées contre l'API. | Répondue |
| 12 | La phrase en langage naturel est-elle fiable ? | 70 % de phrases bien traduites sur le seul jeu encore à l'aveugle (77 % historique), avec confirmation avant toute application. | Répondue, chiffre à rectifier |
| 13 | Et le secret statistique sur les petites communes ? | Le seuil n'est pas appliqué. Les fichiers ne contiennent que des effectifs déjà publics, sans âge ni sexe. | **Sans réponse dans l'outil** |
| 14 | Quel est l'effet de la régulation de l'installation ? | Elle est modélisée par géocodes, mais son effet n'est pas validé par backtest. | Partielle |
| 15 | Où est la demande de soins, pas seulement l'offre ? | Seulement une densité Omphale et le levier pop_scen ; il n'y a pas de modèle de besoin. | **Sans réponse** |

Restent sans réponse les questions 7, 8, 9, 13 et 15. Les questions 2, 3 et 14 n'ont qu'une réponse partielle.

### 6. Tests non faits ou impossibles

- **Backtests MAPE et CRPS** : pas relancés, les chiffres sont sourcés dans les rapports.
- **Reconstruction complète depuis le manifest** : pas relancée.
- **Capture mobile de la recette** : impossible, elle bloque sur idle (deux exécutions tuées après plus de 500 s).
- **Fond de carte en headless** : vide.
- **Images des MP4 avec le ffmpeg de Playwright** : impossible, le décodeur H.264 manque. J'ai contourné avec cv2.
- **Voix off de la V1 et répétition chronométrée du pitch** : non vérifiées. Les 3 minutes sont déclarées, pas mesurées.
- **evaluer_chatbot.py et score_objectifs** : pas relancés, scores lus seulement.
- **Agent** : pas relancé par les vérificateurs, seulement relu.
- **Masquage de 2050 pour les professions hors tolérance N2** : non vérifié.
- **Projection communale** : non testable, elle n'est pas servie.
- **Licences des dépendances dans chatbot/vendor** : non auditées.

**64/100 (54 à 74).** Le prototype est solide et honnête. Il perd ses points sur la réglementation, qui n'est pas écrite, sur un pitch désynchronisé du dépôt et sur une question phare sans effet chiffré. Les rangs 1 à 9 rapporteraient environ +12 points en moins de 4 h Claude (estimé).

## → What it changes
- La session v2 dispose d'une liste de corrections classée par points/heure (section 4). Les trois premières tiennent en environ 1 h de temps Claude, pour environ 4,3 points.

## ? Next
| Item | Cost |
|---|---|
| Rejouer la recette après les corrections du top 5 pour mesurer le gain réel | ~30 min machine |
| Recette mobile : corriger le blocage de recette.mjs sur `map.once('idle')` (pas de timeout) | ~20 min |
