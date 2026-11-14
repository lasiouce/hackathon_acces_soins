// Repérage : capture d'un état de la carte et liste des boutons.
// Usage : node capture/explore.mjs <dossier> [hash] [onglet]   ex. "p=kines&l=quotas:1.2&t=D50&y=2036" terr
import puppeteer from 'puppeteer';
import fs from 'fs';
const [OUT = 'out/explore', HASH = '', TAB = ''] = process.argv.slice(2);
fs.mkdirSync(OUT, {recursive: true});
const b = await puppeteer.launch({executablePath: process.env.CHROME || undefined, args: ['--hide-scrollbars', '--enable-unsafe-swiftshader']});
const p = await b.newPage();
await p.setViewport({width:1920,height:1080,deviceScaleFactor:1});
await p.goto((process.env.BASE || 'http://localhost:8767') + (HASH ? '/#' + HASH : ''), {waitUntil:'networkidle0'});
await new Promise(r=>setTimeout(r,3000));
if (TAB) { await p.click(`#tabs [data-tab="${TAB}"]`); await new Promise(r=>setTimeout(r,1500)); }
const name = (HASH || 'home').replace(/[^a-z0-9]+/gi, '_') + (TAB ? '-' + TAB : '');
await p.screenshot({path:`${OUT}/${name}.png`});
console.log(name, await p.evaluate(()=>[...document.querySelectorAll('button')].map(b=>b.id+':'+b.textContent.trim().slice(0,30)).join(' | ').slice(0, 600)));
await b.close();
