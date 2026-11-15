"""Module de besoin de soins (axe 0 du plan du 2026-11-15).

Le besoin n'est pas un flux sur les effectifs : il est **lu** sur une trajectoire du jumeau, jamais écrit dedans.
  cube.py         Cube [profession, territoire, année] et Population [territoire, année, sexe, âge] (Omphale)
  estimateurs.py  interface NeedEstimator (fit / predict / assumptions), registre, discover()
  estimateurs/    un fichier par estimateur (m0.py, …) ; en ajouter un ne modifie aucun autre fichier
  couverture.py   offre (ETP) lue dans les états, indice C indexé à l'année de référence, agrégé par sommes
  transferts.py   opérateur de transfert s(t)·a, k, m, sur B seulement
  sortie.py       sortie prête pour l'API : besoin, couverture, couverture_base

Règle O2 (registre, 2026-11-15) : la médecine générale et les spécialistes peuvent être des professions **source**
de transferts ; aucun indice de couverture n'est jamais produit pour eux (couverture.SANS_COUVERTURE).

Tests (racine du dépôt) : PYTHONPATH=v2 uv run python -m besoin.tests
"""
