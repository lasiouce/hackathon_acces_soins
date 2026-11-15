---
type: fiche
axe: 1
id: param-besoin-n-grossesse
parametre: "n_grossesse — nombre de contacts de suivi par grossesse (M3, voie « norme », sages-femmes)"
profession: [sages-femmes]
module: besoin (M3 : B₃(SF) = naissances × n_grossesse + femmes 15-49 × n_suivi)
valeur: "7 examens prénataux obligatoires (CSP R. 2122-1) + 1 entretien prénatal précoce + 1 entretien postnatal précoce + 1 examen postnatal (obligatoires) = 10 contacts réglementaires ; HAS 2016 recommande 8 consultations prénatales (soit 10 ou 11 selon que l'EPP double ou non la consultation précoce) ; séances de préparation à la naissance : 7 (ameli 2026) ou 8 (HAS 2016) ; 3 échographies"
unite: "contacts (examens, entretiens, séances) par grossesse menée à terme"
incertitude: "norme, pas recours : la part faite par les SF (et non par les médecins) n'est pas fixée par le texte ; préparation 7 ou 8 séances selon la source ; textes du CSP lus dans une reproduction (Doctrine), pas sur Légifrance ; n_suivi (gynécologie hors grossesse) non couvert par cette fiche"
source: "Code de la santé publique, art. R. 2122-1, R. 2122-2, R. 2122-3 (version du 27 mai 2003) et L. 2122-1 (version du 1er juillet 2022), lus sur doctrine.fr (reproduction ; Légifrance renvoie un défi anti-robot) ; HAS, « Suivi et orientation des femmes enceintes en fonction des situations à risque identifiées », mise à jour mai 2016, p. 13 imprimée (p. 15 du PDF), p. 17 et 21 ; ameli.fr, pages « préparation à la parentalité » (2 juin 2026) et « suivi et accompagnement de la femme enceinte » (16 sept. 2026)"
millesime: "CSP en vigueur au 2026-11-15 (selon la reproduction) ; HAS 2016 ; ameli 2026"
statut: sourcé
date: 2026-11-15
---

# n_grossesse — contacts de suivi par grossesse

**Rôle.** M3, voie (ii) « norme » (dérivation §6) : le besoin des SF lié à la grossesse vaut naissances × `n_grossesse`.
Une norme est indépendante de l'offre, ce qui évite la censure ; elle suppose que la norme est le besoin.

## Textes (cités)
| Contact | Nombre | Texte |
|---|---|---|
| Examens prénataux obligatoires | **7** | R. 2122-1 : « sont au nombre de sept pour une grossesse évoluant jusqu'à son terme » ; premier « avant la fin du troisième mois », puis « périodicité mensuelle à partir du premier jour du quatrième mois et jusqu'à l'accouchement » |
| Entretien prénatal précoce | **1**, obligatoire | L. 2122-1 : « L'entretien prénatal précoce obligatoire est réalisé par un médecin ou une sage-femme dès lors que la déclaration de grossesse a été effectuée. » |
| Entretien postnatal précoce | **1**, obligatoire (+ 1 facultatif) | L. 2122-1 : « Un entretien postnatal précoce obligatoire est réalisé par un médecin ou une sage-femme entre les quatrième et huitième semaines » ; « Un deuxième entretien peut être proposé, entre les dixième et quatorzième semaines » |
| Examen postnatal | **1**, obligatoire | R. 2122-3 : « Un examen médical postnatal doit être obligatoirement effectué dans les huit semaines qui suivent l'accouchement. » |

- L. 2122-1 : les examens sont pratiqués ou prescrits par un médecin ou une sage-femme ; leur nombre est fixé « par voie
  réglementaire ».
- Version de L. 2122-1 en vigueur depuis le 1er juillet 2022 (loi n° 2021-1754, art. 86). La date à laquelle
  l'entretien prénatal précoce est devenu obligatoire n'est pas établie : amendement n° 1963 adopté le 18 octobre 2019,
  version de L. 2122-1 en vigueur au 1er mai 2020 (relecture ; contenu de cette version non lu).

## Recommandations et prise en charge
- **HAS 2016** (p. 13 imprimée, p. 15 du PDF) : la réglementation « comporte 7 consultations » ; la HAS retient « un suivi en 8
  consultations au total », en ajoutant une consultation précoce avant 10 SA. **3 échographies** (11-13 SA + 6 j,
  20-25 SA, 30-35 SA ; p. 17 et 21). « 8 séances de préparation à la naissance et à la parentalité sont systématiquement
  proposées, la première étant consacrée à l'entretien individuel ou en couple » (p. 13 imprimée). La HAS range donc
  l'entretien dans les séances de préparation, pas dans les 8 consultations.
- **ameli 2026** : 7 séances de préparation prises en charge à 100 % ; 7 examens prénataux ; entretien prénatal
  précoce pris en charge à 100 % ; consultation postnatale à 6-8 semaines. Taux de prise en charge de l'entretien
  postnatal (70 % ou 100 %) : non tranché, vu seulement dans des résultats de recherche.
- **Écart 7 / 8 séances** : la HAS (2005, 2007, 2016) dit 8, la première étant l'entretien ; ameli dit 7 séances plus
  l'entretien prénatal précoce, compté à part. Lecture compatible : 1 entretien + 7 séances = 8 contacts. Non confirmé
  dans un texte.

## Valeur retenue (proposée)
| Variante | Contacts par grossesse | Composition | Étiquette |
|---|---|---|---|
| Réglementaire (défaut) | **10** | 7 examens + EPP + EPNP + examen postnatal | sourcé (CSP) |
| Recommandée | **10 ou 11** | 8 consultations HAS + EPNP + examen postnatal, + EPP s'il ne double pas la consultation précoce | sourcé (HAS 2016 + CSP) ; double compte non tranché *[corrigé après relecture : 11 seul]* |
| Avec préparation | **17** ou **18** | réglementaire ou recommandée + 7 séances (ameli) | sourcé, composition supposée |

**Part faite par les SF : non fixée.** Le texte dit « médecin ou sage-femme » ; la part des SF (contre les
gynécologues et les MG) relève du recours, pas de la norme. M3 doit la prendre dans DAMIR (`PSE_ACT_SNDS = 21`,
`PRS_NAT` 1911, 3404 « ENTRETIEN FEMME ENCEINTE ») et l'étiqueter « mesurée sous l'offre actuelle ».

Les échographies sont exclues par défaut, car la part faite par les SF n'est pas connue (choix supposé, à mesurer
dans DAMIR).
