// ACTXION Motion Lab - 3D world for ACTXION LAB (Head to Head: Kane v Yamal).
// Pure function of time: render(t) draws the frame for t seconds. No clocks, no Math.random.
import * as THREE from './lib/three.module.js';

const EP = window.EP;           // beats, colours, crest list, data (injected by build.py)
const B = EP.beats;
const W = 1080, H = 1920;

// ---------- helpers ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, p) => a + (b - a) * p;
const easeOut = p => 1 - Math.pow(1 - clamp(p), 3);
const easeInOut = p => { p = clamp(p); return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; };
const bounce = p => { p = clamp(p); const n = 7.5625, d = 2.75;
  if (p < 1 / d) return n * p * p; if (p < 2 / d) return n * (p -= 1.5 / d) * p + .75;
  if (p < 2.5 / d) return n * (p -= 2.25 / d) * p + .9375; return n * (p -= 2.625 / d) * p + .984375; };
const hash = i => { let x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const win = (t, a, b, fade = .35) => clamp(Math.min((t - a) / fade, (b - t) / fade)); // 0..1 visibility

// ---------- renderer ----------
const canvas = document.getElementById('world');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(EP.colors.sky);
scene.fog = new THREE.Fog(EP.colors.sky, 18, 70);
const camera = new THREE.PerspectiveCamera(42, W / H, 0.1, 200);

// lights
const hemi = new THREE.HemisphereLight(0x8fb4ff, 0x0b1a0f, 0.55); scene.add(hemi);
const key = new THREE.SpotLight(0xfff1d6, 900, 60, 0.55, 0.5, 1.6);
key.position.set(4, 18, 10); key.castShadow = true; key.shadow.mapSize.set(1024, 1024); scene.add(key); scene.add(key.target);
const rim = new THREE.DirectionalLight(0x6fa8ff, 1.4); rim.position.set(-8, 6, -10); scene.add(rim);
const spot = new THREE.SpotLight(0xffffff, 0, 40, 0.22, 0.7, 1.6); spot.position.set(0, 16, 2); scene.add(spot); scene.add(spot.target);

// ---------- textures (canvas, deterministic) ----------
function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
const pitchTex = canvasTex(1024, 1024, (g, w, h) => {
  for (let i = 0; i < 12; i++) { g.fillStyle = i % 2 ? '#1c6b34' : '#21783a'; g.fillRect(0, i * h / 12, w, h / 12); }
  g.strokeStyle = 'rgba(255,255,255,.85)'; g.lineWidth = 6;
  g.strokeRect(60, 60, w - 120, h - 120); g.beginPath(); g.moveTo(60, h / 2); g.lineTo(w - 60, h / 2); g.stroke();
  g.beginPath(); g.arc(w / 2, h / 2, 110, 0, Math.PI * 2); g.stroke();
  g.strokeRect(w / 2 - 220, 60, 440, 170); g.strokeRect(w / 2 - 220, h - 230, 440, 170);
});
const crowdTex = canvasTex(2048, 512, (g, w, h) => {
  g.fillStyle = '#0a0f1c'; g.fillRect(0, 0, w, h);
  const cols = ['#6CABDD', '#ffffff', '#1c2c5b', '#c8102e', '#f4f4f4', '#ffd54a', '#7a263a', '#132257'];
  let i = 0; for (let y = 8; y < h; y += 14) for (let x = 6; x < w; x += 11) { i++;
    g.fillStyle = cols[Math.floor(hash(i) * cols.length)]; g.globalAlpha = .35 + hash(i * 3) * .55;
    g.fillRect(x + hash(i * 7) * 3, y, 6, 8); }
  g.globalAlpha = 1;
});
crowdTex.wrapS = THREE.RepeatWrapping; crowdTex.repeat.set(3, 1);
const ballTex = canvasTex(256, 128, (g, w, h) => {
  g.fillStyle = '#f7f7f7'; g.fillRect(0, 0, w, h); g.fillStyle = '#111';
  for (let k = 0; k < 9; k++) { const x = (k % 3) * 90 + 40 + (Math.floor(k / 3) % 2) * 45, y = Math.floor(k / 3) * 45 + 20;
    g.beginPath(); for (let a = 0; a < 5; a++) { const an = a / 5 * Math.PI * 2; g.lineTo(x + Math.cos(an) * 15, y + Math.sin(an) * 15); } g.fill(); }
});
function textTex(txt, opts = {}) { return canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = opts.bg || 'rgba(0,0,0,0)'; g.fillRect(0, 0, w, h);
  g.fillStyle = opts.color || '#fff'; g.font = `900 ${opts.size || 300}px Inter, Arial`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(txt, w / 2, h / 2 + 10); }); }

// ---------- stadium ----------
const world = new THREE.Group(); scene.add(world);
const pitch = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), new THREE.MeshStandardMaterial({ map: pitchTex, roughness: .9 }));
pitch.rotation.x = -Math.PI / 2; pitch.receiveShadow = true; world.add(pitch);
const outer = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshStandardMaterial({ color: 0x0c2414, roughness: 1 }));
outer.rotation.x = -Math.PI / 2; outer.position.y = -0.02; world.add(outer);
for (let s = 0; s < 4; s++) {           // four tilted stands
  const st = new THREE.Mesh(new THREE.PlaneGeometry(52, 14), new THREE.MeshStandardMaterial({ map: crowdTex, roughness: 1, emissive: 0x111827, emissiveMap: crowdTex, emissiveIntensity: .55 }));
  const a = s * Math.PI / 2; st.position.set(Math.sin(a) * 27, 6, Math.cos(a) * 27); st.lookAt(0, 0, 0); st.rotateX(-0.45); world.add(st);
}
const glowTex = canvasTex(256, 256, (g, w, h) => { const r = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.25, 'rgba(255,245,220,.6)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); });
const floods = [];
for (let s = 0; s < 4; s++) {           // floodlight towers
  const a = Math.PI / 4 + s * Math.PI / 2, x = Math.sin(a) * 30, z = Math.cos(a) * 30;
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(.25, .35, 26), new THREE.MeshStandardMaterial({ color: 0x2b3245 })); pole.position.set(x, 13, z); world.add(pole);
  const g = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: 0xfff3dc, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }));
  g.position.set(x, 26.5, z); g.scale.set(9, 9, 1); world.add(g); floods.push(g);
}

// ---------- The Table: Manchester United, Premier League 2026/27 ----------
const RED = 0xda291c, GOLD = 0xffd54a, GREEN = 0x2ecc71, GREY = 0x8a93a6, LRED = 0xe0283a;
const D = EP.data;   // positions + results from united_by_matchday.tsv (football-data.co.uk)
// league ladder: 20 slabs, 1st at the top
const LX = 1.05, LTOP = 2.77, STEP = .13;
const slotY = p => LTOP - (p - 1) * STEP;
const slabs = [];
for (let p = 1; p <= 20; p++) {
  const c = p === 1 ? GOLD : p >= 18 ? 0x7a1622 : 0x1d2638;
  const m = new THREE.Mesh(new THREE.BoxGeometry(1.7, .1, .45), new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: p === 1 ? .45 : .25, roughness: .5, transparent: true }));
  m.position.set(LX, slotY(p), 0); m.castShadow = true; scene.add(m); slabs.push(m);
  const n = new THREE.Mesh(new THREE.PlaneGeometry(.17, .17), new THREE.MeshBasicMaterial({ map: textTex(String(p), { color: '#c9d1e0', size: 300 }), transparent: true }));
  n.position.set(LX - .98, slotY(p), .05); scene.add(n); slabs.push(n);
}
// United block that rides the ladder, with a position label
const ublock = new THREE.Mesh(new THREE.BoxGeometry(1.86, .15, .55), new THREE.MeshStandardMaterial({ color: RED, emissive: RED, emissiveIntensity: .6, roughness: .35 }));
ublock.castShadow = true; scene.add(ublock);
const posTex = {}; const posLab = new THREE.Mesh(new THREE.PlaneGeometry(.5, .5), new THREE.MeshBasicMaterial({ transparent: true }));
scene.add(posLab);
const ord = n => n + (n % 10 === 1 && n !== 11 ? 'ST' : n % 10 === 2 && n !== 12 ? 'ND' : n % 10 === 3 && n !== 13 ? 'RD' : 'TH');
function setPos(n) { if (!posTex[n]) posTex[n] = textTex(ord(n), { color: '#ffd54a', size: 190 }); posLab.material.map = posTex[n]; posLab.material.needsUpdate = true; }
// results tower: one cube per game, stacked in the order the voice reads them
const tower = D.tower.map((r, i) => { const col = r.res === 'W' ? GREEN : r.res === 'D' ? GREY : LRED;
  const tex = canvasTex(512, 96, (g, w, h) => { g.fillStyle = '#' + col.toString(16).padStart(6, '0'); g.fillRect(0, 0, w, h);
    g.fillStyle = '#0a0f1c'; g.font = '900 72px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(r.label, w / 2, h / 2 + 3); });
  const mats = [new THREE.MeshStandardMaterial({ color: col, roughness: .45 }), new THREE.MeshStandardMaterial({ color: col, roughness: .45 }),
    new THREE.MeshStandardMaterial({ color: col, roughness: .45 }), new THREE.MeshStandardMaterial({ color: col, roughness: .45 }),
    new THREE.MeshStandardMaterial({ map: tex, roughness: .45, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: .25 }), new THREE.MeshStandardMaterial({ color: col, roughness: .45 })];
  const m = new THREE.Mesh(new THREE.BoxGeometry(1.3, .23, .5), mats); m.castShadow = true; scene.add(m); return m; });
// points pillars (to scale)
const pillM = c => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: .35, roughness: .35 });
const pillars = [RED, GOLD].map(c => { const m = new THREE.Mesh(new THREE.BoxGeometry(.9, 1, .9), pillM(c)); m.castShadow = true; scene.add(m); return m; });
// the new manager: a faceless figure in a dark coat
function figure(coat, legs, skinC) {
  const f = new THREE.Group(), m = c => new THREE.MeshStandardMaterial({ color: c, roughness: .6 });
  const add = (geo, mat, x, y, z) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = true; f.add(o); return o; };
  add(new THREE.CapsuleGeometry(.13, .62, 6, 12), m(legs), -.16, .45, 0); add(new THREE.CapsuleGeometry(.13, .62, 6, 12), m(legs), .16, .45, 0);
  add(new THREE.CapsuleGeometry(.38, .9, 8, 16), m(coat), 0, 1.5, 0);
  add(new THREE.CapsuleGeometry(.1, .66, 6, 12), m(coat), -.5, 1.55, 0).rotation.z = .12;
  add(new THREE.CapsuleGeometry(.1, .66, 6, 12), m(coat), .5, 1.55, 0).rotation.z = -.12;
  add(new THREE.SphereGeometry(.27, 24, 24), m(skinC), 0, 2.36, 0);
  add(new THREE.SphereGeometry(.29, 24, 24, 0, Math.PI * 2, 0, Math.PI / 2.2), m(0x4a4a4a), 0, 2.4, -.02);
  scene.add(f); return f; }
const boss = figure(0x151821, 0x151821, 0xd9b08c);

// crests (keep aspect)
const loader = new THREE.TextureLoader(); const crestTex = {}; const loads = [];
for (const k of EP.crests) loads.push(new Promise(r => loader.load(EP.crestData[k], t => { t.colorSpace = THREE.SRGBColorSpace; crestTex[k] = t; r(); }, undefined, () => r())));
const sprites = {}; const used = {};
function showCrest(k, x, y, z, size, vis) { if (!sprites[k] && crestTex[k]) { sprites[k] = new THREE.Sprite(new THREE.SpriteMaterial({ map: crestTex[k], transparent: true, depthWrite: false })); sprites[k].visible = false; scene.add(sprites[k]); }
  const s = sprites[k]; if (!s || vis <= 0.01) return; const im = crestTex[k].image, asp = im.width / im.height;
  s.visible = true; s.material.opacity = vis; s.scale.set(size * Math.min(1, asp), size / Math.max(1, asp), 1); s.position.set(x, y, z); }

// ---------- camera ----------
const cams = EP.cams.map(c => ({ t: c.t, p: new THREE.Vector3(...c.p), l: new THREE.Vector3(...c.l), fov: c.fov || 42, move: c.move || 1.1 }));
function camAt(t) { let i = 0; while (i < cams.length - 1 && cams[i + 1].t <= t) i++;
  const a = cams[Math.max(0, i - 1)], b = cams[i];
  const p = i === 0 ? 1 : easeInOut(clamp((t - b.t) / b.move));
  camera.position.copy(a.p).lerp(b.p, p); const look = a.l.clone().lerp(b.l, p);
  camera.fov = lerp(a.fov, b.fov, p); camera.updateProjectionMatrix();
  camera.position.x += Math.sin(t * .7) * .05; camera.position.y += Math.sin(t * .9 + 1) * .04; camera.lookAt(look); }

function render(t) {
  for (const k in sprites) sprites[k].visible = false;
  camAt(t);
  const dark = clamp(Math.min((t - B.twist) / .25, (B.since - t) / .4));
  const dark2 = clamp(Math.min((t - B.carrick) / .3, (B.first - t) / .4));
  const dk = Math.max(dark, dark2);
  key.intensity = lerp(900, 140, dk); hemi.intensity = lerp(.55, .14, dk);
  const flare = 1 + 1.6 * Math.exp(-t * 3.5);
  floods.forEach(f => { f.material.opacity = lerp(1, .1, dk); f.scale.setScalar(9 * flare); });
  spot.intensity = dk * 340;
  if (dark > 0) { spot.position.set(-1.4, 14, 3); spot.target.position.set(-1.4, 0, 0); } else { spot.position.set(0, 14, 3); spot.target.position.set(0, 0, 0); }

  // ladder + United block (hook to the 18th)
  const lad = t < B.points && dark < .5;
  slabs.forEach(s => s.visible = lad);
  const zone = t >= B.eighteenth ? .45 + .35 * Math.sin((t - B.eighteenth) * 9) : .25;
  for (let p = 18; p <= 20; p++) slabs[(p - 1) * 2].material.emissiveIntensity = zone;
  // position track: [time, position]
  const P = D.track; let pos = P[0][1], prev = P[0][1], tt = 0;
  for (const [a, p] of P) if (t >= a) { prev = pos; pos = p; tt = a; }
  const mv = easeInOut((t - tt) / .7);
  const shake = t >= B.watch && t < B.g1 ? Math.sin(t * 40) * .03 : 0;
  const y = lerp(slotY(prev), slotY(pos), mv);
  ublock.visible = posLab.visible = lad;
  ublock.position.set(LX + shake, y, .08); posLab.position.set(LX + 1.17, y, .3);
  setPos(mv > .5 ? pos : prev);
  if (lad) showCrest('mun', LX - .2, y, .45, .3, 1);

  // results tower
  tower.forEach((m, i) => { const a = D.tower[i].at; const p = bounce((t - a) / .45);
    m.visible = t >= a && t < B.points; m.position.set(-1.35, lerp(4.0, .12 + i * .24, p), 0); m.rotation.y = (1 - clamp((t - a) / .45)) * 1.2; });

  // points pillars: United 8 v Arsenal 27, then Liverpool 18 v United 8
  const pv = t >= B.points && t < B.ask;
  const U = 1.6 / 27;
  const isLiv = t >= B.first;
  const vals = isLiv ? [8, 18] : [8, 27];
  pillars.forEach((m, i) => { m.visible = pv; const g = easeOut((t - (i ? (isLiv ? B.first + .3 : B.arsenal) : (isLiv ? B.first : B.points))) / .9);
    const h = Math.max(.001, vals[i] * U * g); m.scale.y = h; m.position.set(i ? 1.0 : -1.0, h / 2, 0);
    m.material.color.setHex(i ? (isLiv ? 0xc8102e : GOLD) : RED); m.material.emissive.setHex(i ? (isLiv ? 0xc8102e : GOLD) : RED); });
  if (pv && t < B.carrick) { showCrest('mun', -1.0, vals[0] * U + .32, 0, .45, win(t, B.points + .4, B.carrick));
    if (t >= B.arsenal) showCrest('ars', 1.0, 27 * U * easeOut((t - B.arsenal) / .9) + .32, 0, .45, win(t, B.arsenal + .3, B.carrick)); }
  if (t >= B.carrick && t < B.first) pillars.forEach(m => m.visible = false);
  if (t >= B.first && t < B.ask) { showCrest('mun', -1.0, 8 * U * easeOut((t - B.first) / .9) + .32, 0, .45, win(t, B.first + .3, B.ask));
    showCrest('liv', 1.0, 18 * U * easeOut((t - B.first - .3) / .9) + .32, 0, .45, win(t, B.first + .5, B.ask)); }

  // the new manager walks in under the spotlight
  boss.visible = t >= B.carrick && t < B.first;
  const wk = easeOut((t - B.poch) / 1.4);
  boss.position.set(lerp(-3.2, 0, t < B.poch ? 0 : wk), 0, 0); boss.rotation.y = lerp(1.2, .15, wk);
  if (t < B.poch) boss.position.x = -3.2;

  // ask: both crests
  
  renderer.render(scene, camera);
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
const ready = Promise.all(loads).then(() => render(0));
window.__hf.buildReady.world = ready;
window.addEventListener('hf-seek', e => render(e.detail.time));
ready.then(() => render(0));
