// Recette iso-fonctionnelle de la carte : chaque fonction de la page, vérifiée dans Chrome headless.
// Usage (serveur de la carte lancé) : node v2/prototype-carte/recette.mjs [url] [--option1] [--only=R30,O02] [--captures=dossier]
//   url par défaut http://localhost:8767/ (l'option 1 depuis la bascule du 2026-11-14) ; --option1 ajoute les contrôles
//   propres à cette mise en page (panneaux, défilement horizontal, cadrage France, chiffres nationaux) ;
//   --only ne lance que les contrôles listés ; --captures enregistre deux captures (1440×900 et 390×844, Puy-de-Dôme, places +20 %).
// Aucune dépendance : Chrome piloté par le protocole DevTools, WebSocket natif de Node ≥ 22.
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, existsSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const args = process.argv.slice(2);
const URL0 = args.find(a => !a.startsWith("--")) || "http://localhost:8767/";
const OPTION1 = args.includes("--option1");
const ONLY = args.find(a => a.startsWith("--only="))?.slice(7).split(",");
const CAPTURES = args.find(a => a.startsWith("--captures="))?.slice(11);
const CHROME = process.env.CHROME || ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"].find(existsSync);
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------- Chrome et protocole DevTools (WebGL logiciel SwiftShader : MapLibre en a besoin) ----------
const prof = mkdtempSync(join(tmpdir(), "recette-"));
const chrome = spawn(CHROME, ["--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-first-run", "--remote-debugging-port=0", `--user-data-dir=${prof}`, "about:blank"], { stdio: "ignore" });
let port;
for (let i = 0; i < 100 && !port; i++) { await sleep(100); try { port = readFileSync(join(prof, "DevToolsActivePort"), "utf8").split("\n")[0]; } catch {} }
if (!port) { console.error("Chrome n'a pas démarré"); process.exit(2); }
const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === "page");
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r, { once: true }));
let seq = 0; const waiting = new Map(), errors = [];
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m); waiting.delete(m.id); }
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") errors.push(m.params.args.map(a => a.value ?? a.description).join(" "));
});
const cdp = (method, params = {}) => new Promise(r => { const id = ++seq; waiting.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
async function ev(expr) {   // évalue dans la portée globale de la page (les let / const du script y sont visibles)
  const r = await cdp("Runtime.evaluate", { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true });
  if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description?.split("\n")[0] || "exception");
  return r.result?.result?.value;
}
const until = (cond, ms = 8000) => ev(`const t0=performance.now();while(!(${cond})){if(performance.now()-t0>${ms})throw new Error("délai dépassé : ${cond.replace(/"/g, "'")}");await new Promise(r=>setTimeout(r,50));}return true;`);
const idle = () => until("!inflight && carte", 10000).then(() => ev("await new Promise(r=>setTimeout(r,200));return 1"));
async function open(hash = "", w = 1440, h = 900) {
  await cdp("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: w < 700 });
  await cdp("Page.navigate", { url: "about:blank" });
  await cdp("Page.navigate", { url: URL0 + (hash ? "#" + hash : "") });
  try { await until("typeof META!=='undefined' && META && typeof carte!=='undefined' && carte && map && map.isStyleLoaded()", 30000); }
  catch (e) {   // diagnostic : ce qui manque au chargement
    console.error("chargement incomplet :", await ev(`return JSON.stringify({url:location.href,meta:typeof META!=='undefined'&&!!META,carte:typeof carte!=='undefined'&&!!carte,map:typeof map!=='undefined'&&!!map,maplibre:typeof maplibregl,style:typeof map!=='undefined'&&map?.isStyleLoaded?.()})`).catch(x => x.message), errors.slice(-5));
    throw e;
  }
  await idle();
  // téléchargements interceptés : le contenu du dernier fichier est lu dans window.__blob
  await ev(`URL.createObjectURL=b=>{window.__blob=b;return "blob:recette"};HTMLAnchorElement.prototype.click=function(){window.__dl=this.download};return 1`);
}
// adaptateurs : la seule différence de structure tolérée entre la page actuelle et la refonte
const A = {
  expert: `(document.querySelector('[data-tab="xp"]')||document.querySelector('#xbtn')).click();return 1`,
  // la conversation est ouverte au chargement (interface principale, 2026-11-14) : ne cliquer que si elle est fermée
  ask: `const q=document.querySelector('#askq');if(!(q&&q.offsetParent))(document.querySelector('[data-tab="ask"]')||document.querySelector('#askbtn')).click();return 1`,
  // comparaison et épingles : sous la fiche, dans l'onglet « Territoire et comparaison » (2026-11-14)
  pins: `const t=document.querySelector('[data-tab="cmp"]')||document.querySelector('[data-tab="terr"]');if(t)t.click();else{XT="cmp";renderExpert();}return 1`,
};

// ---------- contrôles ----------
const R = [];
async function check(id, name, fn) {
  if (ONLY && !ONLY.includes(id)) return;
  const e0 = errors.length;
  try { const v = await fn(); if (v === false) throw new Error("condition fausse"); if (errors.length > e0) throw new Error("erreur JS : " + errors.slice(e0).join(" | ")); R.push([id, "OK", name, typeof v === "string" ? v : ""]); }
  catch (e) { R.push([id, "ÉCHEC", name, String(e.message || e).slice(0, 160)]); }
}
const mapPoint = `const r=document.querySelector("#map").getBoundingClientRect(),p=map.project([2.6,46.8]);return [r.left+p.x,r.top+p.y]`;

await cdp("Runtime.enable"); await cdp("Page.enable");
await open();

await check("R01", "chargement : 5 professions, ≥ 96 départements colorés, aucune erreur", async () => {
  const n = await ev(`return [Object.keys(META.professions).length,Object.keys(carte.deps).length,map.getFeatureState({source:"d",id:"75"}).c||""]`);
  if (n[0] !== 5 || n[1] < 96 || !/^#/.test(n[2])) throw new Error(JSON.stringify(n)); return `${n[1]} départements`;
});
await check("R02", "carte : sources départements et limites régionales ; zoom +, −, France", () => ev(`return !!map.getSource("d")&&!!map.getSource("r")&&!!document.querySelector("#zin")&&!!document.querySelector("#zout")&&!!document.querySelector("#zfr")`));
await check("R03", "survol : infobulle avec nom et valeur 2050", async () => {
  const [x, y] = await ev(mapPoint);
  await cdp("Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
  await until(`getComputedStyle(document.querySelector("#tip")).opacity==="1"`, 3000);
  return ev(`const t=document.querySelector("#tip").textContent;if(!t.includes("2050"))throw new Error(t);return t`);
});
// vue par département (2026-11-14) : en vue France, un clic ouvre le département sous le curseur
await check("R04", "clic sur la carte en vue France : le département s'ouvre", async () => {
  const [x, y] = await ev(mapPoint);
  await cdp("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
  await cdp("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
  await until(`S.terr&&S.terr.startsWith("D")`, 4000); await idle(); return ev(`return S.terr`);
});
await check("R05", "retour à la France (bouton France entière)", async () => { await ev(`document.querySelector("#zfr").click();return 1`); await until("!S.terr"); await idle(); });
await check("R06", "profession : liste du scénario → couleur, données et lien changent", async () => {
  await ev(`const s=document.querySelector('#profsel');s.value="dentistes";s.dispatchEvent(new Event("change"));return 1`); await idle();
  const r = await ev(`return [S.prof,carte.prof,getComputedStyle(document.documentElement).getPropertyValue("--prof").trim().toLowerCase(),location.hash.includes("p=dentistes")]`);
  await ev(`const s=document.querySelector('#profsel');s.value="kines";s.dispatchEvent(new Event("change"));return 1`); await idle();
  if (r[0] !== "dentistes" || r[1] !== "dentistes" || !r[2] || !r[3]) throw new Error(JSON.stringify(r));
});
await check("R07", "trois indicateurs : évolution, écart au tendanciel, densité (légende suit)", async () => {
  const t = [];
  for (const v of ["ecart", "dens", "evo"]) { await ev(`document.querySelector('[data-v="${v}"]').click();return 1`); t.push(await ev(`return S.v+"|"+document.querySelector("#lt").textContent`)); }
  if (!t[0].startsWith("ecart|Effectif") || !t[1].startsWith("dens|Densité") || !t[2].startsWith("evo|Évolution")) throw new Error(t.join(" / "));
});
await check("R08", "recherche : « puy » → Puy-de-Dôme, Entrée ouvre la fiche", async () => {
  await ev(`const q=document.querySelector("#q");q.focus();q.value="puy";q.dispatchEvent(new Event("input"));return 1`);
  const t = await ev(`return document.querySelector("#results").textContent`); if (!t.includes("Puy-de-Dôme")) throw new Error(t);
  await ev(`document.querySelector("#q").dispatchEvent(new KeyboardEvent("keydown",{key:"Enter"}));return 1`);
  await until(`S.terr==="D63"`); await until(`document.querySelector("#card").textContent.includes("Puy-de-Dôme")`); await idle();
});
await check("R09", "fiche : effectifs, fourchette, trajectoire, repères, flux, zonage, actions", () => ev(`const c=document.querySelector("#card"),t=c.textContent;
  const k=[t.includes("Effectif 2050"),t.includes("fourchette"),c.querySelectorAll("#chart path").length>=4,t.includes("Repères"),t.includes("par flux"),t.includes("Département non régulé"),!!c.querySelector('[onclick="addCmp()"]'),!!c.querySelector('[onclick="exportCard()"]')];
  if(k.includes(false))throw new Error(JSON.stringify(k));return 1`));
await check("R10", "fil d'Ariane : France › Auvergne-Rhône-Alpes › Puy-de-Dôme, cliquable", async () => {
  const t = await ev(`return document.querySelector("#crumb").textContent`); if (!/France.*Auvergne-Rhône-Alpes.*Puy-de-Dôme/.test(t)) throw new Error(t);
  await ev(`document.querySelector('#crumb button[data-t="R84"]').click();return 1`); await until(`S.terr==="R84"`); await idle();
});
await check("R11", "Échap remonte d'un niveau ; « / » place le curseur dans la recherche", async () => {
  await ev(`select("D63");return 1`); await until(`S.terr==="D63"`); await idle();
  await ev(`document.activeElement.blur();dispatchEvent(new KeyboardEvent("keydown",{key:"Escape"}));return 1`); await until(`S.terr==="R84"`);
  await ev(`dispatchEvent(new KeyboardEvent("keydown",{key:"/"}));return 1`); return ev(`return document.activeElement.id==="q"`);
});
await check("R12", "précédent du navigateur : revient au territoire d'avant", async () => {
  await ev(`document.activeElement.blur();select("D63");return 1`); await until(`S.terr==="D63"`); await idle(); await ev(`history.back();return 1`); await until(`S.terr==="R84"`, 5000); await idle();
});
await check("R13", "curseur principal : places +20 % → écart positif et effet de la famille affiché", async () => {
  await ev(`select("D63");return 1`); await idle();
  await ev(`const e=document.querySelector("#lv-quotas");e.value="1.2";e.dispatchEvent(new Event("input"));return 1`); await idle();
  return ev(`if(!(S.lv.quotas===1.2&&SC.scn.at(-1)>SC.base.at(-1)&&/^\\+/.test(document.querySelector("#ef-former").textContent)))throw new Error(document.querySelector("#ef-former").textContent);return document.querySelector("#o-quotas").textContent`);
});
await check("R14", "recalcul perçu : p95 < 500 ms sur 6 réglages (monnaie : < 2 s)", async () => {
  for (const v of [1.1, 1.3, 1.0, 1.4, 0.9, 1.2]) { await ev(`tInput=performance.now();setL(LV("quotas"),${v});refresh();return 1`); await idle(); }
  const p = await ev(`const s=[...lat].sort((a,b)=>a-b);return Math.round(s[Math.floor(.95*(s.length-1))])`); if (!(p < 500)) throw new Error(p + " ms"); return `p95 ${p} ms`;
});
await check("R15", "préréglages et retour à la tendance", async () => {
  await ev(`document.querySelector('.preset[data-p="retenir"]').click();return 1`); await idle();
  const a = await ev(`return S.lv.retraite`); await ev(`document.querySelector("#reset").click();return 1`); await idle();
  if (a !== 2) throw new Error("retraite " + a); return ev(`return META.levers.every(isDef)`);
});
await check("R16", "réglages fins : la régulation active part des zones et destination ; quotas régionaux selon le territoire", async () => {
  const off = await ev(`return document.querySelector("#lv-part_zones").disabled`);
  await ev(`const e=document.querySelector("#lv-regul");e.checked=true;e.dispatchEvent(new Event("change"));return 1`); await idle();
  const on = await ev(`return !document.querySelector("#lv-part_zones").disabled&&!document.querySelector("#lv-quotas_region").disabled`);
  await ev(`document.querySelector("#reset").click();return 1`); await idle(); return off && on;
});
await check("R17", "hypothèses de contexte : population Insee (3 scénarios) et activité", () => ev(`return document.querySelectorAll("#lv-pop_scen option").length===3&&!!document.querySelector("#lv-activite")`));
await check("R18", "source d'un levier dépliable ; liste « Pas encore dans le modèle »", async () => {
  await ev(`document.querySelector('.src[data-k="quotas"]').click();return 1`);
  return ev(`return document.querySelector("#src-quotas").classList.contains("on")&&document.querySelector("#nonmod").textContent.includes("Pas encore dans le modèle")`);
});
await check("R19", "famille sans effet masquée et expliquée (pharmaciens : attirer)", async () => {
  await ev(`S.prof="pharmaciens";applyProf();refresh();return 1`); await idle();
  const r = await ev(`return document.querySelector("#q-attirer").style.display==="none"&&document.querySelector("#nonmod").textContent.includes("diplômés étrangers")`);
  await ev(`S.prof="kines";applyProf();refresh();return 1`); await idle(); return r;
});
await check("R20", "phrase → écran « Ce que j'ai compris » → appliquer", async () => {
  await ev(`await interpret("former 20 % de kinés en plus");return 1`);
  const t = await ev(`return document.querySelector("#nl").classList.contains("on")&&document.querySelector("#nl").textContent`);
  if (!t || !t.includes("Ce que j'ai compris")) throw new Error("écran absent");
  await ev(`document.querySelector("#nlok").click();return 1`); await idle();
  const q = await ev(`return S.lv.quotas`); await ev(`document.querySelector("#reset").click();return 1`); await idle(); return q > 1;
});
await check("R21", "comparer : territoire ajouté, agrégat affiché, retrait possible", async () => {
  await ev(`select("D63");return 1`); await idle(); await ev(`addCmp();return 1`);
  const t = await ev(`return S.cmp.includes("D63")&&document.querySelector("#cmp").textContent`);
  if (!t || !t.includes("Puy-de-Dôme")) throw new Error(String(t));
  await ev(`document.querySelector('#cmp [aria-label="Retirer"]').click();return 1`); return ev(`return S.cmp.length===0`);
});
await check("R22", "export CSV : définition, sources, millésimes, leviers, fourchette, données annuelles", async () => {
  await ev(`exportCard();return 1`); const t = await ev(`return await window.__blob.text()`);
  for (const k of ["Définition", "Sources", "Millésimes", "Leviers", "Fourchette", "Limites", "annee;tendanciel;scenario;bas;haut", "2050;"]) if (!t.includes(k)) throw new Error("manque " + k);
  return ev(`return window.__dl`);
});
await check("R23", "mode expert : flux par année, leviers bruts avec paramètre et source", async () => {
  await ev(A.expert); await until(`document.querySelector("#xbody").textContent.includes("Écart total")`);
  await ev(`document.querySelector('#xp [data-t="lev"]').click();return 1`);
  const r = await ev(`return document.querySelector("#xbody").textContent.includes("entrees.multiplicateur")`);
  await ev(`document.querySelector('#xp [data-t="flux"]').click();return 1`); return r;
});
await check("R24", "scénarios épinglés (3 au plus) et export JSON", async () => {
  await ev(A.pins); await until(`!!document.querySelector("#xpin")`);
  await ev(`document.querySelector("#xpin").click();document.querySelector("#xpin").click();return 1`);
  const n = await ev(`return PIN.length`); await ev(`document.querySelector("#xjson").click();return 1`);
  const j = JSON.parse(await ev(`return await window.__blob.text()`)); if (!(n === 2 && j.epingles.length === 2 && j.version_code)) throw new Error(`${n} épinglés`);
});
await check("R25", "A+ : texte agrandi, mémorisé dans le lien", async () => {
  await ev(`document.querySelector("#txt").click();return 1`); const r = await ev(`return document.documentElement.classList.contains("xl")&&location.hash.includes("z=1")`);
  await ev(`document.querySelector("#txt").click();return 1`); return r;
});
await check("R26", "lien du scénario : copie et message", async () => { await ev(`document.querySelector("#save").click();return 1`); await until(`document.querySelector("#toast").textContent.includes("Lien")`, 3000); });
await check("R27", "lien restauré : profession, leviers, indicateur, territoire, comparaison", async () => {
  await open("p=dentistes&l=quotas:1.3&v=ecart&t=D13&c=D13,R84");
  await until(`S.terr==="D13"`); await until(`document.querySelector("#card").textContent.includes("Bouches-du-Rhône")`);
  return ev(`return S.prof==="dentistes"&&S.lv.quotas===1.3&&S.v==="ecart"&&S.cmp.length===2`);
});
await check("R28", "lien invalide : valeurs remises par défaut avec message", async () => {
  await open("p=kines&l=quotas:9,zzz:1&t=D999"); await until(`document.querySelector("#toast").textContent.includes("valeurs ignorées")`, 4000);
  return ev(`return S.lv.quotas===1&&!S.terr`);
});
await check("R29", "lexique neutre : aucun mot de jugement dans la page", () => ev(`const t=document.body.innerText.toLowerCase();return !/désert|médiocre|catastroph|mauvais|alarmant/.test(t)`));
await check("R31", "curseur d'année : 2035 → carte, légende, fiche, résumé et lien suivent ; sans nouvel appel au serveur", async () => {
  await open("p=kines&l=quotas:1.2&t=D63"); await until(`S.terr==="D63"`); await idle();
  const n0 = await ev(`return performance.getEntriesByType("resource").filter(e=>e.name.includes("/api/carte")).length`);
  await ev(`const r=document.querySelector("#yrange");r.value="2035";r.dispatchEvent(new Event("input"));return 1`);
  await ev(`await new Promise(r=>setTimeout(r,400));return 1`);
  const k = await ev(`return [S.y===2035,location.hash.includes("y=2035"),document.querySelector("#lt").textContent.includes("2035"),document.querySelector("#card").textContent.includes("Effectif 2035"),
    document.querySelector("#scen").textContent.includes("2035"),map.getFeatureState({source:"d",id:"63"}).c!==undefined,performance.getEntriesByType("resource").filter(e=>e.name.includes("/api/carte")).length]`);
  if (k.slice(0, 6).includes(false) || k[6] !== n0) throw new Error(JSON.stringify(k) + " appels avant " + n0);
  await open("p=kines&y=2040"); const y = await ev(`return S.y+"|"+document.querySelector("#yv").textContent`); if (y !== "2040|2040") throw new Error("lien y=2040 : " + y);
  await ev(`const r=document.querySelector("#yrange");r.value="2050";r.dispatchEvent(new Event("input"));return 1`);
  return ev(`return !location.hash.includes("y=")`);
});
await check("R32", "panneau « Questions » (agent) : s'ouvre, dit s'il est disponible, sans erreur", async () => {
  await ev(A.ask); await until(`!!document.querySelector("#askq")&&document.querySelector("#askq").offsetParent!==null`, 4000);
  await ev(`await new Promise(r=>setTimeout(r,800));return 1`);
  return ev(`return document.querySelector("#askst").textContent.slice(0,80)`);
});
await check("R30","mobile 390 px : rien ne déborde à droite, sélecteur de profession, leviers accessibles", async () => {
  await open("", 390, 844);
  // chaque élément visible tient dans la largeur (un overflow-x: hidden masquerait le débordement au lieu de l'éviter)
  return ev(`const out=[...document.querySelectorAll("body *")].filter(e=>{if(e.closest(".maplibregl-map"))return false;const r=e.getBoundingClientRect(),s=getComputedStyle(e);
      return r.width>0&&r.height>0&&s.visibility!=="hidden"&&r.right>innerWidth+1;}).map(e=>e.id?"#"+e.id:e.tagName.toLowerCase()+(e.className&&typeof e.className=="string"?"."+e.className.split(" ")[0]:"")).slice(0,8);
    const fold=document.querySelector("#fold"),fr=fold&&fold.getBoundingClientRect();
    const k=[out.length===0,getComputedStyle(document.querySelector("#profsel")).display!=="none",!!fr&&fr.width>0&&fr.right<=innerWidth];
    if(k.includes(false))throw new Error(JSON.stringify(k)+" débordent : "+out.join(", "));return 1`);
});

if (OPTION1) {
  await open();
  await check("O01", "option 1 : les leviers restent ouverts à l'ouverture d'un territoire", async () => { await ev(`select("D63");return 1`); await idle(); return ev(`return !document.querySelector("#levers").classList.contains("closed")`); });
  await check("O02", "option 1 : deux panneaux dépliables (scénario, territoire)", async () => {
    const r = [];
    for (const [b, p] of [["#fold", "#levers"], ["#cardfold", "#side"]]) {
      await ev(`document.querySelector("${b}").click();return 1`); r.push(await ev(`return document.querySelector("${p}").classList.contains("closed")`));
      await ev(`document.querySelector("${b}").click();return 1`); r.push(!(await ev(`return document.querySelector("${p}").classList.contains("closed")`)));
    }
    if (r.includes(false)) throw new Error(JSON.stringify(r));
  });
  // liste classée retirée (décision du 2026-11-14) ; à la place : le panneau de droite ne défile jamais horizontalement
  await check("O03", "option 1 : panneau de droite sans défilement horizontal (Territoire et comparaison, Expert flux et leviers)", async () => {
    await ev(`select("D63");return 1`); await idle(); await ev(`addCmp();return 1`);
    const over = [];
    for (const [t, sub] of [["terr"], ["xp", "flux"], ["xp", "lev"]]) {
      await ev(`document.querySelector('[data-tab="${t}"]').click();${sub ? `document.querySelector('#xp nav [data-t="${sub}"]').click();` : ""}return 1`);
      await ev(`await new Promise(r=>setTimeout(r,150));return 1`);
      const o = await ev(`const p=[...document.querySelectorAll("#side .panel")].find(x=>!x.hidden);return p.scrollWidth-p.clientWidth`);
      if (o > 1) over.push(`${t}${sub ? "/" + sub : ""} +${o}px`);
    }
    await ev(`S.cmp=[];writeHash();renderCmp();return 1`);
    if (over.length) throw new Error(over.join(", ")); return ev(`return "panneau "+Math.round(document.querySelector("#side").getBoundingClientRect().width)+" px"`);
  });
  await check("O06", "option 1 : panneau de gauche sans défilement horizontal (réglages fins et sources dépliés)", async () => {
    await ev(`document.querySelector("#levmore").open=true;document.querySelectorAll("#levers details").forEach(d=>d.open=true);document.querySelectorAll("#levers .srcbox").forEach(s=>s.classList.add("on"));return 1`);
    const o = await ev(`const b=document.querySelector("#levers .body");return b.scrollWidth-b.clientWidth`);
    await ev(`document.querySelectorAll("#levers .srcbox").forEach(s=>s.classList.remove("on"));document.querySelector("#levmore").open=false;return 1`);
    if (o > 1) throw new Error(`+${o}px`); return ev(`return "panneau "+Math.round(document.querySelector("#levers").getBoundingClientRect().width)+" px"`);
  });
  await check("O07", "option 1 : à l'arrivée, la France est centrée dans la colonne de la carte", async () => {
    await open();
    const r = await ev(`const w=document.querySelector("#mapwrap").getBoundingClientRect(),[x0,y0,x1,y1]=bbox.FR,a=map.project([x0,y1]),b=map.project([x1,y0]);
      return {dx:Math.round((a.x+b.x)/2-w.width/2),inside:a.x>=-2&&a.y>=-2&&b.x<=w.width+2&&b.y<=w.height+2}`);
    if (!r.inside || Math.abs(r.dx) > 40) throw new Error(JSON.stringify(r)); return `décalage ${r.dx} px`;
  });
  await check("O08", "option 1 : chiffres nationaux — sans territoire la fiche montre la France ; bascule territoire ↔ France", async () => {
    const st = () => ev(`return JSON.stringify({h3:document.querySelector("#card h3")?.textContent,terr:S.terr,CS,tab:TAB})`);
    const step = async (name, cond) => { try { await until(cond); } catch { throw new Error(name + " " + await st()); } };
    await ev(`document.querySelector('[data-tab="terr"]').click();return 1`);
    await step("France sans territoire", `document.querySelector("#card h3")?.textContent==="France"`);
    await ev(`select("D63");return 1`); await idle(); await step("territoire ouvert", `document.querySelector("#card h3")?.textContent==="Puy-de-Dôme"`);
    await ev(`document.querySelector('#card [data-cs="fr"]').click();return 1`); await step("bascule France", `document.querySelector("#card h3")?.textContent==="France"&&F&&F.scn.at(-1)>50000`);
    // « France entière » : carte recadrée sur la France (zoom de vue nationale), rien de grisé, pas de repère de territoire
    await ev(`await new Promise(r=>setTimeout(r,1000));return 1`);
    const fr = await ev(`const c=map.getCenter(),grey=Object.keys(carte.deps).filter(id=>map.getFeatureState({source:"d",id}).dim).length;
      return {zoom:+map.getZoom().toFixed(2),lon:+c.lng.toFixed(1),lat:+c.lat.toFixed(1),grey,focus:focusReg,mark:getComputedStyle(document.querySelector("#mark")).display}`);
    if (!(fr.zoom < 6.3 && fr.grey === 0 && fr.focus === null && fr.mark === "none" && fr.lat > 44 && fr.lat < 49)) throw new Error("carte France " + JSON.stringify(fr));
    const keep = await ev(`return S.terr`); await ev(`document.querySelector('#card [data-cs="terr"]').click();return 1`);
    await step("retour territoire", `document.querySelector("#card h3")?.textContent==="Puy-de-Dôme"&&focusReg==="R84"`);
    const g = await ev(`return Object.keys(carte.deps).filter(id=>map.getFeatureState({source:"d",id}).dim).length`);
    return keep === "D63" && g > 0 ? `territoire conservé ; France : zoom ${fr.zoom}, 0 grisé ; retour : ${g} grisés` : false;
  });
  await check("O04", "option 1 : légende avec repère du territoire ouvert", async () => { await ev(`select("D63");return 1`); await idle(); return ev(`const m=document.querySelector("#mark");return getComputedStyle(m).display!=="none"&&m.textContent.includes("Puy-de-Dôme")`); });
  await check("O05", "option 1 : onglets Territoire et comparaison, Expert ; la comparaison est sous la fiche", async () => {
    if (!(await ev(`return !!document.querySelector("#terrpanel #card")&&!!document.querySelector("#terrpanel #cmp")&&!document.querySelector('[data-tab="cmp"]')`))) throw new Error("fiche et comparaison non réunies");
    for (const t of ["xp", "terr"]) { await ev(`document.querySelector('[data-tab="${t}"]').click();return 1`); if (!(await ev(`return document.querySelector('[data-tab="${t}"]').getAttribute("aria-selected")==="true"`))) throw new Error(t); }
  });
}

// ---------- captures (pour le rapport et la comparaison avec la maquette) ----------
if (CAPTURES) {
  for (const [w, h, nom] of [[1440, 900, "ordinateur"], [390, 844, "mobile"]]) {
    await open("p=kines&l=quotas:1.2&v=evo&t=D63", w, h); await until(`S.terr==="D63"`); await idle();
    await ev(`await new Promise(r=>map.once("idle",r));await new Promise(r=>setTimeout(r,600));return 1`);   // carte dessinée, chiffres arrivés au bout de leur animation
    const shot = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: w < 700 });
    writeFileSync(join(CAPTURES, `carte-${nom}.png`), Buffer.from(shot.result.data, "base64"));
  }
}

// ---------- rapport ----------
ws.close(); chrome.kill(); try { rmSync(prof, { recursive: true, force: true }); } catch {}
const ok = R.filter(r => r[1] === "OK").length;
for (const [id, st, name, info] of R) console.log(`${st === "OK" ? "✓" : "✗"} ${id} ${name}${info ? "  — " + info : ""}`);
console.log(`\n${ok}/${R.length} contrôles passés · ${URL0}${OPTION1 ? " · option 1" : ""}`);
process.exit(ok === R.length ? 0 : 1);
