---
type: analysis
date: 2026-11-14
author: Claude
question: Le jumeau, corrigé deux fois, tient-il une troisième revue adversariale ?
headline: "Oui pour les défauts bloquants : il n'en reste plus dans le jumeau. Le seul défaut bloquant était dans le prototype (plantage à la réactivation de la régulation) et il est corrigé. Restent 5 défauts importants confirmés (bornes contournables, rétention > 1 possible, aller-retour JSON, plusieurs tranches 65+) et 3 non vérifiés"
status: done
professions: [all]
hypothesis: axe 0
sources: [v2/jumeau (2026-11-14, après la seconde revue), v2/prototype/server.py]
tags: [revue, axe0, jumeau, validation]
---

# Troisième revue adversariale du jumeau

> **Headline :** il ne reste aucun défaut bloquant dans le jumeau. Les 4
> défauts de la seconde revue sont corrigés dans la configuration réelle.
> Le défaut bloquant trouvé concernait le prototype et il est corrigé. La
> conservation est vérifiée : en 2050, le total tous secteurs du scénario
> régulé diffère du tendanciel d'au plus 0,5 personne (CD, MK, SF, mesuré).

## Résultats (6 constats soumis à réfutation, 6 confirmés)

| # | Gravité | Défaut | Où | Statut |
|---|---|---|---|---|
| 1 | bloquant (prototype) | La régulation ajoute un secteur `bloques`, donc l'état du scénario a plus de cellules que le tendanciel, et `server.py` plantait (IndexError, 606 contre 404) | `v2/prototype/server.py:127` | **corrigé** : un masque par trajectoire |
| 2 | important | Les bornes se contournent en empilant des événements `mul`/`add` (×243 → +14 317 %), et NaN passe la validation | `scenario.py:73-75, 98-102` | ouvert (axe 0) ; le prototype borne lui-même ses entrées et refuse NaN |
| 3 | important | Les bornes ne s'appliquent pas aux événements portant sur un paramètre ajusté : `sorties.retention × 1,3` donne une rétention > 1, donc des créations (+127 929 au lieu de −2 588) | `scenario.py:101` | ouvert (axe 0) |
| 4 | important | Après un aller-retour JSON, `over()` retire la composition de base, ce qui casse la régulation | `scenario.py:107` | ouvert (axe 0) |
| 5 | important | Levier retraite : le séjour en 65+ n'augmente pas exactement de +Δ quand il y a plusieurs tranches ≥ 65 (spécialistes, `stock.parquet`) | `modules/sorties.py:56` | ouvert. Ne touche pas les 5 professions de la phase 1, qui ont une seule tranche 65+ ; concerne la phase 2 |

**Non soumis à réfutation :**
- C2 et C4 ne testent pas la règle « entrées ≤ sorties » elle-même : une mutation qui bloque toutes les entrées passe les deux critères.
- La régulation déplace des entrées négatives vers `bloques`, et le plancher peut y créer des praticiens.
- Une régulation datée (un Event sur `regulation.zones`) passe la validation puis plante.

## → Ce que ça change
- **Le prototype réactive les leviers retraite et régulation**, avec des
  bornes côté serveur : quotas [0,7 ; 1,5], retraite [−2 ; 3]. NaN est
  refusé. Vérifié dans le navigateur : kinés, retraite +1 an et régulation
  → −5 781 en 2050, dont régulation −9 127 et sorties +3 347.
- Les défauts 2 à 5 vont à l'axe 0. Le constat non vérifié sur C2/C4
  (règle non testée) est à traiter avant de citer un chiffre de régulation
  dans un prétirage.
