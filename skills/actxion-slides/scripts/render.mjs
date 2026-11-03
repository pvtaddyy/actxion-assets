// ACTXION slide renderer: node render.mjs slides.json outdir
// slides.json = {"series":"Fan Pulse","slides":[{type,...}]}  -> outdir/01.png ...
// Shared brand with actxion-visuals: newsprint #F2EEE5, card red #E61E28, Anton / Barlow Condensed / Source Serif 4.
import { chromium } from 'playwright';
import fs from 'fs';
const [, , specPath, outDir = 'out'] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const MARK = 'data:image/png;base64,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';

const css = `
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=block');
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#0A0A0A;--paper:#F2EEE5;--card:#E61E28;--mute:#6E6A62;--rule:#D9D3C6}
body{width:1080px;height:1350px;overflow:hidden}
.s{position:relative;width:1080px;height:1350px;padding:84px 88px;display:flex;flex-direction:column;overflow:hidden;background:var(--paper);color:var(--ink)}
.s.night{background:#050505;color:#fff;--mute:#9A968E}
.top{display:flex;justify-content:space-between;align-items:center;height:56px;position:relative;z-index:3;padding-bottom:18px;border-bottom:3px solid currentColor}
.brand{display:flex;align-items:center;gap:14px}
.brand img{height:42px;filter:invert(1)}
.night .brand img{filter:none}
.word{font-family:'Anton';font-size:38px;letter-spacing:.03em}
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
.photo{position:absolute;inset:0;background-size:cover;background-position:center;filter:grayscale(1) contrast(1.25) brightness(.55)}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(0,0,0,.55) 1.3px,transparent 1.6px);background-size:7px 7px;mix-blend-mode:multiply;opacity:.55}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,5,5,.6) 0%,rgba(5,5,5,0) 28%,rgba(5,5,5,.35) 52%,#050505 90%)}
.kicker{font-family:'Barlow Condensed';font-weight:700;font-size:34px;color:var(--card);margin-bottom:18px;position:relative;z-index:3}
/* cover */
.cover .card{position:absolute;right:92px;top:210px;width:240px;height:330px;transform:rotate(7deg);padding:24px 24px 26px;z-index:3;display:flex;flex-direction:column;justify-content:space-between}
.cover .card .k{font-family:'Anton';font-size:112px;line-height:.9}
.cover .card .l{font-family:'Barlow Condensed';font-weight:700;font-size:30px;line-height:1.02}
.cover .h{font-size:136px;position:relative;z-index:3}
.cover .body{position:relative;z-index:3;margin-top:30px;color:#EAE6DD}
/* stat */
.stat .card{padding:44px 56px 52px;transform:rotate(-2.5deg);margin-top:20px;align-self:flex-start;max-width:100%}
.stat .num{font-family:'Anton';line-height:.95}
.stat .unit{font-family:'Barlow Condensed';font-weight:700;font-size:46px;line-height:1.05;margin-top:14px}
.stat .body{margin-top:70px}
/* bars */
.bars .h{font-size:92px;margin:64px 0 60px}
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
/* points */
.points .h{font-size:100px;margin:64px 0 50px}
.pt{display:flex;gap:30px;padding:30px 0;border-top:3px solid var(--ink)}
.pt .i{flex:0 0 68px;height:92px;background:var(--card);color:#fff;border-radius:10px;transform:rotate(-6deg);font-family:'Anton';font-size:54px;display:flex;align-items:center;justify-content:center}
.pt .x{font-family:'Source Serif 4';font-size:33px;line-height:1.32}
.pt .x b{display:block;font-family:'Barlow Condensed';font-weight:800;font-size:46px;line-height:1.05;margin-bottom:6px}
/* outro */
.outro .card{position:absolute;right:-50px;bottom:-80px;width:340px;height:470px;transform:rotate(14deg)}
.outro .h{font-size:120px;position:relative;z-index:3}
.outro .body{margin-top:36px;position:relative;z-index:3;color:#EAE6DD}
.outro .cta{margin-top:56px;align-self:flex-start;background:var(--paper);color:var(--ink);font-family:'Barlow Condensed';font-weight:800;font-size:40px;padding:18px 36px;border-radius:10px;position:relative;z-index:3}
`;

const nl = t => esc(t).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
const top = (i, n) => `<div class="top"><span class="brand"><img src="${MARK}"><span class="word">ACTXION</span></span>
  <span class="meta">${esc(spec.series || '')}${spec.series ? ' &nbsp;' : ''}${n > 1 ? `<span>${i}</span>/${n}` : ''}</span></div>`;
const src = s => s.source ? `<div class="src">${esc(s.source)}</div>` : '';
const NIGHT = new Set(['cover', 'outro']);

const T = {
  cover: s => `${s.photo ? `<div class="photo" style="background-image:url('${s.photo}')"></div><div class="dots"></div><div class="shade"></div>` : ''}
    ${s.card ? `<div class="card"><div class="k">${esc(s.card.big)}</div><div class="l">${nl(s.card.small)}</div></div>` : ''}
    <div class="grow"></div>${s.kicker ? `<div class="kicker">${esc(s.kicker)}</div>` : ''}
    <div class="h">${nl(s.title)}</div>${s.text ? `<div class="body">${nl(s.text)}</div>` : ''}<div style="height:76px"></div>`,
  stat: s => `<div class="grow"></div><div class="card"><div class="num" style="font-size:${Math.min(300, Math.floor(1450 / Math.max(3, String(s.number).length)))}px">${esc(s.number)}</div><div class="unit">${nl(s.label)}</div></div>
    <div class="body">${nl(s.text)}</div><div style="height:110px"></div>`,
  bars: s => {
    const max = Math.max(...s.bars.map(b => b.value));
    return `<div class="h">${nl(s.title)}</div>` + s.bars.map(b =>
      `<div class="bar ${b.highlight ? 'hi' : ''}"><div class="lab"><span>${esc(b.label)}</span><b>${esc(b.display ?? b.value)}</b></div><div class="track"><div class="fill" style="width:${Math.max(3, b.value / max * 100)}%"></div></div></div>`).join('') +
      (s.text ? `<div class="grow"></div><div class="body">${nl(s.text)}</div><div style="height:96px"></div>` : '');
  },
  quote: s => `<div class="grow"></div><div class="card"><div class="q">“${nl(s.quote)}”</div></div>
    <div class="who">${esc(s.who)}<span>${esc(s.role || '')}</span></div><div style="height:120px"></div>`,
  versus: s => `<div class="h">${nl(s.title)}</div>` + s.options.map((o, k) =>
      `<div class="opt ${o.tick ? 'tick' : ''}"><div class="box"></div><div><div class="t">${nl(o.title)}</div>${o.text ? `<div class="d">${nl(o.text)}</div>` : ''}</div></div>`).join('') +
      (s.text ? `<div class="body">${nl(s.text)}</div>` : ''),
  points: s => `<div class="h">${nl(s.title)}</div>` + s.points.map((p, k) =>
      `<div class="pt"><div class="i">${k + 1}</div><div class="x"><b>${esc(p.head)}</b>${esc(p.text || '')}</div></div>`).join(''),
  outro: s => `<div class="card"></div><div class="grow"></div><div class="h">${nl(s.title || 'The fan’s view of\nthe business of football')}</div>
    <div class="body">${nl(s.text || 'A new Fan Pulse every Wednesday.\n500K+ fans already give their verdict on the ACTXION app.')}</div>
    <div class="cta">${esc(s.cta || 'Follow ACTXION')}</div><div style="height:250px"></div>`,
};

async function inline(u) {
  if (!u || u.startsWith('data:')) return u;
  if (!/^https?:/.test(u)) return `data:image/jpeg;base64,${fs.readFileSync(u).toString('base64')}`;
  const r = await fetch(u, { headers: { 'User-Agent': 'ACTXION-slides/1.0 (https://github.com/pvtaddyy/actxion-assets)' } });
  if (!r.ok) throw new Error(`photo ${r.status} ${u}`);
  return `data:${r.headers.get('content-type') || 'image/jpeg'};base64,${Buffer.from(await r.arrayBuffer()).toString('base64')}`;
}
for (const s of spec.slides) if (s.photo) s.photo = await inline(s.photo).catch(e => { console.error('WARN photo dropped:', e.message); return ''; });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
const n = spec.slides.length;
for (let i = 0; i < n; i++) {
  const s = spec.slides[i];
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
    <div class="s ${s.type} ${NIGHT.has(s.type) ? 'night' : ''}"><div class="grain"></div>${top(i + 1, n)}${T[s.type](s)}${src(s)}</div></body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const f = `${outDir}/${String(i + 1).padStart(2, '0')}.png`;
  await page.screenshot({ path: f });
  console.log(f);
}
await browser.close();
