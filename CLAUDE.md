# hackathon-sante — projecting France's health workforce (48 h, 10 people)

## The brief
Build a tool that uses French **open data** to project how many health
professionals there will be, by profession and territory, and lets the user
simulate policy scenarios. The goal is to help public decision-makers
anticipate shortages and territorial imbalances. **General practice is
excluded.**

Scope is **MMOPKSI**: médecins spécialistes, sages-femmes,
chirurgiens-dentistes, pharmaciens, masseurs-kinésithérapeutes and infirmiers.
The liberal sector comes first.

The kind of question the tool must answer: *how many specialists in
Clermont-Ferrand in 2035 if pharmacists can vaccinate?* It needs a visual
picture of the system, many policy levers, and both the state of the system
and its demography.

**Recadrage 2026-11-14 (prime sur le paragraphe ci-dessus).** Projet de
recherche quantitative.
- Sorties : effectif « libéral » (secteur privé, tout employeur public
  exclu) des sages-femmes, dentistes, pharmaciens, kinés et infirmiers.
- Échelles : toutes, jusqu'à la commune. Horizon 2050.
- Spécialistes en phase 2 (cardiologie, dermatologie, ophtalmologie).
- Personas et application : couche ultérieure.
- Voir [`v2/ROADMAP.md`](v2/ROADMAP.md).

**Dossier v2 (2026-11-14).** Tout nouveau travail va dans `v2/` : code,
`v2/docs/lab/` (décisions, ledger, rapports, fiches).
- La v1 (`sante/`, `app/`, `docs/lab/`) est figée et se consulte en lecture
  seule.
- Pour les sessions v2, les règles sur `docs/lab/decisions.md` et
  `open.md` s'appliquent à `v2/docs/lab/`.

## Lab profile
[`docs/lab/profile.md`](docs/lab/profile.md) holds the headline metric (decision usefulness **and**
backtest accuracy), the currencies (480 person-hours, MAPE, levers wired end to
end, < 2 s recompute) and where records go. Every `lab` skill reads it.

## Two rules that change behaviour
1. **Non-trivial work starts with a plan and a challenge.** That means a new
   model component, a data source choice, or a lever's mechanism. Use
   `derive-ansatz` for a new problem and `challenge-design` when something
   already exists. State the constraint in a unit and give a verdict.
   Hackathon speed: the plan is a few lines, never a document.
2. **Every step ends with a filed record and the four-part TL;DR.**
   - The record goes in `docs/lab/` (decisions, explorations, reports), and
     open questions go in `docs/lab/open.md` with a price.
   - The TL;DR is: the number · ⚑ what could make it wrong · → what it
     changes · ? what to study next, with a cost.

## Obsidian vault: how work is organised and presented
The repo root is an Obsidian vault (core plugins only, nothing to install).
[`Home.md`](Home.md) is the entry point.
- Every analysis gets a note in `docs/lab/reports/`, made from
  `docs/templates/analysis.md`. Its frontmatter carries a `headline` with a
  number.
- Every analysis also gets a row in Home's **Analyses log**. Update Home's
  **Status** table when it moves.
- Decks for colleagues go in `docs/lab/presentations/`, made from
  `docs/templates/deck.md`. Slides are separated by `---`, and the deck is
  shown with Obsidian's *Start presentation*.
- Diagrams are Mermaid. Figures go in `docs/lab/figures/`.

## Decisions: every session records them, every session checks them
This applies to every session working in this folder, sub-sessions included.
- **Every decision is recorded in the vault.** A choice made, changed or
  rejected gets a dated entry in [`docs/lab/decisions.md`](docs/lab/decisions.md). That covers
  a method, a parameter value, a scope cut, a data source, or a UI rule.
  - An open choice goes under `## Open / not yet decided`.
  - Never only in chat, and never only in a report.
  - Supersede, never erase: the old entry stays, marked superseded with the
    date.
- **Consistency check every 10 tool calls.** A project hook
  (`.claude/hooks/consistency_check.py`, registered in
  `.claude/settings.json`) reminds the session.
  - Re-read `decisions.md` and compare it with the last 10 calls' work.
  - If something contradicts a recorded decision, **stop and flag it to the
    user** before going on.
  - Record any decision that isn't recorded yet.

## House rules
- **We build estimation algorithms, not one exact number.** Every
  estimator goes behind the common interface in `sante/estimators.py`.
  The backtest compares them; no single figure is presented as "the"
  projection.
- **Neutral wording.** UI text follows [`docs/lab/lexicon.md`](docs/lab/lexicon.md): describe
  and compare (e.g. "accès moindre"), never judge ("médiocre", "désert").
- **Three personas share one model**: ARS/DG (zoom commune → groups of
  communes → département → région),
  Administration (all parameters), politician (plain mode). Stage 1 is the
  demographic projection only (Hippocrate + Omphale).
- Every input names its dataset and vintage. No closed data.
- A lever counts only when it is wired end to end and its effect cites a
  mechanism or a source. Never report the number of parameters as a result.
- Accuracy claims need a backtest against a naive baseline.
- Anything not demoable by H-6 gets cut.

## Skills
The lab process skills and the session helpers (`go`, `huh`, `last`,
`progress`, …) are vendored in `.claude/skills/`, so every teammate who clones
the repo gets them. The shared contract is in `.claude/reference/contract.md`.
Some skills assume `uv` and Python. `progress` expects `eta.py` at its
installed path.

## Git
- Dépôt autonome `hackathon_acces_soins`, indépendant de sevel.
- **Les messages de commit ne mentionnent pas Claude** : pas de ligne
  `Co-Authored-By: Claude …`, ni d'autre attribution à une IA.
- Des commits petits et thématiques (un sujet par commit).
- **À chaque changement majeur, mettre à jour `README.md` dans le même
  commit ou juste après.** Par changement majeur, on entend un nouvel axe ou
  un axe terminé, un changement de périmètre ou de définition, une nouvelle
  source de données, une nouvelle commande de lancement, ou un résultat
  chiffré qui remplace celui du README.
- Jamais de données brutes ni de fichiers d'organisateurs sous accord de
  confidentialité (voir `.gitignore`).

