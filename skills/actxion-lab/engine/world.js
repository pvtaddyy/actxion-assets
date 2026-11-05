// ACTXION Motion Lab - 3D world for "Myth or Fact?" episodes.
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

// ---------- player figure (stylised, no face) ----------
function figure(shirt, shorts, socks, hair, num) {
  const f = new THREE.Group(), m = c => new THREE.MeshStandardMaterial({ color: c, roughness: .55 });
  const skin = m(0xe9c4a6);
  const add = (geo, mat, x, y, z) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = true; f.add(o); return o; };
  add(new THREE.CapsuleGeometry(.13, .55, 6, 12), m(socks), -.17, .42, 0); add(new THREE.CapsuleGeometry(.13, .55, 6, 12), m(socks), .17, .42, 0);
  add(new THREE.CylinderGeometry(.36, .32, .38, 16), m(shorts), 0, 1.0, 0);
  const torso = add(new THREE.CapsuleGeometry(.36, .62, 8, 16), m(shirt), 0, 1.62, 0);
  const numPlane = new THREE.Mesh(new THREE.PlaneGeometry(.42, .42), new THREE.MeshBasicMaterial({ map: textTex(num, { color: '#ffffff' }), transparent: true }));
  numPlane.position.set(0, 1.62, .37); f.add(numPlane);
  add(new THREE.CapsuleGeometry(.1, .62, 6, 12), m(shirt), -.5, 1.55, 0).rotation.z = .18;
  add(new THREE.CapsuleGeometry(.1, .62, 6, 12), m(shirt), .5, 1.55, 0).rotation.z = -.18;
  add(new THREE.SphereGeometry(.28, 24, 24), skin, 0, 2.38, 0);
  add(new THREE.SphereGeometry(.3, 24, 24, 0, Math.PI * 2, 0, Math.PI / 2.1), m(hair), 0, 2.42, -.02);
  add(new THREE.SphereGeometry(.12, 16, 16), m(hair), 0, 2.62, -.2);   // the bun
  f.userData.torso = torso; return f;
}
const hero = figure(EP.colors.shirt, EP.colors.shorts, EP.colors.socks, EP.colors.hair, EP.hero.num);
scene.add(hero);

// ---------- balls ----------
const ballGeo = new THREE.SphereGeometry(.17, 20, 16), ballMat = new THREE.MeshStandardMaterial({ map: ballTex, roughness: .4 });
function ballSet(n) { const im = new THREE.InstancedMesh(ballGeo, ballMat, n); im.castShadow = true; im.frustumCulled = false; scene.add(im); return im; }
const dummy = new THREE.Object3D();
function placeBalls(im, n, t0, span, target, visible) {
  for (let k = 0; k < n; k++) {
    const tk = t0 + (n > 1 ? k * span / (n - 1) : 0), p = (EP_t - tk) / .55;
    const [x, y, z] = target(k);
    if (!visible || p < 0) { dummy.position.set(0, -50, 0); dummy.scale.setScalar(0); }
    else { dummy.position.set(x, lerp(y + 7, y, bounce(p)), z); dummy.scale.setScalar(1); dummy.rotation.set(k + EP_t * 2, k * 1.7, 0); }
    dummy.updateMatrix(); im.setMatrixAt(k, dummy.matrix);
  }
  im.instanceMatrix.needsUpdate = true;
}
let EP_t = 0;
const D = EP.data;
const pile = ballSet(D.total);           // 121 goals pile
const tubeL = ballSet(D.bigG), tubeR = ballSet(D.restG), feast = ballSet(D.feastG);
const tubeSlot = (cx, k) => { const layer = Math.floor(k / 6), a = (k % 6) / 6 * Math.PI * 2 + layer * .52; return [cx + Math.cos(a) * .36, .2 + layer * .3, Math.sin(a) * .36]; };
const pileSlot = k => { const r = 2.6 * Math.sqrt(hash(k + 9)), a = hash(k + 3) * Math.PI * 2, h = Math.max(0, 1.4 - r * .55) * hash(k + 5) + .17; return [Math.cos(a) * r, h, Math.sin(a) * r]; };

// glass tubes
const glass = new THREE.MeshPhysicalMaterial({ color: 0xbfe3ff, transmission: .6, transparent: true, opacity: .22, roughness: .05, metalness: 0, side: THREE.DoubleSide, depthWrite: false });
function tube(x, h) { const g = new THREE.Group();
  const c = new THREE.Mesh(new THREE.CylinderGeometry(.62, .62, h, 40, 1, true), glass); c.position.y = h / 2; g.add(c);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(.62, .03, 8, 48), new THREE.MeshBasicMaterial({ color: 0xffffff })); ring.rotation.x = Math.PI / 2; ring.position.y = h; g.add(ring);
  const base = new THREE.Mesh(new THREE.CylinderGeometry(.7, .75, .12, 40), new THREE.MeshStandardMaterial({ color: 0x1b2233 })); g.add(base);
  g.position.x = x; scene.add(g); return g; }
const TL = -1.25, TR = 1.25;
const tubes = [tube(TL, 5.2), tube(TR, 5.2)];

// crests as sprites
const loader = new THREE.TextureLoader(); const crestTex = {}; const loads = [];
for (const k of EP.crests) loads.push(new Promise(r => loader.load(EP.crestData[k], t => { t.colorSpace = THREE.SRGBColorSpace; crestTex[k] = t; r(); }, undefined, () => r())));
const sprites = {};
function crest(k) { if (sprites[k] && !sprites[k].material.map && crestTex[k]) { scene.remove(sprites[k]); delete sprites[k]; }
  if (!sprites[k]) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: crestTex[k], transparent: true, depthWrite: false }));
  const img = crestTex[k] && crestTex[k].image; const ar = img ? img.width / img.height : 1; s.userData.ar = ar; scene.add(s); sprites[k] = s; } return sprites[k]; }
function showCrest(k, x, y, z, size, vis) { const s = crest(k); s.visible = vis > 0.01; s.material.opacity = vis; const ar = s.userData.ar || 1;
  s.scale.set(size * Math.min(1, ar), size * Math.min(1, 1 / ar), 1); s.position.set(x, y, z); }

// mystery shield
const shieldShape = new THREE.Shape(); shieldShape.moveTo(-1, 1.2); shieldShape.lineTo(1, 1.2); shieldShape.lineTo(1, .1);
shieldShape.quadraticCurveTo(1, -.9, 0, -1.4); shieldShape.quadraticCurveTo(-1, -.9, -1, .1); shieldShape.lineTo(-1, 1.2);
const shield = new THREE.Mesh(new THREE.ExtrudeGeometry(shieldShape, { depth: .25, bevelEnabled: true, bevelSize: .06, bevelThickness: .06, bevelSegments: 3 }),
  new THREE.MeshStandardMaterial({ color: 0x141a26, metalness: .6, roughness: .35, emissive: 0x0d1b33 }));
const q = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.5), new THREE.MeshBasicMaterial({ map: textTex('?', { color: EP.colors.accent, size: 380 }), transparent: true }));
q.position.set(0, 0, .33); shield.add(q); scene.add(shield);

// mini goals grid
const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .3 });
const netMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .12, side: THREE.DoubleSide });
const goals = [];
for (let i = 0; i < D.grid.length; i++) { const g = new THREE.Group();
  const p = new THREE.CylinderGeometry(.03, .03, .55, 8);
  const l = new THREE.Mesh(p, postMat); l.position.set(-.42, .27, 0); const r = l.clone(); r.position.x = .42;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, .87, 8), postMat); bar.rotation.z = Math.PI / 2; bar.position.y = .55;
  const net = new THREE.Mesh(new THREE.PlaneGeometry(.84, .55), netMat); net.position.set(0, .27, -.22);
  const b = new THREE.Mesh(ballGeo, ballMat); b.scale.setScalar(.8); b.position.set(0, .14, -.08); b.castShadow = true;
  g.add(l, r, bar, net, b); g.userData.ball = b; scene.add(g); goals.push(g); }

// pillars
const pillars = D.pillars.map((p, i) => { const m = new THREE.Mesh(new THREE.BoxGeometry(.9, 1, .9), new THREE.MeshStandardMaterial({ color: p.color, emissive: p.color, emissiveIntensity: .25, roughness: .35 }));
  m.castShadow = true; scene.add(m); return m; });

// ---------- camera path ----------
const cams = EP.cams.map(c => ({ t: c.t, p: new THREE.Vector3(...c.p), l: new THREE.Vector3(...c.l), fov: c.fov || 42, move: c.move || 1.1 }));
function camAt(t) { let i = 0; while (i < cams.length - 1 && cams[i + 1].t <= t) i++;
  const a = cams[Math.max(0, i - 1)], b = cams[i];          // move from the previous shot into this one
  const p = i === 0 ? 1 : easeInOut(clamp((t - b.t) / b.move));
  camera.position.copy(a.p).lerp(b.p, p); const look = a.l.clone().lerp(b.l, p);
  // slow push-in while holding a shot
  if (b.t === B.real) { const hold = clamp((t - b.t - b.move) / 3); camera.position.lerp(look, hold * .12); }
  if (t >= B.journey && t < B.total) { const ang = (t - B.journey) * .07, r = Math.hypot(camera.position.x, camera.position.z);
    camera.position.x = Math.sin(ang) * r; camera.position.z = Math.cos(ang) * r; }
  camera.fov = lerp(a.fov, b.fov, p); camera.updateProjectionMatrix();
  camera.position.x += Math.sin(t * .7) * .05; camera.position.y += Math.sin(t * .9 + 1) * .04; camera.lookAt(look); }
// the hook is a dive: start far, arrive at shot 0
cams[0].p0 = cams[0].p.clone().add(new THREE.Vector3(0, 2.5, 9));

// ---------- the frame ----------
function render(t) {
  EP_t = t;
  for (const k in sprites) sprites[k].visible = false;
  camAt(t);
  if (t < cams[1].t) { const p = easeOut(t / 2.4); camera.position.lerpVectors(cams[0].p0, cams[0].p, p); camera.lookAt(cams[0].l); }
  // lights: blackout on the twist, single spotlight on the Newcastle section
  const dark = clamp(Math.min((t - B.twist) / .25, (B.verd2 - t) / .4));
  key.intensity = lerp(900, 120, dark); hemi.intensity = lerp(.55, .12, dark);
  const flare = 1 + 1.6 * Math.exp(-t * 3.5);
  floods.forEach((f, i) => { const off = clamp((t - B.twist - i * .18) / .12) * clamp((B.verd2 - t) / .4);
    f.material.opacity = lerp(1, .06, off); f.scale.setScalar(9 * flare); });
  spot.intensity = dark * 260 + win(t, B.real, B.ask, .4) * 300; spot.target.position.set(0, 1, 0);

  // hero figure: centre stage for hook, myth, verdict and ask; idle bob
  const heroVis = Math.max(win(t, -1, B.total + .2), win(t, B.real, 999));
  hero.visible = heroVis > 0.01; hero.position.set(0, 0, t < B.real ? 0 : -1.5);
  hero.rotation.y = Math.sin(t * .6) * .25; hero.userData.torso.scale.y = 1 + Math.sin(t * 3) * .01;

  // mystery shield: hook only, spinning towards camera
  shield.visible = t < B.myth + .3; shield.position.set(0, lerp(9, 4.4, bounce(t / .9)), 0); shield.rotation.y = Math.sin(t * 1.3) * .35 + easeInOut((t - B.myth + .1) / .35) * Math.PI;
  shield.scale.setScalar(.7 * easeOut(t / .6) * (1 - easeOut((t - B.myth) / .3)) + 1e-3);

  // 121 goals rain into a pile
  placeBalls(pile, D.total, B.total + .1, (B.r1 - B.total) * .75, pileSlot, t >= B.total && t < B.big + .2);

  // round 1 tubes: big six (left) vs everyone else (right)
  const tubesVis = t >= B.big - .2 && t < B.r2 + .1; tubes.forEach(g => g.visible = tubesVis);
  placeBalls(tubeL, D.bigG, B.bigNum, 1.6, k => tubeSlot(TL, k), tubesVis);
  placeBalls(tubeR, D.restG, B.elseNum, 2.0, k => tubeSlot(TR, k), tubesVis);
  

  // round 2: West Ham, Palace, Wolves drop in, 31 balls avalanche
  ['whu', 'cry', 'wol'].forEach((k, i) => { const p = easeOut((t - B.feast - i * .35) / .5);
    showCrest(k, -1.6 + i * 1.6, lerp(9, 3.6, p), 0, 1.0, win(t, B.feast + i * .35, B.twist + .1, .2)); });
  placeBalls(feast, D.feastG, B.feastNum, 1.8, k => { const r = 1.9 * Math.sqrt(hash(k + 40)), a = hash(k + 41) * 6.283; return [Math.cos(a) * r, .17 + hash(k + 42) * .6 * (1 - r / 2), Math.sin(a) * r + .3]; }, t >= B.feast && t < B.twist + .1);

  // the twist: goal grid. Newcastle 7 goals first, then Villa and Bournemouth join (22)
  goals.forEach((g, i) => { const cell = D.grid[i]; const appear = cell.club === 'new' ? B.newc + i * .12 : B.add + (i - 7) * .07;
    const vis = t >= appear && t < B.verdict + .1; g.visible = vis;
    const cols = 4, x = (i % cols - 1.5) * 1.05, z = Math.floor(i / cols) * -1.1 + 1.2;
    g.position.set(x, lerp(-1, 0, easeOut((t - appear) / .35)), z);
    const scoredAt = cell.club === 'new' ? B.newcOne : B.add + 1.0 + i * .05;
    g.userData.ball.visible = cell.scored && t >= scoredAt; });
  showCrest('avl', -1.3, 4.2, 0, 1.0, win(t, B.add, B.worse));
  showCrest('bou', 1.3, 4.2, 0, 1.0, win(t, B.add, B.worse));

  // verdict pillars
  pillars.forEach((m, i) => { const p = easeOut((t - B.verd2 - i * .35) / .9), h = D.pillars[i].v * 5 * p + .01;
    m.visible = t >= B.verd2 && t < B.real + .2; m.scale.y = h; m.position.set((i - 1) * 1.5, h / 2, 0); });
  if (t < B.real - .3) showCrest('new', 0, t < B.add ? 3.0 : 4.2, 0, t < B.add ? 1.3 : 1.0, Math.max(win(t, B.newc, B.add + .1), win(t, B.add, B.worse)));
  else showCrest('new', 0, 4.5, -1.5, 1.9, win(t, B.real, B.ask));

  renderer.render(scene, camera);
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
const ready = Promise.all(loads).then(() => { for (const k of EP.crests) crest(k); render(0); });
window.__hf.buildReady.world = ready;
window.addEventListener('hf-seek', e => render(e.detail.time));
ready.then(() => render(0));
