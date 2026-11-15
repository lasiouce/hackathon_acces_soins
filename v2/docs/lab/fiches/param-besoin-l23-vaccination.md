---
type: fiche
axe: 1
id: param-besoin-l23-vaccination
parametre: "Transfert L23 — vaccination antigrippale en officine (A = médecins, IDE ; B = pharmaciens) : a, k, s_∞, τ, m"
profession: [pharmaciens, infirmiers]
module: besoin (opérateur de transfert)
valeur: "parts des injections en 2018 : médicaux 70,7 %, IDE 29,3 %, PH 0 % ; part PH 27,6 % (2019) → 64,4 % (2024) ; s_∞ = 0,70 [0,63 ; 0,77], τ = 2,8 ans [1,6 ; 3,7] (t₀ = 2018) ; m : non identifié (a priori 0 à +5 %) ; k : supposé, plage [0,25 ; 1]"
unite: "a, s_∞ : fractions des injections antigrippales ; τ : années ; m : fraction du recours ; k : rapport de durées (sans dimension)"
incertitude: "s_∞ et τ dépendent de t₀ (plages ci-dessus, dérivées) ; série 2018 sans officines alors que l'expérimentation tournait (définition de l'année ou du code non documentée) ; m confondu avec la croissance du public cible (+20 %) et le Covid ; a en temps de MG : dénominateur non mesuré ici"
source: "Cour des comptes, « La politique de vaccination depuis 2018 », 7 sept. 2026, p. 43-49, graphique n° 10 et archive open data G10.csv / G9.csv ; IQVIA-Pharmastat, data.gouv.fr, « Vaccination grippe » 2022-23 à 2025-26 ; HAS, recommandation vaccinale validée en juillet 2018, mise en ligne le 8 août 2018, p. 11, 32-33 ; Liard et coll. 2022, Int J Pharm Pract 30(3):253-260, doi:10.1093/ijpp/riac007 ; Buchan et coll. 2017, CMAJ 189(4):E146-E152, doi:10.1503/cmaj.151027 ; DREES ER n° 1381 (2026-08), p. 2"
millesime: "SNDS 2018-2024 (Cour) ; IQVIA saisons 2022-23 à 2025-26, arrêt au 28 février ; HAS 2018 (saison 2017-18) ; GrippeNet 2019-20 (Liard) ; CCHS 2007-2014 (Buchan) ; panel DREES 2025-26"
statut: "a sourcé (parts) ; s_∞ et τ dérivés ; m non identifié (borne sourcée) ; k supposé"
date: 2026-11-15
---

# L23 — vaccination antigrippale en officine

**Opérateur** (dérivation §6, transferts) :
`B'_A = B_A (1 − s a)`, `B'_B = B_B + s a B_A k + m`, `ΣB' − ΣB = s a B_A (k − 1) + m`,
avec `s(t) = s_∞ (1 − e^{−(t−t₀)/τ})`.

**Textes** (lus) :
- expérimentation dans **4 régions**, pas 6 : Auvergne-Rhône-Alpes et Nouvelle-Aquitaine (saison 2017-18, arrêté du
  10 mai 2017), puis Hauts-de-France et Occitanie (2018-19, arrêté du **8 juin 2018**, « deux » remplacé par
  « quatre »). HAS 2018, p. 11 : « Quatre régions sont concernées par l'expérimentation ». L'arrêté du 25 septembre 2018
  élargit le **public** (primo-vaccinés, femmes enceintes), pas les régions ;
- généralisation : décret n° 2019-357 du 23 avril 2019 (texte officiel non lu ; cité par la Cour p. 43) ;
- la Cour dit « environ 5 000 pharmacies dans six régions à partir de 2017 » (p. 43) : contredit par l'arrêté et par
  la HAS. La fiche suit les textes.

## Données mesurées

**Injections antigrippales par catégorie de vaccinateur** (Cour des comptes, graphique n° 10, CSV de l'archive open
data, SNDS ; parts calculées par [`fit_s_t.py`](../reports/2026-11-15-besoin-axe1-fiches/fit_s_t.py)) :

| Année | Total | Pharmacie | Infirmier | Médecin | « aucun acte ou consultation » | Médicaux (médecin + aucun acte) |
|---|---|---|---|---|---|---|
| 2018 | 6 184 138 | 0,0 % | 29,3 % | 42,2 % | 28,5 % | 70,7 % |
| 2019 | 6 625 310 | 27,6 % | 22,8 % | 29,4 % | 20,2 % | 49,6 % |
| 2020 | 7 801 978 | 34,0 % | 21,8 % | 22,2 % | 22,0 % | 44,2 % |
| 2021 | 7 313 228 | 44,7 % | 17,9 % | 19,3 % | 18,0 % | 37,4 % |
| 2022 | 10 011 114 | 51,2 % | 16,3 % | 16,6 % | 15,9 % | 32,6 % |
| 2023 | 9 466 636 | 58,8 % | 13,8 % | 13,5 % | 13,9 % | 27,4 % |
| 2024 | 9 538 770 | 64,4 % | 11,7 % | 11,0 % | 12,9 % | 23,9 % |

- **Rapprochement avec le texte de la Cour (p. 45), dérivé.** Le texte dit : pharmaciens « un peu moins d'une
  vaccination [...] sur trois » en 2019-2020, « près de deux sur trois » en 2024-2025 ; « professionnels médicaux »
  d'« une vaccination sur deux à moins d'une sur quatre » ; infirmiers « d'une sur cinq à environ une sur dix ». Les
  parts du CSV ne retrouvent ces fractions que si la catégorie « aucun acte ou consultation » est comptée avec les
  médecins (49,6 % → 23,9 %). C'est notre lecture, non écrite par la Cour.
- **Total** : « le nombre d'injections a augmenté de 3,3 millions de doses entre 2018 et 2024 » (p. 45) ; CSV :
  +3 354 632 (mesuré).
- **⚑ 2018 sans pharmacie.** La colonne 2018 compte 0 injection en officine alors que la HAS dénombre « près de
  160 000 vaccinations » en 2017-18 (p. 32). Année civile ou saison, et code d'acte retenu : non documentés dans
  l'archive.
- **Volumes officinaux IQVIA** (actes VGP, panel d'environ 60 % des officines extrapolé, du début de campagne au
  28 février ; sommes des fichiers quotidiens, recoupées avec le fichier « campagne » à 6 près) : 5 373 892 (2022-23),
  5 645 132 (2023-24), 6 629 124 (2024-25), 8 020 530 (2025-26). Licence Ouverte 2.0.
- **Par date d'entrée des régions** (Liard 2022, cohorte GrippeNet.fr, adultes à risque, 2019-20 ; texte lu par un
  relais, pas mot à mot) : part des vaccinés en pharmacie 36,7 % (régions de 2017, N = 274), 35,7 % (régions de 2018,
  N = 159), 25,6 % (autres, N = 495). Les données ne viennent **pas** du SNDS : cohorte volontaire, plus âgée et plus
  souvent vaccinée que la population.

## Paramètres

| Paramètre | Valeur | Étiquette | Source, page |
|---|---|---|---|
| `a` (part de l'acte dans le besoin source) | répartition de l'acte avant transfert (2018) : médicaux 70,7 %, IDE 29,3 % des injections antigrippales. En **temps de MG** : numérateur ≈ 2,6 M (injections en consultation) à 4,4 M (avec « aucun acte ») en 2018 ; dénominateur (activité totale de MG en actes ou en temps) **non lu ici** | **sourcé** pour la répartition ; **partiel** pour la part en temps (dénominateur : axe 4, DAMIR `PSE_SPE_SNDS = 1`) | Cour, G10.csv ; [[param-besoin-b-mg-source]] |
| `s_∞` (part transférée à terme) | 0,70 pour t₀ = 2018 ; plage 0,63-0,77 selon t₀ (2017,75 à 2019) ; borne basse observée 0,644 (2024) | **dérivé** (ajustement sur 2019-2024, 6 points, eqm 3,1 points) | Cour, G10.csv ; script |
| `τ` (constante de montée en charge) | 2,8 ans pour t₀ = 2018 ; plage 1,6-3,7 ans | **dérivé**, même ajustement | idem |
| `m` (expansion) | **non identifié** en France. Bornes : 1ʳᵉ saison, couverture des personnes ciblées +0,1 point dans les 2 régions contre −0,2 ailleurs, « pas [...] d'évolution significative » (HAS 2018, p. 33) ; Canada, rapport de prévalence 1,05 [1,02 ; 1,08] (Buchan 2017, résumé lu). Valeur par défaut **0**, plage [0 ; +5 %] du recours | **partiel** : bornes sourcées, mesure attendue de P-B6 | HAS p. 33 ; Buchan, résumé |
| `k = t_B / t_A` | aucune durée publiée de l'acte de vaccination en officine ni chez le médecin (5 recherches). Côté MG, la consultation entière dure 19 min en moyenne (« En 2025, la durée moyenne déclarée d'une consultation est de 19 minutes », ER 1381 p. 2), ce qui n'est pas la durée d'une vaccination. Plage proposée [0,25 ; 1] : rapport des tarifs à la consultation de MG à 30 € (Cour p. 45), 7,56 € / 30 € = 0,25 pour une injection sur prescription d'un tiers (Cour p. 48) et 9,61 € / 30 € = 0,32 pour l'acte du pharmacien ou de l'IDE prescripteur (p. 45) ; 1 = durées égales. *[Borne basse corrigée de 0,32 à 0,25 après relecture.]* | **supposé** | ER 1381 p. 2 ; Cour p. 45, 48 |

**Couverture** (Cour, G9.csv, SNDS) : 65 ans et plus 51,0 % (2018) → 59,9 % (2020) → 53,7 % (2024) ; moins de 65 ans
à risque 29,2 % → 25,3 %. Public cible : 16 M (2018) → plus de 19 M (2024), +20 % (p. 44). La hausse des injections
(+54 % de 2018 à 2024) mêle donc public cible, Covid (2020-2022), et peut-être `m` : elle ne mesure pas `m`.

## Incertitude et limites
- **t₀.** L'autorisation est échelonnée (2017, 2018, 2019) : un t₀ national unique est une approximation. Liard
  montre l'effet de la date d'entrée (36,7 % contre 25,6 % la même saison).
- **Le modèle exponentiel n'est pas testé** contre une logistique (Bass) : 6 points ne suffisent pas à les départager.
- **`s` et la part de l'officine.** Si `m > 0`, la part des pharmaciens surestime `s`, puisqu'une partie des injections
  officinales s'ajoute au lieu de se substituer. Avec `m = 0` (défaut), les deux se confondent.
- **Transposition** aux autres transferts (L25, L27, tension) : `s_∞` et `τ` de la vaccination seraient une hypothèse,
  étiquetée « supposé (transposé de L23) », jamais une mesure.

**Écarts relevés dans les sources** (non résolus) : tarif de l'acte officinal, 9,61 € (Cour p. 45) contre 7,50 € (presse
syndicale, non lue) ; Liard, OR de la vaccination antérieure 1,71 (résumé) contre 0,58 (corps, selon le relais).
