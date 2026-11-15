---
date: 2026-11-15
statut: plan accepté par la session (tâche de besoin-axe5-sensibilite)
---
# Transfert de tâches hypothétique dans l'assistant — plan court avec challenge

ETA ~45 min (30–70) · Claude time + runs du jumeau (démarrage de la carte ≈ 1–2 min).

**Périmètre (une ligne).** L'assistant simule un transfert de tâches proposé par l'utilisateur·rice (« X font p % de
<acte> de Y »). Il passe par `/api/couverture` et répond en balayant `a`. Le résultat est étiqueté « hypothèse de
l'utilisateur ». L23 ne change pas.

**Hors périmètre.** Aucun nouveau levier ni interrupteur dans la carte : au plus un bandeau quand l'assistant propose un
transfert. Pas de projection de la MG ni des spécialistes, pas d'effet sur l'effectif (N9 : pas de rétroaction). Pas
de mode IA (aucune clé).

## Contrainte, en unités
- **Utilité de décision.** Une réponse chiffrée sur l'indice C de la cible (sans unité, 2026 = 1) qui ne se fait pas
  passer pour sourcée.
- **Latence.** Recalcul < 2 s (profil), en pratique < 150 ms comme K5 : pas de nouveau passage du jumeau.

## Forme : celle de L23, généralisée (`besoin/transferts.py`)
- `s(t) = s∞ (1 − e^{−(t−t₀)/τ})`.
- `B'_src = B_src (1 − s·a)` et `B'_cible = B_cible + s·a·k·B_src` (μ = 0).
- Dans `couverture_carte`, la vue est celle d'**une** profession `prof` :
  - si `prof` est la cible : `B1 = B1 + s·a·k·B_src` ;
  - si `prof` est la source (une des 5) : `B1 = B1 (1 − s·a)` ;
  - sinon : 400, car le transfert n'a pas d'effet sur la profession affichée.
- Appliqué **après** L23, sur les tableaux de besoin déjà en cache. Il n'y a ni nouveau passage du jumeau ni nouvelle
  entrée dans le cache du besoin. Les contraintes (s·a ≤ 1, k > 0, τ > 0, O2 sur la cible) restent celles de `Transfert`.

## Ce qui manque quand la source n'est pas la MG
| source | B_src servi | statut |
|---|---|---|
| médecine générale | M1 (profil DAMIR, r̄ = 0,9 × 10⁻³ ETP/hab. standardisé), pour **tous** les estimateurs de la cible (M2a et M3 n'ont pas de MG) | forme mesurée, niveau supposé |
| spécialistes | M0 (population × r̄ = 0,9 × 10⁻³ ETP/hab.) : aucun estimateur ne les sert | supposé (placeholder) |
| une des 5 professions | son propre besoin (même estimateur s'il survit pour elle, sinon M1), sur ses propres états | comme la profession |

Le **niveau** de `B_src` fixe l'ampleur : l'écart vaut à peu près `−s·a·k·B_src/B_cible`. Pour la MG et les
spécialistes, ce niveau est un placeholder. C'est le premier ⚑.

## Paramètres et défauts
Les défauts sont tous étiquetés « supposé (hypothèse de l'utilisateur) ».

| paramètre | sens | défaut | bornes |
|---|---|---|---|
| `tr_a` | part de la demande de la source concernée par l'acte | 0,10 | [0 ; 0,5] |
| `tr_sinf` | part de l'acte transférée à terme | 1 | [0 ; 1] |
| `tr_k` | temps de la cible par unité de temps de la source | 1 | [0,1 ; 3] |
| `tr_tau` | montée en charge, en années (forme de L23, empruntée) | 2,4 | [0,1 ; 20] |
| `tr_t0` | date d'autorisation | 2026 | [2026 ; 2050] |

Lecture d'une phrase :
- « p % **des <acte>** de Y » : `s∞ = p/100`. Le poids de l'acte `a` est inconnu, l'assistant **balaie
  a ∈ {5, 10, 20 %}**.
- « p % **de la demande / de l'activité / du temps** de Y » : `a = p/100` et `s∞ = 1`. L'assistant balaie
  `a ∈ {p/2, p, 2p}`.

## Challenge (alternative la moins chère, dérivée avant de relire l'existant)
- **Alternative :** calculer l'écart dans la passerelle à partir d'un ratio national
  (`écart ≈ −x/(1+x)`, `x = s·a·k·B_src/B_cible`).
- **Pourquoi elle perd :**
  - on perd le département ;
  - on crée une seconde source pour C, contraire à la décision « une seule source pour C (la carte) » ;
  - on ne peut plus vérifier que transfert générique = L23 avec les mêmes paramètres.
- **Verdict : la forme de L23 survit**, généralisée dans l'API.
- **Ce qui la contredirait :** un écart > 10⁻⁹ entre `tr_*` (paramètres de L23, MG → PH) et `l23=1` ; ou un p95 > 150 ms.

## O2 (correction)
- O2 refuse seulement quand la MG ou les spécialistes sont la **cible** de l'indice, c'est-à-dire « couverture des
  généralistes » ou une profession demandée qui est MG/spé.
- Une MG ou un spécialiste **source** d'un transfert est accepté.

## Critères d'acceptation
1. L23 inchangé : `l23=1` donne les mêmes `cs` qu'avant, bit à bit (comparaison avec la sortie d'avant le changement).
2. `tr_a=0` (ou `tr_sinf=0`) ⇒ écart 0 (≤ 10⁻¹²).
3. Transfert générique MG → PH aux paramètres de L23 = `l23=1`, à 10⁻⁹ près.
4. `tr_cible` MG ou spécialistes, ou hors des 5 ⇒ 400. `tr_src` MG ⇒ 200.
5. Compilateur : la phrase d'exemple donne un transfert hypothétique MG → IDE avec `s∞ = 0,10`, D63 et 2035.
6. Sans IA : la phrase d'exemple donne une réponse balayée (3 valeurs de a), étiquetée « hypothèse de l'utilisateur »,
   qui dit pourquoi ce transfert n'est pas un levier de la carte, sans refus O2. « Quelle couverture des généralistes… »
   ⇒ refus O2.
7. p95 de `/api/couverture` avec `tr_*` < 150 ms (à chaud).
