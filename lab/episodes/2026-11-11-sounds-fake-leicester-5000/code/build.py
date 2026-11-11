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
B = dict(hook=0.0, price=at("That's the price"), ctx=at('Sounds Fake'), rebuild=at("Let's rebuild"), before=at('The season before'), bottom=at('bottom of the'),
         months=at('four and a half'), stayed=at('They only'), seven=at('seven of'), title=at('Then the title'), wins=at('Twenty three'),
         draws=at('Twelve draws'), defeats=at('And just three'), points=at('Eighty one'), clear=at('Ten clear'),
         twist=at('And the champions'), twistNum=at('They finished'), vardy=at('Jamie Vardy'), record=at('A Premier League record'),
         goals24=at('Twenty four'), mahrez=at('Riyad Mahrez'), african=at('the first African'), again=at('Five thousand to one', 2),
         happened=at('it really'), ask=at('Will anyone'), yes=at('Yes or never'), nextq=at('Which record'), end=END)
CRESTS = ['lei', 'ars', 'che']
CREST_DATA = {k: 'data:image/png;base64,' + base64.b64encode(open(f'assets/{k}.png', 'rb').read()).decode() for k in CRESTS}
EP = {'crestData': CREST_DATA, 'beats': B, 'crests': CRESTS, 'colors': {'sky': '#070b16', 'accent': '#ffd54a'}, 'data': {},
  'cams': [
    {'t': 0, 'p': [0, 3.0, 15], 'l': [0, 3.6, 0], 'fov': 40, 'move': 1},
    {'t': B['ctx'], 'p': [0, 3.2, 15], 'l': [0, 3.6, 0], 'fov': 40, 'move': 1.0},
    {'t': B['before'], 'p': [0, 4.4, 14], 'l': [0, 4.0, 0], 'fov': 44, 'move': 1.0},
    {'t': B['stayed'], 'p': [0, 3.4, 12], 'l': [0, 3.0, 0], 'fov': 44, 'move': 1.0},
    {'t': B['title'], 'p': [0, 3.2, 13], 'l': [0, 4.0, 0], 'fov': 40, 'move': 1.0},
    {'t': B['defeats'], 'p': [2.2, 3.6, 13], 'l': [0, 4.0, 0], 'fov': 42, 'move': 2.5},
    {'t': B['points'], 'p': [0, 3.2, 14], 'l': [0, 3.4, 0], 'fov': 42, 'move': .9},
    {'t': B['twist'], 'p': [1.0, 3.0, 12], 'l': [1.0, 3.4, 0], 'fov': 42, 'move': 1.0},
    {'t': B['vardy'], 'p': [0, 6.5, 9.5], 'l': [0, 1.4, 0], 'fov': 46, 'move': .9},
    {'t': B['goals24'], 'p': [0, 4.5, 9.5], 'l': [0, 2.4, 1.2], 'fov': 46, 'move': 1.0},
    {'t': B['mahrez'], 'p': [0, 2.6, 9.5], 'l': [0, 2.0, 0], 'fov': 42, 'move': 1.0},
    {'t': B['again'], 'p': [0, 5.5, 16], 'l': [0, 5.6, 0], 'fov': 42, 'move': 1.2},
    {'t': B['ask'], 'p': [0, 6, 16], 'l': [0, 8.6, 0], 'fov': 42, 'move': 1.2},
  ]}
ov = []
def add(id, s, e, inner, kind='title'): ov.append((id, round(s, 3), round(e, 3), inner, kind))
G = lambda s: f'<b>{s}</b>'
SRC = '<div class="src">Data: Premier League 2015/16 (Wikipedia)</div>'
add('n-odds', 0.05, B['ctx'], '<div class="num">5000-1</div><div class="lab">TO WIN THE LEAGUE</div><div class="crow"><img src="assets/crests/lei.png"></div><div class="src">Pre-season odds, 2015/16 (Wikipedia)</div>', 'stat')
add('r-ctx', B['ctx'], B['rebuild'] + .9, '<div class="rk">SOUNDS</div><div class="rt">FAKE</div>', 'round')
add('ctx', B['rebuild'] - .3, B['bottom'] + .8, '<span>LEICESTER CITY · PREMIER LEAGUE · 2015/16</span>', 'chip')
add('t-bottom', B['before'], B['stayed'], f'BOTTOM FOR<br>{G("4½ MONTHS")}<div class="gs">the season before, 2014/15</div>')
add('t-seven', B['seven'], B['title'], f'<div class="num sm">7/9</div><div class="lab">LAST 9 GAMES WON</div><div class="sub">finished 14th</div>', 'stat')
add('t-title', B['title'], B['wins'], f'THE<br>{G("TITLE YEAR")}')
add('n-wdl', B['wins'], B['points'], '<div class="trio"><div><div class="num sm">23</div><div class="lab">WINS</div></div>'
    f'<div data-at="{B["draws"] - B["wins"]}"><div class="num sm sil">12</div><div class="lab">DRAWS</div></div>'
    f'<div data-at="{B["defeats"] - B["wins"] + .5}"><div class="num sm red">3</div><div class="lab">DEFEATS</div></div></div>' + SRC, 'stat')
add('n-pts', B['points'], B['twist'], f'<div class="pair"><div><div class="num sm">81</div><div class="lab">LEICESTER</div></div><div data-at="{B["clear"] - B["points"]}"><div class="num sm sil">71</div><div class="lab">ARSENAL</div></div></div><div class="per" data-at="{B["clear"] - B["points"] + .4}">+10 POINTS</div>' + SRC, 'stat')
add('t-twist', B['twist'], B['twistNum'], f'{G("THE CHAMPIONS?")}', 'glitch')
add('n-che', B['twistNum'], B['vardy'], '<div class="num">10TH</div><div class="lab">CHELSEA · 50 POINTS</div><div class="sub">the defending champions</div>' + SRC, 'stat')
add('n-vardy', B['vardy'] + .2, B['goals24'], '<div class="num" data-to="11">0</div><div class="lab">GAMES IN A ROW</div><div class="sub">Jamie Vardy scored in every one</div>', 'stat')
add('st-rec', B['record'], B['goals24'], 'PREMIER LEAGUE RECORD', 'stamp')
add('n-24', B['goals24'], B['mahrez'], '<div class="num" data-to="24">0</div><div class="lab">LEAGUE GOALS</div><div class="sub">Jamie Vardy, 2015/16</div>' + SRC, 'stat')
add('t-mahrez', B['mahrez'], B['again'], f'RIYAD MAHREZ<br>{G("PLAYERS&#39; PLAYER")}<div class="gs">of the year · first African winner</div>')
add('t-again', B['again'], B['ask'], f'{G("5000-1")}<br>AND IT HAPPENED')
add('ask', B['ask'], END - 1.6, f'<div class="q">YES</div><div class="or">or</div><div class="q b">NEVER?</div><div class="next" data-at="{B["nextq"] - B["ask"]}">Which record do we rebuild next? 👇</div>', 'ask')
for k, s in (('dip-1', B['title']), ('dip-2', B['vardy']), ('dip-3', B['again'])): add(k, s - .1, s + .12, '', 'dip')
DIGITS = [("five thousand to one", "5000-1"), ("twenty fifteen sixteen", "2015/16"), ("four and a half", "4½"), ("twenty three", "23"),
          ("eighty one", "81"), ("twenty four", "24"), ("seven", "7"), ("nine", "9"), ("twelve", "12"), ("three", "3"), ("ten", "10"),
          ("tenth", "10th"), ("eleven", "11")]
KEYW = {'leicester', 'fake', 'bottom', 'wins', 'draws', 'defeats', 'points', 'arsenal', 'chelsea', 'tenth', 'record', 'vardy', 'mahrez',
        'african', 'happened', 'never', 'yes', 'champions'}
PAIRS = {('premier', 'league'), ('leicester', 'city'), ('jamie', 'vardy'), ('riyad', 'mahrez'), ('title', 'year')}
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
HIDE = [(0, B['price'] - .05), (B['ctx'] - .05, B['rebuild']), (B['twist'] - .05, B['twistNum']), (B['again'] - .05, B['ask']), (B['ask'] - .05, END + 1)]
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


sfx = [('impact-2', 0.05, .9), ('cinematic-deep-boom', 0.08, .55), ('whoosh-2', B['ctx'] - .05, .7), ('impact-2', B['ctx'] + .3, .7),
       ('whoosh-cine', B['before'], .45), ('cc0-dark-sting', B['bottom'], .5), ('riser-1', B['title'] - 1.0, .45), ('whoosh-2', B['title'] - .05, .6),
       ('impact-2', B['wins'], .5), ('impact-2', B['draws'], .45), ('impact-2', B['defeats'] + .5, .55), ('impact-2', B['points'], .6),
       ('ding-1', B['clear'] + .4, .5), ('tech-glitch-1', B['twist'], .8), ('cinematic-deep-boom', B['twistNum'], .7),
       ('whoosh-cine', B['vardy'], .5), ('impact-2', B['record'], .8), ('whoosh-2', B['goals24'], .4),
       ('cinematic-deep-boom', B['mahrez'], .6), ('ding-1', B['african'], .45), ('riser-1', B['again'] - 1.0, .4), ('impact-2', B['again'], .8),
       ('whoosh-cine', B['ask'], .5), ('ding-1', B['yes'], .6), ('ding-1', B['nextq'], .5)]
sfx += [('pop-2', B['stayed'] + .3 + i * .17, .45) for i in range(9)]
sfx += [('wood-hit', B['title'] + .9 + i * .16, .3) for i in range(0, 23, 2)]
sfx += [('wood-hit', B['draws'] + i * .12, .3) for i in range(0, 12, 2)]
sfx += [('wood-hit', B['vardy'] + .55 + i * .22, .4) for i in range(11)]
sfx += [('tick-1', B['goals24'] + .2 + k * .12, .3) for k in range(8)]
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
