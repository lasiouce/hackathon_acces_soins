---
type: analysis
date: 2026-11-15
author: session besoin-derivation
question: "La mécanique M4 (2SFCA à paliers, paramètres publiés de la V0) reproduit-elle l'APL DREES V0 2013 aux pharmacies, commune par commune ? (P-B4-PH, protocole gelé)"
headline: "(passage non lancé : écarts au protocole écrits avant calcul)"
status: draft
professions: [pharmaciens]
hypothesis: H-B4-PH ; test P-B4-PH
sources: [APL DREES Méthode initiale V0 2010/2013 (jeu 530, LO 2.0), FINESS historique 2004–2025 (officines, état au 31/12), Insee séries historiques de population (PMUN2008, PMUN2011), OSRM sur OpenStreetMap (ODbL), table de passage communale du dépôt]
tags: [validation, besoin, 2SFCA, APL, pharmaciens, P-B4-PH]
---

# P-B4-PH : reproduction de l'APL V0 aux pharmacies

## Protocole appliqué
`v2/validation/preregistered/2026-11-15-besoin-p-b4-ph-apl-v0.md`, gelé et horodaté (FreeTSA et DigiCert, 04:09 UTC).

## Écarts au protocole, écrits avant tout calcul
Au moment d'écrire ces écarts, l'auteur avait vu :
- l'en-tête et **4 lignes** du fichier cible ; le protocole autorise la lecture après le jeton ;
- les totaux nationaux d'officines FINESS 2010 et 2013 (23 032 et 22 793) ;
- le format de la table OSRM.

Aucune APL n'avait été calculée.

1. **Offre.** Le protocole prévoit la BPE 2013 de l'Insee, absente du disque. On utilise à la place **FINESS
   historique** (catégorie officine, état au 31 décembre 2013, et au 31 décembre 2010 pour la variante 2010), déjà
   traité dans `v2/data/processed/finess_commune_annee.parquet`. C'est une autre source de comptage d'officines, à
   écrire comme menace. La sensibilité à la BPE n'est pas faite.
2. **Géographie.** Tout est ramené à la géographie communale 2026 par `passage_commune.parquet`.
   - Une commune de la cible n'est gardée que si son code 2013 correspond à un seul code 2026, **et** si aucun autre
     code de la cible ne se rattache à ce même code 2026 (appariement un à un ; les fusions sont exclues, comme le
     prévoit le protocole).
   - L'offre et la population, elles, sont agrégées en géographie 2026, y compris les communes fusionnées, pour ne
     perdre aucune officine dans l'étape 1.
   - Les codes de la cible sont lus sur les 5 premiers caractères du champ « Commune » (« 52017_Arc-en-Barrois »).
3. **Population.** Les populations municipales RP 2011 (pour 2013) et RP 2008 (pour 2010) viennent des séries
   historiques de l'Insee (géographie 2025), passées en 2026. La population est **brute**, comme le prévoit le
   protocole.
4. **Distancier.**
   - On utilise la table OSRM de l'axe 2 (M4) : paires à 30 min au plus, centres de communes geo.api 2026, voiture,
     sans trafic.
   - Elle est **symétrisée** (t_ij = t_ji, une paire stockée une fois).
   - Le temps d'une commune vers elle-même vaut 0.
5. **Paliers V0** (Notice, sourcés par le protocole) : 1 pour t < 5 min, 0,3 pour 5 ≤ t < 10, 0,1 pour 10 ≤ t < 15,
   0 au-delà. Les bornes sont **exclusives à droite**.
6. **Champ des références naïves.**
   - N2 au bassin de vie : on utilise les **BV2022**, présents dans la table de passage, au lieu des BV2012 du
     protocole, qui ne sont pas sur disque.
   - N1 et N2 donnent des officines pour 100 000 habitants, comme M4.
7. **Bootstrap** : 2 000 tirages de départements avec remise (sur le département 2026), graine 20261115, IC percentile.
   L'erreur médiane EM est calculée sur `APL > 0`.
8. **Métropole seule**, puisque la table OSRM est métropolitaine. Les DOM de la cible sont exclus.
9. **Valeurs « ND ».** Ajouté après une erreur de lecture, avant tout calcul d'APL. La cible contient des valeurs
   « ND » (non disponible) : elles sont traitées comme manquantes, et les communes concernées sortent du champ de
   l'année en question.

## Résultat
*(à compléter après le passage)*
