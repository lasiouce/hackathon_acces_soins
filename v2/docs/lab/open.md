---
type: ledger
aliases: [Questions ouvertes v2]
---

# Questions ouvertes — v2

Les questions encore ouvertes du ledger v1 (`../../../docs/lab/open.md`)
restent valables : on les reprend ici au moment où on les traite.

| Question | Prix | Soulevée par | Date | Statut |
|---|---|---|---|---|
| Séparer public / privé dans « salarié hospitalier » et « autre salarié » (RPPS détaillé par secteur d'activité, SAE, BTS pour les infirmiers) ; sans ça, la sortie « libéral » des SF va de 12 475 à 26 428 | ~1 h, explore-and-report | recadrage « libéral » | 2026-11-14 || fait 2026-11-14 : SF 12 059 – 14 660, [rapport](reports/2026-11-14-axe4-secteur-public-prive.md) |
| Relancer le banc (K1 + filière) sur le nouveau périmètre « libéral » (privé) | ~20 min après la séparation public/privé | recadrage « libéral » | 2026-11-14 | open |
| Zonage conventionnel par commune × profession en géocodes (statut remplacement seul / obligation d'exercice), millésime actuel | ~30 min | recadrage granularité | 2026-11-14 || fait 2026-11-14 : `v2/data/processed/zonage_commune.parquet`, [rapport](reports/2026-11-14-axe4-zonage-commune.md) |
| Validation à 2050 : reproduire le tendanciel DREES n°76 (CD, SF, PH) avec leurs hypothèses, écart en % | ~2 h | horizon 2050 | 2026-11-14 | open |
| Injecter les diplômés du vivier (`formation`) dans N via filières → installation, à la place du flux ajusté ; comparer au banc | ~1 h (axe 2) | jumeau axe 0 | 2026-11-14 | open |
| Dynamique du secteur public dans le jumeau : aujourd'hui une cellule publique créée vide a s = 1, I = 0 (aucune sortie) ; il faut des taux une fois la séparation public/privé faite | ~30 min après l'axe 4 | jumeau axe 0 | 2026-11-14 | fermé 2026-11-14 : taux publics ajustés sur secteur_stock (axe 4) ; repli explicite sinon (décision « Corrections du contrat ») |
| État communal projetable : CartoSanté n'a ni sexe ni tranches quinquennales (< 40, 40–49, 50–54, 55–59, 60+) ; il faut un vieillissement à largeurs variables ou une ventilation dep → commune | ~45 min | jumeau axe 0 | 2026-11-14 | open |
| Plancher à 0 hérité de la v1 : il crée 0,02 à 0,43 % de N(2050) selon la profession (SF max), là où les entrées nettes ajustées sont négatives ; le traiter comme une sortie au lieu de tronquer ? | ~20 min | jumeau axe 0 | 2026-11-14 | open |
| Sensibilité de N(2050) à l'ordre des modules (permuter sorties/entrées/régulation) | ~15 min | jumeau axe 0 | 2026-11-14 | open |
| Recalcul à la taille commune pour 5 professions × 2 secteurs : 0,61 s mesuré pour 1 profession × 2 secteurs, ≈ 3,0 s extrapolé, au-dessus des 2 s supposés ; mesurer sur l'état communal réel, puis vectoriser si besoin | ~20 min | jumeau axe 0 | 2026-11-14 | open |
| Corriger les défauts bloquants 1–4 du jumeau et réécrire ses critères d'acceptation pour qu'ils puissent échouer | ~1–2 h | revue adversariale axe 0 | 2026-11-14 | open |
| Vérifier les 3 constats non réfutés (conservation identitaire, vieillissement 1/5 pour les tranches communales, état des modules entre runs) | ~10 min | revue adversariale axe 0 | 2026-11-14 | open |
| Axe 3 N3 : 2e test IDE pré-enregistré (borne Rambachan & Roth à M̄ fixé d'avance, ou contrôle synthétique) après l'échec de T1 (p = 0,043) | ~30 min Claude | axe 3 N3 | 2026-11-14 | open |
| Axe 3 N3 : pré-enregistrer θ (part contraignante du plafond) pour E2 kinés et le lancer ; premier module validé de bout en bout si l'IC contient 1 | ~15 min | axe 3 N3 | 2026-11-14 | open |
| Dater le zonage Atlasanté c987d0e2 (2012 ou révision 2014 ?) en le comparant à un arrêté ARS publié ; conditionne E1 et E2 | ~30 min | axe 3 N3 | 2026-11-14 | open |
| Textes primaires des dates d'effet : avenant 1 IDE (2009), avenant 3 IDE (arrêté 25/11/2011, zonage arrêté 21/12/2011), date du rezonage IDE post-avenant 6 (supposé 2020), absence de régulation dentaire avant 2025 (supposée) | ~30 min | axe 3 N3 | 2026-11-14 | open |
| Axe 3 N1 : lancer le banc pré-enregistré sur `jumeau_taux_locaux` (ancien périmètre) et écrire le premier dépôt de prévisions 2027–2030 | ~15 min Claude + ~1 min machine | axe 3 N1 | 2026-11-14 | open |
| Axe 3 N2 : lancer L1–L3 sur `TwinEstimator` ; construire le scénario `dd76_tendanciel` et lancer la partie A | ~1 h 15 Claude | axe 3 N2 | 2026-11-14 | open |
| Axe 3 N4 : lancer avec l'oracle départemental (erreur de répartition seule) | ~15 min Claude + ~1 min machine | axe 3 N4 | 2026-11-14 | open |
| Ventiler « autre secteur » des pharmaciens salariés (5 805 en 2026, part privée supposée 0,5) : sections de l'Ordre (B, C, D, G, H) vs secteurs DREES ; c'est l'essentiel de la fourchette « libéral » PH (60 005 – 67 219) | ~1 h | axe 4, secteur | 2026-11-14 | open |
| Parts privées FINESS en établissements, pas en salariés : pondérer par effectifs (SAE, BTS par catégorie juridique) pour les centres de santé (6 694 dentistes) et le médico-social (2 200 kinés) | ~1 h 30 | axe 4, secteur | 2026-11-14 | open |
| Écart DREES / Ordre sur la part privée des pharmaciens hospitaliers : 17 % (DREES, salariés ESPIC + lucratif) vs 28,6 % (Ordre, inscriptions section H) ; définir laquelle le jumeau suit | ~30 min | axe 4 × axe 1 | 2026-11-14 | open |
| Double compte infirmiers libéraux (SNDS) × salariés (BTS) dans la sortie privée 277 788 (2023) : mesurer le recouvrement | ~30 min | axe 4, secteur | 2026-11-14 | open |
| Brancher `v2/data/processed/secteur_stock.parquet` dans l'état du jumeau (secteur ∈ prive / public / ambigu), à la place du proxy libéral + mixte de `jumeau/check.py` | ~30 min | axe 4 → axe 0 | 2026-11-14 | open |
| Dater le zonage CartoSanté actuel par région (arrêtés ARS) : le service ne publie pas de millésime ; kinés : 2 826 géocodes « non prioritaires » (nouveau zonage) coexistent avec 10 « sur-dotés » (ancien) | ~1 h (17 ARS) | axe 4, zonage | 2026-11-14 | open |
| Zonages intermédiaires (générations 2018–2023) et 1re génération 2008–2011 : aucun jeu ouvert trouvé par commune ; sans eux, l'historique n'a que 2012 et « actuel » | ~1 h de recherche, issue incertaine | axe 4, zonage | 2026-11-14 | open |
| Axe 1 : ouvrir les arrêtés de méthodologie du zonage (IDE 10/01/2020 ; SF, MK, CD 2024) et le texte au JO de l'avenant 7 SF ; seuls les guides ARS les citent | ~30 min | axe 1 | 2026-11-14 | open |
| Axe 1 : l'avenant 11 IDE (signé le 31/03/2026) modifie-t-il la règle en zone sur-dotée ou celle des deux tiers ? | ~20 min | axe 1 | 2026-11-14 | open |
| Axe 1 : effet chiffré de la régulation SF, MK, CD (aucune publication) ; DiD par commune sur le zonage, protocole N3 | ~3 h par profession | axe 1 → axe 3 | 2026-11-14 | open |
| Axe 1 : destination des entrants bloqués ψ (commune voisine, remplacement, salariat, sortie) ; proxy : primo-installations dans les communes limitrophes des zones régulées, avant/après | ~4 h | axe 1 | 2026-11-14 | open |
| Axe 1 : taux de dérogation à la régulation SF, MK, IDE (QE AN 14558 et 14922 sans réponse) | ~30 min de veille | axe 1 | 2026-11-14 | open |
| Axe 1 : cessation par âge x_p(a) non publiée par la DREES ; la mesurer sur `stock.parquet` (taux apparent par cohorte au-dessus de 40 ans ; classe 65 ans et plus ouverte) | ~1 h | axe 1 → axe 0/2 | 2026-11-14 | open |
| Axe 1 : ε_PH récent (diplômés non inscrits à l'Ordre) : primo-inscrits de l'Ordre / inscrits en 6e année (fichier local) ; ouvrir aussi l'Ordre « Projections démographiques 2050 » | ~30 min | axe 1 | 2026-11-14 | open |
| Axe 1 : postes de DES odontologie par DES pour 2012-2017, 2019-2022 et 2025 (arrêtés CNG ; Légifrance bloque le téléchargement automatique) | ~20 min, humain | axe 1 | 2026-11-14 | open |
| Axe 1 : part de l'option « 2 ans en établissement » contre « 2 ans en zone sous-dotée » chez les nouveaux kinés (art. 4.1.1, premiers diplômés en 2027) | non mesurable avant 2028 | axe 1 | 2026-11-14 | open |
| Axe 1 : cumul emploi-retraite par caisse, millésime récent (CARCDSF, CAVP, CARPIMKO ; COR 2016 = données 2015) | ~30 min | axe 1 | 2026-11-14 | open |
| Levier retraite : la tranche ouverte 65+ reçoit un multiplicateur permanent, ce qui peut surestimer l'effet (bug relevé dans le dépôt Evolution-soin, même structure chez nous). Mesurer le séjour moyen en 65+ pour +1 et +3 ans | ~15 min | lecture dépôt Evolution-soin | 2026-11-14 | open |
| Mondes simulés (vérité connue) comme niveau de validation supplémentaire de l'axe 3 | ~1 h | lecture dépôt Evolution-soin | 2026-11-14 | open |
| DREES ER1319 (projections infirmières 2021–2050, ligne libéral, API) comme comparaison à 2050 | ~20 min | lecture dépôt Evolution-soin | 2026-11-14 | open |
| Registre d'événements : ouvrir le texte primaire (Légifrance) des 12 lignes à source secondaire de `v2/data/events.csv` | ~45 min | axe 4, événements | 2026-11-14 | open |
| Dates d'effet de l'avenant 7 kinés par ARS (la date du JO, 25/08/2023, n'est qu'une borne) ; même travail que la datation du zonage | ~1 h | axe 4, événements | 2026-11-14 | open |
| Bornes min / max des objectifs numerus apertus 2021–2025 et bilan ONDPS (site peps.sante.gouv.fr refusé) | ~30 min | axe 4, événements | 2026-11-14 | open |
| Cause de l'artefact Paris Cité dans les inscrits 2025-26 (683 en 2e année d'odontologie au lieu de ~190) ; corriger l'entrée du pipeline avant toute projection 2030+ | 15 min + attente DREES | axe 4, événements | 2026-11-14 | open |
| Écart CartoSanté (communes) vs RPPS (dép.) en 2025 : kinés −5,4 % (Marseille absente, −2 084 dans le 13), dentistes −2,8 % ; à corriger avant toute projection communale | ~30 min | revue axe 0 (C8) | 2026-11-14 | open |
| Nouvelle revue adversariale du jumeau après corrections (lève ou non « axes 2 et 5 attendent ») | ~3 min machine | corrections axe 0 | 2026-11-14 | open |
| Reprise observatoire → axe 0 : levier retraite (B1), convention de date (B2), pièges des entrées (B6), tests de propriétés (A6) | ~1,5 h | reprise observatoire | 2026-11-14 | open |
| Reprise observatoire → axe 3 : mondes simulés (A1), fourchette par pente (A3), robustesse du classement (A4), ER1319 (A7) | ~2 h | reprise observatoire | 2026-11-14 | open |
| Reprise observatoire → axe 4 : zonage data.gouv en contrôle croisé (C1), estimations de population 1975–2026 (C2), Omphale « Population âgée » (C3), cellules masquées (C6) | ~1 h | reprise observatoire | 2026-11-14 | open |
| Borne r ≤ 1,2 des 55+ (observatoire) : reproduit-elle l'emballement des entrées de K1 ? Tester sur un monde simulé | ~20 min | reprise observatoire | 2026-11-14 | open |
| Revue adversariale indépendante des corrections du jumeau (même workflow, 9 agents) | ~3 min machine | lancement axes 2 et 5 | 2026-11-14 | closed 2026-11-14 : 4 défauts bloquants (reports/2026-11-14-revue-adversariale-axe0-v2.md) |
| Choisir une direction artistique pour l'observatoire (A, B ou C) et la soumettre à son auteur | 10 min, temps humain | DA observatoire | 2026-11-14 | open |
| Axe 2 : inscrire puis passer au banc N1 la variante A2 + A1b (shrinkage hiérarchique + âges simples), proposée par défaut mais pas encore confirmatoire | ~5 min Claude + ~3 min machine | axe 2, banc N1 | 2026-11-14 | open |
| Axe 2 : dépôt de prévisions 2027–2030 pour A0 et A2 (seul test hors échantillon non contaminé par K1) | ~10 min | axe 2, banc N1 | 2026-11-14 | open |
| Axe 2 → N2 : A0 et B4 (r ≤ 1,2) divergent de +23 % pour les dentistes en 2050 ; trancher par la reproduction DD76 | ~30 min | axe 2, B4 | 2026-11-14 | open |
| Axe 2 : IC de Δ(A2 − A0) tenant compte de la corrélation entre origines (bootstrap par blocs dép × origine) ; la borne haute actuelle est −0,02 (privé) et −0,002 (ancien) | ~20 min | axe 2, banc N1 | 2026-11-14 | open |
| Axe 2 : banc N1 avec les variantes min / max de la part privée (axe 4) ; les SF privées sont à 13–14 % de MAPE | ~5 min machine | axe 2, banc N1 | 2026-11-14 | open |
| Contrat du jumeau (signalé par l'axe 2, non corrigé) : `Shift` n'accepte pas de fraction par cellule ; A1a passe par un `Add` à somme nulle | décision axe 0, ~20 min | axe 2 | 2026-11-14 | open |
| Contrat du jumeau (signalé par l'axe 2, non corrigé) : `stock_flow_rates` n'est pas injectable ; changer le calibrage oblige à remplacer `sorties` et `entrees` (leviers renommés `methodes_*`, mécanisme retraite recopié) | décision axe 0, ~30 min | axe 2 | 2026-11-14 | open |
| Axe 2 : A1a coûte +1,23 s par profession à la commune jusqu'en 2050 (mesuré) ; optimiser ou réserver A1b ; les tranches CartoSanté cassent l'hypothèse de largeur 5 de la tranche du bas | ~30 min | axe 2 | 2026-11-14 | open |
| Axe 2 : logit d'installation (A4) avec un attribut daté par département (population Insee 1975–2026, C2) | ~1 h | axe 2 | 2026-11-14 | open |
| Axe 2 : modèle bayésien / espace-état (A5) à la commune, sous le protocole N4 | ~2 h | axe 2 | 2026-11-14 | open |
| Axe 2 : série d'inscrits par université avant 2020, pour tester C5 en variation (pas seulement en niveau) | ~1 h de recherche de données | axe 2, C5 | 2026-11-14 | open |
| Axe 2 : diplômés étrangers par profession, avec une source primaire (série ouverte par lieu de diplôme) | ~1 h | axe 2, candidat 3 | 2026-11-14 | open |
| Seconde revue : corriger les défauts 1–4 du jumeau (retraite 65+, régulation non conservative, trajectory qui écrase le scénario de base, valeurs non validées) | ~1–2 h | seconde revue | 2026-11-14 | open |
| Prototype : borner les curseurs et masquer les chiffres retraite et régulation tant que les défauts restent ouverts | ~15 min | seconde revue | 2026-11-14 | closed 2026-11-14 : retraite et régulation suspendues (UI + serveur, 400), quotas bornés à [0,7 ; 1,5], profession validée |
| Axe 2 : réaligner `methodes_sorties.decalage_retraite` (copie du mécanisme `sorties`, biais 65+ relevé par la seconde revue du jumeau) après la correction de l'axe 0 | ~10 min | revue axe 0 v2 | 2026-11-14 | open |
| `fit_rates` (v1) suppose un vieillissement de 1/5 par an ; pour des tranches de largeurs variables (communes), un calibrage à fractions par tranche est à écrire | ~30 min | 2e revue axe 0 | 2026-11-14 | open |
| Troisième revue adversariale du jumeau (lève ou non « leviers retraite et régulation non citables ») | ~3 min machine | 2e corrections axe 0 | 2026-11-14 | open |
| Produit : relire en entier les 6 pages sources du rapport produit (chiffres lus en extrait seulement) | ~20 min Claude | rapport produit | 2026-11-14 | open |
| Produit : seuil de secret statistique sur les sorties communales (ex. n ≥ 11), condition de signature n° 5 et RGPD | ~30 min | rapport produit | 2026-11-14 | open |
| Produit : réconcilier IDE 2050 avec DREES ER1319 (821 000) et notre « libéral » avec le RPPS, condition n° 4 | ~1 h | rapport produit | 2026-11-14 | open |
| Produit : AIPD ou note de non-applicabilité RGPD à l'échelle communale | ~1 h rédaction + DPO, temps humain | rapport produit | 2026-11-14 | open |
| Produit : modèle économique « commun libre EUPL + prestation par ARS < 60 k€ HT » proposé, non décidé par l'équipe | 10 min, temps humain | rapport produit | 2026-11-14 | open |
| Produit : porteur institutionnel et ARS pilote (lettre d'intention, relecture DREES) | semaines, temps humain | rapport produit | 2026-11-14 | open |
| Infirmiers exclus du jumeau tant que la table public / privé (BTS) n'a ni âge ni sexe : ratisser secteur × âge × sexe par département (hypothèse secteur ⟂ âge·sexe, à tester sur le croisement national) | ~20 min | axe 4, prétirage | 2026-11-14 | open |
| Troisième revue → axe 0 : bornes contournables (empilement, NaN), rétention > 1 via un événement, aller-retour JSON, retraite avec plusieurs tranches 65+ (phase 2) | ~1 h | troisième revue | 2026-11-14 | open |
| Tester la règle « entrées ≤ sorties » de la régulation contre une référence indépendante (C2/C4 ne la testent pas) | ~30 min | troisième revue | 2026-11-14 | open |
| Flux d'installation et de cessation par commune (CartoSanté *_flux ou autre) : la donnée qui débloque le choix discret | ~1 h | état de l'art méthodes | 2026-11-14 | open |
| UAT : rejouer la V2 carte avec 1 persona à la fois dans un onglet isolé, captures sur disque | ~30–40 min | rapport UAT | 2026-11-14 | open |
| UAT : latence V2 perçue au premier plan, en rafale (critère < 100 ms ; seuil à définir pour un geste continu ou un changement isolé) | ~5 min + décision | rapport UAT | 2026-11-14 | open |
| UAT : sélecteur d'horizon (2035…) absent en V1 comme en V2, constat le plus grave | ~30 min | rapport UAT | 2026-11-14 | open |
| UAT : fiche exportable (V2 n'a qu'un CSV, sans sources ni hypothèses) | ~45 min | rapport UAT | 2026-11-14 | open |
| UAT : densité pour 100 000 habitants (population Insee/Omphale), avant ou après la démo ? | ~45–90 min + décision | rapport UAT | 2026-11-14 | open |
| UAT : délai d'effet affiché 2032 ou 2033 selon le testeur, pour le même scénario (V1), à expliquer | ~10 min | rapport UAT | 2026-11-14 | open |
| Retour utilisateur carte : zoom région puis département, cases plus grandes, limites ARS séparées, DROM en encarts, milieu de l'échelle de couleur (blanc) qui se confond avec le fond gris | transmis à proto-carte | retour direct | 2026-11-14 | open |
| Table de voisinage communale (commune régulée → commune voisine non régulée) pour la part « voisine » de `regulation.repartition` | ~30 min (axe 4) | défauts axe 1 | 2026-11-14 | open |
| MK : obligation d'exercer 2 ans en zone sous-dotée pour les diplômés à partir de 2027 ; demande de suivre l'ancienneté d'installation des cohortes dans l'état | ~1 h | fiche param-mk-regul-regle | 2026-11-14 | open |
| Part des dentistes spécialistes (ODF, CO, MBD) parmi les entrants, pour `regulation.part_exemptee` (Ordre, RPPS par spécialité) | ~20 min (axe 1) | fiche param-cd-regul-regle | 2026-11-14 | open |
| Axe 3 N6 : écrire `v2/validation/probabilistic.py` (CRPS sur log N, PIT, couverture) et lancer sur la variante par défaut et les naïfs (h = 5 : origine 2021, SF/CD/PH seulement) | ~40 min Claude + ~1 min machine | axe 3 N6 | 2026-11-14 | open |
| Axe 3 N6 : SBC des taux de rétention et des entrées sur 200 mondes N5 (après le générateur N5) | ~45 min Claude + ~5 min machine | axe 3 N6 | 2026-11-14 | open |
| Kinés quotas +20 % en 2050 : le jumeau donne maintenant +19 110 (+11,9 %), le rapport du prototype cite +8 645 (+5,4 %) mesuré avant les corrections ; mettre à jour ce rapport et expliquer l'écart (doublement de l'effet) | ~20 min | pitch animé | 2026-11-14 | open |
| Axe 2, étape 2 : cohortes par composantes bayésiennes, avec des entrées probabilistes (sans elles, la bande APC couvre 50 % au lieu de 80 %) | ~1 j | axe 2, étape 1 | 2026-11-14 | open |
| Axe 2 / axe 3 : référence naïve probabiliste (pente d'erreur par horizon) pour comparer les CRPS à armes égales (APC 6,82 % contre 8,68 % pour A0 ponctuel) | ~30 min | axe 2, étape 1 | 2026-11-14 | open |
| Axe 2 : propager l'incertitude des hyperparamètres θ de l'APC (Laplace sur log θ) et mesurer le gain de couverture | ~45 min | axe 2, étape 1 | 2026-11-14 | open |
| Axe 2 : calibration par simulation de l'APC sur 5 professions × 2 sexes, 200 jeux, θ ré-estimé (aujourd'hui : 1 plan, 40 jeux) | ~40 min machine | axe 2, étape 1 | 2026-11-14 | open |
| Archiver l'Annuaire Santé chaque mois (seule voie ouverte vers des flux d'installation individuels par commune, pour le logit de l'axe 2) | ~30 min + temps du monde | axe 4, grain communal | 2026-11-14 | open |
| Proxy du logit : installations nettes des moins de 40 ans par commune et année (CartoSanté, IDE / MK / CD, 2004–2025) | ~45 min | axe 4, grain communal | 2026-11-14 | open |
| Pharmacies par commune 2004–2025 (FINESS historique, 195 Mo, cat. 620) : ouvertures et fermetures d'officines | ~1 h | axe 4, grain communal | 2026-11-14 | open |
| Sages-femmes : aucune histoire communale ouverte (CartoSanté `sf_popage` illisible) ; signaler l'erreur de métadonnées à Atlasanté | 15 min + attente | axe 4, grain communal | 2026-11-14 | open |
| H_ind infirmiers non testable sur l'âge (BTS sans croisement secteur × âge) : chercher une source (SAE par âge ?) | ~45 min, issue incertaine | axe 4, grain communal | 2026-11-14 | open |
| Intégrer le flux « diplômés hors France » à la filière : 24,4 % des dentistes et 32,5 % des kinés actifs sans DE français (stock) ; il faut un flux annuel (Ordre, ONDPS) | ~1 h | axe 4 → axe 1 | 2026-11-14 | open |
| Retraite + 1 an : +3,02 % d'IDE libéraux en 2050 contre ≈ +1 % cité par la DREES (via l'axe 1) ; vérifier la source et la structure par âge des IDE (SNDS) | ~30 min | leviers axe 0 | 2026-11-14 | open |
| Vivier réel par profession (inscrits IFSI, MK, SF ; jeu DREES 491) à la place du vivier relatif stationnaire de `formation` | ~45 min (axe 4 + axe 0) | leviers axe 0 | 2026-11-14 | open |
| Âge d'entrée des diplômés à l'étranger (28 ans, DD76) au lieu de la répartition des entrées ajustées | ~20 min | leviers axe 0 | 2026-11-14 | open |
