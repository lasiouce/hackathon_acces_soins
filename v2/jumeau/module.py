"""Contrat des modules de flux.

Un module :
  name, order        nom unique (clé du registre et des paramètres) ; rang d'application dans l'année
  params             tuple de Param : chaque paramètre a valeur, unité, source, millésime et statut
  needs, produces    noms des flux qu'il lit dans l'année (ctx.delta) et qu'il écrit ; build() vérifie
                     que chaque besoin est produit par un module placé avant lui, run() que chaque flux
                     rendu est déclaré. Par défaut produces = (name,).
  fit(hist)          optionnel : calibre ses paramètres sur l'historique observé (années <= origine)
  prepare(state, scn) optionnel : complète l'état avant le run (ex. secteur de destination vide)
  begin(state, ctx)  optionnel : remet son état interne à zéro au début de chaque run
  step(state, ctx)   lit l'état, renvoie une liste de flux typés ; ne modifie jamais l'état lui-même

Le moteur applique les flux d'un module avant d'appeler le suivant (séparation d'opérateurs) et
tient le registre de chaque flux, par cellule. Tout ce qui entre ou sort de N passe par un compte
nommé, d'où une conservation vérifiable. Types de flux :
  Shift  vieillissement le long de l'axe âge (fraction frac d'une tranche passe à la suivante)
  Rate   N <- factor * N ; (1 - factor) * N part vers le compte `to` (sorties, décès…)
  Add    N <- N + amount, pris sur le compte `src` (entrées, diplômés…)
  Move   transfert entre cellules (secteur, territoire), amount retiré de src et ajouté à dst
  Pool   remplace le vivier en formation ; `out` crédite des comptes (abandons, diplômés)

Une méthode qui n'est pas un stock-flux (microsimulation, modèle bayésien…) est un module comme
un autre : elle tire ou estime ce qu'elle veut dans fit/step et rend ses résultats sous forme de
flux (agrégés par cellule). Elle peut aussi remplacer toute la composition derrière l'interface
Estimator (estimators.py).

Ajouter un module = déposer un fichier décoré par @register dans jumeau/modules/ ou dans un dossier
passé à discover(). Aucun autre fichier n'est modifié ; le scénario choisit la composition par nom.
"""
import importlib.util
import pkgutil
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

STATUTS = ("mesuré", "sourcé", "supposé", "non mesurable")


@dataclass(frozen=True)
class Param:
    name: str
    value: object          # None = ajusté sur les données par fit()
    unit: str
    source: str
    vintage: str
    status: str
    doc: str = ""
    bounds: tuple | None = None    # (min, max) admissibles ; Scenario.validate refuse une valeur hors plage
    famille: str = ""              # levier : former, attirer, installer, retenir ("" = paramètre technique, pas un levier)

    def __post_init__(self):
        if self.status not in STATUTS:
            raise ValueError(f"{self.name}: statut {self.status!r} hors {STATUTS}")


@dataclass
class Shift:
    name: str
    frac: float


@dataclass
class Rate:
    name: str
    factor: np.ndarray     # [cellule, âge]
    to: str


@dataclass
class Add:
    name: str
    amount: np.ndarray     # [cellule, âge]
    src: str


@dataclass
class Move:
    name: str
    amount: np.ndarray     # [len(src), âge]
    src: np.ndarray        # indices de cellules
    dst: np.ndarray


@dataclass
class Pool:
    name: str
    new: object            # pd.Series (profession, année d'étude) -> effectif
    out: dict              # compte -> pd.Series par profession


class Module:
    name = ""
    order = 50
    params: tuple = ()
    needs: tuple = ()
    optional: tuple = ()           # flux lus s'ils sont produits par la composition (0 sinon)
    produces: tuple | None = None
    doc = ""

    @classmethod
    def outputs(cls) -> tuple:
        return cls.produces if cls.produces is not None else (cls.name,)

    def fit(self, hist) -> None:
        pass

    def prepare(self, state, scenario):
        """Optionnel : rend l'état dont le module a besoin (ex. cellules d'un secteur de destination). Par défaut inchangé."""
        return state

    def begin(self, state, ctx) -> None:
        pass

    def step(self, state, ctx) -> list:
        raise NotImplementedError

    @classmethod
    def param(cls, name) -> Param:
        return next(p for p in cls.params if p.name == name)


def par_profession(value, professions) -> np.ndarray:
    """Valeur d'un paramètre par profession : scalaire, ou dict {profession: valeur} avec "*" pour les autres.
    Une clé couvre aussi ses variantes (« infirmiers » couvre « infirmiers-liberaux »). Sans clé ni "*" : erreur."""
    uniq, inv = np.unique(np.asarray(list(professions), dtype=object).astype(str), return_inverse=True)
    if not isinstance(value, dict):
        return np.full(len(inv), float(value))
    out = []
    for p in uniq:                                       # une recherche par profession distincte, pas par cellule
        keys = [k for k in value if k != "*" and (p == k or p.startswith(k + "-"))]
        if keys:
            out.append(float(value[max(keys, key=len)]))
        elif "*" in value:
            out.append(float(value["*"]))
        else:
            raise KeyError(f"pas de valeur pour la profession {p!r} (clés : {sorted(value)})")
    return np.array(out)[inv]


REGISTRY: dict[str, type] = {}


def register(cls):
    if cls.name in REGISTRY and REGISTRY[cls.name] is not cls:
        raise ValueError(f"module {cls.name!r} déjà enregistré")
    REGISTRY[cls.name] = cls
    return cls


def discover(*paths) -> dict[str, type]:
    """Importe jumeau/modules/ puis chaque fichier .py des dossiers donnés ; renvoie le registre."""
    import jumeau.modules as builtin
    for m in pkgutil.iter_modules(builtin.__path__):
        importlib.import_module(f"jumeau.modules.{m.name}")
    for p in paths:
        for f in sorted(Path(p).glob("*.py")):
            name = f"jumeau_plugin_{f.stem}"
            if name not in sys.modules:
                spec = importlib.util.spec_from_file_location(name, f)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[name] = mod
                spec.loader.exec_module(mod)
    return REGISTRY
