// Shamit Manilal "build log" renderer: node render.mjs spec.json outdir  -> outdir/01.png ...
// spec = {"series":"0 to Unicorn","slides":[{type,...}]}
// Personal look, distinct from the ACTXION page's red-card-on-newsprint: midnight ground, chalk type,
// ACTXION red only for the one key number / underline, signed with his name, small official ACTXION mark.
// Same fonts as the ACTXION family: Anton, Barlow Condensed, Source Serif 4. Photos stay in real colour.
import { chromium } from 'playwright';
import fs from 'fs';
const [, , specPath, outDir = 'out'] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const nl = t => esc(t).replace(/\*\*(.+?)\*\*/g, '<em>$1</em>').replace(/\n/g, '<br>');
const LOGO_DIR = (process.env.ACTXION_LOGO_DIR || new URL('../../actxion-slides/assets/logo/', import.meta.url).pathname).replace(/\/?$/, '/');
const MARK = fs.existsSync(LOGO_DIR + 'mark-white.png') ? `data:image/png;base64,${fs.readFileSync(LOGO_DIR + 'mark-white.png').toString('base64')}` : '';
const NAME = spec.name || 'Shamit Manilal';
const ROLE = spec.role || 'Founder, ACTXION';

const css = `
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400;1,8..60,600&display=block');
*{margin:0;padding:0;box-sizing:border-box}
:root{--night:#0F1115;--chalk:#F4F1EA;--mute:#8C8A85;--line:rgba(244,241,234,.16);--red:#E61E28}
body{width:1080px;height:1350px;overflow:hidden}
.s{position:relative;width:1080px;height:1350px;padding:80px 88px 0;display:flex;flex-direction:column;overflow:hidden;background:var(--night);color:var(--chalk)}
.grain{position:absolute;inset:0;opacity:.09;mix-blend-mode:screen;z-index:2;pointer-events:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
/* top: the 0 -> unicorn track (signature motif) + series label */
.top{position:relative;z-index:3}
.series{display:flex;justify-content:space-between;align-items:baseline;font-family:'Barlow Condensed';font-weight:700;font-size:30px;letter-spacing:.06em;text-transform:uppercase}
.series .n{color:var(--mute);letter-spacing:.02em}
.track{display:flex;align-items:center;gap:18px;margin-top:20px}
.track b{font-family:'Barlow Condensed';font-weight:600;font-size:22px;color:var(--mute);letter-spacing:.1em}
.track .ln{position:relative;flex:1;height:16px}
.track .ln:before{content:'';position:absolute;left:0;right:0;top:7px;height:3px;background:var(--line)}
.track .ln:after{content:'';position:absolute;left:0;width:var(--p,0%);top:6px;height:5px;background:var(--red);border-radius:3px}
.track i{position:absolute;top:1px;width:3px;height:15px;background:var(--line)}
.pic .series,.cover .series{text-shadow:0 1px 10px rgba(0,0,0,.6)}
.h{font-family:'Anton';font-weight:400;line-height:1;letter-spacing:.003em}
.body{font-family:'Source Serif 4';font-size:36px;line-height:1.38;color:#DAD6CD}
.grow{flex:1}
/* signature footer */
.sig{position:absolute;left:88px;right:88px;bottom:64px;display:flex;align-items:center;gap:22px;z-index:3;padding-top:26px;border-top:2px solid var(--line)}
.sig .av{width:64px;height:64px;border-radius:50%;background:var(--red);display:flex;align-items:center;justify-content:center;font-family:'Anton';font-size:30px;color:#fff;flex:0 0 auto}
.sig .nm{font-family:'Barlow Condensed';font-weight:800;font-size:36px;line-height:1}
.sig .rl{font-family:'Barlow Condensed';font-weight:500;font-size:26px;color:var(--mute);margin-top:4px}
.sig img{height:40px;margin-left:auto;opacity:.95}
.src{position:absolute;left:88px;right:88px;bottom:176px;font-family:'Barlow Condensed';font-weight:500;font-size:23px;color:var(--mute);z-index:3}
/* note: his own line, big serif */
.note .mark{font-family:'Anton';font-size:220px;line-height:.7;color:var(--red);height:120px}
.note .q{font-family:'Source Serif 4';font-weight:600;line-height:1.16;letter-spacing:-.005em;margin-top:30px}
.note .q em{font-style:italic;font-weight:600;color:#fff;background:linear-gradient(transparent 70%,rgba(230,30,40,.55) 70%)}
.note .ctx{margin-top:44px;font-size:32px;color:var(--mute);font-family:'Source Serif 4'}
/* stat */
.stat .num{font-family:'Anton';line-height:.9}
.stat .ul{height:14px;width:300px;background:var(--red);margin:26px 0 34px;border-radius:2px}
.stat .lab{font-family:'Barlow Condensed';font-weight:700;font-size:52px;line-height:1.05;max-width:880px}
.stat .body{margin-top:40px;max-width:860px}
/* photo: full-bleed real-colour photo, his hook over a dark fade */
.photo{position:absolute;inset:0;background-size:cover;background-position:center;filter:contrast(1.05) saturate(1.06)}
.fade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,17,21,.9) 0%,rgba(15,17,21,.55) 12%,rgba(15,17,21,0) 26%,rgba(15,17,21,.1) 40%,rgba(15,17,21,.9) 66%,#0F1115 84%)}
.pic .photo{top:216px}
.pic .fade{top:216px;background:linear-gradient(180deg,rgba(15,17,21,.35) 0%,rgba(15,17,21,0) 14%,rgba(15,17,21,.1) 38%,rgba(15,17,21,.9) 62%,#0F1115 80%)}
.pic .h{position:relative;z-index:3;font-size:104px;text-shadow:0 2px 24px rgba(0,0,0,.4)}
.pic .body{position:relative;z-index:3;margin-top:26px;color:#E6E2D9}
.pic .credit{position:absolute;right:26px;top:232px;z-index:3;font-family:'Barlow Condensed';font-size:20px;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.8)}
/* points */
.points .h{font-size:96px;margin:90px 0 40px}
.pt{display:flex;gap:30px;padding:30px 0;border-top:2px solid var(--line)}
.pt .i{flex:0 0 auto;font-family:'Anton';font-size:64px;line-height:1;color:var(--red);width:60px}
.pt .x{font-family:'Source Serif 4';font-size:32px;line-height:1.32;color:#DAD6CD}
.pt .x b{display:block;font-family:'Barlow Condensed';font-weight:800;font-size:46px;line-height:1.05;margin-bottom:6px;color:var(--chalk)}
/* cover (carousel slide 1) */
.cover .h{font-size:132px;position:relative;z-index:3}
.cover .body{position:relative;z-index:3;margin-top:30px}
/* outro */
.outro .h{font-size:110px;margin-top:150px}
.outro .body{margin-top:34px}
.outro .cta{margin-top:54px;align-self:flex-start;background:var(--chalk);color:var(--night);font-family:'Barlow Condensed';font-weight:800;font-size:40px;padding:18px 36px;border-radius:10px}
`;

const fit = (t, big, small, at) => { const L = String(t).length; return L <= at ? big : Math.max(small, Math.round(big * Math.sqrt(at / L))); };
const top = (i, n, pct) => `<div class="top"><div class="series"><span>${esc(spec.series || '0 to Unicorn')}</span><span class="n">${n > 1 ? `${i}/${n}` : ''}</span></div>
  <div class="track" style="--p:${pct}%"><b>0</b><div class="ln">${Array.from({ length: 9 }, (_, k) => `<i style="left:${(k + 1) * 10}%"></i>`).join('')}</div><b>UNICORN</b></div></div>`;
const sig = () => `<div class="sig"><div class="av">${esc(NAME.split(' ').map(w => w[0]).join('').slice(0, 2))}</div><div><div class="nm">${esc(NAME)}</div><div class="rl">${esc(ROLE)}</div></div>${MARK ? `<img src="${MARK}" alt="ACTXION">` : ''}</div>`;
const src = s => s.source ? `<div class="src">${esc(s.source)}</div>` : '';

const T = {
  note: s => `<div class="grow"></div><div class="mark">“</div><div class="q" style="font-size:${fit(s.quote, 78, 50, 70)}px">${nl(s.quote)}</div>${s.context ? `<div class="ctx">${nl(s.context)}</div>` : ''}<div class="grow"></div><div style="height:200px"></div>`,
  stat: s => `<div class="grow"></div><div class="num" style="font-size:${Math.min(330, Math.floor(1700 / Math.max(3, String(s.number).length)))}px">${esc(s.number)}</div><div class="ul"></div><div class="lab">${nl(s.label)}</div>${s.text ? `<div class="body">${nl(s.text)}</div>` : ''}<div class="grow"></div><div style="height:240px"></div>`,
  pic: s => `<div class="photo" style="background-image:url('${s.photo}');background-position:${s.focus || 'center'}"></div><div class="fade"></div>${s.credit ? `<div class="credit">${esc(s.credit)}</div>` : ''}<div class="grow"></div><div class="h" style="font-size:${fit(s.title, 96, 66, 30)}px">${nl(s.title)}</div>${s.text ? `<div class="body">${nl(s.text)}</div>` : ''}<div style="height:${s.source ? 240 : 190}px"></div>`,
  points: s => `<div class="h">${nl(s.title)}</div>` + s.points.map((p, k) => `<div class="pt"><div class="i">${k + 1}</div><div class="x"><b>${esc(p.head)}</b>${esc(p.text || '')}</div></div>`).join(''),
  cover: s => `${s.photo ? `<div class="photo" style="background-image:url('${s.photo}')"></div><div class="fade"></div>` : ''}<div class="grow"></div><div class="h">${nl(s.title)}</div>${s.text ? `<div class="body">${nl(s.text)}</div>` : ''}<div style="height:220px"></div>`,
  outro: s => `<div class="h">${nl(s.title || 'Building ACTXION\nfrom 0 to unicorn,\nin public.')}</div><div class="body">${nl(s.text || 'The app 500K+ fans use to give their verdict. I share the wins, the misses and the lessons here.')}</div><div class="cta">${esc(s.cta || 'Follow Shamit for the build')}</div>`,
};
// alias so specs can say "photo" for the full-bleed template
T.photo = T.pic;

async function inline(u) {
  if (!u || u.startsWith('data:')) return u;
  if (!/^https?:/.test(u)) return `data:image/jpeg;base64,${fs.readFileSync(u).toString('base64')}`;
  const r = await fetch(u, { headers: { 'User-Agent': 'ACTXION-founder-slides/1.0 (https://github.com/pvtaddyy/actxion-assets)' } });
  if (!r.ok) throw new Error(`photo ${r.status} ${u}`);
  return `data:${r.headers.get('content-type') || 'image/jpeg'};base64,${Buffer.from(await r.arrayBuffer()).toString('base64')}`;
}
for (const s of spec.slides) if (s.photo) s.photo = await inline(s.photo).catch(e => { console.error('WARN photo dropped:', e.message); return ''; });

async function launch() {
  try { return await chromium.launch(); } catch (e) {
    for (const p of [process.env.CHROMIUM_PATH, '/opt/pw-browsers/chromium'].filter(Boolean)) if (fs.existsSync(p)) return chromium.launch({ executablePath: p });
    throw e;
  }
}
const browser = await launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
const n = spec.slides.length;
for (let i = 0; i < n; i++) {
  const s = spec.slides[i];
  const type = (s.type === 'photo' || s.type === 'pic') ? 'pic' : s.type;
  const t = (type === 'pic' && !s.photo) ? 'note' : type; // photo failed: fall back to a note card, never a blank one
  if (t === 'note' && !s.quote) s.quote = s.title || '';
  const pct = s.progress ?? spec.progress ?? 0; // fill of the 0 -> unicorn track; 0 until the Day-1 date is known
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
    <div class="s ${t}"><div class="grain"></div>${top(i + 1, n, pct)}${T[t](s)}${src(s)}${sig()}</div></body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const f = `${outDir}/${String(i + 1).padStart(2, '0')}.png`;
  await page.screenshot({ path: f });
  console.log(f);
}
await browser.close();
