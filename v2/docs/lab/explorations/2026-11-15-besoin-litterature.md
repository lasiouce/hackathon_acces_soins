---
type: exploration
date: 2026-11-15
author: session besoin-derivation (3 lecteurs web, synthèse par la session)
question: "Les ansätze du besoin (M0–M4, transferts) existent-ils déjà dans la littérature, et qu'est-ce qui est nouveau ?"
headline: "M2 est aux trois quarts connu (formules de capitation anglaises York 1994, AREA 2002 : offre fixée à la moyenne nationale) et la littérature française prédit l'absence de plateau (Delattre et Dormont 2003) ; M3 = cadre de Birch et Tomblin Murphy ; M4 = E2SFCA (Luo et Qi 2009) ; aucune projection de l'APL sous scénarios démographiques et d'offre conjoints, aucune reproduction de l'APL en données ouvertes ; m est faible (Canada RP 1,05 ; France 46,1 % contre 46,0 % la première année)"
status: final
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
tags: [besoin, litterature, nouveaute, 2SFCA, APL, demande-induite, transferts]
---

# Littérature du module de besoin : ce qui existe, ce qui est nouveau

> **Headline.**
> - **Déjà connu :** le cœur de M2, « recours = f(besoin, offre), évalué à une offre de référence ». C'est la méthode
>   des formules d'allocation anglaises, qui fixent l'offre à la moyenne nationale.
> - **Non trouvé :**
>   - l'évaluation au **point de saturation**, avec la règle « pas de plateau ⇒ demande induite » ;
>   - une **projection de l'APL** sous scénarios conjoints de démographie et d'offre ;
>   - une **reproduction de l'APL en données ouvertes** ;
>   - l'opérateur de transfert explicite (`k`, `m`, identité de conservation).
> - **Ce que dit la littérature française sur M2 :** elle prédit qu'il tombera, faute de plateau.

## Question
Quelles références fondent les ansätze de la [dérivation](../derivations/2026-11-15-besoin-derivation.md) ? Que
reste-t-il à nous, et que peut-on affirmer sans abus ? Cette passe répond à la question de l'utilisateur·rice
(« tu sources ça d'articles déjà existants ? »).

**Méthode.** Trois lecteurs web en parallèle, environ 20 à 30 recherches chacun. Sources consultées : pages d'éditeur,
Crossref, Europe PMC, PMC, PDF d'auteur. Le plus souvent les **résumés** ont été lus, pas les textes intégraux :
chaque ligne dit ce qui a été lu. Ce rapport ne remplace pas une recherche de nouveauté journalisée (`novelty-claim`)
avant d'écrire « premier ».

## Résultat par ansatz

### Le modèle d'observation et la demande induite (le terme D)
| Référence (vérifiée) | DOI | Lu | Apport |
|---|---|---|---|
| Evans RG (1974), « Supplier-induced demand: some empirical evidence and implications », dans Perlman (dir.), *The Economics of Health and Medical Care*, Palgrave, p. 162–173 | 10.1007/978-1-349-63660-0_10 | résumé | fonde le terme `D(A)` |
| Shain M, Roemer MI (1959), *Mod Hosp* 92(4):71–3 (« loi de Roemer ») | PMID 13644010 | métadonnées seulement | corrélation lits / journées ; causalité non établie |
| Andersen RM (1995), « Revisiting the behavioral model… », *J Health Soc Behav* 36(1):1–10 | 10.2307/2137284 | résumé | vocabulaire : φ ↔ facteurs « facilitants », B ↔ « besoin » ; pas d'estimateur |
| **Delattre E, Dormont B (2003)**, « Fixed fees and physician-induced demand: a panel data study on French physicians », *Health Econ* 12(9):741–54 | 10.1002/hec.823 | résumé | **France**, 4 500 médecins libéraux, 1979–93 : la densité baisse à peine l'activité par médecin, compensée par le volume par séance. **Indice fort de demande induite, donc contre le plateau de M2** |
| Léonard C, Stordeur S, Roberfroid D (2009), *Health Policy* 91(2):121–34 | 10.1016/j.healthpol.2008.11.013 | résumé | revue de 25 études : densité et consommation toujours associées ; pas de saturation rapportée |
| Fisher ES, Wennberg JE (2003), « …supply-sensitive care », *Perspect Biol Med* 46(1):69–79 | 10.1353/pbm.2003.0004 | résumé | « soins sensibles à l'offre » : le recours croît avec la capacité, sans référence clinique |
| Fisher ES et al. (2003), *Ann Intern Med* 138(4):273–87 | Crossref et Europe PMC divergent sur le suffixe : **à vérifier avant de citer** | résumé | +60 % de soins dans les régions qui dépensent le plus, sans meilleure qualité |

### M2 : recours non contraint
| Référence | DOI | Lu | Apport |
|---|---|---|---|
| Carr-Hill RA et al. (1994), *BMJ* 309:1046–9 et 1050–4 (formule de York) | 10.1136/bmj.309.6961.1046 | résumé | doubles moindres carrés, l'offre étant endogène ; l'offre est ensuite **retirée** de la formule |
| **Gravelle H, Sutton M et al. (2003)**, « Modelling supply and demand influences on the use of health care… », *Health Econ* 12(12):985–1004 | 10.1002/hec.830 | résumé | version académique d'AREA : 8 414 circonscriptions électorales (*wards*) anglaises ; recours régressé sur besoin **et** offre, puis l'offre est **fixée à sa moyenne nationale** |
| Gravelle H et al. (2011), CHE Research Paper 73, Université de York | eprints.whiterose.ac.uk/136655 | **texte intégral** | deux façons de neutraliser l'offre : la retirer, ou la fixer ; le choix « repose sur des hypothèses non testables » ; la référence « moyenne nationale » est « essentiellement arbitraire » |
| Aigner D, Lovell CAK, Schmidt P (1977), *J Econometrics* 6(1):21–37 | 10.1016/0304-4076(77)90052-5 (déduit du PII, corroboré) | résumé | frontière stochastique, erreur composée |
| Sheng P, Yang T, Zhang T (2021), « The unmet medical demand among China's urban residents », *IJERPH* 18(21):11708 | 10.3390/ijerph182111708 | résumé | **seul précédent trouvé** d'une frontière appliquée à la demande et non à l'efficience des offreurs (12,6 % de demande non satisfaite en 2018) ; non conditionnée à l'offre |
| Goodman DC et al. (1996), *JAMA* 276(22):1811 | 10.1001/jama.1996.03540220035027 | métadonnées | référence = l'effectif du système intégré le mieux doté (HMO) : une idée de frontière |

**Aucun test explicite de plateau** (recours contre densité, forme de Michaelis–Menten) n'a été trouvé.

### M3 : besoin épidémiologique
| Référence | DOI | Lu | Apport |
|---|---|---|---|
| **Birch S et al. (2007)**, « Human resources planning and the production of health: a needs-based analytical framework », *Can Public Policy* 33(S1):S1–S16 | 10.3138/9r62-q0v1-l188-1406 | métadonnées | effectif requis = population × état de santé × niveau de service par besoin × productivité. **C'est le gabarit de M3** |
| Tomblin Murphy G et al. (2016), *Hum Resour Health* 14:77 | 10.1186/s12960-016-0168-x | résumé | stock-flux de l'offre contre un besoin épidémiologique, 32 pays de l'OCDE, jusqu'en 2030 ; 35 % des données voulues trouvées, le reste supposé ; non validé |
| **MacKenzie A, Tomblin Murphy G, Audas R (2019)**, *Hum Resour Health* 17:42 | 10.1186/s12960-019-0376-2 | résumé | `N = Σ P·H·Q·W / R` : W = part des services de type q assurée par la profession n, R = sa productivité. **Plus proche voisin de nos transferts** |
| Tomblin Murphy G et al. (2013), *Health Policy Plan* 28(7):739–49 ; (2014), *Hum Resour Health* 12:67 (pharmaciens, Jamaïque) | 10.1093/heapol/czs115 ; 10.1186/1478-4491-12-67 | résumé | applications du même cadre |

### M4 : accessibilité spatiale
| Référence | DOI | Lu | Apport |
|---|---|---|---|
| Radke J, Mu L (2000), *Geographic Information Sciences* 6(2):105–112 | 10.1080/10824000009480538 | résumé | origine du « rapport offre/demande puis somme » ; services sociaux, pas la santé |
| Luo W, Wang F (2003), *Env Plan B* 30(6):865–884 | 10.1068/b29120 | manuscrit (PMC8238135) | 2SFCA, poids binaire dans le seuil ; cas particulier du modèle gravitaire |
| **Luo W, Qi Y (2009)**, E2SFCA, *Health & Place* 15(4):1100–1107 | 10.1016/j.healthplace.2009.06.002 | PDF d'auteur | paliers 0–10 / 10–20 / 20–30 min ; poids 1 / 0,68 / 0,22 ou 1 / 0,42 / 0,09. **Ancêtre des paliers de l'APL** |
| Barlet M, Coldefy M, Collin C, Lucas-Gabrielli V (2012), IRDES QES n° 174 (= DREES ER n° 795) | — | PDF (version anglaise) | APL d'origine pour les MG : ETP par tranches d'actes, décroissance < 5 / 5–10 / 10–15 min = 1 / 0,3 / 0,1, **estimée sur les flux patients–médecins** |
| Vergier N, Chaput H (2017), *Les Dossiers de la DREES* n° 17 | — | PDF | méthode « concertée » : 1 / 2⁄3 / 1⁄3 sur 0–10 / 10–15 / 15–20 min, **une convention négociée**, pas une estimation |
| DREES, lisez-moi APL (2026-07, N. Vergier) | — | lu | les poids d'âge sont **renormalisés à chaque millésime** : l'APL ne compare pas deux années sous le vieillissement (citation de la DREES) |
| Wan N et al. (2012) 3SFCA, *IJGIS* 26(6) ; Delamater PL (2013) M2SFCA, *Health & Place* 24 ; Luo J (2014) Huff-2SFCA, *Trans GIS* 18(3) ; McGrail MR (2012), *IJHG* 11:50 ; Wang F (2012), *Annals AAG* 102(5) | 10.1080/13658816.2011.624987 ; 10.1016/j.healthplace.2013.07.012 ; 10.1111/tgis.12096 ; 10.1186/1476-072X-11-50 ; 10.1080/00045608.2012.657146 | résumés | variantes : concurrence entre offreurs, configuration sous-optimale, choix probabiliste ; toutes statiques |
| **Páez A, Higgins CD, Vivona SF (2019)**, *PLoS ONE* 14(6):e0218773 | 10.1371/journal.pone.0218773 | page | inflation de la demande et du niveau de service dans les FCA ; une version « équilibrée » préserve les totaux |
| Liu Y et al. (2026), *Front Public Health* 14 ; Shan X et al. (2023), *IJDRS* 14(5):840–857 ; Fowler D et al. (2022), *SSTE* 43:100544 | 10.3389/fpubh.2026.1890540 ; 10.1007/s13753-023-00513-x ; PMID 36460455 | résumés | 2SFCA avec **population projetée** à 2030–2050, **offre figée** (lits, centres d'urgence) |
| Launay L et al. (2019), *PLoS ONE* 14(8):e0221417 | 10.1371/journal.pone.0221417 | page | indice d'accessibilité **en données ouvertes** (BPE) pour MG, MK, IDE, PH, CD en France ; pas un 2SFCA ; aucune comparaison chiffrée à l'APL |

### Transferts de tâches
| Référence | DOI | Lu | Apport pour `a`, `k`, `s(t)`, `m` |
|---|---|---|---|
| **Laurant M et al. (2018)**, Cochrane CD001271.pub3 | 10.1002/14651858.CD001271.pub3 | résumé | substitution médecin → infirmier : consultations probablement plus longues (**k > 1**), retours un peu plus fréquents (**m > 0**) ; pas de minutes dans le résumé |
| Isenor JE et al. (2016), *Vaccine* 34(47):5708–23 | 10.1016/j.vaccine.2016.08.085 | résumé | vaccination par les pharmaciens : couverture toujours plus haute ; un RR poolé de 2,74 n'est vu que dans un résumé secondaire, non vérifié |
| **Buchan SA et al. (2017)**, *CMAJ* 189(4):E146–52 | 10.1503/cmaj.151027 | résumé | Canada, provinces avec et sans la mesure : couverture +2,2 %, rapport de prévalence 1,05 [1,02 ; 1,08]. **m faible : surtout de la substitution** |
| Arrêtés du 10 mai 2017 et du 25 sept. 2018 ; décret n° 2019-357 du 23 avril 2019 | JO | textes (selon le lecteur) | expérimentation en **Auvergne-Rhône-Alpes et Nouvelle-Aquitaine dès octobre 2017**, puis **Hauts-de-France et Occitanie dès octobre 2018**, généralisation en 2019-20 |
| HAS (2018), recommandation sur l'extension des compétences | — | résumé secondaire (Vidal) | couverture non accrue la première année dans les deux régions |
| **Liard R et al. (2022)**, *Int J Pharm Pract* 30(3):253–60 | 10.1093/ijpp/riac007 | résumé | d'après la HAS : couverture 2017-18 de 46,1 % dans les régions de 2017, contre 46,0 % la saison précédente et 45,9 % ailleurs (**m ≈ 0 la première année**). Part des pharmaciens en 2019-20 : 36,7 % (régions de 2017), 35,7 % (2018), 25,6 % (2019). **Une observation directe de `s(t)` par date d'entrée** |
| Dreesch N et al. (2005), *Health Policy Plan* 20(5):267–76 | 10.1093/heapol/czi036 | résumé | temps par intervention → ETP ; transfert qualitatif seulement |
| Birch S, Gibson J, McBride A (2020), *Soc Sci Med* 250:112863 | 10.1016/j.socscimed.2020.112863 | métadonnées | réallocation des tâches dans un cadre de besoin ; équations non lues |
| OMS (2008), *Task shifting*, ISBN 978 92 4 159631 2 | — | page | recommandations, sans opérateur quantitatif |
| Bass FM (1969), *Management Science* 15(5):215–27 | 10.1287/mnsc.15.5.215 | métadonnées | diffusion ; aucune application à l'extension des compétences d'une profession trouvée |
| Ojha HA et al. (2014), *Phys Ther* 94(1):14–30 ; Babatunde OO et al. (2020), *PLoS ONE* 15(7) | 10.2522/ptj.20130096 ; DOI de Babatunde déduit, non ouvert | résumés | accès direct au kiné : moins de séances, d'imagerie et de coûts (**m ≤ 0**, consultations de MG évitées) ; pas de chiffres dans les résumés |
| Durée d'une vaccination | — | — | **aucune mesure trouvée** ; `k` de la vaccination reste non mesuré |

## Ce qui est connu, ce qui est à nous (formulations défendables)
| Élément | Statut | Formulation défendable |
|---|---|---|
| M1 (recours standardisé par l'âge) | **connu** (DREES, APL) | aucune revendication |
| M2, offre fixée à une référence | **connu** (York 1994, AREA 2002, Gravelle 2003) | « suit les formules de capitation fondées sur le recours » |
| M2, référence = **plateau estimé** + règle d'abandon « pas de plateau ⇒ demande induite » | **non trouvé** (environ 20 recherches) | « étend les formules fondées sur le recours en remplaçant la référence “offre moyenne” par un niveau de saturation estimé » |
| M3 | **connu** (Birch 2007, Tomblin Murphy) | « applique le cadre de besoin de Birch et al. aux données ouvertes de la cartographie des pathologies » |
| M4, E2SFCA à paliers | **connu** (Luo et Qi 2009 ; DREES) | aucune revendication |
| M4 **projeté à 2050**, démographie **et** offre en mouvement, par profession, poids d'âge fixés à une année de base | **non trouvé** : les travaux prospectifs figent l'offre | « à notre connaissance, première projection de l'APL sous scénarios conjoints de démographie et d'effectifs » (après recherche journalisée) |
| Reproduction de l'APL **sans** données d'activité individuelle, avec écart mesuré | **non trouvé** | idem |
| Opérateur de transfert (`s·a`, `k`, `m`, identité de conservation) | **en partie connu** (parts W et productivités R chez MacKenzie 2019) ; `m` et `s(t)` absents des modèles lus | « opérateur de transfert explicite et conservatif, qui sépare la conversion de temps `k` de l'expansion `m`, calé sur le déploiement échelonné français » |

## ⚑ Ce qui pourrait rendre ceci faux
- Ce sont surtout des **résumés**. Les textes intégraux ont été lus seulement pour CHE RP73, Luo et Qi, QES 174,
  le *Dossier* DREES 17 et le lisez-moi de l'APL.
- La recherche s'est faite par moteur web et par résumés. Google Scholar, Scopus et HAL n'ont pas été interrogés en
  profondeur.
- **Désaccord sur le nombre de régions** de l'expérimentation : la Cour des comptes (lue, texte extrait) dit
  « environ 5 000 pharmacies dans six régions à partir de 2017 » ; les arrêtés relevés par le lecteur en donnent
  **quatre** (deux en 2017, deux en 2018). À trancher en lisant les arrêtés au Journal officiel, avant de geler P-B6.
- Deux DOI restent à confirmer : Fisher 2003 (suffixes divergents) et Babatunde 2020 (déduit).

## → Ce que ça change
1. **M2 devient deux variantes.**
   - **M2a « AREA »** : l'offre est fixée à sa moyenne nationale. La méthode est établie et identifiée sous R1 ; elle
     produit un « besoin à accès moyen ».
   - **M2b « saturation »** : notre extension, qui reste soumise à P-B2.
   - **A priori défavorable pour M2b** : Delattre et Dormont (France), Léonard et coll. (revue de 25 études) et
     Dartmouth ne voient pas de saturation. On s'attend donc à ce que P-B2 tue M2b ; M2a sert de repli.
2. **M4 projeté.** Les poids d'âge sont **figés à une année de base**, et non renormalisés comme dans l'APL. C'est ce
   qui permet de voir le vieillissement national, que la DREES dit ne pas capter. Le test de conservation
   `Σ P_i A_i = Σ S_j` reste à confronter au texte de Páez et coll. sur l'« inflation ».
3. **Transferts.** On dispose maintenant d'ancrages publiés :
   - `m` faible : a priori RP 1,05, et ≈ 0 la première année en France ;
   - `k > 1` pour la substitution médecin → infirmier ;
   - `s(t)` observable par date d'entrée des régions (Liard 2022).

   P-B6 est donc mieux armé. Les deux saisons avant l'expérimentation restent sa faiblesse.
4. **La formulation de MacKenzie et coll. (2019)**, `N = Σ P·H·Q·W/R`, est la référence à citer pour M3 et les
   transferts.
5. **ML (question de l'utilisateur·rice).** Rien dans cette littérature n'utilise le ML pour identifier le besoin :
   les méthodes établies sont des régressions structurelles. Le ML reste au plus un candidat concurrent dans P-B5
   (backtest), soumis à la même règle d'abandon que C1-GBM.

## ? Suite
| Point | Coût |
|---|---|
| Recherche de nouveauté journalisée (`novelty-claim`) sur « APL projetée » et « reproduction en données ouvertes » (Scholar, HAL), avant d'écrire « premier » | ~30 min |
| Lire les arrêtés de 2017 et 2018 au JO : nombre et liste des régions (quatre ou six ?) | ~15 min |
| Textes intégraux de Birch, Gibson et McBride (2020) et de MacKenzie (2019) : forme exacte de W et R, identité de conservation ? | ~30 min |
| Vérifier la conservation 2SFCA contre Páez et coll. (2019) | ~15 min |
| Lire Gravelle et coll. (2003) en entier : spécification et instruments, pour M2a | ~30 min |
