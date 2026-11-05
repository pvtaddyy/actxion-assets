#!/usr/bin/env python3
"""Voice a script one line at a time with Kokoro, join with fixed gaps, and time every word.
   ~/.venvs/media/bin/python voice_lines.py script.txt hf/assets/voice.wav words.json [--voice bm_fable] [--speed 1.1]
Line starts are exact (we placed them); words inside a line come from whisper.cpp, run per line,
matched to the script by position with spoken numbers normalised, so nothing drifts.
"""
import sys, os, re, json, subprocess, tempfile, difflib
import numpy as np, soundfile as sf, shutil

a = sys.argv[1:]
voice, speed = 'bm_fable', 1.1
if '--voice' in a: i = a.index('--voice'); voice = a[i + 1]; del a[i:i + 2]
if '--speed' in a: i = a.index('--speed'); speed = float(a[i + 1]); del a[i:i + 2]
src, out_wav, out_words = a
WHISPER_MODEL = os.path.expanduser(os.environ.get('WHISPER_MODEL', '~/.claude/skills/actxion-motion/assets/ggml-base.en.bin'))
LEAD, GAP_LINE, GAP_SHORT = 0.15, 0.24, 0.12     # silence before the first line, after a full stop, after a comma-ish line

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kokoro_onnx import Kokoro
from voice import fetch                      # downloads the Kokoro model once (GitHub release)
k = Kokoro(fetch('kokoro-v1.0.onnx'), fetch('voices-v1.0.bin'))
FF = shutil.which('ffmpeg')
if not FF:
    import imageio_ffmpeg; FF = imageio_ffmpeg.get_ffmpeg_exe()
USE_CPP = bool(shutil.which('whisper-cli')) and os.path.exists(WHISPER_MODEL)
_fw = None
def whisper_words(p16):
    """[(token, start, end)] for one line: whisper.cpp if installed, else faster-whisper (cloud)."""
    global _fw
    out = []
    if USE_CPP:
        subprocess.run(['whisper-cli', '-m', WHISPER_MODEL, '-f', p16, '-ml', '1', '-sow', '-oj', '-of', p16[:-4]], capture_output=True)
        for s in json.load(open(p16[:-4] + '.json'))['transcription']:
            out.append((s['text'], s['offsets']['from'] / 1000, s['offsets']['to'] / 1000))
    else:
        if _fw is None:
            from faster_whisper import WhisperModel
            _fw = WhisperModel('base.en', device='cpu', compute_type='int8')
        segs, _ = _fw.transcribe(p16, word_timestamps=True, language='en')
        for sg in segs:
            for w in sg.words: out.append((w.word, w.start, w.end))
    return out

ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()
def n2w(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ('' if n % 10 == 0 else ' ' + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' and ' + n2w(n % 100))
    if 2000 <= n < 2100: return 'twenty ' + n2w(n - 2000) if n > 2009 else 'two thousand' + ('' if n == 2000 else ' and ' + n2w(n - 2000))
    return str(n)
def norm_tokens(text):
    """whisper text -> lowercase word tokens, digits spelled out ('121' -> one hundred and twenty one, '0.69' -> nought point six nine)."""
    toks = []
    for t in re.findall(r"[\w.']+", text.lower()):
        t = t.strip('.')
        if re.fullmatch(r'\d+\.\d+', t):
            whole, frac = t.split('.'); toks += (['nought'] if whole == '0' else n2w(int(whole)).split()) + ['point'] + [ONES[int(c)] for c in frac]
        elif re.fullmatch(r'\d+', t): toks += n2w(int(t)).split()
        elif t: toks.append(t)
    return [x.replace("'", '') for x in toks]

lines = [l.strip() for l in open(src).read().split('\n') if l.strip()]
sr = 24000; pieces = [np.zeros(int(LEAD * sr), dtype=np.float32)]; t = LEAD; words = []
tmp = tempfile.mkdtemp()
for li, line in enumerate(lines):
    samples, sr = k.create(line, voice=voice, speed=speed, lang='en-gb')
    samples = samples.astype(np.float32)
    # trim Kokoro's own leading/trailing silence
    nz = np.where(np.abs(samples) > 0.025)[0]
    if len(nz): samples = samples[max(0, nz[0] - int(.03 * sr)): nz[-1] + int(.06 * sr)]
    dur = len(samples) / sr
    p = os.path.join(tmp, f'l{li}.wav'); sf.write(p, samples, sr)
    p16 = p.replace('.wav', '-16.wav')
    subprocess.run([FF, '-loglevel', 'error', '-y', '-i', p, '-ar', '16000', '-ac', '1', p16], check=True)
    hw = []
    for text, a0, a1 in whisper_words(p16):
        toks = norm_tokens(text)
        if not toks: continue
        for j, tk in enumerate(toks):   # spread a multi-word token (a number) across its span
            hw.append((tk, a0 + (a1 - a0) * j / len(toks), a0 + (a1 - a0) * (j + 1) / len(toks)))
    sw = line.split(); sn = [re.sub(r"[^\w]", '', x.lower()) for x in sw]
    sm = difflib.SequenceMatcher(None, sn, [h[0] for h in hw], autojunk=False)
    tt = [None] * len(sw)
    for x, y, size in sm.get_matching_blocks():
        for q in range(size): tt[x + q] = (hw[y + q][1], hw[y + q][2])
    # fill gaps by character length between known neighbours
    i = 0
    while i < len(sw):
        if tt[i] is None:
            j = i
            while j < len(sw) and tt[j] is None: j += 1
            a0 = tt[i - 1][1] if i > 0 else 0.0
            a1 = tt[j][0] if j < len(sw) else dur
            L = [len(sn[q]) + 1 for q in range(i, j)]; tot = sum(L); c = a0
            for q in range(i, j): d = (a1 - a0) * L[q - i] / tot; tt[q] = (c, c + d); c += d
            i = j
        else: i += 1
    for q, w in enumerate(sw):
        words.append({'w': w, 's': round(t + min(tt[q][0], dur), 3), 'e': round(t + min(tt[q][1], dur), 3), 'line': li})
    pieces.append(samples); t += dur
    gap = GAP_LINE if re.search(r'[.?!]$', line) else GAP_SHORT
    if li < len(lines) - 1: pieces.append(np.zeros(int(gap * sr), dtype=np.float32)); t += gap
audio = np.concatenate(pieces)
sf.write(out_wav.replace('.wav', '-24k.wav'), audio, sr)
subprocess.run([FF, '-loglevel', 'error', '-y', '-i', out_wav.replace('.wav', '-24k.wav'), '-ar', '48000', '-ac', '1', out_wav], check=True)
os.remove(out_wav.replace('.wav', '-24k.wav'))
json.dump(words, open(out_words, 'w'), indent=0)
matched = sum(1 for w in words)
print(json.dumps({'lines': len(lines), 'words': len(words), 'secs': round(len(audio) / sr, 2)}))
