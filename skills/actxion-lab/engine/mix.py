#!/usr/bin/env python3
"""Crisp mix (v3): voice levelled once, effects untouched and on cue, music only in moments, one clean master gain.
   python3 mix.py <silent_video.mp4> <out.mp4> [--music path.mp3] [--music-at 20]
Reads mix.json (sfx list + beats + end) written by build.py. No compressors, no ducking, no loudnorm on the mix
(ghost-editor lesson: level the voice first, never squeeze the finished mix).
"""
import json, subprocess, sys, re, os, tempfile, shutil
FF = shutil.which('ffmpeg')
if not FF:
    import imageio_ffmpeg; FF = imageio_ffmpeg.get_ffmpeg_exe()

args = sys.argv[1:]
music, music_at = 'hf/assets/music.mp3', 20.0
if '--music' in args: i = args.index('--music'); music = args[i + 1]; del args[i:i + 2]
if '--music-at' in args: i = args.index('--music-at'); music_at = float(args[i + 1]); del args[i:i + 2]
video, out = args
M = json.load(open('mix.json')); B, END, SFX = M['beats'], M['end'], M['sfx']
SFX_GAIN = 2.0          # effects sit where they did in v1 relative to the voice (v1 voice was 8 dB quieter)

def measure(path):
    r = subprocess.run([FF, '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])

vo_gain = -16.0 - measure('hf/assets/voice.wav')[0]
END_MUSIC = END - 2.8                               # music moment over the end card

inputs = ['-i', 'hf/assets/voice.wav', '-ss', str(music_at), '-t', '3.2', '-i', music]
for f, s, v in SFX: inputs += ['-i', f'hf/assets/sfx/{f}.wav']
fc = [f'[0:a]aresample=48000,highpass=f=70,volume={vo_gain:.2f}dB,apad=whole_dur={END}[vo]',
      f'[1:a]aresample=48000,volume=-9dB,afade=t=in:d=0.35,afade=t=out:st=1.9:d=1.3,adelay={int(END_MUSIC*1000)}|{int(END_MUSIC*1000)}[mu]']
labels = []
for n, (f, s, v) in enumerate(SFX):
    d = int(max(0, s) * 1000)
    fc.append(f'[{2+n}:a]aresample=48000,volume={v*SFX_GAIN:.3f},adelay={d}|{d}[s{n}]'); labels.append(f'[s{n}]')
fc.append(f'[vo][mu]{"".join(labels)}amix=inputs={2+len(labels)}:normalize=0:duration=first,atrim=duration={END},alimiter=limit=0.6:attack=5:release=60:level=false[a]')
tmp = tempfile.mkdtemp(); raw = os.path.join(tmp, 'mix.wav')
subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '[a]', '-c:a', 'pcm_s24le', raw], check=True)
I, P = measure(raw)
gain = -12.7 - I   # the limiter takes about 0.9 dB back
subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', video, '-i', raw, '-map', '0:v', '-map', '1:a',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
                '-af', f'volume={gain:.2f}dB,alimiter=limit=0.7:level=false:attack=5:release=60,aresample=48000',
                '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', out], check=True)
fI, fP = measure(out)
print(f'voice +{vo_gain:.1f} dB | raw mix {I:.1f} LUFS peak {P:.1f} | master gain {gain:+.1f} dB | final {fI:.1f} LUFS peak {fP:.1f} dBFS')
