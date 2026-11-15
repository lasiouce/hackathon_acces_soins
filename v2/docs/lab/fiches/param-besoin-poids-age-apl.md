---
type: fiche
axe: 1
id: param-besoin-poids-age-apl
parametre: "ω_a(p) — poids d'âge du recours (consommation moyenne de la tranche rapportée à la moyenne nationale)"
profession: [infirmiers, kines, dentistes, sages-femmes]
module: besoin (M1 forme du profil ; M4 population standardisée)
valeur: "19 tranches quinquennales (< 5 … 90+) ; ex. IDE 2024 : 0,06 (< 5 ans), 4,50 (80-84), 15,51 (90+) ; MK : pas de colonne 2024, dernière colonne 2023 ; SF : sur la population féminine"
unite: "sans dimension (consommation par habitant de la tranche / consommation par habitant nationale)"
incertitude: "aucune erreur publiée ; variation d'un millésime au suivant (bandes ω ≥ 0,5, |Δ| / valeur précédente) : IDE ≤ 7,9 % (80-84), CD ≤ 6,5 % (90+), MK ≤ 5,9 %, SF ≤ 5,4 % (20-24) ; de 2022 à 2024 : CD 11,9 %, IDE 9,3 %, SF 8,9 % (dérivé) ; poids arrondis à 0,01 ; champ CD différent (3 régimes extrapolés)"
source: "DREES, jeu 530 « L'accessibilité potentielle localisée (APL) », fichiers « Indicateur d'APL aux infirmiers / kinésithérapeutes / chirurgiens-dentistes / sages-femmes » (xlsx), onglet « Paramètres », bloc « Pondération de la population selon l'âge » — https://data.drees.solidarites-sante.gouv.fr/explore/dataset/530_l-accessibilite-potentielle-localisee-apl/ ; Lisez-moi APL (PDF, 3 p.), p. 3"
millesime: "colonnes 2022, 2023, 2024 = consommations DCIR (SNIIR-AM) 2020, 2021, 2022 ; fichiers téléchargés le 2026-11-15"
statut: mesuré
date: 2026-11-15
---

# ω_a(p) — poids d'âge du recours, fichiers APL de la DREES

**Rôle dans le module.** M1 prend la **forme** de son profil de recours dans ces poids, et le **niveau** dans Open
DAMIR ([[param-besoin-profil-damir]]) : `r(p, a) = r̄(p) · ω_a(p)`. M4 s'en sert pour la population standardisée
`P_std = Σ_a pop_a · ω_a`. Dérivation : [besoin §6](../derivations/2026-11-15-besoin-derivation.md), M1.

**Définition (citée, onglet « Paramètres », note de bas de bloc).**
- Le poids est « la consommation moyenne en soins d'infirmières de la tranche d'âge, rapportée à la consommation moyenne
  nationale » (même phrase pour MK et CD).
- SF : « consommation moyenne en soins de sages-femmes de la tranche d'âge **féminine** ». La population standardisée
  SF est féminine (colonne « Population féminine standardisée 2022 pour les sages-femmes »).
- Lisez-moi, p. 3 : « Un poids est attribué à chaque tranche d'âge quinquennale, proportionnel à la consommation de
  soins moyenne de la tranche d'âge auprès de la profession de santé considérée. » La population standardisée totale
  égale la population totale. Les poids viennent du DCIR et des populations Insee (point 4), et non plus de l'EGB.

**Contrôle (mesuré, 2026-11-15).** Σ population standardisée = Σ population totale, onglet « APL 2024 » :
67 760 573 pour IDE, MK et CD ; 34 949 512 = population féminine pour les SF. Les poids sont donc normalisés à
moyenne 1 sur la population de l'année.

**Champ (cité).**
- IDE, MK, SF : « Consommations de soins auprès des professionnelles de santé libérales et des établissements de santé
  privés ».
- CD : « Consommations de trois régimes (RG, MSA, RSI), extrapolées à la population nationale ». Ce n'est pas le même
  champ : les poids CD ne sont pas strictement comparables aux trois autres.

**Millésimes (cités).** Onglet « Paramètres » : « DCIR 2020, 2021 et 2022, Cnam ; populations municipales 2020, 2021
et 2022 ». L'en-tête de chaque onglet « APL 2024 » dit « consommations de soins par tranche d'âge : SNIIR-AM 2022 » :
la colonne « 2024 » porte les consommations de **2022** (décalage N−2).

## Valeurs (mesurées : lues dans les fichiers)

| Tranche | IDE 2022 | IDE 2023 | IDE 2024 | MK 2022 | MK 2023 | CD 2022 | CD 2023 | CD 2024 | SF 2022 | SF 2023 | SF 2024 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| < 5 ans | 0,03 | 0,05 | 0,06 | 0,16 | 0,18 | 0,07 | 0,08 | 0,08 | 0,04 | 0,04 | 0,05 |
| 5-9 | 0,05 | 0,09 | 0,09 | 0,07 | 0,07 | 0,56 | 0,56 | 0,57 | 0 | 0 | 0 |
| 10-14 | 0,06 | 0,11 | 0,10 | 0,21 | 0,21 | 0,48 | 0,48 | 0,50 | 0,01 | 0,02 | 0,02 |
| 15-19 | 0,12 | 0,17 | 0,15 | 0,32 | 0,31 | 0,52 | 0,53 | 0,54 | 0,36 | 0,36 | 0,38 |
| 20-24 | 0,17 | 0,22 | 0,19 | 0,35 | 0,35 | 0,69 | 0,69 | 0,68 | 1,49 | 1,41 | 1,45 |
| 25-29 | 0,19 | 0,25 | 0,21 | 0,47 | 0,47 | 0,91 | 0,91 | 0,87 | 3,59 | 3,47 | 3,41 |
| 30-34 | 0,21 | 0,27 | 0,24 | 0,56 | 0,56 | 1,02 | 1,02 | 0,98 | 4,37 | 4,33 | 4,21 |
| 35-39 | 0,22 | 0,29 | 0,26 | 0,64 | 0,65 | 1,12 | 1,10 | 1,06 | 2,76 | 2,80 | 2,80 |
| 40-44 | 0,25 | 0,31 | 0,29 | 0,76 | 0,79 | 1,18 | 1,19 | 1,17 | 1,32 | 1,39 | 1,42 |
| 45-49 | 0,32 | 0,36 | 0,33 | 0,94 | 0,95 | 1,26 | 1,23 | 1,18 | 0,73 | 0,75 | 0,74 |
| 50-54 | 0,44 | 0,48 | 0,47 | 1,14 | 1,17 | 1,34 | 1,33 | 1,33 | 0,56 | 0,59 | 0,61 |
| 55-59 | 0,63 | 0,65 | 0,64 | 1,29 | 1,32 | 1,41 | 1,41 | 1,41 | 0,43 | 0,46 | 0,47 |
| 60-64 | 0,85 | 0,86 | 0,86 | 1,32 | 1,34 | 1,42 | 1,43 | 1,44 | 0,38 | 0,41 | 0,41 |
| 65-69 | 1,17 | 1,19 | 1,16 | 1,37 | 1,39 | 1,34 | 1,35 | 1,37 | 0,32 | 0,33 | 0,34 |
| 70-74 | 1,90 | 1,76 | 1,78 | 1,86 | 1,75 | 1,49 | 1,42 | 1,43 | 0,27 | 0,26 | 0,27 |
| 75-79 | 2,85 | 2,79 | 2,99 | 2,12 | 2,16 | 1,30 | 1,36 | 1,40 | 0,18 | 0,19 | 0,22 |
| 80-84 | 4,92 | 4,53 | 4,50 | 2,72 | 2,58 | 1,13 | 1,11 | 1,14 | 0,11 | 0,11 | 0,12 |
| 85-89 | 8,76 | 8,07 | 8,13 | 3,98 | 3,75 | 0,93 | 0,94 | 0,96 | 0,06 | 0,06 | 0,06 |
| 90 et + | 16,01 | 15,11 | 15,51 | 6,64 | 6,25 | 0,59 | 0,62 | 0,66 | 0,03 | 0,03 | 0,03 |

## Anomalie MK : pas de colonne 2024
- L'onglet « Paramètres » MK n'a que deux colonnes (2022, 2023) et cite « DCIR 2020 et 2021 » seulement.
- Pourtant l'onglet « APL 2024 » MK existe et dit « consommations de soins par tranche d'âge : SNIIR-AM 2022 ». Les
  poids MK 2022 (DCIR) ont donc servi au calcul, mais ne sont **pas publiés** (constat, 2026-11-15).
- **Repli retenu pour la fiche :** la colonne MK 2023 (DCIR 2021), étiquetée « millésime N−1 ». L'écart attendu est de
  l'ordre de la variation 2022 → 2023 (≤ 5,9 % sur les bandes ω ≥ 0,5, dérivé).
- **Voie de récupération (non faite) :** la population standardisée MK 2022 est publiée par commune. Avec les
  populations communales par âge quinquennal de l'Insee (2022), une régression sans constante sur ~35 000 communes
  doit retrouver les 19 poids. Ledger, ~20 min.

## Anomalie IDE : onglet « APL 2023 » mal titré
Relevée par la relecture (2026-11-15), confirmée dans le fichier : l'onglet « APL 2023 » du fichier IDE porte le titre
et le millésime 2024, et sa colonne d'en-tête « population 2022 », mais ses populations somment à 67 408 052,
c'est-à-dire la population 2021. Contenu 2023, étiquettes 2024 : à traiter comme une erreur d'étiquette, à vérifier
avant tout usage de l'APL IDE 2023 (P-B4 utilise 2024). Les poids de l'onglet « Paramètres » ne sont pas touchés.

## Incertitude
- **Aucune erreur publiée** ; les poids sont arrondis au centième. Pour les petites tranches (< 0,1), l'arrondi pèse
  jusqu'à ±50 % de la valeur, sans effet notable sur `P_std`.
- **Variation entre millésimes** (dérivé de la table, bandes ω ≥ 0,5). D'un millésime au suivant, |Δ| / valeur
  précédente : IDE ≤ 7,9 % (80-84), CD ≤ 6,5 % (90+), MK ≤ 5,9 %, SF ≤ 5,4 % (20-24). De 2022 à 2024, (max − min) / min :
  CD 11,9 % (90+), IDE 9,3 % (80-84), SF 8,9 % (50-54). *[Corrigé après relecture : la première version donnait les
  écarts 2022 → 2024 comme écarts « d'un millésime à l'autre ».]* IDE de 2022 à 2023 : tous les poids des moins de 50 ans montent de 12 à 83 % (dérivé), sans
  explication publiée (rupture de champ ou effet Covid 2020 : non établi).
- **Censure.** Ce sont des consommations, donc du recours observé sous l'offre de 2020-2022 : la forme hérite de la
  censure (dérivation §2). C'est la limite connue de M1.
- **Renormalisation.** La DREES renormalise à chaque millésime (Lisez-moi p. 3 : la standardisation « ne permet en
  revanche pas de comparer l'accessibilité entre deux millésimes » sous le vieillissement). Le module **fige** les poids
  d'une année de base (décision du 2026-11-15, M4 projeté).

## Usage
- Année de base proposée : colonne **2024** (DCIR 2022) pour IDE, CD, SF ; **2023** (DCIR 2021) pour MK, jusqu'à
  récupération des poids 2022.
- Les valeurs ne sont pas copiées dans le code par cette fiche : l'axe 4 les lit dans le fichier source
  (`v2/data/raw/`, script versionné), ce tableau sert de contrôle.
- Pharmaciens : **aucun** poids APL (pas d'APL pharmaciens). Voir [[param-besoin-profil-damir]].
