// Minimal card renderer for Shamit Manilal's LinkedIn: node render.mjs spec.json outdir -> outdir/01.png ...
// spec = {"slides":[{type,...}]}. Deliberately plain: off-white page, black text, his name small at the bottom.
// No logos, no series labels, no brand colours, no decoration. Photos stay in real colour.
import { chromium } from 'playwright';
import fs from 'fs';
const [, , specPath, outDir = 'out'] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
// **...** is ignored on purpose (kept so older specs still render): plain text only
const nl = t => esc(t).replace(/\*\*(.+?)\*\*/g, '$1').replace(/\n/g, '<br>');
const NAME = spec.name || 'Shamit Manilal';

const css = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=block');
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden}
.s{position:relative;width:1080px;height:1350px;padding:120px 110px;display:flex;flex-direction:column;background:#FAFAF8;color:#111}
.grow{flex:1}
.name{font-family:'Inter';font-weight:500;font-size:28px;color:#8A8A85}
.src{font-family:'Inter';font-size:22px;color:#A3A39E;margin-bottom:14px}
.q{font-family:'Source Serif 4';font-weight:400;line-height:1.22;letter-spacing:-.01em}
.ctx{font-family:'Inter';font-size:30px;line-height:1.45;color:#6B6B66;margin-top:44px;max-width:820px}
.num{font-family:'Inter';font-weight:700;letter-spacing:-.04em;line-height:.95}
.lab{font-family:'Inter';font-weight:500;font-size:44px;line-height:1.2;margin-top:34px;max-width:840px}
.pic{padding:0}
.pic .ph{height:760px;background-size:cover;background-position:center}
.pic .tx{flex:1;display:flex;flex-direction:column;padding:70px 110px 110px}
.pic .h{font-family:'Inter';font-weight:600;line-height:1.12;letter-spacing:-.02em}
.pic .ctx{margin-top:24px;font-size:28px}
.credit{font-family:'Inter';font-size:20px;color:#A3A39E;margin-top:18px}
.pt{padding:30px 0;border-top:1px solid #DDDDD8;font-family:'Inter';font-size:34px;line-height:1.35}
.pt b{display:block;font-weight:600;font-size:40px;margin-bottom:6px}
.h2{font-family:'Inter';font-weight:600;font-size:76px;line-height:1.08;letter-spacing:-.02em;margin-bottom:46px}
`;
const fit = (t, big, small, at) => { const L = String(t).length; return L <= at ? big : Math.max(small, Math.round(big * Math.sqrt(at / L))); };
const foot = s => `${s.source ? `<div class="src">${esc(s.source)}</div>` : ''}<div class="name">${esc(NAME)}</div>`;

const T = {
  note: s => `<div class="grow"></div><div class="q" style="font-size:${fit(s.quote, 80, 52, 60)}px">${nl(s.quote)}</div>${s.context ? `<div class="ctx">${nl(s.context)}</div>` : ''}<div class="grow"></div>${foot(s)}`,
  stat: s => `<div class="grow"></div><div class="num" style="font-size:${Math.min(300, Math.floor(1500 / Math.max(3, String(s.number).length)))}px">${esc(s.number)}</div><div class="lab">${nl(s.label)}</div>${s.text ? `<div class="ctx">${nl(s.text)}</div>` : ''}<div class="grow"></div>${foot(s)}`,
  pic: s => `<div class="ph" style="background-image:url('${s.photo}');background-position:${s.focus || 'center'}"></div><div class="tx"><div class="h" style="font-size:${fit(s.title, 68, 50, 40)}px">${nl(s.title)}</div>${s.text ? `<div class="ctx">${nl(s.text)}</div>` : ''}<div class="grow"></div>${s.credit ? `<div class="credit">${esc(s.credit)}</div>` : ''}<div class="name" style="margin-top:10px">${esc(NAME)}</div></div>`,
  points: s => `<div class="h2">${nl(s.title)}</div>${s.points.map(p => `<div class="pt"><b>${esc(p.head)}</b>${esc(p.text || '')}</div>`).join('')}<div class="grow"></div>${foot(s)}`,
  cover: s => `<div class="grow"></div><div class="q" style="font-size:${fit(s.title, 96, 64, 40)}px">${nl(s.title)}</div>${s.text ? `<div class="ctx">${nl(s.text)}</div>` : ''}<div class="grow"></div>${foot(s)}`,
  outro: s => `<div class="grow"></div><div class="q" style="font-size:64px">${nl(s.title || 'Thanks for reading.')}</div>${s.text ? `<div class="ctx">${nl(s.text)}</div>` : ''}<div class="grow"></div>${foot(s)}`,
};

async function inline(u) {
  if (!u || u.startsWith('data:')) return u;
  if (!/^https?:/.test(u)) return `data:image/jpeg;base64,${fs.readFileSync(u).toString('base64')}`;
  const r = await fetch(u, { headers: { 'User-Agent': 'founder-cards/1.0 (https://github.com/pvtaddyy/actxion-assets)' } });
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
for (let i = 0; i < spec.slides.length; i++) {
  const s = spec.slides[i];
  let t = (s.type === 'photo' || s.type === 'pic') ? 'pic' : s.type;
  if (t === 'pic' && !s.photo) { t = 'note'; s.quote = s.quote || s.title || ''; s.context = s.context || s.text; } // photo failed: plain text card
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body><div class="s ${t}">${T[t](s)}</div></body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const f = `${outDir}/${String(i + 1).padStart(2, '0')}.png`;
  await page.screenshot({ path: f });
  console.log(f);
}
await browser.close();
