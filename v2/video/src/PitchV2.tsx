// Vidéo V2 « Offre libérale 2050 » — un cas d'usage, 60 s, 1920x1080, 30 i/s, sans voix ni musique.
// Conseiller ministériel : +20 % de places en formation de kinés (national), effet lu dans la Manche à 10, 20 et 30 ans.
// Règle de mouvement : un mouvement de caméra par idée ; les horizons défilent par le curseur d'année, caméra fixe.
import React from 'react';
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from 'remotion';
import { C, SANS, MONO, EASE_IO } from './tokens';
import { BlurLine, BlurWord, SlotWord, FranceMap, Wordmark, Chip, Shot, Focus, Cursor, DigitRoll, ramp } from './parts';
import type { Cam } from './parts';
import LAYOUT from './layout-v2.json';

// Table des scènes, en images : seule source de vérité du minutage.
export const SHOTS_V2 = {
  hook: { from: 0, to: 160 },
  promise: { from: 160, to: 240 },
  lever: { from: 240, to: 540 },
  zoom: { from: 540, to: 795 },
  horizons: { from: 795, to: 1530 },
  recap: { from: 1530, to: 1695 },
  outro: { from: 1695, to: 1800 },
};
export const TOTAL_V2 = SHOTS_V2.outro.to;
const XF = 12; // fondu enchaîné entre scènes
const clampE = (ease = EASE_IO) => ({ extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease }) as const;

// delay : la scène reste invisible jusque-là (passage par le fond, sans superposer deux échelles de caméra)
const Fade: React.FC<{ dur: number; children: React.ReactNode; inF?: number; outF?: number; delay?: number }> = ({ dur, children, inF = XF, outF = XF, delay = 0 }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [delay, delay + Math.max(inF, 0.5), dur - outF, dur], [inF ? 0 : 1, 1, 1, outF ? 0 : 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

const Kicker: React.FC<{ at: number; out: number; n: string; text: string; top?: number }> = ({ at, out, n, text, top = 44 }) => {
  const f = useCurrentFrame();
  const t = ramp(f, at, at + 18) * (1 - ramp(f, out - 10, out));
  return (
    <div style={{ position: 'absolute', left: 48, top, opacity: t, transform: `translateX(${(1 - t) * -30}px)`, display: 'flex', alignItems: 'center', gap: 16, background: C.ink, color: '#fff', padding: '14px 24px', borderRadius: 12, fontFamily: SANS, fontSize: 30, fontWeight: 500, boxShadow: '0 12px 34px rgba(22,24,26,.25)' }}>
      <span style={{ fontFamily: MONO, fontSize: 24, opacity: 0.6 }}>{n}</span>{text}
    </div>
  );
};

/** Deux captures fondues l'une dans l'autre sous une même caméra, plus un calque d'annotations. */
const Blend: React.FC<{ a: string; b: string; t: number; keys: Cam[]; children?: React.ReactNode }> = ({ a, b, t, keys, children }) => (
  <>
    <Shot src={a} keys={keys} />
    {t > 0 && b !== a && <Shot src={b} keys={keys} opacity={t} />}
    <Shot src="" keys={keys}>{children}</Shot>
  </>
);

// Chiffres affichés par la carte (/api/scenario, kinés, quotas=1.2, national) le 2026-11-14.
// Densité : pour 100 000 habitants, Insee Omphale scénario central. Fourchette : ≈ 8 cas sur 10.
const H = [
  { y: 2036, dans: 'dans 10 ans', n: '808', lo: '713', hi: '902', ec: '+34', ecp: '+4,4 %', mot: 'légère hausse', d: '171', db: '164', inc: 'incertitude modérée' },
  { y: 2046, dans: 'dans 20 ans', n: '1 033', lo: '791', hi: '1 275', ec: '+98', ecp: '+10,5 %', mot: 'hausse marquée', d: '226', db: '205', inc: 'incertitude élevée · extrapolée' },
  { y: 2050, dans: 'au plus loin : dans 24 ans', n: '1 105', lo: '794', hi: '1 416', ec: '+121', ecp: '+12,3 %', mot: 'hausse marquée', d: '246', db: '219', inc: 'incertitude élevée · extrapolée' },
];

// ---------- 1. Accroche : la question du conseiller ----------
const Hook: React.FC = () => (
  <AbsoluteFill style={{ background: C.ground }}>
    <div style={{ position: 'absolute', right: 70, top: 40 }}>
      <FranceMap size={1000} drawAt={0} fillAt={96} />
    </div>
    <div style={{ position: 'absolute', left: 130, top: 250, fontFamily: SANS, color: C.ink }}>
      <BlurWord at={4} dy={14}>
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 12, fontSize: 30, color: C.mute, border: `1px solid ${C.line}`, background: C.panel, borderRadius: 10, padding: '10px 18px' }}>
          <span style={{ fontFamily: MONO, fontSize: 22, color: C.sel }}>Cas d'usage</span>conseiller ministériel
        </span>
      </BlurWord>
      <div style={{ fontSize: 88, lineHeight: 1.14, letterSpacing: '-0.025em', fontWeight: 500, marginTop: 40 }}>
        <BlurLine at={18} text="+20 % de places" stagger={5} wordStyle={(w) => (w === '+20' || w === '%' ? { fontFamily: MONO, color: C.kine } : undefined)} />
        <BlurLine at={34} text="pour former des kinés :" stagger={4} />
        <div style={{ display: 'flex', gap: 22 }}>
          <BlurWord at={56}>quel effet dans</BlurWord>
          <SlotWord fontSize={88} items={[
            { w: '10 ans', at: 66, color: C.sel },
            { w: '20 ans', at: 90, color: C.sel },
            { w: '30 ans', at: 114, color: C.sel },
          ]} />
        </div>
      </div>
    </div>
  </AbsoluteFill>
);

// ---------- 2. Promesse ----------
const Promise: React.FC = () => (
  <AbsoluteFill style={{ background: C.ground, alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ position: 'absolute', right: 70, top: 40, opacity: 0.16 }}>
      <FranceMap size={1000} drawAt={-200} fillAt={-200} />
    </div>
    <div style={{ transform: 'translateY(-110px)' }}><Wordmark size={104} at={4} /></div>
    <div style={{ position: 'absolute', top: 600, display: 'flex', gap: 36 }}>
      <Chip at={20} v="5" k="professions de santé" />
      <Chip at={26} v="2026 → 2050" k="projection annuelle" />
      <Chip at={32} v="100 %" k="données ouvertes" />
    </div>
  </AbsoluteFill>
);

// ---------- 3. Levier : « Places en formation » de 1,00 à 1,20, puis la caméra va sur l'effet et y reste ----------
const QX = (v: number) => { const b = LAYOUT.l0.quotas; return b.x + 8 + ((v - 0.7) / 0.8) * (b.w - 16); };
const QY = LAYOUT.l0.quotas.y + LAYOUT.l0.quotas.h / 2;
const Lever: React.FC = () => {
  const f = useCurrentFrame();
  const enter = ramp(f, 0, 26);
  const press = 62, drag = [68, 110] as const;
  const v = 1 + 0.2 * interpolate(f, drag, [0, 1], clampE());
  const pos = (v - 1) / 0.05, a = Math.floor(pos), b = Math.min(4, a + 1); // états capturés encadrants, fondus
  const keys = [
    { f: 0, cx: 960, cy: 540, z: 1 }, { f: 24, cx: 960, cy: 540, z: 1 }, { f: 58, cx: 700, cy: 420, z: 1.3 },
    { f: 135, cx: 700, cy: 420, z: 1.3 }, { f: 185, cx: 1440, cy: 300, z: 2 },
  ];
  const kp = LAYOUT.l4.kpis;
  return (
    <AbsoluteFill style={{ background: C.ground }}>
      <AbsoluteFill style={{ transform: `scale(${0.86 + 0.14 * enter}) translateY(${(1 - enter) * 60}px)`, borderRadius: 18 * (1 - enter), overflow: 'hidden', boxShadow: `0 30px 80px rgba(22,24,26,${0.2 * (1 - enter)})` }}>
        <Blend a={`v2/l${a}`} b={`v2/l${b}`} t={pos - a} keys={keys}>
          <Focus at={26} out={130} x={12} y={130} w={392} h={56} />
          <Cursor from={[320, 380]} to={[QX(1), QY]} at={32} click={press} out={press + 2} />
          {f >= press && <DragHand x={QX(v)} y={QY} out={124} />}
          <Focus at={196} out={1e9} x={kp.x + kp.w * 0.68} y={kp.y} w={kp.w * 0.32} h={kp.h * 0.62} />
          <Focus at={220} out={1e9} x={kp.x + kp.w * 0.34} y={kp.y + kp.h * 0.18} w={kp.w * 0.3} h={kp.h * 0.82} color={C.kine} />
        </Blend>
      </AbsoluteFill>
      <Kicker at={8} out={300} n="01" text="Régler un levier national" />
    </AbsoluteFill>
  );
};

/** Curseur qui suit un glissement (après le clic), puis s'efface. Coordonnées page. */
const DragHand: React.FC<{ x: number; y: number; out: number }> = ({ x, y, out }) => {
  const f = useCurrentFrame();
  const vis = 1 - ramp(f, out, out + 10);
  return (
    <svg width={26} height={32} viewBox="0 0 26 32" style={{ position: 'absolute', left: x, top: y, opacity: vis, transform: 'scale(.88)', transformOrigin: '0 0', filter: 'drop-shadow(0 2px 3px rgba(0,0,0,.3))' }}>
      <path d="M2 2 L2 26 L8 20 L12 30 L17 28 L13 18 L22 18 Z" fill={C.ink} stroke="#fff" strokeWidth={2} strokeLinejoin="round" />
    </svg>
  );
};

// ---------- 4. Territoire : Normandie, puis Manche (vrais vols de la carte, caméra vidéo fixe) ----------
// La scène entre après un passage par le fond (delay XF) : ses temps commencent à 12.
const N_VOL = 48;
const vol = (f: number, a: number, b: number) => Math.round(interpolate(f, [a, b], [0, N_VOL - 1], clampE()));
const pad3 = (i: number) => String(i).padStart(3, '0');
const Zoom: React.FC = () => {
  const f = useCurrentFrame();
  const c1 = 56, v1 = [66, 132] as const, c2 = 170, v2 = [180, 228] as const;
  const fix = [{ f: 0, cx: 960, cy: 540, z: 1 }];
  let src = 'v2/l4';
  if (f >= c1 + 2) src = `v2/vol1/${pad3(vol(f, v1[0], v1[1]))}.jpg`;
  if (f >= v1[1] + 2) src = 'v2/r28';
  if (f >= c2 + 2) src = `v2/vol2/${pad3(vol(f, v2[0], v2[1]))}.jpg`;
  if (f >= v2[1] + 2) src = 'v2/d50';
  // au clic, la sélection apparaît en fondu (6 images) au lieu d'une coupe
  const [base, t] = f < c2 + 2 ? ['v2/l4', ramp(f, c1 + 2, c1 + 8)] : ['v2/r28', ramp(f, c2 + 2, c2 + 8)];
  const k1 = LAYOUT.vol1.clic, k2 = LAYOUT.vol2.clic;
  return (
    <AbsoluteFill style={{ background: C.ground }}>
      <Blend a={base} b={src} t={t} keys={fix}>
        <Cursor from={[1000, 620]} to={[k1.x, k1.y]} at={26} click={c1} out={c1 + 16} />
        <Cursor from={[k1.x + 120, k1.y + 200]} to={[k2.x, k2.y]} at={142} click={c2} out={c2 + 16} />
        <Focus at={138} out={166} x={LAYOUT.r28.kpis.x} y={LAYOUT.r28.kpis.y} w={LAYOUT.r28.kpis.w} h={LAYOUT.r28.kpis.h} />
      </Blend>
      <Kicker at={20} out={255} n="02" text="Ouvrir la Normandie, puis la Manche" />
    </AbsoluteFill>
  );
};

// ---------- 5. Horizons : caméra fixe, le curseur d'année défile ----------
const YX = (y: number) => { const b = LAYOUT['an/2036'].yrange; return b.x + 8 + ((y - 2026) / 24) * (b.w - 16); };
const YY = LAYOUT['an/2036'].yrange.y + LAYOUT['an/2036'].yrange.h / 2;
const HZ = [
  { press: 58, drag: [64, 104] as const, from: 2050, to: 2036, show: 112 },
  { press: 292, drag: [298, 338] as const, from: 2036, to: 2046, show: 346 },
  { press: 500, drag: [506, 536] as const, from: 2046, to: 2050, show: 544 },
];
const yearAt = (f: number) => {
  let y = 2050;
  for (const h of HZ) if (f >= h.drag[0]) y = interpolate(f, h.drag, [h.from, h.to], clampE());
  return y;
};
const Horizons: React.FC = () => {
  const f = useCurrentFrame();
  const y = yearAt(f), a = Math.floor(y), b = Math.min(2050, a + 1);
  const keys = [{ f: 0, cx: 960, cy: 540, z: 1 }, { f: 10, cx: 960, cy: 540, z: 1 }, { f: 52, cx: 1350, cy: 320, z: 1.684 }];
  const idx = HZ.reduce((acc, h, i) => (f >= h.show ? i : acc), -1);
  const kp = LAYOUT['an/2036'].kpis;
  return (
    <AbsoluteFill style={{ background: C.ground }}>
      <Blend a={`v2/an/${a}.jpg`} b={`v2/an/${b}.jpg`} t={y - a} keys={keys}>
        <Cursor from={[1080, 160]} to={[YX(2050), YY]} at={30} click={HZ[0].press} out={HZ[0].press + 2} />
        {f >= HZ[0].press && <DragHand x={YX(y)} y={YY} out={HZ[2].drag[1] + 30} />}
        <Focus at={HZ[0].show} out={1e9} x={kp.x} y={kp.y} w={kp.w} h={kp.h} />
      </Blend>
      {idx >= 0 && <Reading idx={idx} />}
      <Kicker at={8} out={735} n="03" text="Lire l'effet à 10, 20 et 30 ans" top={118} />
    </AbsoluteFill>
  );
};

/** Valeur qui passe de l'ancienne à la nouvelle en fondu, sur place (pas de remise à zéro). */
const Swap: React.FC<{ a: React.ReactNode; b: React.ReactNode; t: number }> = ({ a, b, t }) => (
  <span style={{ display: 'inline-grid' }}>
    {t < 1 && <span style={{ gridArea: '1 / 1', opacity: 1 - t, transform: `translateY(${-t * 10}px)` }}>{a}</span>}
    <span style={{ gridArea: '1 / 1', opacity: t, transform: `translateY(${(1 - t) * 10}px)` }}>{b}</span>
  </span>
);

/** Encart de lecture d'un horizon : effectif, écart, densité, fourchette (jamais un chiffre seul).
 *  Il apparaît une fois ; ensuite seules les valeurs changent, et il s'estompe pendant que le curseur glisse. */
const Reading: React.FC<{ idx: number }> = ({ idx }) => {
  const f = useCurrentFrame();
  const h = H[idx], p = H[Math.max(0, idx - 1)];
  const at0 = HZ[0].show;
  const box = ramp(f, at0, at0 + 20);
  const tr = idx === 0 ? 1 : ramp(f, HZ[idx].show, HZ[idx].show + 14);
  const next = HZ[idx + 1];
  const dim = next ? ramp(f, next.press, next.press + 8) * (1 - ramp(f, next.show - 4, next.show + 6)) : 0;
  const t = (k: number) => ramp(f, at0 + k, at0 + k + 16); // entrée échelonnée des lignes, une seule fois
  const sw = (pick: (x: typeof h) => React.ReactNode) => <Swap a={pick(p)} b={pick(h)} t={tr} />;
  const row = (k: number, label: string, big: React.ReactNode, sub: React.ReactNode) => (
    <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', alignItems: 'baseline', padding: '10px 0', borderTop: `1px solid ${C.line}`, opacity: t(k), transform: `translateY(${(1 - t(k)) * 14}px)` }}>
      <div style={{ fontFamily: SANS, fontSize: 25, color: C.mute }}>{label}</div>
      <div>
        <div style={{ fontFamily: MONO, fontSize: 44, fontWeight: 500, color: C.ink }}>{big}</div>
        <div style={{ fontFamily: SANS, fontSize: 23, color: C.mute, marginTop: 2 }}>{sub}</div>
      </div>
    </div>
  );
  const gap = (x: React.ReactNode, y: React.ReactNode) => <span style={{ display: 'inline-flex', alignItems: 'baseline', gap: 12 }}>{x}{y}</span>;
  return (
    <div style={{ position: 'absolute', left: 56, top: 204, width: 820, opacity: box, transform: `translateY(${(1 - box) * 30}px)`, background: C.panel, borderRadius: 18, padding: '24px 36px 14px', boxShadow: '0 24px 70px rgba(22,24,26,.16)', border: `1px solid ${C.line}` }}>
      <div style={{ opacity: 1 - 0.6 * dim }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 20, marginBottom: 6 }}>
        <span style={{ fontFamily: MONO, fontSize: 72, fontWeight: 500, color: C.sel, lineHeight: 1 }}>
          {idx === 0 ? <DigitRoll value={String(h.y)} delay={at0 - 6} fontSize={72} color={C.sel} /> : sw((x) => x.y)}
        </span>
        <span style={{ fontFamily: SANS, fontSize: 32, color: C.ink, opacity: t(0) }}>{sw((x) => x.dans)}</span>
      </div>
      <div style={{ fontFamily: SANS, fontSize: 22, color: C.mute, marginBottom: 14 }}>Manche · kinés libéraux · +20 % de places en formation en France</div>
      {row(4, 'Effectif projeté', <span style={{ color: C.kine }}>{idx === 0 ? <DigitRoll value={h.n} delay={at0 + 4} fontSize={44} color={C.kine} /> : sw((x) => x.n)}</span>, 'kinés libéraux, scénario')}
      {row(10, 'Écart au tendanciel', sw((x) => gap(<span style={{ color: C.sel }}>{x.ec}</span>, <span style={{ fontSize: 28, color: C.mute }}>{x.ecp}</span>)), sw((x) => x.mot))}
      {row(16, 'Densité', sw((x) => gap(x.d, <span style={{ fontFamily: SANS, fontSize: 24, color: C.mute }}>pour 100 000 habitants</span>)), sw((x) => `tendanciel : ${x.db}`))}
      {row(22, 'Fourchette', sw((x) => <>{x.lo} – {x.hi}</>), sw((x) => `≈ 8 cas sur 10 · ${x.inc}`))}
      {idx === 2 && <div style={{ fontFamily: SANS, fontSize: 22, color: C.ink, background: C.ground, borderRadius: 10, padding: '10px 14px', marginTop: 6, opacity: ramp(f, HZ[2].show + 16, HZ[2].show + 32) }}>30 ans (2056) dépasse l'horizon du modèle : il s'arrête en 2050.</div>}
      </div>
    </div>
  );
};

// ---------- 6. Récapitulatif : trois horizons côte à côte ----------
const Recap: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ground, alignItems: 'center' }}>
      <div style={{ marginTop: 120, textAlign: 'center' }}>
        <BlurLine at={4} text="Manche · kinés libéraux · +20 % de places en formation" stagger={2} style={{ fontFamily: SANS, fontSize: 44, fontWeight: 500, color: C.ink, letterSpacing: '-0.015em' }} />
        <div style={{ fontFamily: SANS, fontSize: 26, color: C.mute, marginTop: 10, opacity: ramp(f, 14, 30) }}>Projection sous hypothèses · effectif, écart au tendanciel, densité et fourchette</div>
      </div>
      <div style={{ display: 'flex', gap: 34, marginTop: 70 }}>
        {H.map((h, i) => {
          const t = ramp(f, 22 + i * 10, 42 + i * 10);
          return (
            <div key={h.y} style={{ width: 470, opacity: t, transform: `translateY(${(1 - t) * 26}px)`, background: C.panel, border: `1px solid ${C.line}`, borderRadius: 16, padding: '26px 32px', boxShadow: '0 10px 30px rgba(22,24,26,.07)' }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 14 }}>
                <span style={{ fontFamily: MONO, fontSize: 52, color: C.sel, fontWeight: 500 }}>{h.y}</span>
                <span style={{ fontFamily: SANS, fontSize: 24, color: C.mute }}>{i === 2 ? 'dans 24 ans' : h.dans}</span>
              </div>
              <div style={{ fontFamily: MONO, fontSize: 60, color: C.kine, fontWeight: 500, marginTop: 10 }}>{h.n}</div>
              <div style={{ fontFamily: SANS, fontSize: 23, color: C.mute }}>fourchette {h.lo} – {h.hi}</div>
              <div style={{ height: 1, background: C.line, margin: '18px 0' }} />
              <div style={{ fontFamily: SANS, fontSize: 26, color: C.ink }}><b style={{ fontFamily: MONO, fontWeight: 500, color: C.sel }}>{h.ec}</b> <span style={{ color: C.mute }}>({h.ecp}) vs tendanciel</span></div>
              <div style={{ fontFamily: SANS, fontSize: 26, color: C.ink, marginTop: 8 }}><b style={{ fontFamily: MONO, fontWeight: 500 }}>{h.d}</b> <span style={{ color: C.mute }}>pour 100 000 hab. ({h.db})</span></div>
            </div>
          );
        })}
      </div>
      <div style={{ fontFamily: SANS, fontSize: 25, color: C.mute, marginTop: 44, opacity: ramp(f, 60, 80) }}>
        Rappel France, 2050 : <b style={{ fontFamily: MONO, fontWeight: 500, color: C.ink }}>+19{' '}110</b> kinés par rapport au tendanciel (+11,9 %), fourchette 129 269 – 230 517
      </div>
    </AbsoluteFill>
  );
};

// ---------- 7. Clôture ----------
const Outro: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.ground, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 34 }}>
        <Wordmark size={112} at={4} />
        <BlurLine at={22} text="Anticiper l'offre de soins, territoire par territoire." stagger={3} style={{ fontFamily: SANS, fontSize: 44, color: C.mute }} />
        <div style={{ fontFamily: MONO, fontSize: 21, color: C.faint, marginTop: 40, opacity: ramp(f, 40, 56) }}>
          DREES · Insee Omphale · CartoSanté · FINESS · Annuaire Santé — données ouvertes
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------- Sous-titres (minutés à la main : pas de voix off), en images du film ----------
const S = SHOTS_V2;
const LINES: { from: number; to: number; text: string }[] = [
  { from: S.promise.from + 10, to: S.promise.to - 4, text: 'Offre libérale 2050 projette l\'effectif libéral de cinq professions de santé.' },
  { from: S.lever.from + 12, to: S.lever.from + 110, text: 'Un seul levier : +20 % de places en formation de kinés, partout en France.' },
  { from: S.lever.from + 114, to: S.lever.from + 170, text: 'Premier effet en 2032 : le temps des études.' },
  { from: S.lever.from + 176, to: S.lever.to - 4, text: 'En France, en 2050 : +19 110 kinés par rapport au tendanciel, avec sa fourchette.' },
  { from: S.zoom.from + 70, to: S.zoom.from + 166, text: 'On ouvre la Normandie : +745 kinés en 2050, soit +12 %.' },
  { from: S.zoom.from + 172, to: S.zoom.to - 4, text: 'Puis la Manche, l\'un de ses cinq départements.' },
  { from: S.horizons.from + 12, to: S.horizons.from + HZ[0].show - 4, text: 'Dans la Manche, on déplace le curseur d\'année.' },
  { from: S.horizons.from + HZ[0].show, to: S.horizons.from + HZ[1].press, text: 'Dans 10 ans, en 2036 : +34 kinés, légère hausse par rapport au tendanciel.' },
  { from: S.horizons.from + HZ[1].show, to: S.horizons.from + HZ[2].press, text: 'Dans 20 ans, en 2046 : +98, hausse marquée ; la fourchette s\'élargit.' },
  { from: S.horizons.from + HZ[2].show, to: S.horizons.to - 6, text: '30 ans dépasse l\'horizon du modèle : on lit 2050, dans 24 ans.' },
  { from: S.recap.from + 84, to: S.recap.to - 6, text: 'Effectif, écart, densité, fourchette : jamais un chiffre seul.' },
];
const Subtitles: React.FC = () => {
  const f = useCurrentFrame();
  const l = LINES.find((x) => f >= x.from && f < x.to);
  if (!l) return null;
  const t = ramp(f, l.from, l.from + 5) * (1 - ramp(f, l.to - 5, l.to));
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, bottom: 54, display: 'flex', justifyContent: 'center', opacity: t }}>
      <div style={{ background: 'rgba(22,24,26,.82)', color: '#fff', fontFamily: SANS, fontSize: 34, fontWeight: 500, padding: '10px 22px', borderRadius: 10, maxWidth: 1400, textAlign: 'center' }}>{l.text}</div>
    </div>
  );
};

export const PitchV2: React.FC<{ subtitles: boolean }> = ({ subtitles }) => {
  const scenes: [keyof typeof SHOTS_V2, React.FC][] = [['hook', Hook], ['promise', Promise], ['lever', Lever], ['zoom', Zoom], ['horizons', Horizons], ['recap', Recap], ['outro', Outro]];
  return (
    <AbsoluteFill style={{ background: C.ground }}>
      {scenes.map(([k, Comp], i) => {
        const s = SHOTS_V2[k];
        const last = i === scenes.length - 1;
        const dur = s.to - s.from + (last ? 0 : XF);
        return (
          <Sequence key={k} from={s.from} durationInFrames={dur}>
            <Fade dur={dur} inF={i === 0 ? 0 : XF} outF={last ? 20 : XF} delay={k === 'zoom' ? XF : 0}><Comp /></Fade>
          </Sequence>
        );
      })}
      {subtitles && <Subtitles />}
    </AbsoluteFill>
  );
};
