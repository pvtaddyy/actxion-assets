// ACTXION Motion Lab - 3D world for ACTXION LAB (What If? half-time table).
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

// ---------- What If? Premier League 2026/27 stopped at half-time ----------
const GOLD = 0xffd54a, GREEN = 0x2ecc71, GREY = 0x8a93a6, LRED = 0xe0283a;
const D = EP.data;   // positions + results from facts.tsv (football-data.co.uk)
const LX = 1.05, LTOP = 2.77, STEP = .13;
const slotY = p => LTOP - (p - 1) * STEP;
const slabs = [];
for (let p = 1; p <= 20; p++) {
  const c = p === 1 ? GOLD : 0x1d2638;
  const m = new THREE.Mesh(new THREE.BoxGeometry(1.7, .1, .45), new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: p === 1 ? .45 : .25, roughness: .5, transparent: true }));
  m.position.set(LX, slotY(p), 0); m.castShadow = true; scene.add(m); slabs.push(m);
  const n = new THREE.Mesh(new THREE.PlaneGeometry(.17, .17), new THREE.MeshBasicMaterial({ map: textTex(String(p), { color: '#c9d1e0', size: 300 }), transparent: true }));
  n.position.set(LX - .98, slotY(p), .05); scene.add(n); slabs.push(n);
}
const hex = c => '#' + c.toString(16).padStart(6, '0');
function labelTex(txt, bg, fg) { return canvasTex(512, 64, (g, w, h) => { g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.fillStyle = fg; g.font = '900 50px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(txt, w / 2, h / 2 + 3); }); }
// club blocks that ride the ladder: {code, name, col, fg, track:[[t,pos,xoff]]}
const blocks = D.clubs.map(cl => { const tex = labelTex(cl.name, hex(cl.col), cl.fg);
  const mats = [0, 1, 2, 3, 4, 5].map(i => i === 4 ? new THREE.MeshStandardMaterial({ map: tex, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: .35, roughness: .4 })
    : new THREE.MeshStandardMaterial({ color: cl.col, emissive: cl.col, emissiveIntensity: .45, roughness: .4 }));
  const m = new THREE.Mesh(new THREE.BoxGeometry(1.86, .125, .55), mats); m.castShadow = true; scene.add(m); return m; });
// results towers: one cube per game (Bournemouth at half-time; Arsenal's six level games, which flip to wins)
function cube(label, res) { const col = res === 'W' ? GREEN : res === 'D' ? GREY : LRED; const tex = labelTex(label, hex(col), '#0a0f1c');
  const mats = [0, 1, 2, 3, 4, 5].map(i => i === 4 ? new THREE.MeshStandardMaterial({ map: tex, roughness: .45, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: .25 }) : new THREE.MeshStandardMaterial({ color: col, roughness: .45 }));
  const m = new THREE.Mesh(new THREE.BoxGeometry(1.3, .23, .5), mats); m.castShadow = true; scene.add(m); return m; }
const btower = D.bou.map(r => cube(r.label, r.res));
const atower = D.ars.map(r => ({ d: cube(r.ht, 'D'), w: cube(r.ft, 'W') }));
// half-time clock: a disc with a sweeping hand to 45'
const clockTex = canvasTex(512, 512, (g, w, h) => { g.fillStyle = '#f4f6fb'; g.beginPath(); g.arc(256, 256, 250, 0, Math.PI * 2); g.fill();
  g.fillStyle = 'rgba(255,213,74,.9)'; g.beginPath(); g.moveTo(256, 256); g.arc(256, 256, 236, -Math.PI / 2, Math.PI); g.fill();
  g.fillStyle = '#0a0f1c'; for (let k = 0; k < 12; k++) { const an = k / 12 * Math.PI * 2; g.save(); g.translate(256 + Math.sin(an) * 210, 256 - Math.cos(an) * 210); g.rotate(an); g.fillRect(-6, -22, 12, 44); g.restore(); }
  g.font = '900 120px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText("45'", 256, 340); });
const clock = new THREE.Group(); scene.add(clock);
const face = new THREE.Mesh(new THREE.CircleGeometry(.75, 64), new THREE.MeshStandardMaterial({ map: clockTex, emissive: 0xffffff, emissiveMap: clockTex, emissiveIntensity: .35, roughness: .5 }));
clock.add(face);
const rimM = new THREE.Mesh(new THREE.TorusGeometry(.77, .06, 12, 64), new THREE.MeshStandardMaterial({ color: 0x2b3245, metalness: .6, roughness: .3 })); clock.add(rimM);
const hand = new THREE.Mesh(new THREE.BoxGeometry(.06, .62, .03), new THREE.MeshStandardMaterial({ color: 0xe0283a, emissive: 0xe0283a, emissiveIntensity: .5 }));
hand.geometry.translate(0, .28, 0); hand.position.z = .03; clock.add(hand);
// goal pillars (to scale): Arsenal first-half 5 v second-half 10
const pillM = c => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: .35, roughness: .35 });
const pillars = [GREY, GOLD].map(c => { const m = new THREE.Mesh(new THREE.BoxGeometry(.9, 1, .9), pillM(c)); m.castShadow = true; scene.add(m); return m; });
const balls = [];
for (let i = 0; i < 15; i++) { const b = new THREE.Mesh(new THREE.SphereGeometry(.13, 20, 20), new THREE.MeshStandardMaterial({ map: ballTex, roughness: .5 })); b.castShadow = true; scene.add(b); balls.push(b); }

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
  const dk = clamp(Math.min((t - B.twist) / .25, (B.seventh - t) / .4));
  key.intensity = lerp(900, 140, dk); hemi.intensity = lerp(.55, .14, dk);
  const flare = 1 + 1.6 * Math.exp(-t * 3.5);
  floods.forEach(f => { f.material.opacity = lerp(1, .1, dk); f.scale.setScalar(9 * flare); });
  spot.intensity = dk * 340; spot.position.set(LX, 14, 3); spot.target.position.set(LX, slotY(1), 0);

  // ladder (hidden while the goal pillars stand)
  const lad = !(t >= B.ten && t < B.city) && t < B.real;
  slabs.forEach(s => s.visible = lad);
  // whistle shake
  const sh = t >= B.whistle && t < B.twist ? Math.sin(t * 46) * .035 * clamp((B.twist - t) / .5) : 0;
  D.clubs.forEach((cl, i) => { const m = blocks[i]; const tr = cl.track;
    let k = 0; while (k < tr.length - 1 && tr[k + 1][0] <= t) k++;
    const a = tr[Math.max(0, k - 1)], b = tr[k]; const p = k === 0 ? 1 : easeInOut((t - b[0]) / .7);
    const y = lerp(slotY(a[1]), slotY(b[1]), p), x = lerp(a[2], b[2], p);
    m.visible = lad && x < 3.5; m.position.set(LX + x + sh * (i % 2 ? 1 : -1), y, .08);
    m.rotation.x = (t >= B.whistle && t < B.twist) ? Math.sin(t * 9 + i) * .25 * clamp((t - B.whistle) / .3) : 0;
    const glow = (cl.code === 'bou' && t >= B.twist) || (cl.code === 'ars' && t < B.took) ? .7 + .25 * Math.sin(t * 6) : .45;
    m.material.forEach((mm, j) => { if (j !== 4) mm.emissiveIntensity = glow; }); });

  // clock: sweeps to 45' then the whistle
  const cv = win(t, B.took, B.twist, .3); clock.visible = cv > 0.01;
  clock.position.set(-1.25, 1.35 + (1 - easeOut((t - B.took) / .5)) * 3, 0); clock.scale.setScalar(.6 + .4 * cv);
  hand.rotation.z = -lerp(0, Math.PI * 1.5, easeInOut((t - B.took - .3) / Math.max(.5, B.whistle - B.took - .3)));

  // Bournemouth's half-time results tower
  btower.forEach((m, i) => { const a = D.bou[i].at; const p = bounce((t - a) / .4);
    m.visible = t >= a && t < B.ars; m.position.set(-1.35, lerp(4.0, .12 + i * .24, p), 0); m.rotation.y = (1 - clamp((t - a) / .4)) * 1.2; });
  // Arsenal's six level games: grey at half-time, flip to green wins
  atower.forEach((c, i) => { const a = D.ars[i].at; const p = bounce((t - a) / .4);
    const vis = t >= a && t < B.ten; const y = lerp(4.0, .12 + i * .24, p);
    const f = clamp((t - B.allsix - i * .12) / .3);
    c.d.visible = vis && f < .5; c.w.visible = vis && f >= .5;
    for (const m of [c.d, c.w]) { m.position.set(-1.35, y, 0); m.rotation.x = f * Math.PI * 2; m.rotation.y = (1 - clamp((t - a) / .4)) * 1.2; } });
  if (t >= B.ars && t < B.ten) showCrest('ars', -1.35, .12 + Math.min(6, Math.max(0, D.ars.filter(r => t >= r.at).length)) * .24 + .25, .1, .4, win(t, B.ars + .2, B.ten));
  if (t >= B.seven && t < B.ars) showCrest('bou', -1.35, .12 + D.bou.filter(r => t >= r.at).length * .24 + .25, .1, .4, win(t, B.seven + .2, B.ars));

  // goal pillars: 5 first-half v 10 second-half, balls pour in
  const pv = t >= B.ten && t < B.city;
  const U = .26;
  const vals = [5, 10];
  pillars.forEach((m, i) => { m.visible = pv; const g = easeOut((t - (B.ten + (i ? .6 : 0))) / .9);
    const h = Math.max(.001, vals[i] * U * g * .5); m.scale.y = h; m.position.set(i ? 1.0 : -1.0, h / 2, 0); });
  balls.forEach((b, j) => { const i = j < 5 ? 0 : 1, n = j < 5 ? j : j - 5; const a = B.ten + (i ? .6 : 0) + n * .09;
    const top = vals[i] * U * .5 * easeOut((t - (B.ten + (i ? .6 : 0))) / .9);
    b.visible = pv && t >= a; const p = bounce((t - a) / .5);
    b.position.set((i ? 1.0 : -1.0) + (n % 2 ? .18 : -.18), lerp(6, top + .14 + (n % 2) * .02, p), .55 - (n % 3) * .05); b.rotation.x = t * 3 + j; });
  if (pv) showCrest("ars", 0, .75, 0, .5, win(t, B.ten + .4, B.city));

  // real v half-time: two crests on gold plinths
  if (t >= B.real && t < B.ask) { showCrest('ars', -1.0, 1.25, .2, .9, win(t, B.real + .1, B.ask));
    if (t >= B.htt) showCrest('bou', 1.0, 1.25, .2, .9, win(t, B.htt + .1, B.ask)); }
  renderer.render(scene, camera);
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
const ready = Promise.all(loads).then(() => render(0));
window.__hf.buildReady.world = ready;
window.addEventListener('hf-seek', e => render(e.detail.time));
ready.then(() => render(0));
