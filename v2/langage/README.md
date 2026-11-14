# v2/langage — compilateur de politiques en langage naturel

Pour un·e élu·e non technique : une phrase (« augmenter de 20 % le numerus apertus des kinés dans
le Puy-de-Dôme ») devient un réglage des 9 leviers du prototype (`v2/prototype/server.py`).

## Règle : traduire, jamais calculer
- **Aucun modèle de langage, aucune boîte noire.** Le compilateur est déterministe : glossaire
  relisible + règles explicites. Même texte, même sortie.
- Il produit des **réglages de leviers**, jamais un effectif. Les effectifs viennent du jumeau
  (`/api/scenario`), et `phrases.py` ne fait que les mettre en mots.
- Ce qui n'est pas dans le modèle est **dit** (`non_modelise`, avec la raison), pas approché.

## Architecture
```
texte ─► norm (accents, casse, tirets) ─► glossaire.yaml
        ├─ neutralisation du lexique  → reformulations
        ├─ politiques non modélisées → non_modelise (+ raison, source)
        ├─ profession (synonymes), territoire (régions, départements de geo(), villes)
        └─ propositions (, ; : et) → terme de levier + quantité (%, ans, ×, doubler, moitié…)
              → bornes LEVIERS_UI (bornage signalé) → parse_levers du serveur → leviers_valides
réponse /api/scenario ─► phrases.py → « En 2050, environ 1 930 kinés libéraux dans le Puy-de-Dôme… »
```
| Fichier | Rôle |
|---|---|
| `glossaire.yaml` | termes par levier, directions, unités, professions, villes, neutralisation, non modélisé (champ `source`, `null` si inconnu) |
| `compilateur.py` | `compile(texte, profession=None, territoire=None) -> dict` |
| `cas_test.yaml` | 36 politiques écrites **avant** le code, non ajustées ensuite |
| `evaluer.py` | taux de correspondance exacte et par champ, liste des échecs |
| `phrases.py` | gabarits de phrases ; fourchette = règle de `index.html` : scn × (1 ± k × horizon) |

Lancer (racine du dépôt) :
```
uv run python v2/langage/evaluer.py
uv run python v2/langage/compilateur.py "Doubler les PADHUE chez les dentistes en Bretagne"
uv run python v2/langage/phrases.py "Augmenter de 20 % les quotas de kinés dans le Puy-de-Dôme"
```

## Taux mesuré (2026-11-14)
`evaluer.py` : **35/36 (97 %)** en correspondance exacte (leviers + profession + territoire) ;
profession 36/36, territoire 36/36, non modélisé 36/36. Échec : #34, « augmenter les quotas des kinés
et des infirmiers de 10 % » (le « et » coupe la proposition, le +10 % n'est pas rattaché).

⚑ **Ce chiffre surestime la qualité réelle** : les cas et le glossaire ont été écrits par la même
personne, dans la même session ; c'est un taux *en échantillon*. Un essai hors échantillon de 8
phrases nouvelles a révélé 4 défauts génériques (décimale « 1,5 » coupée, « pas de régulation »
activait la régulation, « dans les » non reconnu, « plafonner » ignoré en silence), corrigés sans
toucher aux cas. Il faut un jeu de cas écrit par quelqu'un d'autre pour un chiffre honnête.
Second essai hors échantillon (branchement dans la carte, 2026-11-14) : « en régulant » non reconnu, « ne pas
réguler » / « supprimer la régulation » **activaient** la régulation, « maisons de santé » tombait en « pas compris ».
Corrigés (formes verbales, marqueurs de négation, entrée `exercice_coordonne`) ; cas de test inchangés, toujours 35/36.

## Taux hors échantillon (2026-11-14) — le chiffre à citer
`evaluer_hors_echantillon.py` sur `cas_test_hors_echantillon.yaml` (30 phrases écrites à l'aveugle par un agent qui n'a vu
ni le glossaire ni le compilateur) : **14/30 (47 %)** en correspondance exacte. Par champ : leviers 17/30, profession 28/30,
territoire 30/30, non modélisé 29/30. Par catégorie : simple 4/12, combinée 1/6, négation 4/4, non modélisé 2/4, piège 3/4.
Défauts dominants : tournures sans terme du glossaire (« un bon tiers », « diplômées à l'étranger », « l'âge de départ »,
« départs anticipés », « réduire le numerus apertus », « un an de travail en plus », « venir … étrangers »), demi-années
arrondies, deuxième levier d'une phrase combinée perdu, « dans la région seulement ». Le glossaire **n'a pas été ajusté** sur
ces cas : le jeu reste hors échantillon pour la prochaine version. Sortie complète : `score_hors_echantillon.txt`.

## Glossaire étendu, mesuré sur trois jeux à l'aveugle successifs (2026-11-14)
Chaque jeu est écrit par un agent qui n'a vu ni le glossaire, ni le compilateur, ni les jeux précédents. Il est **noté avant
toute modification** ; ses échecs servent ensuite à corriger des *classes* d'erreurs (jamais une phrase), et le jeu suivant mesure.

| Version | Jeu à l'aveugle (jamais vu) | Exact | Leviers | Profession | Territoire |
|---|---|---|---|---|---|
| glossaire d'origine | jeu 1 | 14/30 (47 %) | 17/30 | 28/30 | 30/30 |
| + synonymes, fractions, demi-années, quantité par type de levier | jeu 2 | 16/30 (53 %) | 20/30 | 28/30 | 28/30 |
| + sens le plus proche de la quantité, racines conjuguées, arrondi au pas, « emploi et retraite » | jeu 3 | **21/30 (70 %)** | 25/30 | 30/30 | 24/30 |

**Le chiffre à citer est 70 %** (jeu 3). Les jeux 1 et 2 sont désormais en échantillon (29/30 et 24/30 : non citables) ;
les cas d'origine restent à 35/36. Défauts restants (jeu 3) : gentilés de ville (« lyonnais », « marseillaises » :
6 territoires sur 9 échecs), « remplacer un confrère qui part » (régulation sans le mot), « % des territoires » pour la part
des zones, négation qui écarte un levier alors qu'un autre est demandé (« sans réguler…, un doublement des étrangers »),
« réservée à la région ». Un jeu 4 est nécessaire pour mesurer la version suivante. Sorties : `score_hors_echantillon*.txt`.

## Dans la carte
`v2/prototype-carte/server.py` expose `GET /api/interpret?q=…&prof=…&terr=…` (profession et territoire affichés
servent de défaut). La carte montre « Ce que j'ai compris / Pas encore dans le modèle / Pas compris / À noter » et
n'applique rien avant « Appliquer ce scénario » ; les leviers restent ensuite réglables à la main.

## Limites connues
- Une seule profession et un seul territoire par scénario (le premier cité, avec avertissement).
- Pas de grain commune ni de groupement : ville → département (liste courte de `villes`).
- Une quantité se rattache au levier de sa proposition ou, à défaut, au levier cité juste avant
  sans ampleur ; les phrases à coordination (« A et B de 10 % ») échouent.
- Pas de dates ni de calendrier (« d'ici 2030 ») : le serveur décide en 2026 ; l'année citée est ignorée.
- Pourcentage sans verbe de sens (« quotas à 20 % ») : signalé, non traduit. « Plafonner » : signalé.
- Négation gérée seulement pour les bascules (« pas de », « sans »).
- Dans `phrases.py`, l'article du département est « le / l' » (faux pour « la Creuse », « les Landes »).
- Termes génériques (« prime », « places », « régulation ») : risque de faux positifs.
- `compile` importe le serveur (charge le jumeau, quelques secondes au premier appel).
