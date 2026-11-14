# Vidéos de présentation — Offre libérale 2050

Deux compositions Remotion (1920×1080, 30 i/s) :
- `PitchV2`, la **V2** : `out/pitch-v2.mp4`, 60 s.
- `Pitch`, la **V1** : `out/pitch.mp4`, 57 s, conservée.

## V2 — un cas d'usage, 60 s, sans voix ni musique
« En tant que conseiller ministériel, je veux voir l'impact d'une hausse de 20 % des places en formation de kinés dans 10, 20 et 30 ans, au niveau national. » Le récit passe par des sous-titres minutés à la main.

| # | Temps | Scène | Ce qu'on voit |
|---|---|---|---|
| 1 | 0–5,5 s | Accroche | Cas d'usage, « +20 % de places pour former des kinés : quel effet dans 10 / 20 / 30 ans », carte tracée |
| 2 | 5,5–9 s | Promesse | Marque, 5 professions · 2026 → 2050 · données ouvertes |
| 3 | 9–20 s | 01 Régler un levier national | Glissement de « Places en formation » de +0 à +20 %, la carte se recolore. La caméra va sur la fiche France et y reste : +19 110 en 2050 (+11,9 %), fourchette 129 269 – 230 517 |
| 4 | 20–29 s | 02 Normandie, puis Manche | Clic, puis vrai vol de la carte (images MapLibre) ; Normandie +745 en 2050 |
| 5 | 29–50 s | 03 Lire l'effet à 10, 20 et 30 ans | Caméra fixe ; le curseur d'année passe à 2036, puis 2046, puis 2050. Un encart donne l'effectif, l'écart au tendanciel, la densité et la fourchette. En 2050, l'encart rappelle que 30 ans (2056) dépasse l'horizon du modèle |
| 6 | 50–56 s | Récapitulatif | Les trois horizons côte à côte, et le rappel France |
| 7 | 56–60 s | Clôture | Marque, accroche, sources |

Chiffres de la Manche (carte de décision, `/api/scenario`, kinés, `quotas=1.2`, au 2026-11-14) :

| Horizon | Effectif | Fourchette | Écart au tendanciel | Densité (tendanciel) |
|---|---|---|---|---|
| 2036 | 808 | 713 – 902 | +34 (+4,4 %) | 171 (164) |
| 2046 | 1 033 | 791 – 1 275 | +98 (+10,5 %) | 226 (205) |
| 2050 | 1 105 | 794 – 1 416 | +121 (+12,3 %) | 246 (219) |

Densité : pour 100 000 habitants (Insee Omphale, scénario central). Fourchette : environ 8 cas sur 10.

```bash
cd v2/video && npm install
# la carte doit tourner : uv run python v2/prototype-carte/server.py 8767
npm run capture:v2     # public/textures/v2/ + src/layout-v2.json (≈ 3 min)
npm run render:v2      # out/pitch-v2.mp4
```
- `src/PitchV2.tsx` : table `SHOTS_V2`, scènes, encart de lecture, sous-titres.
- `capture/capture-v2.mjs` :
  - états fixes en PNG 2x : levier `l0`…`l4`, `r28`, `d50` ;
  - séquences en JPEG 2x : vols `vol1/`, `vol2/` (48 images chacun, zoom autour d'un point fixe) et années `an/2036`…`an/2050` ;
  - les séquences (64 Mo) ne sont pas commitées : `npm run capture:v2` les régénère.
- Le navigateur est celui de Puppeteer, ou celui de la variable `CHROME`. Le rendu WebGL est logiciel (SwiftShader).

# V1

Vidéo motion de 57 s (1920×1080, 30 i/s) pour le jury, en Remotion, avec une voix off IA en français.

## Plan
| # | Temps | Scène | Ce qu'on voit |
|---|---|---|---|
| 1 | 0–6,5 s | Accroche | « En 2050, combien de kinés / infirmiers / sages-femmes… », carte des départements tracée puis colorée |
| 2 | 6,5–14,5 s | Promesse | Marque « Offre libérale 2050 », 5 professions · 2026 → 2050 · données ouvertes |
| 3 | 14,5–27 s | 01 Explorer le territoire | Captures France → Auvergne-Rhône-Alpes → Puy-de-Dôme ; fiche kinés 1 071 → 1 731, fourchette |
| 4 | 27–40,5 s | 02 Simuler une politique | Clic sur « Former 20 % de plus », volet avant/après, +19 110 en 2050, délai et statut du levier |
| 5 | 40,5–46,8 s | 03 Une phrase | Saisie de la phrase, « Ce que j'ai compris », confirmation |
| 6 | 46,8–56,8 s | Clôture | Données ouvertes · hypothèses sourcées · pas de boîte noire ; marque et accroche |

## Refaire la vidéo
```bash
cd v2/video
npm install
# 1. captures (la carte doit tourner : uv run python v2/prototype-carte/server.py 8767)
npm run capture
# 2. aperçu interactif
npm run dev
# 3. rendu
npm run render                                        # out/pitch.mp4 (avec musique)
npx remotion render src/index.ts Pitch out/pitch-sans-musique.mp4 --props=out/props-nobgm.json
```
Le fichier `out/props-nobgm.json` contient `{"bgm":false,"subtitles":true}`. Sous Windows, passez les props par fichier : la ligne de commande retire les guillemets du JSON.

## Fichiers
- `src/Pitch.tsx`
  - `SHOTS` : seule table de minutage, en secondes de voix (`v(sec)`).
  - Scènes et sous-titres, générés depuis `src/voix-words.json`.
- `src/parts.tsx` : briques visuelles.
  - Mots qui entrent depuis un flou, fente de mots qui défilent.
  - Carte tracée, caméra sur capture, cadres de mise en évidence, curseur.
- `src/tokens.ts` : tokens repris de la carte (IBM Plex, couleurs, courbes de mouvement).
- `capture/capture.mjs` : captures 2x et `src/layout.json`.
- `capture/france_paths.py` : contours simplifiés des départements depuis `app/assets/` (IGN/Etalab).
- `src/lib/` : composants copiés de video-shotcraft (licence Apache-2.0).

## Sources des médias
- Voix : ElevenLabs, voix « Perle | Premium French Corporate Voice », modèle eleven_v4. Le texte est dans la décision du 2026-11-14 (`v2/docs/lab/decisions.md`).
- Musique : « House Vibez » (Lily J), Mixkit Stock Music Free License, sans attribution.
- Chiffres : ceux affichés par la carte de décision au 2026-11-14.
  - Kinés, Puy-de-Dôme : 1 071 en 2026, 1 731 en 2050 (fourchette 1 244 – 2 219).
  - Préréglage « Former 20 % de plus » : +19 110 en France en 2050.
- Licence Remotion : gratuite pour les particuliers et les petites équipes.
