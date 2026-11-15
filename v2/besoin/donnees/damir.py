"""Open DAMIR (Assurance maladie, inter-régimes) : agrégats mensuels lus en flux, aucun fichier brut stocké.

Run (racine du dépôt) :
    uv run python v2/besoin/donnees/damir.py 202501            # un mois de flux (pilote)
    uv run python v2/besoin/donnees/damir.py 202401-202412     # une plage
    uv run python v2/besoin/donnees/damir.py --fenetre         # la fenêtre décidée le 2026-11-15 (registre)
    uv run python v2/besoin/donnees/damir.py --controle        # contrôles et fiche de manifeste (après lecture)

Règle de l'utilisateur·rice (registre, 2026-11-15) : `curl | gunzip | filtre`, le CSV (~0,95 Go compressé par mois)
n'est jamais écrit sur disque ; seuls les agrégats le sont. Pas d'API : lien à jeton lu sur
`open-data-assurance-maladie.ameli.fr/depenses/download.php?Dir_Rep=Open_DAMIR&Annee=AAAA`.

Le fichier `AAAAMM` est un mois de **flux** (date de chargement, FLX_ANN_MOI) : il contient des soins de plusieurs
mois (SOI_ANN, SOI_MOI), gardés en clé. Descriptif lu (xlsx, assurance-maladie.ameli.fr, consulté le 2026-11-15) :
  - indicateurs bruts (PRS_ACT_QTE, PRS_PAI_MNT…) : « filtre impératif sur type de remboursement = 0 » sinon doublons ;
    on filtre donc PRS_REM_TYP = 0 (prestation de référence, part légale), et PRS_REM_MNT y est la part légale ;
  - compter les actes avec la quantité (PRS_ACT_QTE), pas le dénombrement (pas remonté pour tous les régimes) ;
  - dentistes : nature d'activité 19, 53, 54 **et** spécialité 36 (ODF) ;
  - TOP_PS5_TRG = 1 : périmètre de la Statistique mensuelle tous régimes ; PSE_STJ_SNDS (libéral / salarié) n'est
    renseigné que pour le régime général et les régimes infogérés (9 = inconnu sinon).
Professions (clé `prof`) : SF (21), CD (19, 53, 54 ou spé. 36), PH (50), MK (26), IDE (24), MG (spécialité 1,
catégorie médecin ; source des transferts seulement, décision O2).
Géographie : BEN_RES_REG (résidence du bénéficiaire) et EXE_INS_REG (région du PS exécutant), 13 zones depuis 2015 ;
DOM regroupés en un code 5 (non séparables) ; PACA et Corse fusionnées (93) ; 99 = inconnu.

Sorties (Licence Ouverte 2.0) : v2/data/processed/besoin/damir/
  - agg_AAAAMM.parquet (~15 Mo par mois, **non commité**, ignoré par git : ~0,7 Go pour la fenêtre ; se
    reconstruit en ~3 h de machine) : flx × soi_ann × soi_moi × ben_reg × exe_reg × age × sexe × prof × stj × ppu × top_ps5 ×
    prs_nat → qte, nbr, pai_mnt, rem_bse, rem_mnt, dep_mnt ;
  - ctl_AAAAMM.parquet : totaux du fichier entier (toutes catégories) par catégorie d'exécutant × enveloppe ×
    top_ps5, pour les contrôles contre la Statistique mensuelle publiée ;
  - pilote.csv : une ligne par mois lu (octets compressés, lignes, secondes, débit).
Tables dérivées commitées (`--controle`), v2/data/processed/besoin/ :
  - damir_profils.parquet : flux 2024 et 2025, somme sur les mois de flux, clés flx_ann × soi_ann × ben_reg × âge ×
    sexe × prof × stj × ppu × top_ps5 × prs_nat (sans région de l'exécutant ni mois de soins) ;
  - damir_vaccination.parquet : tous les mois lus, `PRS_NAT` de vaccination seulement (VACC ci-dessous), clés
    flx × soi_ann × soi_moi × ben_reg × exe_reg × âge × sexe × prof × stj × ppu (P-B6).

Contrôles (`--controle`) :
  1. information : part de chaque profession dans la dépense du fichier entier, par mois (pas de verdict : la
     catégorie d'exécutant PSE_ACT_CAT ne recoupe pas la nature d'activité, ex. pharmacie en « fournisseur ») ;
  2. externe : **aucun total publié au même périmètre n'a été trouvé**. La Statistique mensuelle de la Cnam
     (« dépenses risque statistique mensuelle », zip de décembre 2025, fichier 2_Lieu_execution) est en champ
     **régime général + SLM** (PDF « Champ des données en date de remboursement », lu le 2026-11-15), et DAMIR n'a
     pas de variable de régime pour s'y restreindre. On publie donc le rapport DAMIR (tous régimes, flux 2025,
     libéral × privé, part légale) / RG (cabinets libéraux, montants remboursés 2025) par profession, attendu
     un peu au-dessus de 1, sans seuil à 0,5 % : ce n'est pas le critère de l'axe 4, il reste ouvert (open.md).
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.csv as pcsv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import OUT_LO  # noqa: E402

OUT = OUT_LO / "damir"
PAGE = "https://open-data-assurance-maladie.ameli.fr/depenses/download.php?Dir_Rep=Open_DAMIR&Annee={a}"
BASE = "https://open-data-assurance-maladie.ameli.fr/depenses/"
CLES = ["FLX_ANN_MOI", "SOI_ANN", "SOI_MOI", "BEN_RES_REG", "EXE_INS_REG", "AGE_BEN_SNDS", "BEN_SEX_COD",
        "PSE_STJ_SNDS", "PRS_PPU_SEC", "TOP_PS5_TRG", "PRS_NAT"]
MESURES = ["PRS_ACT_QTE", "PRS_ACT_NBR", "PRS_PAI_MNT", "PRS_REM_BSE", "PRS_REM_MNT", "PRS_DEP_MNT"]
AUTRES = ["PSE_ACT_CAT", "PSE_ACT_SNDS", "PSE_SPE_SNDS", "PRS_REM_TYP", "CPT_ENV_TYP"]
NOMS = {"FLX_ANN_MOI": "flx", "SOI_ANN": "soi_ann", "SOI_MOI": "soi_moi", "BEN_RES_REG": "ben_reg",
        "EXE_INS_REG": "exe_reg", "AGE_BEN_SNDS": "age", "BEN_SEX_COD": "sexe", "PSE_STJ_SNDS": "stj",
        "PRS_PPU_SEC": "ppu", "TOP_PS5_TRG": "top_ps5", "PRS_NAT": "prs_nat", "PRS_ACT_QTE": "qte",
        "PRS_ACT_NBR": "nbr", "PRS_PAI_MNT": "pai_mnt", "PRS_REM_BSE": "rem_bse", "PRS_REM_MNT": "rem_mnt",
        "PRS_DEP_MNT": "dep_mnt", "PSE_ACT_CAT": "cat", "CPT_ENV_TYP": "env"}
# fenêtre décidée le 2026-11-15 : profils 2024 et 2025 ; campagnes oct.–fév. des saisons 2015-16 à 2019-20 (P-B6)
FENETRE = ([f"{a}{m:02d}" for a in (2025, 2024) for m in range(1, 13)]
           + [f"{a}{m:02d}" for s in range(2015, 2020) for a, m in [(s, 10), (s, 11), (s, 12), (s + 1, 1), (s + 1, 2)]])


def lien(mois: str) -> str:
    html = urllib.request.urlopen(PAGE.format(a=mois[:4]), timeout=60).read().decode("utf-8", "ignore")
    m = re.search(r'href="\./(download_file\.php\?token=[0-9a-f]+&file=Open_DAMIR/A' + mois + r'\.csv\.gz)"', html)
    if not m:
        raise SystemExit(f"pas de lien pour {mois}")
    return BASE + m.group(1)


def prof(df: pd.DataFrame) -> pd.Series:
    a, s = df["PSE_ACT_SNDS"], df["PSE_SPE_SNDS"]
    p = pd.Series(pd.NA, index=df.index, dtype="string")
    p[a == 21] = "SF"
    p[a.isin([19, 53, 54]) | (s == 36)] = "CD"
    p[a == 50] = "PH"
    p[a == 26] = "MK"
    p[a == 24] = "IDE"
    p[(s == 1) & (df["PSE_ACT_CAT"] == 1)] = "MG"
    return p


def lire_mois(mois: str) -> dict:
    url = lien(mois)
    t0 = time.time()
    curl = subprocess.Popen(["curl", "-s", "-L", "--fail", "-w", "%{stderr}%{size_download}", url], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    gz = subprocess.Popen(["gunzip", "-c"], stdin=curl.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    curl.stdout.close()
    cols = CLES + MESURES + AUTRES
    types = {c: pa.float64() if c in MESURES else pa.int32() for c in cols}
    types["PRS_NAT"] = pa.int32()
    lecteur = pcsv.open_csv(gz.stdout, read_options=pcsv.ReadOptions(block_size=64 << 20),
                            parse_options=pcsv.ParseOptions(delimiter=";"),
                            convert_options=pcsv.ConvertOptions(include_columns=cols, column_types=types))
    parts, ctl, n = [], [], 0
    k_ctl = ["FLX_ANN_MOI", "PSE_ACT_CAT", "CPT_ENV_TYP", "TOP_PS5_TRG"]
    for lot in lecteur:
        df = lot.to_pandas()
        n += len(df)
        df = df[df["PRS_REM_TYP"] == 0]
        ctl.append(df.groupby(k_ctl, dropna=False)[MESURES].sum().reset_index())
        df = df.assign(prof=prof(df)).dropna(subset=["prof"])
        parts.append(df.groupby(CLES + ["prof"], dropna=False)[MESURES].sum().reset_index())
        if len(parts) >= 20:
            parts = [pd.concat(parts).groupby(CLES + ["prof"], dropna=False)[MESURES].sum().reset_index()]
        print(f"\r  {mois} : {n / 1e6:,.1f} M lignes, {time.time() - t0:,.0f} s", end="", flush=True)
    avert = gz.communicate()[1].decode("utf-8", "ignore").strip()
    octets = int((curl.communicate()[1] or b"0").decode().strip() or 0)
    # gunzip rend 2 sur un simple avertissement (« trailing garbage ignored ») : accepté, et noté dans pilote.csv
    if curl.returncode or gz.returncode not in (0, 2):
        raise SystemExit(f"\n{mois} : curl {curl.returncode}, gunzip {gz.returncode} {avert}")
    agg = pd.concat(parts).groupby(CLES + ["prof"], dropna=False)[MESURES].sum().reset_index().rename(columns=NOMS)
    ctl = pd.concat(ctl).groupby(k_ctl, dropna=False)[MESURES].sum().reset_index().rename(columns=NOMS)
    OUT.mkdir(parents=True, exist_ok=True)
    agg.to_parquet(OUT / f"agg_{mois}.parquet", index=False)
    ctl.to_parquet(OUT / f"ctl_{mois}.parquet", index=False)
    s = time.time() - t0
    r = {"mois": mois, "octets_gz": octets, "lignes": n, "lignes_agg": len(agg), "secondes": round(s, 1),
         "mo_par_s": round(octets / 1e6 / s, 2), "gunzip": f"{gz.returncode} {avert}"[:200], "lu_le": time.strftime("%Y-%m-%dT%H:%M:%S")}
    print(f"\n  {mois} : {octets / 1e9:.2f} Go en {s:,.0f} s ({r['mo_par_s']} Mo/s), {n:,} lignes → {len(agg):,}")
    log = OUT / "pilote.csv"
    pd.DataFrame([r]).to_csv(log, mode="a", header=not log.exists(), index=False)
    return r


STATMENS = "https://www.assurance-maladie.ameli.fr/sites/default/files/2025-12_depenses-par-type-de-risque_serie-mensuelle.zip"
LIEU = {"CD": "Dentistes", "SF": "Sages-femmes", "IDE": "Infirmiers", "MK": "Masseurs kinésithérapeutes",
        "MG": "dont généralistes"}


def rg_2025() -> dict:
    """Montants remboursés 2025 du régime général, cabinets libéraux, par profession (Statistique mensuelle)."""
    import io
    import zipfile
    from _commun import CACHE
    p = CACHE / "statmens" / "2025-12.zip"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(STATMENS, headers={"User-Agent": "Mozilla/5.0"})
        p.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    z = zipfile.ZipFile(p)
    nom = next(n for n in z.namelist() if n.startswith("2_Lieu"))
    v = pd.read_excel(io.BytesIO(z.read(nom)), sheet_name=0, engine="calamine", header=None)
    lab = v[0].astype(str).str.strip()
    return {k: float(v.loc[lab == x, 1].iloc[0]) for k, x in LIEU.items()}


# PRS_NAT de vaccination (modalités du descriptif) : actes (1959 VAX, 3360 VGP, 3415 RVA, 1982-83 HPV, 1925-26,
# 3119 grippe A), produits délivrés (3331 vaccin antigrippe, 3332 ROR, 3334-35 hémisphère Sud, 3374 kit), honoraire
# de dispensation (3379), 9211 (militaires / CRPCEN). L'IDE facture la vaccination en AMI (3111) : non isolable.
VACC = [1925, 1926, 1959, 1982, 1983, 3119, 3331, 3332, 3334, 3335, 3360, 3374, 3379, 3415, 9211]
K_PROF = ["flx_ann", "soi_ann", "ben_reg", "age", "sexe", "prof", "stj", "ppu", "top_ps5", "prs_nat"]
K_VACC = ["flx", "soi_ann", "soi_moi", "ben_reg", "exe_reg", "age", "sexe", "prof", "stj", "ppu", "prs_nat"]
M = ["qte", "nbr", "pai_mnt", "rem_bse", "rem_mnt", "dep_mnt"]


def controler():
    from _commun import controle, ecrire
    lus = sorted(p.stem[4:] for p in OUT.glob("agg_*.parquet"))
    prof, vacc = [], []
    for m in lus:
        a = pd.read_parquet(OUT / f"agg_{m}.parquet")
        vacc.append(a[a.prs_nat.isin(VACC)].groupby(K_VACC, dropna=False)[M].sum().reset_index())
        if m[:4] in ("2024", "2025"):
            prof.append(a.assign(flx_ann=a.flx // 100).groupby(K_PROF, dropna=False)[M].sum().reset_index())
    src = "Assurance maladie, Open DAMIR base complète, fichiers mensuels A{AAAAMM}.csv.gz (lus en flux)"
    dom = "DOM regroupés en une zone (code 5), non séparables ; PACA et Corse fusionnées (93) ; 99 = inconnu"
    cmd = "uv run python v2/besoin/donnees/damir.py --fenetre && uv run python v2/besoin/donnees/damir.py --controle"
    if prof:
        p = pd.concat(prof).groupby(K_PROF, dropna=False)[M].sum().reset_index()
        tot = sum(pd.read_parquet(OUT / f"agg_{m}.parquet").pai_mnt.sum() for m in lus if m[:4] in ("2024", "2025"))
        ck = [controle("damir_profils Σ dépense = Σ agg mensuels 2024–2025", p.pai_mnt.sum(), tot, seuil=1e-9,
                       source_publie="agg_AAAAMM (même lecture)")]
        ecrire(p, "damir_profils", licence="LO2", source=src, commande=cmd, dom=dom, controles=ck,
               millesime="flux " + ", ".join(m for m in lus if m[:4] in ("2024", "2025")),
               notes="filtre PRS_REM_TYP = 0 ; libéral = stj 1 et ppu 2, à appliquer à l'usage ; une année de soins "
                     "n'est complète qu'avec les flux des mois suivants (soins de déc. 2025 en partie absents)")
    v = pd.concat(vacc, ignore_index=True)
    ecrire(v, "damir_vaccination", licence="LO2", source=src, commande=cmd, dom=dom,
           millesime="flux " + ", ".join(lus), notes=f"PRS_NAT {VACC}")
    interne, ext = [], []
    for m in lus:
        a = pd.read_parquet(OUT / f"agg_{m}.parquet")
        c = pd.read_parquet(OUT / f"ctl_{m}.parquet")
        tot = c.pai_mnt.sum()
        for pr, g in a.groupby("prof"):
            interne.append({"controle": f"DAMIR {m} {pr} part de la dépense du fichier (PRS_REM_TYP = 0)",
                            "reconstruit": g.pai_mnt.sum(), "publie": tot, "ratio": g.pai_mnt.sum() / tot,
                            "ok": None, "source_publie": "ctl_AAAAMM (totaux du fichier entier)",
                            "note": "information, pas un contrôle : catégorie d'exécutant ≠ nature d'activité"})
    m25 = [m for m in lus if m.startswith("2025")]
    if len(m25) == 12:
        rg = rg_2025()
        a = pd.concat([pd.read_parquet(OUT / f"agg_{m}.parquet") for m in m25])
        a = a[(a.stj == 1) & (a.ppu == 2)]
        for pr, v in rg.items():
            r = a[a["prof"] == pr].rem_mnt.sum()
            ext.append({"controle": f"DAMIR 2025 {pr} remboursé libéral / RG cabinets libéraux", "reconstruit": r,
                        "publie": v, "ecart_rel": abs(r - v) / v, "ratio": r / v, "seuil": None, "ok": False,
                        "source_publie": "Cnam, Statistique mensuelle déc. 2025, 2_Lieu_execution (RG + SLM)",
                        "note": "périmètres différents (tous régimes contre RG) : pas un contrôle à 0,5 %"})
            print(f"  [info] {pr} : DAMIR {r:,.0f} / RG {v:,.0f} = {r / v:.3f}")
    log = pd.read_csv(OUT / "pilote.csv")
    meta = pd.DataFrame({"mois": lus})
    ecrire(meta, "damir/index", licence="LO2",
           source="Assurance maladie, Open DAMIR base complète, fichiers mensuels A{AAAAMM}.csv.gz (lus en flux)",
           millesime=f"mois de flux lus : {', '.join(lus)}", commande="uv run python v2/besoin/donnees/damir.py --fenetre",
           dom="DOM regroupés en une zone (code 5), non séparables ; PACA et Corse fusionnées (93)",
           controles=interne + ext,
           notes=f"{len(lus)} mois, {log.octets_gz.sum() / 1e9:.1f} Go lus en {log.secondes.sum() / 3600:.2f} h "
                 f"(médiane {log.mo_par_s.median():.2f} Mo/s) ; agg_AAAAMM et ctl_AAAAMM à côté de cet index")


def mois_de(arg: str) -> list[str]:
    if arg == "--fenetre":
        return FENETRE
    if "-" in arg:
        a, b = arg.split("-")
        return [str(p.strftime("%Y%m")) for p in pd.period_range(pd.Period(a, "M"), pd.Period(b, "M"), freq="M")]
    return [arg]


if __name__ == "__main__":
    if "--controle" in sys.argv:
        controler()
        raise SystemExit
    for m in [x for a in sys.argv[1:] for x in mois_de(a)]:
        if (OUT / f"agg_{m}.parquet").exists():
            print(f"  {m} : déjà agrégé, sauté")
            continue
        lire_mois(m)
