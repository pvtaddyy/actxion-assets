#!/usr/bin/env python3
"""Fetch THE MIC sound kit into an episode project:   python3 mic_kit.py hf/assets
Mixkit Free licence (commercial OK, no credit needed) forbids redistributing the files, so they are never committed:
every run downloads them from assets.mixkit.co. Rain and crowd beds are synthesised in mix.py (no files).
NEVER add cinematic-cine-hit (Mixkit 2901) or cinematic-film-flash (3131): crackly static tails (owner, 5 Nov 2026)."""
import os, sys, shutil, subprocess, urllib.request, json
FF = shutil.which('ffmpeg')
if not FF:
    import imageio_ffmpeg; FF = imageio_ffmpeg.get_ffmpeg_exe()
SFX = {'impact-2': '788', 'whoosh-2': '1492', 'whoosh-cine': '1491', 'whoosh-3': '1714', 'reaction-crowd-boo': '463',
       'reaction-crowd-laugh': '424', 'cinematic-deep-boom': '553', 'ding-1': '2870', 'pop-2': '2354', 'tech-ui-confirm': '2865'}
UA = {'User-Agent': 'Mozilla/5.0 (ACTXION THE MIC)'}
def main(out):
    d = os.path.join(out, 'sfx'); os.makedirs(d, exist_ok=True); res = {}
    for name, mid in SFX.items():
        dst = os.path.join(d, f'{name}.wav'); tmp = dst + '.mp3'
        try:
            open(tmp, 'wb').write(urllib.request.urlopen(urllib.request.Request(f'https://assets.mixkit.co/active_storage/sfx/{mid}/{mid}-preview.mp3', headers=UA), timeout=60).read())
            subprocess.run([FF, '-y', '-loglevel', 'error', '-i', tmp, '-ac', '1', '-ar', '48000', dst], check=True); os.remove(tmp); res[name] = 'ok'
        except Exception as e: res[name] = f'FAILED {e}'
    print(json.dumps(res, indent=1))
    if any(v.startswith('FAILED') for v in res.values()): sys.exit('some sounds failed: swap them in build.py for ones that downloaded')
if __name__ == '__main__': main(sys.argv[1] if len(sys.argv) > 1 else 'hf/assets')
