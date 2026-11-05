#!/usr/bin/env bash
# ACTXION LAB cloud setup (once per run). Prints each step's time. Safe to re-run.
#   source skills/actxion-lab/cloud_setup.sh
t0=$(date +%s); step(){ echo "[setup $(( $(date +%s) - t0 ))s] $*"; }
PY=python3
step "python $($PY --version 2>&1), node $(node --version 2>/dev/null)"
$PY -m pip install -q --ignore-installed numpy scipy soundfile imageio-ffmpeg faster-whisper kokoro-onnx static-ffmpeg 2>&1 | tail -2
step "pip done"
# ffmpeg + ffprobe on PATH (HyperFrames needs both)
if ! command -v ffprobe >/dev/null; then
  $PY -c "import static_ffmpeg; static_ffmpeg.add_paths()" >/dev/null 2>&1
  SFF=$($PY -c "import static_ffmpeg.run as r; f,p=r.get_or_fetch_platform_executables_else_raise(); print(f)" 2>/dev/null)
  if [ -n "$SFF" ]; then export PATH="$(dirname "$SFF"):$PATH"; fi
fi
if ! command -v ffmpeg >/dev/null; then
  mkdir -p "$HOME/bin"; ln -sf "$($PY -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')" "$HOME/bin/ffmpeg"; export PATH="$HOME/bin:$PATH"
fi
step "ffmpeg: $(command -v ffmpeg) | ffprobe: $(command -v ffprobe || echo MISSING)"
# Node 22+ for HyperFrames
NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
if [ "$NODE_MAJOR" -lt 22 ]; then
  step "node $NODE_MAJOR too old: installing node 22 via npm 'n'"
  npm i -g -s n >/dev/null 2>&1 && n -q 22 >/dev/null 2>&1 && hash -r
  step "node now $(node --version 2>/dev/null)"
fi
# Chrome for HyperFrames: its own download, else the box's Playwright Chromium
npx -y hyperframes@0.9.15 browser ensure >/tmp/hf-browser.log 2>&1 || true
if ! npx -y hyperframes@0.9.15 browser path >/dev/null 2>&1; then
  CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1)
  [ -n "$CH" ] && export PUPPETEER_EXECUTABLE_PATH="$CH" PRODUCER_CHROME_PATH="$CH" CHROME_PATH="$CH"
  step "using Playwright chromium: $CH"
fi
step "hyperframes browser: $(npx -y hyperframes@0.9.15 browser path 2>/dev/null | tail -1)"
npx -y hyperframes@0.9.15 doctor 2>&1 | tail -12
step "setup done"
