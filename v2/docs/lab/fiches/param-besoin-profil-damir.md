---
type: fiche
axe: 1
id: param-besoin-profil-damir
parametre: "r̄(p) — recours moyen par habitant (niveau) et profil d'âge des pharmaciens, depuis Open DAMIR"
profession: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
module: besoin (M1 niveau ; profil complet des pharmaciens)
valeur: "fiche de source et de méthode : valeurs à produire par l'axe 4 (lecture en flux) ; grain : 8 tranches d'âge (0-19, 20-29 … 70-79, 80 et +) + âge inconnu ; 13 régions ; mensuel 2009-01 → 2025-12"
unite: "actes (quantité de prestations) par habitant et par an"
incertitude: "tranche ouverte 80 et + (profil IDE et MK écrasé au-delà de 80 ans) ; « âge inconnu » à répartir ; statut libéral renseigné seulement pour le régime général et les régimes infogérés ; région du bénéficiaire, pas de département"
source: "Assurance maladie, Open DAMIR base complète, descriptif des variables 2024 (xlsx, onglets « OPEN DAMIR » et « MOD OPEN DAMIR ») — https://www.assurance-maladie.ameli.fr/sites/default/files/2024_descriptif-variables_open-damir-base-complete.xlsx ; data.gouv.fr, jeu « Open DAMIR » (API lue), Licence Ouverte"
millesime: "fichiers mensuels 2009-01 à 2025-12 (12 fichiers 2025 listés sur open-data-assurance-maladie.ameli.fr) ; descriptif 2024"
statut: "méthode sourcée ; valeur à mesurer (axe 4)"
date: 2026-11-15
---

# r̄(p) et profil d'âge des pharmaciens — Open DAMIR

**Rôle.** M1 : `r(p, a) = r̄(p) · ω_a(p)`. La forme `ω_a` vient des fichiers APL pour IDE, MK, CD, SF
([[param-besoin-poids-age-apl]]) ; le **niveau** `r̄(p)` vient de DAMIR. Pour les **pharmaciens**, il n'y a pas d'APL :
forme **et** niveau viennent de DAMIR.

## Variables (citées, descriptif 2024)
| Usage | Variable | Modalités utiles |
|---|---|---|
| Âge du bénéficiaire | `AGE_BEN_SNDS` « Tranche d'Age Bénéficiaire au moment des soins » | 0 = « 0-19 ANS », 20, 30, 40, 50, 60, 70, 80 = « 80 ANS ET + », 99 = « AGE INCONNU » |
| Sexe | `BEN_SEX_COD` | 1, 2 ; 0 et 9 inconnus |
| Profession exécutante | `PSE_ACT_SNDS` (professions non médicales) | 19 chirurgie dentaire, 21 sage-femme, 24 infirmier, 26 masseur-kinésithérapeute, **50 pharmacie** |
| Médecine générale (pour [[param-besoin-b-mg-source]]) | `PSE_SPE_SNDS` (professions médicales) | 1 « MEDECINE GENERALE » |
| Libéral / salarié | `PSE_STJ_SNDS` | 1 « PROFESSIONS LIBERALES » ; renseigné seulement pour le régime général et les régimes infogérés |
| Public / privé | `PRS_PPU_SEC` | 1 public, 2 privé, 9 inconnu |
| Quantité | `PRS_ACT_QTE` (brute) ou `FLT_ACT_QTE` (préfiltrée) | « Pour compter des actes, il faut utiliser la variable « quantité d'actes » » ; brut : filtre impératif `PRS_REM_TYP = 0` |
| Périmètre | `TOP_PS5_TRG = 1` (statistique mensuelle tous régimes) ; `CPT_ENV_TYP = 1` (soins de ville) | |
| Géographie | `BEN_RES_REG` (résidence), `EXE_INS_REG` (exécutant), depuis 2015 | 13 regroupements ; pas de département |

## Méthode proposée (pour l'axe 4)
1. Filtrer en flux chaque fichier mensuel de la fenêtre retenue (décision du 2026-11-15 : ~37 à 49 fichiers, aucun
   fichier brut stocké) : profession `p`, `TOP_PS5_TRG = 1`, préfiltré `FLT_ACT_QTE`.
2. Agréger par année × région de résidence × tranche d'âge × sexe.
3. Diviser par la population Insee de la même région × tranche × sexe : `r(p, a)` régional et national.
4. `r̄(p) = Σ_a r(p, a) · pop_a / Σ_a pop_a` (national) ; pour les pharmaciens, profil `r(p, a)` sur 8 tranches.
5. Répartir « âge inconnu » au prorata (à documenter : part à mesurer).

## Limites
- **80 ans et plus** : une seule tranche. Le profil IDE APL va de 4,50 (80-84) à 15,51 (90+) : DAMIR ne peut pas servir
  à la forme pour IDE et MK, d'où le recours aux poids APL. Pour les pharmaciens, la forme au-delà de 80 ans est
  **plate par construction** : à étiqueter.
- **Unité « acte ».** Pour la pharmacie, un acte DAMIR mêle délivrances, honoraires de dispensation (`HDA`, `HDE`) et
  actes (`VGP`) ; le choix des `PRS_NAT` qui définissent « le recours au pharmacien » est une décision de l'axe 4, à
  enregistrer.
- **Statut libéral** : non renseigné hors régime général et régimes infogérés : filtrer sur `PSE_STJ_SNDS = 1` biaise
  le champ. Préférer `PRS_PPU_SEC = 2` (privé), cohérent avec « libéral = privé » (décision du 2026-11-14), à tester.
- **Censure** : c'est du recours observé, pas du besoin (dérivation §2).
