// Frame-by-frame renderer: timeline.json -> silent 1080x1920 30 fps H.264 (or stills).
//   node render.mjs timeline.json out.mp4 --ffmpeg /path/to/ffmpeg [--stills 0.5,3,12 --dir frames/]
// Needs playwright (npm i playwright@1.49.1) and its chromium.
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [tlPath, outPath] = args;
const TL = JSON.parse(fs.readFileSync(tlPath, "utf8"));
const fps = TL.fps || 30;
const ffmpeg = opt("--ffmpeg", "ffmpeg");
const stills = opt("--stills", null);

// The cloud image ships its own Chromium (often newer than this Playwright pins): fall back to it.
async function launch() {
  const a = { args: ["--disable-web-security", "--allow-file-access-from-files"] };
  try { return await chromium.launch(a); } catch (e) {
    for (const executablePath of [process.env.CHROMIUM_PATH, "/opt/pw-browsers/chromium"].filter(Boolean))
      if (fs.existsSync(executablePath)) return chromium.launch({ ...a, executablePath });
    throw e;
  }
}
const browser = await launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.addInitScript((tl) => { window.TL = tl; }, TL);
page.on("pageerror", (e) => { console.error("PAGE ERROR", e.message); process.exitCode = 2; });
await page.goto(pathToFileURL(path.join(here, "reel.html")).href);
await page.evaluate(() => window.ready);

if (stills) {
  const dir = opt("--dir", ".");
  fs.mkdirSync(dir, { recursive: true });
  for (const t of stills.split(",").map(Number)) {
    await page.evaluate((t) => window.seek(t), t);
    await page.screenshot({ path: path.join(dir, `frame-${t.toFixed(2)}.jpg`), type: "jpeg", quality: 90 });
  }
  await browser.close();
  process.exit();
}

const n = Math.ceil(TL.dur * fps);
const ff = spawn(ffmpeg, ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
  "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-preset", "medium", "-crf", "18", "-r", String(fps), "-movflags", "+faststart", outPath],
  { stdio: ["pipe", "inherit", "inherit"] });
const t0 = Date.now();
for (let i = 0; i < n; i++) {
  await page.evaluate((t) => window.seek(t), i / fps);
  const buf = await page.screenshot({ type: "jpeg", quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();
console.log(JSON.stringify({ path: outPath, frames: n, secs: ((Date.now() - t0) / 1000).toFixed(1) }));
