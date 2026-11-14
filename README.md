# Jumeau numérique de l'offre de soins libérale

> Hackathon santé publique : **« Anticiper l'évolution de l'offre de soins »**

Un projet de recherche quantitative. On simule des **politiques publiques nationales** et on mesure
leur effet sur le nombre de professionnels de santé **libéraux** (hors médecine générale) jusqu'en
**2050**, à toutes les échelles, de la commune au national. Chaque politique est un réglage
d'hyperparamètres **sourcés** : quotas de formation, âge de départ, diplômés à l'étranger, régulation
de l'installation, etc. Chaque résultat est **reproductible, falsifiable et interprétable**, sans
boîte noire.

## Sommaire

- [Le problème](#le-problème)
- [Notre réponse](#notre-réponse)
- [Ce que fait le jumeau](#ce-que-fait-le-jumeau)
- [Données et méthode](#données-et-méthode)
- [Démarrage rapide](#démarrage-rapide)
- [Architecture](#architecture)
- [Confidentialité des données](#confidentialité-des-données)
- [Limites connues](#limites-connues)
- [Feuille de route](#feuille-de-route)

## Le problème

Former un professionnel de santé prend de 3 à 10 ans. Une décision prise aujourd'hui (quotas,
régulation de l'installation, âge de départ) ne produit son plein effet que bien plus tard, et souvent
ailleurs que là où on l'attendait. Les projections publiées (DREES, Insee) sont nationales et
tendancielles. Il manque un outil qui dise, **pour un territoire donné**, ce qu'une politique change
et avec quelle incertitude.

## Notre réponse

| Axe | Contenu | État |
|---|---|---|
| 0. Jumeau | État unique (profession × secteur × âge × sexe × territoire × année), modules de flux en plug-ins, scénarios | ✅ 10 critères d'acceptation sur 10, revue adversariale passée puis corrigée |
| 1. Hyperparamètres | Fiches sourcées : régulation conventionnelle, filières en pharmacie, spécialisation en odontologie, abandon en IFSI… | ✅ 27 fiches |
| 2. Méthodes | Battre le stock-flux sans boîte noire (âges fins, shrinkage hiérarchique, choix d'installation…) | 🔄 en cours |
| 3. Validation | Protocoles pré-enregistrés (gelés par SHA-256) : prévision, long terme, effet des leviers (différence de différences), échelle fine | ✅ protocoles écrits, en partie exécutés |
| 4. Données | Séparation public / privé, registre de 30 événements datés, zonage par commune | ✅ |
| 5. Sensibilité | Morris puis Sobol : quels paramètres déplacent vraiment l'effectif en 2050 ? | 🔄 en cours |
| Phase 2 | Cardiologie, dermatologie, ophtalmologie | à venir |

Professions couvertes : **sages-femmes, chirurgiens-dentistes, pharmaciens,
masseurs-kinésithérapeutes, infirmiers**.

**Pourquoi « libéral » au sens large ?** Ici, « libéral » désigne **tout le secteur privé**,
lucratif ou non : libéraux et mixtes, pharmaciens adjoints d'officine, salariés de cliniques privées,
industrie. Tout employeur public est exclu. C'est plus large que le sens habituel du RPPS ou
d'ameli (exercice indépendant), et chaque sortie le rappelle.

### Utilisateurs visés (couche ultérieure)

| Persona | Niveau | Usage |
|---|---|---|
| ARS / directeur général | commune → groupes de communes → département → région | hebdomadaire, visibilité maximale |
| Administration | France / régions | quotidien, tous les paramètres |
| Décideur politique | France | occasionnel, mode simple |

## Ce que fait le jumeau

- **Un état, des flux, des scénarios.** Chaque année, les modules (vieillissement, sorties,
  entrées, formation, régulation…) lisent l'état et écrivent des flux. Un registre garde chaque
  flux, si bien que tout écart s'explique par ses composantes.
- **Les leviers sont des événements datés** : « quotas × 1,2 à partir de l'année de décision +
  durée des études », « régulation activée dans telle liste de géocodes ». Un scénario se sérialise
  en JSON et se rejoue à l'identique.
- **Régulation par géocodes.** En zone « remplacement d'un départ seulement », les entrées ne
  peuvent pas dépasser les sorties. L'excédent est déplacé (par défaut vers le secteur public),
  jamais perdu.
- **Plusieurs estimateurs, pas un chiffre unique.** Persistance, tendance et variantes du
  stock-flux sont comparés sur le même banc.
- **Rapide.** Un scénario se recalcule en 17 ms au département (mesuré).

## Données et méthode

| Donnée | Producteur | Période | Usage |
|---|---|---|---|
| Démographie des professionnels de santé (RPPS), département × âge × sexe × mode × secteur | DREES | 2012-2026 (kinés : 2017-2026) | stock et taux |
| Infirmières libérales (SNDS), infirmières salariées (BTS) | DREES / Insee | 2012-2023 | stock IDE |
| Projections de population Omphale (département × âge × sexe) | Insee | 2018-2070 | population, densités |
| Effectifs libéraux, 23 spécialités | ameli (Assurance Maladie) | 2010-2025 | contrôle croisé |
| Effectifs par commune et zonage conventionnel | CartoSanté / Atlasanté | 2004-2025 | échelle communale, régulation |
| Établissements (FINESS) | Ministère de la Santé | 2026 | séparation public / privé |
| Projections DREES (Dossier n°76, ER 1319) | DREES | 2021-2050 | comparaison à long terme |
| Inscriptions en santé par université | DREES (SISE) | 2020-2025 | vivier, **fichiers organisateurs non versionnés** |

Points de méthode :

- **Modèle de départ : stock-flux par cohortes**, en tranches d'âge de 5 ans. Taux de rétention
  ajustés par territoire, avec un shrinkage vers le national. Les entrées sont un flux absolu
  (pas de rétention supérieure à 1, pour éviter le double comptage relevé lors du backtest K1).
- **Backtest contre des références naïves.** Par département, à 5-8 ans : 8,08 % de MAPE pour
  le stock-flux à taux locaux, contre 8,68 % pour la tendance (mesuré sur l'ancien périmètre
  libéral + mixte).
- **2050 ne se backteste pas.** Les données vont de 2012 à 2026, donc on valide au plus
  sur environ 10 ans. Au-delà, on s'appuie sur la reproduction des projections DREES, les cas
  limites du modèle et des fourchettes extrapolées, toujours affichées comme telles.
- **Chaque nombre dit s'il est mesuré, sourcé, dérivé ou supposé.** Chaque entrée cite son jeu de
  données et son millésime. Le vocabulaire reste neutre : on décrit et on compare, on ne juge
  pas (« accès moindre », jamais « désert »).

## Démarrage rapide

Prérequis : Python 3.12+ et [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python -m sante.load                                 # données ouvertes -> data/processed/
uv run python v2/data/build_secteur.py                      # séparation public / privé (≈ 30 s)
uv run python v2/data/build_zonage.py                       # zonage par commune
PYTHONPATH=v2 uv run python -m jumeau.check                 # critères d'acceptation du jumeau
uv run python -m sante.backtest                             # banc de comparaison des estimateurs
PYTHONPATH=v2 uv run python -m methodes.banc                # axe 2 : nouvelles méthodes
PYTHONPATH=v2 uv run --with scipy python -m validation.did  # axe 3 : effet de la régulation
```

Application de démonstration v1 (Streamlit) :

```bash
uv run --directory app streamlit run main.py
```

Les fichiers des organisateurs (inscriptions par université) sont à copier à la main dans
`data/raw/`. Ils ne sont jamais commités.

## Architecture

```
v2/                        travail actuel (le recadrage du 2026-11-14 prime)
  ROADMAP.md               objectif, axes de recherche, ordre de travail
  jumeau/                  état, moteur, scénarios, modules de flux (plug-ins), critères
  methodes/                axe 2 : estimateurs et modules candidats, banc
  validation/              axe 3 : protocoles pré-enregistrés, prévision, DiD, échelle fine
  sensibilite/             axe 5 : Morris, Sobol, fourchettes à 2050
  data/                    axe 4 : scripts public/privé, zonage, events.csv
  prototype/               écran de décision (en cours)
  docs/lab/                décisions, questions ouvertes, rapports, fiches, design
sante/                     v1 (figée) : chargeurs, estimateurs, backtest
app/                       v1 (figée) : application Streamlit
docs/lab/                  v1 (figée) : registre de laboratoire
Home.md                    page d'accueil du coffre Obsidian
```

Le dépôt est aussi un **coffre Obsidian** : ouvrez la racine dans Obsidian et commencez par
`Home.md`. Chaque décision est datée dans `v2/docs/lab/decisions.md`, et chaque question ouverte
a un prix dans `v2/docs/lab/open.md`.

## Confidentialité des données

Le dépôt est **privé**, réservé à l'équipe.

- `data/raw/`, `data/processed/`, `v2/data/raw/` et `v2/data/processed/` sont exclus par
  `.gitignore`. Ils se régénèrent avec les commandes ci-dessus.
- Les fichiers fournis par les organisateurs sont couverts par un accord de confidentialité et ne
  sont **jamais** versionnés, ni bruts ni dérivés à la maille université.
- Les documents tiers (mémoire EHESP) restent en local.

## Limites connues

- **Le public et le privé ne sont séparés que par estimation.** Les fichiers DREES regroupent les
  salariés hospitaliers. La sortie 2026 est donc une fourchette (sages-femmes : 12 059 à 14 660).
- Les tranches d'âge de 5 ans supposent des âges uniformes dans chaque tranche, ce qui conduit à
  surestimer les seniors (biais connu, traité par l'axe 2).
- Le levier « âge de départ » s'applique encore de façon permanente à la tranche ouverte 65+ et
  surestime donc son effet (correctif identifié, à intégrer).
- À la commune, le recalcul prend environ 3 s (extrapolé). Il faudra précalculer pour une
  interface fluide.
- Les effectifs sont comptés en têtes, pas en équivalents temps plein.

## Feuille de route

- Terminer les axes 2 (méthodes) et 5 (sensibilité), puis une seconde revue adversariale du jumeau.
- Prototype de l'écran de décision : écart au tendanciel expliqué par flux, délai d'effet,
  fourchette. Direction artistique « sémiologie graphique », tokens modifiables dans Figma.
- Phase 2 : cardiologie, dermatologie, ophtalmologie (appui : rapport HCAAM sur les dépassements
  d'honoraires).
- Couche personas et restitution, en s'appuyant sur l'observatoire de l'équipe.

Détail : [`v2/ROADMAP.md`](v2/ROADMAP.md).
