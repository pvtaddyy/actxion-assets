#!/usr/bin/env python3
"""Build the HyperFrames index.html for What If? half-time table.  python3 build.py -> hf/index.html"""
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
B = dict(hook=0.0, now=at("Right now"), nine=at('Nine wins'), clear=at('five points clear'), took=at('So I took'), whistle=at('blew the whistle'),
         twist=at('The new leaders'), bou=at('are Bournemouth'), seventh=at('Seventh in'), first=at('First at'), pts23=at('twenty three points'),
         seven=at('In seven'), brighton=at('Brighton stay'), villa=at('Then Villa'), brentford=at('then Brentford'), ars=at('And Arsenal'),
         fifth=at('Fifth on'), six=at('Six of their'), allsix=at('They won all six'), ten=at('Ten of their'), two=at('just two'),
         late=at("That's a team"), city=at('Man City drop'), real=at('Real table', 2), htt=at('Half-time table'), ask=at('So which half'),
         firstsec=at('First or second'), oneword=at('One word'), nextq=at('Which rule'), end=END)
OFF = 4.2
CLUBS = [
  dict(code='ars', name='ARSENAL', col=0xEF0107, fg='#ffffff', track=[[0, 1, 0], [B['twist'] + .1, 1, OFF], [B['fifth'] - .2, 5, OFF], [B['fifth'], 5, 0]]),
  dict(code='bha', name='BRIGHTON', col=0x0057B8, fg='#ffffff', track=[[0, 2, 0], [B['twist'] + .15, 2, OFF], [B['brighton'], 2, 0]]),
  dict(code='mci', name='MAN CITY', col=0x6CABDD, fg='#0a0f1c', track=[[0, 3, 0], [B['twist'] + .2, 3, OFF], [B['city'] - .2, 7, OFF], [B['city'], 7, 0]]),
  dict(code='bou', name='BOURNEMOUTH', col=0xB50E12, fg='#ffffff', track=[[0, 7, 0], [B['twist'] + .25, 1, 0]]),
  dict(code='bre', name='BRENTFORD', col=0xF2F2F2, fg='#d20a0a', track=[[0, 8, 0], [B['twist'] + .3, 8, OFF], [B['brentford'] - .2, 4, OFF], [B['brentford'], 4, 0]]),
  dict(code='avl', name='ASTON VILLA', col=0x670E36, fg='#ffffff', track=[[0, 10, 0], [B['twist'] + .35, 10, OFF], [B['villa'] - .2, 3, OFF], [B['villa'], 3, 0]]),
]
# Bournemouth half-time scores, in date order (facts.tsv / E0.csv HTHG-HTAG)
BOU = [('1-0 MCI', 'W'), ('1-0 EVE', 'W'), ('2-1 NEW', 'W'), ('1-1 BRE', 'D'), ('0-0 LIV', 'D'), ('0-2 CHE', 'L'), ('1-0 SUN', 'W'), ('2-0 MUN', 'W'), ('1-0 LEE', 'W'), ('1-0 IPS', 'W')]
ARS = [('0-0 AVL', '1-0 AVL'), ('1-1 CHE', '2-1 CHE'), ('0-0 SUN', '2-0 SUN'), ('0-0 LEE', '2-1 LEE'), ('0-0 NFO', '1-0 NFO'), ('0-0 HUL', '1-0 HUL')]
bstep = (B['brighton'] - B['seven'] - .6) / 10
astep = (B['allsix'] - B['six'] - .3) / 6
CRESTS = ['ars', 'bou']
CREST_DATA = {k: 'data:image/png;base64,' + base64.b64encode(open(f'assets/{k}.png', 'rb').read()).decode() for k in CRESTS}
EP = {'crestData': CREST_DATA, 'beats': B, 'crests': CRESTS, 'colors': {'sky': '#070b16', 'accent': '#ffd54a'},
  'data': {'clubs': CLUBS, 'bou': [{'label': l, 'res': r, 'at': B['seven'] + .3 + i * bstep} for i, (l, r) in enumerate(BOU)],
           'ars': [{'ht': h, 'ft': f, 'at': B['six'] + .2 + i * astep} for i, (h, f) in enumerate(ARS)]},
  'cams': [
    {'t': 0, 'p': [0, 1.15, 14.5], 'l': [0, .85, 0], 'fov': 42, 'move': 1},
    {'t': B['now'], 'p': [.3, 1.2, 13.8], 'l': [.2, .9, 0], 'fov': 42, 'move': 1.2},
    {'t': B['twist'], 'p': [1.05, 2.3, 7.5], 'l': [1.05, 2.0, 0], 'fov': 42, 'move': .6},
    {'t': B['seventh'], 'p': [0, 1.15, 14.5], 'l': [0, .85, 0], 'fov': 42, 'move': .8},
    {'t': B['ten'], 'p': [0, .75, 11], 'l': [0, .55, 0], 'fov': 42, 'move': .8},
    {'t': B['city'], 'p': [0, 1.15, 14.5], 'l': [0, .85, 0], 'fov': 42, 'move': .8},
    {'t': B['real'], 'p': [0, .9, 11], 'l': [0, .7, 0], 'fov': 42, 'move': .8},
    {'t': B['ask'], 'p': [0, 3.8, 11.5], 'l': [0, 3.7, 0], 'fov': 42, 'move': 1.0},
  ]}
ov = []
def add(id, s, e, inner, kind='title'): ov.append((id, round(s, 3), round(e, 3), inner, kind))
G = lambda s: f'<b>{s}</b>'
SRC = '<div class="src">Data: football-data.co.uk half-time scores, to 8 Nov 2026</div>'
add('t-hook', 0.05, B['now'], f'STOP EVERY GAME<br>AT {G("HALF-TIME")}<div class="gs">who\'s top?</div>')
add('ctx', 0.9, B['took'], '<span>PREMIER LEAGUE 2026/27 · FIRST 10 GAMES</span>', 'chip')
add('t-now', B['now'], B['took'], f'ARSENAL {G("1ST")}<div class="gs">9 wins from 10 · 27 pts</div>')
add('t-took', B['took'], B['twist'], f'{G("100")} GAMES<div class="gs">final whistle at 45 minutes</div>')
add('t-bou', B['twist'] + .05, B['seventh'], f'{G("BOURNEMOUTH")}', 'glitch')
add('n-7', B['seventh'], B['seven'], '<div class="pair"><div><div class="num sm sil">7TH</div><div class="lab">REAL TABLE</div></div><div data-at="' + str(round(B['first'] - B['seventh'], 2)) + '"><div class="num sm">1ST</div><div class="lab">HALF-TIME</div><div class="sub" data-at="' + str(round(B['pts23'] - B['seventh'], 2)) + '">23 pts</div></div></div>' + SRC, 'stat')
add('t-seven', B['seven'], B['brighton'], f'{G("7")} OF 10<div class="gs">winning at half-time</div>')
add('t-top4', B['brighton'], B['ars'], f'HALF-TIME {G("TOP 4")}')
add('st-5', B['fifth'], B['six'], 'ARSENAL 5TH · 15 PTS', 'stamp')
add('t-six', B['six'], B['allsix'], f'{G("6")} LEVEL<div class="gs">at half-time</div>')
add('t-allsix', B['allsix'], B['ten'], f'{G("6")} WINS<div class="gs">at full time</div>')
add('n-goals', B['ten'], B['late'], '<div class="pair"><div><div class="num sm sil">5</div><div class="lab">1ST HALF</div></div><div data-at=".6"><div class="num sm">10</div><div class="lab">2ND HALF</div></div></div><div class="sub">Arsenal league goals</div><div class="per" data-at="' + str(round(B['two'] - B['ten'], 2)) + '">CONCEDED 2 AFTER THE BREAK</div>' + SRC, 'stat')
add('t-late', B['late'], B['city'], f'WINS IT {G("LATE")}')
add('t-city', B['city'], B['real'], f'MAN CITY {G("7TH")}<div class="gs">3rd in the real table</div>')
add('t-real', B['real'], B['ask'], f'REAL TABLE<br>{G("ARSENAL")}<div class="gs" data-at="{round(B["htt"] - B["real"], 2)}">half-time table: Bournemouth</div>')
add('ask', B['ask'], END - 1.6, f'<div class="q">FIRST HALF</div><div class="or">or</div><div class="q b">SECOND HALF?</div><div class="next" data-at="{round(B["nextq"] - B["ask"], 2)}">Which rule do we change next? 👇</div>', 'ask')
for k, s in (('dip-1', B['twist']), ('dip-2', B['ten'])): add(k, s - .1, s + .12, '', 'dip')
DIGITS = [("twenty three", "23"), ("hundred", "100"), ("seventh", "7th"), ("fifth", "5th"), 
          ("fifteen", "15"), ("seven", "7"), ("nine", "9"), ("ten", "10"), ("five", "5"), ("six", "6"), ("two", "2")]
KEYW = {'arsenal', 'bournemouth', 'brighton', 'villa', 'brentford', 'city', 'half-time', 'halftime', 'top', 'leaders', 'late', 'break', 'points', 'wins', 'won', 'level', 'whistle'}
PAIRS = {('premier', 'league'), ('man', 'city'), ('who\'s', 'top'), ('real', 'table'), ('one', 'word'), ('all', '6')}
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
HIDE = [(0, B['now'] - .05), (B['twist'] - .05, B['seventh']), (B['ask'] - .05, END + 1)]
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


sfx = [('impact-2', 0.05, .9), ('cinematic-deep-boom', 0.08, .55), ('whoosh-2', .9, .5), ('whoosh-cine', B['now'], .5), ('ding-1', B['nine'] + .2, .45),
       ('whoosh-2', B['took'], .55), ('riser-1', B['took'] + .2, .3), ('tick-1', B['took'] + .6, .3), ('tick-1', B['took'] + 1.0, .3), ('tick-1', B['took'] + 1.4, .3),
       ('impact-2', B['whistle'] + .2, .6),
       ('tech-glitch-1', B['twist'], .8), ('cinematic-deep-boom', B['twist'] + .05, .6), ('impact-2', B['bou'] + .3, .8),
       ('whoosh-cine', B['seventh'], .5), ('impact-2', B['seventh'] + .3, .55), ('impact-2', B['first'], .7), ('ding-1', B['pts23'], .5),
       ('whoosh-2', B['seven'], .5),
       ('whoosh-2', B['brighton'], .5), ('impact-2', B['brighton'] + .5, .55), ('impact-2', B['villa'] + .4, .55), ('impact-2', B['brentford'] + .4, .55),
       ('whoosh-cine', B['ars'], .5), ('cinematic-deep-boom', B['fifth'], .6), ('impact-2', B['fifth'] + .2, .8),
       ('whoosh-2', B['six'], .5), ('riser-1', B['allsix'] - .5, .35), ('ding-1', B['allsix'] + .2, .55),
       ('whoosh-cine', B['ten'], .5), ('impact-2', B['ten'] + .9, .6), ('impact-2', B['ten'] + 1.5, .6), ('impact-2', B['two'], .7),
       ('whoosh-2', B['late'], .5), ('whoosh-cine', B['city'], .5), ('impact-2', B['city'] + .9, .6),
       ('whoosh-2', B['real'], .5), ('impact-2', B['real'] + .3, .6), ('impact-2', B['htt'] + .3, .7),
       ('whoosh-cine', B['ask'], .5), ('impact-2', B['ask'] + .9, .5), ('ding-1', B['oneword'], .55), ('ding-1', B['nextq'], .5)]
sfx += [('wood-hit', r['at'] + .35, .45) for r in EP['data']['bou'][::2]]
sfx += [('wood-hit', r['at'] + .35, .45) for r in EP['data']['ars']]
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
