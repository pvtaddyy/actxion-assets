// Minimal card + carousel renderer for Shamit Manilal's LinkedIn: node render.mjs spec.json outdir -> outdir/01.png ...
// spec = {"slides":[{type,...}]}. Plain: off-white page, black text, ONE muted accent, his name small bottom-left,
// slide number bottom-right on carousels. No logos, series labels or brand colours. Photos stay in real colour.
// Carousel rules (ig-carousel skill): 1080x1350, all text inside a 120px safe area, nothing smaller than 32px
// except the footer, cover <= 6 words, one idea per slide (headline 3-7 words + <= 25 words), recap, one CTA.
import { chromium } from 'playwright';
import fs from 'fs';
const [, , specPath, outDir = 'out'] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const nl = t => esc(t).replace(/\*\*(.+?)\*\*/g, '$1').replace(/\n/g, '<br>');
const NAME = spec.name || 'Shamit Manilal';
const ACCENT = '#2F5D50'; // one muted accent (deep green): slide numbers, rule, recap numerals. Nothing else.

const css = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=block');
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden}
.s{position:relative;width:1080px;height:1350px;padding:120px;display:flex;flex-direction:column;background:#FAFAF8;color:#111}
.grow{flex:1}
.foot{position:absolute;left:120px;right:120px;bottom:72px;display:flex;justify-content:space-between;align-items:baseline;font-family:'Inter';font-weight:500;font-size:26px;color:#8A8A85}
.foot .n{color:${ACCENT};font-weight:600}
.src{font-family:'Inter';font-size:22px;color:#A3A39E;margin-top:28px}
.q{font-family:'Source Serif 4';font-weight:400;line-height:1.22;letter-spacing:-.01em}
.ctx{font-family:'Inter';font-size:32px;line-height:1.45;color:#5E5E59;margin-top:40px}
.num{font-family:'Inter';font-weight:700;letter-spacing:-.04em;line-height:.95}
.lab{font-family:'Inter';font-weight:500;font-size:44px;line-height:1.2;margin-top:34px}
.rule{width:96px;height:6px;background:${ACCENT};margin-bottom:44px}
/* photo card */
.pic{padding:0}
.pic .ph{height:760px;background-size:cover;background-position:center}
.pic .tx{flex:1;display:flex;flex-direction:column;padding:64px 120px 140px}
.pic .h{font-family:'Inter';font-weight:600;line-height:1.12;letter-spacing:-.02em}
.pic .ctx{margin-top:22px;font-size:32px}
.credit{font-family:'Inter';font-size:22px;color:#A3A39E;margin-top:auto}
/* carousel */
.cover .h{font-family:'Inter';font-weight:700;line-height:1.02;letter-spacing:-.035em}
.cover .p{font-family:'Source Serif 4';font-size:42px;line-height:1.3;color:#3E3E3A;margin-top:40px}
.cover .swipe{font-family:'Inter';font-weight:600;font-size:30px;color:${ACCENT};margin-top:56px}
.stake .q{font-size:64px}
.idea .k{font-family:'Inter';font-weight:600;font-size:30px;color:${ACCENT};margin-bottom:26px}
.idea .h{font-family:'Inter';font-weight:700;font-size:76px;line-height:1.06;letter-spacing:-.025em}
.idea .b{font-family:'Source Serif 4';font-size:44px;line-height:1.36;color:#2E2E2B;margin-top:40px}
.recap .h{font-family:'Inter';font-weight:700;font-size:64px;letter-spacing:-.02em;margin-bottom:40px}
.recap .it{display:flex;gap:28px;padding:28px 0;border-top:2px solid #E2E2DC;font-family:'Inter';font-size:40px;line-height:1.3}
.recap .it:last-child{border-bottom:2px solid #E2E2DC}
.recap .it i{font-style:normal;font-weight:700;color:${ACCENT};flex:0 0 44px}
.cta .h{font-family:'Inter';font-weight:700;font-size:80px;line-height:1.06;letter-spacing:-.025em}
.cta .b{font-family:'Source Serif 4';font-size:44px;line-height:1.36;color:#3E3E3A;margin-top:36px}
`;
const fit = (t, big, small, at) => { const L = String(t).length; return L <= at ? big : Math.max(small, Math.round(big * Math.sqrt(at / L))); };

const T = {
  // single cards
  note: s => `<div class="grow"></div><div class="q" style="font-size:${fit(s.quote, 80, 52, 60)}px">${nl(s.quote)}</div>${s.context ? `<div class="ctx">${nl(s.context)}</div>` : ''}${s.source ? `<div class="src">${esc(s.source)}</div>` : ''}<div class="grow"></div>`,
  stat: s => `<div class="grow"></div><div class="num" style="font-size:${Math.min(300, Math.floor(1400 / Math.max(3, String(s.number).length)))}px">${esc(s.number)}</div><div class="lab">${nl(s.label)}</div>${s.text ? `<div class="ctx">${nl(s.text)}</div>` : ''}${s.source ? `<div class="src">${esc(s.source)}</div>` : ''}<div class="grow"></div>`,
  pic: s => `<div class="ph" style="background-image:url('${s.photo}');background-position:${s.focus || 'center'}"></div><div class="tx"><div class="h" style="font-size:${fit(s.title, 68, 50, 40)}px">${nl(s.title)}</div>${s.text ? `<div class="ctx">${nl(s.text)}</div>` : ''}${s.credit ? `<div class="credit">${esc(s.credit)}</div>` : ''}</div>`,
  // carousel slides
  cover: s => `<div class="grow"></div><div class="rule"></div><div class="h" style="font-size:${fit(s.title, 128, 92, 22)}px">${nl(s.title)}</div>${s.promise ? `<div class="p">${nl(s.promise)}</div>` : ''}<div class="swipe">Swipe →</div><div class="grow"></div>`,
  stake: s => `<div class="grow"></div><div class="q">${nl(s.text)}</div><div class="grow"></div>`,
  idea: s => `<div class="grow"></div>${s.kicker ? `<div class="k">${esc(s.kicker)}</div>` : ''}<div class="h">${nl(s.title)}</div>${s.text ? `<div class="b">${nl(s.text)}</div>` : ''}${s.source ? `<div class="src">${esc(s.source)}</div>` : ''}<div class="grow"></div>`,
  recap: s => `<div class="grow"></div><div class="h">${nl(s.title || 'In short')}</div>${s.items.map((x, k) => `<div class="it"><i>${k + 1}</i><span>${nl(x)}</span></div>`).join('')}<div class="grow"></div>`,
  cta: s => `<div class="grow"></div><div class="rule"></div><div class="h">${nl(s.title)}</div>${s.text ? `<div class="b">${nl(s.text)}</div>` : ''}<div class="grow"></div>`,
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
const n = spec.slides.length;
for (let i = 0; i < n; i++) {
  const s = spec.slides[i];
  let t = (s.type === 'photo' || s.type === 'pic') ? 'pic' : s.type;
  if (t === 'pic' && !s.photo) { t = 'note'; s.quote = s.quote || s.title || ''; s.context = s.context || s.text; }
  const foot = `<div class="foot"><span>${esc(NAME)}</span>${n > 1 ? `<span class="n">${i + 1}/${n}</span>` : ''}</div>`;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body><div class="s ${t}">${T[t](s)}${foot}</div></body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const f = `${outDir}/${String(i + 1).padStart(2, '0')}.png`;
  await page.screenshot({ path: f });
  console.log(f);
}
await browser.close();
