#!/usr/bin/env python3
"""Fetch the ACTXION LAB sound kit and end-card music into an episode project.
   python3 lab_kit.py hf/assets
Mixkit Free licence (commercial OK, no credit) forbids redistributing the files, so they are never committed:
every run downloads them from assets.mixkit.co. CC0 sounds ship in ../assets/sfx-cc0/.
NEVER add cinematic-cine-hit (Mixkit 2901) or cinematic-film-flash (3131): crackly static tails (owner, 5 Nov 2026).
"""
import os, sys, shutil, subprocess, urllib.request, json
FF = shutil.which('ffmpeg')
if not FF:
    import imageio_ffmpeg; FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
SFX = {   # file name used in build.py -> Mixkit id
    'whoosh-2': '1492', 'whoosh-cine': '1491', 'tick-1': '2531', 'impact-2': '788', 'riser-1': '790',
    'ding-1': '2870', 'pop-2': '2354', 'cinematic-deep-boom': '553', 'tech-glitch-1': '1031', 'wood-hit': '2182',
}
CC0 = ['cc0-dark-sting']
MUSIC = {'music': '440'}   # Infinity (upbeat), only as the end-card moment
UA = {'User-Agent': 'Mozilla/5.0 (ACTXION LAB)'}

def get(url, dst):
    open(dst, 'wb').write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())

def main(out):
    sfx_dir = os.path.join(out, 'sfx'); os.makedirs(sfx_dir, exist_ok=True)
    res = {}
    for name, mid in SFX.items():
        dst = os.path.join(sfx_dir, f'{name}.wav'); tmp = dst + '.mp3'
        try:
            get(f'https://assets.mixkit.co/active_storage/sfx/{mid}/{mid}-preview.mp3', tmp)
            subprocess.run([FF, '-y', '-loglevel', 'error', '-i', tmp, '-ac', '1', '-ar', '48000', dst], check=True)
            os.remove(tmp); res[name] = 'ok'
        except Exception as e:
            res[name] = f'FAILED {e}'
    # engine/ is copied into the work dir, so ../assets may not exist: also try $LAB_ASSETS and repo checkouts
    import glob
    cands = [os.path.join(HERE, '..', 'assets'), os.environ.get('LAB_ASSETS', ''),
             *glob.glob(os.path.expanduser('~/*/skills/actxion-lab/assets')), *glob.glob('/home/*/*/skills/actxion-lab/assets')]
    for name in CC0:
        src = next((os.path.join(c, 'sfx-cc0', f'{name}.wav') for c in cands if c and os.path.exists(os.path.join(c, 'sfx-cc0', f'{name}.wav'))), None)
        if src: shutil.copy(src, os.path.join(sfx_dir, f'{name}.wav')); res[name] = 'ok (cc0)'
        else: res[name] = 'FAILED cc0 file not found (set LAB_ASSETS=<repo>/skills/actxion-lab/assets)'
    for name, mid in MUSIC.items():
        try: get(f'https://assets.mixkit.co/music/{mid}/{mid}.mp3', os.path.join(out, f'{name}.mp3')); res[name] = 'ok'
        except Exception as e: res[name] = f'FAILED {e}'
    print(json.dumps(res, indent=1))
    if any(v.startswith('FAILED') for v in res.values()):
        sys.exit('some sounds failed: replace them in build.py with ones that downloaded, never skip the hook hit')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'hf/assets')
