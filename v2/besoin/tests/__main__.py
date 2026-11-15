"""Critères d'acceptation de l'axe 0 du module de besoin, écrits pour pouvoir échouer.

Run (racine du dépôt) : PYTHONPATH=v2 uv run python -m besoin.tests   -> v2/artifacts/besoin_a0/results.json
Code de sortie 1 si un critère échoue. Chaque critère porte un **contrôle** : la même mesure sur une entrée
volontairement fausse, qui doit dépasser la tolérance (preuve que le test sait échouer).

  B1 M0            C = densité / densité₂₀₂₆ à 10⁻⁹, densité recalculée par un chemin pandas indépendant, 5 professions
  B2 transferts 0  effectifs du jumeau inchangés bit à bit (empreinte de N) ; s ≡ 0 ⇒ B, C, densités identiques
  B3 additivité    Σ_communes B = B_dep = … = B_nat à 10⁻⁹ relatif ; C régional = rapport des sommes
  B4 conservation  ΣB' − ΣB = s·a·B_A·(k−1) + m à 10⁻⁶ ETP, deux transferts, k ≠ 1, μ > 0
  B5 latence       besoin_api au département, une profession, 2026–2050 : 95ᵉ centile < 5 ms, n ≥ 30
  B6 plug-in       estimateur déposé hors du paquet, servi par nom ; aucun fichier de v2/besoin modifié
  B7 O2            aucun indice de couverture pour la MG ni les spécialistes, par aucun chemin
`jumeau.check` (18/18) se lance à part : PYTHONPATH=v2 uv run python -m jumeau.check
"""
import json
import sys
from pathlib import Path

import importlib
import pkgutil

import besoin.tests
from besoin.tests.criteres import CRITERES as _AXE0, RESULTS

# critères de l'axe 0 puis ceux de chaque module besoin/tests/criteres_*.py (un par estimateur ou protocole)
CRITERES = list(_AXE0) + [f for m in sorted(pkgutil.iter_modules(besoin.tests.__path__), key=lambda m: m.name)
                          if m.name.startswith("criteres_")
                          for f in importlib.import_module(f"besoin.tests.{m.name}").CRITERES]

OUT = Path("v2/artifacts/besoin_a0")


def main():
    for f in CRITERES:
        try:
            f()
        except Exception as e:                       # un critère qui plante est un échec, pas un arrêt
            RESULTS.append(dict(id=f.__name__, critere="exception", mesure=f"{type(e).__name__}: {e}"[:300], ok=False))
            print(f"ÉCHEC {f.__name__} : {type(e).__name__}: {e}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(RESULTS, ensure_ascii=False, indent=1, default=str))
    failed = [r["id"] for r in RESULTS if not r["ok"]]
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} ; échecs :", failed or "aucun")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
