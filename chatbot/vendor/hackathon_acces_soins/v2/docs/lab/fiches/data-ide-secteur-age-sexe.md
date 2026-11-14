---
parametre: N_IDE_secteur_age_sexe
profession: IDE
module: etat (secteur)
valeur: "2023 : privé 277 788, public 329 856 ; dép × secteur × 10 âges × sexe, 2013–2023"
unite: personnes
incertitude: "H_ind (secteur ⟂ âge·sexe dans un dép.) ; testée sur le sexe : écart médian de part de femmes privé − public 2,1 points (seuil 3, non rejetée) ; non testable sur l'âge"
source: "DREES/Insee BTS infirmières salariées 2013–2023 ; DREES SNDS libérales ; ratissage v1 sante/nurses.py ; Annuaire Santé (test)"
millesime: "publication DREES 2026-07-02 ; Annuaire 2026-11-13"
statut: dérivé
---

# Infirmiers : secteur × âge × sexe par département

Table `v2/data/processed/infirmiers_secteur_age_sexe.parquet`, script `v2/data/build_infirmiers.py`. Permet
aux infirmiers d'entrer dans l'état du jumeau. Rapport : [grain communal](../reports/2026-11-14-axe4-grain-communal.md).
