---
date: 2026-11-14
statut: "remplacé le 2026-11-15 par 2026-11-15-besoin-derivation.md et 2026-11-15-besoin-plan.md (survit comme M1 + transferts, corrigé)"
headline: "Besoin = habitants × profil d'âge du recours ; un transfert de tâches déplace une part du besoin, il ne crée aucun professionnel"
---

# Module de besoin : plan

> **Remplacé le 2026-11-15** par la [dérivation du besoin](2026-11-15-besoin-derivation.md) et le [plan par axes](2026-11-15-besoin-plan.md). Gardé tel quel ; ses corrections sont au §9 de la dérivation.

**ETA (temps Claude, non calibré) :** ~1 h 30 (1 h–2 h 30), dont ~30 min pour le test d'abandon, qui peut tout arrêter.

**Portée en une ligne :** rendre répondable la question du sujet, « combien de spécialistes à Clermont-Ferrand en 2035
si les pharmaciens peuvent vacciner ? », sans changer la projection des effectifs.

## Contrainte, en unités
- **Utilité pour la décision.** Le levier « transfert de tâches » produit aujourd'hui 0 effet : il est classé « pas dans le
  modèle » dans la carte et dans le compilateur. Cible : ≥ 3 leviers de transfert branchés de bout en bout (L23 vaccination en
  officine, L25 IPA, L27 accès direct au kiné), chacun avec sa source ou l'étiquette « supposé ».
- **Latence.** Le besoin est une multiplication après coup sur la population déjà chargée : < 5 ms ajoutées au recalcul
  (budget < 2 s, carte < 150 ms).
- **Boîte blanche.** Un paramètre par profession et par tranche d'âge, lu dans un fichier ouvert et daté.

## Alternative la moins chère, dérivée avant de lire l'existant
**Besoin ∝ habitants.** C'est déjà ce que fait la densité pour 100 000 depuis 23ed102 : le « ratio offre / besoin » vaut
densité / densité 2026. Coût nul.

Ce qu'elle ne sait pas faire :
1. **Le vieillissement.** Une population qui vieillit consomme plus de soins infirmiers et de kinésithérapie à effectif égal.
2. **Le transfert de tâches.** Pour le représenter, il faut un besoin par profession qu'on peut déplacer de l'une à l'autre.

## Forme retenue (ansatz)
- Besoin d'une profession p, sur un territoire T, l'année t :
  `B(p,T,t) = Σ_âge pop(T,t,âge) × r(p,âge)`
- `r(p,âge)` est le recours par habitant et par tranche d'âge, en 2026, pour la profession p. Il est **mesuré**, depuis l'Open
  DAMIR (actes remboursés par spécialité d'exécutant et tranche d'âge du bénéficiaire, Assurance maladie, open data). Il est
  supposé constant après 2026 : le levier L31 de la v1 (dérive du recours) reste hors du périmètre.
- **Indice de couverture** : `C(p,T,t) = [offre(p,T,t) × activité / B(p,T,t)] / [offre(p,T,2026) / B(p,T,2026)]`. Il vaut 1 en
  2026. C < 1 signifie une couverture moindre qu'aujourd'hui, dans le lexique neutre.
- **Transfert de tâches** (levier τ) : une part `s` du besoin de la profession A passe à la profession B à partir de la date
  de décision :
  - `B'(A) = B(A) × (1 − s·a)`, et `B'(B) = B(B) + s·a·B(A) × k`.
  - `a` est la part du besoin de A concernée par l'acte transféré, par exemple la vaccination dans l'activité des infirmiers.
  - `k` convertit le temps de l'acte de la profession A à la profession B.
  - `s` est le levier. `a` et `k` viennent d'une source, ou sont étiquetés « supposé ».
- **Les effectifs projetés ne changent pas.** C'est voulu : le jumeau ne modélise pas une installation qui répondrait au
  besoin. La décision N9 de l'axe 3 a mesuré un effet nul de la densité sur les installations.

## Verdict
**À construire, sous réserve du test d'abandon.** La forme proportionnelle aux habitants survit comme cas limite (r constant
avec l'âge). Elle est remplacée seulement si le vieillissement change matériellement l'indice.

## Test d'abandon (~30 min)
Calculer `B` pour les infirmiers et les kinés avec les profils Open DAMIR, et le comparer au besoin proportionnel aux
habitants en 2050, par département.
- Si l'écart est inférieur à 2 % dans plus de 90 % des départements, la pondération par âge est abandonnée. On garde la
  densité, et le module se réduit aux transferts de tâches.
- Si les profils par âge ne sont pas trouvables en données ouvertes pour une profession, elle reste au besoin proportionnel
  aux habitants, étiquetée « supposé ».

## Dans le périmètre
- `v2/besoin/` : `profil_recours.py`, qui construit `r(p,âge)` depuis l'Open DAMIR, et `besoin.py`, qui calcule `B`, `C` et
  les transferts.
- Sorties d'API `besoin`, `couverture`, `couverture_base`.
- Une vue de carte « Couverture du besoin 2050 », un repère dans la fiche, une ligne dans le mode expert.
- Leviers L23, L25 et L27 dans la famille de contexte « Transferts de tâches ». Le glossaire du compilateur les retire de
  « non modélisés » et les fait pointer vers ces leviers, avec la même mesure à l'aveugle avant et après.

## Hors périmètre (non-objectifs nommés)
- Une rétroaction du besoin sur les installations ou les départs (N9 : effet nul mesuré).
- Les prix, les tarifs, le reste à charge.
- La dérive du recours par âge (L31).
- La médecine générale (exclue du sujet).
- Les spécialistes, qui sont en phase 2. Pour eux, seul le côté « source » d'un transfert est porté, à titre de contexte.
- Les communes : population communale non chargée.

## Critères d'acceptation (vérifiables)
1. Avec r constant, `C` = densité / densité 2026, à 1e-9 près. Le cas limite est reproduit.
2. Avec tous les τ à 0, les effectifs et les densités sont identiques à 23ed102.
3. Conservation : `ΣB` avant et après un transfert diffère exactement de `s·a·B(A)·(k − 1)`, à 1e-6 près.
4. Trois leviers de transfert sont branchés de bout en bout : API, carte, fiche, export et compilateur. Chacun a une source
   ou porte « supposé » ; aucune valeur n'est inventée sans cette étiquette.
5. Le recalcul de la carte reste sous 150 ms au 95ᵉ centile (mesuré, n ≥ 30).
6. La phrase « combien de kinés à Clermont-Ferrand en 2035 si l'accès direct est généralisé ? » donne un effectif inchangé et
   un indice de couverture modifié, et l'écran le dit en clair.

## Ce qui prouverait que ce plan a tort
- Le test d'abandon (ci-dessus).
- Si `a` ou `k` ne sont sourçables pour aucun des trois transferts, les leviers n'afficheraient que des hypothèses. Il
  vaudrait alors mieux les laisser en « pas dans le modèle », avec la raison.
