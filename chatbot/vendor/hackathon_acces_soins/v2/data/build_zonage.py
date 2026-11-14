"""Axe 4 — zonage conventionnel par commune × profession, en géocodes.

Run : uv run python v2/data/build_zonage.py   (depuis la racine du dépôt, ≈ 2 s)

Deux millésimes, tous deux ouverts :
  - « actuel » : CartoSanté (Atlasanté, ARS), service TJS `zonage_conv`, référentiel arm2026 (communes COG 2026,
    Paris, Lyon et Marseille remplacés par leurs arrondissements, zonés à ce niveau),
    attributs z_sf, z_dent, z_kine, z_infi ; extrait le 2026-11-14. Date des arrêtés non publiée par le service
    (« Pour en savoir + » renvoie aux arrêtés ARS) : millésime = date d'extraction.
  - « 2012 » : Atlasanté, jeu uuid c987d0e2 (z_infi, z_kine, z_dent ; pas de z_sf), métropole, codes région
    d'avant 2016 ; métadonnées datées 2014-01-22 / 2014-10-22 / 2019-03-13. Lu par l'axe 3 comme la génération
    de zonage de 2012.

Statut (ce que le modèle lit) :
  remplacement_seul : conventionnement d'un nouvel installé seulement en remplacement d'un départ
                      (zones « sur-dotées » et, nouveau zonage kinés / dentistes, « non prioritaires »)
  incitation        : zones très sous-dotées / sous-dotées (aides conventionnelles à l'installation)
  autre             : intermédiaire, très dotée, non renseigné
Le statut « obligation d'exercice » n'est pas une classe de zonage dans ces fichiers (voir le rapport).

Sortie : v2/data/processed/zonage_commune.parquet
  com, profession, millesime, classe, libelle, statut, regime, source
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "v2" / "data" / "raw" / "zonage"
OUT = ROOT / "v2" / "data" / "processed"

PROF = {"z_sf": "sages-femmes", "z_dent": "dentistes", "z_kine": "kines", "z_infi": "infirmiers"}
SRC_NOW = ("CartoSanté (Atlasanté) TJS zonage_conv, arm2026 (communes COG 2026, Paris / Lyon / Marseille par arrondissement), sources CNAMTS – ARS, extrait 2026-11-14")
SRC_OLD = ("Atlasanté catalogue uuid c987d0e2-e99c-4a11-a3a4-aa81de6aa416, ARS, métadonnées 2014-10-22 "
           "(màj fiche 2019-03-13), extrait 2026-11-14")

# classe CartoSanté -> (libellé, statut, régime)
CLASSES = {
    "1_Tres_sous_dotee": ("Très sous-dotée", "incitation", ""),
    "2_Sous_dotee": ("Sous-dotée", "incitation", ""),
    "3_intermediaire": ("Intermédiaire", "autre", ""),
    "4_Tres_dotee": ("Très dotée", "autre", ""),
    "5_Sur_dotee": ("Sur-dotée", "remplacement_seul", "ancien zonage"),
    "5b_Non_prioritaire": ("Non prioritaire", "remplacement_seul", "nouveau zonage"),
}
OLD = {"1": "1_Tres_sous_dotee", "2": "2_Sous_dotee", "3": "3_intermediaire", "4": "4_Tres_dotee",
       "5": "5_Sur_dotee"}


def read_tjs(path: Path) -> pd.DataFrame:
    x = path.read_text(encoding="utf-8")
    rows = re.findall(r"<Row><K>([^<]*)</K><V>([^<]*)</V></Row>", x)
    return pd.DataFrame(rows, columns=["com", "classe"])


def main():
    parts = []
    for attr, prof in PROF.items():
        t = read_tjs(RAW / f"cartosante_zonage_conv_arm2026_{attr}.xml")
        parts.append(t.assign(profession=prof, millesime="actuel (extrait 2026-11-14)", source=SRC_NOW))
    feats = json.loads((RAW / "atlasante_zonage_c987d0e2.geojson").read_text())["features"]
    old = pd.DataFrame([f["properties"] for f in feats])
    for attr in ["z_infi", "z_kine", "z_dent"]:
        t = old[["codgeo", attr]].rename(columns={"codgeo": "com", attr: "classe"})
        t["classe"] = t["classe"].astype(str).str.strip().map(OLD).fillna("")
        parts.append(t.assign(profession=PROF[attr], millesime="2012 (génération ARS, fiche 2014)", source=SRC_OLD))
    z = pd.concat(parts, ignore_index=True)
    z["classe"] = z["classe"].fillna("").replace({"3_Intermediaire": "3_intermediaire", "-9999": ""})
    unknown = set(z["classe"]) - set(CLASSES) - {""}
    assert not unknown, unknown
    z["libelle"] = z["classe"].map(lambda c: CLASSES.get(c, ("Non renseigné",))[0])
    z["statut"] = z["classe"].map(lambda c: CLASSES.get(c, ("", "autre"))[1])
    z["regime"] = z["classe"].map(lambda c: CLASSES.get(c, ("", "", ""))[2])
    z["niveau"] = z["com"].str.match(r"^(751\d\d|6938\d|132\d\d)$").map({True: "arm", False: "com"})
    z = z[["com", "niveau", "profession", "millesime", "classe", "libelle", "statut", "regime", "source"]]
    OUT.mkdir(parents=True, exist_ok=True)
    z.to_parquet(OUT / "zonage_commune.parquet", index=False)
    print(z.groupby(["millesime", "profession", "libelle"]).size().unstack(fill_value=0).to_string())
    print(z.groupby(["millesime", "profession"]).com.nunique())


if __name__ == "__main__":
    main()
