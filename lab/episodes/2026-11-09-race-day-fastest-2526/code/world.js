// ACTXION Motion Lab - 3D world for "Race Day" episodes.
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

// ---------- running figure (stylised, no face) ----------
function figure(k) {
  const f = new THREE.Group(), body = new THREE.Group(); f.add(body);
  const mats = []; const m = c => { const x = new THREE.MeshStandardMaterial({ color: c, roughness: .55, transparent: true }); mats.push(x); return x; };
  const skin = m(k.skin);
  const mesh = (geo, mat, x, y, z, parent = body) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = true; parent.add(o); return o; };
  const limb = (x, y, len, r, top, bot) => { const g = new THREE.Group(); g.position.set(x, y, 0); body.add(g);
    mesh(new THREE.CapsuleGeometry(r, len * .5, 6, 12), top, 0, -len * .3, 0, g);
    mesh(new THREE.CapsuleGeometry(r * .92, len * .45, 6, 12), bot, 0, -len * .72, 0, g); return g; };
  const legL = limb(-.17, .86, .95, .13, skin, m(k.socks)), legR = limb(.17, .86, .95, .13, skin, m(k.socks));
  mesh(new THREE.CylinderGeometry(.36, .32, .38, 16), m(k.shorts), 0, 1.0, 0);
  const torso = mesh(new THREE.CapsuleGeometry(.36, .62, 8, 16), m(k.shirt), 0, 1.62, 0);
  if (k.num) { const np = new THREE.Mesh(new THREE.PlaneGeometry(.42, .42), new THREE.MeshBasicMaterial({ map: textTex(k.num, { color: '#ffffff' }), transparent: true }));
    np.position.set(0, 1.62, .37); body.add(np); mats.push(np.material); }
  const sl = m(k.sleeves || k.shirt);
  const armL = limb(-.5, 2.0, .78, .1, sl, skin), armR = limb(.5, 2.0, .78, .1, sl, skin);
  mesh(new THREE.SphereGeometry(.28, 24, 24), skin, 0, 2.38, 0);
  mesh(new THREE.SphereGeometry(.3, 24, 24, 0, Math.PI * 2, 0, Math.PI / 2.1), m(k.hair), 0, 2.42, -.02);
  if (k.bun) mesh(new THREE.SphereGeometry(.12, 16, 16), m(k.hair), 0, 2.62, -.2);
  f.userData = { body, legL, legR, armL, armR, mats, torso };
  scene.add(f); return f;
}
// pose: phase = stride phase (radians), amp 0..1 (0 = standing), lean forward
function pose(f, phase, amp) { const u = f.userData, s = Math.sin(phase);
  u.legL.rotation.x = s * .95 * amp; u.legR.rotation.x = -s * .95 * amp;
  u.armL.rotation.x = -s * 1.0 * amp; u.armR.rotation.x = s * 1.0 * amp;
  u.armL.rotation.z = -.18 * (1 - amp) ; u.armR.rotation.z = .18 * (1 - amp);
  u.body.rotation.x = .28 * amp; u.body.position.y = Math.abs(Math.cos(phase)) * .14 * amp; }
function setOpacity(f, o) { f.userData.mats.forEach(m => { m.opacity = o; m.depthWrite = o > .95; }); f.visible = o > .01; }

const KIT = EP.kits;
const R = { haa: figure(KIT.haa), fri: figure(KIT.fri), mar: figure(KIT.mar), tch: figure(KIT.tch), tch2: figure(KIT.tch), vdv: figure(KIT.vdv) };
const ghostMat = R.tch2.userData.mats; ghostMat.forEach(m => m.emissive = new THREE.Color(0x5a3a00));
const shadowFig = figure({ shirt: '#0b0f1a', shorts: '#0b0f1a', socks: '#0b0f1a', hair: '#0b0f1a', skin: '#0b0f1a', num: '' });
shadowFig.userData.mats.forEach(m => { m.emissive = new THREE.Color(0x0a1830); m.metalness = .3; });

// ---------- the track: 4 lanes across the pitch, start x=-12, finish x=+8 ----------
const LANES = [2.4, .8, -.8, -2.4];      // lane 1 nearest the camera
const START = -12, FINISH = 8, DIST = FINISH - START;
const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .85 });
const track = new THREE.Group(); scene.add(track);
const lane = new THREE.Mesh(new THREE.PlaneGeometry(34, 6.4), new THREE.MeshStandardMaterial({ color: 0x8a2b1f, roughness: .95 }));
lane.rotation.x = -Math.PI / 2; lane.position.set(-2, .005, 0); lane.receiveShadow = true; track.add(lane);
for (let i = 0; i <= 4; i++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(34, .06), lineMat); l.rotation.x = -Math.PI / 2; l.position.set(-2, .012, 3.2 - i * 1.6); track.add(l); }
const chk = canvasTex(64, 512, (g, w, h) => { for (let y = 0; y < 32; y++) for (let x = 0; x < 4; x++) { g.fillStyle = (x + y) % 2 ? '#111' : '#fff'; g.fillRect(x * 16, y * 16, 16, 16); } });
const fin = new THREE.Mesh(new THREE.PlaneGeometry(.5, 6.4), new THREE.MeshBasicMaterial({ map: chk })); fin.rotation.x = -Math.PI / 2; fin.position.set(FINISH, .014, 0); track.add(fin);
const st = new THREE.Mesh(new THREE.PlaneGeometry(.12, 6.4), lineMat); st.rotation.x = -Math.PI / 2; st.position.set(START, .014, 0); track.add(st);
for (let i = 0; i < 4; i++) { const n = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: textTex(String(i + 1), { color: '#ffffff', size: 330 }), transparent: true, opacity: .8 }));
  n.rotation.x = -Math.PI / 2; n.rotation.z = -Math.PI / 2; n.position.set(START - 1.0, .015, LANES[i]); track.add(n); }
// finish gate posts with lights
const gateMat = new THREE.MeshStandardMaterial({ color: 0xffd54a, emissive: 0xffd54a, emissiveIntensity: .6 });
[-3.3, 3.3].forEach(z => { const p = new THREE.Mesh(new THREE.BoxGeometry(.14, 3.2, .14), gateMat); p.position.set(FINISH, 1.6, z); track.add(p); });
const bar = new THREE.Mesh(new THREE.BoxGeometry(.14, .14, 6.74), gateMat); bar.position.set(FINISH, 3.2, 0); track.add(bar);

// ---------- races ----------
// distance covered: accelerate for the first 25 %, then flat out; after the line, ease to a stop 3 m on
function runX(t, t0, dur, freeze = false) { const p = (t - t0) / dur;
  if (p <= 0) return START; if (p < 1) { const a = .25; return START + DIST * (p < a ? (p * p) / (2 * a) / (1 - a / 2) : (p - a / 2) / (1 - a / 2)); }
  if (freeze) return FINISH; return FINISH + 1.6 * easeOut((t - t0 - dur) / .8); }
function place(f, t, t0, dur, laneI, opts = {}) {
  const x = runX(t, t0, dur, opts.freeze) + (opts.dx || 0), x2 = runX(t + .02, t0, dur, opts.freeze) + (opts.dx || 0);
  const v = (x2 - x) / .02; f.position.set(x, 0, LANES[laneI]); f.rotation.y = Math.PI / 2;
  const amp = opts.freeze && t > t0 + dur ? 1 : clamp(v / 6); pose(f, (x - START) * 1.35 + laneI, amp); return x; }
const DUR = s => 2.3 * (37.3 / s);       // run time scales with top speed

// pillars for the all-time podium
const POD = [{ k: 'wal', v: 37.31, c: '#6CABDD', crest: 'mci', x: -1.6 }, { k: 'vdv', v: 37.38, c: '#ffffff', crest: 'tot', x: 0 }, { k: 'tch', v: 37.30, c: '#FDB913', crest: 'wol', x: 1.6 }];
const pillars = POD.map(p => { const m = new THREE.Mesh(new THREE.BoxGeometry(1.1, 1, 1.1), new THREE.MeshStandardMaterial({ color: p.c, emissive: p.c, emissiveIntensity: .22, roughness: .35 }));
  m.castShadow = true; scene.add(m); return m; });

// crests as sprites
const loader = new THREE.TextureLoader(); const crestTex = {}; const loads = [];
for (const k of EP.crests) loads.push(new Promise(r => loader.load(EP.crestData[k], t => { t.colorSpace = THREE.SRGBColorSpace; crestTex[k] = t; r(); }, undefined, () => r())));
const sprites = {};
function crest(k) { if (sprites[k] && !sprites[k].material.map && crestTex[k]) { scene.remove(sprites[k]); delete sprites[k]; }
  if (!sprites[k]) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: crestTex[k], transparent: true, depthWrite: false }));
  const img = crestTex[k] && crestTex[k].image; const ar = img ? img.width / img.height : 1; s.userData.ar = ar; scene.add(s); sprites[k] = s; } return sprites[k]; }
function showCrest(k, x, y, z, size, vis) { const s = crest(k); s.visible = vis > 0.01; s.material.opacity = vis; const ar = s.userData.ar || 1;
  s.scale.set(size * Math.min(1, ar), size * Math.min(1, 1 / ar), 1); s.position.set(x, y, z); }

const disc = new THREE.Sprite(new THREE.SpriteMaterial({ map: canvasTex(128, 128, (g) => { g.fillStyle = '#f2f4f8'; g.beginPath(); g.arc(64, 64, 62, 0, 7); g.fill(); }), transparent: true, depthWrite: false }));
disc.scale.set(1.0, 1.0, 1); disc.visible = false; scene.add(disc);
// ---------- camera ----------
const V = (x, y, z) => new THREE.Vector3(x, y, z);
let camPrev = null;
function setCam(p, l, fov) { camera.position.copy(p); camera.lookAt(l); camera.fov = fov; camera.updateProjectionMatrix(); }
// side tracking shot on a runner at x
const track3 = (x, laneZ, back = 16, h = 3.0) => [V(x - .8, h, laneZ + back), V(x + .6, 1.2, laneZ)];

// ---------- the frame ----------
function render(t) {
  for (const k in sprites) sprites[k].visible = false;
  Object.values(R).forEach(f => setOpacity(f, 0)); shadowFig.visible = false;
  pillars.forEach(m => m.visible = false); disc.visible = false;
  track.visible = true;
  // lights: dark hook, lights up on Race Day; blackout on the twist, spotlight on Tchatchoua and the ask
  const lightsOn = easeOut((t - B.ctx) / .6);
  const dark = Math.max(1 - lightsOn, clamp(Math.min((t - B.twist) / .2, (B.tNum - t) / .5)) * .85, clamp((t - B.ask) / .4) * .7);
  key.intensity = lerp(900, 90, dark); hemi.intensity = lerp(.55, .1, dark);
  floods.forEach((f, i) => { const on = clamp((t - B.ctx - i * .12) / .1); const off = clamp(Math.min((t - B.twist - i * .15) / .12, (B.tNum - t) / .4));
    f.material.opacity = t < B.ctx ? .08 : lerp(1, .06, off) * on; f.scale.setScalar(9 * (1 + 1.4 * Math.exp(-(t - B.ctx) * 4) * (t > B.ctx))); });
  spot.intensity = 0;
  let cp, cl, fov = 42;

  if (t < B.ctx) {                                   // HOOK: a dark silhouette sprinting in slow motion under one light
    shadowFig.visible = true; shadowFig.position.set(0, 0, 0); shadowFig.rotation.y = Math.PI / 2 - .5; pose(shadowFig, t * 4.2, 1);
    spot.intensity = 380; spot.position.set(0, 14, 3); spot.target.position.set(0, 1, 0);
    const a = -.5 + t * .12; cp = V(Math.sin(a) * 6.5, 1.9 + t * .05, Math.cos(a) * 6.5); cl = V(0, 1.5, 0); fov = 40;
    const dive = easeOut(t / 1.6); cp.lerp(V(0, 9, 16), 1 - dive);
  } else if (t < B.l1) {                             // RACE DAY card: wide shot of the empty track, lights on
    const p = easeInOut((t - B.ctx) / (B.l1 - B.ctx)); cp = V(lerp(-6, -10, p), lerp(9, 4, p), 13); cl = V(-8, 0, 0); fov = 46;
    ['haa', 'fri', 'mar', 'tch'].forEach((k, i) => { setOpacity(R[k], 1); R[k].position.set(START, 0, LANES[i]); R[k].rotation.y = Math.PI / 2; pose(R[k], 0, 0); });
  } else if (t < B.wins) {                           // LANE 1 Haaland, then LANE 2 Frimpong
    const t1 = B.l1 + .35, t2 = B.l2 + .35;
    setOpacity(R.haa, 1); const xh = place(R.haa, t, t1, DUR(36.20), 0);
    if (t >= B.l2 - .2) { setOpacity(R.fri, 1); const xf = place(R.fri, t, t2, DUR(36.18), 1); [cp, cl] = track3(xf, LANES[1]); }
    else [cp, cl] = track3(xh, LANES[0]);
  } else if (t < B.l3) {                             // PHOTO FINISH: both together, freeze on the line
    const t0 = B.wins - 1.2, d = 2.4; setOpacity(R.haa, 1); setOpacity(R.fri, 1);
    const xh = place(R.haa, t, t0, d, 0, { freeze: true, dx: .16 }); place(R.fri, t, t0, d, 1, { freeze: true, dx: -.16 });
    const p = easeInOut((t - (t0 + d)) / .8);
    cp = V(lerp(xh - .8, FINISH + .3, p), lerp(3.0, 9.5, p), lerp(LANES[0] + 16, LANES[0] + 7.5, p)); cl = V(lerp(xh + .6, FINISH, p), lerp(1.2, 0, p), lerp(LANES[0], -1.0, p)); fov = 42;
  } else if (t < B.twist) {                          // LANE 3 Martinelli
    const t3 = B.l3 + .35; setOpacity(R.mar, 1); const xm = place(R.mar, t, t3, DUR(36.74), 2); [cp, cl] = track3(xm, LANES[2]);
  } else if (t < B.tch) {                            // TWIST: blackout, track in the dark
    const p = (t - B.twist) / (B.tch - B.twist); cp = V(-4, lerp(5, 3, p), 12); cl = V(-6, .5, 0); fov = 44;
  } else if (t < B.even) {                           // TCHATCHOUA in lane 4 runs away from all three
    const t0 = B.tch + .6;
    const rs = [['haa', 1, 36.20], ['fri', 2, 36.18], ['mar', 3, 36.74], ['tch', 0, 37.30]];
    let xt = 0; rs.forEach(([k, li, s]) => { setOpacity(R[k], k === 'tch' ? 1 : .55); const x = place(R[k], t, t0, 2.6 * Math.pow(37.3 / s, 3), li); if (k === 'tch') xt = x; });
    spot.intensity = 300 * clamp((B.tNum - t) / .5 + .3); spot.position.set(xt, 12, LANES[0] + 2); spot.target.position.set(xt, 0, LANES[0]);
    [cp, cl] = track3(xt, LANES[0]);
  } else if (t < B.since) {                          // his 2nd best (ghost) v Martinelli
    const t0 = B.even + .3; setOpacity(R.mar, 1); setOpacity(R.tch2, .62);
    place(R.mar, t, t0, 2.6 * Math.pow(37.3 / 36.74, 3), 2); const xg = place(R.tch2, t, t0, 2.6 * Math.pow(37.3 / 36.97, 3), 1);
    [cp, cl] = track3(xg, (LANES[1] + LANES[2]) / 2); 
  } else if (t < B.ask) {                            // all-time podium
    track.visible = false;
    POD.forEach((p, i) => { const m = pillars[i], appear = i === 1 ? B.vdv : (i === 0 ? B.walker : B.since + .2);
      const pr = easeOut((t - appear) / .8), h = (p.v - 35.5) * 1.3 * pr + .01; m.visible = t >= appear - .05; m.scale.y = h; m.position.set(p.x, h / 2, 0);
      showCrest(p.crest, p.x, h + .6, .05, .8, clamp((t - appear - .3) / .3));
      if (p.crest === 'tot') { disc.visible = t >= appear + .3; disc.position.set(p.x, h + .6, 0); } });
    const p = easeInOut((t - B.since) / 1.2); cp = V(0, lerp(6, 3.0, p), lerp(16, 13, p)); cl = V(0, 1.4, 0); fov = 44;
  } else {                                          // ASK: the two side by side, facing us, under the light
    track.visible = true; setOpacity(R.tch, 1); setOpacity(R.vdv, 1);
    R.tch.position.set(-1.1, 0, 1); R.vdv.position.set(1.1, 0, 1);
    R.tch.rotation.y = .25 + Math.sin(t * .6) * .08; R.vdv.rotation.y = -.25 - Math.sin(t * .6) * .08; pose(R.tch, 0, 0); pose(R.vdv, 0, 0);
    spot.intensity = 320; spot.position.set(0, 14, 5); spot.target.position.set(0, 1, 1);
    const p = easeOut((t - B.ask) / 1.2); cp = V(0, 1.8, lerp(13, 10.5, p)); cl = V(0, 1.5, 1); fov = 40;
  }
  camera.position.copy(cp); camera.position.x += Math.sin(t * .7) * .04; camera.position.y += Math.sin(t * .9 + 1) * .03;
  camera.fov = fov; camera.updateProjectionMatrix(); camera.lookAt(cl);
  renderer.render(scene, camera);
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
key.angle = .95; key.position.set(2, 18, 12);
const ready = Promise.all(loads).then(() => { for (const k of EP.crests) crest(k); render(0); });
window.__hf.buildReady.world = ready;
window.addEventListener('hf-seek', e => render(e.detail.time));
ready.then(() => render(0));
