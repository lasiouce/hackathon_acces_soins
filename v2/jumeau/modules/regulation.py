"""Régulation conventionnelle de l'installation, par liste de géocodes.

Zone « remplacement seul » : dans le secteur privé d'un territoire régulé, les entrées de l'année ne
peuvent dépasser les sorties de l'année (cellule = profession × territoire × sexe). L'excédent n'est
pas perdu : il est déplacé vers la cellule `destination` (même profession, territoire, sexe, âge),
par défaut le secteur public. La destination réelle des entrants bloqués est une inconnue (axe 1) ;
`destination` est donc un paramètre supposé. Lit les flux `entrees` et `sorties` de l'année (needs) :
build() refuse une composition où ils manquent. Des zones qui ne touchent aucune cellule du secteur
régulé sont une erreur, pas un effet nul.
"""
import numpy as np

from jumeau.module import Module, Move, Param, register


@register
class Regulation(Module):
    name = "regulation"
    order = 40
    needs = ("entrees", "sorties")
    params = (
        Param("zones", {}, "profession -> [géocodes]", "avenants conventionnels SF, CD, MK, IDE (axe 4 : zonage)",
              "à renseigner", "sourcé", "Territoires en « remplacement d'un départ seulement »."),
        Param("secteur_regule", "prive", "secteur", "décision 2026-11-14 « libéral » = privé", "2026", "sourcé"),
        Param("destination", "public", "secteur", "hypothèse en attendant l'axe 1", "—", "supposé",
              "Où vont les entrants bloqués."),
    )

    def step(self, state, ctx):
        zones = ctx.param(self, "zones")
        if not zones:
            return []
        c = state.cells
        reg = np.zeros(len(c), bool)
        for prof, geo in zones.items():
            reg |= (c.profession == prof).to_numpy() & c.territory.isin(geo).to_numpy()
        reg &= (c.sector == ctx.param(self, "secteur_regule")).to_numpy()
        src = np.flatnonzero(reg)
        if src.size == 0:
            raise ValueError(f"regulation : aucune cellule du secteur {ctx.param(self, 'secteur_regule')!r} dans les zones "
                             f"(secteurs de l'état : {sorted(c.sector.unique())})")
        dst = state.index(c.iloc[src].assign(sector=ctx.param(self, "destination")))
        if (dst < 0).any():
            raise ValueError("cellule de destination absente : State.ensure_sector(destination) d'abord")
        ent = ctx.delta(self, "entrees")[src]
        out = -ctx.delta(self, "sorties")[src]
        e, x = ent.sum(1), out.sum(1)
        frac = np.where(e > 0, np.clip((e - x) / np.where(e > 0, e, 1), 0, 1), 0.0)
        return [Move(self.name, ent * frac[:, None], src, dst)]
