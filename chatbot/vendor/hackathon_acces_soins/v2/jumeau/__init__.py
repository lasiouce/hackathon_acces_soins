"""Jumeau numérique de l'offre de soins (axe 0, v2/ROADMAP.md).

Trois composants :
  state.py     l'état N[cellule = (profession, secteur, territoire, sexe), âge] + le vivier en formation
  module.py    le contrat des modules de flux (plug-ins) : paramètres sourcés, flux typés, registre
  scenario.py  le scénario : surcharges de paramètres + événements datés avec sélecteur
engine.py fait avancer l'état année par année ; estimators.py branche le jumeau sur le banc v1.
Lancer depuis la racine du dépôt : PYTHONPATH=v2 uv run python -m jumeau.check
"""
