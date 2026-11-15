"""Manifeste des tables du module de besoin (axe 4) : licence, chemin, commit ou non, source, DOM, contrôles.

Run (racine du dépôt) : uv run python v2/besoin/donnees/manifest.py   → v2/besoin/donnees/MANIFEST.md et
v2/besoin/donnees/controles.csv (tous les contrôles de totaux, une ligne chacun).

Lit les fiches `*.meta.json` écrites par `_commun.ecrire` dans v2/data/processed/besoin/ (Licence Ouverte, commité)
et v2/data/odbl/besoin/ (ODbL, ignoré par git), plus le journal des mois d'Open DAMIR (damir/pilote.csv).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _commun import OUT_LO, OUT_ODBL, ROOT  # noqa: E402

ICI = Path(__file__).resolve().parent


def main():
    metas = [json.loads(p.read_text(encoding="utf-8")) for d in (OUT_LO, OUT_ODBL, OUT_LO / "damir")
             if d.exists() for p in sorted(d.glob("*.meta.json"))]
    ctl = pd.DataFrame([{"table": m["table"], **c} for m in metas for c in m["controles"]])
    ctl.to_csv(ICI / "controles.csv", index=False)
    out = ["# Manifeste — module de besoin, axe 4 (données)", "",
           "Généré par `uv run python v2/besoin/donnees/manifest.py`. Une ligne par table. Les tables ODbL ne sont pas",
           "commitées (décision de licence ouverte, registre § Open) : les reconstruire avec leur commande.", "",
           "| Table | Chemin | Lignes | SHA-256 (16) | Licence | Commitée | Source | Millésime | DOM | Contrôles (ok / total) | Commande |",
           "|---|---|---:|---|---|---|---|---|---|---|---|"]
    for m in metas:
        c = m["controles"]
        v = [x for x in c if x.get("ok") is not None]  # ok = None : ligne d'information, sans verdict
        ok = f"{sum(bool(x['ok']) for x in v)} / {len(v)}" + (f" (+{len(c) - len(v)} info)" if len(c) > len(v) else "") \
            if c else "—"
        out.append(f"| `{m['table']}` | `{m['chemin']}` | {m['lignes']} | `{m['sha256_16']}` | {m['licence']} | "
                   f"{'oui' if m['commite'] else '**non**'} | {m['source']} | {m['millesime']} | {m['dom']} | {ok} | "
                   f"`{m['commande']}` |")
    log = OUT_LO / "damir" / "pilote.csv"
    if log.exists():
        p = pd.read_csv(log)
        out += ["", "## Open DAMIR : mois lus en flux", "",
                "Licence Ouverte 2.0, agrégats commités dans `v2/data/processed/besoin/damir/` ; aucun CSV brut écrit.", "",
                "| " + " | ".join(p.columns) + " |", "|" + "---|" * len(p.columns)]
        out += ["| " + " | ".join(map(str, r)) + " |" for r in p.itertuples(index=False)]
    info = ctl[ctl.ok.isna()] if len(ctl) else ctl
    ctl = ctl[ctl.ok.notna()].assign(ok=lambda x: x.ok.astype(bool)) if len(ctl) else ctl
    if len(ctl):
        ec = ctl.dropna(subset=["ecart_rel"]) if "ecart_rel" in ctl else ctl
        out += ["", "## Contrôles de totaux", "",
                f"{int(ctl.ok.sum())} contrôles réussis sur {len(ctl)} (seuil 0,5 % sauf mention) ; détail dans "
                "`controles.csv`. Échecs :", ""]
        bad = ctl[~ctl.ok]
        out += [f"- `{r.table}` — {r.controle} : écart {r.ecart_rel:.2%}" if pd.notna(r.get("ecart_rel")) else
                f"- `{r.table}` — {r.controle}" for _, r in bad.iterrows()] or ["- aucun"]
        if len(ec):
            out += ["", f"Écart relatif maximal : {ec.ecart_rel.max():.3%} ; médian : {ec.ecart_rel.median():.4%}."]
    if len(info):
        out += ["", f"Lignes d'information sans verdict : {len(info)} (dans `controles.csv`, colonne `ok` vide)."]
    (ICI / "MANIFEST.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"MANIFEST.md : {len(metas)} tables, {len(ctl)} contrôles ({int(ctl.ok.sum()) if len(ctl) else 0} ok)")


if __name__ == "__main__":
    main()
