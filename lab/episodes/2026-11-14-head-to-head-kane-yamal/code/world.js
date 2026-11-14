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

// ---------- Head to Head: Kane v Yamal, league 2026/27 ----------
function figure(shirt, shorts, socks, hair, skinC, num) {
  const f = new THREE.Group(), m = c => new THREE.MeshStandardMaterial({ color: c, roughness: .55 });
  const skin = m(skinC);
  const add = (geo, mat, x, y, z) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = true; f.add(o); return o; };
  add(new THREE.CapsuleGeometry(.13, .55, 6, 12), m(socks), -.17, .42, 0); add(new THREE.CapsuleGeometry(.13, .55, 6, 12), m(socks), .17, .42, 0);
  add(new THREE.CylinderGeometry(.36, .32, .38, 16), m(shorts), 0, 1.0, 0);
  add(new THREE.CapsuleGeometry(.36, .62, 8, 16), m(shirt), 0, 1.62, 0);
  const np = new THREE.Mesh(new THREE.PlaneGeometry(.42, .42), new THREE.MeshBasicMaterial({ map: textTex(num, { color: '#ffffff' }), transparent: true }));
  np.position.set(0, 1.62, .37); f.add(np);
  add(new THREE.CapsuleGeometry(.1, .62, 6, 12), m(shirt), -.5, 1.55, 0).rotation.z = .18;
  add(new THREE.CapsuleGeometry(.1, .62, 6, 12), m(shirt), .5, 1.55, 0).rotation.z = -.18;
  add(new THREE.SphereGeometry(.28, 24, 24), skin, 0, 2.38, 0);
  add(new THREE.SphereGeometry(.3, 24, 24, 0, Math.PI * 2, 0, Math.PI / 2.1), m(hair), 0, 2.42, -.02);
  scene.add(f); return f;
}
const RED = 0xdc052d, BLAU = 0x004d98, GRANA = 0xa50044;
const kane = figure(RED, RED, RED, 0x8a6a45, 0xeac3a4, '9');
const yamal = figure(GRANA, BLAU, BLAU, 0x111111, 0xa87150, '10');

// Ballon d'Or orb over Kane in the hook
const goldM = new THREE.MeshStandardMaterial({ color: 0xffd54a, emissive: 0xffb000, emissiveIntensity: .55, roughness: .25, metalness: .6 });
const orb = new THREE.Mesh(new THREE.SphereGeometry(.42, 32, 24), goldM); orb.castShadow = true; scene.add(orb);

// glass tubes + goals (balls) and assists (gold cubes)
const glass = new THREE.MeshStandardMaterial({ color: 0xbfd8ff, transparent: true, opacity: .16, roughness: .05, metalness: .1, side: THREE.DoubleSide, depthWrite: false });
const tubes = [-1, 1].map(s => { const m = new THREE.Mesh(new THREE.CylinderGeometry(.27, .27, 3.7, 32, 1, true), glass); scene.add(m); return m; });
const ballGeo = new THREE.SphereGeometry(.16, 20, 14), ballM = new THREE.MeshStandardMaterial({ map: ballTex, roughness: .4 });
const balls = { k: [], y: [] };
for (let i = 0; i < 10; i++) { for (const s of ['k', 'y']) { const b = new THREE.Mesh(ballGeo, ballM); b.castShadow = true; scene.add(b); balls[s].push(b); } }
const cubeGeo = new THREE.BoxGeometry(.4, .3, .4);
const cubes = { k: [], y: [] };
for (let i = 0; i < 8; i++) { for (const s of ['k', 'y']) { const c = new THREE.Mesh(cubeGeo, goldM); c.castShadow = true; scene.add(c); cubes[s].push(c); } }

// minutes: two long bars (lengths to scale: 712 and 991)
const barM = c => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: .35, roughness: .35 });
const barK = new THREE.Mesh(new THREE.BoxGeometry(1, .42, .42), barM(RED)), barY = new THREE.Mesh(new THREE.BoxGeometry(1, .42, .42), barM(GRANA));
barK.castShadow = barY.castShadow = true; scene.add(barK, barY);

// per minute: two stopwatch rings that sweep 59/60 and 55/60 of a lap
const faceM = new THREE.MeshStandardMaterial({ color: 0x141a26, roughness: .6, transparent: true, opacity: .85 });
const faces = [-1, 1].map(() => { const g = new THREE.Group();
  const d = new THREE.Mesh(new THREE.CircleGeometry(.95, 48), faceM); g.add(d);
  for (let k = 0; k < 12; k++) { const tk = new THREE.Mesh(new THREE.BoxGeometry(.04, .14, .02), new THREE.MeshBasicMaterial({ color: 0x8792a8 }));
    const a = k / 12 * Math.PI * 2; tk.position.set(Math.sin(a) * .78, Math.cos(a) * .78, .02); tk.rotation.z = -a; g.add(tk); }
  const hand = new THREE.Mesh(new THREE.BoxGeometry(.05, .7, .03), new THREE.MeshBasicMaterial({ color: 0xffffff })); hand.geometry.translate(0, .35, 0); hand.position.z = .05; g.add(hand);
  g.userData.hand = hand; scene.add(g); return g; });
const arcCache = {};
const arcs = [null, null];
function setArc(i, frac, color) { const key = i + ':' + frac.toFixed(3);
  if (!arcCache[key]) arcCache[key] = new THREE.RingGeometry(.84, .95, 64, 1, Math.PI / 2 - frac * Math.PI * 2, frac * Math.PI * 2);
  if (!arcs[i]) { arcs[i] = new THREE.Mesh(arcCache[key], new THREE.MeshBasicMaterial({ color, side: THREE.DoubleSide })); arcs[i].position.z = .03; faces[i].add(arcs[i]); }
  arcs[i].geometry = arcCache[key]; }

// Wembley: a goal, a ball in early, then a penalty off the bar
const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .3 });
const netMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .16, side: THREE.DoubleSide });
const goal = new THREE.Group();
{ const p = new THREE.CylinderGeometry(.06, .06, 2.0, 12);
  const l = new THREE.Mesh(p, postMat); l.position.set(-2.4, 1.0, 0); const r = l.clone(); r.position.x = 2.4;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, 4.9, 12), postMat); bar.rotation.z = Math.PI / 2; bar.position.y = 2.0;
  const net = new THREE.Mesh(new THREE.PlaneGeometry(4.8, 2.0), netMat); net.position.set(0, 1.0, -1.0);
  goal.add(l, r, bar, net); scene.add(goal); }
const shot = new THREE.Mesh(new THREE.SphereGeometry(.2, 24, 18), ballM); shot.castShadow = true; scene.add(shot);

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
  const dark = clamp(Math.min((t - B.wembley) / .3, (B.madrid - t) / .4));
  key.intensity = lerp(900, 120, dark); hemi.intensity = lerp(.55, .14, dark);
  const flare = 1 + 1.6 * Math.exp(-t * 3.5);
  floods.forEach(f => { f.material.opacity = lerp(1, .1, dark); f.scale.setScalar(9 * flare); });
  spot.intensity = dark * 320; spot.position.set(0, 16, 4); spot.target.position.set(0, 1, 0);

  // figures: hook Kane alone with the orb, Yamal rises in on "This season"
  const inRounds = t >= B.r1 && t < B.wembley;
  const figVis = t < B.wembley || t >= B.madrid - .1;
  kane.visible = figVis; yamal.visible = figVis && t >= B.season - .05;
  let kx = -1.3, yx = 1.3, ky = .35, yy = -.35;
  if (inRounds) { kx = -2.35; yx = 2.35; ky = .5; yy = -.5; }
  if (t >= B.madrid - .1) { const p = easeInOut((t - B.madrid) / 1.0); kx = lerp(-2.4, -1.0, p); yx = lerp(2.4, 1.0, p); ky = lerp(.5, 1.4, p); yy = lerp(-.5, -1.4, p);
    if (t >= B.ask) { const q = easeInOut((t - B.ask) / .8); kx = lerp(-1.0, -1.3, q); yx = lerp(1.0, 1.3, q); ky = lerp(1.4, .35, q); yy = lerp(-1.4, -.35, q); } }
  const ent = t < B.r1 + 1 ? easeInOut((t - B.r1) / .8) : 1;
  if (t >= B.r1 && t < B.r1 + 1) { kx = lerp(-1.3, -2.35, ent); yx = lerp(1.3, 2.35, ent); }
  kane.position.set(kx, 0, 0); kane.rotation.y = ky + Math.sin(t * .6) * .08;
  const rise = easeOut((t - B.season) / .6);
  yamal.position.set(yx, lerp(-2.6, 0, t < B.ctx ? rise : 1), 0); yamal.rotation.y = yy + Math.sin(t * .6 + 1) * .08;
  orb.visible = t < B.ctx + .2; orb.position.set(kx, 3.15 + .08 * Math.sin(t * 2.2), 0); orb.rotation.y = t;
  orb.scale.setScalar(easeOut(t / .6) + 1e-3);

  // context: club crests over each player
  showCrest('bay', -1.3, 3.3, 0, .8, win(t, B.ctx + .9, B.r1));
  showCrest('bar', 1.3, 3.3, 0, .8, win(t, B.ctx + .9, B.r1));

  // tubes: goals then assists
  const tubeVis = t >= B.r1 + .3 && t < B.minutes;
  tubes.forEach((m, i) => { m.visible = tubeVis; m.position.set(i ? .85 : -.85, 1.85, 0); m.scale.y = easeOut((t - B.r1 - .3) / .5) + 1e-3; m.position.y = 1.85 * m.scale.y; });
  const dropBall = (b, at, i, x) => { const p = bounce((t - at) / .45); b.visible = t >= at && t < B.r2; b.position.set(x, lerp(4.2, .18 + i * .34, p), 0); };
  balls.y.forEach((b, i) => dropBall(b, B.goalsY + .25 + i * .1, i, .85));
  balls.k.forEach((b, i) => i < 4 ? dropBall(b, B.goalsK + .25 + i * .12, i, -.85) : (b.visible = false));
  const dropCube = (c, at, i, x) => { const p = bounce((t - at) / .4); c.visible = t >= at && t < B.minutes; c.position.set(x, lerp(4.2, .17 + i * .32, p), 0); c.rotation.y = (1 - clamp((t - at) / .4)) * 1.4; };
  cubes.k.forEach((c, i) => dropCube(c, B.astK + .2 + i * .1, i, -.85));
  cubes.y.forEach((c, i) => dropCube(c, B.astY + .2 + i * .1, i, .85));
  if (t >= B.goalsY && t < B.r2) showCrest('bar', .85, 3.95, 0, .55, win(t, B.goalsY, B.r2));
  if (t >= B.goalsK && t < B.r2) showCrest('bay', -.85, 3.95, 0, .55, win(t, B.goalsK, B.r2));
  if (t >= B.astK && t < B.level) showCrest('bay', -.85, 3.95, 0, .55, win(t, B.astK, B.level, .2));
  if (t >= B.astY && t < B.level) showCrest('bar', .85, 3.95, 0, .55, win(t, B.astY, B.level, .2));

  // minutes: bars grow from the left, to scale
  const mv = t >= B.minutes && t < B.perMin;
  const U = 3.9 / 991;
  const gK = easeOut((t - B.minK) / 1.0) * 712 * U + 1e-3, gY = easeOut((t - B.minY) / 1.0) * 991 * U + 1e-3;
  barK.visible = mv && t >= B.minK; barY.visible = mv && t >= B.minY;
  barK.scale.x = gK; barK.position.set(-1.6 + gK / 2, 3.55, .8); barY.scale.x = gY; barY.position.set(-1.6 + gY / 2, 2.95, .8);
  if (mv) { showCrest('bay', -1.95, 3.55, .8, .45, win(t, B.minK, B.perMin)); showCrest('bar', -1.95, 2.95, .8, .45, win(t, B.minY, B.perMin)); }

  // per minute: stopwatches
  const sv = t >= B.perMin && t < B.wembley;
  faces.forEach((f, i) => { f.visible = sv; f.position.set(i ? 1.0 : -1.0, 2.9, 1.0); f.scale.setScalar(.82 * easeOut((t - B.wK + .4) / .4) + 1e-3); });
  const fK = 59 / 60 * easeInOut((t - B.wK) / 1.2), fY = 55 / 60 * easeInOut((t - B.wY) / 1.2);
  if (sv) { setArc(0, Math.max(.001, fK), RED); setArc(1, Math.max(.001, fY), 0xffd54a);
    faces[0].userData.hand.rotation.z = -fK * Math.PI * 2; faces[1].userData.hand.rotation.z = -fY * Math.PI * 2; }

  // Wembley: early goal, then penalty off the bar
  const gv = t >= B.wembley - .1 && t < B.madrid;
  goal.visible = gv; goal.position.set(0, 0, -1.5);
  shot.visible = gv && t >= B.scored - .4 && t < B.won;
  if (t < B.pen) { const p = clamp((t - B.scored + .4) / .5); shot.position.set(lerp(.6, -1.6, p), lerp(.2, 1.2, p) + Math.sin(p * Math.PI) * .6, lerp(4.5, -2.3, p)); }
  else { const p = clamp((t - B.pen) / .45), q = clamp((t - B.pen - .45) / .7);
    if (p < 1) shot.position.set(lerp(0, .4, p), lerp(.2, 2.02, p), lerp(4.5, -1.5, p));
    else shot.position.set(lerp(.4, 1.6, q), 2.02 + Math.sin(q * Math.PI) * 1.4 - q * 1.8, lerp(-1.5, 3.5, q)); }
  if (gv) showCrest('spain', 0, 2.75, -1.5, .8, win(t, B.won, B.madrid));

  // Madrid: face off, national crests above
  if (t >= B.madrid && t < B.ask) { showCrest('england', kx, 3.3, 0, .8, win(t, B.madrid + .6, B.ask)); showCrest('spain', yx, 3.3, 0, .8, win(t, B.madrid + .6, B.ask)); }
  renderer.render(scene, camera);
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
const ready = Promise.all(loads).then(() => render(0));
window.__hf.buildReady.world = ready;
window.addEventListener('hf-seek', e => render(e.detail.time));
ready.then(() => render(0));
