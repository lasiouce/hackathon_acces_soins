---
parametre: N_liberal_commune_age
profession: IDE;MK;CD
module: etat (commune)
valeur: "IDE 2004–2025, MK 2005–2025, CD 2006–2025 ; 5 tranches d'âge ; Marseille par arrondissement (2010–2025)"
unite: libéraux actifs au 31/12 (FNPS/SNDS)
incertitude: "Σ communes vs RPPS libéral + mixte, même année, 2025 : MK −3,2 %, CD −0,8 % ; IDE vs SNDS 2023 : +4,7 % ; ordre des lignes TJS inféré (contrôlé) ; SF illisibles"
source: "CartoSanté (Atlasanté) TJS *_popage, référentiels com2026 et arm2026 ; table v1 data/processed/stock_commune.parquet"
millesime: "extraits 2026-11-13 et 2026-11-14"
statut: mesuré
---

# Stock libéral par commune × âge — série 2004–2025

Table `v2/data/processed/commune_stock.parquet` (`estime = True` pour les restes du dép. 13). Contrôles :
`commune_checks.csv`. Script `v2/data/build_commune.py`. Rapport : [grain communal](../reports/2026-11-14-axe4-grain-communal.md).
