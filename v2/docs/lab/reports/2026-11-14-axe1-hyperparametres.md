---
type: analysis
date: 2026-11-14
author: Claude (session axe 1)
question: "Quels hyperparamètres propres à chaque profession peut-on sourcer et mesurer, avec quelle valeur ?"
headline: "27 fiches de paramètres : 19 sourcés, 1 mesuré, 1 supposé, 6 non mesurables ; seul effet de régulation chiffré = IDE (−25,57 IDEL / 100 000 hab., IRDES)"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "Chaque piste de l'axe 1 a au moins une source primaire chiffrée par profession concernée"
sources: [Ordre national des pharmaciens Panorama 2024-2025, DREES jeu 491 enquête Écoles, IRDES QES 270, avenants conventionnels IDE/SF/MK et convention CD, CNG arrêtés internat odontologie, DREES DD76, CNOMK 2024, COR 2016, data.gouv zonages]
tags: [axe1, parametres, fiches, regulation, pharmacie, odontologie, ifsi]
---

# Axe 1 — hyperparamètres sourcés par profession

> **Headline.** 27 fiches dans [`fiches/`](../fiches/) : 19 sourcées, 1
> mesurée, 1 supposée, 6 non mesurables. Les 4 pistes prioritaires sont
> couvertes pour chaque profession concernée. Le seul effet de la régulation
> chiffré dans la littérature concerne les IDE : −25,57 IDEL pour
> 100 000 hab. en zone sur-dotée, par rapport aux zones intermédiaires
> (IRDES, DiD, 2006-2016).

## Question
Quelles spécificités par profession le jumeau (axe 0) peut-il recevoir comme
paramètres nommés, sourcés et datés ? Voir la piste « Axe 1 » de
[ROADMAP](../../../ROADMAP.md).

## Correction de la note de cadrage
**L'obligation temporaire d'exercice de 2 ans concerne les kinés, pas les
dentistes.**
- Kinés : avenant 7, art. 4.1.1. Elle vise les MK entrés en formation à
  partir de 2023, donc un premier effet en 2027.
- Dentistes : la convention de 2023 ne prévoit que des engagements liés aux
  aides (CAICD sur 5 ans, CAMCD sur 3 ans) et le CESP pour les volontaires.
- Le tableau 13 du mémoire EHESP 2025 et le texte intégral de la convention
  dentaire concordent. Voir [[param-mk-obligation-exercice]].

## Résultat — paramètres × statut

Légende des statuts :
- **sourcé** : valeur lue dans une source primaire (éventuellement un ratio
  calculé à partir de deux nombres cités, signalé dans la fiche) ;
- **mesuré** : calculé par nous sur une donnée ouverte téléchargée ;
- **supposé** : valeur par défaut sans mesure ;
- **non mesurable** : aucune source chiffrée aujourd'hui (la fiche dit
  comment la mesurer).

| Piste | Profession | Fiche | Module | Valeur (résumé) | Millésime | Statut |
|---|---|---|---|---|---|---|
| 1 Régulation | IDE | [[param-ide-regul-regle]] | régulation | sur-dotée : 1 entrée pour 1 cessation ; ⅔ de l'activité en périphérie ; 27,4 % de la population | avenant 6 (2019) ; zonage 20/10/2026 | sourcé |
| 1 Régulation | IDE | [[param-ide-regul-effet-densite]] | régulation | −25,57 IDEL / 100 000 (−18,8 chez les < 40 ans) | 2006-2016 | sourcé |
| 1 Régulation | IDE | [[param-regul-theta-fuite]] | régulation | θ = 0,80 [0,74 ; 0,87] | 2004-2019 | supposé |
| 1 Régulation | SF | [[param-sf-regul-regle]] | régulation | sur-dotée : 1 pour 1 ; 12,2 % de la population | avenant 4 (2018), reconduit par l'avenant 7 (2023) | sourcé |
| 1 Régulation | SF | [[param-sf-regul-effet]] | régulation | direction seulement (inégalités en baisse 2016-2019) | 2016-2019 | non mesurable |
| 1 Régulation | MK | [[param-mk-regul-regle]] | régulation | non prioritaire : 1 pour 1 ; 26,5 % de la population | avenant 7 (2023) | sourcé |
| 1 Régulation | MK | [[param-mk-obligation-exercice]] | installation | 2 ans en zone (très) sous-dotée ou 2 ans en établissement | 2023, effet en 2027 | sourcé |
| 1 Régulation | MK | [[param-mk-regul-effet]] | régulation | non chiffré | — | non mesurable |
| 1 Régulation | CD | [[param-cd-regul-regle]] | régulation | non prioritaire : 1 pour 1 ; 4,8 % de la population ; spécialistes exemptés | convention 2023, effet au 01/01/2025 | sourcé |
| 1 Régulation | CD | [[param-cd-regul-effet]] | régulation | non chiffré ; borne haute ≈ 5 % du flux | — | non mesurable |
| 1 Régulation | SF, CD, MK, IDE | [[param-regul-report-entrants]] | régulation | destination des entrants bloqués : qualitative seulement | 2022-2024 | non mesurable |
| 2 Filières | PH | [[param-ph-filiere-primo-inscrits]] | filières | D 71,0 % · H 9,5 % · B 8,6 % · G 5,7 % · E 3,5 % · A 1,2 % · C 0,4 % | 1/1/2026 | sourcé |
| 2 Filières | PH | [[param-ph-part-privee-biologie]] | transitions | G privé 55,8 % | 1/1/2026 | sourcé |
| 2 Filières | PH | [[param-ph-part-privee-etablissements]] | transitions | H privé 28,6 % (Ordre), contre 17 % (DREES, axe 4) | 1/1/2026 | sourcé |
| 2 Filières | PH | [[param-ph-internat-postes]] | filières | 746 postes (biologie 266, pharmacie hospitalière 480) ; ≈ 14 % d'une promotion | rentrée 2025 | sourcé |
| 2 Filières | PH | [[param-ph-taux-inscription-diplomes]] | abandon | 32,8 % de non-inscrits à 3 ans | 2015 | sourcé |
| 3 Odontologie | CD | [[param-cd-specialisation-des]] | filières | 9,2 % d'une promotion ; ODF 52 · CO 25 · MBD 44 | 2024-25 | sourcé |
| 3 Odontologie | CD | [[param-cd-stock-specialistes]] | filières | ODF 5,3 % · CO 0,5 % · MBD 0,2 % du stock | 2022 | sourcé |
| 4 Abandon IFSI | IDE | [[param-ide-rendement-diplomes]] | formation | ρ = 0,72 (1 − ρ = 28,2 %) | entrée 2022 | mesuré |
| 4 Abandon IFSI | IDE | [[param-ide-abandon-promotion]] | abandon | 25,0 % (toutes interruptions) ; 11,9 % définitives | promotions 2024-2025 | sourcé |
| 4 Abandon IFSI | IDE | [[param-ide-abandon-1a]] | abandon | 12,0 % en 1re année | 2025 | sourcé |
| Suite | toutes | [[param-cessation-par-age]] | sorties | non publié par la DREES ; mesurable sur le RPPS | — | non mesurable |
| Suite | toutes | [[param-mortalite]] | sorties | incluse dans la cessation | — | non mesurable |
| Suite | toutes | [[param-age-entree-exercice]] | installation | SF 24 · CD 26 · PH 27-29 ans | RPPS 2020 | sourcé |
| Suite | toutes | [[param-cumul-emploi-retraite]] | sorties | CD 4,7 % · PH 1,8 % · MK + IDE 1,5 % · SF 0,8 % | 2015 | sourcé |
| Suite | MK | [[param-mk-age-retraite]] | sorties | 66,8-67,3 ans | 2019-2023 | sourcé |
| Suite | PH | [[param-ph-sorties-ordre]] | sorties | 3 902 radiations par an ; 18,4 % de 60 ans et plus | 2024 | sourcé |

**Trois résultats qui changent le modèle.**
1. **« 30 % d'abandon par an » chez les IDE n'a pas de source primaire.**
   - Le chiffre vient d'une réponse ministérielle (QO AN n° 101, 2023) qui
     ne cite aucune source.
   - Ce que mesure la DREES : 12-13,5 % d'interruptions en 1re année, et un
     rendement diplômés / entrants passé de 0,84 (avant 2019) à 0,72 (entrée
     2022).
   - La rupture coïncide avec Parcoursup (2019) et le gonflement des quotas.
2. **En pharmacie, 71 % des nouveaux inscrits entrent comme adjoints
   d'officine.** Avec A, B et C, plus de 81 % des primo-inscrits sont
   privés par construction. L'ambiguïté se concentre sur G et H (15 % du
   flux). La part privée de H diffère selon la source (17 % ou 28,6 %).
3. **La régulation ne touche pas toutes les professions de la même façon.**
   - Part de la population couverte : CD 4,8 %, SF 12,2 %, MK 26,5 %,
     IDE 27,4 %.
   - Les spécialistes dentaires sont exemptés.
   - Le seul effet causal publié (IDE) est une borne haute de l'effet
     national, car les zones témoins reçoivent le report.

## How
- **Données.** Les fiches citent chaque source avec son lien et son
  millésime.
- **Recherche.** Six recherches documentaires parallèles (textes de la
  régulation, effets, filières pharmacie, odontologie, IFSI, sorties).
  Les sources ont été ouvertes et leur texte extrait. Les notes brutes sont
  restées dans le dossier de travail de la session, hors dépôt.
- **Contrôle croisé.** Les communes en « remplacement seul » du fichier
  data.gouv concordent avec les fiches `data-zonage-*` de l'axe 4 (par
  exemple MK : 8,1 % de 35 002 communes ≈ 2 835, contre 2 836 géocodes
  CartoSanté).
- **Seul calcul propre, ρ_IDE.** Script ci-dessous, rejoué sur le fichier
  DREES. Il reproduit le tableau de la fiche à 0,1 point près. Il donne
  aussi 81,4 % pour l'entrée 2018, contre 81 % publié par l'ER 1266.

```python
# ρ_IDE = diplômés(t+3) / inscrits en 1re année(t)
# Fichier : DREES jeu 491, « Séries longues – 1966-2025.xlsx »
# (https://data.drees.solidarites-sante.gouv.fr/explore/dataset/491_la-formation-aux-professions-de-sante/),
# champ France métropolitaine et DROM.
# Usage : python3 -I ide_rendement.py <series_longues.xlsx>
import sys
import pandas as pd

def serie(f, onglet):
    d = pd.read_excel(f, onglet, header=None)
    annees = [int(float(str(a).rstrip('*'))) if str(a).rstrip('*').replace('.', '').isdigit() else None
              for a in d.iloc[4]]
    ligne = d[d[1].astype(str).str.strip() == "Infirmiers diplômés d'État"].iloc[0]
    return {a: int(v) for a, v in zip(annees, ligne) if a and str(v).strip() not in ('-', 'nan')}

f = sys.argv[1]
dip, ins = serie(f, 'Diplomes_an'), serie(f, 'Inscrits1ere_an')
print('entree_t,inscrits_1A,diplomes_t+3,rho,1-rho')
for t in sorted(ins):
    if t + 3 in dip:
        r = dip[t + 3] / ins[t]
        print(f'{t},{ins[t]},{dip[t+3]},{r:.3f},{1-r:.1%}')
```

## ⚑ What could make it wrong
- **Filières pharmacie.**
  - φ décrit la *section d'inscription*, pas l'employeur. Une partie de
    l'industrie ne s'inscrit pas à l'Ordre, donc φ_B est sous-estimé.
  - L'extraction texte des camemberts de l'Ordre inverse A et B : les
    valeurs ont été relues sur le rendu graphique.
- **Abandon IFSI.**
  - Il n'y a pas de suivi individuel : la DREES raisonne sur des promotions
    théoriques.
  - La définition change en 2022 (toutes interruptions contre définitives),
    puis le questionnaire change en 2025.
- **Régulation, textes de méthode.** Les arrêtés de méthodologie du zonage
  (2020, 2024) et le texte au JO de l'avenant 7 SF sont cités par les ARS
  mais n'ont pas été ouverts.
  - L'avenant 11 IDE (2026) pourrait modifier la règle : non vérifié.
- **Régulation, effet.** L'effet IDE porte sur le zonage de 2011. Rien de
  chiffré ne couvre la période après 2019, ni les SF, MK ou CD.
- **Données anciennes.** Le cumul emploi-retraite date de 2015, ε_PH aussi.

## → What it changes
- **Axe 0, module `regulation`.**
  - La règle « entrées ≤ sorties » est confirmée pour les 4 professions,
    avec leurs types de zones.
  - Il faut ajouter :
    - l'exemption des spécialistes CD ;
    - la règle des deux tiers (IDE) ;
    - l'obligation d'exercice MK à partir de 2027 ;
    - θ et ψ comme paramètres de scénario.
- **Axe 0, modules `formation`, `abandon` et `filières`.**
  - ρ_IDE remplace un abandon supposé.
  - φ_PH et σ_CD alimentent le module `filières`.
- **Axe 3.** L'IRDES −25,57 / 100 000 est une seconde cible pour N3 IDE.
  Les fiches SF et MK décrivent les DiD à construire.
- **Axe 5.** Plages proposées : θ ∈ [0,5 ; 1], ψ en 3 variantes, ρ_IDE ∈
  [0,72 ; 0,84], φ_D ∈ [0,66 ; 0,75].
- **Ancienne v1, levier L18 SF.** Le texte est trouvé (avenant 4, art. 3.3).
  Ce n'est plus « assumed ».

## ? Next
| Item | Cost |
|---|---|
| Ouvrir les arrêtés de méthodologie du zonage (IDE 2020 ; SF, MK, CD 2024) et l'avenant 7 SF au JO | ~30 min (Claude) |
| Vérifier l'avenant 11 IDE (2026) : la règle en zone sur-dotée est-elle modifiée ? | ~20 min (Claude) |
| Mesurer x_p(a) sur `stock.parquet` (taux apparent par cohorte au-dessus de 40 ans) | ~1 h (axe 0 ou 2) |
| DiD SF et MK sur leurs zonages (même protocole que N3) | ~3 h chacun (axe 3) |
| Postes DES odontologie 2019-2022 et 2025, relevés à la main sur Légifrance | ~20 min (humain) |
| ε_PH récent : primo-inscrits de l'Ordre / inscrits en 6e année (fichier local) | ~30 min |
