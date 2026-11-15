---
type: fiche
axe: 1
id: param-mortalite
parametre: "μ_p(a, s) — mortalité des professionnels en exercice"
profession: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
module: sorties
valeur: "non séparée : incluse dans la cessation x_p(a) par la DREES"
unite: "quotient annuel de décès"
incertitude: "aucune table spécifique ni surmortalité publiée pour ces professions ; aucun ordre de grandeur sourcé ici (tables Insee à lire si le module la sépare)"
source: "DREES, Les Dossiers n° 76 (2021), ER n° 1062, 1075, 1319 : aucune occurrence de mortalité au sens démographique (vérifié par recherche plein texte)"
millesime: "2018-2024"
statut: non mesurable
relecture: "2026-11-15 : confirmé"
date: 2026-11-14
---

# μ_p — mortalité

**Mécanisme.** Le décès est une sortie du stock. Les modèles de la DREES ne
le séparent pas de la cessation : une personne active en t et inactive en
t+1 est sortie, quelle qu'en soit la cause.

**Décision de modélisation proposée.** Ne pas créer de module mortalité
séparé. μ reste inclus dans x_p(a) ([[param-cessation-par-age]]). Une
séparation n'aurait de sens que pour un scénario agissant sur la seule
mortalité (choc sanitaire), qui n'est pas au programme.

**Comment le mesurer si nécessaire.** Appliquer les quotients de mortalité
Insee par âge et sexe (tables de mortalité annuelles, ou hypothèses
d'Omphale). En l'absence de source, l'hypothèse de non-surmortalité
professionnelle est *supposée*.

## Relecture en texte intégral (2026-11-15)

Verdict : **confirmé** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- Aucune occurrence de mortalité au sens démographique dans DD76, les ER 1062 et 1075, ni l'ER 1319 : confirmé en texte intégral.
