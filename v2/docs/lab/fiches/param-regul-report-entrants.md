---
type: fiche
axe: 1
id: param-regul-report-entrants
parametre: "ψ_p,d — destination des entrants bloqués par la régulation (commune voisine, zone intermédiaire, remplacement, salariat, abandon)"
profession: [sages-femmes, dentistes, kines, infirmiers]
module: régulation
valeur: "non chiffré ; qualitatif : report vers les zones intermédiaires en bordure des zones sur-dotées, et contournement par le remplacement (IDE)"
unite: "parts des entrants bloqués par destination d (somme = 1)"
incertitude: "aucune source ne chiffre le nombre de refus de conventionnement ni la ventilation par destination"
source: "IRDES QES n° 270 (2022), p. 6 — https://www.irdes.fr/recherche/questions-d-economie-de-la-sante/270-inegalites-territoriales-de-repartition-des-infirmieres-liberales.pdf ; Cour des comptes, mai 2024, p. 95 — https://www.vie-publique.fr/files/rapport/pdf/294141.pdf"
millesime: "2022 ; 2024"
statut: non mesurable
date: 2026-11-14
---

# ψ — où vont les entrants bloqués

**Mécanisme.** Quand la règle « entrées ≤ sorties » mord dans une zone,
l'entrant bloqué a cinq destinations possibles :
1. une commune voisine non régulée (zone intermédiaire en bordure) ;
2. le remplacement, sans conventionnement en propre ;
3. le salariat privé, qui reste « libéral » au sens v2 ;
4. le salariat public, qui sort du « libéral » ;
5. un report d'entrée ou un abandon.

Sans ψ, le jumeau viole la conservation des effectifs ou suppose
implicitement une destination.

**Ce qu'on sait** (*cité*, qualitatif).
- Pour les IDE : report en limite des zones sur-denses, et contournement
  par le remplacement.
- Les signataires semblent avoir jugé le report réel : l'avenant 6 IDE
  encadre l'activité autour des zones sur-dotées (deux tiers de l'activité
  dans la zone d'installation, d'après le mémoire EHESP, note 55).

**Valeur par défaut proposée** (*supposée*, à tester par l'axe 5).
- ψ = 1 vers « commune voisine non régulée la plus proche ». C'est
  cohérent avec les observations qualitatives et avec la conservation des
  effectifs.
- Variantes de sensibilité : 50 % voisine / 50 % salariat (public et privé
  au prorata) ; 100 % sortie.

**Comment le mesurer.**
- Suivi individuel RPPS (identifiant + adresse d'exercice par millésime).
  Pour les IDE et MK libéraux sortant d'une installation refusée, le refus
  n'est pas observé. Proxy : primo-installations dans les communes
  limitrophes des zones sur-dotées, avant/après.
- Le RPPS individuel est-il ouvert ? Annuaire santé, extraction
  « personne / activité » : oui pour l'adresse, mais pas en historique. Il
  faut empiler des millésimes.
- Coût estimé : ~4 h.
