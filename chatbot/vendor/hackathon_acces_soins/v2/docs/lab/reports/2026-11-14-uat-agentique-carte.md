---
type: analysis
date: 2026-11-14
author: Claude
question: "Les 5 personas cibles accomplissent-elles leur mission sur la carte V2 (http://localhost:8767/) quand chacune travaille dans un onglet isolé, et quels constats résistent à une vérification adversariale ?"
headline: "5 tâches réussies sur 21 (14 partielles, 2 échecs) ; 37 constats confirmés sur 41 soumis ; après dédoublonnage, 3 P0 (titre de fiche d'une autre profession, sélecteur de profession hors écran sur mobile, export sans sources) et 9 P1"
status: done
tags: [uat, carte, personas]
---

# Recette agentique de la carte V2 (port 8767), deuxième passe

> **Headline :** 5 tâches réussies sur 21 (14 partielles, 2 échecs). 37 constats confirmés sur 41 soumis. Après dédoublonnage, il reste **3 P0** et **9 P1**. Le moteur donne des chiffres cohérents et l'API répond vite (4 à 132 ms mesurés). L'interface bloque sur des recouvrements d'éléments, sur la traçabilité et sur le mobile.

## Question
Les cinq personas peuvent-elles accomplir leur mission sur la carte V2, maintenant que chacune travaille dans un onglet isolé ? Ce sont la DG d'ARS (Auvergne-Rhône-Alpes), un chargé de mission DGOS, un·e élu·e du Cantal, un utilisateur mobile et un testeur adversarial. Quels constats résistent à une vérification adversariale ? Qu'est-ce qui a changé depuis la recette précédente (`2026-11-14-uat-interface.md`) ?

## Méthode
- **5 personas, une à la fois, chacune dans son propre onglet.** Cela corrige le principal défaut de protocole de la passe précédente, où toutes partageaient un onglet. Fenêtres utilisées : 1024×768 (ARS, élu·e), 1440×900 (DGOS), 375×812 avec le préréglage mobile et un rechargement (mobile).
- **Vérification adversariale par angle.** Les 41 constats ont été répartis entre trois vérificateurs : fonctionnel (18), ux (18) et robustesse (5). Chaque vérificateur rejoue le constat ou cherche à le réfuter, en lisant le DOM, le code `index.html`, l'API ou en lançant curl.
- **Durées :** temps-utilisateur **estimé** par les agents, de 5 à 420 s par tâche, soit environ 51 min au total. Rien n'a été chronométré.
- **Latences :** **mesurées** avec `performance.now()`, `PerformanceObserver` et curl.
- **Limites :**
  - Ce sont des agents, pas de vrais utilisateurs.
  - Aucune capture n'a été écrite sur disque. Chaque preuve est décrite en texte (sélecteur, texte visible, coordonnées).
  - Le volet du navigateur était souvent masqué. Dans ce cas, `requestAnimationFrame` ne se déclenche pas (test : « timeout 3000 »). Plusieurs constats de latence et de fiche périmée viennent de cet artefact, et ils sont signalés comme tels plus bas.

## Résultats

### Tableau persona × tâche

| Persona | Tâche | Réussite | Temps estimé (s) | Actions | Point clé |
|---|---|---|---|---|---|
| DG ARS | ARA puis Puy-de-Dôme, kinés : effectifs 2026, 2050 et 2035 | partielle | 150 | 14 | D63 : 1 071 → 1 731 (1 244 – 2 219). La valeur 2035 n'est lisible que par l'API (1 397). Le clic sur une suggestion de recherche est sans effet. |
| DG ARS | Places en formation +20 %, seulement dans la région | oui | 120 | 9 | D63 +198 (+11,5 %), ARA +2 343 (+11,7 %). Les départements 13 et 75 restent égaux au tendanciel. |
| DG ARS | Régulation à l'installation : départements d'ARA concernés | partielle | 180 | 12 | « 6 département(s) approché(s) » sans liste. 0 en ARA, mais visible seulement dans l'API. |
| DG ARS | Comparer Puy-de-Dôme et Rhône, avec la fourchette | partielle | 200 | 14 | La fourchette est absente du bandeau. Le 2e « Comparer » ne fonctionne qu'au clavier. |
| DGOS | Dentistes, France : 3 scénarios comparés en 2050 | partielle | 420 | 22 | Évolution de +80,5 %, +90,8 % et +66,5 %, contre +61,4 % au tendanciel. Pas de comparaison côte à côte. |
| DGOS | Statut sourcé ou supposé et source de chaque levier | partielle | 240 | 6 | La source n'est que dans un `title` au survol, avec `tabIndex -1`. |
| DGOS | Limites du modèle | partielle | 300 | 8 | Seul l'horizon est explicité (« Aucun backtest n'existe à 2050 »). |
| DGOS | Exporter une fiche avec sources et hypothèses | **non** | 180 | 6 | CSV sans source, sans millésime et sans hypothèse. |
| Élu·e | Sages-femmes du Cantal en 2050, en une phrase | partielle | 150 | 9 | 16 → 38 (16 – 59). La phrase est à écrire soi-même. La suggestion ne répond pas au clic. |
| Élu·e | Effet de « réguler l'installation » sur le Cantal | partielle | 240 | 8 | Aucun effet (regul_deps = [974]), mais la fiche invoque « places en formation × 1,00 ». |
| Élu·e | Relevé du jargon et des termes jugeants | oui | 120 | 2 | 0 terme jugeant. Une quinzaine de termes de jargon. |
| Mobile | Pharmaciens d'ARA en 2035 et 2050, avec l'incertitude (375 px) | partielle | 240 | 14 | Le sélecteur de profession est hors écran (contournement par l'URL). 2050 : 9 019 (8 498 – 9 539). 2035 : visible seulement dans l'API (8 412). |
| Mobile | 3 leviers de familles différentes | partielle | 180 | 10 | 2 familles seulement. +1 740 = 413 + 1 326 + 1, cohérent. |
| Mobile | Revenir au préréglage desktop et fermer l'onglet | oui | 5 | 2 | — |
| Adversarial | Rafale de 30 changements de curseurs | partielle | 60 | 4 | L'état final est cohérent (+81,8 %). Le recalcul est figé tant que rAF ne se déclenche pas. |
| Adversarial | Valeurs aux bornes et hors bornes dans l'API | oui | 45 | 3 | 400 avec les bornes. Trous trouvés : terr inconnu, booléens invalides, une erreur 500. |
| Adversarial | Valeurs hors bornes dans le hash | **non** | 60 | 5 | Carte vide, et l'erreur ne peut pas être corrigée depuis l'interface. |
| Adversarial | Mesure « seulement dans la région », puis retour à la France | partielle | 50 | 7 | +30 % devient national sans message (+61,2 % → +85,8 %). |
| Adversarial | Régulation pour les pharmaciens (pas de zonage) | partielle | 40 | 6 | Le levier est désactivé, mais le badge reste à « 1 actif » s'il a été activé ailleurs. |
| Adversarial | Somme des départements = France ; scénario neutre = tendanciel | partielle | 60 | 6 | Égalités vérifiées pour 4 professions. La fiche porte le titre d'une autre profession. |
| Adversarial | Lexique neutre | oui | 10 | 1 | 0 occurrence des termes interdits. |

**Bilan :** 5 tâches réussies, 14 partielles et 2 échecs, sur 21 tâches.

### Constats confirmés, dédoublonnés, triés par gravité

Gravité : celle de la persona. Quand un constat est fusionné, c'est la plus haute qui est retenue. Les réserves des vérificateurs sont indiquées.

| # | Gravité | Constat | Personas | Preuve courte | Suggestion |
|---|---|---|---|---|---|
| 1 | **P0** | La fiche garde le libellé de l'ancienne profession après un changement de profession. | adv (P0), dgos (P1), élu·e (P3) | Fiche France en dentistes, puis clic sur Pharmaciens : « Chirurgiens-dentistes · secteur libéral » au-dessus de 63 612 / 72 309, qui sont les chiffres des pharmaciens. Cause : `renderCard` ne refait l'en-tête que si `c.dataset.t!==S.terr` (l.427). **Réserve :** le mélange effectifs/fourchette vient de rAF (volet masqué). Le titre faux, lui, persiste aussi au premier plan d'après le code. | Clé t+prof dans `dataset`, ou reconstruire l'en-tête au changement de profession. |
| 2 | **P0** | Sur mobile, le sélecteur de profession, « Enregistrer le scénario » et « Taille du texte » sont hors écran. | mobile | À 375 px, les boutons de profession sont à x = 459 à 595, `#save` à x = 539, avec `overflow:hidden` sur body et html. read_page ne liste aucun bouton de profession. | Sous 768 px : barre en colonne, ou menu déroulant des professions, ou rangée défilante. |
| 3 | **P0** | L'export ne contient ni sources, ni millésimes, ni hypothèses. | dgos | `exportCard()` (l.486) : une ligne `# … leviers quotas=1 … dest=salariat … origine …`, puis `annee;tendanciel;scenario;bas;haut`. **Correction du vérificateur :** l'export existe aussi au niveau France (fiche t=FR). | Bloc de métadonnées : jeux de données et millésimes, puis, pour chaque levier actif, son libellé, sa valeur, son statut, sa source et son délai, et enfin les limites. |
| 4 | P1 | La légende recouvre le panneau Leviers : Installer, Retenir et « Couleur de la carte » ne se cliquent pas, et le panneau ne défile pas. | ars, dgos, élu·e, mobile | En 1024×768, `#legend` occupe y 525–750, et elementFromPoint sur « Installer » renvoie `#legend`. En 1440×900, le bouton « Écart au tendanciel » est sous la légende. Dans le panneau, `.body` a scrollHeight = clientHeight = 492. En 375 px, Installer, Retenir, lv-cumul et lv-precoces renvoient tous la légende. | `max-height` et `overflow-y:auto` sur le panneau Leviers. Replier ou déplacer la légende quand le panneau est ouvert. |
| 5 | P1 | Une suggestion de recherche ne répond pas au clic : le HEADER la recouvre. | élu·e (P1), ars (P2) | Option à y 74–112 : elementFromPoint renvoie HEADER (inside=false), et la sélection dépend d'un mousedown sur `#results` (l.396). Seul le clavier fonctionne. **Correction :** l'élément qui recouvre est le HEADER, pas la puce du fil d'Ariane. | z-index sur la liste, ou `pointer-events` sur l'en-tête. Ajouter un test e2e du clic. |
| 6 | P1 | Le bandeau de comparaison recouvre le bouton « Comparer » : impossible d'ajouter un 2e territoire à la souris. | ars | En 1024×768, le bouton est à y 696–735 et `#cmp` à 667–750. elementFromPoint renvoie « DIV.c : Puy-de-Dôme… ». CSS : `#cmp{left:50%;bottom:16px}`. | Déplacer le bandeau, ou ajouter un padding-bottom à la fiche. |
| 7 | P1 | Au retour à la France, une hausse des places prévue pour une seule région s'applique à toute la France, sans message. | adv | Hash `quotas:1.3,quotas_region:1` → `quotas:1.3,quotas_region:0`. La légende passe de +61,2 % à +85,8 %. MutationObserver sur `#toast` : []. `closeCard()` ne touche pas à `quotas`. | Remettre `quotas` à 1, ou demander, ou au minimum afficher un toast explicite. |
| 8 | P1 | Un lien partagé avec des valeurs invalides donne une carte vide, sans moyen visible d'en sortir. | adv | `quotas:99,retraite:-5,cumul:NaN` : légende vide et étiquette « +9800 % ». Ensuite, l'erreur sur retraite reste invisible (curseur à 0), le toast disparaît après 2 200 ms et il n'y a aucun bouton de réinitialisation. Avec `p=medecins` : aucune profession sélectionnée et fil d'Ariane « France › D999 ». | Borner chaque valeur dans `readHash` à [min ; max] de META, remplacer NaN par la valeur par défaut, et prévenir par un toast « lien partiellement invalide ». |
| 9 | P1 | L'effectif 2035 et sa fourchette sont absents de l'interface. | mobile (P1), ars (P2) | `chart()` produit un SVG statique, sans gestionnaire de souris, et les indicateurs ne donnent que 2026 et 2050. API : D63 2035 = 1 397, R84 = 16 556, pharmaciens R84 = 8 412. Les bornes 2035 sont calculables à partir de k. | Info-bulle par année ou sélecteur d'horizon : valeur, tendanciel, fourchette. |
| 10 | P1 | Sur mobile, la fiche territoire est coupée à gauche. | mobile | `#card` va de left −103 à right 357, pour une largeur de 400 px. Le bloc « Effectif 2026 » est à [−84, 49]. | Tiroir bas pleine largeur sous 768 px. |
| 11 | P1 | Les sources des leviers ne sont que dans une infobulle au survol, et en jargon interne. | dgos | 9 badges `.badge[title]` en `tabIndex -1`. Exemples : « fiche param-age-entree-exercice… », « mécanisme B1 de l'observatoire », « axe 4 : zonage ». Aucune de ces sources n'apparaît dans `innerText`. | Ligne « Source : … » visible ou bouton (i) atteignable au clavier, avec des références citables. |
| 12 | P1 | Régulation : l'interface ne dit pas combien de départements de la région sont concernés. | ars | « 6 département(s) approché(s) » sans liste. regul_deps = [66, 971, 34, 13, 2A, 67], soit 0 en ARA, et s50 identique avec ou sans régulation. **Réserve :** la valeur « +2 343 » n'a pas été reproduite, car les leviers étaient par défaut. | « Départements régulés dans la région : 0 sur 12 » et « levier sans effet ici ». Lister les départements concernés. |
| 13 | P2 | Axes de la trajectoire tronqués. | ars | Les graduations Y débordent de −5 px et « 2050 » de −6 px, parce que les graduations sont à x = 34 avec `text-anchor` end. | Marges du SVG plus larges, ou format « 19,5 k ». |
| 14 | P2 | La fiche peut rester périmée sous un curseur déjà déplacé. | ars | Reproduit **seulement en arrière-plan**, où le refresh en attente ne part jamais. Au premier plan, le décalage est d'environ 32 ms (médiane mesurée, n = 8). Le vérificateur propose P3. | Jeton de requête ou AbortController, plus un état « calcul… ». |
| 15 | P2 | Le levier dest s'affiche « effet supposé » alors que l'API le déclare « non mesurable ». | dgos | l.377 : `sup=l.status!="sourcé"&&l.status!="mesuré"`. | Ajouter un 3e état « non mesurable ». |
| 16 | P2 | Aucune limite du modèle ni aucun jeu de données nommé dans l'interface. | dgos | grep sur le fichier servi : 0 occurrence de limite, RPPS, DREES, INSEE, Hippocrate, millésime ou Méthode. | Panneau « Méthode et limites ». |
| 17 | P2 | Pour un levier sans effet, la fiche explique l'absence d'écart par « places en formation × 1,00 ». | élu·e | Cantal, regul:1 : « Aucun écart … (places en formation × 1,00) ». Le département 974 n'est nommé nulle part. | Phrase propre au territoire, qui nomme le levier et les départements concernés. |
| 18 | P2 | Pas de phrase en langage courant ni de mode simple. | élu·e | « Hachures : fourchette indicative ≈ 8 cas sur 10, pente d'erreur de backtest… ». `/mode simple\|politique/` ne trouve rien. | Phrase générée en tête de fiche. Détail technique replié. |
| 19 | P2 | Jargon et références internes à l'écran et dans les infobulles. | élu·e | « Écart au tendanciel », « décomposé par flux », « remplacement seul », « pts », « param-… », « axe 4 », « B1 ». 0 terme jugeant. | Glossaire au survol. Ne garder que les sources publiques. |
| 20 | P2 | Cibles tactiles de moins de 44 px. | mobile | Curseurs 260×18, cases 15×15, boutons de profession 32×38, `#fold` 28×28. | Zone de toucher d'au moins 44×44. |
| 21 | P2 | Le texte d'aide de la légende ne suit pas la vue. | mobile (P2), ars (P3) | « Vue France : régions… Maj + clic » est écrit en dur dans le HTML, y compris sur R84 et D63. | Aide adaptée au niveau affiché et au type de pointeur. |
| 22 | P2 | L'API accepte en silence les entrées invalides, et une requête renvoie 500. | adv | terr=ZZ ou D99 → 200 avec les chiffres France. regul=2, oui ou −1 → traités comme 0. dest vide → 200. `quotas_region=1&terr=FR` → 500, **seulement si quotas ≠ 1**. | Répondre 400 sur terr, sur les booléens, sur dest et sur la ValueError. |
| 23 | P2 | Les infirmiers sont exposés sans mention de leur statut. | adv | Bouton actif, `missing = {}`, 100 départements contre 101 pour les kinés. **Sous-constat réfuté :** le total France est cohérent (277 788 correspond à 2023, l'origine, et 288 833 à la somme des départements en 2026). | Marquer le bouton selon la décision de périmètre, ou documenter le département manquant et l'origine 2023. |
| 24 | P2 | Les badges « 1 actif » et « oui » s'affichent pour la régulation des pharmaciens, qui n'a pas d'effet. | adv | Après activation pour les kinés puis passage aux pharmaciens : `regul:1` reste dans le hash, `#on-installer` affiche « 1 actif » alors que `lv-regul` est désactivé. Total identique (72 308,7). | Ne compter que les leviers disponibles pour la profession, et afficher « sans objet ». |
| 25 | P3 | Le compteur « réponse perçue » affiche plusieurs secondes et la ligne de debug est visible. | ars, dgos, adv | Affichages de 2 034 à 19 833 ms, contre une API mesurée entre 4 et 132 ms. C'est un artefact rAF du volet masqué : la mesure s'arrête après deux rAF (l.328). | Écarter les mesures quand `visibilityState` n'est pas 'visible'. Masquer `#lat` hors mode admin. |
| 26 | P3 | La file de recalcul attend requestAnimationFrame. | adv | Test rAF : « timeout 3000 ». Le hash reste figé sur la 1re valeur de la rafale. L'état final est juste une fois l'image rendue. | Écrire le hash avant d'attendre rAF. |
| 27 | P3 | Modifier le hash à la main n'applique pas les leviers. | adv | Aucun écouteur hashchange. popstate (l.501) ne lit que `t`, puis writeHash réécrit le hash. | Écouteur hashchange qui relance `readHash()` avec bornage, puis `refresh()`. |
| 28 | P3 | Navigation et libellés. | ars, élu·e | Sous 1200 px, le fil d'Ariane devient « France › Puy-de-Dôme » (il est correct en 1440 px). « Région de Puy-de-Dôme » et « Région de Cantal » viennent de `levState`. | Fil d'Ariane à 3 niveaux à toutes les largeurs. Afficher la région réelle. |
| 29 | P3 | Recherche et accessibilité. | ars, dgos | Le placeholder promet « Commune », mais la recherche répond « Grain communal : à venir ». Sous 900 px, les boutons de profession n'ont pas de nom accessible. `/api/meta` contient « D62 Nord-Pas-de-Calais » et « Côte-d Or ». | Corriger le placeholder, ajouter un aria-label, corriger les libellés via le COG. |

### Constats réfutés

- **« Environ 0,5 s par levier à cause d'un anti-rebond » (élu·e) :** le code n'a pas d'anti-rebond, et l'API répond en 4 à 22 ms (curl). Les 0,5 s mesurent le bridage du volet masqué.
- **« Pas d'effectif national » (dgos) :** réfuté pour cette moitié. La recherche « France » ouvre une fiche t=FR avec les effectifs 2026 et 2050 et la fourchette. **La seconde moitié tient :** « Comparer » compare des territoires, pas des scénarios.
- **« Quatre familles de leviers dépliées par défaut sur mobile » :** seule « Former » est ouverte. Ce qui est vrai : le panneau, non replié par défaut, couvre la majeure partie de la carte (299×751).
- **« t= non restauré au rechargement » (mobile) :** c'est un artefact rAF, et la fiche s'affiche dès la première image. **Défaut réel, reformulé :** lors d'un changement de hash sans rechargement, `p=` est ignoré puis écrasé, alors que `t=` est bien appliqué.

## Comparaison avec l'UAT précédente

**Corrigé ou amélioré**
- **Protocole :** les onglets sont isolés, et les personas peuvent toutes se prononcer, contre 5 tâches sur 16 auparavant.
- **Leviers retraite et régulation :** ils ne sont plus suspendus et ils agissent. Exemples : retraite = 2 donne +2 428 dentistes en 2050 ; la régulation donne −6 230 kinés en France.
- **Effectif national :** lisible dans la fiche France.
- **Export :** il existe aussi au niveau France (V1 n°2 en partie corrigé).
- **Flux :** la somme est exacte (+1 740 = 413 + 1 326 + 1).
- **Fil d'Ariane France › région › département :** présent en 1440 px, mais pas sous 1200 px.
- **Grain communal :** l'interface dit maintenant « Grain communal : à venir » (V1 n°6 en partie corrigé, mais le placeholder promet toujours « Commune »).
- **Latence de l'API :** confirmée faible, de 4 à 132 ms mesurés (V1 n°11).
- **Lexique neutre :** respecté.
- **Panneau détail figé (question ouverte n°1) :** pas de figement au premier plan. Décalage d'environ 32 ms mesuré.

**Reste**
- **C1, horizon :** toujours aucune valeur 2035 dans l'interface.
- **C3, export :** toujours un CSV brut. C'est maintenant un P0.
- **C2 :** professions inatteignables sur mobile (aggravé en P0) et sans nom accessible sous 900 px.
- **C5 et C6, jargon :** déplacé vers les infobulles des sources (« param-… », « B1 », « axe 4 »). « plancher » reste affiché tel quel dans les flux.
- **C7, infirmiers :** le problème a changé. Ils ne sont plus grisés : ils sont exposés sans mention de statut.
- **Interface mobile :** panneau ouvert par défaut qui couvre la carte (C8), cibles de moins de 44 px (C9).
- **Traçabilité :** jeu de données jamais nommé (C11), pas de comparaison de scénarios (C12), instrumentation visible (C13).
- **Hash :** toujours non validé (C14), et l'effet est maintenant visible : carte vide.
- **API :** un territoire inconnu répond encore 200 (V1 n°26), et une erreur 500 subsiste (V1 n°27, sur `quotas_region`).
- **Libellés D62 et Côte-d Or (V1 n°7) :** présents.
- **Régulation :** toujours pas reliée au territoire affiché (V1 n°9, sous une autre forme : ni compte régional ni explication).

**Non testé dans cette passe :** coupure réseau (C10), densité (C4), 404 en HTML (C15), accord « libérales » (V1 n°25), latence perçue au premier plan.

## ⚑ Ce qui pourrait rendre ce rapport faux
- **Volet du navigateur masqué :** rAF ne se déclenche pas. Tous les constats de latence perçue, de fiche périmée ou de mélange de chiffres en dépendent en partie. Les constats n°14, 25 et 26 et une partie du n°1 pourraient être moins graves au premier plan.
- **Gravité dépendante de la largeur :** les recouvrements (n°4, 5 et 6) et le fil d'Ariane ont été mesurés en 1024×768, 1440×900 et 375×812. Sur un écran de démo plus grand, certains peuvent disparaître.
- **États des leviers différents :** persona et vérificateur n'avaient pas toujours les mêmes réglages (ARA +2 343 non reproduit, valeurs d'axes différentes). Les mécanismes sont confirmés, mais pas toujours les chiffres exacts.
- **Méthode :** agents et non utilisateurs réels. Les temps sont estimés. Le mobile n'a eu qu'une seule passe, et l'angle robustesse n'a vérifié que 5 constats.
- **Pas de captures sur disque :** les preuves sont textuelles et ne peuvent pas être rejouées visuellement.
- **Gravités :** les P0 et P1 ont été attribués par les agents, sans arbitrage de l'équipe.

## → Ce que ça change
À corriger dans `v2/prototype-carte/index.html` (et `server.py` pour l'API), dans cet ordre :
1. **P0 :** `renderCard` doit reconstruire l'en-tête quand la profession change (clé t+prof, l.427).
2. **P0 :** barre du haut sous 768 px, pour rendre les professions, « Enregistrer » et « A+ » atteignables.
3. **P0 :** métadonnées dans l'export : jeux de données, millésimes, leviers avec statut et source, limites.
4. **P1 :** panneau Leviers défilable, avec la légende repliée quand il est ouvert. Touche 4 personas.
5. **P1 :** liste de suggestions de recherche au-dessus du HEADER.
6. **P1 :** bandeau de comparaison qui ne recouvre plus le bouton « Comparer ».
7. **P1 :** `closeCard()` : remettre les quotas à 1, ou prévenir l'utilisateur, quand on quitte une mesure régionale.
8. **P1 :** borner les valeurs dans `readHash`, avec retour aux valeurs par défaut et un toast.
9. **P1 :** valeur et fourchette 2035, par info-bulle ou sélecteur d'horizon.
10. **P1 :** fiche en tiroir pleine largeur sur mobile.
11. **P1 :** sources visibles et citables sous chaque levier.
12. **P1 :** compte et liste des départements régulés dans la fiche région, avec un message « sans effet ici ».

Pour la démo, tant que les points 4 à 6 ne sont pas faits, utiliser un poste de bureau large et le clavier (Entrée) pour la recherche et pour « Comparer ».

## ? Pour la suite

| Item | Coût |
|---|---|
| Rejouer les constats n°1, 14, 25 et 26 avec le volet au premier plan, pour séparer l'artefact rAF du défaut produit | ~10 min Claude (estimé) |
| Mesurer la latence perçue au premier plan (20 gestes, lecture de `window.__lat`) | ~5 min Claude (estimé) |
| Correctifs P0 n°1 à 3 | ~20–40 min Claude (estimé) |
| Correctifs P1 n°4 à 12 | ~45–90 min Claude (estimé) |
| Re-recette ciblée des P0 et P1 après correction, en onglets isolés, avec captures écrites sur disque | ~30–40 min Claude (estimé) |
| Tester ce qui ne l'a pas été : coupure réseau (C10), 404 JSON (C15), densité (C4) | ~10 min Claude pour C10 et C15 ; C4 : 45–90 min Claude plus une décision d'équipe |
| Un vrai utilisateur (ARS ou élu·e) sur 2 tâches | ~20 min de temps humain (monde), à planifier |
