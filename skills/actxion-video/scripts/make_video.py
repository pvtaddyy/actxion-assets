#!/usr/bin/env python3
"""ACTXION vertical video maker: Still Frame cards + a narrated voiceover -> 1080x1920 MP4.

Usage: python3 make_video.py spec.json out.mp4
spec = {
  "voice": "path/to/en_GB-northern_english_male-medium.onnx",
  "slides": [{"image": "card1.png", "say": "Line the narrator reads over this card"}, ...],
  "end_secs": 1.2          # optional hold on the last card after the voice stops
}
Each card is shown for as long as its line takes to say (at least 2.2 s), with a slow push-in,
on a blurred, darkened copy of itself so the 4:5 card fills a 9:16 screen. Needs Pillow,
imageio-ffmpeg and piper-tts (pip install pillow imageio-ffmpeg piper-tts).
"""
import json
import os
import subprocess
import sys
import tempfile
import wave

import imageio_ffmpeg
from PIL import Image, ImageEnhance, ImageFilter

W, H, FPS = 1080, 1920, 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def tts(voice, text, path):
    with wave.open(path, "wb") as w:
        voice.synthesize_wav(text, w)
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def canvas(card_path, path):
    card = Image.open(card_path).convert("RGB")
    bg = card.copy()
    scale = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.45)
    fg = card.resize((W, int(card.height * W / card.width)))
    bg.paste(fg, (0, (H - fg.height) // 2))
    bg.save(path, quality=95)


def segment(still, secs, path):
    frames = max(1, round(secs * FPS))
    # slow push-in from 100% to 106% across the shot
    vf = (f"scale={W * 2}:{H * 2},zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-i", still, "-vf", vf,
                    "-frames:v", str(frames), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20", path],
                   check=True)


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    from piper import PiperVoice
    voice = PiperVoice.load(spec["voice"])
    tmp = tempfile.mkdtemp(prefix="actxion-video-")
    clips, audio, total = [], [], 0.0
    n = len(spec["slides"])
    for i, s in enumerate(spec["slides"]):
        wav = os.path.join(tmp, f"{i:02d}.wav")
        spoken = tts(voice, s["say"], wav)
        secs = max(2.2, spoken + 0.35) + (spec.get("end_secs", 1.2) if i == n - 1 else 0)
        still = os.path.join(tmp, f"{i:02d}.jpg")
        canvas(s["image"], still)
        clip = os.path.join(tmp, f"{i:02d}.mp4")
        segment(still, secs, clip)
        clips.append(clip)
        audio.append((wav, secs))
        total += secs
    with open(os.path.join(tmp, "v.txt"), "w") as f:
        f.writelines(f"file '{c}'\n" for c in clips)
    video = os.path.join(tmp, "video.mp4")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(tmp, "v.txt"), "-c", "copy", video], check=True)
    # each line starts when its card appears
    inputs, filters, t = [], [], 0.0
    for k, (wav, secs) in enumerate(audio):
        inputs += ["-i", wav]
        filters.append(f"[{k + 1}:a]adelay={int(t * 1000)}|{int(t * 1000)}[a{k}]")
        t += secs
    mix = "".join(f"[a{k}]" for k in range(len(audio)))
    filters.append(f"{mix}amix=inputs={len(audio)}:normalize=0,apad[aout]")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", video, *inputs, "-filter_complex", ";".join(filters),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print(json.dumps({"out": out, "seconds": round(total, 1), "slides": n}))


if __name__ == "__main__":
    main()
