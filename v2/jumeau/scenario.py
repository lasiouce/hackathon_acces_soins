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

    def over(self, base: "Scenario") -> "Scenario":
        """Ce scénario posé sur un scénario de base : paramètres fusionnés (les siens priment), événements
        ajoutés après ceux de la base, composition et graine de la base s'il n'en donne pas."""
        return Scenario(name=self.name, params={**base.params, **self.params}, events=list(base.events) + list(self.events),
                        modules=self.modules or base.modules, seed=self.seed if self.seed else base.seed,
                        doc=self.doc or base.doc)

    def validate(self, modules, cells=None) -> "Scenario":
        """modules : instances ou classes de la composition ; cells : cellules de l'état (pour les sélecteurs).
        Lève ValueError à la première incohérence : nom, opération, axe ou valeur de sélecteur inconnus,
        valeur hors des bornes déclarées par le paramètre."""
        decl = {f"{m.name}.{p.name}": p for m in modules for p in m.params}
        names = {m.name for m in modules}
        missing = set(self.composition) - names
        if missing:
            raise ValueError(f"scénario {self.name!r} : modules de la composition non construits {sorted(missing)}")

        def check_value(key, v, what):
            b = decl[key].bounds
            if isinstance(v, dict) and b is not None:
                for sub in v.values():
                    if isinstance(sub, (int, float)) and not isinstance(sub, bool):
                        check_value(key, sub, what)
                return
            if b is None or isinstance(v, (dict, str, bool)) or v is None:
                return
            arr = np.asarray(v, dtype=float)
            if arr.size and (not np.isfinite(arr).all() or arr.min() < b[0] or arr.max() > b[1]):
                raise ValueError(f"scénario {self.name!r} : {what} {key} = {v} hors des bornes {b}")

        for k, v in self.params.items():
            if k not in decl:
                raise ValueError(f"scénario {self.name!r} : paramètre inconnu {k!r} (connus : {sorted(decl)})")
            check_value(k, v, "paramètre")
        for e in self.events:
            if e.param not in decl:
                raise ValueError(f"scénario {self.name!r} : événement sur un paramètre inconnu {e.param!r}")
            if e.op not in OPS:
                raise ValueError(f"événement {e.param} : opération {e.op!r} hors {OPS}")
            if e.end is not None and e.end < e.start:
                raise ValueError(f"événement {e.param} : fin {e.end} avant début {e.start}")
            bad = set(e.selector) - set(AXES)
            if bad:
                raise ValueError(f"événement {e.param} : axes de sélecteur inconnus {sorted(bad)}")
            if cells is not None:
                for axis, v in e.selector.items():
                    vals = v if isinstance(v, (list, tuple, set)) else [v]
                    unknown = [x for x in vals if x not in set(cells[axis])]
                    if unknown:
                        raise ValueError(f"événement {e.param} : {axis} = {unknown} absent de l'état "
                                         f"(ex. de valeurs : {sorted(map(str, set(cells[axis])))[:5]})")
            v0 = decl[e.param].value
            if isinstance(v0, (dict, str, bool)) or (v0 is not None and not isinstance(v0, (int, float))):
                raise ValueError(f"événement {e.param} : paramètre non numérique ({type(v0).__name__}) ; "
                                 f"le fixer par `params`, pas par un événement")
            if isinstance(e.value, bool) or not isinstance(e.value, (int, float)) or not np.isfinite(e.value):
                raise ValueError(f"événement {e.param} : valeur {e.value!r} non numérique ou non finie")
        # valeur composée (événements empilés) aux années où elle change, pour les paramètres à défaut scalaire ;
        # les paramètres ajustés (défaut None) sont bornés à l'exécution par check_bounds (Context.param)
        for key in {e.param for e in self.events}:
            base = self.params.get(key, decl[key].value)
            if base is None or cells is None:
                continue
            years = sorted({e.start for e in self.events if e.param == key}
                           | {e.end + 1 for e in self.events if e.param == key and e.end is not None})
            for y in years:
                check_value(key, self.resolve(key, base, y, cells), f"valeur composée en {y}")
        return self

        return self

    def to_dict(self) -> dict:
        d = asdict(self)
        d["modules"] = list(self.modules) if self.modules else None     # None = « composition de la base » (over)
        d["format"] = FORMAT
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True,
                          default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))

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

    def touches(self, key: str, year: int) -> bool:
        return key in self.params or any(e.param == key and e.active(year) for e in self.events)

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
