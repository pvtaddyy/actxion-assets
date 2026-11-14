#!/usr/bin/env python3
"""Build the HyperFrames index.html for Sounds Fake: Leicester at 5000-1.  python3 build.py -> hf/index.html"""
import json, re, html, base64
ROOT = 'hf'
words = json.load(open('words.json'))
norm = [re.sub(r"[^\w']", '', w['w'].lower()) for w in words]
def at(phrase, nth=1):
    p = [re.sub(r"[^\w']", '', x.lower()) for x in phrase.split()]
    hit = 0
    for i in range(len(norm) - len(p) + 1):
        if norm[i:i + len(p)] == p:
            hit += 1
            if hit == nth: return round(words[i]['s'], 3)
    raise SystemExit(f'phrase not found: {phrase}')
END = round(words[-1]['e'] + 2.0, 2)
B = dict(hook=0.0, season=at('This season'), ctx=at('Head to Head'), league=at('League games'), kaneAt=at('Kane at Bayern'), r1=at('Round one'),
         goalsY=at('Yamal has ten'), goalsK=at('Kane has four'), r2=at('Round two'), astK=at('Kane eight'), astY=at('Yamal eight'), level=at('Dead level'),
         minutes=at('But Kane'), minK=at('Seven hundred'), minY=at("Yamal's nine"), perMin=at('So per minute'), wK=at('every fifty nine'),
         wY=at('every fifty five'), apart=at('Four minutes apart'), wembley=at('The last time'), scored=at('Yamal scored'), pen=at("Kane's penalty"),
         won=at('Spain won'), madrid=at('This weekend'), ask=at('Kane or Yamal'), oneword=at('One word'), nextq=at('Who do we'), end=END)
CRESTS = ['bay', 'bar', 'spain', 'england']
CREST_DATA = {k: 'data:image/png;base64,' + base64.b64encode(open(f'assets/{k}.png', 'rb').read()).decode() for k in CRESTS}
EP = {'crestData': CREST_DATA, 'beats': B, 'crests': CRESTS, 'colors': {'sky': '#070b16', 'accent': '#ffd54a'}, 'data': {},
  'cams': [
    {'t': 0, 'p': [0, 2.6, 9.5], 'l': [-.6, 2.3, 0], 'fov': 42, 'move': 1},
    {'t': B['season'], 'p': [0, 2.8, 11], 'l': [0, 2.3, 0], 'fov': 42, 'move': 1.0},
    {'t': B['ctx'], 'p': [0, 3.0, 11.5], 'l': [0, 2.4, 0], 'fov': 42, 'move': 1.0},
    {'t': B['r1'], 'p': [0, 3.0, 12.5], 'l': [0, 2.6, 0], 'fov': 42, 'move': 1.0},
    {'t': B['astK'], 'p': [.8, 3.2, 12.5], 'l': [0, 2.6, 0], 'fov': 42, 'move': 2.0},
    {'t': B['minutes'], 'p': [0, 3.0, 12.5], 'l': [0, 2.4, 0], 'fov': 42, 'move': 1.0},
    {'t': B['perMin'], 'p': [0, 3.0, 11.5], 'l': [0, 2.5, 0], 'fov': 42, 'move': 1.0},
    {'t': B['wembley'], 'p': [0, 2.4, 10.5], 'l': [0, 1.6, -1.5], 'fov': 44, 'move': 1.0},
    {'t': B['madrid'], 'p': [0, 2.8, 10.5], 'l': [0, 2.3, 0], 'fov': 42, 'move': 1.0},
    {'t': B['ask'], 'p': [0, 4.5, 13], 'l': [0, 4.4, 0], 'fov': 42, 'move': 1.2},
  ]}
ov = []
def add(id, s, e, inner, kind='title'): ov.append((id, round(s, 3), round(e, 3), inner, kind))
G = lambda s: f'<b>{s}</b>'
SRC = '<div class="src">Data: StatMuse, league games 2026/27, to 8 Nov</div>'
add('t-bdo', 0.05, B['season'], f'{G("BALLON D&#39;OR")}<div class="gs">Harry Kane, 2026</div>')
add('t-edge', B['season'], B['ctx'], f'THIS SEASON<br>{G("YAMAL")} HAS<br>THE EDGE?')
add('r-ctx', B['ctx'], B['league'] + .5, '<div class="rk">HEAD</div><div class="rt">TO HEAD</div>', 'round')
add('ctx', B['league'], B['r1'], '<span>KANE · BAYERN  v  YAMAL · BARÇA · LEAGUE 2026/27</span>', 'chip')
add('r-1', B['r1'], B['goalsY'] - .1, '<div class="rk">ROUND 1</div><div class="rt">GOALS</div>', 'round')
add('n-goals', B['goalsY'], B['r2'], f'<div class="pair"><div data-at="{B["goalsK"] - B["goalsY"]}"><div class="num sm sil">4</div><div class="lab">KANE</div></div><div><div class="num sm">10</div><div class="lab">YAMAL</div></div></div>' + SRC, 'stat')
add('r-2', B['r2'], B['astK'] - .1, '<div class="rk">ROUND 2</div><div class="rt">ASSISTS</div>', 'round')
add('n-ast', B['astK'], B['minutes'], f'<div class="pair"><div><div class="num sm sil">8</div><div class="lab">KANE</div></div><div data-at="{B["astY"] - B["astK"]}"><div class="num sm">8</div><div class="lab">YAMAL</div></div></div>' + SRC, 'stat')
add('st-level', B['level'], B['minutes'], 'DEAD LEVEL', 'stamp')
add('t-min', B['minutes'], B['minK'], f'KANE HAS PLAYED<br>{G("FEWER MINUTES")}')
add('n-min', B['minK'], B['perMin'], f'<div class="pair"><div><div class="num sm sil">712</div><div class="lab">KANE</div></div><div data-at="{B["minY"] - B["minK"]}"><div class="num sm">991</div><div class="lab">YAMAL</div></div></div><div class="sub">league minutes, 2026/27</div>' + SRC, 'stat')
add('t-per', B['perMin'], B['wK'] - .3, f'{G("PER MINUTE")}', 'glitch')
add('n-per', B['wK'] - .3, B['wembley'], f'<div class="lab">A GOAL OR ASSIST EVERY</div><div class="pair"><div><div class="num sm sil">59</div><div class="lab">KANE</div></div><div data-at="{B["wY"] - B["wK"] + .3}"><div class="num sm">55</div><div class="lab">YAMAL</div></div></div><div class="per" data-at="{B["apart"] - B["wK"] + .3}">4 MINUTES APART</div><div class="src">minutes ÷ (goals + assists), StatMuse</div>', 'stat')
add('t-wem', B['wembley'], B['scored'], f'LAST TIME<br>{G("WEMBLEY")}<div class="gs">Nations League, Sept 2026</div>')
add('n-2', B['scored'], B['pen'], '<div class="num">2&#39;</div><div class="lab">YAMAL SCORES</div><div class="src">England 2-3 Spain (Al Jazeera, Flashscore)</div>', 'stat')
add('st-bar', B['pen'] + .5, B['won'], 'KANE PEN: OFF THE BAR', 'stamp')
add('n-won', B['won'], B['madrid'], '<div class="num sm">3-2</div><div class="lab">SPAIN WON</div><div class="sub">at Wembley, 26 Sept 2026</div>', 'stat')
add('t-mad', B['madrid'], B['ask'], f'SPAIN v ENGLAND<br>{G("MADRID")}<div class="gs">15 Nov · 7:45pm UK</div>')
add('ask', B['ask'], END - 1.6, f'<div class="q">KANE</div><div class="or">or</div><div class="q b">YAMAL?</div><div class="next" data-at="{B["nextq"] - B["ask"]}">Who goes head to head next? 👇</div>', 'ask')
for k, s in (('dip-1', B['r1']), ('dip-2', B['perMin']), ('dip-3', B['madrid'])): add(k, s - .1, s + .12, '', 'dip')
DIGITS = [("seven hundred and twelve", "712"), ("nine hundred and ninety one", "991"), ("twenty six twenty seven", "2026/27"),
          ("fifty nine", "59"), ("fifty five", "55"), ("three two", "3-2"), ("ten", "10"), ("four", "4"), ("eight", "8"), ("two", "2")]
KEYW = {'kane', 'yamal', "kane's", "yamal's", 'goals', 'assists', 'level', 'minutes', 'minute', 'wembley', 'bar', 'madrid', 'spain', 'england', 'bayern', 'barcelona', 'edge', 'penalty'}
PAIRS = {('harry', 'kane'), ('lamine', 'yamal'), ('dead', 'level'), ('per', 'minute'), ('every', '59'), ('every', '55')}
HIDE_EXTRA = []
plain = lambda w: re.sub(r"[^\w']", '', w.lower())
toks, i = [], 0
while i < len(words):
    hit = None
    for ph, dg in DIGITS:
        p = ph.split()
        if [plain(x['w']) for x in words[i:i + len(p)]] == p:
            hit = (len(p), dg); break
    if hit:
        n, dg = hit; last = words[i + n - 1]; punct = re.sub(r"^[\w']+", '', last['w'])
        if ' ' in dg: a_, b_ = dg.split(' '); toks.append({'t': a_, 's': words[i]['s'], 'e': words[i]['e'], 'num': True, 'line': words[i]['line']}); toks.append({'t': b_ + punct, 's': last['s'], 'e': last['e'], 'num': False, 'line': last['line']})
        else: toks.append({'t': dg + punct, 's': words[i]['s'], 'e': last['e'], 'num': True, 'line': words[i]['line']})
        i += n
    else:
        w = words[i]; toks.append({'t': w['w'], 's': w['s'], 'e': w['e'], 'num': False, 'line': w['line']}); i += 1
HIDE = [(0, B['ctx'] - .05), (B['ctx'] - .05, B['league']), (B['r1'] - .05, B['goalsY'] - .1), (B['r2'] - .05, B['astK'] - .1), (B['perMin'] - .05, B['wK'] - .3), (B['madrid'] - .05, B['madrid'] + 2.2), (B['ask'] - .05, END + 1)]
hidden = lambda s: any(a <= s < b for a, b in HIDE)
groups, cur = [], []
for j, tk in enumerate(toks):
    if hidden(tk['s']): 
        if cur: groups.append(cur); cur = []
        continue
    cur.append(j)
    nxt = toks[j + 1] if j + 1 < len(toks) else None
    end_p = re.search(r'[.?!,]$', tk['t']) or not nxt or nxt['line'] != tk['line'] or nxt['s'] - tk['e'] > .2
    pair = nxt and (plain(tk['t']), plain(nxt['t'])) in PAIRS
    WEAK = {'a', 'the', 'of', 'in', 'and', 'to', "it's", 'he', 'his', 'is', 'that', 'or', 'but', 'if', 'you', 'since', 'than', 'one'}
    if end_p:
        groups.append(cur); cur = []
    elif len(cur) >= 3 and not pair:
        if plain(toks[cur[-1]]['t']) in WEAK: groups.append(cur[:-1]); cur = cur[-1:]
        else: groups.append(cur); cur = []
if cur: groups.append(cur)
# merge a lonely short word into the next group of the same sentence
merged = []
for g in groups:
    if merged and len(merged[-1]) == 1 and len(toks[merged[-1][0]]['t']) <= 4 and not re.search(r'[.?!,]$', toks[merged[-1][0]]['t']) \
       and len(merged[-1]) + len(g) <= 3 and toks[g[0]]['line'] == toks[merged[-1][0]]['line']:
        merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    s = toks[g[0]]['s'] - .06; e = toks[g[-1]]['e'] + .3
    if gi + 1 < len(groups): e = min(e, toks[groups[gi + 1][0]]['s'] - .07)
    e = max(e, s + .4)
    for a, b2 in HIDE:
        if s < a < e: e = a
    spans = []
    for j in g:
        tk = toks[j]; txt = html.escape(tk['t'].strip('"'))
        cls = 'w k' if (tk['num'] or plain(tk['t']) in KEYW) else 'w'
        spans.append(f'<span class="{cls}" data-ws="{round(tk["s"] - s, 3)}">{txt}</span>')
    n_chars = sum(len(toks[j]['t']) + 1 for j in g)
    size = '' if n_chars <= 17 else (' style="font-size:62px"' if n_chars <= 23 else ' style="font-size:54px"')
    caps.append((f'c{gi}', round(max(.12, s), 3), round(e, 3), f'<span class="ln"{size}>' + ' '.join(spans) + '</span>'))


sfx = [('impact-2', 0.05, .9), ('cinematic-deep-boom', 0.08, .55), ('whoosh-cine', B['season'], .5), ('impact-2', B['season'] + .5, .55),
       ('whoosh-2', B['ctx'] - .05, .7), ('impact-2', B['ctx'] + .3, .7), ('ding-1', B['league'] + 1.0, .4),
       ('riser-1', B['r1'] - 1.0, .4), ('whoosh-2', B['r1'] - .05, .6), ('impact-2', B['goalsY'], .55), ('impact-2', B['goalsK'], .55),
       ('riser-1', B['r2'] - 1.0, .4), ('whoosh-2', B['r2'] - .05, .6), ('impact-2', B['astK'], .5), ('impact-2', B['astY'], .5), ('impact-2', B['level'], .8),
       ('whoosh-cine', B['minutes'], .5), ('whoosh-2', B['minK'], .5), ('whoosh-2', B['minY'], .5),
       ('tech-glitch-1', B['perMin'], .8), ('impact-2', B['wK'] - .3, .5), ('ding-1', B['wK'] + 1.2, .45), ('ding-1', B['wY'] + 1.2, .5), ('impact-2', B['apart'], .6),
       ('cinematic-deep-boom', B['wembley'], .6), ('whoosh-2', B['scored'] - .4, .55), ('impact-2', B['scored'] + .1, .7),
       ('whoosh-2', B['pen'], .5), ('wood-hit', B['pen'] + .45, .9), ('impact-2', B['pen'] + .5, .6), ('impact-2', B['won'], .6),
       ('riser-1', B['madrid'] - 1.0, .4), ('whoosh-cine', B['madrid'], .5), ('impact-2', B['madrid'] + .6, .6),
       ('whoosh-cine', B['ask'], .5), ('ding-1', B['oneword'], .55), ('ding-1', B['nextq'], .5)]
sfx += [('pop-2', B['goalsY'] + .25 + i * .1 + .3, .35) for i in range(0, 10, 2)]
sfx += [('pop-2', B['goalsK'] + .25 + i * .12 + .3, .35) for i in range(4)]
sfx += [('wood-hit', B['astK'] + .2 + i * .1 + .3, .3) for i in range(0, 8, 2)]
sfx += [('wood-hit', B['astY'] + .2 + i * .1 + .3, .3) for i in range(0, 8, 2)]
sfx += [('tick-1', B['wK'] + k * .15, .3) for k in range(8)]
sfx += [('tick-1', B['wY'] + k * .15, .3) for k in range(8)]
def clip(id, s, e, cls, inner, track):
    return f'<div id="{id}" class="clip {cls}" data-start="{s}" data-duration="{round(e - s, 3)}" data-track-index="{track}"><div class="in">{inner}</div></div>'

body = '\n'.join(clip(i, s, e, f'ov {k}', h, 2) for i, s, e, h, k in ov)
capb = '\n'.join(clip(i, s, e, 'cap', h, 3) for i, s, e, h in caps)
import subprocess
import soundfile as _sf
def dur(f): return _sf.info(f'{ROOT}/assets/sfx/{f}.wav').duration
aud = '\n'.join(f'<audio id="sfx{n}" class="clip" src="assets/sfx/{f}.wav" data-start="{round(s, 3)}" data-duration="{round(min(dur(f), END - s - .05), 3)}" data-volume="{v}" data-track-index="{10 + n}"></audio>' for n, (f, s, v) in enumerate(sfx))

json.dump({'sfx': sfx, 'beats': B, 'end': END}, open('mix.json', 'w'), indent=1)
page = open('template.html').read()
page = page.replace('{{EP}}', json.dumps(EP)).replace('{{END}}', str(END)).replace('{{OVERLAYS}}', body).replace('{{CAPTIONS}}', capb).replace('{{SFX}}', '').replace('{{ENDCARD}}', str(round(END - 1.6, 2)))
open(f'{ROOT}/index.html', 'w').write(page)
json.dump(B, open('beats.json', 'w'), indent=1)
print('end', END, 'overlays', len(ov), 'captions', len(caps), 'sfx', len(sfx))
