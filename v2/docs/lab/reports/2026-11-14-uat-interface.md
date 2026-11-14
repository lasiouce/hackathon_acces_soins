---
type: analysis
date: 2026-11-14
author: Claude (session UAT)
question: Les personas cibles accomplissent-elles leur mission sur l'écran de décision, en V1 (8766) et en V2 carte (8767) ?
headline: "V1 : 11 tâches réussies sur 22 (6 échecs, dont l'effectif 2035 et l'export) ; 38 constats confirmés sur 40. V2 : verdict « à porter en démo », mais recette faussée par un onglet partagé (5 tâches sur 16) ; P1 = sélecteur d'horizon, libellés clairs, erreurs réseau"
status: draft
professions: [sages-femmes, dentistes, pharmaciens, kines]
hypothesis: L'interface répond aux 6 critères (écart, flux, délai, <100 ms, incertitude, fiche)
sources: [v2/prototype/, v2/prototype-carte/, docs/lab/lexicon.md]
tags: [uat, interface, prototype]
---

# Recette utilisateur (UAT) de l'écran de décision, V1 et V2 carte

> **Headline :** V1 : 11 tâches réussies sur 22 et 38 constats confirmés sur 40. Le choix de l'année hors 2050 et la fiche exportable échouent. La V2 carte corrige 7 constats V1 et en corrige 4 en partie. Elle est recommandée pour la démo, sous réserve des P1 : horizon, libellés clairs, gestion des erreurs réseau.

## Question
Les cinq personas peuvent-ils accomplir leur mission chronométrée sur le prototype ? Il s'agit de la DG d'ARS, de l'administration centrale (DGOS), d'un·e élu·e, d'un utilisateur mobile et d'un testeur adversarial. Quels constats résistent à une vérification adversariale ? Les critères d'interface (`v2/docs/lab/decisions.md`, section Open) sont repris dans les tableaux ci-dessous.

## How
- **Méthode :** deux workflows multi-agents. V1 : 5 personas, 40 constats, chacun revérifié par un agent qui tente de le réfuter (46 agents). V2 : la même chose, avec la liste des constats V1 en entrée (44 agents). Une synthèse classe ensuite les constats par score gravité × fréquence.
- **Temps :** les durées sont du temps-utilisateur **estimé** par les agents, pas mesuré. Seules les latences en ms sont mesurées.
- **Retours directs de l'utilisateur·rice (2026-11-14), sur la V2 carte :**
  - un meilleur zoom sur les régions et les départements, avec du détail fin dès les premières vues ;
  - des cases plus grandes ;
  - des limites de régions ARS mieux séparées : en vue France, on voit tout et c'est difficile de s'y retrouver ;
  - les DOM-TOM rapprochés en encarts.
  - couleurs : le blanc des départements à faible écart se confond avec le fond gris clair ; le milieu de l'échelle et les contours doivent rester visibles sur le fond.
  - clic sur une région : estomper les autres (désaturation, opacité ~0,3) plutôt que les flouter ;
  - encarts de données encore trop petits : fiche ~520 px, chiffres clés 32–36 px, aucun texte sous 14 px ;
  - fil d'Ariane France › région › département › commune pour remonter d'échelle ;
  - panneau Leviers cryptique et chargé : refonte proposée (familles en questions, 3 niveaux de détail, badges discrets, leviers indisponibles regroupés, résumé du scénario en tête), transmise à la session v2.
  Ces retours ont été transmis à la session proto-carte et sont classés **P1** pour la lisibilité de la carte.

## ⚑ What could make it wrong
- **Captures :** aucun fichier image n'a été écrit dans `figures/uat/`. Les captures du navigateur intégré restent dans le contexte des agents. Chaque constat décrit donc sa capture en texte (élément, texte visible). Il faut rejouer la recette avec un outil qui écrit sur disque.
- **Recette V2 faussée :** `tabs_create` a atteint son plafond, et les 5 personas ont partagé un seul onglet. Au moins 4 échecs viennent du protocole. Les latences d'environ 1 s ont été réfutées : c'est l'effet d'un onglet en arrière-plan.
- **V2 changeante :** la V2 était en développement pendant le test. Les constats valent pour son état à ce moment-là.
- **Durées et actions :** ce sont des estimations d'agents, pas de vrais utilisateurs.

## → What it changes
- Pour la session v2 / proto-carte : la liste P1 ci-dessous. Le prototype n'a pas été modifié.
- Pour la démo : porter la V2 sur un poste de bureau large, et dire à l'oral ce qui manque encore.

# Partie A : V1 (port 8766)

## Synthèse UAT : prototype de décision du jumeau (V1, http://localhost:8766)

Les durées sont estimées par les testeurs à la place d'un utilisateur. Elles n'ont pas été mesurées. Seules les latences de recalcul (en ms) ont été mesurées.

### 1. Persona × tâche

| Persona | Tâche | Réussite | Temps estimé (s) | Actions |
|---|---|---|---|---|
| DG ARS | Choisir kinés et zoomer jusqu'au Puy-de-Dôme | oui | 25 | 3 |
| DG ARS | Kinés en 2050, sur la tendance | oui | 15 | 0 |
| DG ARS | Kinés en 2035 | **non** | 90 | 5 |
| DG ARS | Effet de quotas à +20 % | oui | 30 | 2 |
| DG ARS | Zoomer jusqu'à la commune (Clermont-Ferrand) | **non** | 60 | 4 |
| DGOS | Comparer 3 scénarios pour les dentistes | partielle | 180 | 9 |
| DGOS | Vérifier les sources et les hypothèses | partielle | 90 | 3 |
| DGOS | Repérer les limites du modèle | oui | 60 | 2 |
| DGOS | Exporter une fiche | **non** | 60 | 3 |
| DGOS | Signalement des leviers suspendus | oui | 20 | 1 |
| Élu·e (Cantal) | Résumer la situation des sages-femmes en une phrase | partielle | 75 | 5 |
| Élu·e (Cantal) | Tester le levier formation | oui | 30 | 2 |
| Mobile (390×844) | Choisir pharmaciens puis Auvergne-Rhône-Alpes | oui | 25 | 4 |
| Mobile (390×844) | Effectif 2035 avec sa fourchette | **non** | 90 | 6 |
| Adversarial | Valeurs extrêmes dans le curseur | oui | 60 | 6 |
| Adversarial | Changements rapides (11 valeurs) | oui | 20 | 11 |
| Adversarial | Latence au regard du seuil de 100 ms | partielle | 30 | 8 |
| Adversarial | Coupure réseau simulée | **non** | 30 | 3 |
| Adversarial | Second onglet | partielle | 20 | 2 |
| Adversarial | Leviers suspendus | oui | 15 | 1 |
| Adversarial | Requêtes API invalides | partielle | — | 14 |
| Adversarial | Trouver une fiche exportable | **non** | 45 | 2 |

**Bilan :** 11 tâches réussies, 5 partielles, 6 échouées sur 22.

### 2. Constats confirmés, dédoublonnés, triés par gravité × fréquence

Les notes de gravité et de fréquence sont celles du vérificateur. Quand un constat apparaît chez plusieurs personas, on retient le score le plus haut.

| # | Score | Constat | Personas | Repro courte | Capture |
|---|---|---|---|---|---|
| 1 | 16 (g4×f4) | **Ni effectif ni fourchette pour une année autre que 2050.** Le titre et la fourchette sont écrits en dur sur 2050. | DG ARS, mobile, DG ARS (fourchette) | Choisir un territoire puis cliquer sur la courbe vers 2035. | Le titre reste « … en 2050 : ≈ 1 731 ». Seul « D'où vient l'écart en 2037 » change. Dans le code, `render()` utilise `d.base[last]` et le gestionnaire `#hit.onclick` n'appelle pas `render()`. |
| 2 | 12 | **Aucune fiche exportable.** Seule une règle `@media print` existe, et rien ne la signale. Elle masque d'ailleurs les leviers à l'impression. | les 5 | Chercher Exporter, PDF, CSV ou Imprimer sur la page. | Le seul bouton d'action est « Revenir à la tendance ». |
| 3 | 12 | **On ne peut pas comparer l'effet d'un levier à l'incertitude.** Seule la fourchette du scénario est donnée, celle de la tendance ne l'est pas, et aucun message n'indique « non distinguable ». | DG ARS, DGOS | Puy-de-Dôme, quotas à +20 %. | « +198 (+11,5 %) » à côté d'une fourchette 1 387 – 2 473 (±28 %), soit 198 face à environ 540 de demi-largeur. |
| 4 | 12 | **Les scénarios ne sont ni conservés ni partageables.** Aucune sauvegarde, aucune comparaison A/B, état absent de l'URL. | DGOS, adversarial | Dentistes à 0,7, puis à 1,5 : le premier résultat disparaît. Un second onglet repart de zéro. | Le titre est remplacé. L'URL reste `localhost:8766/`. |
| 5 | 12 | **Ni densité ni point de comparaison** (moyenne régionale ou nationale), alors que le lexique les demande. Le constat vaut aussi pour la V2 carte. | Élu·e | Sages-femmes, Cantal. | Seulement « ≈ 37 contre 16 », sans population dans les données. |
| 6 | 9 | **L'échelle communale n'existe pas, et l'interface ne le dit pas.** La limite n'est écrite que dans `server.py`. | DG ARS | Chercher Clermont-Ferrand dans le sélecteur de 121 options. | La matrice reste sur les 12 départements de la région. |
| 7 | 8 | **Libellés de départements faux** : D62 « Nord-Pas-de-Calais », « Côte-d Or », « Val-d Oise », « Côtes-d Armor », et une entrée D20 « Corse non précisé ». Ils viennent de `dep_name` dans `stock.parquet`. | DG ARS, DGOS, élu·e, adversarial | Appel `/api/meta` ou tableau au niveau France. | `{"id":"D62","name":"Nord-Pas-de-Calais"}` |
| 8 | 8 | **Source et millésime loin du chiffre** : le RPPS et CartoSanté ne sont cités qu'en pied de page. | DGOS | Lire `#sub`. | « Origine des données 2026 · décision 2026 · recalcul 67 ms » |
| 9 | 8 | **Le zonage de régulation ne dépend pas du territoire choisi.** La liste est nationale. | Élu·e | Sages-femmes, Cantal. | « 1 département(s) … (974) » s'affiche pour le Cantal. |
| 10 | 8 | **Le choix de l'année est peu visible.** La consigne « Cliquez » est placée sous la décomposition. Il n'y a ni étiquette au survol, ni graduation 2035, ni sélecteur exact. | Mobile, DG ARS (reste du constat réfuté) | Chercher comment changer d'année. | Petit texte gris sous les flux. |
| 11 | 8 | **Latence au-delà de 100 ms quand on enchaîne les changements.** Le coût vient du travail Python et du JSON de 44 Ko, pas du réseau. Le serveur sature quand les requêtes arrivent en même temps. | Adversarial | Changer le curseur 4 fois de suite. | Mesuré : 78, 130, 191 puis 314 ms. Changements espacés : 80–85 ms. Jumeau seul : environ 3 ms. |
| 12 | 6 | **Coupure réseau.** Le texte brut « Failed to fetch » remplace le titre, et des chiffres périmés restent affichés sans avertissement. | Adversarial | `window.fetch` qui rejette, puis curseur à +50 %. | `#headline` affiche « Failed to fetch ». L'écart total −4 777 correspond encore à −5 %. |
| 13 | 6 | **Aucun mode simple** pour l'élu·e. | Élu·e | Chercher une vue simplifiée. | Les leviers sont affichés d'emblée. |
| 14 | 6 | **Jargon non expliqué** : « flux du jumeau », « tendanciel », « origine », « décision », « recalcul N ms (jumeau N ms) ». | Élu·e | Lire les textes sous le graphique et sous le titre. | Aucune infobulle. |
| 15 | 6 | **Fourchette large sans explication à côté du chiffre.** La méthode n'est donnée qu'en pied de page, en jargon. | Élu·e | Sages-femmes, Cantal. | « 16 – 59 » autour de 37. |
| 16 | 6 | **« Plancher à zéro » n'est pas expliqué.** C'est un artefact de calcul présenté comme un flux. | DGOS | Dentistes, formation à 0,7. | « Plancher à zéro −24 » |
| 17 | 5 | **Les messages des leviers suspendus sont en jargon interne** (« faux », « défaut », « seconde revue du jumeau »). | Élu·e | Lire le panneau des leviers. | Texte sous « Âge » et sous « Installation régulée ». |
| 18 | 5 | **L'onglet actif par défaut est kinés**, alors que sages-femmes est le premier de la liste. Rien ne l'explique. | Élu·e | Ouvrir un onglet neuf. | `S.prof: 'kines'` |
| 19 | 4 | **La raison de l'onglet infirmiers inactif n'apparaît qu'au survol**, et contient « axe 4 ». | Adversarial | Cliquer sur Infirmiers. | La raison n'est que dans l'attribut `title`. |
| 20 | 3 | **Débordement horizontal sur mobile** : scrollWidth de 478 px pour un écran de 390 px. | Mobile | Écran 390×844. | La colonne `span.end` de la matrice dépasse à droite. |
| 21 | 3 | **Libellés du graphique illisibles sur mobile** (environ 5 px). | Mobile | Écran 390×844. | Le viewBox fait 720 et s'affiche sur environ 326 px. |
| 22 | 3 | **La somme des flux ne tombe pas juste**, alors que la page annonce « l'écart exact ». Chaque terme est arrondi séparément. | DG ARS | Puy-de-Dôme, +20 %. | −10 + 209 ≠ +198 |
| 23 | 2 | **Cibles tactiles sous 44 px.** Les lignes de la matrice font 20 px. | Mobile | Mesure des éléments à 390 px. | Onglets 35 px, curseurs 16 px, tris 27 px. |
| 24 | 2 | **Fil d'Ariane cassé et select qui touche le bord** sur mobile. | Mobile | Cantal à 390 px. | « Auvergne- / Rhône- / Alpes » sur plusieurs lignes. |
| 25 | 2 | **Accord grammatical** : « sages-femmes libéraux ». | Élu·e | Titre. | « libéraux » est écrit en dur. |
| 26 | 2 | **Un territoire inconnu renvoie le national avec un code 200.** Touche seulement l'API appelée directement. | Adversarial | `?terr=ZZZ` | Résultat identique à `terr=FR`. |
| 27 | 1 | **Erreur 500 avec le message de la ValueError** pour un paramètre non numérique. Touche seulement l'API. | Adversarial | `?quotas=abc` | `{"error":"ValueError: …"}` |

### 3. Constats réfutés

- **« Le clic sur le graphique tombe sur 2037 ou 2038 »** : réfuté. La conversion du clic est linéaire et un clic au milieu de 2030 et 2040 donne 2035. Il reste une remarque d'ergonomie (pas de retour au survol, graduations irrégulières), reprise au constat 10.
- **« L'état de l'onglet "seed" change sous l'utilisateur »** : c'est un artefact du protocole de test (onglet partagé entre testeurs), pas un défaut du produit.

### 4. Recommandations classées

**P1, avant la démonstration**
1. **Sélection de l'année.** `render()` doit être calculé sur l'année choisie (`S.year`) : titre, sous-titre, fourchette, et `h = S.year − origine`. Ajouter une étiquette « 2035 : ≈ N (a – b) » sur le curseur du graphique, un sélecteur d'année exact (curseur ou flèches) et des graduations tous les 5 ans. Corrige les constats 1 et 10.
2. **Export de fiche.** Ajouter un bouton « Exporter la fiche » avec deux sorties. La première appelle `window.print()`, avec un encart qui reprend les leviers, le territoire, la fourchette, la source et la date ; il ne faut plus masquer les hypothèses à l'impression. La seconde télécharge un CSV en reprenant `exportCard()` de la V2 carte, avec les bornes basse et haute et la décomposition par flux. Corrige le constat 2.
3. **Fourchette de la tendance et phrase de lecture.** Afficher la fourchette de la tendance à côté de celle du scénario. Ajouter une phrase neutre conditionnelle : « écart inférieur à la largeur de la fourchette : non distinguable à cet horizon ». Corrige les constats 3 et 15.
4. **Libellés des départements.** Les prendre dans le COG Insee, avec son millésime. Traiter D20 à part. Ajouter un test dans `check.py`. Corrige le constat 7.
5. **Mention de l'échelle la plus fine.** Afficher « Échelle la plus fine : département » et un lien vers la V2 carte. Corrige le constat 6.

**P2**

6. Inscrire l'état du scénario dans l'URL, ajouter « Garder ce scénario » et une comparaison de 3 scénarios au plus (constat 4).
7. Ajouter la population (Insee, Omphale), la densité pour 100 000 habitants et un point de référence régional et national (constat 5).
8. Citer la source et son millésime dans `#sub` (constat 8). Rendre le texte du zonage relatif au territoire choisi (constat 9).
9. Gérer la coupure réseau : message neutre, bouton « Réessayer », valeurs périmées grisées, `textContent` au lieu de `innerHTML` (constat 12).
10. Réduire la latence : ne recalculer qu'à la fin du geste ou après un délai d'environ 150 ms, mettre en cache côté serveur, alléger le JSON (constat 11).
11. Ajouter une vue simplifiée, un glossaire et reformuler le jargon : « tendanciel », « flux du jumeau », « Plancher à zéro » renommé en correction technique, messages des leviers suspendus et raison de l'onglet infirmiers rendue visible (constats 13, 14, 16, 17 et 19).

**P3**
12. Corriger l'affichage mobile : `overflow-x` sur la matrice, taille des textes du graphique, cibles de 44 px, fil d'Ariane (constats 20, 21, 23 et 24).
13. Faire tomber juste la somme des flux affichés, ou écrire « à l'arrondi près » (constat 22). Corriger l'accord « libérales » (constat 25). Aligner l'onglet par défaut sur l'ordre de la liste (constat 18).
14. Valider les entrées de l'API : erreur 400 pour un territoire inconnu ou un paramètre non numérique, et un champ indiquant le territoire réellement utilisé (constats 26 et 27).

### 5. Critères d'interface

| Critère | État | Remarque |
|---|---|---|
| Écart au tendanciel | **présent** | Valeur et pourcentage dans le titre, matrice par département. |
| Décomposition par flux | **présent** | Arrondi incohérent (constat 22), « Plancher à zéro » non expliqué (constat 16). |
| Délai d'effet | **présent** | Note « Premier effet … supposé » et repère « 1ers diplômés en plus » sur le graphique. |
| Réponse en moins de 100 ms | **partiel** | 80–85 ms mesurées avec des changements espacés, 130–314 ms en rafale. Jumeau seul : environ 3 ms. |
| Incertitude | **partiel** | Toujours tracée, mais chiffrée seulement en 2050 et pour le scénario seul. Pas de lecture de la significativité. |
| Fiche exportable | **absent** dans la V1 | Seulement une règle `@media print` non signalée. La V2 carte a un export CSV, d'après le code. |

### 6. Signalement des leviers retraite et régulation

**Clair sur le fond, pour les 5 personas.** La mention « Levier suspendu » est donnée avec sa cause, rappelée en pied de page, et l'API renvoie une erreur 400 pour ces leviers. Trois réserves :
- **Jargon interne** dans les messages : « faux », « défaut », « seconde revue du jumeau ».
- **Désactivation incohérente selon les rapports.** L'adversarial et la DG ARS voient le curseur retraite désactivé. La DGOS et le persona mobile décrivent des contrôles encore manipulables (retraite à +9 an dans l'onglet partagé, case cochable).

### 7. Comparaison V1 / V2

**Non faite.** Les 5 testeurs ont trouvé le port 8767 injoignable (curl renvoie 000). Plusieurs vérificateurs l'ont pourtant vu répondre (HTTP 200) plus tard, et ont seulement lu son code : recherche par commune et bouton « Exporter la fiche » qui télécharge un CSV. Un vérificateur ne trouve en revanche aucun motif d'export dans `prototype-carte/*.html`. Ce point est contradictoire et la V2 reste à recetter.

### 8. Questions ouvertes

1. **Délai d'effet incohérent.** Pour le même scénario (kinés, Puy-de-Dôme, +20 %), un rapport affiche « 2033 (≈ 6 ans) » et un autre « 2032 (≈ 5 ans) ». Est-ce que le paramètre dépend d'un autre état, ou est-ce une erreur ? Coût estimé : environ 10 min de lecture de `formation.py` et `server.py`.
2. **Sorties −10 contre −19** pour ce même scénario selon le testeur. Est-ce un reste du curseur retraite dans l'onglet partagé, qui voudrait dire que le levier suspendu agit encore ? Coût estimé : environ 10 min avec curl.
3. **Incertitude propre à l'écart.** La tendance et le scénario partagent la même erreur de modèle. Faut-il estimer une incertitude de l'écart, par exemple par la sensibilité des paramètres du levier, plutôt que celle du niveau ? Coût estimé : 1 à 2 h, à faire passer par une décision.
4. **Échelle communale dans la V1.** Elle coûte environ 3 s par scénario. Faut-il précalculer la tendance à la commune et ne recalculer les leviers qu'au département ? Coût estimé : 1 à 2 h, décision à enregistrer.
5. **Statut de la V2 carte.** Faut-il relancer une recette sur le port 8767 avant de choisir entre V1 et V2 ? Coût estimé : environ 20 min de temps machine pour 5 personas.
6. **Réponse en moins de 100 ms.** Le critère porte-t-il sur un changement isolé ou sur un geste continu ? La réponse détermine si la recommandation 10 est P1 ou P2. Coût : une décision de quelques minutes.

Aucun fichier n'a été modifié.

# Partie B : V2 carte (port 8767) et comparaison

## Recette V2 de la carte : synthèse de 5 personas

**Avertissement sur la validité.** Les 5 sessions ont toutes dû travailler dans le même onglet « seed », parce que `tabs_create` refusait d'ouvrir un onglet (plafond atteint). Chaque session modifiait le hash et le viewport des autres. Les échecs de tâche viennent donc en grande partie de ce protocole, pas du produit. Les constats ci-dessous ont été revérifiés un par un, surtout dans le code et l'API, et rarement dans le navigateur. Aucune tâche n'a été rejouée dans un onglet isolé.

### 1. Tableau persona × tâche (V2)

| Persona | Tâche | Réussite | Temps estimé (s) | Actions |
|---|---|---|---|---|
| DG d'ARS | Kinés libéraux du Puy-de-Dôme en 2035 et 2050 | non (onglet partagé) | 60 | 6 |
| DG d'ARS | Effet des quotas +20 % | non testé | 0 | 0 |
| DG d'ARS | Zoom jusqu'à Clermont-Ferrand | non testé | 0 | 0 |
| DG d'ARS | Signalement des leviers défectueux | partielle | 15 | 1 |
| DGOS | Comparer 3 scénarios dentistes | partielle | 240 | 9 |
| DGOS | Vérifier sources, millésimes, hypothèses | partielle | 90 | 3 |
| DGOS | Identifier les limites du modèle | oui | 60 | 2 |
| DGOS | Exporter une fiche | partielle | 60 | 2 |
| Élu·e | Sages-femmes du Cantal en une phrase | non (onglet partagé) | 150 | 14 |
| Mobile | Pharmaciens de sa région en 2035, avec incertitude | non | 90 | 7 |
| Mobile | Mesures mobiles (débordement, cibles, troncature) | oui | 20 | 2 |
| Adversarial | Rafale de valeurs extrêmes sur le curseur | oui | 20 | 2 |
| Adversarial | Lire effectif, fourchette, écart, flux | oui | 30 | 2 |
| Adversarial | Coupure réseau simulée | non | 15 | 1 |
| Adversarial | API invalide (curl) | oui | 30 | 8 |
| Adversarial | Hash d'URL invalide | partielle | 10 | 2 |

Bilan : 5 tâches sur 16 réussies, 5 partielles et 6 en échec ou non testées. Au moins 4 des échecs sont dus à l'onglet partagé.

### 2. Constats V2 confirmés (dédoublonnés)

Les constats sont triés par score = gravité × fréquence, avec les valeurs réévaluées à la vérification (gravité et fréquence sur 5).

| # | Constat | G×F | Personas | Repro | Ce qu'on observe |
|---|---|---|---|---|---|
| C1 | Aucun choix de l'année. Le titre reste figé sur « Offre libérale 2050 » et la fiche ne donne que 2026 et 2050. | 3×4 = 12 | ARS, DGOS, mobile, adversarial | Chercher un réglage d'année | Titre écrit en dur (index.html l.134). Fiche limitée à « Effectif 2050 » et « Écart en 2050 ». 2035 n'est qu'une graduation de la courbe. Seul le CSV contient toutes les années. |
| C2 | Sous 900 px, les professions ne sont que des pastilles de couleur, sans libellé ni nom accessible. La barre déborde de l'écran. | 3×4 = 12 | ARS, élu, mobile | Fenêtre de 390 px | `#profs span{display:none}` (l.126), aucun aria-label. Barre jusqu'à x = 438 pour 390 px d'écran : Kinés coupé, Infirmiers hors écran, sans possibilité de défiler. |
| C3 | L'export est un CSV brut, pas une fiche. | 3×4 = 12 | DGOS | Ouvrir un territoire, puis « Exporter la fiche » | Une ligne d'en-tête, puis `annee;tendanciel;scenario;bas;haut`. Rien sur les sources, les flux, les hypothèses ou la définition de la fourchette. |
| C4 | Ni densité ni référence par habitant. | 3×4 = 12 | DGOS | Fiche de l'Indre | Effectifs bruts seulement (78 → 175). Aucune donnée de population dans le code. |
| C5 | La raison des leviers retraite et régulation est donnée en jargon interne. C'est une régression : la V1 avait une formulation claire. | 2×4 = 8 | les 5 | Panneau Leviers | « levier retraite faux sur la tranche 65+ (seconde revue, défaut 1) », recopié tel quel depuis server.py l.47-48 |
| C6 | Termes non expliqués : « plancher », « remplacement seul », « tendanciel », « pente d'erreur de backtest », « points d'écart à la France ». | 2×4 = 8 | DGOS, élu | Fiche France, bloc Zonage, légende | Flux « plancher −16 » affiché avec sa clé brute (absente de FLOWLBL) |
| C7 | La raison de l'absence des infirmiers n'apparaît qu'au survol (title), et en jargon. | 2×4 = 8 | ARS, DGOS | Bouton Infirmiers grisé | « Absent : table public / privé sans âge ni sexe (axe 4)… jumeau » |
| C8 | En mobile, le panneau Leviers est ouvert par défaut et masque la carte. | 2×4 = 8 | ARS, DGOS, élu, mobile | 390×844, à l'ouverture | Panneau de 260×510 px : 67 % de la largeur, environ 40 % de la surface, environ 50 % avec l'aide et la légende. Les 70 % annoncés étaient exagérés. |
| C9 | Cibles tactiles de moins de 44 px | 2×4 = 8 | mobile, adversarial | 390×844, getBoundingClientRect | 6 éléments vérifiés (et non 11) : repli 24×24, zoom 36 à 40 px, curseurs de 16 px de haut, pastilles 32×34 |
| C10 | Une coupure réseau passe inaperçue : le curseur et les chiffres affichés ne correspondent plus. | 3×2 = 6 | adversarial | Faire échouer fetch, puis curseur à ×1,40 | Le curseur indique ×1,40, le panneau garde les chiffres de ×0,80, aucun message. `refresh()` n'a pas de catch (l.282-294). |
| C11 | Le jeu de données source n'est jamais nommé. | 2×3 = 6 | DGOS | Sous-titre de la fiche, pied de page | « origine des données 2026 » ; « Données : jumeau v2 » |
| C12 | Pas de comparaison entre scénarios. « Comparer » compare des territoires. | 2×3 = 6 | DGOS | Bouton Comparer | addCmp() ajoute un territoire et S.quotas reste une valeur unique |
| C13 | L'instrumentation de développement est visible par l'utilisateur. | 1×5 = 5 | ARS, élu, mobile | Bas de la légende | « réponse perçue p50 … ms · p95 … · jumeau … ms » |
| C14 | Un hash invalide est ignoré sans message, et q = 99 est quand même envoyé à l'API et à l'export. | 2×1 = 2 | adversarial | `#p=infirmiers&q=99&v=zzz` | readHash() ne valide rien, le listener hashchange est vide |
| C15 | Une route API inconnue renvoie un 404 en HTML au lieu de JSON. | 1×1 = 1 | adversarial | `curl /api/territoire?code=99999` | Page « Error response » de SimpleHTTP |

**Constats réfutés**
- **Onglet partagé (3 personas)** : c'est un artefact du protocole de test, pas un défaut du produit. Aucun code ne modifie le hash tout seul.
- **Latence perçue d'environ 1 s (4 personas)** : c'est un artefact de mesure. requestAnimationFrame est limité à environ 1 Hz dans un onglet en arrière-plan. Le serveur répond en 1 à 15 ms (mesuré au curl).
- **Panneau détail figé quand le levier bouge (DGOS)** : le code recalcule bien le panneau via refresh(). Le constat venait probablement d'une version antérieure. Reste à vérifier dans le navigateur.
- **Effectif affiché à 0 (2 personas)** : le tween démarre à 96 % de la valeur et dure 280 ms. Le 0 n'est visible que si requestAnimationFrame est suspendu.

### 3. Comparaison V1 / V2

#### Constats V1

| n° | Constat V1 | Statut V2 |
|---|---|---|
| 1 | Rien hors de 2050 | Présent, en partie corrigé : trajectoire complète sur la courbe et dans le CSV, mais rien de lisible dans l'interface |
| 2 | Pas de fiche exportable | En partie corrigé : CSV brut sans sources ni hypothèses |
| 3 | Effet non comparable à l'incertitude | Corrigé : fourchette et écart au tendanciel côte à côte |
| 4 | Pas d'URL d'état | Corrigé : hash plus bouton « Enregistrer le scénario » |
| 5 | Ni densité ni comparaison | Présent (« Comparer » et écart à la France existent, mais aucune densité) |
| 6 | Échelle communale | Non vérifié (la recherche annonce les communes) |
| 7 | Libellés de départements faux | Non vérifié (« Indre » s'affiche correctement) |
| 8 | Source loin du chiffre | En partie corrigé : le millésime est près du chiffre, le jeu de données n'est pas nommé |
| 9 | Zonage non territorialisé | En partie corrigé : zonage au département, mais « remplacement seul » non défini |
| 10 | Choix de l'année peu visible | Présent et aggravé : il n'y a plus aucun choix |
| 11 | Latence > 100 ms | Non établi en V2 : la mesure est faussée, le serveur répond en 1 à 15 ms. À remesurer au premier plan. |
| 12 | Coupure réseau | Présent, sous une forme silencieuse, ce qui est plus trompeur |
| 13 | Pas de mode simple | Présent (non vu) |
| 14 | Jargon | Présent |
| 15 | Fourchette inexpliquée | Corrigé |
| 16 | « Plancher » inexpliqué | Présent |
| 17 | Jargon des leviers suspendus | Présent, et en régression par rapport à la formulation V1 |
| 18 | Kinés par défaut | Présent (observation partielle) |
| 19 | Raison infirmiers au survol | Présent |
| 20 | Débordement mobile | Corrigé pour la page (scrollWidth 390), mais la barre des professions déborde |
| 21 | Libellés du graphique d'environ 5 px | Non vérifié |
| 22 | Somme des flux inexacte | Corrigé (−9 070 exact) |
| 23 | Cibles tactiles < 44 px | Présent |
| 24 | Fil d'Ariane mobile | Non vérifié |
| 25 | Accord grammatical | Non vérifié |
| 26-27 | API sans validation | Corrigé (400 avec bornes) ; reste le 404 en HTML |

Bilan : 7 corrigés, 4 en partie, 12 présents, 1 non établi, 6 non vérifiés.

#### Critères d'interface

| Critère | V1 | V2 |
|---|---|---|
| Vue territoriale d'emblée | non | oui, carte plein écran |
| État partageable | non | oui |
| Incertitude face à l'effet du levier | non | oui, avec la fourchette expliquée |
| Décomposition par flux | inexacte | exacte |
| Choix de l'horizon | peu visible | absent |
| Fiche exportable | non | CSV brut |
| Sources nommées | loin du chiffre | millésime seul |
| Mobile | débordement de la page | pas de débordement de page, mais panneau, pastilles et cibles gênants |
| Robustesse réseau | erreur brute | chiffres périmés sans signal |
| Langage | jargon | jargon, avec régression sur le n°17 |
| Latence | 130 à 314 ms mesurés | serveur à 1-15 ms, ressenti au premier plan non mesuré |

### 4. Recommandations V2

**P1, avant la démo**
1. Ajouter un sélecteur d'horizon (2030, 2035, 2040, 2050), mis dans l'URL. Il pilote le titre, la carte, la fiche, la fourchette et un repère sur la courbe. Résout C1.
2. Ajouter dans le front des libellés en langage clair pour les leviers suspendus et pour les infirmiers, toujours visibles, en reprenant la formulation V1. Ajouter « plancher » à FLOWLBL et définir « remplacement seul ». Résout C5, C6 et C7.
3. Sous 900 px : abréviations visibles (SF, Dent., Pharma, Kiné, Inf.) ou un `<select>`, aria-label sur chaque bouton, barre limitée à 100vw. Résout C2.
4. Gérer les erreurs dans `refresh()` et au clic : bandeau « chiffres du scénario précédent », bouton Réessayer. Résout C10.
5. Masquer `#lat` sauf avec `?debug=1`. Résout C13.

**P2**
1. Nommer le jeu de données et son millésime (RPPS…) dans la fiche, l'attribution et l'export. Résout C11.
2. Faire une fiche imprimable avec leviers, flux, fourchette et sa méthode, sources et leviers suspendus, et garder le CSV en complément. Résout C3.
3. En mobile : panneau Leviers replié par défaut sous 768 px, cibles d'au moins 44 px. Résout C8 et C9.
4. Écarter de l'indicateur les mesures prises quand l'onglet est masqué, puis remesurer au premier plan avec au moins 20 mesures.

**P3**
1. Densité pour 100 000 habitants à partir d'INSEE et d'Omphale. Résout C4.
2. Épingler 2 ou 3 scénarios superposés, et renommer le bouton en « Comparer ce territoire ». Résout C12.
3. Valider readHash() et prévenir par un toast quand un paramètre est corrigé. Résout C14.
4. Renvoyer un 404 en JSON. Résout C15.
5. Protocole de test : lancer les personas l'un après l'autre, ou chacun dans son contexte de navigateur.

### 5. Verdict

**La V2 va en démo.**

Sur ce qui a été vérifié, elle couvre ce qui manquait le plus à la V1 :
- la vue territoriale ;
- l'URL d'état ;
- la fourchette comparée à l'effet du levier ;
- des flux exacts ;
- une API qui valide ses paramètres.

Les personas qui ont pu se prononcer (DGOS, élu, mobile, adversarial) la préfèrent tous. Ses défauts principaux (C1, C2, C5, C10, C13) relèvent de l'interface et se corrigent en peu de temps, car les données par année existent déjà (f.years, f.scn).

Ce qui ferait changer d'avis :
- une latence au premier plan supérieure à 100 ms ;
- le bug du panneau figé reproduit dans un onglet isolé ;
- les points P1 n°1, 2 et 4 non faits avant H-6.

Dans ce dernier cas, il faut présenter la V2 sur un poste de bureau large, sans couper le réseau, et dire à l'oral que le choix de l'année est absent.

### 6. Questions ouvertes

1. **Le panneau détail suit-il vraiment le levier ?** Le refus du constat repose sur le code seul. Il faut rejouer dentistes, France, quotas de 0,8 à 1,2 dans un onglet isolé. Coût : environ 5 min de Claude.
2. **Quelle est la latence perçue au premier plan ?** Rafale de 20 mouvements du curseur, lecture de `window.__lat`. Coût : environ 5 min de Claude.
3. **Les constats non vérifiés (6, 7, 13, 21, 24, 25, 18) et l'élu sur le Cantal** : il faut rejouer les 5 personas l'un après l'autre dans des onglets isolés. Coût : environ 30 à 40 min de Claude (estimation).
4. **Densité (C4) avant ou après la démo ?** Il faut joindre la population INSEE puis la projection Omphale au serveur, et décider si la carte se colore par densité. Coût : environ 45 à 90 min de Claude (estimation), en plus d'une décision d'équipe à inscrire dans `v2/docs/lab/decisions.md`.

Aucun fichier n'a été modifié.

## ? Next
| Item | Cost |
|---|---|
| Rejouer la V2 avec 1 persona à la fois, dans un onglet isolé, captures écrites sur disque | ~30–40 min Claude (estimé) |
| Latence V2 au premier plan, 20 mesures en rafale | ~5 min Claude |
| Contrôler que les retours sur la carte (zoom, cases, limites ARS, DROM) sont intégrés | ~10 min Claude après livraison proto-carte |
