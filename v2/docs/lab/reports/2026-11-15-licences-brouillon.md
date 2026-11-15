---
date: 2026-11-15
type: analysis
status: brouillon — aucune décision prise, rien d'activé
headline: "14 tables LO 2.0 commitées, 5 tables ODbL non commitées ; recommandation : ODbL commitée avec NOTICE, code sous EUPL 1.2 (à trancher)"
author: session besoin-axe0-interface
---

# Licences : sources, tables ODbL, code (brouillon)

**Portée.** Rédaction seulement. Les deux entrées du registre § Open (« Licence des tables dérivées de jeux ODbL »,
« Conformité … licence du code ») restent ouvertes. `NOTICE.draft` et `LICENSE.draft` à la racine ne sont pas
activés : aucun outil ne lit un fichier `.draft`, GitHub n'affiche aucune licence tant que `LICENSE` n'existe pas.

**Statut des faits.** « Lue » = licence écrite dans le dépôt (manifeste, en-tête de script, exploration) d'après la
page source. « Non lue » = je ne l'ai pas vérifiée dans cette session ; la licence indiquée est la licence habituelle
du producteur, **à confirmer** sur la page du jeu avant de remplir `NOTICE`. Rien ici n'est un avis juridique.

## 1. Sources et licences

### 1a. Module de besoin (`v2/besoin/donnees/MANIFEST.md`) — licences lues

| Table(s) | Producteur, jeu | Licence | Commitée |
|---|---|---|---|
| `apl_commune`, `apl_parametres` | DREES, APL (jeu 530) | Licence Ouverte 2.0 (lue) | oui |
| `damir_profils`, `damir_vaccination`, `damir/index` | Assurance maladie, Open DAMIR | Licence Ouverte 2.0 (lue) | oui |
| `medic_vaccins` | Assurance maladie, Open Medic | Licence Ouverte 2.0 (lue) | oui |
| `iqvia_campagne`, `iqvia_quotidien`, `iqvia_regional` | IQVIA France, vaccination grippe, data.gouv.fr | Licence Ouverte 2.0 (lue) | oui |
| `distancier_vol_oiseau` | geo.api.gouv.fr, centres des communes | Licence Ouverte 2.0 (lue) | oui |
| `ameli_demographie`, `ameli_patientele`, `ameli_honoraires`, `ameli_pathologies_effectifs`, `ameli_pathologies_depenses` | CNAM, data.ameli.fr (API Opendatasoft) | **ODbL 1.0** (lue dans les métadonnées de l'API le 2026-11-15) | **non** (`v2/data/odbl/`, ignoré par git) |
| matrice de temps OSRM (axe M4, à venir) | OpenStreetMap / Geofabrik | **ODbL 1.0** (lue, [exploration](../explorations/2026-11-15-besoin-sources.md)) ; logiciel OSRM : BSD-2 (non lue) | pas encore produite |

### 1b. Socle (`v2/data/processed/MANIFEST.md`) — le manifeste renvoie à l'en-tête des scripts

Le manifeste ne porte pas de colonne licence ; les en-têtes des scripts nomment les sources, pas leur licence.

| Source (script) | Producteur | Licence | Statut |
|---|---|---|---|
| Démographie RPPS, SNDS IDE, BTS (`build_secteur`, `build_infirmiers`, `sante.load`) | DREES | Licence Ouverte 2.0 | non lue |
| Omphale 2022, grille de densité, RP (`sante.load`, `build_attributs`) | Insee | Licence Ouverte 2.0 | non lue |
| Effectifs communaux, zonage (`build_commune`, `build_flux`, `build_zonage`) | CartoSanté / Atlasanté (CNAM – ARS) ; zonage data.gouv | **non lue** — à vérifier en priorité : Atlasanté n'est pas sur data.gouv pour tous ses indicateurs | non lue |
| Annuaire Santé (`build_annuaire`, `build_pharmaciens`) | ANS | Licence Ouverte 2.0 | non lue |
| FINESS historique (`build_finess_histo`, `build_secteur`) | Ministère de la Santé, data.gouv | Licence Ouverte 2.0 | non lue |
| Contours (`prototype-carte/server.py /geo`) | IGN / geo.api.gouv | Licence Ouverte 2.0 | non lue |
| DSFR (`prototype-carte/dsfr/`) | SIG | Licence Etalab 2.0 + marque réservée à l'État (lue, README) | — |

Prix pour lever les « non lue » : ≈ 15 min de Claude (une page par jeu, colonne `licence` ajoutée à `manifest.py`).

## 2. Ce que les licences de données imposent

- **Licence Ouverte 2.0 (Etalab).** Réutilisation libre, y compris commerciale, sous une seule condition : la
  **paternité** (nommer la source et la date de dernière mise à jour). Compatible avec ODbL, CC-BY, OGL ; aucune
  clause de partage à l'identique. Rien n'interdit de la mêler à une base ODbL ou de la publier sous une autre licence.
- **ODbL 1.0.** Trois obligations à la redistribution d'une **base de données dérivée** :
  1. *attribuer* (mention de la base source et de l'ODbL) ;
  2. *partager à l'identique* : la base dérivée publiée reste sous ODbL (ou licence compatible déclarée) ;
  3. *garder ouvert* : pas de mesure technique qui empêche la réutilisation (ou une version sans cette mesure).
  Une **« œuvre produite »** (Produced Work : carte rendue, graphique, chiffre dans un rapport, réponse de l'API à une
  requête) n'est pas une base : elle peut porter toute licence, avec une simple mention « contient des données …
  sous ODbL ». La frontière est la question à poser pour chaque fichier.
- **Où tombent nos fichiers.**
  - `ameli_*.parquet` : extraction et agrégation d'une base → **base dérivée** → ODbL si publiée.
  - Matrice de temps OSRM commune × commune : base dérivée d'OSM → ODbL si publiée. Un indice M4 par commune
    calculé avec elle est plus discutable ; la position prudente de la communauté OSM (guides « Substantial »,
    « Collective Database ») le traite comme base dérivée s'il est redistribué en table.
  - Une table mêlant LO 2.0 et ODbL (p. ex. besoin M3 × APL) : la part ODbL contamine la table entière → ODbL.
  - La carte, les fiches, l'export PNG et les réponses JSON ponctuelles de l'API : œuvres produites → mention seule.
  - Un **export CSV complet** des valeurs ODbL (toutes communes) se rapproche d'une base dérivée → ODbL + mention.

## 3. Options pour les tables ODbL

| | A. Commiter sous ODbL | B. Script de reconstruction seulement (règle d'attente actuelle) |
|---|---|---|
| Ce qu'on fait | retirer `v2/data/odbl/` du `.gitignore` ; `v2/data/odbl/LICENSE` = texte ODbL 1.0 ; `NOTICE` racine ; colonne licence au manifeste (déjà là) | rien ; `ameli.py` reconstruit en ≈ 1 à 2 min (export parquet de l'API, mesuré à la construction, non revérifié) |
| Obligations | attribution CNAM / OSM, ODbL sur ces fichiers seulement, pas de DRM | attribution dans la carte et les exports seulement (œuvres produites) |
| Clone neuf | reproductible hors ligne, sommes de contrôle vérifiables | dépend de l'API data.ameli.fr au moment du clone ; le millésime peut changer sous nos pieds |
| Risque | mélange de licences dans `v2/data/` : un relecteur peut croire que tout `processed/` est ODbL ; il faut garder le répertoire séparé | reproductibilité exacte perdue si data.ameli.fr réécrit un jeu ; contradiction douce avec la décision « on commite les données traitées » (2026-11-14) |
| Mise en œuvre | ≈ 15 min de Claude | 0 min |
| Taille ajoutée | ≈ 11 M lignes au total ; octets non mesurés ici (à lire avec `du -sh v2/data/odbl`) | 0 |

**Recommandation : A**, conditionnée à deux choses : le répertoire `v2/data/odbl/` reste séparé et porte son propre
`LICENSE` ; la taille mesurée tient sous la limite GitHub (100 Mo par fichier). La décision du 2026-11-14 (« on
commite les données traitées ») et l'exigence de reproductibilité (backtest) penchent pour A ; ODbL est faite pour ce
cas. Ce qui ferait basculer vers B : un fichier > 100 Mo, ou un refus de toute clause share-alike dans le dépôt.

## 4. Options pour le code

| | EUPL 1.2 | MIT | Apache 2.0 |
|---|---|---|---|
| Type | copyleft faible, réseau inclus (art. 1 « distribution / communication » couvre la mise à disposition en ligne) | permissive | permissive, clause de brevets |
| Obligations | garder la licence et les mentions ; publier les modifications si on distribue ou **sert en ligne** une version modifiée ; licence compatible listée en annexe (GPL, AGPL, MPL, LGPL, EPL, CeCILL, OSL, CC-BY-SA, LiLiQ) | garder la mention de copyright et le texte | garder les mentions, signaler les fichiers modifiés, transmettre `NOTICE` |
| Juridiction | 23 langues officielles, droit de l'UE, recommandée par la DINUM pour les codes sources publics (liste des licences autorisées, décret 2017-638 : EUPL non listée par le décret mais admise par la doctrine DINUM — **non lu ici, à vérifier**) | US | US |
| Avec nos dépendances (pandas, numpy, scikit-learn : BSD ; DSFR : MIT pour le code) | compatible | compatible | compatible |
| Effet pour une ARS qui réutilise | doit republier ses modifications si elle sert la carte modifiée | aucune contrainte | aucune contrainte, protection brevets |

**Données vs code.** La licence du code ne s'applique pas aux données : LO 2.0 et ODbL suivent leurs fichiers.
`NOTICE` le dit explicitement. Aucune des trois licences de code n'entre en conflit avec ODbL (domaines distincts).

**Recommandation : EUPL 1.2**, pour un projet porté par le Ministère chargé de la santé (registre, levée DSFR du
2026-11-15) : licence de l'UE, en français, et copyleft réseau qui garde ouvertes les versions servies par d'autres
administrations. MIT si l'équipe veut la réutilisation la plus large sans condition. Apache 2.0 n'apporte rien ici
(pas de brevets en jeu).

## 5. Brouillons

- [`NOTICE.draft`](../../../../NOTICE.draft) : attributions par source, séparation code / données.
- [`LICENSE.draft`](../../../../LICENSE.draft) : en-tête EUPL 1.2 et renvoi au texte officiel (le texte intégral est à
  copier depuis `https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12` au moment d'activer,
  pour ne pas recopier de mémoire un texte juridique).
- Activer = renommer en `NOTICE` / `LICENSE` et compléter les « à confirmer ». Prix ≈ 10 min de Claude.

## TL;DR

- **Chiffre.** 14 tables LO 2.0 commitées, 5 tables ODbL non commitées, 1 matrice ODbL à venir ; 6 sources du socle
  à licence non lue.
- ⚑ Les licences du socle sont présumées, non lues ; CartoSanté / Atlasanté est la plus incertaine. La frontière
  base dérivée / œuvre produite pour l'indice M4 est interprétative.
- → `decisions.md` § Open (deux recommandations ajoutées, entrées non fermées) ; `.gitignore` et `v2/data/odbl/` si A.
- ? Lire les 6 licences du socle et ajouter la colonne `licence` au manifeste du socle (≈ 15 min) ; mesurer
  `du -sh v2/data/odbl` (≈ 1 min).
