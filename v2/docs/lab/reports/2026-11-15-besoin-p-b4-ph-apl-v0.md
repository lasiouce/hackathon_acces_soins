---
type: analysis
date: 2026-11-15
author: session besoin-derivation
question: "La mécanique M4 (2SFCA à paliers, paramètres publiés de la V0) reproduit-elle l'APL DREES V0 2013 aux pharmacies, commune par commune ? (P-B4-PH, protocole gelé)"
headline: "P-B4-PH échoue : M4 contre APL V0 2013 aux pharmacies, Spearman 0,72 [0,71 ; 0,74] (seuil 0,90), erreur médiane 33 % (seuil 15 %), gain sur la meilleure densité naïve +0,14 [+0,12 ; +0,16] ; niveau moyen reproduit (22,1 contre 22,5 officines pour 100 000 hab.) ; M4 pharmaciens reste un indice maison"
status: done
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
Commande : `uv run --with scipy --with python-calamine --with pyarrow python v2/besoin/validation/pb4ph.py --cible <csv V0 pharmacies> --raw <v2/data/raw/insee>`.
Sortie : `v2/besoin/validation/out/pb4ph.json`. Graine 20261115, B = 2 000.

> **Headline :** la mécanique 2SFCA avec les paliers V0 **ne reproduit pas** l'APL V0 des pharmacies, commune par
> commune. Le niveau moyen est bien retrouvé, mais pas le classement. M4 pharmaciens reste un **indice maison**.
> Il bat nettement la densité simple.

| Statistique (2013, 33 897 communes) | Valeur | Seuil | Verdict |
|---|---|---|---|
| Spearman M4–APL | **0,723** [0,707 ; 0,738] (m) | ≥ 0,90 | échoue |
| Erreur relative médiane (APL > 0) | **33,1 %** [31,3 ; 35,3] (m) | ≤ 15 % | échoue |
| Spearman N1 (densité de la commune) | 0,584 (m) | — | — |
| Spearman N2 (densité du bassin de vie 2022) | 0,158 (m) | — | — |
| Gain G = ρ_M4 − max(ρ_N1, ρ_N2) | **+0,139** [+0,121 ; +0,158] (m) | ≥ 0,05, IC > 0 | passe |
| Conservation Σ P·A = Σ S | écart relatif 0,0 (m) | < 10⁻⁹ | passe (bloquant) |
| Niveau moyen, officines pour 100 000 hab. | M4 22,1 ; APL 22,5 (m) | — | — |

- **Par taille de commune (2013)** : Spearman 0,63 (< 1 000 hab.), 0,77 (1 000 à 10 000), 0,67 (> 10 000) (m).
- **2010** (rapporté, non décisif) : Spearman 0,721, erreur médiane 32,8 %, G +0,135 (m). Même verdict.
- Les 20 communes les plus écartées sont dans `pb4ph.json`.

**Lecture.**
- C'est le même profil que P-B4 sur les quatre autres professions (Spearman de 0,71 à 0,76) : le niveau est bon, le
  classement fin ne l'est pas.
- Ici, l'offre est un simple **nombre d'officines**, sans conversion en ETP. L'activité non ouverte de la DREES ne peut
  donc pas être la cause principale de l'écart.
- Restent les **paliers courts** (5 min) face aux écarts de distancier : centres geo.api contre chefs-lieux et Metric
  2013, contre OSM 2025. Restent aussi la **source de l'offre** (FINESS contre SNIIR-AM) et la géographie 2013 ramenée
  à 2026.
- La faiblesse de N2 (0,16) vient probablement de la taille des bassins de vie 2022 face à des paliers de 15 min :
  c'est une hypothèse.

## Comment
- **Données :** APL V0 2013 (DREES, LO 2.0) ; FINESS officines au 31/12/2013 ; RP 2011 ; OSRM sur OSM (ODbL),
  paires à 30 min au plus ; BV2022.
- **Méthode :** 2SFCA aux paliers V0 (1 / 0,3 / 0,1 sur 0–5 / 5–10 / 10–15 min), population brute, bootstrap des
  départements. Script : `v2/besoin/validation/pb4ph.py`.

## ⚑ Ce qui pourrait rendre ceci faux
- **FINESS au lieu de la BPE** (écart 1) : la sensibilité à la BPE n'est pas faite.
- **Distancier OSM 2025** et centres geo.api au lieu de Metric 2013 et des chefs-lieux. À 5 min, chaque minute compte.
- **Appariement un à un des communes** : les communes fusionnées sont exclues de la comparaison, pas de l'offre.
- **Seuils supposés** (repris de P-B4).

## → Ce que ça change
- **M4** n'est jamais présenté comme « l'APL », ni pour les pharmaciens ni pour les quatre autres professions. C'est un
  indice d'accessibilité maison, meilleur que la densité simple (G > 0 partout).
- La suite naturelle serait un test du distancier seul : le temps OSRM vers l'officine la plus proche, comparé au
  temps Insee (carreaux). Le protocole le prévoit en « rapporté, non décisif », et il n'est pas fait ici.

## ? Suite
| Point | Coût |
|---|---|
| Contrôle du distancier : OSRM contre le temps Insee vers la pharmacie la plus proche (BPE, carreaux 200 m ; 28,7 Go, téléchargement) | ~45 min + téléchargement |
| Sensibilité de l'offre : BPE 2013 au lieu de FINESS | ~20 min + téléchargement |
| Fusionner la table OSRM et ce passage dans un M4 servi pour les pharmaciens (indice maison, à part) | ~30 min |
