---
type: analysis
date: 2026-11-15
author: session besoin-axe0-interface
question: Le squelette du module de besoin (interface, M0, indice C, transferts, sortie d'API) tient-il ses sept critères d'identité sans toucher au jumeau ?
headline: "7/7 critères passés : M0 redonne densité/densité₂₀₂₆ à 1,3 × 10⁻¹⁵ près, conservation des transferts à 5,7 × 10⁻¹⁰ ETP, additivité commune → national à 1,5 × 10⁻¹⁴ relatif, 0,72 ms au 95ᵉ centile (budget 5 ms) ; jumeau.check 18/18 inchangé"
status: draft
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: "Aucune : tests d'identité (plan, axe 0)"
sources: [data/processed/population.parquet, v2/data/processed/commune_geo.parquet, v2/data/processed/secteur_stock.parquet, v2/data/processed/infirmiers_secteur_age_sexe.parquet]
tags: [besoin, interface, M0, couverture, transferts, axe0]
---

# Module de besoin, axe 0 : interface, M0, indice de couverture, transferts

> **Headline :** les sept critères d'acceptation de l'axe 0 passent. Chacun porte un contrôle qui le fait échouer
> sur une entrée volontairement fausse. Le jumeau n'est pas modifié. Tous les paramètres sont des placeholders
> étiquetés « supposé » en attendant l'axe 1.

## Question
Le [plan](../derivations/2026-11-15-besoin-plan.md) (axe 0) demande un squelette `v2/besoin/` qui produit B et C
sans écrire dans les effectifs. Il demande aussi qu'on puisse ajouter un estimateur sans toucher à un autre fichier.
La [décision O2](../decisions.md) interdit tout indice de couverture pour la médecine générale.

## Result
Mesuré par `PYTHONPATH=v2 uv run python -m besoin.tests` (2026-11-15). Résultats dans
`v2/artifacts/besoin_a0/results.json`, hors git.

| # | Critère | Verdict | Mesure | Contrôle (doit échouer) |
|---|---|---|---|---|
| 1 | M0 : `C = densité / densité₂₀₂₆` à 10⁻⁹, 5 professions, dép., 2026–2050 | **passé** | écart max 1,3 × 10⁻¹⁵ | scénario Omphale « haut » au lieu de « central » : 0,35 |
| 2 | transferts à 0 : effectifs, offre, B et C identiques bit à bit ; `jumeau.check` 18/18 | **passé** | empreinte SHA-256 de N identique avant/après ; B, C, base égaux bit à bit ; `jumeau.check` 18/18 (C1–C18, plus T), code de sortie 0 | transfert actif : C ≠ base |
| 3 | additivité de B entre échelles, 10⁻⁹ relatif ; C par sommes | **passé** | com → dep 4,1 × 10⁻¹⁵ ; com → rég 2,7 × 10⁻¹⁵ ; dep → nat 1,5 × 10⁻¹⁴ ; C régional 8,9 × 10⁻¹⁶ | moyenne des C départementaux : 0,17 |
| 4 | conservation `ΣB' − ΣB = s·a·B_A·(k−1) + m` à 10⁻⁶ | **passé** | 5,7 × 10⁻¹⁰ ETP sur 13 947 ETP déplacés ; 3/3 contraintes refusées ; B' ≥ 0 | k biaisé de 10⁻³ : 23,5 ETP |
| 5 | latence < 5 ms ajoutées au département, 95ᵉ centile, n ≥ 30 | **passé** | 0,72 ms au 95ᵉ centile (n = 60 par profession, pire des 5) | première version : 10,5 ms (échec, corrigé) |
| 6 | ajouter un estimateur ne modifie aucun autre fichier | **passé** | estimateur déposé dans un dossier temporaire, servi par son nom ; 11 fichiers `.py` de `v2/besoin` inchangés (SHA-256) | nom inconnu refusé |
| 7 | aucun C pour la MG (ni les spécialistes) | **passé** | 0 clé MG ou spécialistes en sortie ; 6/6 chemins refusés (offre, couverture, agrégat, cible de transfert) ; « ETP de MG libérés » rapportés | — |

Latence par profession (ms, p50 / p95, mesuré) : SF 0,62 / 0,64 ; CD 0,62 / 0,64 ; PH 0,68 / 0,69 (avec L23) ;
MK 0,62 / 0,70 ; IDE 0,70 / 0,72. La carte (< 150 ms) n'est pas mesurée : le module n'y est pas branché.

## How
- **Données :** population Insee Omphale 2022 (`data/processed/population.parquet`, dép. × sexe × âge × année,
  3 scénarios) ; communes Insee (`v2/data/processed/commune_geo.parquet`) pour la ventilation de test ; offre =
  trajectoire tendancielle du jumeau (stock-flux à taux locaux, secteur privé), `sector_table` de l'axe 4.
- **Méthode :** le besoin est **lu** sur la trajectoire, après le run, et jamais rendu comme flux du moteur.
  - `interface.py` : `NeedEstimator` (`fit` / `predict` / `assumptions`, `norme`, `params` en `jumeau.module.Param`),
    registre et `discover()`.
  - `estimateurs/m0.py`, `couverture.py` (offre, C, agrégation), `transferts.py`, `sortie.py` (`besoin_api`).
- **Tests :** [`v2/besoin/tests/criteres.py`](../../../besoin/tests/criteres.py). La densité de B1 est recalculée par
  un chemin pandas indépendant (format long du jumeau, parquet relu).

Choix d'implémentation (registre, même date) :
- **lecteur, pas module de flux** : le moteur applique à N tout flux rendu. Un lecteur garantit par construction
  qu'il n'écrit pas dans les effectifs, sans modifier `v2/jumeau/` ;
- **indexation sur la base** : C du scénario est divisé par `S/B` de la base, sans transfert, à 2026. Un transfert
  actif dès 2026 se lit ainsi contre la même référence ;
- **expansion** : `m = μ · s·a·B_A·k`, en temps de la cible, avec μ = 0 par défaut.

## ⚑ What could make it wrong
- **Placeholders partout** (supposé) : activité 1 ETP par professionnel, r̄ de la MG et des spécialistes
  0,9 × 10⁻³ ETP/hab, L23 (a = 0,01, k = 1, s_∞ = 0,6, τ = 3 ans, μ = 0). Sous M0, ils ne changent pas C sans
  transfert (r̄ et activité s'annulent). Avec un transfert, ils fixent l'ampleur de l'effet. Aucun chiffre d'effet
  de L23 n'est donc présentable avant l'axe 1.
- **r̄ des professions de sortie** = offre nationale / population nationale en 2026 : c'est une **norme** (« l'offre
  de 2026 satisfait le besoin »), pas une mesure. Elle est déclarée dans `M0.norme`.
- **Population communale ventilée** au prorata de la population communale, avec la structure d'âge du département.
  Elle sert au test d'additivité, pas de projection communale.
- **Le critère 2 « au commit de référence »** est vérifié par l'empreinte de N avant/après et par `jumeau.check`. Il
  n'y a pas de comparaison à un fichier d'effectifs figé, puisque `v2/jumeau/` n'est pas modifié.
- **`jumeau.check` a besoin des données brutes** (`data/raw`, `v2/data/raw`, hors git). Dans le worktree, elles ont
  été reliées par lien symbolique au dépôt principal le temps du passage, puis les liens ont été retirés.
- **Latence mesurée sur une machine** (portable de développement), sur la trajectoire déjà calculée : c'est le temps
  ajouté par le besoin, pas celui du run du jumeau.

## → What it changes
- **Axe 2** (M1–M4, transferts) : chaque estimateur se dépose dans `v2/besoin/estimateurs/`. Il est jugé par les
  mêmes critères ; M1 doit redonner B1 quand le profil est plat.
- **Axe 1** : les fiches remplacent les placeholders `r_bar`, `activite` et `L23_PARAMS`, sans toucher au code.
- **Carte / API** : `besoin.sortie.besoin_api` est prêt. Le branchement attend l'accord (question au ledger).

## ? Next
| Item | Cost |
|---|---|
| Brancher `besoin_api` dans `/api/carte` (couverture, couverture_base) et mesurer la carte < 150 ms au 95ᵉ centile | ~30 min Claude, après accord |
| Une table d'offre multi-professions (tranches d'âge différentes par source) : un seul appel pour les 5 professions | ~20 min |
| Remplacer les placeholders par les fiches de l'axe 1 | ~10 min après l'axe 1 |
