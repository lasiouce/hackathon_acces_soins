"""Estimateurs du besoin derrière une interface commune, sur le modèle de sante.estimators et jumeau.module.

Un estimateur :
  name               clé du registre (M0, M1, …)
  norme              ce que « besoin » veut dire pour lui : c'est un choix déclaré, pas une mesure
  assumptions        hypothèses en mots simples
  params             tuple de jumeau.module.Param : valeur, unité, source, millésime, statut (mesuré / sourcé /
                     supposé / non mesurable) ; value None = ajusté par fit()
  fit(pop, etat, ref)  calibre ce qui doit l'être (année de référence `ref`, en général 2026)
  predict(pop, etat, years) -> Cube B[profession, territoire, année] en ETP-équivalents

`etat` est un dict année -> jumeau.state.State (la trajectoire de l'offre). Un estimateur le lit, ne l'écrit jamais.
Le besoin peut être demandé pour une profession source (médecine générale, spécialistes) : c'est permis ; seul
l'indice de couverture leur est interdit (couverture.SANS_COUVERTURE, décision O2).

Ajouter un estimateur = déposer un fichier décoré par @register dans besoin/estimateurs/ ou dans un dossier passé
à discover(). Aucun autre fichier n'est modifié ; la sortie le choisit par nom.
"""
import importlib
import importlib.util
import pkgutil
import sys
from pathlib import Path

from jumeau.module import Param

from besoin.cube import Cube, Population

PROFESSIONS = ("sages-femmes", "dentistes", "pharmaciens", "kines", "infirmiers")   # sorties (couverture)
SOURCES = ("medecine-generale", "specialistes")                                       # sources de transferts seulement


class NeedEstimator:
    name = ""
    norme = ""
    assumptions = ""
    params: tuple = ()
    professions: tuple = PROFESSIONS + SOURCES

    def fit(self, pop: Population, etat: dict | None = None, ref: int = 2026) -> "NeedEstimator":
        self.ref = ref
        return self

    def predict(self, pop: Population, etat: dict | None = None, years=None) -> Cube:
        raise NotImplementedError

    @classmethod
    def param(cls, name) -> Param:
        return next(p for p in cls.params if p.name == name)

    def hypotheses(self) -> list[dict]:
        """Paramètres avec leur statut, pour la sortie : aucun nombre sans étiquette."""
        return [dict(name=p.name, value=p.value, unit=p.unit, source=p.source, vintage=p.vintage, status=p.status,
                     doc=p.doc) for p in self.params]


REGISTRY: dict[str, type] = {}


def register(cls):
    if cls.name in REGISTRY and REGISTRY[cls.name] is not cls:
        raise ValueError(f"estimateur {cls.name!r} déjà enregistré")
    REGISTRY[cls.name] = cls
    return cls


def discover(*paths) -> dict[str, type]:
    """Importe besoin/estimateurs/ puis chaque fichier .py des dossiers donnés ; renvoie le registre."""
    import besoin.estimateurs as builtin
    for m in pkgutil.iter_modules(builtin.__path__):
        importlib.import_module(f"besoin.estimateurs.{m.name}")
    for p in paths:
        for f in sorted(Path(p).glob("*.py")):
            name = f"besoin_plugin_{f.stem}"
            if name not in sys.modules:
                spec = importlib.util.spec_from_file_location(name, f)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[name] = mod
                spec.loader.exec_module(mod)
    return REGISTRY
