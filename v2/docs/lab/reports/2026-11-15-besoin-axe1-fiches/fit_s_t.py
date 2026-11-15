"""Montée en charge s(t) de la vaccination antigrippale en officine (L23).

Entrée : graphique n° 10 du rapport de la Cour des comptes « La politique de vaccination
depuis 2018 » (2026-09), fichier G10.csv de l'archive open data
https://www.ccomptes.fr/sites/default/files/2026-09/Open-data-RPT-EPP-Politique-vaccinale.zip
(injections antigrippales par catégorie, SNDS, 2018-2024). Le CSV n'est pas commité.

Usage : python3 -I fit_s_t.py chemin/vers/G10.csv
Sortie : parts par catégorie, puis s_inf et tau de s(t) = s_inf (1 - exp(-(t - t0)/tau))
par moindres carrés sur grille, pour plusieurs t0.
"""
import csv, math, sys

rows = list(csv.reader(open(sys.argv[1], encoding='utf-8')))
yrs = [int(y) for y in rows[0][1:]]
ph, ide, med, aucun = ([float(x) for x in r[1:]] for r in rows[1:5])
tot = [a + b + c + d for a, b, c, d in zip(ph, ide, med, aucun)]
print('an total PH% IDE% MED% aucun% medicaux(MED+aucun)%')
for i, y in enumerate(yrs):
    print(y, int(tot[i]), *(round(100 * v[i] / tot[i], 1) for v in (ph, ide, med, aucun)),
          round(100 * (med[i] + aucun[i]) / tot[i], 1))
s = [p / t for p, t in zip(ph, tot)]
for t0 in (2017.75, 2018, 2018.5, 2019):
    pts = [(y, v) for y, v in zip(yrs, s) if y > t0]
    best = None
    for si in range(600, 1201):
        for ti in range(20, 1501):
            sinf, tau = si / 1000, ti / 100
            e = sum((sinf * (1 - math.exp(-(y - t0) / tau)) - v) ** 2 for y, v in pts)
            if best is None or e < best[0]:
                best = (e, sinf, tau)
    print('t0=%s s_inf=%.3f tau=%.2f ans rmse=%.4f n=%d'
          % (t0, best[1], best[2], math.sqrt(best[0] / len(pts)), len(pts)))
