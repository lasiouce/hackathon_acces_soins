---
type: fiche
axe: 1
id: param-sf-regul-effet
parametre: "β_SF — effet de la régulation du conventionnement des sages-femmes en zone sur-dotée"
profession: sages-femmes
module: régulation
valeur: "non chiffré : « réduction des inégalités » 2016-2019 (direction seulement)"
unite: "—"
incertitude: "aucune ampleur publiée ; indicateur IGAS = rapport des densités départementales max/min, sans valeur citée ; la Cour des comptes note un écart d'APL « réduit » pour les SF sur 2016-2019"
source: "IGAS, rapport n° 2022-027R (Albertone, Gueydan, Flamant, Perruchon), Évaluation de la COG 2018-2022 de la CNAM, p. 67, § 200 et note 133 ; Cour des comptes, Organisation territoriale des soins de premier recours, mai 2024, p. 31 — https://www.vie-publique.fr/files/rapport/pdf/294141.pdf"
millesime: "2016-2019 (IGAS 2022) ; 2016-2019 (Cour des comptes 2024)"
statut: non mesurable
relecture: "2026-11-15 : corrigé (attribution)"
date: 2026-11-14
---

# β_SF — effet de la régulation des sages-femmes

**Mécanisme.** En zone sur-dotée, une sage-femme ne peut se conventionner
qu'après la cessation d'activité conventionnée d'une autre sage-femme dans
la même zone. Le flux d'entrées y est donc plafonné par les sorties (voir
[[param-sf-regul-regle]]).

**Ce qu'on sait.**
- **Direction.** Disparités en baisse pour les sages-femmes, comme pour les
  IDE, entre 2016 et 2019 (*cité*, IGAS). Ce n'est pas une estimation
  causale.
- **Ampleur.** Aucune ampleur publiée. Le bilan Cnam présenté en commission
  GDR (juin 2022), qui sert de source à l'IGAS et à la Cour, ne semble pas
  public.

**Comment le mesurer** (statut « non mesurable » tant que ce n'est pas fait).
- Différence de différences propre : densité de SF libérales par commune
  (CartoSanté, déjà dans `data/processed/stock_commune.parquet`), zones
  sur-dotées contre zones intermédiaires, avant/après la date d'effet.
- Cela demande le zonage SF par commune (axe 4).
- Coût estimé : ~3 h une fois le zonage disponible.

## Relecture en texte intégral (2026-11-15)

Verdict : **corrigé (attribution)** ([[2026-11-15-axe1-relecture-sources]]). Lecteur Haiku, puis vérificateur contradictoire.

- Direction seule confirmée : baisse des disparités 2016-2019 (IGAS p. 67, note 133 ; Cour p. 31). **Correction** : le bilan Cnam en commission GDR (23 juin 2022 selon la Cour, juillet 2022 selon l'IGAS) porte sur les aides à l'installation, pas sur la régulation. Il ne source pas la baisse SF, et la note 133 ne cite aucune source.
