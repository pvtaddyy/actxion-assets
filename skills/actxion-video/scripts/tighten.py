#!/usr/bin/env python3
"""Pass 01 follow-up (tighten the cut): shorten every pause over 0.4 s in the voiceover,
keeping about 0.1 s of breath each side, and re-time words.json to match.

    python3 tighten.py voice.mp3 words.json voice-tight.wav words-tight.json [--keep 0.28]

--keep is the pause length left inside a sentence (default 0.28 s: 0.1 s breath + a short beat);
sentence ends keep 0.45 s, and a "..." in the script keeps 0.5 s.
"""
import json
import subprocess
import sys
import tempfile
import wave

import imageio_ffmpeg
import numpy as np

SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()


def main():
    a = sys.argv[1:]
    keep = 0.28
    if "--keep" in a:
        i = a.index("--keep"); keep = float(a[i + 1]); del a[i:i + 2]
    src, wj, out_wav, out_json = a
    tmp = tempfile.mktemp(suffix=".wav")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(SR), tmp], check=True)
    with wave.open(tmp) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).copy()
    W = json.load(open(wj))
    words = W["words"]
    pieces, shift, cut_total = [], 0.0, 0.0
    cursor = 0
    new = [dict(w) for w in words]
    for i in range(len(words) - 1):
        gap0, gap1 = words[i]["e"], words[i + 1]["s"]
        gap = gap1 - gap0
        w = words[i]["w"]
        # a full stop / question gets a fuller beat than a pause inside a sentence
        want = 0.5 if w.endswith("...") else (keep + 0.17 if w[-1:] in ".?!" else keep)
        if gap > 0.4 and gap > want:
            # keep breath after the word and before the next one, drop the middle
            c0 = int((gap0 + want / 2) * SR)
            c1 = int((gap1 - want / 2) * SR)
            pieces.append(x[cursor:c0])
            cursor = c1
            removed = (c1 - c0) / SR
            cut_total += removed
            for j in range(i + 1, len(words)):
                new[j]["s"] = round(new[j]["s"] - removed, 3)
                new[j]["e"] = round(new[j]["e"] - removed, 3)
    pieces.append(x[cursor:])
    y = np.concatenate(pieces)
    # 4 ms fades at each join are inaudible; a short global fade avoids a click at the very end
    y = y.astype(np.float32)
    y[-480:] *= np.linspace(1, 0, 480)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes())
    W2 = {"words": new, "pauses": [], "dur": round(len(y) / SR, 3), "cut": round(cut_total, 3)}
    json.dump(W2, open(out_json, "w"), indent=1)
    print(json.dumps({"path": out_wav, "dur": W2["dur"], "cut_secs": W2["cut"]}))


if __name__ == "__main__":
    main()
