#!/usr/bin/env python3
"""Build the HyperFrames index.html for a Myth or Fact? episode from words.json + this file's EPISODE block.
   python3 build.py   ->  hf/index.html
"""
import json, re, html

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

END = round(words[-1]['e'] + 2.2, 2)
B = dict(myth=at('Everyone says'), total=at('A hundred and twenty'), r1=at('Round one'), big=at('Against Arsenal'),
         bigNum=at('twenty seven'), bigPer=at('Nought point six', 1), rest=at('Against everyone'), elseNum=at('Ninety four'),
         restPer=at('Nought point nine'), totPer=at('nought point eight'), feastPer=at('Nearly one'), addPer=at('Nought point three'), journey=at('I went through'), slow=at('So yes'), r2=at('Round two'), feast=at('West Ham'), feastNum=at('Thirty one'),
         twist=at("But here's"), newc=at('Newcastle. Seven'), newcOne=at('One goal'), add=at('Add Villa'), worse=at('Worse than'),
         verdict=at('So, the verdict'), verd2=at('He does score'), elite=at('still elite'), real=at('His real'),
         itsNew=at("It's Newcastle"), ask=at('Big game player'), nextq=at('And which myth'), end=END)
B['else'] = B['rest']

grid = [{'club': 'new', 'scored': i == 3} for i in range(7)] + \
       [{'club': 'avl', 'scored': i in (1, 4)} for i in range(6)] + \
       [{'club': 'bou', 'scored': i in (0, 2, 5, 7)} for i in range(9)]
import base64
CREST_DATA = {k: 'data:image/png;base64,' + base64.b64encode(open(f'assets/{k}.png','rb').read()).decode() for k in ['ars','liv','che','tot','mun','whu','cry','wol','new','avl','bou','pl']}
EP = {
  'crestData': CREST_DATA,
  'beats': B,
  'colors': {'sky': '#070b16', 'shirt': '#6CABDD', 'shorts': '#ffffff', 'socks': '#6CABDD', 'hair': '#e8cf8a', 'accent': '#ffd54a'},
  'hero': {'num': '9'},
  'crests': ['ars', 'liv', 'che', 'tot', 'mun', 'whu', 'cry', 'wol', 'new', 'avl', 'bou', 'pl'],
  'data': {'total': 121, 'bigG': 27, 'restG': 94, 'feastG': 31, 'grid': grid,
           'pillars': [{'v': .92, 'color': '#6CABDD'}, {'v': .69, 'color': '#ffd54a'}, {'v': .32, 'color': '#9aa3b5'}]},
  'cams': [
    {'t': 0, 'p': [0, 3.4, 13], 'l': [0, 2.6, 0], 'fov': 38, 'move': 3.2},
    {'t': B['myth'], 'p': [0, 2.2, 7.2], 'l': [0, 2.0, 0], 'fov': 40, 'move': 1.2},
    {'t': B['total'], 'p': [0, 8, 10], 'l': [0, 1.8, 0], 'fov': 44, 'move': 1.0},
    {'t': B['big'], 'p': [0, 3.4, 12.5], 'l': [0, 4.2, 0], 'fov': 40, 'move': .9},
    {'t': B['slow'], 'p': [2.2, 4.4, 11.5], 'l': [0, 4.0, 0], 'fov': 40, 'move': 2.5},
    {'t': B['feast'], 'p': [0, 6, 10.5], 'l': [0, 3.2, 0], 'fov': 44, 'move': .8},
    {'t': B['newc'], 'p': [0, 6.5, 8.5], 'l': [0, 2.6, -.8], 'fov': 44, 'move': .9},
    {'t': B['add'], 'p': [0, 8.5, 9.5], 'l': [0, 2.4, -2.2], 'fov': 46, 'move': 1.0},
    {'t': B['verd2'], 'p': [0, 3.2, 14], 'l': [0, 4.0, 0], 'fov': 40, 'move': 1.0},
    {'t': B['real'], 'p': [0, 2.8, 9], 'l': [0, 3.8, -1], 'fov': 40, 'move': 1.0},
    {'t': B['ask'], 'p': [0, 1.8, 9.5], 'l': [0, 3.9, -1.5], 'fov': 40, 'move': 1.5},
  ],
}

# ---------------- overlays ----------------
ov = []   # (id, start, end, html, kind)
def add(id, s, e, inner, kind='title'): ov.append((id, round(s, 3), round(e, 3), inner, kind))
G = lambda s: f'<b>{s}</b>'
add('t-hook', 0.05, B['myth'], f'ONE CLUB HE <br>{G("CAN&#39;T SCORE")} AGAINST')
add('ctx', .3, B['total'], '<span>ERLING HAALAND · MAN CITY · PREMIER LEAGUE</span>', 'chip')
add('t-myth', B['myth'], B['journey'], f'"HE ONLY BULLIES<br>{G("SMALL TEAMS")}"')
add('st-myth', B['myth'] + 1.3, B['journey'], 'MYTH OR FACT?', 'stamp')
add('t-journey', B['journey'], B['total'], f'EVERY PREMIER LEAGUE<br>{G("GOAL")} SINCE 2022')
add('n-total', B['total'], B['r1'], '<div class="num" data-to="121">0</div><div class="lab">PREMIER LEAGUE GOALS</div><div class="sub">in 141 games</div><div class="per" data-at="%s">0.86 a game</div><div class="src">Data: StatMuse</div>' % (B['totPer'] - B['total']), 'stat')
add('r-1', B['r1'], B['big'], '<div class="rk">ROUND 1</div><div class="rt">THE BIG SIX</div><div class="crow big"><img src="assets/crests/ars.png"><img src="assets/crests/liv.png"><img src="assets/crests/che.png"><img src="assets/crests/tot.png"><img src="assets/crests/mun.png"></div><div class="rs">v Arsenal · Liverpool · Chelsea<br>Spurs · Man United</div>', 'round')
add('n-big', B['big'], B['r2'], '<div class="pair"><div><div class="num sm" data-to="27" data-delay="%s">0</div><div class="lab">v BIG SIX</div><div class="crow"><img src="assets/crests/ars.png"><img src="assets/crests/liv.png"><img src="assets/crests/che.png"><img src="assets/crests/tot.png"><img src="assets/crests/mun.png"></div><div class="sub">39 games</div><div class="per" data-at="%s">0.69 a game</div></div>'
    '<div><div class="num sm" data-to="94" data-delay="%s">0</div><div class="lab">v EVERYONE ELSE</div><div class="crow"><img src="assets/crests/pl.png"></div><div class="sub">102 games</div><div class="per" data-at="%s">0.92 a game</div></div></div><div class="src">Data: StatMuse</div>'
    % (B['bigNum'] - B['big'], B['bigPer'] - B['big'], B['elseNum'] - B['big'], B['restPer'] - B['big']), 'stat')
ov[-1] = ov[-1][:2] + (round(B['slow'] + .25, 3),) + ov[-1][3:]
add('t-slow', B['slow'] + .3, B['r2'], f'THE BIG CLUBS<br>{G("DO SLOW HIM")}')
add('bars-slow', B['slow'] + 1.2, B['r2'], '<div class="bars panel"><div class="bar" style="--v:.69;--c:#ffd54a"><i></i><span>v Big Six 0.69</span></div><div class="bar" style="--v:.92;--c:#6CABDD"><i></i><span>v everyone else 0.92</span></div></div>', 'bars')
add('dip-1', B['feast'] - .1, B['feast'] + .12, '', 'dip')
add('dip-2', B['add'] - .1, B['add'] + .12, '', 'dip')
add('r-2', B['r2'], B['feast'], '<div class="rk">ROUND 2</div><div class="rt">WHO DOES HE FEAST ON?</div>', 'round')
add('n-feast', B['feastNum'], B['twist'], '<div class="num" data-to="31">0</div><div class="lab">GOALS IN 21 GAMES</div><div class="sub">West Ham · Palace · Wolves</div><div class="per" data-at="%s">1.48 a game</div><div class="src">Data: StatMuse</div>' % (B['feastPer'] - B['feastNum']), 'stat')
add('t-twist', B['twist'], B['newc'], f'{G("THE TWIST")}<div class="gs">The club that stops him<br>isn&#39;t in the Big Six</div>', 'glitch')
add('n-newc', B['newc'] + .4, B['add'], '<div class="num">1</div><div class="lab">GOAL IN 7 GAMES</div><div class="sub">v Newcastle</div>', 'stat')
add('n-add', B['add'] + .6, B['verdict'], '<div class="num" data-to="7">0</div><div class="lab">GOALS IN 22 GAMES</div><div class="sub">Newcastle · Villa · Bournemouth</div><div class="per" data-at="%s">0.32 a game</div><div class="src">Data: StatMuse</div>' % (B['addPer'] - B['add'] - .6), 'stat')
add('bars-worse', B['worse'], B['verdict'], '<div class="bars panel"><div class="bar" style="--v:.69;--c:#ffd54a"><i></i><span>Big Six 0.69</span></div><div class="bar" style="--v:.32;--c:#9aa3b5"><i></i><span>NEW · AVL · BOU 0.32</span></div></div>', 'bars')
add('r-v', B['verdict'], B['verd2'], '<div class="rk">THE</div><div class="rt">VERDICT</div>', 'round')
add('t-v', B['verd2'], B['real'], '<div class="plab"><span>EVERYONE<br>ELSE<br><b>0.92</b></span><span>BIG<br>SIX<br><b>0.69</b></span><span>NEW · AVL<br>· BOU<br><b>0.32</b></span></div>', 'pl')
add('st-v', B['elite'], B['real'], 'HALF TRUE', 'stamp')
add('t-real', B['real'], B['ask'], f'HIS REAL PROBLEM?<br>{G("NEWCASTLE")}')
add('ask', B['ask'], END - 1.6, f'<div class="q">BIG GAME PLAYER</div><div class="or">or</div><div class="q b">FLAT TRACK BULLY?</div><div class="next" data-at="{B["nextq"] - B["ask"]}">Which myth do we test next? 👇</div>', 'ask')

# ---------------- captions v3: phrases of 1-3 tokens, numbers as digits, word-by-word light-up ----------------
DIGITS = [("a hundred and twenty one", "121"), ("a hundred and forty one", "141"), ("a hundred and two", "102"),
          ("nought point eight six", "0.86"), ("nought point six nine", "0.69"), ("nought point nine two", "0.92"),
          ("nought point three two", "0.32"), ("twenty twenty two", "2022"), ("twenty seven", "27"), ("thirty nine", "39"),
          ("ninety four", "94"), ("thirty one", "31"), ("twenty one", "21"), ("twenty two", "22"),
          ("one and a half", "1.5"), ("seven", "7"), ("one goal", "1 goal")]
KEYW = {'small', 'myth', 'fact', 'big', 'six', 'feast', 'newcastle', 'twist', 'verdict', 'elite', 'bully', 'player',
        'wolves', 'palace', 'ham', 'villa', 'bournemouth', 'mile', 'slow', 'every', 'one'}
PAIRS = {('west', 'ham'), ('big', 'six'), ('man', "city's"), ('premier', 'league'), ('flat', 'track'), ('big', 'game'), ('big', 'clubs')}
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
HIDE = [(B['r1'] - .05, B['big']), (B['r2'] - .05, B['feast']), (B['twist'] - .05, B['newc']), (B['verdict'] - .05, B['verd2']),
        (B['real'] - .05, END + 1)]
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

# ---------------- sound effects (crisp, on graphics) ----------------
sfx = [('impact-2', 0.0, .9), ('cinematic-deep-boom', 0.02, .5), ('whoosh-cine', B['myth'] - .1, .5), ('impact-2', B['myth'] + 1.3, .8),
       ('riser-1', B['r1'] - 1.0, .45), ('whoosh-2', B['r1'] - .05, .7), ('impact-2', B['bigNum'], .45), ('impact-2', B['elseNum'], .45),
       ('riser-1', B['r2'] - 1.0, .45), ('whoosh-2', B['r2'] - .05, .7), ('tech-glitch-1', B['twist'], .8),
       ('cinematic-deep-boom', B['newc'], .8), ('pop-2', B['newcOne'], .8), ('whoosh-cine', B['add'], .45),
       ('cc0-dark-sting', B['worse'], .55), ('impact-2', B['verdict'], .8), ('impact-2', B['elite'], .9),
       ('cinematic-deep-boom', B['real'], .55), ('whoosh-cine', B['ask'], .5), ('ding-1', B['ask'] + 1.0, .6), ('ding-1', B['nextq'], .5),
       ('whoosh-2', B['slow'] + .3, .4), ('whoosh-2', B['journey'], .3)]
sfx += [('tick-1', B['total'] + .1 + k * .12, .3) for k in range(0, 11)]
sfx += [('wood-hit', B['bigNum'] + k * 1.6 / 26 + .2, .35) for k in range(0, 6)]
sfx += [('wood-hit', B['elseNum'] + k * 2.0 / 93 + .2, .35) for k in range(0, 8, 2)]
sfx += [('cinematic-deep-boom', B['feast'] + i * .35 + .3, .45) for i in range(3)]

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
