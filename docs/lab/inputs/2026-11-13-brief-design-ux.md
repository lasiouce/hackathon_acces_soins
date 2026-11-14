---
type: input
date: 2026-11-13
author: UX designer (team), filed by Claude
tags: [design, personas, scope]
---

# Design brief (UX designer): "Anticiper l'évolution de l'offre de soins"

The designer's brief, filed verbatim. It is reconciled against
`decisions.md` at the end of this note.

> **CONTEXTE.** Domaine : Projet de Santé publique.
> L'évolution démographique des professionnels de santé et des besoins de la population est difficile à anticiper, ce qui complique la planification territoriale des soins. Avec à la clé des risques de pénurie de professionnels, des déséquilibres territoriaux et des difficultés d'accès aux soins.
>
> **Solution envisagée.** Développer un outil de modélisation exploitant les données ouvertes pour projeter l'évolution démographique des professionels de santé (hors médecine générale) et simuler différents scénarios. Un outil de modélisation qui permet de cartographier la présence d'infrastructures et ressources humaines de domaine de la santé, pour que les décideurs publics puissent prendre des décisions éclairées sur l'impact des politiques publiques.
>
> **OBJECTIF.** Aider les décideurs publics à anticiper les besoins, adapter les ressources et améliorer la répartition territoriale de l'offre de soins.
> - Objectif 1 — Visualisation de l'état présent du système de santé publique en France
> - Objectif 2 — Identification des paramètres clés pour modéliser l'évolution du système de santé publique
> - Objectif 3 — Synthèse de l'impact des politiques publiques et leur mise en opération
>
> **CIBLE.**
> - Persona 1. Niveau national — Politiques publiques de santé. Ne connaît pas les paramètres, il veut voir si ces idées marchent. Fréquence d'accès : occasionnel. Niveau sémantique : professionnel.
> - Niveau régional — Persona 2. Fonctionnaires du Ministère de la Santé. Fréquence d'accès : journalier.
> - Persona 2 bis. ARS — Agence Régionale de Santé. Fréquence d'accès : hebdomadaire ?
>
> **SCOPE.** Système de santé de toute la France : au niveau national des politiques publiques, et au niveau régional au niveau des régions, départements et des villes.
>
> **VALEUR.** 1. Aide à la prise de décision des politiciens sur le domaine de la santé. 2. Facilite la mise en place des politiques publiques au niveau régional. 3. Facilite la gestion de ressources de santé publique.
>
> **RISQUES.** Questions ? **Veille.**

## Reconciliation with the record (Claude, 2026-11-13)

| Brief | Record | Status |
|---|---|---|
| Persona 1 (national policy, occasional, doesn't know the parameters) | "politician" persona | **matches** |
| Persona 2 (ministry officials, **daily**) | "Administration" persona (every parameter) | matches. New fact: daily use |
| Persona 2 bis (ARS, **weekly?**) | ARS zoom commune → groups → dép → région | matches. New fact: weekly use, still a "?" |
| Persona 1 semantic level "**professionnel**" | lexicon: neutral, descriptive wording | compatible: professional register *and* neutral. Not plain popular language |
| Objectives 1 / 2 / 3 | stage 1 (demography), lever registry, scenarios | matches |
| "Cartographier la présence d'**infrastructures**" | not in any decision | **NEW SCOPE**, open: health establishments (e.g. the FINESS register) are not in stage 1 |
| Scope down to "villes" | ARS commune decision | matches |
