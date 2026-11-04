#!/usr/bin/env python3
"""Voiceover from a script with Kokoro-82M (Apache-2.0 weights, MIT runtime: free for commercial use).

    python3 voice.py script.txt voice.wav [--voice bm_george] [--speed 1.08]

Needs Python 3.10+ and: pip install kokoro-onnx soundfile
The model (~330 MB) downloads once to ~/.cache/kokoro from the kokoro-onnx GitHub release.
ElevenLabs direction tags like [pause] are removed; "..." gives a natural pause.
British male voices: bm_george (default), bm_fable, bm_lewis, bm_daniel. Female: bf_emma, bf_isabella.
Credit in the YouTube description: "Voice: Kokoro-82M (Apache 2.0)".
"""
import os
import re
import sys
import urllib.request

REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
CACHE = os.path.expanduser("~/.cache/kokoro")


def fetch(name):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if not os.path.exists(p) or os.path.getsize(p) < 1_000_000:
        urllib.request.urlretrieve(REL + name, p + ".part")
        os.replace(p + ".part", p)
    return p


def main():
    a = sys.argv[1:]
    voice, speed = "bm_george", 1.08
    if "--voice" in a:
        i = a.index("--voice"); voice = a[i + 1]; del a[i:i + 2]
    if "--speed" in a:
        i = a.index("--speed"); speed = float(a[i + 1]); del a[i:i + 2]
    src, out = a
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(fetch("kokoro-v1.0.onnx"), fetch("voices-v1.0.bin"))
    text = re.sub(r"\[[^\]]*\]", " ", open(src).read())
    text = re.sub(r"\s+", " ", text).strip()
    lang = "en-gb" if voice.startswith("b") else "en-us"
    samples, sr = k.create(text, voice=voice, speed=speed, lang=lang)
    sf.write(out, samples, sr)
    print(f'{{"path": "{out}", "voice": "{voice}", "secs": {len(samples) / sr:.2f}}}')


if __name__ == "__main__":
    main()
