"""Scénario = jeu d'hyperparamètres + événements datés. Une politique publique est un scénario.

  params   "module.param" -> valeur, sur tout l'horizon (remplace la valeur par défaut ou ajustée)
  events   Event(param, start, value, op, end, selector) : à partir de `start` (jusqu'à `end`
           inclus), sur les cellules choisies par `selector` (axe -> valeur ou liste), la valeur
           est remplacée (set), multipliée (mul) ou augmentée (add). C'est la forme concrète de la
           proposition Perturbation(slot, selector, profile) : slot = param, profile = start/end/op.
  modules  composition (noms du registre) ; None = DEFAULT_MODULES
  seed     graine du générateur aléatoire fourni aux modules (ctx.rng), pour les méthodes stochastiques
Le scénario par défaut (tendanciel) est l'identité : aucun paramètre ne bouge.
validate(modules) refuse toute clé, opération ou axe inconnu ; to_dict / from_dict (JSON) le rendent
sérialisable, avec un numéro de format.
"""
import json
from dataclasses import asdict, dataclass, field

import numpy as np

DEFAULT_MODULES = ("vieillissement", "sorties", "entrees")
FORMAT = 1
OPS = ("set", "mul", "add")
AXES = ("profession", "sector", "territory", "sex")


@dataclass(frozen=True)
class Event:
    param: str
    start: int
    value: float
    op: str = "set"
    end: int | None = None
    selector: dict = field(default_factory=dict)
    source: str = ""

    def active(self, year: int) -> bool:
        return self.start <= year and (self.end is None or year <= self.end)


@dataclass
class Scenario:
    name: str = "tendanciel"
    params: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    modules: tuple | None = None
    seed: int = 0
    doc: str = ""

    @property
    def composition(self) -> tuple:
        return tuple(self.modules or DEFAULT_MODULES)

    def validate(self, modules) -> "Scenario":
        """modules : instances ou classes de la composition. Lève ValueError à la première incohérence."""
        known = {f"{m.name}.{p.name}" for m in modules for p in m.params}
        names = {m.name for m in modules}
        missing = set(self.composition) - names
        if missing:
            raise ValueError(f"scénario {self.name!r} : modules de la composition non construits {sorted(missing)}")
        for k in self.params:
            if k not in known:
                raise ValueError(f"scénario {self.name!r} : paramètre inconnu {k!r} (connus : {sorted(known)})")
        for e in self.events:
            if e.param not in known:
                raise ValueError(f"scénario {self.name!r} : événement sur un paramètre inconnu {e.param!r}")
            if e.op not in OPS:
                raise ValueError(f"événement {e.param} : opération {e.op!r} hors {OPS}")
            if e.end is not None and e.end < e.start:
                raise ValueError(f"événement {e.param} : fin {e.end} avant début {e.start}")
            bad = set(e.selector) - set(AXES)
            if bad:
                raise ValueError(f"événement {e.param} : axes de sélecteur inconnus {sorted(bad)}")
        return self

    def to_dict(self) -> dict:
        d = asdict(self)
        d["modules"] = list(self.composition)
        d["format"] = FORMAT
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> "Scenario":
        d = dict(d)
        if d.pop("format", None) != FORMAT:
            raise ValueError(f"format de scénario attendu : {FORMAT}")
        d["events"] = [Event(**e) for e in d.get("events", [])]
        d["modules"] = tuple(d["modules"]) if d.get("modules") else None
        return cls(**d)

    @classmethod
    def from_json(cls, s: str) -> "Scenario":
        return cls.from_dict(json.loads(s))

    def resolve(self, key: str, base, year: int, cells):
        """Valeur du paramètre `key` pour l'année : scalaire, ou tableau dont l'axe 0 = cellules."""
        val = self.params.get(key, base)
        evs = [e for e in self.events if e.param == key and e.active(year)]
        if not evs:
            return val
        val = np.array(val, dtype=float)
        if val.ndim == 0:
            val = np.full(len(cells), float(val))
        else:
            val = val.copy()
        for e in evs:
            m = np.ones(len(cells), bool)
            for axis, v in e.selector.items():
                m &= cells[axis].isin(v if isinstance(v, (list, tuple, set)) else [v]).to_numpy()
            m = m.reshape(-1, *[1] * (val.ndim - 1))
            new = {"set": np.broadcast_to(e.value, val.shape), "mul": val * e.value, "add": val + e.value}[e.op]
            val = np.where(m, new, val)
        return val
