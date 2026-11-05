#!/usr/bin/env python3
"""THE MIC: lay the voice lines on one timeline (voice/<id>.mp3 from ElevenLabs, else voice/<id>-kokoro.wav).
   python3 lines.py   (reads script.tsv + voice/<id>.mp3 (ElevenLabs) or voice/<id>-kokoro.wav)
Writes hf/assets/voice.wav, words.json (w,s,e,line,who), timeline.json (lines with start/end + loudness envelope)."""
import csv, json, os, re, subprocess, wave, numpy as np

WHISPER = os.environ.get('WHISPER_MODEL', os.path.expanduser('~/.claude/skills/actxion-motion/assets/ggml-base.en.bin'))
import shutil
def word_times(wav16):
    '''[(start, end)] per word: whisper.cpp on a Mac, faster-whisper in the cloud.'''
    if shutil.which('whisper-cli') and os.path.exists(WHISPER):
        subprocess.run(['whisper-cli', '-m', WHISPER, '-f', wav16, '-ml', '1', '-sow', '-oj', '-of', wav16 + '.wh'], capture_output=True)
        wh = [x for x in json.load(open(wav16 + '.wh.json'))['transcription'] if x['text'].strip()]
        return [(a['offsets']['from'] / 1000, a['offsets']['to'] / 1000) for a in wh]
    from faster_whisper import WhisperModel
    m = WhisperModel('base.en', device='cpu', compute_type='int8')
    segs, _ = m.transcribe(wav16, word_timestamps=True, language='en')
    return [(w.start, w.end) for s in segs for w in s.words]
SR = 48000
def gap_for(i, who): return .25 if i == 0 else (.55 if who == 'MIC' else .4)   # silence before each line
FPS = 30

def sh(*a): return subprocess.run(a, check=True, capture_output=True, text=True)

def load(path):
    tmp = path + '.48k.wav'
    # trim silence at both ends, mono 48k
    sh('ffmpeg', '-y', '-v', 'error', '-i', path, '-af',
       'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
       'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,loudnorm=I=-16:TP=-2:LRA=7',
       '-ar', str(SR), '-ac', '1', tmp)
    with wave.open(tmp) as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x

rows = list(csv.DictReader(open('script.tsv'), delimiter='\t'))
track, words, lines, t = [], [], [], 0.0
for n, r in enumerate(rows):
    src = f"voice/{r['id']}.mp3" if os.path.exists(f"voice/{r['id']}.mp3") else f"voice/{r['id']}-kokoro.wav"
    x = load(src)
    gap = gap_for(n, r['who'])
    track.append(np.zeros(int(gap * SR), np.float32)); t += gap
    start = t; dur = len(x) / SR
    # word times: whisper.cpp on this line, script spelling laid over
    sh('ffmpeg', '-y', '-v', 'error', '-i', src + '.48k.wav', '-ar', '16000', '-ac', '1', src + '.16k.wav')
    wh = word_times(src + '.16k.wav')
    script = re.sub(r'\[[^\]]*\]', ' ', r['text']).split()
    if len(wh) == len(script):
        times = wh
    else:   # spread script words over the voiced span by character length
        print('word count differs', r['id'], len(script), len(wh))
        a0 = wh[0][0] if wh else 0.05; a1 = wh[-1][1] if wh else dur - .05
        L = [len(w) + 1 for w in script]; c = np.cumsum([0] + L) / sum(L)
        times = [(a0 + (a1 - a0) * c[i], a0 + (a1 - a0) * c[i + 1]) for i in range(len(script))]
    for wd, (a, b) in zip(script, times):
        words.append({'w': wd, 's': round(start + a, 3), 'e': round(start + min(b, dur), 3), 'line': r['id'], 'who': r['who']})
    # loudness envelope at FPS for talking animation
    hop = SR // FPS
    env = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]
    m = max(env) or 1
    lines.append({'id': r['id'], 'who': r['who'], 's': round(start, 3), 'e': round(start + dur, 3),
                  'env': [round(v / m, 2) for v in env], 'src': os.path.basename(src)})
    track.append(x); t += dur
track.append(np.zeros(int(.1 * SR), np.float32))
y = np.concatenate(track)
os.makedirs('hf/assets', exist_ok=True)
with wave.open('hf/assets/voice.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(words, open('words.json', 'w'), indent=0)
json.dump({'lines': lines, 'voice_end': round(t, 3)}, open('timeline.json', 'w'))
for l in lines: print(l['id'], l['who'], l['s'], l['e'], l['src'])
print('voice ends', round(t, 2))
