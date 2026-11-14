---
type: analysis
date: 2026-11-14
author: Claude (session axe 4)
question: Quel zonage conventionnel s'applique à chaque commune, par profession, et sous quel statut (remplacement seul, incitation, autre) ?
headline: "34 919 géocodes × 4 professions (communes COG 2026 + 45 arrondissements PLM) ; « remplacement seul » : 97 géocodes et 4,8 % de la population pour les dentistes (cité : 97 communes, ≈ 5 %), 27–28 % pour kinés et infirmiers, 12 % pour les SF"
status: done
professions: [sages-femmes, dentistes, kines, infirmiers]
hypothesis: module `regulation` du jumeau (liste de géocodes par profession)
sources: [CartoSanté TJS zonage_conv arm2026 (extrait 2026-11-14), Atlasanté uuid c987d0e2 (génération 2012), geo.api.gouv.fr (populations)]
tags: [data, axe4, zonage, regulation, commune]
---

# Axe 4 — Zonage conventionnel par commune × profession

> **Headline :** `v2/data/processed/zonage_commune.parquet` donne, pour 34 919 géocodes (communes COG 2026,
> Paris / Lyon / Marseille par arrondissement) et 4 professions, la classe ARS et le statut lu par le
> module `regulation`. Contrôle : les dentistes « non prioritaires » sont **97 géocodes, 4,8 % de la
> population**, contre 97 communes et ≈ 5 % cités par le mémoire EHESP 2025.

## Question
Le module `regulation` du jumeau lit une liste de géocodes par profession (décision « granularité », 2026-11-14).
Il faut la liste réelle, avec son millésime, et l'historique s'il existe.

## Result

**Millésime actuel** (CartoSanté, extrait 2026-11-14) — géocodes et part de la population :

| Profession | Remplacement seul | Incitation (très sous- / sous-dotée) | Autre | Non renseigné |
|---|---|---|---|---|
| Sages-femmes | 1 471 · 12,3 % | 11 862 · 17,4 % | 21 562 · 70,3 % | 24 (Guyane) |
| Dentistes | 97 · 4,8 % | 26 769 · 44,4 % | 8 027 · 50,8 % | 26 (La Réunion) |
| Kinés | 2 836 · 27,4 % | 18 840 · 29,8 % | 13 241 · 42,8 % | 2 |
| Infirmiers | 4 786 · 27,6 % | 5 690 · 15,3 % | 24 441 · 57,0 % | 2 |

- Kinés : deux régimes coexistent, 2 826 géocodes « non prioritaires » (nouveau zonage) et 10 « sur-dotés »
  (ancien). Dentistes : seul le nouveau zonage (« non prioritaire ») est servi.
- **Historique** (Atlasanté c987d0e2, génération 2012, métropole, IDE / MK / CD, pas de SF) : 36 700
  communes de l'époque. Remplacement seul : 3 135 communes (IDE), 547 (MK), 908 (CD).

**Contrôles contre des totaux connus** (mesurés) :
- Communes : 34 877 communes zonées = 34 969 communes du COG (geo.api.gouv.fr) − 92 des COM (975, 984, 986,
  987, 988, 989), hors champ. Avec PLM : 34 877 − 3 + 45 arrondissements = **34 919** ✔.
- Dentistes « non prioritaires » : **97 géocodes, 4,8 % de la population**, contre « 97 communes, environ 5 %
  de la population » (mémoire EHESP 2025, § 3.3.2, cité par [param-cd-regul-effet](../fiches/param-cd-regul-effet.md)) ✔.
- Génération 2012 : codes région d'avant 2016 (« 82 » = Rhône-Alpes) et 36 700 communes, cohérent avec un
  zonage antérieur aux fusions de communes nouvelles ; lu par l'axe 3 comme celui de 2012.

## How
- **Data :** service OGC TJS de CartoSanté, `GetData` sur `zonage_conv`, référentiel `arm2026`, attributs
  `z_sf`, `z_dent`, `z_kine`, `z_infi` (4 × ≈ 1,6 Mo XML), sources CNAMTS – ARS ; GeoJSON Atlasanté uuid
  c987d0e2 (6,4 Mo), licence « utilisation libre sous réserve de mentionner la source et la date de dernière
  mise à jour ». Bruts dans `v2/data/raw/zonage/`.
- **Method :** [`v2/data/build_zonage.py`](../../../data/build_zonage.py). Classe → statut : sur-dotée ou non
  prioritaire → `remplacement_seul` ; très sous- / sous-dotée → `incitation` ; le reste → `autre`.
- **Run :** `uv run python v2/data/build_zonage.py` (≈ 2 s).
- Les dates d'effet des règles qui s'attachent à ces statuts sont dans `v2/data/events.csv`
  (type `avenant_conventionnel`).

## ⚑ What could make it wrong
- **Le millésime actuel n'est pas daté.** CartoSanté renvoie aux arrêtés ARS sans servir leur date ; des
  régions peuvent être à des générations différentes (indice : les 10 communes kinés encore « sur-dotées »).
- **« Obligation d'exercice » n'est pas une classe.** L'avenant 7 des kinés ajoute une obligation pour les
  nouveaux conventionnés d'exercer en zone sous-dotée (fiche
  [param-mk-regul-effet](../fiches/param-mk-regul-effet.md)) ; aucune obligation équivalente n'a été trouvée
  pour les dentistes (recherche axe 4, 2026-11-14). Le modèle peut la lire comme « zones
  `incitation` de la profession » ; ce n'est pas un champ de la source.
- `incitation` regroupe très sous-dotée et sous-dotée ; les aides diffèrent selon la classe. La colonne
  `classe` garde le détail.
- L'historique n'a qu'une génération (2012). Les générations 2008–2011 et 2018–2023 manquent : un module qui
  bascule le zonage dans le temps doit le dire.
- Populations : geo.api.gouv.fr (dernier recensement légal), pas la population de l'année du zonage.

## → What it changes
- **Module `regulation` (axe 0) :** remplacer les zones illustratives de `v2/jumeau/check.py`
  (`zones = ["06", "13", …]`) par `zonage_commune.parquet` filtré sur `statut == 'remplacement_seul'`.
  L'état communal doit utiliser les mêmes géocodes (arrondissements PLM).
- **Axe 3 (E1, DiD infirmier) :** la génération 2012 est maintenant en table, au même format que l'actuelle.
- **Axe 1 (`param-cd-regul-effet`) :** la borne « 97 communes, ≈ 5 % » est confirmée sur la donnée.
- Fiches : `data-zonage-sf`, `-cd`, `-mk`, `-ide`.

## ? Next
| Item | Cost |
|---|---|
| Dater le zonage actuel par région (17 arrêtés ARS) | ~1 h |
| Chercher les générations 2018–2023 (data.gouv, ARS) pour un historique annuel | ~1 h, issue incertaine |
| Coder l'obligation d'exercice comme règle (profession, date, zones `incitation`) dans le module `regulation` | ~20 min, axe 0 |
