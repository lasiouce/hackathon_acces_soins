---
type: exploration
date: 2026-11-15
headline: "14 requêtes, profondeur « scan+ » : aucune des trois revendications n'est contredite, aucune n'est établie ; le plus proche voisin de la n° 1 est Bruns et coll. 2026 (IZA DP 18801, médecins généralistes, Basse-Saxe, 2040), sans 2SFCA"
---

# Nouveauté du module de besoin (`novelty-claim`)

Source des revendications : [passe de littérature](2026-11-15-besoin-litterature.md), § « Ce qui est connu, ce qui est à nous ».

## Profondeur réellement atteinte : « scan+ », pas « standard »
- 14 requêtes web, plus 3 lectures de pages (MacKenzie 2019 en texte intégral, page IZA DP 18801, résumé de Tanimoto 2017).
- **Écarts à la commande** (à dire) :
  - Google Scholar et Scopus **non interrogés directement** : l'outil est un moteur web généraliste. HAL, theses.fr,
    PubMed et Europe PMC sont couverts par filtre de domaine, pas par leur moteur propre.
  - Textes intégraux non lus : Birch 2007, Gibson et McBride 2020 (introuvable : la requête ne renvoie que des
    ouvrages de gestion sans rapport ; référence **non vérifiée**), Doi et coll. 2017 (titre trouvé, méthode non lue),
    le PDF de Bruns et coll. 2026 (binaire non lisible ; seule la page d'accueil est lue).
- Conséquence : le mot « premier » **reste interdit**. Une recherche de profondeur « scan » peut trouver un
  antécédent, jamais établir une nouveauté.

## Journal des requêtes (2026-11-15, moteur web généraliste)
| # | Filtre | Mots-clés | Résultats ouverts / lus | Pertinent |
|---|---|---|---|---|
| 1 | aucun | projection accessibilité potentielle localisée APL 2030 2040 scénarios démographie médicale | 10 / 3 résumés | IRDES QES : tendance APL MG ; pas de projection APL publiée |
| 2 | aucun | two-step floating catchment area future projection workforce population scenarios 2040 | 10 / 2 | E2SFCA Allemagne, 11 ans **rétrospectifs** (RuR) |
| 3 | aucun | reproduction APL DREES open data replication sans SNDS | 10 / 3 | **code APL public sur le GitLab DREES** ; entrée activité = SNDS |
| 4 | aucun | task shifting workforce model pharmacist vaccination substitution productivity | 10 / 3 | HRSA PhSRM (productivité en scénario), CfWI 2040 |
| 5 | aucun | Bruns IZA DP 18801 pharmacist vaccination | 10 / 0 | rien (la référence était mal attribuée, voir #12) |
| 6 | aucun | vaccination en officine France déploiement échelonné régions expérimentation | 10 / 3 | calendrier 2017 (2 régions) → 2018 (4) → 2019 (national) ; aucune évaluation causale publiée trouvée |
| 7 | hal.science, theses.fr | accessibilité potentielle localisée projection prospective | 9 / 2 | APL décrite, aucune projection |
| 8 | PubMed, Europe PMC, PMC | floating catchment area projected accessibility physicians future supply demographic change | 10 / 3 | Texas : demande ETP projetée à 2032, accessibilité non projetée |
| 9 | aucun | MacKenzie 2019 skill mix workforce planning task shifting | 10 / 2 | MacKenzie, Tomblin Murphy, Audas 2019 (HRH 17:42) |
| 10 | aucun | Doi 2017 spatial accessibility physicians projection Japan 2SFCA | 10 / 3 | Doi 2017 (IJERPH), Hara 2018, Ishikawa 2017, Nakamura 2017 |
| 11 | aucun | Gibson McBride 2020 workforce planning task substitution | 18 / 0 | rien |
| 12 | lecture | docs.iza.org/dp18801 + page d'accueil | 1 | **Bruns, Meier, Thomsen, Wolf 2026** : médecins généralistes, Basse-Saxe |
| 13 | aucun | Ohashi 2022 future projection accessibility hospital beds Osaka | 10 / 2 | **Tanimoto 2017** (2SFCA projeté à 2025, lits) |
| 14 | aucun | "Future projection of the physician workforce and its geographical equity in Japan" | 10 / 1 | Hara et coll. 2018 (BMJ Open), cohortes-composantes |
| 15 | aucun | capitation formula utilisation-based saturation plateau supply-induced demand | 10 / 2 | Gravelle 2003 ; aucun « plateau » |
| 16 | lecture | PMC6567915 (MacKenzie 2019) texte intégral | 1 | voir tableau |
| 17 | lecture | J-STAGE jjhg 69(4) 425 (Tanimoto 2017) résumé | 1 | voir tableau |

## Plus proches voisins
| Travail (URL vérifiée) | Fait | Ne fait pas | Lu |
|---|---|---|---|
| Bruns, Meier, Thomsen, Wolf 2026, IZA DP 18801 ([page](https://www.iza.org/publications/dp/18801)) | projette offre **et** demande de MG sur 105 zones de planification, 2025–2040 ; 4 872 ETP contre 5 131 requis | pas de 2SFCA (ratios par zone) ; MG seuls ; pas de transfert de tâches ; horizon 2040 | page d'accueil seulement |
| Tanimoto 2017, Jpn J Hum Geogr 69(4) ([J-STAGE](https://www.jstage.jst.go.jp/article/jjhg/69/4/69_425/_article/-char/en)) | **2SFCA projeté** (2025) sous scénarios de transports et de lits | lits, pas professions ; une zone ; on ignore si la population bouge | résumé |
| Hara et coll. 2018, BMJ Open e023696 | cohortes-composantes des médecins par zone secondaire, 2005–2035, équité géographique | pas d'accessibilité spatiale ; médecins seuls | résumé |
| Doi et coll. 2017, IJERPH | « patient access area model » : demande et offre futures selon l'accès géographique | méthode non lue : **non vérifiée** comme 2SFCA | titre et résumé |
| RuR 2024 (Allemagne, E2SFCA, 11 ans) ([article](https://rur.oekom.de/index.php/rur/article/view/2278)) | évolution de l'E2SFCA dans le temps | rétrospectif, aucune projection | résumé |
| DREES, APL et code GitLab ([data.gouv](https://www.data.gouv.fr/datasets/donnees-sur-lindicateur-daccessibilite-potentielle-localisee-apl)) | méthode et code publiés | activité individuelle tirée du SNDS ; aucune reproduction en données ouvertes trouvée | page |
| MacKenzie, Tomblin Murphy, Audas 2019, HRH 17:42 ([PMC6567915](https://pmc.ncbi.nlm.nih.gov/articles/PMC6567915)) | N = Σ P·H·Q·W / R : parts W de chaque service par profession, productivité R | aucune identité de conservation écrite ; aucun terme d'expansion `m` ; calage par facturation et panel, pas par expérience naturelle | texte intégral (fin par résumé de modèle) |
| HRSA PhSRM ; CfWI 2016 | scénarios de productivité et de rôle du pharmacien | pas d'opérateur de transfert entre professions | résumés |
| Gravelle et coll. 2003, Health Econ 12(12) | utilisation contrôlée par l'offre → capitation | pas de niveau de saturation estimé | résumé |

**Voisin le plus dangereux pour la n° 1 : Bruns et coll. 2026.** Un relecteur dira : « projection à petite échelle
de l'offre et de la demande, déjà faite ». La différence tient en trois points : nous passons par une accessibilité
spatiale à 2SFCA (débordement entre zones), nous couvrons cinq professions hors médecine générale, et nous allons à
2050. Le PDF doit être lu avant toute publication (~15 min) : s'il contient un 2SFCA, la n° 1 tombe.

## Verdict et formulation par revendication
| # | Classe | Formulation défendable | Ce qui l'invaliderait |
|---|---|---|---|
| 1 Projection d'un 2SFCA/APL à 2050, démographie et effectifs en mouvement, par profession, poids d'âge figés | **nouvelle conjonction** (non trouvée en scan) | « Nous projetons un indicateur d'accessibilité de type APL (E2SFCA) jusqu'en 2050 en faisant varier ensemble la population (Omphale) et les effectifs par profession. Dans une recherche de profondeur limitée (14 requêtes, 2026-11-15), nous n'avons pas trouvé de travail combinant ces éléments ; les plus proches projettent soit les effectifs sans accessibilité spatiale (Bruns 2026, Hara 2018), soit un 2SFCA sur une seule ressource à court terme (Tanimoto 2017). » | un 2SFCA dans Bruns 2026 ; un outil DREES de projection de l'APL (annoncé par la presse, non trouvé) ; Doi 2017 s'il projette un 2SFCA par profession |
| 2 Reproduction de l'APL DREES en données ouvertes, écart mesuré | **nouvelle évaluation**, revendication faible | « Nous reproduisons l'APL publiée par la DREES sans les données d'activité individuelles du SNDS, à partir du code public de la DREES et de données ouvertes, et nous publions l'écart. » Pas de « premier » : le code est public, d'autres l'ont sûrement fait sans publier. | une reproduction publiée (mémoire, thèse, dépôt GitHub) ; un écart si grand que la reproduction ne mérite pas ce nom |
| 3 Opérateur de transfert conservatif (`s·a`, `k`, `m`, ΣB'−ΣB = s·a·B_A·(k−1)+m), calé sur le déploiement échelonné | **extension formelle** d'un cadre connu | « Nous écrivons le transfert de tâches de MacKenzie et coll. (parts W, productivités R) comme un opérateur conservatif qui sépare la conversion de temps `k` de l'expansion `m`, et nous calons `s(t)` sur le déploiement français 2017–2019 ; `m` reste supposé nul (P-B6 : non attribuable). » | un modèle publié avec un terme d'expansion distinct ; une évaluation causale publiée du déploiement échelonné (elle deviendrait la référence de calage) |
| 3b Plateau de saturation dans les formules de capitation (M2b) | **sans objet** | aucune : M2b est tué par P-B2, la revendication n'est plus utilisée | — |

## ⚑ Ce qui pourrait rendre ceci faux
- Scholar, Scopus et la littérature grise DREES/IRDES non interrogés directement : le manque le plus probable.
- Le moteur résume les pages ; la profondeur réelle est le plus souvent « résumé ».

## ? À étudier ensuite
- Lire le PDF de Bruns 2026 et la méthode de Doi 2017 : ~20 min Claude.
- Passe « standard » sur Google Scholar et Scopus, à la main (accès institutionnel) : ~1 h de votre temps.

## Addendum, même jour : textes lus et deuxième passe (APIs ouvertes)
- **Google Scholar : refusé** (page « trafic exceptionnel » avec CAPTCHA, que je ne contourne pas). Scopus demande
  votre accès institutionnel. Remplacés par les API ouvertes d'Europe PMC et de HAL.
- **Bruns et coll. 2026, PDF lu (34 p.) :** besoin = population ÷ ratio population-par-médecin réglementaire (RPPR) par
  zone de planification ; offre en stock-flux par cohorte (registre KVN 2009–2024, pseudonymisé, non ouvert).
  **Aucun 2SFCA, aucune distance, aucune accessibilité spatiale, aucun transfert de tâches.** La revendication n° 1 tient.
  Elle s'en distingue aussi par les données : Bruns s'appuie sur un registre fermé.
- **Doi et coll. 2017, résumé lu (Europe PMC, DOI 10.3390/ijerph14111367) :** « patient access area model »,
  hospitalisations projetées tous les 5 ans contre les **lits** à moins d'une heure de route, Tokyo, horizon 2030.
  L'offre (lits) reste fixe, il n'y a pas de 2SFCA ni de professions. Le texte intégral (MDPI, erreur 403) n'est pas lu.

| # | Moteur | Requête | N | Lus (titres) | Pertinent |
|---|---|---|---|---|---|
| 18 | Google Scholar | "floating catchment" projection 2040 OR 2050 workforce supply population scenarios | CAPTCHA | 0 | — |
| 19 | Europe PMC | "floating catchment" AND (projection OR projected OR future OR scenario) AND (2030…2050) | 116 | 8 | aucun ne projette l'offre ; protonthérapie 2030 = infrastructure |
| 20 | Europe PMC | "floating catchment" AND (workforce OR "supply projection") AND (forecast OR projection) | 9 | 8 | revue de méthodes de planification rurale 2026 (HRH), Texas 2024 |
| 21 | Europe PMC | TITLE:"Patient Access Area Model" | 1 | 1 | Doi 2017 |
| 22 | Europe PMC | ("task shifting" OR "skill mix") AND "workforce planning" AND (conservation OR "induced demand" OR expansion) AND model | 191 | 8 | aucun opérateur conservatif |
| 23 | HAL | text:(accessibilité potentielle localisée) | 19 | 6 (3 résumés) | Chéron et coll. 2025 (indicateur complémentaire), Carrère 2024, Coris 2022 : aucune projection, aucune reproduction |
| 24 | HAL | text:(accessibilité potentielle localisée) AND text:(projection) | 0 | — | — |
| 25 | HAL | title_t:(two-step floating catchment) | 1 | 1 | hôpitaux 2021, transversal |
| 26 | HAL | vaccination officine pharmaciens (expérimentation OR évaluation) | 24 | 8 | thèses d'exercice descriptives (DUMAS) ; aucune évaluation causale du déploiement échelonné |

**Bilan :** 25 requêtes exécutées, profondeur entre « scan » et « standard ». Les trois formulations restent celles
du tableau, inchangées : aucun antécédent trouvé. « À notre connaissance » demande encore Scholar et Scopus.
