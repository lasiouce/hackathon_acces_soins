---
type: analysis
date: 2026-11-14
author: Claude
question: Peut-on passer l'écran de décision d'une page qu'on fait défiler à un logiciel « carte au centre », fluide, branché sur le jumeau ?
headline: "Oui. Carte MapLibre plein écran (localhost:8767) : un mouvement de levier recolore les 101 départements et met à jour la fiche en 53 ms (p50), 66 ms (p95), 87 ms (max) de réponse perçue, n = 35, sous la cible de 150 ms"
status: draft
professions: [sages-femmes, dentistes, pharmaciens, kines]
hypothesis: couche personas (écran de décision V2)
sources: [jumeau v2, app/assets/departements-avec-outre-mer.geojson, v2/data/processed/zonage_commune.parquet]
tags: [prototype, interface, direction-A, carte]
---

# Écran de décision V2 : la carte au centre

> **Headline :** réponse perçue (de l'événement `input` du curseur à
> l'image affichée, deux `requestAnimationFrame`) **p50 53 ms, p95 66 ms,
> max 87 ms, n = 35** (mesuré dans le navigateur intégré, 1440 × 900,
> kinés, Puy-de-Dôme ouvert, 30 valeurs espacées de 250 ms puis une rafale
> de 25 valeurs à 16 ms). Le jumeau compte pour ~24 ms.

## Ce qui a été construit
- `v2/prototype-carte/server.py` importe `v2/prototype/server.py` sans le
  modifier (modèles, bornes des quotas [0,7 ; 1,5], leviers suspendus).
  Deux routes ajoutées :
  - `/geo` : contours départementaux, coordonnées arrondies à 1e-3°, gzip ;
  - `/api/carte` : effectif libéral 2026 (observé, origine 2026) et 2050,
    tendanciel et scénario, pour les 101 départements, en un appel ;
    agrégé par `np.bincount` (546 ms → ~24 ms, mesuré).
- `v2/prototype-carte/index.html` : carte plein écran, l'écran ne défile
  pas. Par-dessus : recherche (région, département ; `/` pour y aller ;
  la carte s'envole vers le territoire), sélecteur de profession (une
  couleur fixe par profession ; infirmiers grisés avec la raison), panneau
  de leviers repliable, légende, zoom.
- Fiche flottante au clic : effectif 2026 et 2050, écart au tendanciel,
  fourchette en hachures, décomposition de l'écart par flux, zonage.
  Chiffres animés (280 ms, ease-out).
- Actions : comparer (bandeau de 4 territoires, recalculé avec les
  leviers), enregistrer le scénario (état complet dans l'URL, lien copié),
  exporter la fiche (CSV).
- Leviers retraite et régulation désactivés, raison affichée (seconde
  revue, défauts 1 et 2). Le serveur les refuse toujours (400).

## Choix de sémiologie
- Gamme divergente ocre ↔ bleu encre, sans rouge ni vert.
- « Évolution 2026 → 2050 » est lue **en points d'écart à l'évolution
  nationale** : en tendanciel, tous les départements croissent pour les
  kinés (+20 % à +121 %, national +58 %) ; centrée sur 0, la carte était
  monochrome. Lexique : « au-dessus / en dessous de la moyenne ».
- « Écart au tendanciel » : paliers fixes ±1/3/8 % tant que l'écart est
  faible, élargis par paliers ronds sinon (quotas ×1,48 → ≈ +27 % partout).

## Retour UAT (2026-11-14) : zoom régions / départements, cases plus grandes
- Limites régionales tracées en trait sombre épais dès la vue France,
  dérivées côté serveur des contours départementaux (`/geo-regions` :
  arêtes partagées par deux régions différentes ; aucune géométrie
  externe ajoutée).
- Clic à deux temps : le premier clic sur un département, en vue France,
  ouvre et cadre sa **région** (fiche régionale) ; le clic suivant ouvre
  le **département**. Maj + clic va directement au département. Rappel
  dans la légende.
- Cases plus grandes : texte de base 15 px, leviers 336 px, fiche 432 px,
  courbe 180 px de haut, chiffres clés 24 px, contrôles 48 px.
- Latence **non re-mesurée** après ce changement : le volet du navigateur
  était masqué (images non rendues). Le chemin du recalcul est inchangé ;
  seule une couche de lignes statique s'ajoute.

## Retour UAT n° 2 : vue France par régions ARS
- Sous le zoom 6,3, la carte colore les **18 régions** (agrégat des
  départements) au lieu des 101 départements. Les limites départementales
  sont masquées, et les limites régionales ont un liseré clair de 5 à 7 px
  sous un trait sombre, ce qui écarte visuellement les régions.
- Une région ouverte (clic ou recherche) montre ses départements même en
  vue large. À partir du zoom 6,3, tous les départements apparaissent.
- Le survol en vue France affiche la région et son chiffre.
- Vérifié dans le navigateur : vue France en régions, clic → Auvergne-Rhône-Alpes
  en départements, avec sa fiche.

## Retour UAT n° 3 : DROM en encarts
- Guadeloupe, Martinique, Guyane, La Réunion et Mayotte sont déplacées
  côté serveur (`ENCARTS` dans `server.py`) en une colonne à l'ouest de la
  Bretagne, chacune remise à l'échelle (Guyane ×0,3, Mayotte ×1,6…).
  Positions schématiques, comme sur les cartes Insee ; le survol et la
  fiche donnent le vrai nom. La vue France les inclut.
- `/geo` n'est plus mis en cache (`no-cache`) pour que ces changements
  arrivent sans vider le cache.

## Retour UAT n° 4 : contraste du milieu de gamme
- Fond de mer #D5DADF (gris bleuté) au lieu de #E9EBE6 ; milieu de la
  gamme divergente #C4C2B8 (gris chaud) au lieu de #ECEDE8 : la classe
  « écart faible » se distingue du fond.
- Trait de côte et frontières tracés (arêtes d'un seul département, gris
  #5C6166) ; limites départementales visibles à 35 % en vue France.
- Vérifié dans le navigateur (kinés, vue France).

## Retour UAT n° 5 : région ouverte au premier plan
- Quand une région est ouverte, les départements des autres régions sont
  estompés (opacité 0,3, transition 350 ms), contours gardés. Pas de vrai
  flou : illisible et coûteux au rendu.
- Échap ou un clic hors de la carte ramènent à la vue France.
- Vérifié dans le navigateur : Auvergne-Rhône-Alpes ouverte, autres
  régions estompées ; Échap → vue France (zoom 5,2), aucune région ouverte.

## Retour UAT n° 6 : encarts de données plus grands
- Fiche min(520 px, 36 vw), chiffres clés 34 px, aucun texte sous 14 px,
  courbe 250 px, infobulle 15 px, leviers et légende 380 px, encarts de
  comparaison ≥ 190 px.
- Bouton A / A+ (×1,15 sur les panneaux), mémorisé dans l'URL (`z=1`).
- Vérifié dans le navigateur (Haute-Savoie, kinés, quotas ×1,10).

## Retour UAT n° 7 : fil d'Ariane
- Fil toujours visible sous la barre du haut : France › région ›
  département (la commune s'ajoutera comme un niveau de plus). Chaque
  niveau parent est cliquable ; le niveau courant est en gras.
- Échap ou Retour arrière (hors saisie) remonte d'un niveau ; le bouton
  précédent du navigateur fonctionne (`pushState` à chaque changement de
  territoire).
- Écran étroit (< 1200 px) : niveaux intermédiaires repliés en « … ».
- Vérifié dans le navigateur : Puy-de-Dôme → clic « Auvergne-Rhône-Alpes »
  → Retour arrière → France → précédent → Auvergne-Rhône-Alpes.

## Retour utilisateur·rice : dégradé continu
- Les 7 classes deviennent un dégradé continu : 7 couleurs (mêmes teintes
  ocre ↔ gris ↔ bleu) réparties de −B à +B, interpolées en RVB, bornées
  aux extrêmes (B = 30 pts en « évolution », palier adaptatif en « écart »).
- La légende devient une barre en dégradé avec 5 repères (−B, −B/2, 0,
  +B/2, +B). Vérifié dans le navigateur (Auvergne-Rhône-Alpes, kinés).
- Prix : un dégradé continu se lit moins précisément qu'une classe (Bertin :
  l'œil compare mal des teintes proches) ; le chiffre exact reste au survol.

## Retour utilisateur·rice : zoomer davantage, encarts plus grands
- Le panneau des leviers se replie dès qu'un territoire s'ouvre ; la
  marge gauche du cadrage passe de 410 à 150 px, celle de droite suit la
  largeur réelle de la fiche. Zoom maximal : 8,5 (région), 10 (département).
- Mesuré à 1440 × 900 : Auvergne-Rhône-Alpes au zoom 6,65 (avant ≈ 6,0),
  Puy-de-Dôme au zoom 8,33, le département remplit la zone libre.
- Fiche, légende, leviers, comparaison et infobulle agrandis ×1,15 par
  défaut (×1,32 avec A+) ; la barre du haut n'est pas agrandie pour ne pas
  couper les professions.
- Limite : dans le volet masqué du navigateur intégré, l'animation de vol
  ne progresse pas ; vérifié avec un cadrage sans animation.

## ⚑ Ce qui pourrait rendre faux
- Latence mesurée en localhost, une seule machine ; un serveur distant
  ajoute l'aller-retour réseau.
- La fourchette reste la pente nationale × horizon (méthode V1) appliquée
  à chaque département : non validée au département.
- Grain départemental seulement ; la recherche ne trouve pas encore les
  communes (message affiché).

## → Ce que ça change
Remplace `v2/prototype/` comme écran de démonstration. Lancement :
`uv run python v2/prototype-carte/server.py 8767` (entrée
`decision-carte` de `.claude/launch.json`).

## ? À étudier ensuite
- Grain communal : précalcul d'une grille (≈ 3 s par scénario aujourd'hui) — ~1 h Claude.
- Mode élu·e simplifié (masquer flux et fourchette) — ~30 min Claude.
- Fourchette départementale par backtest au département — ~1 h Claude + run.
