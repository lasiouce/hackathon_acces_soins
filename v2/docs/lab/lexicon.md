---
type: lexicon
aliases: [Lexique, Lexicon]
status: draft
---

# Neutral lexicon (UI text, especially the politician view)

Rule: **describe and compare, never judge.** Every qualitative word states
its reference point (national average, regional average, the same territory
in a past year). It must also be reproducible from a number shown next to it.

Draft list. The team adds and reviews entries. An LLM that writes UI text
gets this table as a constraint.

| Avoid (value judgement or alarm) | Use (descriptive, comparative) |
|---|---|
| l'accès aux soins est médiocre / mauvais | l'accès aux soins est **moindre** (que la moyenne nationale / régionale) |
| désert médical | territoire où la densité de professionnels est **inférieure à la moyenne** |
| pénurie, manque | **écart** entre l'offre projetée et les besoins projetés |
| sur-doté, trop de professionnels | densité **supérieure à la moyenne** |
| situation catastrophique / critique / alarmante | la densité **diminue de X %** d'ici AAAA |
| les territoires abandonnés / oubliés | les territoires où la densité a **le plus baissé** |
| bon / mauvais élève | au-dessus / en dessous de la moyenne |
| échec de la politique X | l'effet projeté de X est de **+/− N professionnels** |
| il faut / on doit | le scénario X conduit à … ; le scénario Y conduit à … |
| prévision, ce qui va arriver | **projection** sous hypothèses (always state the scenario) |

Number rules:
- Always give the reference point and the year.
- Give a range when one exists ("entre 410 et 450").
- Prefer densities (per 100,000 inhabitants) to raw counts when comparing
  territories.

## Vocabulaire des grandeurs (2026-11-14) — un mot par plage, calculé par le code

Les qualificatifs de grandeur ne sont **jamais choisis par le modèle de langage** : la passerelle du chatbot
(`chatbot/passerelle/requetes.py`, `qualificatifs`) les calcule à partir des seuils ci-dessous et les joint à chaque
résultat ; l'agent ne peut employer que ceux-là, et un contrôle automatique le vérifie (`chatbot/chat/verif.py`).
Seuils **supposés** (aucune norme publiée trouvée) : à valider par l'équipe, à changer ici et dans le code ensemble.

| Grandeur | Mesure | Mots (dans l'ordre des plages) |
|---|---|---|
| Évolution depuis l'origine, ou écart au tendanciel | variation relative, % | **stable** (\|x\| < 1) · **légère hausse / baisse** (1 à 5) · **hausse / baisse marquée** (5 à 15) · **forte hausse / baisse** (≥ 15) |
| Densité comparée à la France | écart relatif à la densité France, % | **nettement inférieure à la moyenne nationale** (< −25) · **inférieure à la moyenne nationale** (−25 à −10) · **proche de la moyenne nationale** (±10) · **supérieure à la moyenne nationale** (10 à 25) · **nettement supérieure à la moyenne nationale** (> 25) |
| Incertitude | demi-largeur de la fourchette, % | **incertitude faible** (< 5) · **incertitude modérée** (5 à 15) · **incertitude élevée** (> 15) ; **extrapolée** au-delà de 10 ans d'horizon |
| Délai d'effet d'un levier | années entre la décision et le premier effet | **court terme** (< 3) · **moyen terme** (3 à 6) · **long terme** (> 6) |

Hors vocabulaire (signalés) : modeste, significatif, considérable, spectaculaire, massif, sensible, nette hausse,
importante hausse, faible hausse, et leurs féminins ou pluriels.
