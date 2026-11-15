"""Régulation conventionnelle de l'installation, par liste de géocodes.

Zone « remplacement seul » (CD, MK : zones « non prioritaires » ; IDE, SF : « sur-dotées ») : dans le secteur
privé d'un territoire régulé, les entrées de l'année ne peuvent dépasser les sorties de l'année
(cellule = profession × territoire × sexe ; fiches axe 1 param-*-regul-regle). Mécanisme :
  excédent    = max(entrées − sorties, 0) × (1 − part_exemptee_p)
  bloqués     = θ × excédent           θ = part contraignante du plafond (fuite : 1 − θ s'installe quand même)
  bloqués se répartissent selon `repartition` (somme = 1) :
    voisine   installation dans un territoire voisin non régulé, toujours dans le privé. Au département et
              au-dessus, la commune voisine est presque toujours dans le même territoire : ces entrants restent
              dans leur cellule (effet nul à ce grain, par construction). À la commune, il faut une table
              `voisins` {territoire régulé : territoire voisin} ; sans elle, erreur.
    salariat  déplacés vers le secteur `destination` (par défaut `bloques`, créé vide, démographie du privé
              par la règle de repli de history.py) : hors de la sortie « libéral ».
    sortie    quittent l'exercice (compte `regulation_sortie` du registre).
Valeurs par défaut (fiches axe 1) : θ = 0,80 [0,74 ; 0,87], supposé (axe 3, N3, IDE 2012-2019, exploratoire) ;
repartition = 100 % voisine, supposé (param-regul-report-entrants : destination non mesurable ; variantes
pour l'axe 5 : 50/50 voisine/salariat, 100 % sortie) ; part_exemptee : dentistes spécialistes (ODF, CO, MBD),
conventionnables sans succession en place supplémentaire (convention 2023, art. 35.5 : dérogation, pas exemption ;
relecture du 2026-11-15), part non mesurée dans nos données → 0, supposé.

Non représenté ici, faute d'objet dans un modèle d'effectifs :
  - IDE, zones intermédiaires ou très dotées en périphérie : ≥ 2/3 de l'activité dans la zone d'installation
    (contrainte d'activité, pas d'effectif) ;
  - MK, obligation d'exercer 2 ans en zone sous-dotée pour les diplômés à partir de 2027 : demande de suivre
    l'ancienneté d'installation des cohortes (open.md).
Lit les flux `entrees` et `sorties` de l'année (needs). Des zones qui ne touchent aucune cellule du secteur
régulé sont une erreur, pas un effet nul.
"""
import numpy as np

from jumeau.module import Add, Module, Move, Param, par_profession, register

PARTS = ("voisine", "salariat", "sortie")


@register
class Regulation(Module):
    name = "regulation"
    order = 40
    needs = ("entrees", "sorties")
    optional = ("lien_formation", "etrangers")      # entrées supplémentaires de l'année, plafonnées aussi si présentes
    produces = ("regulation", "regulation_sortie")
    params = (
        Param("zones", {}, "profession -> [géocodes]", "avenants conventionnels SF, CD, MK, IDE (axe 4 : zonage)",
              "à renseigner", "sourcé", "Territoires en « remplacement d'un départ seulement », dans l'ordre de "
              "priorité (ex. densité décroissante) : `part_zones` garde les premiers.", None, "installer"),
        Param("part_zones", {"*": 1.0}, "part des zones listées, par profession", "levier de scénario",
              "—", "supposé", "0 = régulation retirée ; 1 = toutes les zones listées. Garde les round(part × n) "
              "premières zones de la liste.", (0.0, 1.0), "installer"),
        Param("secteur_regule", "prive", "secteur", "décision 2026-11-14 « libéral » = privé", "2026", "sourcé"),
        Param("theta", 0.80, "sans dimension", "axe 3, N3 (DiD zonage IDE 2012-2019) ; fiche param-regul-theta-fuite",
              "2004-2019", "supposé", "Part contraignante du plafond ; plage 0,5-1 pour l'axe 5.", (0.0, 1.0),
              "installer"),
        Param("repartition", {"voisine": 1.0, "salariat": 0.0, "sortie": 0.0}, "parts (somme = 1)",
              "fiche param-regul-report-entrants (IRDES QES 270, 2022 ; Cour des comptes 2024 : qualitatif)",
              "2022 ; 2024", "non mesurable", "Destination des entrants bloqués ; défaut supposé : commune voisine.",
              (0.0, 1.0), "installer"),
        Param("destination", "bloques", "secteur", "hypothèse en attendant l'axe 1", "—", "supposé",
              "Secteur qui reçoit la part « salariat » (créé vide si absent ; démographie du privé par repli)."),
        Param("part_exemptee", {"dentistes": 0.0, "*": 0.0}, "part des entrants, par profession",
              "convention nationale des chirurgiens-dentistes 2023, art. 35.5 (spécialistes : dérogation, place "
              "supplémentaire hors succession) ; fiche param-cd-regul-regle", "2023", "non mesurable",
              "Part des entrants non soumis à la règle ; dentistes spécialistes : part non mesurée → 0.", (0.0, 1.0),
              "installer"),
        Param("voisins", None, "{territoire régulé : territoire voisin}", "à construire (axe 4)", "—", "supposé",
              "Requis à la commune si la part « voisine » est non nulle."),
    )

    def prepare(self, state, scenario):
        if not scenario.params.get(f"{self.name}.zones"):
            return state
        rep = scenario.params.get(f"{self.name}.repartition", self.param("repartition").value)
        if rep.get("salariat", 0) <= 0:
            return state
        return state.ensure_sector(scenario.params.get(f"{self.name}.destination", self.param("destination").value))

    def step(self, state, ctx):
        zones = ctx.param(self, "zones")
        if not zones:
            return []
        rep = ctx.param(self, "repartition")
        if set(rep) - set(PARTS) or abs(sum(rep.values()) - 1) > 1e-9:
            raise ValueError(f"regulation.repartition : clés {PARTS}, somme 1 (reçu {rep})")
        c = state.cells
        reg = np.zeros(len(c), bool)
        pz = ctx.param(self, "part_zones")
        kept = {}
        for prof, geo in zones.items():
            kept[prof] = list(geo)[:int(round(float(par_profession(pz, [prof])[0]) * len(geo)))]
            reg |= (c.profession == prof).to_numpy() & c.territory.isin(kept[prof]).to_numpy()
        if not any(kept.values()):
            return []                                    # aucune zone gardée (part_zones = 0, ou arrondi à 0 zone)
        reg &= (c.sector == ctx.param(self, "secteur_regule")).to_numpy()
        src = np.flatnonzero(reg)
        if src.size == 0:
            raise ValueError(f"regulation : aucune cellule du secteur {ctx.param(self, 'secteur_regule')!r} dans les zones "
                             f"(secteurs de l'état : {sorted(c.sector.unique())})")
        ent = np.clip(sum(ctx.delta(self, n) for n in ("entrees",) + self.optional)[src], 0, None)   # entrées brutes positives seulement : une entrée
                                                                    # nette négative (départ) n'est pas « bloquée »
        out = -ctx.delta(self, "sorties")[src]
        e, x = ent.sum(1), out.sum(1)
        frac = np.where(e > 0, np.clip((e - x) / np.where(e > 0, e, 1), 0, 1), 0.0)
        frac = frac * (1 - par_profession(ctx.param(self, "part_exemptee"), c.profession.iloc[src])) * ctx.param(self, "theta")
        blocked = ent * frac[:, None]
        flows = []
        if rep.get("voisine", 0) > 0 and state.level == "com":
            voisins = ctx.param(self, "voisins")
            if not voisins:
                raise ValueError("regulation : à la commune, la part « voisine » demande regulation.voisins")
            dst = state.index(c.iloc[src].assign(territory=c.territory.iloc[src].map(voisins)))
            if (dst < 0).any():
                raise ValueError("regulation : voisin absent de l'état pour certaines cellules régulées")
            flows.append(("voisine", dst))
        if rep.get("salariat", 0) > 0:
            dst = state.index(c.iloc[src].assign(sector=ctx.param(self, "destination")))
            if (dst < 0).any():
                raise ValueError("cellule de destination absente : State.ensure_sector(destination) d'abord")
            flows.append(("salariat", dst))
        moves = [Move(self.name, blocked * rep[k], src, dst) for k, dst in flows]
        if len(moves) > 1:                               # un seul flux nommé `regulation` par module et par an
            amount = np.concatenate([m.amount for m in moves])
            moves = [Move(self.name, amount, np.concatenate([m.src for m in moves]),
                          np.concatenate([m.dst for m in moves]))]
        res = moves
        if rep.get("sortie", 0) > 0:
            gone = np.zeros_like(state.N)
            np.add.at(gone, src, -blocked * rep["sortie"])
            res = res + [Add("regulation_sortie", gone, src="regulation_sortie")]
        return res
