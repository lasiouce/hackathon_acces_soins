---
type: analysis
date: 2026-11-14
author: Claude
question: À quoi doit ressembler l'écran d'accueil de la carte V2 pour les trois personas ?
headline: "3 personas sur 3 refusent l'accueil actuel (France par régions, leviers ouverts, aucun chiffre avant clic) ; 3 sur 3 veulent un chiffre-phrase dès l'ouverture et les leviers repliés ; désaccord sur le point d'entrée (territoire pour ARS et élu·e, national sourcé pour l'Administration)"
status: draft
hypothesis: couche personas (écran de décision V2)
sources: [v2/prototype-carte/index.html, /api/meta, /api/carte, /api/scenario]
tags: [prototype, interface, personas, accueil]
---

# Accueil de la carte V2 : challenge par les trois personas

> **Headline :** trois agents, un par persona (ARS/DG, Administration
> centrale, élu·e), ont lu l'écran et interrogé l'API. **Ils sont d'accord
> sur 4 points et en désaccord sur 1.** Ce sont des avis simulés : ils ne
> remplacent pas un test avec de vrais utilisateurs.

## Convergences (3 sur 3, sauf mention)
1. **Un chiffre en phrase dès l'ouverture**, sans clic. Exemple de l'ARS :
   « Kinés libéraux en ARA : 13 240 en 2026, environ 20 100 en 2050 au
   tendanciel ». Aujourd'hui, rien ne s'affiche avant un clic.
2. **Constater avant d'agir** : les leviers sont repliés derrière
   « Simuler une politique ». Le panneau ouvert, avec deux leviers
   « désactivés », donne l'impression d'un outil incomplet.
3. **La fourchette est toujours visible** : ARS et Administration la
   veulent en chiffres, l'élu·e en mots (« entre … et … »). Personne ne veut
   d'« écart au tendanciel » avant qu'un scénario existe : il vaut alors 0.
4. **Le périmètre se dit en clair** : infirmiers non projetés et grain
   départemental, en une ligne et pas en bouton grisé. Les termes
   « tendanciel », « flux », « pts » et « × 1,00 » sont du jargon pour
   l'élu·e.

## Désaccord : par où on entre
| Persona | Point d'entrée | Ce qu'il·elle refuse |
|---|---|---|
| ARS/DG | sa région, en départements, fiche ouverte | la vue France qui oblige à cliquer |
| Élu·e | « Quel est votre territoire ? » (commune) | la vue nationale et les paramètres d'emblée |
| Administration | la France, avec source, millésime, version du modèle et lien vers le backtest | tout chiffre sans fourchette ni source |

## Proposition de synthèse (à valider)
- **Ouverture** : la carte de France reste en fond, estompée. Au centre,
  un seul champ : « Quel territoire ? » (commune, département, région).
  En dessous, en petit, « ou voir la France ».
- **Après le choix** : on vole vers le territoire, le reste passe en gris
  (fait le 2026-11-14), et la fiche s'ouvre. Elle commence par la
  phrase-chiffre avec sa fourchette en mots, puis montre les 4 professions
  côte à côte.
- **Leviers** : repliés, derrière « Simuler une politique ». Retraite et
  régulation n'apparaissent pas tant qu'ils sont fermés.
- **Deux modes, un seul modèle** :
  - « Simple » (par défaut) : phrases, fourchette en mots ;
  - « Expert » : flux, écart en points, source et millésime, lien vers la
    méthode, export.
- **Compatible avec la commune** : la recherche et le grisage portent
  déjà sur « le territoire ouvert ». La commune s'y ajoute comme un
  niveau de plus.

## Inspiration CartoSanté (fond seulement, pas la forme)
D'après ce que je connais de CartoSanté (outil ATIH / ARS) : à vérifier
sur le site, non relu ici.
- **Entrée par le territoire et son maillage** : le choix porte sur la
  commune, le bassin de vie ou le territoire de vie-santé. Il conforte
  l'entrée « Quel territoire ? » et prépare le grain communal.
- **Portrait de territoire** : une fiche-type comparée au département, à
  la région et à la France, en quatre colonnes. On peut le reprendre dans
  la fiche sous forme de lignes « ce territoire / sa région / France ».
- **Indicateur d'accès (APL)**, plutôt qu'un effectif brut. Il rejoint la
  demande de densité de l'ARS et suppose des données de population.
- **À ne pas reprendre** : menus en cascade, formulaires avant toute carte,
  rapports PDF.

## ⚑ Ce qui pourrait rendre faux
- Les personas sont des agents qui ont lu le code ; ils ne viennent pas
  du terrain.
- L'ARS demande une densité pour 10 000 habitants. Elle exige une
  population par département et par année projetée, absente du serveur
  actuel.

## → Ce que ça change
`v2/prototype-carte/index.html` : accueil, mode Simple/Expert, leviers
repliés. Rien n'est construit tant que la synthèse n'est pas validée.

## ? À étudier ensuite
- Construire l'accueil de synthèse : ~30 à 45 min de Claude.
- Densité pour 10 000 habitants : il faut d'abord une source de projection
  de population (Omphale, Insee). ~1 h de Claude plus les données.
- Test avec un·e vrai·e utilisateur·rice par persona : temps humain.
