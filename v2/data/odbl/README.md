# Données sous ODbL 1.0

`besoin/` contient des bases dérivées des jeux de la CNAM sur data.ameli.fr :
- démographie ;
- patientèle ;
- honoraires détaillés ;
- pathologies (effectifs et dépenses).

Source : © Caisse nationale de l'Assurance Maladie, data.ameli.fr, Open Database License 1.0.

Ces fichiers sont mis à disposition sous **ODbL 1.0** (https://opendatacommons.org/licenses/odbl/1-0/) : attribution,
partage à l'identique et maintien de l'ouverture. Ils sont reconstruits par `uv run python v2/besoin/donnees/ameli.py`.
Les millésimes et les contrôles de chaque table sont dans les fichiers `.meta.json` voisins et dans
`v2/besoin/donnees/MANIFEST.md`.

Les cartes, figures et réponses ponctuelles qui en sont tirées sont des « œuvres produites » au sens de l'ODbL. Elles
portent la mention : « Contient des données de data.ameli.fr (CNAM), sous ODbL ».

`osm/` (dérivés d'OpenStreetMap, © les contributeurs d'OpenStreetMap, ODbL 1.0) n'est pas versionné à cause de sa
taille : on le reconstruit par `v2/besoin/donnees/distancier_osrm.py`.
