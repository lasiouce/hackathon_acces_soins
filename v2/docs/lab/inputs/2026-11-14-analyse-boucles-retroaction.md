---
type: input
date: 2026-11-14
author: utilisateur·rice (analyse transmise), revue par la session v2
status: référence, non adoptée
tags: [rétroaction, non-linéarité, sensibilité, axe2, axe5]
---

# Analyse transmise : stock-flux, Morris/Sobol, dynamiques non linéaires et boucles de rétroaction

**Statut.** Gardée comme référence, à la demande de l'utilisateur·rice (2026-11-14 : « pas
maintenant »). Rien n'est lancé.

## Contenu, en résumé
1. Le stock-flux par composantes comme socle : N(t+1) = max(0, s ⊙ Shift(N) + k(t)(I + p·h)),
   avec des opérateurs typés, un levier retraite calibré sur le temps de séjour, et la
   régulation E ≤ X avec une fuite θ.
2. Morris (μ*, σ) puis Sobol (S_i, S_Ti).
3. Alternatives : dynamique des systèmes, ABM, microsimulation, bayésien hiérarchique. Voie
   recommandée : un hybride.
4. Non-linéarités : seuils, rétroactions positives et négatives, délais.
5. Trois boucles formalisées, sur l'exemple des kinés :
   - charge → départs : d = d₀(1 + α max(0, C/C* − 1)^β) ;
   - densité → attractivité, en sigmoïde ou en exponentielle ;
   - régulation : E = min(E souhaité, θX).
6. Conclusion : garder le stock-flux, renforcer l'estimation et l'incertitude, introduire des
   boucles là où elles sont justifiées empiriquement, valider à chaque échelle.

## Revue (session v2, 2026-11-14)
**Ce qui concorde avec le projet.**
- Les sections 1 à 3 décrivent fidèlement le jumeau et les axes 2 et 5.
- La recommandation hybride est le programme de l'axe 2 (décision « Programme de l'axe 2 »).

**Les nuances.**
1. **Échelle communale.** Le coût n'est pas encore « raisonnable » à la commune : environ
   6,8 s par scénario pour une cible de 2 s (C15 de l'axe 0, en cours).
2. **Paramètres non identifiables.** α, β, γ, δ, C* et D* n'ont pas de source et ne sont
   probablement pas identifiables avec 15 ans de stocks par département. Un Sobol sur ces
   paramètres mesurerait nos a priori.
3. **La boucle 1 suppose un module de besoin** (charge = P/N), qui reste une question ouverte.
4. **La boucle 2 doit être estimée, pas supposée.** C'est le logit conditionnel
   d'installation de l'axe 2 (étape 3), avec la densité comme covariable. Les données
   viennent de l'axe 4 : proxy d'installations nettes par commune, 2012-2025.
5. **Bornes déjà dérivées** (derivations/stress-tests-and-feedback, H3) :
   - une réallocation ne dépasse pas le flux d'entrants, soit environ 3 % du stock par an ;
   - les tests K-cons (conservation du total national) et K-osc (oscillation) s'appliquent à
     toute boucle.
6. **Validation par expérience naturelle** (axe 3, N3) : elle avait échoué au département pour
   les infirmiers et est reprise par bassin de vie.

**Conduite proposée, en attente.**
1. Tester le signe empiriquement, environ 1 h par boucle : densité → installations, et
   densité → départs avant 60 ans.
2. Si la boucle 2 est confirmée, l'ajouter comme covariable du logit de l'axe 2.
3. Garder la boucle 1 comme scénario de stress, étiqueté « supposé ».
4. Ensuite seulement, faire un Sobol qui sépare les paramètres estimés des paramètres supposés.
