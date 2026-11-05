#!/usr/bin/env python3
"""The ACTXION sound kit: football sounds for the reels, fetched once per machine.

    python3 sfx_kit.py            # fetch + prepare every sound into ~/.cache/actxion-sfx/
    python3 sfx_kit.py --list     # show the kit

Two sources, both cleared for commercial use:
  mixkit  Mixkit Free SFX licence: commercial use OK, no credit, but the files may NOT be
          redistributed as-is, so they are never committed: every run downloads them from
          assets.mixkit.co into the cache.
  cc0     Freesound CC0 1.0 (public domain): committed in ../sfx/ (from the ghost-editor kit).
Every file is trimmed of leading silence, cut to its max length, faded out, made 48 kHz mono
and peak-normalised to -1 dBFS, so mix.py sets level by role.
No music, no meme sounds (air horns, vine booms): the brand is a fan verdict, not a meme page.
"""
import json
import os
import subprocess
import sys
import urllib.request

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
CC0 = os.path.join(HERE, "..", "sfx")
CACHE = os.path.expanduser("~/.cache/actxion-sfx")

# name: (source, id or file, max seconds, what it is / when we use it)
KIT = {
    "kick":    ("mixkit", "2108", 0.6, "soccer ball quick kick: frame one of the hook, the first beat"),
    "whoosh":  ("mixkit", "1492", 0.9, "cinematic fast whoosh: scene changes (rotates with whoosh2 and the synth)"),
    "whoosh2": ("cc0", "cc0-whoosh-reverse.wav", 1.2, "reverse whoosh: sucks into a reveal (versus, ask)"),
    "boom":    ("cc0", "cc0-deep-boom.wav", 1.8, "deep boom: the hook claim, under the kick"),
    "impact":  ("mixkit", "788", 1.6, "big cinematic impact: a number landing, the verdict card"),
    "riser":   ("cc0", "cc0-riser-short.wav", 1.6, "short riser: the 1.2 s before the A or B reveal"),
    "roar":    ("mixkit", "3022", 1.8, "stadium joy shouting: a goal on the scoreboard"),
    "groan":   ("mixkit", "463", 2.2, "crowd disappointment: a red card, a miss, a bad stat"),
    "whistle": ("mixkit", "615", 0.9, "short pea whistle: red or yellow card, full time"),
    "yell":    ("mixkit", "2110", 2.5, "crowd yelling at the stadium: controversy, a row"),
    "chant":   ("mixkit", "438", 6.0, "crowd chanting at the stadium: swells under the ask"),
    "bed":     ("mixkit", "2111", 11.0, "crowd at the stadium: the match-day bed under the whole video"),
    "typing":  ("mixkit", "2531", 0.7, "keyboard typing: the source chip typing in"),
    "ding":    ("mixkit", "2870", 1.2, "soft correct-answer ding: the ask card"),
}

# Music beds (Mixkit Free Music licence: commercial social use OK, no attribution; never committed,
# downloaded at render time). Chosen per series mood. Mixed far under the voice by mix.py:
# high-passed at 160 Hz (no hum), about 13 dB under speech, ducked whenever someone talks.
MUSIC = {
    "drive":     ("167", "Brainiac: driving electronic. Pick your side, Head to head"),
    "tense":     ("134", "Deep Techno Ambience: tense, minimal. Fans say... myth tests, controversy"),
    "upbeat":    ("440", "Infinity: upbeat tech. Combined XI, Then and now"),
    "drama":     ("606", "Drawing the Sky: dramatic, cinematic. A big night, a red card, a farewell"),
    "cinematic": ("184", "Vastness: spacious drone. Records, legends"),
}


def music_path(name):
    """Prepared music bed (48 kHz mono, high-passed, -16 LUFS) for a MUSIC mood name."""
    mid, _ = MUSIC[name]
    os.makedirs(CACHE, exist_ok=True)
    dst = os.path.join(CACHE, f"music-{name}.wav")
    if os.path.exists(dst):
        return dst
    raw = os.path.join(CACHE, f"mkm-{mid}.mp3")
    if not os.path.exists(raw):
        req = urllib.request.Request(f"https://assets.mixkit.co/music/{mid}/{mid}.mp3",
                                     headers={"User-Agent": "Mozilla/5.0 (ACTXION video)"})
        open(raw, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", raw, "-af",
                    "highpass=f=160,loudnorm=I=-16:TP=-1.5", "-ac", "1", "-ar", "48000", dst], check=True)
    return dst


def prep(src, dst, maxs):
    fade = min(0.25, maxs / 4)
    af = (f"silenceremove=start_periods=1:start_threshold=-45dB,atrim=0:{maxs},"
          f"afade=t=out:st={max(0, maxs - fade)}:d={fade},loudnorm=I=-16:TP=-1,alimiter=limit=0.89")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-af", af, "-ac", "1", "-ar", "48000", dst], check=True)


def path(name):
    """Local prepared file for a kit sound (fetching it if needed)."""
    src, ref, maxs, _ = KIT[name]
    os.makedirs(CACHE, exist_ok=True)
    dst = os.path.join(CACHE, f"{name}.wav")
    if os.path.exists(dst):
        return dst
    if src == "mixkit":
        raw = os.path.join(CACHE, f"mk-{ref}.mp3")
        if not os.path.exists(raw):
            req = urllib.request.Request(f"https://assets.mixkit.co/active_storage/sfx/{ref}/{ref}-preview.mp3",
                                         headers={"User-Agent": "Mozilla/5.0 (ACTXION video)"})
            open(raw, "wb").write(urllib.request.urlopen(req, timeout=30).read())
    else:
        raw = os.path.join(CC0, ref)
    prep(raw, dst, maxs)
    return dst


if __name__ == "__main__":
    if "--list" in sys.argv:
        for k, (s, r, m, w) in KIT.items():
            print(f"{k:8} {s:6} {r:24} {m:>4}s  {w}")
        for k, (mid, w) in MUSIC.items():
            print(f"music:{k:10} mixkit #{mid:5} {w}")
        sys.exit()
    ok = {}
    for k in KIT:
        try:
            ok[k] = path(k)
        except Exception as e:  # one missing sound never stops a render; mix.py falls back to the synth
            ok[k] = f"FAILED {e}"
    for k in MUSIC:
        try:
            ok["music:" + k] = music_path(k)
        except Exception as e:
            ok["music:" + k] = f"FAILED {e}"
    print(json.dumps(ok, indent=1))
