"""Moteur du jumeau : fait avancer l'état d'une année à l'autre sous un scénario.

Pour chaque année t+1 : chaque module de la composition (trié par `order`) lit l'état courant et
rend des flux, que le moteur applique aussitôt (le module suivant voit l'état mis à jour), puis un
plancher à 0 (le montant tronqué va au compte `plancher`, pour que rien ne disparaisse sans trace).
Le registre (`ledger`) garde chaque flux par année et par cellule.
build() vérifie les dépendances déclarées (needs / produces) ; run() valide le scénario contre la
composition, refuse un flux non déclaré et remet chaque module à zéro (begin) avant de commencer.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from jumeau.module import Add, Move, Pool, Rate, Shift, discover
from jumeau.scenario import Scenario
from jumeau.state import State


@dataclass
class Context:
    year: int
    origin: int
    scenario: Scenario
    cells: pd.DataFrame
    rng: np.random.Generator
    n_ages: int = 0
    deltas: dict = field(default_factory=dict)     # flux de l'année déjà appliqués : nom -> ΔN [cellule, âge]
    pools: dict = field(default_factory=dict)      # flux Pool de l'année : nom -> {compte: valeurs}

    @property
    def h(self) -> int:
        return self.year - self.origin

    def param(self, module, name, base=None, cells=None):
        """Valeur résolue pour l'année : base (ajustée) ou défaut, puis surcharges et événements du scénario.
        `cells` remplace les cellules de l'état pour les sélecteurs (ex. vivier : une ligne par profession)."""
        p = module.param(name)
        default = p.value if base is None else base
        key = f"{module.name}.{name}"
        val = self.scenario.resolve(key, default, self.year, self.cells if cells is None else cells)
        if p.bounds is not None and self.scenario.touches(key, self.year) and not isinstance(val, (dict, str, bool)):
            arr = np.asarray(val, dtype=float)                 # bornes sur la valeur composée, ajustée ou non
            if not np.isfinite(arr).all() or arr.min() < p.bounds[0] or arr.max() > p.bounds[1]:
                raise ValueError(f"{key} en {self.year} : valeur composée hors des bornes {p.bounds} "
                                 f"(min {np.nanmin(arr):.4g}, max {np.nanmax(arr):.4g})")
        return val

    def param_of(self, module_name: str, name: str, default=None):
        """Valeur d'un paramètre d'un autre module (surcharges du scénario comprises) ; `default` si non surchargé."""
        return self.scenario.params.get(f"{module_name}.{name}", default)

    def delta(self, module, name) -> np.ndarray:
        """ΔN [cellule, âge] du flux `name` dans l'année ; seulement s'il est déclaré dans module.needs."""
        if name not in module.needs and name not in module.optional:
            raise KeyError(f"{module.name} lit le flux {name!r} sans le déclarer dans needs")
        if name in self.pools:
            raise TypeError(f"{name!r} est un flux de vivier (Pool) : le lire par ctx.pool_out(module, flux, compte)")
        return self.deltas.get(name, np.zeros((len(self.cells), self.n_ages)))   # producteur muet cette année = 0

    def pool_out(self, module, name, account):
        """Compte d'un flux Pool de l'année (ex. formation / diplomes) ; seulement s'il est déclaré dans needs."""
        if name not in module.needs:
            raise KeyError(f"{module.name} lit le flux {name!r} sans le déclarer dans needs")
        return self.pools.get(name, {}).get(account)


@dataclass
class Trajectory:
    states: dict                       # année -> State
    ledger: list                       # (year, flux, compte, ΔN par cellule)

    def frame(self) -> pd.DataFrame:
        return pd.concat([s.to_frame() for s in self.states.values()], ignore_index=True)

    def totals(self, by=("profession", "territory")) -> pd.DataFrame:
        return pd.DataFrame({y: s.total(by) for y, s in self.states.items()})

    def flows(self) -> pd.DataFrame:
        return pd.DataFrame([(y, f, c, d.sum()) for y, f, c, d in self.ledger], columns=["year", "flux", "compte", "n"])


def apply(x: np.ndarray, f) -> np.ndarray:
    """Applique un flux à N [cellule, âge] ; renvoie le nouvel N (opérations identiques à sante.model.project)."""
    if isinstance(f, Shift):
        if np.ndim(f.frac) == 0:
            prev = np.roll(x, 1, axis=1)
            prev[:, 0] = 0
            y = (1.0 - f.frac) * x + f.frac * prev
            y[:, -1] = x[:, -1] + f.frac * x[:, -2]      # tranche ouverte du haut
            return y
        moved = x * np.asarray(f.frac)[None, :]          # une fraction par tranche (1 / largeur)
        moved[:, -1] = 0
        y = x - moved
        y[:, 1:] += moved[:, :-1]
        return y
    if isinstance(f, Rate):
        return f.factor * x
    if isinstance(f, Add):
        return x + f.amount
    if isinstance(f, Move):
        y = x.copy()
        np.subtract.at(y, f.src, f.amount)
        np.add.at(y, f.dst, f.amount)
        return y
    raise TypeError(f)


def check_dependencies(modules) -> None:
    """Chaque flux lu (needs) doit être produit par un module placé avant ; deux modules ne produisent pas le même."""
    produced = {}
    later = {n: m.name for m in modules for n in m.outputs()}
    for m in modules:
        for n in m.optional:
            if n in later and n not in produced:
                raise ValueError(f"module {m.name!r} lit le flux optionnel {n!r}, produit après lui par {later[n]!r}")
        for n in m.needs:
            if n not in produced:
                raise ValueError(f"module {m.name!r} a besoin du flux {n!r}, produit par aucun module placé avant lui")
        for n in m.outputs():
            if n in produced:
                raise ValueError(f"flux {n!r} produit par {produced[n]!r} et {m.name!r}")
            produced[n] = m.name


def build(names, registry=None) -> list:
    reg = registry or discover()
    unknown = [n for n in names if n not in reg]
    if unknown:
        raise ValueError(f"modules inconnus {unknown} (registre : {sorted(reg)})")
    mods = sorted((reg[n]() for n in names), key=lambda m: m.order)
    check_dependencies(mods)
    return mods


def run(state: State, modules: list, scenario: Scenario, until: int, origin: int | None = None,
        floor: bool = True) -> Trajectory:
    """floor=False retire le plancher à 0 (le modèle devient linéaire) : sert aux tests de conservation."""
    origin = state.year if origin is None else origin
    if {m.name for m in modules} != set(scenario.composition):
        raise ValueError(f"modules fournis {[m.name for m in modules]} ≠ composition du scénario {scenario.composition}")
    check_dependencies(modules)
    x = state.copy()
    for m in modules:
        x = m.prepare(x, scenario)
    scenario.validate(modules, x.cells)
    rng = np.random.default_rng(scenario.seed)
    out, ledger = {}, []
    for m in modules:
        m.begin(x, Context(state.year, origin, scenario, x.cells, rng, len(x.ages)))
    for year in range(state.year + 1, until + 1):
        ctx = Context(year, origin, scenario, x.cells, rng, len(x.ages))
        N = x.N
        for m in modules:
            for f in m.step(x, ctx):
                if f.name not in m.outputs():
                    raise ValueError(f"module {m.name!r} rend le flux non déclaré {f.name!r}")
                if isinstance(f, Pool):
                    x.pool = f.new
                    ctx.pools[f.name] = dict(f.out)
                    for acct, v in f.out.items():
                        ledger.append((year, f.name, acct, v if hasattr(v, "index") else np.asarray(v, float)))   # Series : par profession
                    continue
                new = apply(N, f)
                d = new - N
                ctx.deltas[f.name] = ctx.deltas.get(f.name, 0) + d
                acct = f.to if isinstance(f, Rate) else f.src if isinstance(f, Add) else "interne"
                ledger.append((year, f.name, acct, d.sum(axis=1)))
                N = new
                x = State(x.cells, x.ages, N, x.year, x.level, x.pool, x._key)
        floored = np.maximum(N, 0) if floor else N
        ledger.append((year, "plancher", "plancher", (floored - N).sum(axis=1)))
        x = State(x.cells, x.ages, floored, year, x.level, x.pool, x._key)
        out[year] = x
    return Trajectory(out, ledger)
