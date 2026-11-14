"""EXPLORATOIRE (hors protocole, écrit après avoir vu l'échec de T1 dans validation.did). Ne valide rien.

Deux lectures de l'échec du test de tendances parallèles pour E1 (infirmiers) :
  1. tendance pré-période linéaire extrapolée : β corrigé = β − pente_pre × (moy(post) − moy(pre))
  2. borne « relative magnitudes » (Rambachan & Roth 2023, M̄ = 1) : chaque variation annuelle de la
     violation après 2008 est au plus la plus grande variation annuelle observée avant ; le biais sur la
     moyenne post est donc au plus M̄ · max|ΔD_pre| · moy(t − 2008).
Run : PYTHONPATH=v2 uv run --with scipy python -m validation.did_explore
"""
import json

import numpy as np

from validation.did import OUT, cells, diff, did

PRE, POST, REF = list(range(2004, 2009)), list(range(2012, 2020)), 2008


def main() -> None:
    Y, _ = cells("infirmiers-liberaux", "z_infi", ("3", "5"), REF)
    D, _ = diff(Y, "5", "3", REF)
    m = D[PRE + POST].dropna()
    beta = did(m, PRE, POST)
    x = np.array(PRE, float)
    pre_mean = m[PRE].mean(0).to_numpy()
    slope = float(np.polyfit(x, pre_mean, 1)[0])
    corr = beta["est"] - slope * (np.mean(POST) - np.mean(PRE))
    dmax = float(np.abs(np.diff(pre_mean)).max())
    bias = dmax * np.mean(np.array(POST) - REF)
    out = {"beta": beta, "pente_pre_par_an": slope, "beta_corrige_tendance_lineaire": corr,
           "max_variation_annuelle_pre": dmax, "borne_biais_RR_Mbar1": bias,
           "intervalle_RR_Mbar1": [beta["lo"] - bias, beta["hi"] + bias]}
    (OUT / "did_explore.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
