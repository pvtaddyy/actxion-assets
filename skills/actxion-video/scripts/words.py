#!/usr/bin/env python3
"""Pass 01 (transcribe): voiceover -> words.json with a start and end time for every word.

    python3 words.py voice.mp3 words.json [--script script.txt]

Uses faster-whisper (base.en, CPU, word timestamps). With --script (the exact text the voice
read), the script's own spelling is laid onto the timings, so names are never misheard
("Cunha", not "Kuna"). Also lists every pause over 0.4 s.
words.json = {"words": [{"w": "Matheus", "s": 0.12, "e": 0.48}, ...], "pauses": [[t0, t1], ...], "dur": 31.2}
Needs: pip install faster-whisper
"""
import difflib
import json
import re
import sys


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def main():
    a = sys.argv[1:]
    script = None
    if "--script" in a:
        i = a.index("--script"); script = open(a[i + 1]).read(); del a[i:i + 2]
    src, out = a
    from faster_whisper import WhisperModel
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    segs, info = model.transcribe(src, word_timestamps=True, beam_size=5, vad_filter=False,
                                  initial_prompt=None)  # a script prompt made base.en skip the opening seconds (cloud run, 4 Nov 2026)
    heard = []
    for s in segs:
        for w in s.words:
            heard.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    words = heard
    if script:
        # drop ElevenLabs direction tags like [pause] before aligning
        target = [t for t in re.sub(r"\[[^\]]*\]", " ", script).split() if norm(t)]
        hn = [norm(h["w"]) for h in heard]
        tn = [norm(t) for t in target]
        sm = difflib.SequenceMatcher(a=hn, b=tn, autojunk=False)
        words = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal":
                for k in range(i2 - i1):
                    h = heard[i1 + k]
                    words.append({"w": target[j1 + k], "s": h["s"], "e": h["e"]})
            elif j2 > j1:
                # spread the script's words over the heard span (or a gap after the last word)
                s0 = heard[i1]["s"] if i1 < len(heard) else (words[-1]["e"] if words else 0)
                e0 = heard[i2 - 1]["e"] if i2 > i1 else (heard[i1]["s"] if i1 < len(heard) else s0 + 0.3 * (j2 - j1))
                e0 = max(e0, s0 + 0.12 * (j2 - j1))
                step = (e0 - s0) / (j2 - j1)
                for k in range(j2 - j1):
                    words.append({"w": target[j1 + k], "s": round(s0 + k * step, 3), "e": round(s0 + (k + 1) * step, 3)})
    pauses = [[words[i]["e"], words[i + 1]["s"]] for i in range(len(words) - 1) if words[i + 1]["s"] - words[i]["e"] > 0.4]
    json.dump({"words": words, "pauses": pauses, "dur": round(info.duration, 3)}, open(out, "w"), indent=1)
    print(json.dumps({"path": out, "words": len(words), "dur": round(info.duration, 2), "pauses": len(pauses)}))


if __name__ == "__main__":
    main()
