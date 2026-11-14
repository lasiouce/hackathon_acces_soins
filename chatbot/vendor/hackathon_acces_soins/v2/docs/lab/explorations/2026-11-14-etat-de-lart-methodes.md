---
type: exploration
date: 2026-11-14
author: Claude
status: done
headline: "Le gain viendra d'abord de meilleurs modèles statistiques sur la même structure transparente (cohortes par composantes, bayésien hiérarchique), puis de données de flux ciblées, et presque pas de nouveaux hyperparamètres. Chaque brique proposée a une référence publiée et un contrôle qu'un statisticien peut refaire"
professions: [all]
tags: [état-de-l'art, méthodes, axe2, axe3, boîte-blanche]
---

# Modèles vérifiables pour projeter l'offre de soins : faut-il plus de données, plus d'hyperparamètres ou de meilleurs modèles ?

**Question de l'utilisateur·rice (2026-11-14).** Mettre l'accent sur une recherche
méthodologique poussée, avec des modèles **surtout pas boîte noire**, vérifiables et
validables facilement par n'importe quel statisticien. Faut-il plus de données, plus
d'hyperparamètres, de meilleurs modèles ?

**Provenance.** Les références ci-dessous viennent de recherches web du 2026-11-14
(arXiv et revues). Elles ont été **lues au niveau du résumé ou d'extraits, pas en texte
intégral**. Un chiffre tiré d'une référence est marqué *cité* ; un chiffre de notre dépôt
est marqué *mesuré*, avec le rapport d'où il vient. Toute référence doit être lue en
entier avant d'entrer dans un prétirage (`refs.bib`).

## 1. Diagnostic : d'où vient notre erreur aujourd'hui (mesuré)

| Symptôme | Mesure | Source |
|---|---|---|
| L'erreur par département dépasse de loin l'erreur nationale : c'est la **répartition territoriale** qui domine | MAPE dép. 8,08 % ; erreur nationale bien plus faible avant la correction | `docs/lab/reports/2026-11-13-k1-backtest.md` |
| **Biais national** : entrées en hausse, et activité au-delà de 65 ans | entrées 25–39 ans et 65+ sous-estimées (+5 217 spécialistes de 35–39 ans en 2026) | `docs/lab/reports/2026-11-13-pipeline-entries.md` |
| **Petits effectifs** à la commune | bruit ≈ ±45 % pour N = 5 (dérivé, 1/√N) | `docs/lab/decisions.md` (v1) |
| **2050 ne se backteste pas** | données 2012–2026, horizon testable ≈ 10 ans | `v2/ROADMAP.md`, axe 3 |
| Les **5 variantes de l'axe 2 sont toutes des stock-flux** ; les écarts entre elles sont faibles | voir le rapport de l'axe 2 | `v2/docs/lab/reports/` (axe 2) |
| Le jumeau a eu des défauts silencieux, attrapés par deux revues adversariales | 6 puis 4 défauts bloquants | `v2/docs/lab/reports/2026-11-14-revue-adversariale-axe0*.md` |

## 2. Réponse courte

1. **De meilleurs modèles d'abord, mais sur la même structure.** On garde l'identité
   comptable des cohortes par composantes : stock(t+1) = stock(t) + entrées − sorties.
   Elle est connue, pas apprise, donc transparente par construction. On remplace les
   taux estimés « à la main » (moindres carrés, rétrécissement ad hoc de poids 200,
   supposé) par des **modèles statistiques explicites** : bayésiens hiérarchiques avec
   des a priori écrits, une incertitude propagée, et des contrôles standard. C'est ce qui
   attaque nos trois symptômes : répartition territoriale, petits effectifs, non-stationnarité.
2. **Des données de flux ciblées ensuite**, pas « plus de données » en général. Ce qui
   manque, ce sont les données qui identifient les flux du modèle :
   - installations et cessations par commune ;
   - origine du diplôme (France ou étranger) ;
   - inscrits par région de formation ;
   - âge × sexe des infirmiers selon le secteur.
3. **Presque pas de nouveaux hyperparamètres.** Un paramètre que les données
   n'identifient pas n'améliore pas la prévision. Il élargit seulement l'incertitude
   honnête, ou la cache s'il est fixé à la main. On ajoute un paramètre seulement si deux
   conditions sont remplies :
   - **il porte un levier** de politique publique, ce qui est le rôle de l'axe 1 ;
   - **l'analyse de sensibilité montre qu'il bouge la sortie**, ce qui est le rôle de
     l'axe 5.

## 3. État de l'art, par brique du jumeau

### 3.1 Projections des effectifs de santé : la pratique courante
- **OCDE**, revue de 26 modèles de projection dans 18 pays : Ono, Lafortune et
  Schoenstein, *OECD Health Working Paper* n° 62, 2013.
  [oecd.org](https://www.oecd.org/social-issues-migration-health/health-workforce-planning-in-oecd-countries_5k44t787zcwb-en)
  · [EconPapers](https://econpapers.repec.org/RePEc:oec:elsaad:62-en)
- **Revue systématique 2010–2023** : Lee et al., *Human Resources for Health*, 2024.
  Elle trouve des modèles en stock-flux, des microsimulations et des simulations par
  cohortes, constate **un manque de standardisation dans la description des méthodes**,
  et propose une grille de reporting.
  [PMC11025158](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11025158/)
  - → **À reprendre** comme grille de nos prétirages : c'est exactement le critère
    « vérifiable par un statisticien ». Le décompte « n = 40 stock-flux » d'un extrait
    reste à vérifier dans le texte intégral.
- **DREES**, Dossier n° 76 (2021) : modèle par composantes, et microsimulation pour les
  seuls médecins (`docs/lab/explorations/drees-projections-and-apl.md`).
  [DD76.pdf](https://drees.solidarites-sante.gouv.fr/sites/default/files/2021-03/DD76.pdf)

### 3.2 Cohortes par composantes en bayésien, y compris pour de petites zones
C'est la piste principale : même structure que notre jumeau, mais estimée et
probabilisée.
- **Alexander & Alkema**, modèle bayésien contraint de cohortes par composantes pour des
  populations infranationales avec peu de données, validé sur le recensement kényan.
  [arXiv 2102.06121](https://arxiv.org/pdf/2102.06121)
- **Bryant & Zhang**, *Bayesian Demographic Estimation and Forecasting* (Chapman &
  Hall/CRC, 2018) : estimation et prévision réunies, pour des séries isolées ou des
  systèmes démographiques entiers, avec des mesures détaillées d'incertitude.
  [éditeur (revendeur)](https://www.abbeys.com.au/book/bayesian-demographic-estimation-and-forecasting.do)
  · version petites zones : Zhang, Bryant & Nissen, « Bayesian small area demography »,
  *Survey Methodology* 2019.
  [Statistique Canada](https://www150.statcan.gc.ca/n1/pub/12-001-x/2019001/article/00001-eng.htm)
  · article préalable [PKU](https://fem.pku.edu.cn/docs/20190604105919231342.pdf)
  - Un paquet R associé, `bage`, a une vignette « Bayesian workflow » ; son lien avec
    Bryant n'est pas vérifié.
    [vignette](https://mirror.uned.ac.cr/cran/web/packages/bage/vignettes/vig5_workflow.html)
- **Goes & Engelhardt**, projections bayésiennes par âge, en cohortes par composantes,
  pour de petites régions, *Demographic Research* 54(23).
  [demographic-research.org](https://www.demographic-research.org/articles/volume/54/23)
- **Peterson et al.**, modèle bayésien hiérarchique de petites zones qui fusionne
  plusieurs sources administratives avec leur incertitude.
  [arXiv 2112.09813](https://arxiv.org/abs/2112.09813v1)
  · voir aussi [arXiv 1904.11144](https://ar5iv.labs.arxiv.org/html/1904.11144)
- **Raftery, Alkema & Gerland**, projections probabilistes de population pour l'ONU :
  modèles hiérarchiques bayésiens de la fécondité et de l'espérance de vie, paquets R
  `bayesTFR`, `bayesLife` et `bayesPop`. L'ONU publie des projections probabilistes
  depuis 2015 (cité, revue 2022).
  [arXiv 1405.4708](https://arxiv.org/pdf/1405.4708) ·
  [Statistical Science](https://dx.doi.org/10.1214/13-sts419) ·
  [bayesPop, JSS](https://www.jstatsoft.org/article/view/2943/0) ·
  [revue 2022, PMC9783793](https://pmc.ncbi.nlm.nih.gov/articles/PMC9783793)
  - → C'est le **précédent institutionnel** : un organisme public a remplacé des
    projections déterministes par des projections bayésiennes publiées, avec leur code.

### 3.3 Taux de sortie non stationnaires (activité au-delà de 65 ans)
- **Modèles âge-période-cohorte bayésiens (APC)**, estimés par INLA : effets d'âge, de
  période et de cohorte en marches aléatoires lissées, puis prolongés pour projeter.
  - Riebler & Held, *Biometrical Journal* 2017, paquet `BAPC`.
    [PDF](https://faculty.washington.edu/jonno/APCmaterial/rieblerheld17.pdf) ·
    [BAPC](https://rdrr.io/rforge/BAPC/man/BAPC.html)
  - Riebler et al., *Annals of Applied Statistics* 2012, qui empruntent de la force à des
    populations proches.
    [arXiv 1108.0606](https://pdf.arxiv.org/pdf/1108.0606)
  - Goes, *Demography* 2024 : petites populations régionales, beaucoup de zéros
    (via la recherche, non ouvert).
  - → Pour nous, on traite les **cessations comme des comptages de Poisson** par âge ×
    année × cohorte, et la « rétention des 60 ans et plus en tendance » devient un effet
    de période estimé, avec son incertitude. **Aucun précédent publié n'a été trouvé
    pour les sorties de professionnels de santé** : ce serait une contribution.

### 3.4 Répartition territoriale : là où se fait la plus grande part de l'erreur
- **Choix discret de l'installation** (logit conditionnel, utilité aléatoire) : c'est le
  modèle de référence pour les choix d'installation révélés par les données.
  - Logit conditionnel sur le premier lieu d'installation, avec une limite à connaître :
    les caractéristiques individuelles constantes entre les lieux candidats ne sont pas
    identifiées. [PMC2739028](https://pmc.ncbi.nlm.nih.gov/articles/PMC2739028)
  - Modèle en deux temps : bouger ou non, puis où.
    [HSR 10.1111/1475-6773.12656](https://zendy.io/title/10.1111/1475-6773.12656)
  - Modèle structurel pour simuler des incitations.
    [PAA 2018](https://paa.confex.com/paa/2018/mediafile/ExtendedAbstract/Paper21370/PAA2018_Kulka%20and%20McWeeny_2017_Rural%20Physician%20Shortages%20and%20Policy%20Intervention.pdf)
  - Logit emboîté mobilité × lieu (Australie).
    [Melbourne Institute WP 2012/13](https://melbourneinstitute.unimelb.edu.au/downloads/working-paper-series/wp2012n13.pdf)
  - Expériences de choix déclarés (DCE).
    [BMC HRH 2019](https://www.doi.org/10.1186/s12960-019-0374-4) ·
    [OMS 2010](https://scielosp.org/pdf/bwho/2010.v88n5/333-341/en)
  - → C'est le **seul modèle où les leviers « régulation » et « incitation » ont un
    mécanisme estimé** (utilité d'une zone), au lieu d'un effet supposé. Chaque
    coefficient se lit comme un arbitrage, un statisticien sait l'estimer et le tester,
    et la régulation par géocodes y devient une restriction de l'ensemble de choix.

### 3.5 Cohérence entre échelles (commune → région → national)
- **Réconciliation optimale des prévisions hiérarchiques (MinT)** : Wickramasuriya,
  Athanasopoulos & Hyndman, *JASA* 114(526), 2019, paquet R `hts`. Elle rend les
  prévisions de tous les niveaux additives en minimisant la variance des erreurs. Un
  prolongement impose la non-négativité.
  [EconPapers](https://econpapers.repec.org/RePEc:taf:jnlasa:v:114:y:2019:i:526:p:804-819) ·
  [hts::MinT](https://search.r-project.org/CRAN/refmans/hts/html/MinT.html)
  - → Remplace notre règle « projeter au département, puis répartir par parts
    actuelles » par une méthode **publiée et optimale**, qu'on peut tester sur le banc.

### 3.6 Validation vérifiable par un statisticien
- **Règles de score propres et calibration** : Gneiting & Raftery (*JASA* 2007), et
  Gneiting, Balabdaoui & Raftery (*JRSS-B* 2007) : maximiser la netteté sous contrainte
  de calibration, avec l'histogramme PIT et le CRPS. Pondérer un score propre par une
  fonction de y le rend impropre.
  [rapport DTIC](https://apps.dtic.mil/sti/pdfs/ADA454828.pdf) ·
  [arXiv 1512.09244](https://arxiv.org/pdf/1512.09244)
  - → Notre MAPE ponctuelle ne suffit pas pour des prévisions probabilistes : il faut
    ajouter **CRPS et PIT** au protocole de l'axe 3 (niveau 1).
- **Bayesian workflow** : Gelman et al., 2020 — construction itérative, vérification par
  la prédiction, comparaison de modèles.
  [arXiv 2011.01808](https://arxiv.org/abs/2011.01808)
- **Calibration par simulation (SBC)** : vérifier que l'algorithme d'inférence retrouve
  des paramètres connus. Référence probable : Talts et al., arXiv 1804.06788, **non
  confirmée par la recherche**, à vérifier avant toute citation.
  - → C'est la version formelle des « mondes simulés » repris de l'observatoire.

## 4. Proposition : un programme de recherche en boîte blanche

Critère d'acceptation de chaque modèle : un statisticien extérieur doit pouvoir le
vérifier en une demi-journée à partir du prétirage seul. Pour cela :
1. le modèle tient en **une page d'équations**, avec l'identité comptable plus un modèle
   statistique par flux ;
2. **chaque paramètre** a un a priori écrit, une source de données et un sens ;
3. il existe une **vérification par simulation** (SBC ou mondes simulés) et des
   **contrôles prédictifs a posteriori** ;
4. il est évalué **hors échantillon** contre les références naïves, avec CRPS, PIT et
   MAPE, selon le protocole pré-enregistré de l'axe 3 ;
5. le code, les graines et les données sont ouverts et millésimés.

| Brique | Modèle proposé | Attaque quel symptôme | Données nécessaires | Coût estimé (temps Claude) |
|---|---|---|---|---|
| Sorties | APC bayésien de Poisson sur les cessations (BAPC / INLA) | biais > 65 ans, non-stationnarité | RPPS âge × année (déjà là) | ~3 h |
| Petits effectifs | cohortes par composantes bayésiennes hiérarchiques (commune ⊂ département ⊂ région) | bruit communal | CartoSanté par commune (déjà là pour 3 professions) | ~1 j |
| Répartition | logit conditionnel d'installation, régulation = ensemble de choix restreint | erreur territoriale, mécanisme des leviers | installations par commune (manquant : CartoSanté `*_flux`) + attributs des communes | ~1 j + données |
| Entrées | effectifs en formation × abandon × filières, plus diplômés étrangers | biais national sur les entrées | inscrits par région, diplômés étrangers (axe 4) | ~3 h |
| Cohérence | réconciliation MinT entre échelles | additivité commune → national | aucune nouvelle | ~2 h |
| Validation | CRPS, PIT, SBC, mondes simulés | 2050 non testable, défauts silencieux | aucune nouvelle | ~3 h |

**Données prioritaires à chercher (axe 4) :**
- **flux d'installation et de cessation par commune** : CartoSanté `*_flux`, question
  ouverte au ledger. C'est la donnée qui débloque le choix discret ;
- **diplômés étrangers** par profession et par an ;
- **inscrits par région de formation** ;
- **infirmiers par secteur × âge × sexe**.

## ⚑ Ce qui pourrait rendre ceci faux
- Aucune référence n'a été lue en texte intégral : ce sont des résumés et des extraits.
- Les coûts sont estimés, non mesurés.
- Un modèle bayésien bien spécifié peut rester mal identifié avec 15 ans de données. La
  calibration par simulation (SBC) sert justement à le détecter avant de publier.
- Le choix discret dépend d'une donnée de flux communale dont l'existence en open data
  n'est pas confirmée.

## Sources consultées (recherches du 2026-11-14)
Toutes les URL citées ci-dessus, plus les pages de recherche :
- OCDE [record](https://oecd.org/en/publications/health-workforce-planning-in-oecd-countries_5k44t787zcwb-en) ;
- [bayespop, CSSS](https://csss.uw.edu/research/working-papers/bayespop-probabilistic-population-projections) ;
- [Raftery et al., espérance de vie](https://researchonline.jcu.edu.au/28347/1/RafteryChunnEtAl_LifeExp.pdf) ;
- [CSSS WP97](https://csss.uw.edu/Papers/wp97.pdf).
