---
type: fiche
axe: 1
id: param-cessation-par-age
parametre: "x_p(a, s, mode) — probabilité de cesser l'exercice entre t et t+1, par âge, sexe et mode d'exercice"
profession: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
module: sorties
valeur: "non publiée par la DREES (définition seule) ; à mesurer sur nos stocks RPPS 2012-2026"
unite: "probabilité annuelle"
incertitude: "la DREES calcule ces taux sur le panel RPPS 2016-2020 (DD76, tab. 11) sans en publier les valeurs ; décès inclus implicitement ; cumul emploi-retraite inclus (champ < 70 ans)"
source: "DREES, Les Dossiers n° 76 (mars 2021), tableau 11, p. 41-42 — https://drees.solidarites-sante.gouv.fr/sites/default/files/2021-03/DD76.pdf ; ER n° 1062 (IDE) et n° 1075 (MK), encadré 2 (bornes : aucune cessation avant 40 ans ; aucun exercice après 67 ans pour les IDE, après 70 ans pour les MK)"
millesime: "panel RPPS 2016-2020 (DD76) ; CNAM 2011-2015 (IDE, ER 1062) et 2011-2016 (MK, ER 1075) ; DADS 2011-2014"
statut: non mesurable
date: 2026-11-14
---

# x_p(a) — cessation par âge

**Mécanisme.** C'est le flux de sortie principal : N(a+1, t+1) = N(a, t) ·
(1 − x(a)) + entrées. La DREES le définit comme la « probabilité d'être en
activité une année et inactif la suivante ». Il inclut décès, retraite et
départs. Une « réserve » d'inactifs peut reprendre une activité.

**Statut.** « Non mesurable » à partir des publications : aucune valeur
numérique n'est publiée dans DD76, ER 1062, 1075 ou 1319. Le paramètre est
en revanche **mesurable** sur nos données. La v1 en dérive déjà un taux de
sortie apparent par cohorte (`sante/`), et le ROADMAP signale qu'il n'est
pas stationnaire.

**Comment le mesurer.**
- Taux apparent par cohorte sur `data/processed/stock.parquet` :
  x(a) = 1 − N(a+1, t+1) / N(a, t), au-dessus de 40 ans, là où les
  entrées sont négligeables (hypothèse de la DREES).
- ⚑ La classe « 65 ans et plus » est ouverte : on ne peut rien mesurer
  au-delà de 65 ans. Il faut l'annuaire santé individuel.
- Coût estimé : ~1 h (axe 0 ou axe 2).
