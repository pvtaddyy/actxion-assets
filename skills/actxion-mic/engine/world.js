// THE MIC - 3D sets (street / pub / viewing centre) for an animated vox-pop. Pure function of time: render(t). No clocks, no Math.random.
import * as THREE from './lib/three.module.js';

const EP = window.EP, B = EP.beats, LINES = EP.lines;
const SET = EP.set || 'street', OUT = SET === 'street';
const C1 = EP.club.primary, C2 = EP.club.secondary, C3 = EP.club.third ?? 0x15161c;
const hex = c => '#' + c.toString(16).padStart(6, '0');
const W = 1080, H = 1920;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, p) => a + (b - a) * p;
const easeInOut = p => { p = clamp(p); return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; };
const easeOut = p => 1 - Math.pow(1 - clamp(p), 3);
const hash = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const noise = (t, s) => Math.sin(t * 1.3 + s) * .5 + Math.sin(t * 2.7 + s * 1.7) * .3 + Math.sin(t * 5.1 + s * 2.3) * .2;

// ---------- renderer ----------
const canvas = document.getElementById('world');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const SKY = 0x0b0e1a;
scene.background = new THREE.Color(SKY); scene.fog = new THREE.FogExp2(0x12131f, .028);
const camera = new THREE.PerspectiveCamera(46, W / H, .05, 300); scene.add(camera);

scene.add(new THREE.HemisphereLight(0x6f7fa8, 0x22180c, .8));
const moon = new THREE.DirectionalLight(0x9fb6ff, .35); moon.position.set(-6, 10, 6); scene.add(moon);

function M(c, r = .6, m = 0) { return new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: m }); }
function mesh(geo, mat, parent, x = 0, y = 0, z = 0) { const o = new THREE.Mesh(geo, mat); o.position.set(x, y, z); parent.add(o); return o; }
function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
const glowTex = canvasTex(256, 256, (g, w, h) => { const r = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
  r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.2, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); });
const glow = (color, size, x, y, z, op = 1) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color, transparent: true, opacity: op,
  depthWrite: false, blending: THREE.AdditiveBlending })); s.position.set(x, y, z); s.scale.set(size, size, 1); scene.add(s); return s; };

// ---------- street (outdoor set) ----------
let floods = [];
if (OUT) {
const roadTex = canvasTex(512, 1024, (g, w, h) => {
  g.fillStyle = '#16171c'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 2600; i++) { g.fillStyle = `rgba(${hash(i) > .5 ? 255 : 0},${hash(i) > .5 ? 255 : 0},${hash(i) > .5 ? 255 : 0},${hash(i * 3) * .05})`;
    g.fillRect(hash(i * 7) * w, hash(i * 11) * h, 2 + hash(i * 13) * 4, 2 + hash(i * 17) * 4); }
  g.fillStyle = 'rgba(230,230,200,.55)'; for (let y = 0; y < h; y += 128) g.fillRect(w / 2 - 6, y, 12, 64);  // centre dashes
});
roadTex.wrapS = roadTex.wrapT = THREE.RepeatWrapping; roadTex.repeat.set(1, 8);
const road = new THREE.Mesh(new THREE.PlaneGeometry(9, 90), new THREE.MeshStandardMaterial({ map: roadTex, roughness: .22, metalness: .55, color: 0x9a9aa6 }));
road.rotation.x = -Math.PI / 2; road.position.z = -25; scene.add(road);
const paveTex = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#2a2b31'; g.fillRect(0, 0, w, h); g.strokeStyle = '#1c1d22'; g.lineWidth = 4;
  for (let i = 0; i <= 4; i++) { g.beginPath(); g.moveTo(0, i * 64); g.lineTo(w, i * 64); g.stroke(); g.beginPath(); g.moveTo(i * 64, 0); g.lineTo(i * 64, h); g.stroke(); } });
paveTex.wrapS = paveTex.wrapT = THREE.RepeatWrapping; paveTex.repeat.set(2, 40);
for (const sx of [-1, 1]) { const p = new THREE.Mesh(new THREE.BoxGeometry(3.2, .14, 90), new THREE.MeshStandardMaterial({ map: paveTex, roughness: .35, metalness: .3 }));
  p.position.set(sx * 6.1, .07, -25); scene.add(p); }

// terraced houses
const brickTex = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#4a2a22'; g.fillRect(0, 0, w, h);
  for (let y = 0, r = 0; y < h; y += 16, r++) for (let x = (r % 2) * 16; x < w; x += 32) {
    const k = r * 40 + x; g.fillStyle = `rgb(${90 + hash(k) * 40},${45 + hash(k * 2) * 20},${35 + hash(k * 3) * 15})`; g.fillRect(x + 1, y + 1, 30, 14); }
});
brickTex.wrapS = brickTex.wrapT = THREE.RepeatWrapping;
const winLit = new THREE.MeshBasicMaterial({ color: 0xffc679 }), winDark = new THREE.MeshStandardMaterial({ color: 0x0d1018, roughness: .2, metalness: .7 });
for (const sx of [-1, 1]) for (let i = 0; i < 9; i++) {
  const z = 4 - i * 6, hgt = 6.5 + hash(i + sx * 9) * 1.2;
  const bt = brickTex.clone(); bt.needsUpdate = true; bt.repeat.set(2, 2.2);
  const b = new THREE.Mesh(new THREE.BoxGeometry(4, hgt, 5.9), new THREE.MeshStandardMaterial({ map: bt, roughness: .9 }));
  b.position.set(sx * 9.7, hgt / 2, z); scene.add(b);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(4.2, .3, 6), new THREE.MeshStandardMaterial({ color: 0x23252c })); roof.position.set(sx * 9.7, hgt + .15, z); scene.add(roof);
  for (let fl = 0; fl < 2; fl++) for (let wi = 0; wi < 2; wi++) {
    const lit = hash(i * 7 + fl * 3 + wi + (sx > 0 ? 50 : 0)) > .55;
    const wm = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.3), lit ? winLit : winDark);
    wm.position.set(sx * 7.69, 2 + fl * 2.6, z - 1.4 + wi * 2.8); wm.rotation.y = -sx * Math.PI / 2; scene.add(wm);
    if (lit) glow(0xffb35c, 2.2, sx * 7.5, 2 + fl * 2.6, z - 1.4 + wi * 2.8, .35);
  }
  const door = new THREE.Mesh(new THREE.PlaneGeometry(1, 2.1), new THREE.MeshStandardMaterial({ color: [0x1d3b2a, 0x5a1414, 0x14233f][i % 3], roughness: .5 }));
  door.position.set(sx * 7.69, 1.2, z + .2); door.rotation.y = -sx * Math.PI / 2; scene.add(door);
}

// street lamps (sodium) with fake puddle reflections
const lampMat = new THREE.MeshStandardMaterial({ color: 0x1b1d22, metalness: .7, roughness: .4 });
const lampZ = [2, -8, -18, -28, -38];
for (const sx of [-1, 1]) for (const z0 of lampZ) { const z = z0 + (sx > 0 ? -5 : 0);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(.07, .09, 5.6), lampMat); pole.position.set(sx * 4.9, 2.8, z); scene.add(pole);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(1, .08, .08), lampMat); arm.position.set(sx * 4.45, 5.55, z); scene.add(arm);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(.16, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffb04a })); bulb.position.set(sx * 4.0, 5.4, z); scene.add(bulb);
  glow(0xff9a3a, 4.2, sx * 4.0, 5.4, z, .9);
  glow(0xff9a3a, 3.0, sx * 4.0, -5.4, z, .22);   // reflection in the wet road
  const pl = new THREE.PointLight(0xff9d4d, 26, 13, 1.6); pl.position.set(sx * 4.0, 5.2, z); scene.add(pl);
}

// stadium at the end of the street
const standTex = canvasTex(1024, 512, (g, w, h) => {
  g.fillStyle = '#2b2f3a'; g.fillRect(0, 0, w, h);
  for (let x = 0; x < w; x += 64) { g.fillStyle = '#3a3f4c'; g.fillRect(x, 0, 6, h); }
  g.fillStyle = hex(C1); g.fillRect(0, h * .62, w, h * .1);
  g.fillStyle = 'rgba(255,255,255,.75)'; for (let x = 20; x < w; x += 46) g.fillRect(x, h * .2, 24, 16);
});
const stand = new THREE.Mesh(new THREE.CylinderGeometry(34, 34, 18, 48, 1, true, -.55, 1.1), new THREE.MeshStandardMaterial({ map: standTex, side: THREE.DoubleSide, roughness: .7, emissive: 0x1a0606, emissiveIntensity: .6 }));
stand.position.set(0, 9, -82); scene.add(stand);
floods = [-14, -5, 5, 14].map((x, i) => glow(0xf5f0ff, 16, x, 21, -50, .95));
glow(0xd7e2ff, 70, 0, 18, -60, .25);   // floodlight haze over the ground

} else buildInterior(SET);

// ---------- indoor sets: 'pub' (watch-party bar) and 'viewing' (viewing centre, Lagos / Nairobi style) ----------
function buildInterior(kind) {
  const pub = kind === 'pub';
  scene.background = new THREE.Color(pub ? 0x140c08 : 0x0d0d12); scene.fog = new THREE.FogExp2(pub ? 0x1a100a : 0x111118, .035);
  const floorTex = canvasTex(512, 512, (g, w, h) => { g.fillStyle = pub ? '#3a2416' : '#4a4a4f'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 16; i++) { g.fillStyle = pub ? `rgba(0,0,0,${.1 + hash(i) * .2})` : `rgba(255,255,255,${hash(i) * .05})`; g.fillRect(0, i * 32, w, pub ? 3 : 32); } });
  floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set(4, 20);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 70), new THREE.MeshStandardMaterial({ map: floorTex, roughness: pub ? .45 : .8, metalness: pub ? .2 : 0 }));
  floor.rotation.x = -Math.PI / 2; floor.position.z = -25; scene.add(floor);
  const wallMat = new THREE.MeshStandardMaterial({ color: pub ? 0x4a2a1c : 0x2a2c33, roughness: .9 });
  for (const sx of [-1, 1]) { const w = new THREE.Mesh(new THREE.PlaneGeometry(70, 6), wallMat); w.position.set(sx * 7, 3, -25); w.rotation.y = -sx * Math.PI / 2; scene.add(w); }
  if (pub) { const ceil = new THREE.Mesh(new THREE.PlaneGeometry(16, 70), new THREE.MeshStandardMaterial({ color: 0x1c120c })); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, 5, -25); scene.add(ceil); }
  else { const roofTex = canvasTex(256, 256, (g, w, h) => { for (let x = 0; x < w; x += 16) { g.fillStyle = x % 32 ? '#5b5f66' : '#7a7f86'; g.fillRect(x, 0, 16, h); } });
    roofTex.wrapS = roofTex.wrapT = THREE.RepeatWrapping; roofTex.repeat.set(4, 12);
    const roof = new THREE.Mesh(new THREE.PlaneGeometry(16, 70), new THREE.MeshStandardMaterial({ map: roofTex, metalness: .6, roughness: .5 })); roof.rotation.x = Math.PI / 2; roof.position.set(0, 4.6, -25); scene.add(roof);
    for (let z = 2; z > -50; z -= 6) for (const sx of [-1, 1]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 4.6), M(0x3a3d44, .5, .6)); p.position.set(sx * 6.5, 2.3, z); scene.add(p); } }
  // the big screen at the end of the room, glowing in the club's colours
  const scr = canvasTex(1024, 576, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#2a7a3a'); gr.addColorStop(1, '#174d24'); g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(255,255,255,.6)'; g.lineWidth = 6; g.strokeRect(60, 60, w - 120, h - 120); g.beginPath(); g.moveTo(w / 2, 60); g.lineTo(w / 2, h - 60); g.stroke();
    g.fillStyle = 'rgba(0,0,0,.6)'; g.fillRect(40, 30, 300, 60); g.fillStyle = '#fff'; g.font = '900 40px Inter, Arial'; g.fillText('FULL TIME', 60, 74); });
  const screen = new THREE.Mesh(new THREE.PlaneGeometry(9, 5.06), new THREE.MeshBasicMaterial({ map: scr })); screen.position.set(0, 3.2, -40); scene.add(screen);
  glow(0x7fe08a, 26, 0, 3.2, -39.5, .35);
  // string bulbs / warm pub lights
  for (let z = 2; z > -38; z -= 2.2) for (const sx of [-1, 1]) { const x = sx * (2.5 + hash(z) * 2.5);
    const b = new THREE.Mesh(new THREE.SphereGeometry(.07, 8, 6), new THREE.MeshBasicMaterial({ color: pub ? 0xffb35c : 0xfff2c4 })); b.position.set(x, pub ? 4.6 : 4.2, z); scene.add(b);
    glow(pub ? 0xff9a3a : 0xfff0c0, 1.6, x, pub ? 4.6 : 4.2, z, .7); }
  for (let z = -2; z > -38; z -= 9) { const pl = new THREE.PointLight(pub ? 0xffa05a : 0xfff0d0, 22, 14, 1.5); pl.position.set(0, 4, z); scene.add(pl); }
  // club flags / bunting on the walls
  for (let z = 0; z > -38; z -= 5) for (const sx of [-1, 1]) { const fl = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1), new THREE.MeshStandardMaterial({ color: (z / 5) % 2 ? C1 : C2, roughness: .9, side: THREE.DoubleSide }));
    fl.position.set(sx * 6.9, 3.2, z); fl.rotation.y = -sx * Math.PI / 2; scene.add(fl); }
  if (pub) { const bar = new THREE.Mesh(new THREE.BoxGeometry(1, 1.1, 14), M(0x2a170d, .4)); bar.position.set(5.8, .55, -12); scene.add(bar); }
  else for (let z = -26; z > -36; z -= 1.6) { const bench = new THREE.Mesh(new THREE.BoxGeometry(9, .45, .5), M(0x5a3b22, .8)); bench.position.set(0, .23, z); scene.add(bench); }
}

// ---------- rain (deterministic line segments) ----------
const RN = 2200, rainPos = new Float32Array(RN * 6), rainGeo = new THREE.BufferGeometry();
rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPos, 3));
const rain = new THREE.LineSegments(rainGeo, new THREE.LineBasicMaterial({ color: 0xbfd0ff, transparent: true, opacity: .32 }));
rain.frustumCulled = false; if (OUT) scene.add(rain);
function updateRain(t, cx, cz) {
  for (let i = 0; i < RN; i++) { const x = cx + (hash(i) - .5) * 14, z = cz - hash(i * 3) * 16 + 2, h = 9, sp = 9 + hash(i * 5) * 3;
    const y = h - (((t * sp + hash(i * 7) * h) % h)); const len = .22;
    rainPos.set([x, y, z, x - .03, y - len, z], i * 6); }
  rainGeo.attributes.position.needsUpdate = true;
}

// ---------- background crowd leaving the ground ----------
const CN = 70, crowdBody = new THREE.InstancedMesh(new THREE.CapsuleGeometry(.26, .9, 4, 8), new THREE.MeshStandardMaterial({ roughness: .7 }), CN);
const crowdHead = new THREE.InstancedMesh(new THREE.SphereGeometry(.18, 10, 8), new THREE.MeshStandardMaterial({ roughness: .7 }), CN);
const cCols = [C1, C3, C1, C2, 0x2b2f3a, C1, 0x1d2742], skins = [0xe9c4a6, 0x8d5a3b, 0x5a3825, 0xc89a78, 0xf1d3bd];
for (let i = 0; i < CN; i++) { crowdBody.setColorAt(i, new THREE.Color(cCols[i % cCols.length])); crowdHead.setColorAt(i, new THREE.Color(skins[Math.floor(hash(i * 9) * 5)])); }
scene.add(crowdBody, crowdHead); crowdBody.frustumCulled = crowdHead.frustumCulled = false;
const dmy = new THREE.Object3D();
function updateCrowd(t) {
  for (let i = 0; i < CN; i++) {
    const lane = (hash(i * 3) - .5) * 7.2, sp = .9 + hash(i * 5) * .5, span = 60;
    let z = -52 + ((hash(i * 11) * span + t * sp) % span);            // walking towards camera, away from the ground
    let bob = Math.abs(Math.sin(t * 6 * sp + i)) * .05;
    if (!OUT) { z = -6.5 - hash(i * 11) * 32; bob = Math.abs(Math.sin(t * 2.2 + i)) * .03; }          // indoors: standing, swaying
    const nearFan = EP.fans.some(f => Math.abs(f.x - lane) < .9 && Math.abs(f.z - z) < 1.2);
    const y = nearFan ? -10 : 0;
    dmy.position.set(lane, .72 + bob + y, z); dmy.rotation.set(0, 0, Math.sin(t * 6 * sp + i) * .04); dmy.updateMatrix(); crowdBody.setMatrixAt(i, dmy.matrix);
    dmy.position.set(lane, 1.48 + bob + y, z); dmy.updateMatrix(); crowdHead.setMatrixAt(i, dmy.matrix);
  }
  crowdBody.instanceMatrix.needsUpdate = crowdHead.instanceMatrix.needsUpdate = true;
}

// ---------- the fans (stylised characters) ----------
function makeFan(f) {
  const g = new THREE.Group(), body = new THREE.Group(); g.add(body);
  const coat = M(f.coat, .7), shirt = M(f.shirt, .6), legs = M(f.legs, .8), skin = M(f.skin, .55), shoe = M(0x111111, .5);
  for (const sx of [-1, 1]) { mesh(new THREE.CapsuleGeometry(.13, .62, 6, 10), legs, body, sx * .15, .48, 0); mesh(new THREE.BoxGeometry(.2, .1, .34), shoe, body, sx * .15, .05, .06); }
  const torso = mesh(new THREE.CapsuleGeometry(.34, .6, 8, 16), coat, body, 0, 1.25, 0);
  if (f.open) { const sh = mesh(new THREE.CylinderGeometry(.345, .345, .7, 24, 1, true, -.45, .9), shirt, body, 0, 1.28, 0); sh.scale.set(1.02, 1, 1.02); }          // shirt showing in an open coat
  const headG = new THREE.Group(); headG.position.set(0, 1.95, 0); body.add(headG);
  mesh(new THREE.CylinderGeometry(.11, .12, .16, 12), skin, headG, 0, -.14, 0);
  const head = mesh(new THREE.SphereGeometry(.27, 28, 22), skin, headG, 0, .1, 0); head.scale.set(1, 1.08, 1);
  const ink = M(0x15110f, .4);
  const eyes = [-1, 1].map(sx => { const e = mesh(new THREE.SphereGeometry(.034, 12, 10), ink, headG, sx * .095, .15, .245); e.scale.set(1, 1.35, .6); return e; });
  const brows = [-1, 1].map(sx => { const b = mesh(new THREE.BoxGeometry(.1, .022, .02), M(f.hair, .8), headG, sx * .095, .235, .25); return b; });
  const mouth = mesh(new THREE.SphereGeometry(.04, 14, 10), M(0x3a1414, .6), headG, 0, .0, .262); mouth.scale.set(1.3, .25, .3);
  const acc = f.acc;
  if (acc.includes('cap')) { mesh(new THREE.SphereGeometry(.3, 24, 14, 0, Math.PI * 2, 0, Math.PI / 2.2), M(0x3a3a3a, .9), headG, 0, .16, -.01).scale.set(1.04, .8, 1.08);
    mesh(new THREE.BoxGeometry(.36, .03, .2), M(0x333333, .9), headG, 0, .24, .27).rotation.x = .22; }
  if (acc.includes('scarf')) { const sc = mesh(new THREE.TorusGeometry(.2, .07, 10, 24), M(C1, .8), headG, 0, -.2, 0); sc.rotation.x = Math.PI / 2;
    for (let k = 0; k < 5; k++) mesh(new THREE.BoxGeometry(.14, .12, .05), M(k % 2 ? C2 : C1, .8), body, .12, 1.55 - k * .12, .36); }
  if (acc.includes('ponytail')) { mesh(new THREE.SphereGeometry(.285, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), M(f.hair, .7), headG, 0, .13, -.02);
    mesh(new THREE.CapsuleGeometry(.07, .3, 6, 8), M(f.hair, .7), headG, 0, .02, -.3).rotation.x = .5; }
  if (acc.includes('hood')) { const h = mesh(new THREE.SphereGeometry(.34, 24, 16, Math.PI * .36, Math.PI * 1.28), M(f.coat, .8), headG, 0, .12, -.04); h.rotation.y = Math.PI / 2; }
  if (acc.includes('bucket')) { mesh(new THREE.CylinderGeometry(.24, .29, .2, 24), M(0x1d1d22, .9), headG, 0, .33, 0); mesh(new THREE.CylinderGeometry(.42, .42, .025, 28), M(0x1d1d22, .9), headG, 0, .24, 0); }
  if (acc.includes('beanie')) { mesh(new THREE.SphereGeometry(.285, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), M(0x2f6b3c, .95), headG, 0, .14, 0);
    mesh(new THREE.TorusGeometry(.27, .04, 8, 24), M(0x2f6b3c, .95), headG, 0, .16, 0).rotation.x = Math.PI / 2; }
  if (acc.includes('glasses')) { for (const sx of [-1, 1]) mesh(new THREE.TorusGeometry(.065, .014, 8, 18), M(0x111111, .3, .5), headG, sx * .1, .12, .26);
    mesh(new THREE.BoxGeometry(.07, .015, .015), M(0x111111, .3), headG, 0, .13, .27); }
  // arms on shoulder pivots
  const arms = [-1, 1].map(sx => { const p = new THREE.Group(); p.position.set(sx * .43, 1.62, 0); body.add(p);
    mesh(new THREE.CapsuleGeometry(.1, .32, 6, 10), coat, p, 0, -.2, 0);
    const el = new THREE.Group(); el.position.set(0, -.42, 0); p.add(el);
    mesh(new THREE.CapsuleGeometry(.09, .3, 6, 10), coat, el, 0, -.18, 0); mesh(new THREE.SphereGeometry(.09, 12, 10), skin, el, 0, -.4, 0);
    return { p, el }; });
  g.position.set(f.x, .14, f.z); g.rotation.y = f.face; scene.add(g);
  return { g, body, headG, arms, f, eyes, brows, mouth };
}
const FANS = {}; EP.fans.forEach(f => FANS[f.who] = makeFan(f));
const lineOf = who => LINES.filter(l => l.who === who);
function envAt(t, who) { for (const l of lineOf(who)) if (t >= l.s && t <= l.e) { const i = Math.floor((t - l.s) * 30); return l.env[Math.min(i, l.env.length - 1)] || 0; } return 0; }
function since(t, who) { for (const l of lineOf(who)) if (t >= l.s - .2 && t <= l.e + .6) return { k: t - l.s, d: l.e - l.s }; return null; }

function pose(fan, t) {
  const { body, headG, arms, f, brows, mouth, eyes } = fan, e = envAt(t, f.who), s = since(t, f.who), talk = s ? 1 : 0;
  mouth.scale.y = .18 + e * 1.1 * (.6 + .4 * Math.abs(Math.sin(t * 17)));
  const BR = f.mood ?? 0;    // brows: + angry, - sad/worried
  brows[0].rotation.z = -BR; brows[1].rotation.z = BR; brows.forEach(b => b.position.y = .235 + (f.laugh ? .02 * talk : 0));
  const blink = ((t + f.x * 3) % 3.7) < .12 ? .15 : 1; eyes.forEach(ey => ey.scale.y = 1.35 * blink);
  mouth.scale.x = f.laugh && talk ? 1.6 : 1.3;
  const breathe = Math.sin(t * 2.1 + f.x) * .012;
  body.position.y = breathe + e * .03; body.rotation.set(0, 0, 0);
  headG.rotation.set(e * .12 * Math.sin(t * 9) + Math.sin(t * .8 + f.z) * .04, Math.sin(t * .6 + f.x) * .12, 0);
  const [L, R] = arms; // default: arms down
  L.p.rotation.set(0, 0, -.12); R.p.rotation.set(0, 0, .12); L.el.rotation.set(0, 0, 0); R.el.rotation.set(0, 0, 0);
  const k = s ? s.k : 0;
  const pop = s && f.pop != null ? clamp((k - f.pop) / .22) * clamp((f.pop + (f.popHold || 2) - k) / .3) : 0;
  switch (f.gesture) {
    case 'pockets':
      headG.rotation.x += .28 - (talk ? e * .15 : 0); headG.rotation.y += Math.sin(t * 1.4) * .12 * talk;   // head down, slow shake
      body.rotation.x = .08; L.p.rotation.set(.25, 0, -.05); R.p.rotation.set(.25, 0, .05); L.el.rotation.x = -.9; R.el.rotation.x = -.9; break;   // hands in pockets
    case 'jab':
      R.p.rotation.set(-.9 - e * .6 * Math.abs(Math.sin(t * 7)), 0, .25); R.el.rotation.x = -1.1;      // jabbing
      L.p.rotation.set(-.3, 0, -.4); L.el.rotation.x = -1.4; headG.rotation.y += Math.sin(t * 6) * .1 * e; body.rotation.x = -.05 * talk; break;
    case 'point': {
      const point = talk * clamp(k / .25);
      R.p.rotation.set(lerp(0, -1.45, point), 0, .1); R.el.rotation.x = lerp(0, -.2, point);                 // points at the mic
      L.p.rotation.set(-.5 * talk, 0, -.7 * talk - .1); L.el.rotation.x = -.6 * talk; body.position.y += Math.abs(Math.sin(t * 5)) * .05 * e; break; }
    case 'handsup': {
      const up = pop;
      L.p.rotation.set(-.2, 0, lerp(-.3, -2.6, up)); R.p.rotation.set(-.2, 0, lerp(.3, 2.6, up));             // hands up on "Lagos!"
      L.el.rotation.x = -.3; R.el.rotation.x = -.3;
      body.position.y += Math.abs(Math.sin(t * 11)) * .045 * e; headG.rotation.x -= .15 * up; body.rotation.z = Math.sin(t * 8) * .03 * e; break; }
    case 'crossed': {
      const upk = pop;
      L.p.rotation.set(-.85, .5, -.1); L.el.rotation.set(-1.3, 0, .9);                                            // arms crossed
      R.p.rotation.set(lerp(-.85, -2.9, upk), lerp(-.5, 0, upk), lerp(.1, .15, upk)); R.el.rotation.set(lerp(-1.3, 0, upk), 0, lerp(-.9, 0, upk)); // points upstairs
      headG.rotation.x -= .25 * upk; break; }
    case 'shrug': {
      const sh = Math.max(pop, talk * .3);
      L.p.rotation.set(-.4, 0, lerp(-.15, -.9, sh)); R.p.rotation.set(-.4, 0, lerp(.15, .9, sh)); L.el.rotation.set(-1.2 * sh, 0, 0); R.el.rotation.set(-1.2 * sh, 0, 0);
      headG.rotation.z = .15 * sh; body.position.y += .03 * sh; break; }
    case 'facepalm': {
      R.p.rotation.set(lerp(0, -2.2, Math.max(pop, .0)), -.4 * pop, .3 * pop); R.el.rotation.x = lerp(0, -1.6, pop);
      headG.rotation.x += .3 * pop; L.p.rotation.set(.2, 0, -.1); break; }
  }
}

// ---------- the mic (camera's point of view, always in frame) ----------
const mic = new THREE.Group(); camera.add(mic);
mesh(new THREE.CylinderGeometry(.022, .03, .34, 16), M(0x111214, .35, .4), mic, 0, -.17, 0);
const foam = mesh(new THREE.SphereGeometry(.052, 24, 18), new THREE.MeshStandardMaterial({ color: 0xE61E28, roughness: .95, emissive: 0x5a0508, emissiveIntensity: .8 }), mic, 0, .05, 0); foam.scale.set(1, 1.15, 1);
const flagTex = canvasTex(512, 256, (g, w, h) => { g.fillStyle = '#ffffff'; g.fillRect(0, 0, w, h); g.fillStyle = '#E61E28'; g.fillRect(0, h - 28, w, 28);
  g.fillStyle = '#0b0b0d'; g.font = '900 104px Inter, Arial'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('ACTXION', w / 2, h / 2 - 12); });
const flagMat = new THREE.MeshStandardMaterial({ map: flagTex, roughness: .5 });
const flag = new THREE.Mesh(new THREE.BoxGeometry(.09, .05, .09), [flagMat, M(0xffffff), M(0xffffff), M(0xffffff), flagMat, M(0xffffff)]);
flag.position.set(0, -.045, 0); mic.add(flag);
mic.position.set(.2, -.36, -1.0); mic.rotation.set(-.2, .25, .12);
const camLight = new THREE.SpotLight(0xfff0e0, 9, 9, .5, .8, 1.2); camLight.position.set(.3, .25, 0); camera.add(camLight);
const camTarget = new THREE.Object3D(); camTarget.position.set(0, -.1, -3); camera.add(camTarget); camLight.target = camTarget;

// ---------- camera: one shot per line, whip between ----------
const shots = EP.shots.map(s => ({ ...s, p: new THREE.Vector3(...s.p), l: new THREE.Vector3(...s.l) }));
function camAt(t) {
  let i = 0; while (i < shots.length - 1 && shots[i + 1].t <= t) i++;
  const a = shots[Math.max(0, i - 1)], b = shots[i];
  const p = i === 0 ? 1 : easeInOut((t - b.t) / (b.move || .38));
  const pos = a.p.clone().lerp(b.p, p), look = a.l.clone().lerp(b.l, p);
  const hold = t - b.t;                                          // slow push while holding
  pos.lerp(look, clamp(hold / 6) * (b.push ?? .08));
  if (b.crane) { pos.y += easeInOut(hold / 3.2) * b.crane; pos.z += easeInOut(hold / 3.2) * b.crane * 1.2; }
  const shake = b.shake ?? 1;                                   // handheld
  pos.x += noise(t * 1.1, 1) * .025 * shake; pos.y += noise(t * 1.3, 7) * .02 * shake;
  camera.position.copy(pos); camera.lookAt(look);
  camera.rotation.z += noise(t * .9, 3) * .012 * shake;
  camera.fov = lerp(a.fov || 46, b.fov || 46, p); camera.updateProjectionMatrix();
  mic.position.y = -.36 + noise(t * 1.7, 5) * .008; mic.rotation.z = .18 + noise(t, 9) * .03;
  return { pos, whip: i > 0 && p < 1 ? Math.sin(p * Math.PI) : 0 };
}

function render(t) {
  const c = camAt(t);
  for (const k in FANS) pose(FANS[k], t);
  updateRain(t, camera.position.x, camera.position.z);
  updateCrowd(t);
  floods.forEach((f, i) => f.material.opacity = .85 + Math.sin(t * 3 + i) * .03);
  mic.visible = t < B.endcard;
  renderer.render(scene, camera);
  window.__whip = c.whip;
}
window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady.world = Promise.resolve().then(() => render(0));
window.addEventListener('hf-seek', e => render(e.detail.time));
render(0);
