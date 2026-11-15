---
type: analysis
date: 2026-11-15
author: audit (session principale)
question: Le projet est-il conforme au RGPD, une AIPD est-elle obligatoire, et l'outil est-il un dispositif médical au sens du règlement (UE) 2017/745 ?
headline: "Pas un dispositif médical (aucune finalité médicale individuelle) ; AIPD probablement non obligatoire (2 critères G29 sur 9 au plus, données déjà publiques) ; un point RGPD réel : 52,5 % des 1 251 610 cellules commune × âge publiées sur un dépôt GitHub public valent 1 personne"
status: draft
professions: [sages-femmes, dentistes, pharmaciens, kines, infirmiers]
hypothesis: Le traitement ne porte que sur des données agrégées et ouvertes, sans finalité médicale
sources: [v2/data/processed/, data/processed/, chatbot/, v2/prototype-carte/, v2/prototype-carte/dsfr/LICENSE.md]
tags: [rgpd, aipd, dispositif-medical, conformite, faisabilite]
---

# Audit RGPD, AIPD et règlement 2017/745

> **Headline :** Le projet n'est **pas un dispositif médical**. Une **AIPD n'est probablement pas obligatoire**. Il reste **un point RGPD réel** : des cellules à 1 personne, au grain commune × tranche d'âge, sont republiées sur un dépôt GitHub **public**. S'y ajoutent deux points hors RGPD : l'habillage DSFR et l'absence de licence du code.
>
> Ce pré-audit a été fait par une IA, pas par un juriste ni un DPO. Il sert à préparer leur relecture, pas à la remplacer.

## Question
Le jury note la faisabilité sur 20 points, en citant « données, éthique, RGPD, cadre réglementaire (dispositif médical) ».
- La recette jury ([2026-11-15-jury-grille](2026-11-15-jury-grille.md)) a noté ce critère 5,5 sur 10, faute de tout document.
- Deux questions du registre sont concernées : `open.md`, « AIPD ou note de non-applicabilité » et « seuil de secret statistique ».

## Result

### 1. Inventaire des traitements (mesuré le 2026-11-15, commit 8d8df4a)

| Traitement | Données | Personnes concernées | Données personnelles ? |
|---|---|---|---|
| Construction des tables (local) | RPPS, Annuaire Santé, CartoSanté, ameli, FINESS, Insee | Professionnels de santé | **Oui à l'entrée.** L'Annuaire Santé est nominatif ; il reste dans `data/raw/`, ignoré par git. Aucun nom ni identifiant RPPS dans les 34 fichiers traités : colonnes vérifiées une à une. |
| Tables traitées commitées (dépôt **public** `progdinh/hackathon_acces_soins`) | Effectifs agrégés | Professionnels | **Oui pour une partie** : petits effectifs, voir 2. |
| Projection (jumeau, API, carte) | Agrégats département, région, France | — | Non : l'affichage s'arrête au département. |
| Assistant (`chatbot/`, `v2/agent/`) | Texte libre tapé par l'utilisateur, envoyé à l'API Anthropic | L'utilisateur, et toute personne qu'il nommerait | **Possible**, si l'utilisateur tape une donnée personnelle. |
| Serveurs | Requêtes HTTP | Utilisateur | Non conservées. Écoute sur `127.0.0.1` seulement, journaux de requêtes désactivés (`log_message` surchargé dans `v2/prototype/server.py`, `chatbot/passerelle/server.py`, `chatbot/chat/server.py`). Aucune écriture de conversation sur disque. |
| Fichiers des organisateurs (accord de confidentialité) | Inscrits par université | Étudiants | Exclus : `v2/data/manifest.py --check` → OK, aucun lu par un script de construction, aucun suivi par git. |

### 2. Petits effectifs dans les tables publiées (mesuré)

Part des cellules non nulles qui valent 1, ou moins de 5 :

| Fichier (dépôt public) | Grain | Cellules > 0 | n = 1 | n < 5 |
|---|---|---:|---:|---:|
| `v2/data/processed/commune_stock.parquet` | profession × commune × tranche d'âge × année | 1 251 610 | **52,5 %** | 87,3 % |
| `data/processed/stock_commune.parquet` | idem (v1) | 1 240 401 | 52,9 % | 87,9 % |
| `v2/data/processed/annuaire_commune.parquet` | profession × commune × sexe × mode × statut × lieu de diplôme | 114 634 | 38,1 % | 80,8 % |
| `v2/data/processed/flux_installations_commune.parquet` | profession × commune × année (moins de 40 ans) | 328 937 | 39,2 % | 80,7 % |
| `data/processed/stock.parquet` | profession × département × âge × sexe × mode | 954 367 | 33,9 % | 65,6 % |

**Lecture.** L'Annuaire Santé est public et nominatif : il donne le nom et la commune d'exercice. Une cellule à 1 dans `commune_stock` révèle donc la **tranche d'âge** d'un professionnel qu'on peut nommer. Dans `annuaire_commune`, elle révèle son **sexe** et son **lieu de diplôme** (France, UE, autre). Ce sont des données personnelles indirectement identifiantes (RGPD, considérant 26).

**Ce qui limite le risque.**
- Ces cellules viennent de sources déjà publiées au même grain (CartoSanté, Annuaire Santé). Le projet ne révèle rien de nouveau.
- Les données sont professionnelles (âge, sexe, lieu de diplôme). Ce ne sont pas des données de santé (art. 9) ; aucune donnée de patient n'est traitée.

Rendre une donnée publique ne la fait pas sortir du champ du RGPD. Sa réutilisation reste un traitement, avec une finalité et une base légale.

### 3. RGPD : constat article par article (dérivé)

| Exigence | Constat | État |
|---|---|---|
| Finalité (art. 5.1.b) | Projeter des effectifs agrégés pour la décision publique et la recherche. Compatible avec la finalité de publication des sources. | ✅ |
| Base légale (art. 6) | 6.1.f (intérêt légitime de recherche) pour l'équipe ; 6.1.e (mission d'intérêt public) si un ministère ou une ARS porte l'outil. **Non écrite.** | ⚠ à écrire |
| Minimisation (art. 5.1.c) | Noms et identifiants retirés dès la construction. **Mais** le grain commune × âge est publié alors que la carte ne l'affiche pas. | ⚠ |
| Recherche (art. 89) | Garanties possibles : agrégation, seuil de diffusion. Pas encore de seuil. | ⚠ |
| Information des personnes (art. 14) | Dérogation 14.5.b plausible : effort disproportionné, données publiques. Il faut quand même une mention publique (README, page « données »). | ⚠ à écrire |
| Sous-traitant hors UE (art. 28, chap. V) | L'assistant envoie le texte libre à Anthropic (États-Unis). Pas d'avertissement « ne saisissez pas de données personnelles », pas d'analyse de transfert. | ⚠ |
| Sécurité (art. 32) | Écoute locale, pas de journaux, clé d'API dans `.env` ignoré par git. | ✅ pour un prototype |
| Registre des traitements (art. 30) | Aucun. | ⚠ à créer si l'outil est déployé |

### 4. AIPD (art. 35) : test de seuil (dérivé)

Les lignes directrices du G29 (WP248 rév. 01), reprises par la CNIL, donnent 9 critères. Une AIPD est en principe requise à partir de 2.

| Critère G29 | Rempli ? |
|---|---|
| Évaluation ou notation de personnes | Non : aucun résultat individuel. |
| Décision automatisée à effet juridique | Non. Le zonage de régulation simulé concerne des territoires, et l'outil ne décide rien. |
| Surveillance systématique | Non. |
| Données sensibles ou hautement personnelles | Non : données professionnelles. |
| **Grande échelle** | **Discutable** : environ 600 000 professionnels couverts, mais en agrégats. |
| **Croisement de jeux de données** | **Oui** : RPPS, CartoSanté, Annuaire Santé, FINESS, ameli, Insee. |
| Personnes vulnérables | Non. |
| Usage innovant de la technologie | **Discutable**, et à compter traitement par traitement. Pour les tables des professionnels : non, c'est de l'agrégation classique. Pour l'assistant : **oui**, car la CNIL range l'IA parmi les usages innovants. Ce traitement-là ne porte que sur le texte libre de l'utilisateur, et ne remplit aucun autre critère. (Corrigé le 2026-11-15 : la première version disait « non » sans distinguer les deux traitements.) |
| Blocage d'un droit ou d'un service | Non. |

**Verdict : 1 à 2 critères. Une AIPD n'est probablement pas obligatoire.** L'opération ne figure pas non plus sur la liste CNIL des traitements soumis à AIPD.
- **Recommandation :** une **note de non-applicabilité** d'une page, signée par le porteur, plutôt qu'une AIPD complète.
- **Condition :** appliquer un seuil de diffusion (voir → ci-dessous). Avec le grain commune × âge publié tel quel, le critère « grande échelle » pèse davantage, et un DPO pourrait demander l'AIPD.

### 5. Règlement (UE) 2017/745, dispositifs médicaux (dérivé)

- **Définition (art. 2.1) :** un dispositif médical sert, chez l'humain, à une fin médicale : diagnostic, prévention, surveillance, prédiction, pronostic ou traitement d'une maladie.
- **Considérant 19 :** un logiciel à usage général n'est pas un dispositif médical, même utilisé en milieu de soins. Le guide MDCG 2019-11 exclut de même les logiciels de gestion ou d'administration et ceux qui ne traitent pas de données d'un patient pour son bénéfice individuel.
- **L'outil :** il projette des **effectifs de professionnels** pour la **planification publique**. Il ne reçoit aucune donnée de patient et ne rend rien pour une personne soignée.
- **Verdict : pas un dispositif médical, donc pas de marquage CE ni de classification (annexe VIII).**
  - **Condition :** la destination déclarée (« intended purpose ») doit rester sans revendication clinique. À écrire dans le README : « outil d'aide à la planification des effectifs ; ne fournit aucune information diagnostique ou thérapeutique sur un patient ».
  - Le futur module de besoin, avec le recours aux soins par âge sur des agrégats de population, ne change pas ce verdict tant qu'il reste populationnel.
- **Hors 2017/745 mais proche (règlement IA 2024/1689) :** l'assistant est un système d'IA en interaction avec des personnes. L'art. 50 demande d'informer l'utilisateur qu'il échange avec une IA. La carte dit déjà « aucun chiffre écrit par l'IA » dans le détail des calculs, mais aucune mention n'apparaît à l'ouverture de l'assistant. Il n'est pas « à haut risque » : il ne relève d'aucun domaine de l'annexe III, et l'accès aux services publics essentiels vise des décisions sur des personnes.

### 6. Hors RGPD, relevés au passage (mesuré)

- **Habillage DSFR.** `v2/prototype-carte/dsfr/LICENSE.md`, l. 1 : le DSFR « ne doit pas être utilisé par des entités extérieures à l'administration ». La carte affiche le bloc-marque « République française ». Sans porteur public réel, c'est l'identité visuelle de l'État utilisée par une équipe privée, sur un dépôt public. C'est aussi le risque le plus visible pour le jury.
- **Pas de licence du code** (pas de fichier `LICENSE`) : légalement, personne ne peut le réutiliser. `open.md` propose l'EUPL, sans décision de l'équipe.
- **Licences des données :** Insee, DREES, ameli, FINESS et Annuaire Santé sont sous Licence Ouverte Etalab 2.0 (supposé d'après les portails, à confirmer fichier par fichier). Les conditions de réutilisation de CartoSanté (Atlasanté) **n'ont pas été vérifiées**.

## How
- **Données :** les 34 fichiers traités commités (`data/processed/`, `v2/data/processed/`), au commit 8d8df4a. Pour chaque fichier, colonnes et part des cellules à n = 1 et n < 5 (script en ligne, pandas).
- **Code :** recherche des journaux, des écritures sur disque, des adresses d'écoute et des appels Anthropic dans `chatbot/`, `v2/agent/`, `v2/prototype*/`. `manifest.py --check`. Visibilité du dépôt avec `gh repo view`.
- **Droit :** RGPD (art. 5, 6, 9, 14, 28, 30, 32, 35, 89, chap. V) ; WP248 rév. 01 ; règlement 2017/745, art. 2.1 et considérant 19 ; MDCG 2019-11 ; règlement 2024/1689, art. 50. Cités de mémoire, sans relecture du texte intégral pendant l'audit.

## ⚑ What could make it wrong
- **Ce n'est pas un avis juridique.** Les qualifications (6.1.f, 14.5.b, non-dispositif médical) sont des lectures plausibles. Un DPO ou un juriste peut conclure autrement, surtout sur le critère « grande échelle ».
- Les textes sont cités de mémoire. Les numéros d'articles sont sûrs ; le libellé exact du MDCG 2019-11 (révision en vigueur) n'a pas été relu.
- La licence CartoSanté n'a pas été vérifiée. Si elle interdit la rediffusion, la publication des tables communales pose un problème de licence en plus du RGPD.
- La part de cellules à 1 compte les cellules non nulles de toutes les années. Sur une seule année, elle peut différer de quelques points.

## → What it changes
- **Faisabilité (jury, ×20) :** la recette jury estimait qu'une note de conformité rapporte environ 3 points pour 45 min. Ce rapport en est la matière première. Il reste à en tirer une page lisible dans le README.
- **`open.md` :** le « seuil de secret statistique » et l'« AIPD ou note de non-applicabilité » ont maintenant un verdict argumenté. La décision revient à l'équipe (voir le registre, section Open).
- **Pitch :** ne pas dire « avec le Ministère de la Santé » sans porteur réel, d'autant que la carte porte le bloc-marque de l'État.

## ? Next
| Item | Cost |
|---|---|
| Seuil de diffusion sur les tables communales publiées (cellules < 5 regroupées ou masquées, ou tables communales retirées du dépôt public et reconstruites localement) | ~30 min Claude |
| Page « Conformité » dans le README : finalité, base légale, art. 14, destination non clinique, mention IA, avertissement sur le texte libre | ~20 min Claude |
| Avertissement à l'ouverture de l'assistant : « réponses rédigées par une IA (Anthropic) ; ne saisissez pas de données personnelles » | ~10 min Claude |
| Décider le DSFR : porteur public réel, ou habillage neutre (direction A) hors .gouv.fr | 10 min équipe, puis ~30 min Claude |
| Choisir une licence de code (EUPL 1.2 proposée) | 10 min équipe |
| Vérifier les conditions de réutilisation de CartoSanté | ~15 min Claude |
| Relecture par un DPO ou un juriste | temps humain |
