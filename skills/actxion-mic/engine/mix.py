#!/usr/bin/env python3
"""THE MIC mix: voices on top (already levelled per line), a synthesised bed (street: rain + crowd murmur; indoors: louder murmur),
Mixkit effects on cue, one clean master gain to -14 LUFS.   python3 mix.py <silent.mp4> <out.mp4>"""
import json, subprocess, sys, re, os, tempfile
video, out = sys.argv[1:3]
M = json.load(open('mix.json')); END, SFX, B = M['end'], M['sfx'], M['beats']
OUT = M.get('set', 'street') == 'street'
def measure(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])
EC = B['endcard']
inputs = ['-i', 'hf/assets/voice.wav',
          '-f', 'lavfi', '-t', str(END), '-i', 'anoisesrc=color=white:sample_rate=48000:seed=7',
          '-f', 'lavfi', '-t', str(END), '-i', 'anoisesrc=color=brown:sample_rate=48000:seed=11']
for f, s, v in SFX: inputs += ['-i', f'hf/assets/sfx/{f}.wav']
fc = [f'[0:a]aresample=48000,highpass=f=80,apad=whole_dur={END}[vo]',
      # rain: hiss with a little stereo-free shimmer, under everything, out over the end card
      f'[1:a]highpass=f=1400,lowpass=f=7500,volume={-31 if OUT else -60}dB,tremolo=f=7:d=0.15,afade=t=in:d=0.4,afade=t=out:st={EC}:d=1.2[rain]',
      # crowd murmur: low band of brown noise breathing slowly, louder on the wide shots
      f'[2:a]bandpass=f=420:width_type=h:w=520,volume={-17 if OUT else -14}dB,tremolo=f=0.35:d=0.5,afade=t=in:d=0.6,afade=t=out:st={EC}:d=1.2[crowd]']
labels = []
for n, (f, s, v) in enumerate(SFX):
    d = int(max(0, s) * 1000)
    fc.append(f'[{3+n}:a]aresample=48000,volume={v*1.6:.3f},adelay={d}|{d}[s{n}]'); labels.append(f'[s{n}]')
fc.append(f'[vo][rain][crowd]{"".join(labels)}amix=inputs={3+len(labels)}:normalize=0:duration=first,atrim=duration={END},alimiter=limit=0.6:attack=5:release=60:level=false[a]')
tmp = tempfile.mkdtemp(); raw = os.path.join(tmp, 'mix.wav')
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', '[a]', '-c:a', 'pcm_s24le', raw], check=True)
I, P = measure(raw); gain = -13.2 - I
R = M.get('rec')
vin, vmap, vfc = ['-i', video], '0:v', []
if R:   # lay the real app recording onto the phone screen (rounded corners, fade in/out)
    HERE = os.path.dirname(os.path.abspath(__file__)); appd = os.environ.get('MIC_APP', os.path.join(HERE, 'app'))
    vin += ['-ss', str(R['in']), '-t', str(R['out'] - R['in']), '-i', os.path.join(appd, R['file']), '-loop', '1', '-i', os.path.join(appd, 'screen-mask.png')]
    d = R['t1'] - R['t0']
    vfc = ['-filter_complex', f"[1:v]setpts=(PTS-STARTPTS)/{R['speed']},fps=30,scale={R['w']}:{R['h']},format=yuva420p,tpad=stop_mode=clone:stop_duration={d}[r];"
           f"[2:v]scale={R['w']}:{R['h']},format=gray,trim=duration={d}[m];[r][m]alphamerge,trim=duration={d},fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st={d - .2}:d=0.2:alpha=1,"
           f"setpts=PTS-STARTPTS+{R['t0']}/TB[rr];[0:v][rr]overlay={R['x']}:{R['y']}:eof_action=pass[v]"]
    vmap = '[v]'
nin = len([x for x in vin if x == '-i'])
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *vin, '-i', raw, *vfc, '-map', vmap, '-map', f'{nin}:a',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-maxrate', '10M', '-bufsize', '20M',
                '-af', f'volume={gain:.2f}dB,alimiter=limit=0.7:level=false:attack=5:release=60,aresample=48000',
                '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', '-shortest', out], check=True)
fI, fP = measure(out)
print(f'raw {I:.1f} LUFS | gain {gain:+.1f} | final {fI:.1f} LUFS peak {fP:.1f} dBFS')
