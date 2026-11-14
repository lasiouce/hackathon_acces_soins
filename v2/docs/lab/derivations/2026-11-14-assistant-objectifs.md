---
date: 2026-11-14
statut: plan, en attente d'accord
headline: "D'un objectif chiffré à un plan de leviers daté : le jumeau cherche, vérifie et date chaque mélange ; le modèle de langage traduit et explique"
---

# Assistant : politique hors modèle → mélange de leviers ; objectif → leviers à actionner aujourd'hui

**ETA (temps Claude) :** ~2 h (1 h 30 – 3 h 30), fin ≈ 19:30, non calibré. Temps machine négligeable (< 5 s par
recherche).

**Portée en une ligne :** l'utilisateur·rice donne soit une politique que le modèle n'a pas, soit un objectif chiffré à un
horizon ; l'assistant répond par des mélanges de leviers du modèle, calculés et vérifiés par le jumeau, avec l'année où il
faut décider chacun.

## Les deux cas
1. **Facilitation** : « aides à l'installation », « rendre le métier plus attractif » ne sont pas des leviers. Deux
   chemins, dans cet ordre :
   - si l'intention a un **effet chiffrable** (« +10 % de kinés en Bretagne »), on se ramène au cas 2 ;
   - sinon, une **traduction supposée** vers les leviers qui portent le même mécanisme (attractivité → moins de départs
     avant 60 ans, plus de cumul emploi-retraite), affichée comme telle, confirmée par l'utilisateur·rice, jamais
     appliquée en silence. Table relisible `chatbot/passerelle/correspondances.yaml` : politique du glossaire
     `non_modelises` (12 entrées) → leviers, mécanisme, statut « supposé », source si elle existe ; l'absence de
     correspondance se dit (« pas dans le modèle »).
2. **Objectif → leviers (le vrai but)** : « je veux au moins 200 kinés pour 100 000 habitants en Auvergne en 2035 :
   quels leviers actionner aujourd'hui ? ». Problème inverse : trouver les mélanges qui atteignent la cible, dans les
   bornes, en tenant compte des **délais** (un levier qui agit après l'horizon ne sert à rien), et dire **quand décider**.

## Contraintes, en unités
- **Exactitude** : 100 % des mélanges proposés atteignent la cible **recalculés par le jumeau** (pas par un
  substitut).
- **Optimalité** : sur 3 cas témoins, le mélange « le plus simple » coïncide avec la force brute sur une grille
  réduite, ou s'en écarte d'un pas de grille au plus.
- **Latence** : recherche < 5 s (mesuré : 1 évaluation C1 ≈ 30 ms ; `atteindre` 1,1 s) ; réponse < 20 s.
- **Faisabilité** : cible hors d'atteinte (même tous leviers au maximum) ou horizon plus court que le délai → dit
  explicitement, avec le meilleur atteignable.

## Alternative la moins chère, dérivée avant de relire l'existant
**Leviers un par un** (`atteindre`, existe) + « tous au maximum ». Coût nul. Ne sait pas proposer un mélange
intermédiaire (« +10 % de places et +1 an de retraite » au lieu de « +35 % de places »), ni dater les décisions.

**Force brute** : 5 leviers × ~8 niveaux ≈ 33 000 combinaisons × 30 ms ≈ 16 min. Trop lent pour une conversation.

**Ansatz retenu : substitut additif, puis vérification.**
1. Courbe d'effet de chaque levier seul sur sa grille (≈ 60 évaluations, ≈ 2 s).
2. Énumération des mélanges sur la somme des courbes (instantané), rangés selon trois critères explicites :
   **le plus simple** (moins de leviers, puis plus petit déplacement normalisé dans les bornes), **le plus tôt** (premier
   effet le plus précoce), **leviers sourcés seulement**.
3. Les 3 à 5 meilleurs recalculés **ensemble** par le jumeau : seuls ces chiffres sont montrés. Si l'interaction fait
   manquer la cible (régulation), on monte d'un pas et on recalcule.
4. Plan daté : pour chaque levier, délai et **année limite de décision** = horizon − délai ; « à décider en 2026 » si
   le délai consomme tout l'horizon.
5. Prudence : la cible est-elle atteinte en valeur centrale seulement, ou aussi au bas de la fourchette ? Option
   « prudente » qui vise le bas de la fourchette.

**Verdict.** Survit contre « un par un » (ne répond pas au mélange) et contre la force brute (trop lente).
**Kill test (≈ 15 min)** : sur 20 mélanges tirés au hasard, écart entre la somme des effets seuls et l'effet combiné
réel. Si > 10 % de la cible pour plus de 2 mélanges, l'additivité ne tient pas : passer à une recherche locale (descente
pas à pas avec le jumeau, ≈ 10 s).

## Ce qui sera construit
- `chatbot/passerelle/requetes.py` : requête **`planifier`** (profession, territoire, année, cible : effectif ou densité,
  en absolu ou en % du tendanciel ou d'aujourd'hui ; contraintes : leviers exclus, sourcés seulement, nombre maximal) →
  mélanges vérifiés, qualificatifs, délai et année limite de décision, statut et source, faisabilité.
- `correspondances.yaml` + requête **`traduire_politique`** pour le cas 1.
- Prompt : « Plan d'action » (ce qu'il faut décider, quand, pour quel effet) ; hors modèle → correspondance supposée
  annoncée comme telle.
- Interface : carte « Plan d'action » (chronologie décision → premier effet → horizon) et « Afficher ce mélange sur
  la carte ».
- 10 questions d'objectif et 6 de politiques hors modèle, **écrites avant le code**, dans `v2/agent/questions.yaml`.

## Hors périmètre
Coûts (aucune donnée ouverte : « pas dans le modèle ») ; optimisation multi-territoires (une région à la fois) ;
leviers continus hors grille ; poids d'« effort » autres que les trois critères affichés.

## Critères d'acceptation
1. « Au moins 200 kinés pour 100 000 habitants en Auvergne-Rhône-Alpes en 2035 : quels leviers actionner aujourd'hui ? »
   → au moins deux mélanges vérifiés, avec l'année limite de décision de chaque levier et la fourchette.
2. 10/10 mélanges proposés atteignent la cible au recalcul ; cibles impossibles signalées 100 %.
3. Kill test d'additivité mesuré et consigné.
4. 6 politiques hors modèle : correspondance supposée annoncée, ou « pas dans le modèle ».
5. Recette de la carte sans régression ; ancrage et vocabulaire mesurés sur les nouvelles questions.

## Questions ouvertes (à trancher par l'utilisateur·rice)
- Les trois critères de classement (simple, tôt, sourcé) suffisent-ils, ou faut-il un critère « réalisme » (rester
  près des valeurs actuelles) ?
- Qui valide la table des correspondances (traductions supposées des politiques hors modèle) ?
