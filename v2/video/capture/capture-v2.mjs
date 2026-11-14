// Captures de la vidéo V2 (cas d'usage : kinés, +20 % de places en formation, national, lu dans la Manche).
// Prérequis : `uv run python v2/prototype-carte/server.py 8767` lancé.
// Sorties : public/textures/v2/ (états fixes en PNG 2x, séquences en JPEG 2x) + src/layout-v2.json (px CSS 1920x1080).
// Les vols de carte sont de vraies images MapLibre : la caméra de la carte zoome autour d'un point fixe, image par image.
import puppeteer from 'puppeteer';
import fs from 'fs';
const BASE = process.env.BASE || 'http://localhost:8767';
const OUT = 'public/textures/v2';
const N_VOL = 48;                       // images par vol de carte
const ANS = [2036, 2050];               // années capturées pour le curseur (toutes, de 2036 à 2050)
for (const d of ['', '/vol1', '/vol2', '/an']) fs.mkdirSync(OUT + d, {recursive: true});
const layout = {};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const b = await puppeteer.launch({executablePath: process.env.CHROME || undefined, args: ['--hide-scrollbars', '--enable-unsafe-swiftshader']});
const p = await b.newPage();
await p.setViewport({width: 1920, height: 1080, deviceScaleFactor: 2});
await p.goto(`${BASE}/#p=kines&v=ecart`, {waitUntil: 'networkidle0'});
await p.evaluate(() => document.fonts.ready);
await sleep(3000);
await p.click('#tabs [data-tab="terr"]');
await sleep(1200);

const idle = () => p.evaluate(() => new Promise((r) => { map.once('idle', r); map.triggerRepaint(); setTimeout(r, 4000); }));
const settle = async () => { await p.waitForNetworkIdle({idleTime: 400, timeout: 20000}).catch(() => {}); await idle(); await sleep(250); };
const box = (s) => p.evaluate((s) => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; }, s);
async function shot(name, boxes = {}, jpg = false) {
  await p.mouse.move(1919, 1079);
  await p.screenshot(jpg ? {path: `${OUT}/${name}.jpg`, type: 'jpeg', quality: 90} : {path: `${OUT}/${name}.png`});
  if (Object.keys(boxes).length) { layout[name] = {}; for (const [k, s] of Object.entries(boxes)) layout[name][k] = await box(s); }
  console.log('ok', name);
}
const UI = {quotas: '#lv-quotas', yrange: '#yrange', card: '#card', kpis: '#card .kpis', legend: '#legend', crumb: '#crumb'};

// L : le levier « Places en formation », de 1,00 à 1,20 par pas de 0,05 (France, écart au tendanciel, 2050)
await settle();
for (const [i, v] of ['1', '1.05', '1.1', '1.15', '1.2'].entries()) {
  if (i) { await p.evaluate((v) => { const e = document.querySelector('#lv-quotas'); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); }, v); await sleep(300); await settle(); await sleep(600); }
  await shot(`l${i}`, UI);
}

// Vol : zoom autour du point fixe qui amène la caméra A sur la caméra B (pas de dérive latérale)
async function vol(dir, id, maxZoom) {
  const pt = await p.evaluate((id) => { const [w, s, e, n] = bbox[id].flat(); const q = map.project([(w + e) / 2, (s + n) / 2]), o = map.getContainer().getBoundingClientRect(); return {x: o.x + q.x, y: o.y + q.y}; }, id);
  const A = await p.evaluate(() => ({c: map.getCenter().toArray(), z: map.getZoom()}));
  await p.evaluate((id) => select(id, false), id);
  await settle(); await sleep(800);
  const B = await p.evaluate((id, mz) => { const c = map.cameraForBounds(bbox[id], {padding: pad(), maxZoom: mz}); return {c: maplibregl.LngLat.convert(c.center).toArray(), z: c.zoom}; }, id, maxZoom);
  for (let i = 0; i < N_VOL; i++) {
    const t = i / (N_VOL - 1);
    await p.evaluate((A, B, t) => {
      const M = (c) => maplibregl.MercatorCoordinate.fromLngLat(c);
      const a = M(A.c), bb = M(B.c), rB = 2 ** (B.z - A.z), z = A.z + (B.z - A.z) * t, r = 2 ** (z - A.z);
      const P = {x: (bb.x - a.x / rB) / (1 - 1 / rB), y: (bb.y - a.y / rB) / (1 - 1 / rB)};
      const c = new maplibregl.MercatorCoordinate(P.x + (a.x - P.x) / r, P.y + (a.y - P.y) / r).toLngLat();
      map.jumpTo({center: c, zoom: z});
    }, A, B, t);
    await idle();
    await shot(`${dir}/${String(i).padStart(3, '0')}`, {}, true);
  }
  layout[dir] = {clic: pt, A, B};
}
await vol('vol1', 'R28', 8.5);
await shot('r28', UI);
await vol('vol2', 'D50', 10);
await shot('d50', UI);

// Curseur d'année, caméra fixe : un état par année, de 2036 à 2050
for (let y = ANS[0]; y <= ANS[1]; y++) {
  await p.evaluate((y) => setYear(y), y);
  await sleep(250); await idle(); await sleep(250);
  await shot(`an/${y}`, y === ANS[0] || y === ANS[1] ? UI : {}, true);
}
fs.writeFileSync('src/layout-v2.json', JSON.stringify(layout, null, 1));
await b.close();
