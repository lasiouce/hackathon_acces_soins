---
type: analysis
date: 2026-11-14
author: Claude
question: Le jumeau corrigé tient-il une seconde revue adversariale indépendante ?
headline: "Non. Les 6 constats soumis à réfutation sont confirmés, soit 4 défauts bloquants distincts : levier retraite (tranche 65+ ouverte, +41 % à Δ = 2), régulation qui fait encore varier le total (+254 dentistes), scénario passé à trajectory() qui écrase le scénario de base (quotas ×1,1 → −15 %), valeurs de sélecteur et de levier non validées (quotas ×110 → +5 millions)"
status: done
professions: [all]
hypothesis: axe 0
sources: [v2/jumeau (état du 2026-11-14 après corrections), v2/artifacts/a0_jumeau]
tags: [revue, axe0, jumeau, validation]
---

# Seconde revue adversariale du jumeau (axe 0)

> **Headline :** les 6 constats soumis à réfutation sont confirmés. Trois
> décrivent le même défaut du levier retraite, ce qui laisse 4 défauts
> bloquants distincts. Deux défauts de la première revue (2 et 4) ne sont
> corrigés qu'en partie, et un nouveau défaut vient d'une correction.

## Méthode
Même workflow que la première revue : 9 agents en lecture seule, 3 angles
(tests, physique, contrat), et pour chaque angle les 2 constats les plus
graves soumis à un agent chargé de les réfuter en exécutant le code. Les
chiffres sont mesurés par les agents ; leurs scripts sont dans
`/private/tmp/revue0`, hors du dépôt.

## Résultats

| # | Gravité | Défaut | Où | Preuve (mesurée) |
|---|---|---|---|---|
| 1 | **bloquant** | **Levier retraite.** Le masque `60 ≤ âge ≤ 65` inclut la tranche ouverte 65+. Son taux de sortie y est multiplié par (1 − Δ/5) de façon permanente, donc le séjour dépasse le report annoncé et devient infini pour Δ ≥ 5. Le correctif adopté le 2026-11-14 (e/(1+Δe), « reprise de l'observatoire ») **n'est pas appliqué** : le code contredit une décision inscrite. C7 compare à la v1, qui a le même masque, et ne peut donc pas le voir. *Trouvé indépendamment par les 3 angles.* | `modules/sorties.py:39` | dentistes : séjour en 65+ +1,31 an pour Δ = 1 ; effet en 2050 +3 137 contre +2 229 avec le correctif pour Δ = 2 (+41 %) ; Δ = 5 → +30 % contre +7 % |
| 2 | **bloquant** | **Le défaut 2 n'est corrigé qu'à moitié.** Dans la configuration réelle (`sector_table`, historique public présent), la régulation fait encore varier le total privé + public : un déplacement ne devrait pas changer le total. | `modules/regulation.py:42`, `history.py` | dentistes, 5 dép., 2050, sans plancher : **+254** personnes pour 4 704 déplacées ; kinés −474 (C2 publie lui-même 175 145 contre 174 665 sans le signaler) |
| 3 | **bloquant** | **Nouveau défaut, introduit par la correction du défaut 1.** `trajectory(until, scenario)` **remplace** le scénario de base de l'estimateur au lieu de s'y ajouter, et le paramètre `entrees.filiere` est perdu sans message. | `estimators.py:48,68` | dentistes, twin_of(StockFlowLocalPipeline) : `predict` 102 987 ; `trajectory(Scenario())` 82 374 ; quotas ×1,1 → **−15,2 %** face au tendanciel annoncé |
| 4 | **bloquant** | **Le défaut 4 n'est corrigé que pour les noms.** Ni les valeurs de sélecteur ni les plages de valeurs ne sont validées : un ciblage mal écrit rend le tendanciel sans erreur. | `scenario.py:69,110` | `{'profession': 'dentiste'}` → écart 0,0 ; `{'territory': 6}` → 0,0 (alors que '06' donne +129) ; quotas ×110 → **+5 085 033** dentistes |

**Non soumis à réfutation (plafond de 2 par angle) :**
- **Calibrage.** `stock_flow_rates` passe par `fit_rates`, qui suppose toujours un vieillissement de 1/5 par an, même pour les tranches communales (C10 incomplet).
- **Dépendances.** `build()` accepte une dépendance vers un flux de type Pool, ou vers un producteur muet une année donnée, puis `ctx.delta` lève un KeyError brut. Les diplômés ne sont pas accessibles par le contrat.

## Portée
- **Prototype (`v2/prototype/`).** Il est touché par les défauts 1, 2 et 4 :
  - son curseur retraite va jusqu'à +3 ans ;
  - la régulation est active pour SF, CD et MK ;
  - aucune borne n'est appliquée au serveur.

  Il n'est pas touché par le défaut 3, puisqu'il utilise StockFlowLocal et
  rappelle REG à chaque appel. **Ses chiffres retraite et régulation ne sont
  pas citables.**
- **Axe 5.** Si sa grille de sensibilité contient `decalage_retraite`
  (plage [0, 2] dans les décisions), l'indice de ce facteur est surestimé.
- **Axe 2.** Il n'appelle pas trajectory() sur une variante filière
  aujourd'hui (grep), mais le piège reste ouvert.

## ⚑ Ce qui pourrait rendre ce rapport faux
- La relecture porte sur l'état du code à 2026-11-14, après les
  corrections de l'axe 0.
- Les 2 constats non vérifiés n'ont pas été soumis à réfutation.

## → Ce que ça change
- **Le jumeau ne passe pas la seconde revue.** Les chiffres qui dépendent
  des leviers retraite et régulation ne sont pas citables tant que les
  défauts 1, 2 et 4 restent ouverts.
- **Les axes 2 et 5 continuent sur le tendanciel**, qui n'est pas affecté
  : C1 reproduit la v1 à l'identique.

## ? Pour la suite
| Point | Coût |
|---|---|
| Axe 0 : corriger les défauts 1–4, et ajouter pour chacun un test qui échoue avant la correction | ~1–2 h |
| Vérifier les 2 constats non réfutés | ~10 min |
| Troisième revue, après corrections | ~3 min machine |
