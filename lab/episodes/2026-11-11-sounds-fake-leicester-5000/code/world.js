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

// ---------- Sounds Fake: Leicester 2015/16 ----------
function figure(shirt, shorts, socks, hair, skinC, num) {
  const f = new THREE.Group(), m = c => new THREE.MeshStandardMaterial({ color: c, roughness: .55 });
  const skin = m(skinC);
  const add = (geo, mat, x, y, z) => { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); o.castShadow = true; f.add(o); return o; };
  add(new THREE.CapsuleGeometry(.13, .55, 6, 12), m(socks), -.17, .42, 0); add(new THREE.CapsuleGeometry(.13, .55, 6, 12), m(socks), .17, .42, 0);
  add(new THREE.CylinderGeometry(.36, .32, .38, 16), m(shorts), 0, 1.0, 0);
  const torso = add(new THREE.CapsuleGeometry(.36, .62, 8, 16), m(shirt), 0, 1.62, 0);
  const np = new THREE.Mesh(new THREE.PlaneGeometry(.42, .42), new THREE.MeshBasicMaterial({ map: textTex(num, { color: '#ffffff' }), transparent: true }));
  np.position.set(0, 1.62, .37); f.add(np);
  add(new THREE.CapsuleGeometry(.1, .62, 6, 12), m(shirt), -.5, 1.55, 0).rotation.z = .18;
  add(new THREE.CapsuleGeometry(.1, .62, 6, 12), m(shirt), .5, 1.55, 0).rotation.z = -.18;
  add(new THREE.SphereGeometry(.28, 24, 24), skin, 0, 2.38, 0);
  add(new THREE.SphereGeometry(.3, 24, 24, 0, Math.PI * 2, 0, Math.PI / 2.1), m(hair), 0, 2.42, -.02);
  f.userData.torso = torso; scene.add(f); return f;
}
const BLUE = 0x1f4fd1;
const fox = figure(BLUE, 0xffffff, BLUE, 0x2a1d14, 0xe9c4a6, '');        // hook + finale: a Leicester player, no face
const vardy = figure(BLUE, 0xffffff, BLUE, 0x2a1d14, 0xe9c4a6, '9');
const mahrez = figure(BLUE, 0xffffff, BLUE, 0x141010, 0xb07a55, '26');

// the odds tower: 5000 printed on a giant block, the player tiny beside it
const oddsTex = canvasTex(512, 1024, (g, w, h) => { g.fillStyle = '#141a26'; g.fillRect(0, 0, w, h);
  g.strokeStyle = '#ffd54a'; g.lineWidth = 14; g.strokeRect(14, 14, w - 28, h - 28);
  g.fillStyle = '#ffd54a'; g.font = '900 210px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.save(); g.translate(w / 2, h / 2); g.rotate(-Math.PI / 2); g.fillText('5000-1', 0, 10); g.restore(); });
const oddsMat = new THREE.MeshStandardMaterial({ map: oddsTex, emissive: 0xffffff, emissiveMap: oddsTex, emissiveIntensity: .35, roughness: .5 });
const odds = new THREE.Mesh(new THREE.BoxGeometry(1.8, 6.4, 1.8), [new THREE.MeshStandardMaterial({ color: 0x141a26 }), new THREE.MeshStandardMaterial({ color: 0x141a26 }),
  new THREE.MeshStandardMaterial({ color: 0x1b2233 }), new THREE.MeshStandardMaterial({ color: 0x1b2233 }), oddsMat, new THREE.MeshStandardMaterial({ color: 0x141a26 })]);
odds.castShadow = true; scene.add(odds);

// league ladder: 20 slabs, Leicester's glows blue
const slabs = [];
for (let i = 0; i < 20; i++) { const s = new THREE.Mesh(new THREE.BoxGeometry(3.6, .2, .9), new THREE.MeshStandardMaterial({ color: 0x2a3247, roughness: .5 }));
  scene.add(s); slabs.push(s); }
const leiSlab = new THREE.Mesh(new THREE.BoxGeometry(3.9, .26, 1.0), new THREE.MeshStandardMaterial({ color: BLUE, emissive: BLUE, emissiveIntensity: .8 }));
scene.add(leiSlab);
const slabY = pos => 6.0 - (pos - 1) * .29;   // position 1 at the top

// last nine: 9 balls, 7 gold
const ballGeo = new THREE.SphereGeometry(.26, 24, 18);
const goldM = new THREE.MeshStandardMaterial({ color: 0xffd54a, emissive: 0xffb000, emissiveIntensity: .45, roughness: .3, metalness: .4 });
const greyM = new THREE.MeshStandardMaterial({ color: 0x59627a, roughness: .6 });
const nine = []; const NINE = [1, 1, 0, 1, 1, 1, 0, 1, 1];   // shape only: 7 of 9 lit (order not claimed)
for (let i = 0; i < 9; i++) { const b = new THREE.Mesh(ballGeo, NINE[i] ? goldM : greyM); b.castShadow = true; scene.add(b); nine.push(b); }

// the title tower: 38 blocks, 23 wins (blue), 12 draws (silver), 3 defeats (red)
const blockGeo = new THREE.BoxGeometry(1.5, .13, 1.5);
const mW = new THREE.MeshStandardMaterial({ color: BLUE, emissive: BLUE, emissiveIntensity: .35, roughness: .4 });
const mD = new THREE.MeshStandardMaterial({ color: 0xc9d1e0, roughness: .4, metalness: .3 });
const mL = new THREE.MeshStandardMaterial({ color: 0xd92b3a, emissive: 0x7a0a12, emissiveIntensity: .4, roughness: .4 });
const blocks = [];
for (let i = 0; i < 38; i++) { const b = new THREE.Mesh(blockGeo, i < 23 ? mW : i < 35 ? mD : mL); b.castShadow = true; scene.add(b); blocks.push(b); }

// points pillars: LEI 81, ARS 71, CHE 50
const pil = D => { const m = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1, 1.2), new THREE.MeshStandardMaterial({ color: D, emissive: D, emissiveIntensity: .3, roughness: .35 })); m.castShadow = true; scene.add(m); return m; };
const pLei = pil(BLUE), pArs = pil(0xdb0007), pChe = pil(0x034694);

// Vardy: 11 mini goals in an arc, a ball into each in turn; then 24 balls rain
const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .3 });
const netMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .14, side: THREE.DoubleSide });
const smallBall = new THREE.SphereGeometry(.13, 16, 12), ballTexM = new THREE.MeshStandardMaterial({ map: ballTex, roughness: .4 });
const goals = [];
for (let i = 0; i < 11; i++) { const g = new THREE.Group();
  const p = new THREE.CylinderGeometry(.03, .03, .55, 8);
  const l = new THREE.Mesh(p, postMat); l.position.set(-.42, .27, 0); const r = l.clone(); r.position.x = .42;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, .87, 8), postMat); bar.rotation.z = Math.PI / 2; bar.position.y = .55;
  const net = new THREE.Mesh(new THREE.PlaneGeometry(.84, .55), netMat); net.position.set(0, .27, -.22);
  const b = new THREE.Mesh(smallBall, ballTexM); b.castShadow = true;
  g.add(l, r, bar, net, b); g.userData.ball = b; scene.add(g); goals.push(g); }
const rain = new THREE.InstancedMesh(smallBall, ballTexM, 24); rain.castShadow = true; rain.frustumCulled = false; scene.add(rain);
const dummy = new THREE.Object3D();

// Mahrez: a gold ring under him
const ring = new THREE.Mesh(new THREE.TorusGeometry(1.1, .06, 12, 64), new THREE.MeshStandardMaterial({ color: 0xffd54a, emissive: 0xffb000, emissiveIntensity: 1 }));
ring.rotation.x = Math.PI / 2; scene.add(ring);

// crests
const loader = new THREE.TextureLoader(); const crestTex = {}; const loads = [];
for (const k of EP.crests) loads.push(new Promise(r => loader.load(EP.crestData[k], t => { t.colorSpace = THREE.SRGBColorSpace; crestTex[k] = t; r(); }, undefined, () => r())));
const sprites = {};
function showCrest(k, x, y, z, size, vis) { if (!sprites[k] && crestTex[k]) { sprites[k] = new THREE.Sprite(new THREE.SpriteMaterial({ map: crestTex[k], transparent: true, depthWrite: false })); scene.add(sprites[k]); }
  const s = sprites[k]; if (!s) return; s.visible = vis > 0.01; s.material.opacity = vis; s.scale.set(size, size, 1); s.position.set(x, y, z); }

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
  if (t < B.ctx) { const p = easeInOut(t / 4.5); camera.position.set(lerp(2.5, 0, p), lerp(1.8, 3.0, p), lerp(10, 15, p)); camera.lookAt(0, lerp(2.2, 3.6, p), 0); }
  // lights: blackout on the Chelsea twist and for Mahrez; spot follows
  const dark = Math.max(clamp(Math.min((t - B.twist) / .25, (B.vardy - t) / .4)), clamp(Math.min((t - B.mahrez) / .3, (B.again - t) / .4)));
  key.intensity = lerp(900, 110, dark); hemi.intensity = lerp(.55, .12, dark);
  const flare = 1 + 1.6 * Math.exp(-t * 3.5);
  floods.forEach((f, i) => { f.material.opacity = lerp(1, .08, dark); f.scale.setScalar(9 * flare); });
  spot.intensity = dark * 320; 

  // hook: tiny player beside the giant 5000-1 block (rises out of the ground)
  const hookVis = t < B.ctx + .3;
  odds.visible = hookVis; odds.position.set(1.9, lerp(-3.3, 2.5, easeOut(t / 1.1)), -.9); odds.rotation.y = -.3;
  fox.visible = hookVis || (t >= B.again - .1 && t < B.ask);
  if (hookVis) { fox.position.set(-1.3, 0, .6); fox.rotation.y = .35 + Math.sin(t * .6) * .1; }
  else { fox.position.set(0, blocksTopY(t), 0); fox.rotation.y = Math.sin(t * .6) * .25; }

  // ladder: bottom for 4.5 months, then climbs to 14th
  const ladVis = t >= B.before - .2 && t < B.title + .1;
  slabs.forEach((s, i) => { s.visible = ladVis; const p = easeOut((t - B.before - i * .03) / .4); s.position.set(0, slabY(i + 1) * p, 0); s.scale.x = p + 1e-3; });
  leiSlab.visible = ladVis; const climb = easeInOut((t - B.stayed - 1.4) / 1.6);
  leiSlab.position.set(0, slabY(lerp(20, 14, climb)) + .02, .12); leiSlab.scale.setScalar(1 + .06 * Math.sin(t * 6));
  showCrest('lei', -1.25, slabY(lerp(20, 14, climb)) + .05, .9, .7, win(t, B.before + .3, B.title));
  nine.forEach((b, i) => { const at = B.stayed + .3 + i * .17; b.visible = ladVis && t >= at; const p = bounce((t - at) / .45);
    b.position.set((i - 4) * .4, lerp(3, .26, p), 2.4); });

  // tower of 38 results
  blocks.forEach((b, i) => { const at = i < 23 ? B.title + .9 + i * .08 : i < 35 ? B.draws + (i - 23) * .06 : B.defeats + .4 + (i - 35) * .25;
    b.visible = t >= at && t < B.points + .2; const p = bounce((t - at) / .4);
    b.position.set(0, lerp(i * .14 + 6, i * .14 + .07, p), 0); b.rotation.y = (1 - clamp((t - at) / .4)) * 1.2; });

  // points pillars
  const pv = t >= B.points - .1 && t < B.vardy;
  const hgt = v => v / 81 * 4.2;
  const grow = (m, v, at, x) => { const p = easeOut((t - at) / 1.0), h = hgt(v) * p + .01; m.visible = pv && t >= at; m.scale.y = h; m.position.set(x, h / 2, 0); return h; };
  const hL = grow(pLei, 81, B.points, -1.5), hA = grow(pArs, 71, B.points + 1.4, 0), hC = grow(pChe, 50, B.twistNum, 1.5);
  if (pv) { showCrest('lei', -1.5, hL + .65, 0, .9, win(t, B.points, B.vardy)); showCrest('ars', 0, hA + .65, 0, .9, win(t, B.points + 1.4, B.vardy));
    if (t >= B.twistNum) showCrest('che', 1.5, hC + .65, 0, .9, win(t, B.twistNum, B.vardy)); }
  if (t >= B.twist && t < B.vardy) spot.target.position.set(1.5, 0, 0); else spot.target.position.set(0, 0, 0);
  spot.position.set(t >= B.twist && t < B.vardy ? 1.5 : 0, 16, 2);

  // Vardy: 11 goals in a row
  const vv = t >= B.vardy - .1 && t < B.mahrez - .1;
  vardy.visible = vv; vardy.position.set(0, 0, 1.6); vardy.rotation.y = Math.sin(t * .8) * .3;
  goals.forEach((g, i) => { const a = (i - 5) / 5 * 1.25, at = B.vardy + .3 + i * .22;
    g.visible = vv && t >= at; g.position.set(Math.sin(a) * 3.2, lerp(-1, 0, easeOut((t - at) / .3)), -Math.cos(a) * 3.2 + 1.6); g.lookAt(0, 0, 1.6);
    const sAt = at + .25, p = clamp((t - sAt) / .3); g.userData.ball.visible = t >= sAt; g.userData.ball.position.set(0, .14, lerp(1.6, -.1, p)); });
  for (let k = 0; k < 24; k++) { const at = B.goals24 + .2 + k * .045, p = (t - at) / .5;
    const r = 1.6 * Math.sqrt(hash(k + 40)), a = hash(k + 41) * 6.283;
    if (!vv || p < 0) { dummy.position.set(0, -50, 0); dummy.scale.setScalar(0); } else { dummy.position.set(Math.cos(a) * r, lerp(7, .13 + hash(k + 42) * .3, bounce(p)), Math.sin(a) * r + 1.6); dummy.scale.setScalar(1); }
    dummy.updateMatrix(); rain.setMatrixAt(k, dummy.matrix); }
  rain.instanceMatrix.needsUpdate = true;

  // Mahrez under the spotlight with a gold ring
  const mv = t >= B.mahrez - .1 && t < B.again;
  mahrez.visible = mv; mahrez.position.set(0, 0, 0); mahrez.rotation.y = Math.sin(t * .6) * .3 + (1 - easeOut((t - B.mahrez) / .8)) * 2;
  ring.visible = mv; ring.position.set(0, .05 + .02 * Math.sin(t * 3), 0); ring.scale.setScalar(easeOut((t - B.mahrez - .4) / .6) + 1e-3);

  // finale: the tower comes back, the player on top, crest above
  if (t >= B.again - .1) { blocks.forEach((b, i) => { b.visible = true; const at = B.again + i * .02, p = easeOut((t - at) / .35); b.position.set(0, lerp(-2, i * .14 + .07, p), 0); b.rotation.y = 0; });
    showCrest('lei', -1.5, blocksTopY(t) + 1.4, .3, 1.0, win(t, B.again + .6, B.ask + .2)); }
  renderer.render(scene, camera);
}
function blocksTopY(t) { return 38 * .14 + .02; }

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
const ready = Promise.all(loads).then(() => render(0));
window.__hf.buildReady.world = ready;
window.addEventListener('hf-seek', e => render(e.detail.time));
ready.then(() => render(0));
