#!/usr/bin/env python3
"""Time every script word in a finished voice file (ElevenLabs or any whole-script take).
   python3 align_voice.py script.txt voice.mp3 hf/assets/voice.wav words.json
Converts the voice to 48 kHz mono WAV with a 0.15 s lead (build.py expects that), runs faster-whisper with word
timestamps (whisper.cpp if installed), matches words to the script by position with spoken numbers normalised
(121 <-> one hundred and twenty one), fills any gaps by word length, and writes words.json with line numbers.
"""
import json, os, re, sys, shutil, subprocess, difflib, tempfile
src, voice_in, wav_out, out = sys.argv[1:5]
FF = shutil.which('ffmpeg')
if not FF:
    import imageio_ffmpeg; FF = imageio_ffmpeg.get_ffmpeg_exe()
LEAD = 0.15
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()
def n2w(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' and ' + n2w(n % 100))
    if 2010 <= n < 2100: return 'twenty ' + n2w(n - 2000)
    return str(n)
def norm(text):
    toks = []
    for t in re.findall(r"[\w.']+", text.lower()):
        t = t.strip('.')
        if re.fullmatch(r'\d+\.\d+', t):
            w, f = t.split('.'); toks += (['nought'] if w == '0' else n2w(int(w)).split()) + ['point'] + [ONES[int(c)] for c in f]
        elif re.fullmatch(r'\d+', t): toks += n2w(int(t)).split()
        elif t: toks.append(t.replace("'", ''))
    return toks
tmp = tempfile.mkdtemp()
# 48 kHz mono with the lead silence, trimmed of the provider's own leading silence
subprocess.run([FF, '-y', '-loglevel', 'error', '-i', voice_in, '-af',
                f'silenceremove=start_periods=1:start_threshold=-50dB,adelay={int(LEAD*1000)}', '-ac', '1', '-ar', '48000', wav_out], check=True)
p16 = os.path.join(tmp, 'v16.wav')
subprocess.run([FF, '-y', '-loglevel', 'error', '-i', wav_out, '-ac', '1', '-ar', '16000', p16], check=True)
hw = []
from faster_whisper import WhisperModel
m = WhisperModel('base.en', device='cpu', compute_type='int8')
import soundfile as sf
audio, _sr = sf.read(p16, dtype='float32')   # numpy input avoids PyAV version issues
segs, _ = m.transcribe(audio, word_timestamps=True, language='en')
for sg in segs:
    for w in sg.words:
        tk = norm(w.word)
        for j, x in enumerate(tk): hw.append((x, w.start + (w.end - w.start) * j / len(tk), w.start + (w.end - w.start) * (j + 1) / len(tk)))
lines = [l for l in open(src).read().split('\n') if l.strip()]
sw, li = [], []
for i, l in enumerate(lines):
    for w in l.split(): sw.append(w); li.append(i)
sn = [re.sub(r"[^\w]", '', x.lower()) for x in sw]
sm = difflib.SequenceMatcher(None, sn, [h[0] for h in hw], autojunk=False)
tt = [None] * len(sw); matched = 0
for x, y, size in sm.get_matching_blocks():
    for q in range(size): tt[x + q] = (hw[y + q][1], hw[y + q][2]); matched += 1
i = 0
while i < len(sw):
    if tt[i] is None:
        j = i
        while j < len(sw) and tt[j] is None: j += 1
        a0 = tt[i - 1][1] if i > 0 else LEAD; a1 = tt[j][0] if j < len(sw) else a0 + .3 * (j - i)
        L = [len(sn[q]) + 1 for q in range(i, j)]; tot = sum(L); c = a0
        for q in range(i, j): d = (a1 - a0) * L[q - i] / tot; tt[q] = (c, c + d); c += d
        i = j
    else: i += 1
json.dump([{'w': sw[q], 's': round(tt[q][0], 3), 'e': round(tt[q][1], 3), 'line': li[q]} for q in range(len(sw))], open(out, 'w'), indent=0)
print(json.dumps({'words': len(sw), 'matched': matched, 'secs': round(tt[-1][1], 2)}))
