// ACTXION slide renderer: node render.mjs slides.json outdir
// slides.json = {"series":"Fan Pulse","slides":[{type,...}]}  -> outdir/01.png ...
// Shared brand with actxion-visuals: newsprint #F2EEE5, card red #E61E28, Anton / Barlow Condensed / Source Serif 4.
import { chromium } from 'playwright';
import fs from 'fs';
const [, , specPath, outDir = 'out'] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
// Official ACTXION logos (transparent PNGs): lockup = mark + wordmark, mark = icon only.
// Looked up in $ACTXION_LOGO_DIR, else ../assets/logo next to this script.
const LOGO_DIR = process.env.ACTXION_LOGO_DIR || new URL('../assets/logo/', import.meta.url).pathname;
const logo = n => `data:image/png;base64,${fs.readFileSync(LOGO_DIR.replace(/\/?$/, '/') + n).toString('base64')}`;
const LOCK = { black: logo('lockup-black.png'), white: logo('lockup-white.png') };

const css = `
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=block');
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#0A0A0A;--paper:#F2EEE5;--card:#E61E28;--mute:#6E6A62;--rule:#D9D3C6}
body{width:1080px;height:1350px;overflow:hidden}
.s{position:relative;width:1080px;height:1350px;padding:84px 88px;display:flex;flex-direction:column;overflow:hidden;background:var(--paper);color:var(--ink)}
.s.night{background:#050505;color:#fff;--mute:#9A968E}
.top{display:flex;justify-content:space-between;align-items:center;height:56px;position:relative;z-index:3;padding-bottom:18px;border-bottom:3px solid currentColor}
.brand{display:block;height:40px;width:auto}
.meta{font-family:'Barlow Condensed';font-weight:700;font-size:28px;letter-spacing:.02em}
.meta span{color:var(--card)}
.h{font-family:'Anton';font-weight:400;line-height:.98;letter-spacing:.002em}
.body{font-family:'Source Serif 4';font-size:36px;line-height:1.36;max-width:880px}
.body strong{font-weight:600}
.src{position:absolute;left:88px;right:88px;bottom:56px;font-family:'Barlow Condensed';font-weight:500;font-size:24px;color:var(--mute);z-index:3;padding-top:14px;border-top:2px solid var(--rule)}
.night .src{border-top-color:rgba(255,255,255,.18)}
.grow{flex:1}
.grain{position:absolute;inset:0;opacity:.22;mix-blend-mode:multiply;z-index:2;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .3 0 0 0 0 .27 0 0 0 0 .22 0 0 0 .55 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.night .grain{mix-blend-mode:screen;opacity:.10}
.card{background:var(--card);color:#fff;border-radius:18px;box-shadow:0 2px 0 rgba(0,0,0,.25),0 24px 50px rgba(0,0,0,.28)}
.photo{position:absolute;inset:0;background-size:cover;background-position:center;filter:contrast(1.06) saturate(1.08)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,5,5,.55) 0%,rgba(5,5,5,0) 24%,rgba(5,5,5,.2) 46%,rgba(5,5,5,.86) 72%,#050505 92%)}
/* photo band on newsprint slides: real-colour photo across the top, ink rule under it */
.band{position:absolute;left:0;right:0;top:0;height:var(--bh,500px);overflow:hidden;border-bottom:6px solid var(--ink);z-index:1}
.band .photo{filter:contrast(1.05) saturate(1.08)}
.band:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.62) 0%,rgba(0,0,0,0) 34%)}
.has-band .top{color:#fff;border-bottom-color:rgba(255,255,255,.85)}
.has-band .meta{text-shadow:0 1px 8px rgba(0,0,0,.5)}
.has-band .meta span,.night .meta span{color:#fff;background:var(--card);padding:0 8px;border-radius:5px;margin-right:4px}
.bandpad{height:calc(var(--bh,500px) - 140px);flex:0 0 auto}
.credit{position:absolute;right:20px;top:calc(var(--bh,500px) - 40px);z-index:3;font-family:'Barlow Condensed';font-weight:500;font-size:20px;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.7)}
.kicker{align-self:flex-start;font-family:'Barlow Condensed';font-weight:700;font-size:30px;background:var(--card);color:#fff;padding:6px 16px 8px;border-radius:8px;margin-bottom:22px;position:relative;z-index:3}
/* cover */
.cover .card{position:absolute;right:92px;top:210px;width:240px;height:330px;transform:rotate(7deg);padding:24px 24px 26px;z-index:3;display:flex;flex-direction:column;justify-content:space-between}
.cover .card .k{font-family:'Anton';font-size:112px;line-height:.9}
.cover .card .l{font-family:'Barlow Condensed';font-weight:700;font-size:30px;line-height:1.02}
.cover .h{font-size:136px;position:relative;z-index:3}
.cover .body{position:relative;z-index:3;margin-top:30px;color:#F2EEE5}
.cover .h,.outro .h{text-shadow:0 2px 24px rgba(0,0,0,.35)}
/* stat */
.stat .card{padding:44px 56px 52px;transform:rotate(-2.5deg);margin-top:20px;align-self:flex-start;max-width:100%}
.stat .num{font-family:'Anton';line-height:.95}
.stat .unit{font-family:'Barlow Condensed';font-weight:700;font-size:46px;line-height:1.05;margin-top:14px}
.stat .body{margin-top:70px}
.has-band.stat .card{margin-top:-10px}
.has-band.stat .body{margin-top:60px;font-size:40px}
/* bars */
.bars .h{font-size:92px;margin:64px 0 60px}
.has-band .h{margin-top:40px!important}
.has-band.bars .h{font-size:76px;margin-bottom:40px}
.has-band .bar{margin-bottom:26px}
.has-band .bar .track{height:26px}
.bar{margin-bottom:40px}
.bar .lab{display:flex;justify-content:space-between;align-items:baseline;font-family:'Barlow Condensed';font-weight:600;font-size:36px;margin-bottom:10px}
.bar .lab b{font-family:'Anton';font-weight:400;font-size:50px}
.bar .track{height:34px;background:var(--rule)}
.bar .fill{height:100%;background:var(--ink)}
.bar.hi .fill{background:var(--card)}
.bars .body{font-size:34px}
/* quote */
.quote .card{padding:56px 60px 60px;transform:rotate(-2deg)}
.quote .q{font-family:'Anton';font-size:84px;line-height:1.02}
.quote .who{font-family:'Barlow Condensed';font-weight:800;font-size:40px;margin-top:40px}
.quote .who span{display:block;font-family:'Source Serif 4';font-weight:400;font-size:30px;color:var(--mute);margin-top:6px}
/* versus (ballot) */
.versus .h{font-size:100px;margin:64px 0 54px}
.opt{display:flex;gap:30px;align-items:flex-start;padding:34px 0;border-top:3px solid var(--ink)}
.opt:last-of-type{border-bottom:3px solid var(--ink)}
.opt .box{flex:0 0 78px;height:78px;border:5px solid var(--ink);position:relative;transform:rotate(-2deg)}
.opt.tick .box:after{content:'';position:absolute;left:18px;top:-6px;width:28px;height:56px;border:solid var(--card);border-width:0 12px 12px 0;transform:rotate(40deg)}
.opt .t{font-family:'Anton';font-size:64px;line-height:1}
.opt .d{font-family:'Source Serif 4';font-size:30px;margin-top:10px;color:#3A3833}
.versus .body{margin-top:44px}
.opt .pic{flex:0 0 210px;height:150px;margin-left:auto;border-radius:12px;background-size:cover;background-position:center;border:4px solid var(--ink);transform:rotate(1.5deg)}
.opt.tick .pic{border-color:var(--card)}
.has-band.versus .h{font-size:78px;margin-bottom:34px}
.has-band .opt{padding:20px 0}
.has-band .opt .t{font-size:56px}
.has-band.versus .body{margin-top:28px;font-size:32px}
/* ballot with two photo tiles: side-by-side picks */
.pair{display:flex;gap:28px;margin-top:8px}
.tile{flex:1;display:flex;flex-direction:column}
.tile .img{height:430px;border-radius:14px;background-size:cover;background-position:center;border:5px solid var(--ink);position:relative}
.tile:first-child .img{transform:rotate(-1.5deg)}.tile:last-child .img{transform:rotate(1.5deg)}
.tile.tick .img{border-color:var(--card)}
.tile .row{display:flex;gap:18px;align-items:flex-start;margin-top:30px}
.tile .box{flex:0 0 58px;height:58px;border:5px solid var(--ink);position:relative;transform:rotate(-2deg)}
.tile.tick .box:after{content:'';position:absolute;left:12px;top:-6px;width:22px;height:44px;border:solid var(--card);border-width:0 10px 10px 0;transform:rotate(40deg)}
.tile .t{font-family:'Anton';font-size:50px;line-height:1}
.tile .d{font-family:'Source Serif 4';font-size:27px;margin-top:8px;color:#3A3833}
.pair + .body{margin-top:40px;font-size:32px}
/* points */
.points .h{font-size:100px;margin:64px 0 50px}
.has-band.points .h{font-size:80px;margin-bottom:30px}
.has-band .pt{padding:22px 0}
.pt{display:flex;gap:30px;padding:30px 0;border-top:3px solid var(--ink)}
.pt .i{flex:0 0 68px;height:92px;background:var(--card);color:#fff;border-radius:10px;transform:rotate(-6deg);font-family:'Anton';font-size:54px;display:flex;align-items:center;justify-content:center}
.pt .x{font-family:'Source Serif 4';font-size:33px;line-height:1.32}
.pt .x b{display:block;font-family:'Barlow Condensed';font-weight:800;font-size:46px;line-height:1.05;margin-bottom:6px}
/* outro */
.outro .card{position:absolute;right:-50px;bottom:-80px;width:340px;height:470px;transform:rotate(14deg)}
.outro .sign{width:560px;margin-bottom:64px;position:relative;z-index:3}
.outro .h{font-size:108px;position:relative;z-index:3}
.outro .body{margin-top:36px;position:relative;z-index:3;color:#EAE6DD}
.outro .cta{margin-top:56px;align-self:flex-start;background:var(--paper);color:var(--ink);font-family:'Barlow Condensed';font-weight:800;font-size:40px;padding:18px 36px;border-radius:10px;position:relative;z-index:3}
`;

const nl = t => esc(t).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
const top = (i, n, night, bare) => `<div class="top">${bare ? '<span></span>' : `<img class="brand" src="${night ? LOCK.white : LOCK.black}" alt="ACTXION">`}
  <span class="meta">${esc(spec.series || '')}${spec.series ? ' &nbsp;' : ''}${n > 1 ? `<span>${i}</span>/${n}` : ''}</span></div>`;
const src = s => s.source ? `<div class="src">${esc(s.source)}</div>` : '';
const NIGHT = new Set(['cover', 'outro']);

const T = {
  cover: s => `${s.photo ? `<div class="photo" style="background-image:url('${s.photo}')"></div><div class="shade"></div>` : ''}
    ${s.card ? `<div class="card"><div class="k">${esc(s.card.big)}</div><div class="l">${nl(s.card.small)}</div></div>` : ''}
    <div class="grow"></div>${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ''}
    <div class="h">${nl(s.title)}</div>${s.text ? `<div class="body">${nl(s.text)}</div>` : ''}<div style="height:76px"></div>`,
  stat: s => `${s.photo ? '<div class="bandpad"></div>' : '<div class="grow"></div>'}<div class="card"><div class="num" style="font-size:${Math.min(300, Math.floor(1450 / Math.max(3, String(s.number).length)))}px">${esc(s.number)}</div><div class="unit">${nl(s.label)}</div></div>
    <div class="body">${nl(s.text)}</div><div style="height:110px"></div>`,
  bars: s => {
    const max = Math.max(...s.bars.map(b => b.value));
    return `${s.photo ? '<div class="bandpad"></div>' : ''}<div class="h">${nl(s.title)}</div>` + s.bars.map(b =>
      `<div class="bar ${b.highlight ? 'hi' : ''}"><div class="lab"><span>${esc(b.label)}</span><b>${esc(b.display ?? b.value)}</b></div><div class="track"><div class="fill" style="width:${Math.max(3, b.value / max * 100)}%"></div></div></div>`).join('') +
      (s.text ? `<div class="grow"></div><div class="body">${nl(s.text)}</div><div style="height:96px"></div>` : '');
  },
  quote: s => `${s.photo ? '<div class="bandpad"></div>' : '<div class="grow"></div>'}<div class="card"><div class="q">“${nl(s.quote)}”</div></div>
    <div class="who">${esc(s.who)}<span>${esc(s.role || '')}</span></div><div style="height:120px"></div>`,
  versus: s => (s.options.length === 2 && s.options.every(o => o.photo)) ? `<div class="h" style="font-size:84px;margin:56px 0 40px">${nl(s.title)}</div><div class="pair">` + s.options.map(o =>
      `<div class="tile ${o.tick ? 'tick' : ''}"><div class="img" style="background-image:url('${o.photo}')"></div><div class="row"><div class="box"></div><div><div class="t">${nl(o.title)}</div>${o.text ? `<div class="d">${nl(o.text)}</div>` : ''}</div></div></div>`).join('') + `</div>` + (s.text ? `<div class="body">${nl(s.text)}</div>` : '')
    : `${s.photo ? '<div class="bandpad"></div>' : ''}<div class="h">${nl(s.title)}</div>` + s.options.map((o, k) =>
      `<div class="opt ${o.tick ? 'tick' : ''}"><div class="box"></div><div><div class="t">${nl(o.title)}</div>${o.text ? `<div class="d">${nl(o.text)}</div>` : ''}</div>${o.photo ? `<div class="pic" style="background-image:url('${o.photo}')"></div>` : ''}</div>`).join('') +
      (s.text ? `<div class="body">${nl(s.text)}</div>` : ''),
  points: s => `${s.photo ? '<div class="bandpad"></div>' : ''}<div class="h">${nl(s.title)}</div>` + s.points.map((p, k) =>
      `<div class="pt"><div class="i">${k + 1}</div><div class="x"><b>${esc(p.head)}</b>${esc(p.text || '')}</div></div>`).join(''),
  outro: s => `${s.photo ? `<div class="photo" style="background-image:url('${s.photo}')"></div><div class="shade"></div>` : ''}<div class="card"></div><div class="grow"></div><img class="sign" src="${LOCK.white}" alt="ACTXION"><div class="h">${nl(s.title || 'The fan’s view of\nthe business of football')}</div>
    <div class="body">${nl(s.text || '500K+ fans already give their verdict on the ACTXION app.')}</div>
    <div class="cta">${esc(s.cta || 'Follow for Fan Pulse every Wednesday')}</div><div style="height:250px"></div>`,
};

async function inline(u) {
  if (!u || u.startsWith('data:')) return u;
  if (!/^https?:/.test(u)) return `data:image/jpeg;base64,${fs.readFileSync(u).toString('base64')}`;
  const r = await fetch(u, { headers: { 'User-Agent': 'ACTXION-slides/1.0 (adnana@actxion.com)' } });
  if (!r.ok) throw new Error(`photo ${r.status} ${u}`);
  return `data:${r.headers.get('content-type') || 'image/jpeg'};base64,${Buffer.from(await r.arrayBuffer()).toString('base64')}`;
}
const safe = u => inline(u).catch(e => { console.error('WARN photo dropped:', e.message); return ''; });
for (const s of spec.slides) {
  if (s.photo) s.photo = await safe(s.photo);
  for (const o of s.options || []) if (o.photo) o.photo = await safe(o.photo);
}

// The cloud image ships its own Chromium (often a newer build than this Playwright pins),
// so fall back to it instead of failing on a missing download.
async function launch() {
  try { return await chromium.launch(); } catch (e) {
    const fallbacks = [process.env.CHROMIUM_PATH, '/opt/pw-browsers/chromium'].filter(Boolean);
    for (const executablePath of fallbacks) if (fs.existsSync(executablePath)) return chromium.launch({ executablePath });
    throw e;
  }
}
const browser = await launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
const n = spec.slides.length;
for (let i = 0; i < n; i++) {
  const s = spec.slides[i];
  const band = !!s.photo && !NIGHT.has(s.type);
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
    <div class="s ${s.type} ${NIGHT.has(s.type) ? 'night' : ''} ${band ? 'has-band' : ''}" style="--bh:${s.bandHeight || ({ quote: 620, stat: 560 }[s.type] || 460)}px">
    ${band ? `<div class="band"><div class="photo" style="background-image:url('${s.photo}');background-position:${s.focus || 'center'}"></div></div>` : ''}
    <div class="grain"></div>${top(i + 1, n, NIGHT.has(s.type) || band, s.type === 'outro')}${T[s.type](s)}${src(s)}</div></body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const f = `${outDir}/${String(i + 1).padStart(2, '0')}.png`;
  await page.screenshot({ path: f });
  console.log(f);
}
await browser.close();
