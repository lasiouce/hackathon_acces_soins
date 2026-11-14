# Prétirages v2 (format arXiv)

Chaque axe de recherche produit un prétirage : `v2/papers/axeN-<sujet>/main.tex` (+ `refs.bib`, `figures/`).

- Partir de `template/` : copier `main.tex` et `refs.bib` dans le dossier de l'axe. Le préambule commun
  (`template/preamble.tex`) est inclus et n'est pas modifié par un axe.
- Source TeX autonome, compilable en pdfLaTeX : c'est ce qu'arXiv attend. Pas de dépendance hors TeX Live.
- Langue : français, avec un résumé anglais.
- Chaque nombre porte sa provenance : `\mesure`, `\derive` ou `\suppose`, et vient d'un rapport de `v2/docs/lab/reports/`.
- Seules les références lues et vérifiées entrent dans `refs.bib`. Aucune citation inventée.
- Compilation : `tectonic main.tex` ou `latexmk -pdf main.tex` (aucun moteur TeX n'est installé sur cette machine
  au 2026-11-14 : `brew install tectonic`, à valider).
