---
type: analysis
date: 2026-11-15
author: relecture axe 1 (lecteurs Haiku, vérificateurs Sonnet)
question: Les valeurs des fiches d'hyperparamètres de l'axe 1 sont-elles dans le texte intégral de leurs sources ?
headline: "29 paramètres relus : 20 confirmés, 8 corrigés dans leur fiche, 1 introuvable ; aucune valeur du code ne change, jumeau.check 18 sur 18"
status: done
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: les fiches lues en extrait contiennent des valeurs mal attribuées
sources: [DREES DD76, ER 1026, 1062, 1075, 1266, 1319, DREES 491, COR 2016 doc. 11, ONCD 2019-2022, CNOMK 2024, CNOP 2016/2024/2025, conventions CD 2023, avenant 6 IDE, avenant 7 MK, avenant 4 SF, IRDES QES 270, IRDES DRIMK, Cour des comptes 2024, IGAS 2022-027R, CNG 2018, arrêtés 2023-2024, SAE]
tags: [axe1, relecture, sources]
---

# Relecture en texte intégral des sources de l'axe 1

> **Headline :** 29 paramètres et 355 affirmations relus. Résultat : 20 paramètres confirmés, 8 corrigés dans leur
> fiche, 1 introuvable, aucune source entièrement inaccessible. **Aucune valeur du code ne change** : `jumeau.check`
> reste à 18 sur 18 et ses sorties sont identiques à la référence, hors temps de calcul.

## Question
Le statut de Home disait « sources à relire en texte intégral ». Chaque valeur des fiches `param-*` figure-t-elle dans
sa source, avec la bonne unité, le bon champ et la bonne année ? La source contient-elle une meilleure valeur ?
Registre : [[decisions]], entrées du 2026-11-15.

## Comment
- **Lecture.** 23 agents Haiku, un par source. Consigne : [`consigne-lecteur.md`](2026-11-15-axe1-relecture/consigne-lecteur.md).
  - Textes intégraux : 16 PDF téléchargés et convertis page par page. Les PDF de la DREES, que le site refuse à curl,
    ont été lus par WebFetch. Les classeurs DREES 491 et « pharma 2e et 3e cycle » ont été lus en local.
  - Résultat : 355 affirmations, dont 247 confirmées, 35 écarts, 67 introuvables et 6 inaccessibles.
  - JSON : [`lecteurs/`](2026-11-15-axe1-relecture/lecteurs/).
- **Vérification.** Chaque écart et chaque introuvable est passé par un vérificateur Sonnet, chargé de le réfuter
  (10 agents). Consigne : [`consigne-verificateur.md`](2026-11-15-axe1-relecture/consigne-verificateur.md).
  - Un écart n'est retenu que s'il survit.
  - 6 écarts ont été réfutés et 27 introuvables retrouvés, souvent dans une autre source de la même fiche.
  - JSON : [`verificateurs/`](2026-11-15-axe1-relecture/verificateurs/).
- **Impact.** `PYTHONPATH=v2 uv run python -m jumeau.check`, avant et après les changements.
  - L'âge d'entrée a été mesuré avec [`impact_age.py`](2026-11-15-axe1-relecture/impact_age.py).

## Résultat

| Paramètre (fiche) | Valeur de la fiche | Source principale | Verdict |
|---|---|---|---|
| age-entree-exercice | SF 24 · CD 26 · PH 27-29 ; étrangers 28 | DD76 tab. 12-13 | **confirmé** ; MK étrangers 26 ans ajouté (ER 1075 p. 2) |
| cd-regul-effet | non chiffré | mémoire Bahroun p. 53 | **confirmé** |
| cd-regul-regle | 1 pour 1, cédant ≥ 2 j/sem | convention CD 2023 art. 33.1, 35 | **confirmé** ; art. 35.5 = dérogation (code relibellé) |
| cd-specialisation-des | 9,1 % (2024) | arrêtés 2023-2024, CNG 2018 | **corrigé** : 2023 = 9,0 % (120 / 1 332) |
| cd-stock-specialistes | ODF 2 465 (5,3 %) | ONCD 2019-2022 | **corrigé** : 5,4 % |
| cessation-par-age | non publiée | DD76 tab. 11 ; ER 1062, 1075 | **corrigé** (libellé) : SF sans le sexe ; ancrages agrégés ajoutés |
| cumul-emploi-retraite | 0,8 · 4,7 · 1,8 · 1,5 % | COR 2016 doc. 11 ann. 2 | **confirmé** ; champ CARPIMKO et spécialistes notés *supposés* |
| diplomes-etrangers-flux | CD 1 300 · MK 2 200 · IDE 400 · PH 240 · SF 80 | ONCD, QE, CNOMK, CNOP, ER 1319 | **confirmé** (valeurs du code) ; étiquettes corrigées (CD *dérivé*, IDE 1 100 *supposé*, PH ≈ 237) |
| ide-abandon-1a | 12,0 % (2025) | DREES 491 | **confirmé** ; « quadruplé » → « triplé 2011-2021 » |
| ide-abandon-promotion | 25,0 % ; 11,9 % | DREES 491, ER 1266 | **confirmé** ; définition « sans report » jusqu'en 2021 |
| ide-regul-effet-densite | −25,57 / 100 000 | IRDES QES 270 p. 5 | **confirmé** ; page p. 3 ; repères 2012 = presse |
| ide-regul-regle | 1 pour 1 ; 2/3 de l'activité | avenant 6 IDE | **confirmé** |
| ide-rendement-diplomes | 0,72 | DREES 491 | **confirmé** ; « 76 % » = diplômés 2022 / inscrits 2019 |
| mk-age-retraite | 66,8-67,3 ans | CNOMK 2024 tab. 5, 7 | **confirmé** ; libellé « cessation d'activité » |
| mk-obligation-exercice | 2 ans, 6 000 actes | avenant 7 MK art. 4.1.1 | **confirmé** |
| mk-regul-effet | non chiffré | IRDES DRIMK, Cour 2024 | **corrigé** : sens établi (travail achevé), ampleur non publiée |
| mk-regul-regle | 1 pour 1, ≥ 1 200 actes | avenant 7 MK, CE 488665 | **confirmé** |
| mortalite | incluse dans la cessation | DD76, ER 1062/1075/1319 | **confirmé** |
| part-privee-salaries-sae | SF 19,8 · PH 29,4 · MK 44,3 · CD 2,2 % | SAE (jeu 708) | **confirmé** (codes ; parts *mesurées*, non recalculées) |
| ph-filiere-primo-inscrits | D 71,0 % … N = 3 044 | CNOP dépliant 2025 | **confirmé** |
| ph-internat-postes | 746 postes ; 536 internes | arrêté 06/12/2024 | **confirmé** |
| ph-part-privee-biologie | 55,8 % | CNOP 2025 | **confirmé** |
| ph-part-privee-etablissements | 28,6 % ; 30,0 % | CNOP 2016, 2024, 2025 | **corrigé** : unités, « 8 106 personnes » faux, ligne 2015 en double |
| ph-sorties-ordre | 3 902 radiations | CNOP Synthèse 2024 | **corrigé** : primo-inscrits − radiations = −975 |
| ph-taux-inscription-diplomes | 32,8 % | CNOP 2016 p. 6-7 | **confirmé** |
| regul-report-entrants | qualitatif | IRDES QES 270, Cour 2024 | **introuvable** : « contournement par le remplacement » et « deux tiers (EHESP) » |
| regul-theta-fuite | θ = 0,80 [0,74 ; 0,87] | rapport interne axe 3 N3 | **confirmé** |
| sf-regul-effet | non chiffré | IGAS 2022-027R, Cour 2024 | **corrigé** : le bilan GDR porte sur les aides, pas sur la régulation |
| sf-regul-regle | 1 pour 1 | avenant 4 SF art. 3.3 | **corrigé** : les entrées dérogatoires ne rendent pas de place (3.3.3 a-b) |

**Inaccessibles en partie, sans fiche entièrement bloquée :**
- base RegProf de la Commission européenne (1 309 reconnaissances UE, non vérifiable) ;
- communiqué DREES du 07/11/2023 ;
- Légifrance, page anti-robot : les textes ont été lus dans des reproductions JO.

**Impact sur le jumeau.**
- Les valeurs numériques du code sont toutes confirmées ou défendables : FLUX 1 300 / 2 200 / 400 / 240 / 80,
  PART_CUMUL, ABANDON (IDE 0,718 ; SF 0,0331 et L = 4, recontrôlés), θ 0,80.
- Les seuls changements sont de libellé, dans `regulation.py`, `etrangers.py` et `sorties.py` : `jumeau.check` passe
  à 18 sur 18 et donne les mêmes sorties.
- Écart mesuré mais non corrigé : l'âge d'entrée des diplômés à l'étranger, unique à 28 ans. N(2050) dans le scénario
  « étrangers × 2 » (*mesuré*) :

  | Profession | Âge de la source | Écart sur N(2050) |
  |---|---|---|
  | MK | 26 ans | 0 (même tranche) |
  | PH | 31 ans | −191 (−0,2 %) |
  | CD | 32 ans (ER 1026, contredit par DD76 : 28) | −1 369 (−1,3 %) |

  Le tendanciel ne bouge pas. Le corriger demande un paramètre par profession et une réécriture de C17. C'est ouvert
  dans le registre (`## Open`).

## ⚑ Ce qui pourrait fausser le résultat
- Les lecteurs Haiku ont souvent lu par mots-clés plutôt que page à page (« accès partiel » sur environ la moitié des
  sources). Un écart non signalé n'a pas été vérifié : les 247 « confirmés » n'ont pas eu de second passage.
- Les PDF à colonnes (CNOP) s'extraient mal. Les valeurs de camemberts n'ont été contrôlées que sur le rendu image par
  le vérificateur.
- Deux sources se contredisent elles-mêmes, et la fiche suit l'une des deux :
  - ONCD 2022 : 1 333 hors France p. 27, mais 1 321 d'après le tableau p. 28 ;
  - dénominateur odontologie : 1 332 (SNESUP, Weka) contre 1 322 (L'Étudiant).

## → Ce que ça change
- Toutes les fiches `param-*` : champ `relecture` et section datée. Le statut « sources à relire » de Home est levé.
- Code : libellés des modules `regulation`, `etrangers` et `sorties`, sans effet numérique.
- Module `regulation`, SF : la règle « 1 pour 1 » surestime la fermeture quand des entrées sont dérogatoires. Ces
  entrées ne sont pas modélisées (part inconnue).
- Article `v2/papers/axe1-hyperparametres/main.tex` : il dit déjà « dérogation, pas exemption ». La part CD 2023
  (9,0 %) et l'ODF 5,4 % y restent à reporter si l'article les cite.

## ? Suite
| Point | Prix |
|---|---|
| Âge d'entrée des diplômés à l'étranger par profession (dictionnaire + C17) | ≈ 30 min Claude |
| Second passage sur un échantillon des 247 « confirmés » (taux de faux confirmés) | ≈ 20 min Claude, ≈ 10 agents Haiku |
| Sourcer ou retirer le « contournement par le remplacement » (regul-report-entrants) | ≈ 20 min |
| Fichier annuel DREES 2025, tableau 1E (4 694 / 1 155 / 2 036) et 33 972 nouveaux inscrits | ≈ 10 min |
| Entrées dérogatoires SF : part observable ? | ≈ 1 h (données CNAM, sans doute non ouvertes) |
