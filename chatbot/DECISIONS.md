# Décisions

## 2026-11-14 — Dépôt séparé ; le modèle en sous-module épinglé
**Décision.** Le chatbot vit dans son propre dépôt. Le modèle (`progdinh/hackathon_acces_soins`) y est un sous-module git
épinglé sur `426422c`, jamais modifié ici. **Pourquoi.** Demande de l'utilisateur·rice : « un autre dépôt, pas sur
celui-ci ». Le sous-module fixe la version exacte interrogée et rend toute modification visible (`git status`).

## 2026-11-14 — Deux processus : une passerelle en lecture seule, un chatbot qui n'importe pas le modèle
**Décision.** Seule `passerelle/` charge le modèle et n'expose que 8 requêtes GET en liste blanche, aux arguments validés
par schéma. Le chatbot et le modèle de langage n'y accèdent qu'en HTTP ; aucun outil d'écriture, de fichier ou de commande.
**Pourquoi.** « Le LLM doit avoir accès au modèle pour l'interroger, mais pas pouvoir modifier le code du modèle. » Une
consigne de prompt ne suffit pas : la garantie vient de l'absence de capacité, vérifiée par des tests.
**Résidu.** Verrou système (lecture seule, non-root) fourni par `scripts/lancer.sh`, non vérifié en développement.

## 2026-11-14 — Périmètre servi par le modèle, et vérification mécanique des nombres
**Décision.** Requête `perimetre` (couvert / hors périmètre / non modélisé, avec raisons) intégrée au prompt ; marqueurs
« Hors du périmètre du modèle » et « Limite du modèle : » ; tout nombre de réponse non rattaché à un résultat déclenche une
correction puis un blocage. **Pourquoi.** « S'il ne peut pas répondre, il ne doit pas halluciner. »
**Ce qui le renverserait.** Un taux de faux blocages élevé sur des réponses correctes (tolérance de 6 % à revoir), mesuré
par `eval/evaluer_perimetre.py`.

## Ouvert
- Mesurer le mode IA : `eval/evaluer_analyse.py` (60 appels) et `eval/evaluer_perimetre.py` (27 conversations).
- Faire écrire un jeu de périmètre à l'aveugle par quelqu'un d'autre (le jeu actuel est en échantillon).
- Fournisseur du modèle de langage : Claude ici ; la question Mistral reste ouverte côté équipe.
