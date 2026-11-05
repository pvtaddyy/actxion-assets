#!/usr/bin/env python3
"""Pass 05 (sound): voice on top, synthesised SFX on the motion cues, optional music bed ducked
under the voice, mastered to -14 LUFS with true peaks under -1 dB.

    python3 mix.py voice.(mp3|wav) cues.json out.wav [--music bed.mp3] [--dur 31.5]

cues.json = [{"t": 0.0, "sfx": "hit"}, {"t": 2.1, "sfx": "whoosh"}, ...]
SFX kinds (all generated here from noise and sine waves, so nothing is licensed or copied):
  hit     low punch + click, for the hook on frame one and big reveals
  tap     short click, for every tick, tile or checklist item
  whoosh  filtered noise sweep, for every scene change
  riser   rising noise + tone, into a reveal
  chime   two soft bells, to close
  buzz    low sawtooth, for a red card / wrong answer
  count   tiny tick, for numbers counting up
Voice is cleaned (rumble cut below 80 Hz, hiss above 14 kHz, light denoise and compression).
"""
import json
import os
import subprocess
import sys
import tempfile
import wave

import imageio_ffmpeg
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import sfx_kit
except Exception:  # the kit is optional: without it every sound falls back to the synth below
    sfx_kit = None

SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    return e


def lp(x, k):  # one-pole low-pass, k in 0..1
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc)
        y[i] = acc
    return y


_kit_cache = {}


def kit_sound(kind):
    """A prepared football sound from sfx_kit (Mixkit / CC0), or None to fall back to the synth."""
    if sfx_kit is None or kind not in sfx_kit.KIT:
        return None
    if kind not in _kit_cache:
        try:
            _kit_cache[kind] = read_audio(sfx_kit.path(kind))
        except Exception as e:
            print(f"WARN kit sound {kind} unavailable ({e}); using the synth", file=sys.stderr)
            _kit_cache[kind] = None
    return _kit_cache[kind]


FALLBACK = {"kick": "hit", "boom": "hit", "impact": "hit", "whoosh2": "whoosh", "roar": "riser", "groan": "buzz",
            "whistle": "tap", "yell": "riser", "chant": "riser", "typing": "tap", "ding": "chime"}


def sfx(kind):
    k = kit_sound(kind)
    if k is not None:
        return k
    kind = FALLBACK.get(kind, kind)
    if kind == "hit":
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        f = 120 * np.exp(-t * 18) + 45
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.22)
        click = rng.standard_normal(n) * env(n, 0.0005, 0.012) * 0.5
        return 0.9 * body + click
    if kind == "tap":
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1800 * t) * 0.4 + rng.standard_normal(n) * 0.25) * env(n, 0.0005, 0.015)
    if kind == "count":
        n = int(0.04 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * 2600 * t) * env(n, 0.0003, 0.008) * 0.25
    if kind == "whoosh":
        n = int(0.45 * SR)
        noise = rng.standard_normal(n)
        shape = np.sin(np.linspace(0, np.pi, n)) ** 2
        k = np.linspace(0.02, 0.35, n)
        y = np.zeros(n)
        acc = 0.0
        for i in range(n):
            acc += k[i] * (noise[i] - acc)
            y[i] = acc
        return y * shape * 0.9
    if kind == "riser":
        n = int(1.0 * SR)
        t = np.arange(n) / SR
        noise = lp(rng.standard_normal(n), 0.15) * (t / t[-1]) ** 2
        tone = np.sin(2 * np.pi * np.cumsum(200 + 600 * (t / t[-1]) ** 2) / SR) * (t / t[-1]) ** 3 * 0.3
        return (noise * 0.8 + tone)
    if kind == "chime":
        n = int(1.6 * SR)
        t = np.arange(n) / SR
        a = sum(np.sin(2 * np.pi * f * t) * w for f, w in [(1318.5, 0.5), (2637, 0.15), (3951, 0.05)]) * env(n, 0.002, 0.5)
        b = np.zeros(n)
        off = int(0.14 * SR)
        b[off:] = (sum(np.sin(2 * np.pi * f * t) * w for f, w in [(1760, 0.45), (3520, 0.12)]) * env(n, 0.002, 0.6))[: n - off]
        return (a + b) * 0.45
    if kind == "buzz":
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        saw = 2 * ((t * 70) % 1) - 1
        return lp(saw, 0.2) * env(n, 0.005, 0.25) * 0.7
    raise SystemExit(f"unknown sfx {kind}")


def read_audio(path):
    tmp = tempfile.mktemp(suffix=".wav")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), tmp], check=True)
    with wave.open(tmp) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    os.remove(tmp)
    return x


def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    a = sys.argv[1:]
    music = None
    dur = None
    if "--music" in a:
        i = a.index("--music"); music = a[i + 1]; del a[i:i + 2]
    if "--dur" in a:
        i = a.index("--dur"); dur = float(a[i + 1]); del a[i:i + 2]
    voice_path, cues_path, out = a
    tmpd = tempfile.mkdtemp()
    clean = os.path.join(tmpd, "voice.wav")
    # clean the voice: rumble, hiss, light denoise, gentle compression
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", voice_path, "-af",
                    "highpass=f=80,lowpass=f=14000,afftdn=nf=-30,acompressor=threshold=-18dB:ratio=3:attack=5:release=80",
                    "-ac", "1", "-ar", str(SR), clean], check=True)
    v = read_audio(clean)
    total = max(len(v), int((dur or 0) * SR))
    fx = np.zeros(total + SR * 2)
    gains = {"hit": 0.55, "tap": 0.30, "count": 0.25, "whoosh": 0.22, "riser": 0.25, "chime": 0.35, "buzz": 0.35,
             "kick": 0.55, "boom": 0.30, "whoosh2": 0.26, "impact": 0.30, "roar": 0.32, "groan": 0.30,
             "whistle": 0.30, "yell": 0.24, "chant": 0.20, "typing": 0.18, "ding": 0.26}
    cues = json.load(open(cues_path))
    bed = next((c for c in cues if c.get("sfx") == "bed"), None)
    for c in cues:
        if c.get("sfx") == "bed":
            continue
        s = sfx(c["sfx"])
        if c.get("dur"):
            n = int(c["dur"] * SR)
            s = s[:n].copy()
            f = min(len(s), int(0.4 * SR))
            s[-f:] *= np.linspace(1, 0, f)
        s = s * gains.get(c["sfx"], 0.3) * c.get("gain", 1.0)
        i = int(max(0, c["t"]) * SR)
        fx[i:i + len(s)] += s[: len(fx) - i]
    fx = fx[:total]
    mix = np.zeros(total)
    mix[: len(v)] += v
    # duck SFX a little under speech so the voice stays on top
    venv_ = np.convolve(np.abs(np.pad(v, (0, total - len(v)))), np.ones(2400) / 2400, mode="same")
    duck = 1 - 0.45 * np.clip(venv_ / (venv_.max() + 1e-9) * 3, 0, 1)
    mix += fx * duck
    if bed is not None:
        # match-day crowd bed under the whole video: looped with crossfades, ducked hard under speech
        b = sfx("bed")
        if b is not None and len(b) > SR:
            xf = int(0.8 * SR)
            loop = b.copy()
            while len(loop) < total:
                seg = b.copy()
                seg[:xf] *= np.linspace(0, 1, xf)
                loop[-xf:] *= np.linspace(1, 0, xf)
                loop = np.concatenate([loop[:-xf], loop[-xf:] + seg[:xf], seg[xf:]])
            loop = loop[:total]
            fi, fo = int(0.3 * SR), int(1.2 * SR)
            loop[:fi] *= np.linspace(0, 1, fi)
            loop[-fo:] *= np.linspace(1, 0, fo)
            speech = np.clip(venv_ / (venv_.max() + 1e-9) * 3, 0, 1)
            mix += loop * 0.11 * bed.get("gain", 1.0) * (1 - 0.6 * speech)
    if music:
        # a mood name from sfx_kit.MUSIC ("drive", "tense"...) or a file path
        if sfx_kit is not None and music in sfx_kit.MUSIC:
            try:
                music = sfx_kit.music_path(music)
            except Exception as e:
                print(f"WARN music {music} unavailable ({e}); no music", file=sys.stderr)
                music = None
    if music:
        m = read_audio(music)
        start = int(min(len(m) * 0.15, 8 * SR))  # skip a slow intro so the bed is already moving
        m = m[start:]
        m = np.tile(m, int(np.ceil(total / len(m))))[:total]
        fi, fo = int(0.25 * SR), int(1.5 * SR)
        m[:fi] *= np.linspace(0, 1, fi)
        m[-fo:] *= np.linspace(1, 0, fo)
        speech = np.clip(venv_ / (venv_.max() + 1e-9) * 3, 0, 1)
        # about 13 dB under the voice while it talks, comes up a little in the gaps (sidechain-style duck)
        mix += m * 0.16 * (1 - 0.65 * speech)
    pre = os.path.join(tmpd, "pre.wav")
    write(pre, mix * 0.8)
    # two-pass loudness to -14 LUFS, true peak -1 dB
    r = subprocess.run([FF, "-hide_banner", "-i", pre, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1]
    m = json.loads(js)
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    mid = os.path.join(tmpd, "mid.wav")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", pre, "-af", af, "-ar", str(SR), "-ac", "2", mid], check=True)

    def measure(path):
        r = subprocess.run([FF, "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True)
        return json.loads(r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1])

    # loudnorm can stop short of -14 when it protects the peaks: close the gap with gain + a limiter
    gap = -14.0 - float(measure(mid)["input_i"])
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", mid, "-af",
                    f"volume={gap:.2f}dB,alimiter=limit=0.84:attack=2:release=50:level=false", "-ar", str(SR), out], check=True)
    js = measure(out)
    print(json.dumps({"path": out, "lufs": js["input_i"], "true_peak": js["input_tp"]}))


if __name__ == "__main__":
    main()
