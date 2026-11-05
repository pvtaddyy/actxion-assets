#!/usr/bin/env python3
"""ACTXION reel builder: spec.json + voice + words.json -> finished 1080x1920 MP4 + cover.

    python3 build.py spec.json out.mp4 [--plan] [--stills 0.5,4,12]

--plan   only print the motion plan and caption key words (pass 03/04 review), render nothing
--stills only render those moments to <out>-frames/ (fast check before the full render)

Runs the five passes of the reel edit in order, from one spec:
 01 words.json (made by words.py) times everything
 02 cut-outs (made by cutout.py) are the "photo" of player/versus scenes
 03 captions: 1-3 words at a time on the word, one key word per sentence big (spec "keywords")
 04 motion: one scene per idea, each fired on its trigger word ("at")
 05 sound: hit on frame one, whoosh on each scene change, taps on list items, ticks on counts,
    buzz on a red card, chime to close, voice on top, -14 LUFS (mix.py)
spec keys: voice, words, scenes[], keywords[], header{text,key[],at}, accent, credit, mark, tail, sfx[]
Scene "at" = a spoken word ("penalty", "two#2" = second "two") or seconds (3.2).
"""
import json
import os
import re
import subprocess
import sys

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "engine")
FF = imageio_ffmpeg.get_ffmpeg_exe()
PHOTO_KEYS = ("photo", "bgPhoto", "homeCrest", "awayCrest")


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


class Clock:
    def __init__(self, words):
        self.words = words
        self.cur = 0

    def at(self, ref, advance=True):
        if isinstance(ref, (int, float)):
            return float(ref)
        name, _, nth = str(ref).partition("#")
        nth = int(nth or 1)
        key = norm(name)
        seen = 0
        for i in range(self.cur, len(self.words)):
            if norm(self.words[i]["w"]).startswith(key):
                seen += 1
                if seen == nth:
                    if advance:
                        self.cur = i
                    return self.words[i]["s"]
        raise SystemExit(f'trigger word "{ref}" not found after word {self.cur} ("{self.words[self.cur]["w"]}")')


def captions(words, keywords, dur):
    keys = {norm(k.lstrip("!")): k.startswith("!") for k in keywords}
    chunks, cur = [], []
    used_key = False

    def flush():
        nonlocal cur
        if cur:
            chunks.append(cur)
        cur = []

    for i, w in enumerate(words):
        n = norm(w["w"])
        is_key = n in keys
        gap = words[i]["s"] - words[i - 1]["e"] if i else 0
        if is_key:
            flush(); chunks.append([dict(w, k=True, hot=keys[n])]); continue
        if cur and (len(cur) == 3 or gap > 0.3 or re.search(r"[.,?!…]$", cur[-1]["w"])):
            flush()
        cur.append(dict(w, k=False))
    flush()
    out = []
    for j, ch in enumerate(chunks):
        s = ch[0]["s"]
        nxt = chunks[j + 1][0]["s"] if j + 1 < len(chunks) else min(dur, ch[-1]["e"] + 0.6)
        e = max(nxt, s + 0.4)
        if out and s < out[-1]["e"]:
            s = out[-1]["e"]
        parts = [{"t": re.sub(r"[.,…;:]+$", "", p["w"]).replace("...", ""), "k": p["k"], "hot": p.get("hot", False)} for p in ch]
        out.append({"s": round(s, 3), "e": round(max(e, s + 0.4), 3), "parts": parts})
    return out


SERIES_MUSIC = {"pick your side": "drive", "head to head": "drive", "fans say": "tense",
                "combined xi": "upbeat", "then and now": "cinematic"}


def sound_plan(spec, scenes, words, dur):
    """Football sound design: the kit (sfx_kit.py) on the motion cues, one reason per sound.
    Layers: voice on top; a Mixkit music bed by series mood (spec "music": mood name, file, or "none");
    optional crowd bed (spec "crowd": true); then the moments below. Never meme sounds, never music
    near voice level, never two big hits within 2 s."""
    series = str(spec.get("series", "pick your side")).lower()
    music = spec.get("music", next((m for k, m in SERIES_MUSIC.items() if k in series), "drive"))
    music = None if music in (None, "none", "") else music
    cues = []

    def add(t, sfx, why, **kw):
        cues.append(dict(t=round(max(0.0, t), 3), sfx=sfx, why=why, **kw))

    add(0.0, "kick", "frame one: a ball being struck, the hook lands")
    add(0.0, "boom", "frame one: weight under the hook claim", gain=0.7)
    if spec.get("crowd"):
        add(0.0, "bed", "match-day crowd under the whole video")
    whooshes = ["whoosh", "whoosh2", "whoosh"]
    for i, sc in enumerate(scenes):
        s0 = sc["s"]
        if i:
            if sc["type"] in ("versus", "ask"):
                add(s0 - 1.1, "riser", "builds into the A or B moment", gain=0.9)
                add(s0 - 0.25, "whoosh2", "sucks into the reveal")
            else:
                add(s0 - 0.12, whooshes[i % len(whooshes)], f"scene change into {sc['type']}")
        t = sc["type"]
        if t == "score":
            for st in sc["states"][1:]:
                add(st["t"], "roar", f"goal: {st['h']}-{st['a']}", dur=1.6)
                add(st["t"], "tap", "the digit rolls")
        elif t == "stat":
            for k in range(12):
                add(s0 + k * 0.075, "count", "counter ticking" if k == 0 else "", gain=0.8)
            add(s0 + sc.get("countFor", 0.9), "impact", f"{sc.get('value')} {sc.get('unit', '')} lands", gain=0.8)
        elif t == "list":
            for it in sc["items"]:
                add(it["t"], "tap", f"tick: {it['text'][:30]}")
        elif t == "compare":
            for r in sc["rows"]:
                add(r["t"], "tap", f"bar grows: {r['label']}")
        elif t == "pitch":
            for k in range(len(sc["players"])):
                add(s0 + 0.3 + k * 0.07, "count", "player pops onto the pitch" if k == 0 else "", gain=0.6)
            add(s0 + 0.2, "yell", "stadium noise as the XI walks out", dur=1.8, gain=0.7)
        elif t == "card":
            add(s0 + 0.05, "whistle", "the referee's whistle")
            if sc.get("colour", "red") == "red":
                add(s0 + 0.35, "groan", "the crowd reacts to the red", dur=2.0)
        elif t == "versus":
            add(s0 + 0.15, "impact", "both sides slam in", gain=0.7)
        elif t == "ask":
            add(s0 + 0.15, "ding", "the question appears")
            add(s0, "chant", "the crowd rises under the ask", dur=max(1.0, dur - s0), gain=0.8)
        if sc.get("source"):
            add(s0 + 0.4, "typing", f"source chip types: {sc['source']}", dur=0.5)
    clk = Clock(words)
    for c in spec.get("sfx", []):
        add(clk.at(c["at"], advance=False) + c.get("offset", 0), c["sfx"], c.get("why", "spec extra"), gain=c.get("gain", 1))
    cues.sort(key=lambda c: c["t"])
    # density: never two big hits within 2 s (keep the earlier one)
    big = {"impact", "boom", "roar", "groan"}
    out, last_big = [], -9.0
    for c in cues:
        if c["sfx"] in big and c["t"] - last_big < 2.0 and c["t"] > 0:
            continue
        if c["sfx"] in big:
            last_big = c["t"]
        out.append(c)
    return out, music


def fileurl(p, base):
    if p.startswith(("http", "file:")):
        return p
    return "file://" + os.path.abspath(os.path.join(base, p))


def main():
    a = sys.argv[1:]
    plan_only = "--plan" in a
    if plan_only:
        a.remove("--plan")
    stills = None
    if "--stills" in a:
        i = a.index("--stills"); stills = a[i + 1]; del a[i:i + 2]
    spec_path, out = a
    base = os.path.dirname(os.path.abspath(spec_path))
    spec = json.load(open(spec_path))
    W = json.load(open(os.path.join(base, spec["words"])))
    words = W["words"]
    voice_end = words[-1]["e"]
    dur = round(voice_end + spec.get("tail", 1.0), 3)
    clk = Clock(words)

    scenes = []
    for sc in spec["scenes"]:
        sc = dict(sc)
        sc["s"] = 0.0 if not scenes else clk.at(sc["at"])
        if sc["type"] == "score":
            sc["states"] = [{"t": (sc["s"] if k == 0 else clk.at(st["at"], advance=False)), "h": st["h"], "a": st["a"], "foot": st.get("foot")}
                            for k, st in enumerate(sc["states"])]
        if sc["type"] == "list":
            sc["items"] = [dict(it, t=clk.at(it["at"], advance=False)) for it in sc["items"]]
        if sc["type"] == "compare":
            sc["rows"] = [dict(r, t=(sc["s"] + 0.3 * k if "at" not in r else clk.at(r["at"], advance=False))) for k, r in enumerate(sc["rows"])]
            for k in ("aPhoto", "bPhoto"):
                if sc.get(k):
                    sc[k] = fileurl(sc[k], base)
        for k in PHOTO_KEYS:
            if sc.get(k):
                sc[k] = fileurl(sc[k], base)
        for side in ("a", "b"):
            if isinstance(sc.get(side), dict) and sc[side].get("photo"):
                sc[side] = dict(sc[side], photo=fileurl(sc[side]["photo"], base))
        scenes.append(sc)
    for i, sc in enumerate(scenes):
        sc["e"] = scenes[i + 1]["s"] if i + 1 < len(scenes) else dur

    hd = spec.get("header")
    header = None
    if hd:
        html = hd["text"]
        for k in hd.get("key", []):
            html = html.replace(k, f'<span class="k">{k}</span>', 1)
        header = {"html": html, "from": 0.0 if hd.get("at") in (None, 0) else Clock(words).at(hd["at"])}

    caps = captions(words, spec.get("keywords", []), dur)

    # sound plan (pass 05): every sound has a reason, printed below for review
    cues, music = sound_plan(spec, scenes, words, dur)
    cues.sort(key=lambda c: c["t"])

    if plan_only or True:
        print("MOTION PLAN (pass 04)")
        print(f"{'time':>6}  {'trigger':<14} {'scene':<8} element")
        for sc in scenes:
            what = sc.get("word") or sc.get("text") or sc.get("label") or sc.get("unit") or sc.get("title") or ""
            print(f"{sc['s']:6.2f}  {str(sc.get('at', 0)):<14} {sc['type']:<8} {what}")
        print("KEY WORDS (pass 03):", ", ".join(" ".join(p["t"] for p in c["parts"]) for c in caps if c["parts"][0]["k"]))
        print("SOUND PLAN (pass 05)   music bed:", music or "none")
        for c in cues:
            print(f"{c['t']:6.2f}  {c['sfx']:<8} {c.get('why', '')}")
        print(f"DURATION {dur}s, {len(caps)} captions, {len(cues)} sound cues")
    if plan_only:
        return

    tl = {"fps": 30, "dur": dur, "accent": spec.get("accent", "#E61E28"), "accentHi": spec.get("accentHi", "#FF4A52"),
          "header": header, "scenes": scenes, "captions": caps, "credit": spec.get("credit", ""),
          "mark": fileurl(spec["mark"], base) if spec.get("mark") else None}
    stem = os.path.splitext(out)[0]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    tl_path = stem + "-timeline.json"
    json.dump(tl, open(tl_path, "w"), indent=1)
    node = os.environ.get("NODE", "node")
    render = os.path.join(ENGINE, "render.mjs")
    env = dict(os.environ)
    if stills:
        subprocess.run([node, render, tl_path, out, "--ffmpeg", FF, "--stills", stills, "--dir", stem + "-frames"], check=True, env=env)
        print(json.dumps({"frames": stem + "-frames"}))
        return
    silent = stem + "-silent.mp4"
    subprocess.run([node, render, tl_path, silent, "--ffmpeg", FF], check=True, env=env)
    cues_path = stem + "-cues.json"
    json.dump(cues, open(cues_path, "w"))
    audio = stem + "-mix.wav"
    mix = [sys.executable, os.path.join(HERE, "mix.py"), os.path.join(base, spec["voice"]), cues_path, audio, "--dur", str(dur)]
    if music:
        mix += ["--music", music if "." not in music else os.path.join(base, music)]
    r = subprocess.run(mix, check=True, capture_output=True, text=True)
    loud = json.loads(r.stdout.strip().splitlines()[-1])
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", silent, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-t", str(dur), "-movflags", "+faststart", out], check=True)
    # cover: the frame with the first big word on screen
    cover_t = spec.get("cover_t", 0.6)
    cover = stem + "-cover.jpg"
    subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(cover_t), "-i", silent, "-frames:v", "1", "-q:v", "2", cover], check=True)
    for f in (silent, cues_path):
        os.remove(f)
    print(json.dumps({"path": out, "cover": cover, "dur": dur, "lufs": loud["lufs"], "true_peak": loud["true_peak"]}))


if __name__ == "__main__":
    main()
