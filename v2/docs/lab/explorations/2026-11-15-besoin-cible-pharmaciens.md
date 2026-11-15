---
type: exploration
date: 2026-11-15
author: session besoin-cible-pharmaciens
question: Existe-t-il une cible de validation externe ouverte pour M4 (2SFCA) appliqué aux pharmaciens d'officine ?
headline: "Oui : l'archive DREES « APL Méthode initiale V0 » (jeu 530, Licence Ouverte 2.0, 4,1 Mo) contient une APL aux pharmacies libérales par commune, 2010 et 2013 (36 747 lignes, offre = nombre d'officines sans ETP, paliers 0–5 / 5–10 / 10–15 min à 1 / 0,3 / 0,1) ; l'IRDES QES 308 n'a pas d'APL des pharmacies (distance Insee seulement) ; l'Insee donne le temps à la pharmacie la plus proche au carreau de 200 m (Licence Ouverte) : cible secondaire d'une autre grandeur"
professions: [pharmaciens]
tags: [besoin, M4, 2SFCA, APL, pharmaciens, validation, sources]
---

# Cible de validation externe pour M4 pharmaciens

Provenance : (s) sourcé (fichier ou page lus), (d) dérivé, (h) supposé.

## Ce qui existe

### (a) DREES, APL « Méthode initiale V0 2010, 2013 » — **contient les pharmacies**
- Fichier : `Méthode initiale Version 0 - 2010, 2013.7z`, 4 096 456 octets
  (en-tête HTTP lu) (s), pièce jointe du jeu 530
  (`…/530_l-accessibilite-potentielle-localisee-apl/attachments/methode_initiale_version_0_2010_2013_7z`).
  Licence Ouverte 2.0 (métadonnées du jeu) (s).
- Contenu (listé, rien exécuté) (s) : 11 CSV pour 10 professions libérales
  (généralistes, et généralistes de moins de 40 ans à part ; CD, gynécologues,
  IDE, MK, ophtalmologues, **pharmaciennes**, psychiatres, pédiatres, SF),
  plus `Notice APL.pdf` et trois liens (ER 795, DT 124, ER 970).
- Fichier pharmacies : `…aux pharmaciennes libérales.csv`, 36 747 lignes (s),
  grain **commune** (clé `code_nom`, code Insee de l'époque). Colonnes : APL
  2010 ancien distancier, APL 2010 nouveau distancier, APL 2013 nouveau
  distancier (s).
- Paramètres (Notice) (s) : la méthode « a également été implémentée pour les
  pharmacies » ; **offre = nombre d'officines, sans ETP** (pas d'activité).
  Paliers : poids 1 de 0 à 5 min, 0,3 de 5 à 10, 0,1 de 10 à 15, 0 au-delà.
  Ils sont **empruntés** aux autres professions : la Notice précise que les
  flux de patients manquent pour les pharmacies.
- Ordre de grandeur 2010 (Notice) (s) : moyenne 36,1, médiane 36,6, Q1 29,0 ;
  unité probablement officines pour 100 000 habitants (d, non écrite pour les
  pharmacies).
- Les versions V1 (2015–2016) et V2 (2015–2022) n'ont pas de fichier libellé
  pharmacies (liste des pièces jointes) (s) ; archives V1/V2 non ouvertes.

Les valeurs d'APL n'ont pas été lues (règle de gel : seules la liste des
fichiers et la Notice l'ont été). L'archive reste dans le bac à sable, hors
dépôt.

### (b) IRDES, Bonal, Padilla, Chevillard, Lucas-Gabrielli, QES n° 308 (mai 2026)
- **Pas d'APL des pharmacies** (prémisse corrigée) (s). L'annexe 1 utilise la
  « distance à la pharmacie la plus proche », Insee 2023, en minutes, par
  commune. L'APL ne sert qu'aux généralistes (DREES), IDE et MK.
- Typologie en 7 classes (ACP puis CAH), ~35 000 communes, hors Mayotte (s).
- Fichier communal de la typologie : non trouvé ; licence non écrite (s).
  Utilisable au mieux comme repère qualitatif, pas comme cible de M4.

### (c) Insee, « Localisation et accès de la population aux équipements »
- data.gouv.fr `67fe0fe2423db9c4a05d8ced` (s) : carreau de **200 m**, Parquet
  partitionné par région (~30 fichiers de 39,5 Mo à 1,8 Go), Licence Ouverte
  2.0, mise à jour du 18/08/2026 (s). Millésime BPE et Filosofi non écrits
  sur la page (s).
- Temps et distance routiers en voiture, distancier Metric-OSRM (s) ; origine
  au carreau peuplé (d, non écrit). Présence de D307 (pharmacie) à confirmer
  dans le dictionnaire (non lu).
- Grandeur différente : un temps au plus proche n'est pas une APL (pas
  d'offre rapportée à la demande). Il ne valide que la **brique distancier**
  de M4.

## Ce qui ne marche pas
- La cible V0 a 13 ans : il faut l'offre 2010/2013 (officines par commune) et
  la population de l'époque, que le jumeau n'a pas en état historique pour les
  pharmacies. Sources candidates (non vérifiées) : BPE 2013 (D301 pharmacie
  dans l'ancienne nomenclature) ou extraction FINESS archivée.
- Paliers V0 ≠ paliers 2022+. Le test vérifie la **mécanique** 2SFCA sur les
  pharmacies, pas les paramètres que le jumeau utilisera en projection.
- Distancier V0 (« nouveau distancier » DREES de 2013) non ouvert : même
  menace que P-B4, plus forte avec des paliers à 5 min.

## Recommandation
Cible principale : **APL V0 pharmacies 2013** (nouveau distancier), avec
2010 nouveau distancier en reproduction secondaire. Protocole
[P-B4-PH](../../../validation/preregistered/2026-11-15-besoin-p-b4-ph-apl-v0.md)
rédigé, **non gelé**. Contrôle secondaire, non décisif : temps OSRM du jumeau
contre le temps Insee à la pharmacie la plus proche.
