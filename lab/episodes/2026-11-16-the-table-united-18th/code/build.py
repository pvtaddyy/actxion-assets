#!/usr/bin/env python3
"""Build the HyperFrames index.html for The Table: Man Utd 18th.  python3 build.py -> hf/index.html"""
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
B = dict(hook=0.0, watch=at('Watch where'), g1=at('Game one'), hull=at('Hull'), seventeenth=at('Seventeenth'), g2=at('Game two'), ipswich=at('Ipswich'),
         tenth=at('Up to tenth'), twist=at('That was their'), aug=at('The thirtieth'), since=at('Since then'), notone=at('Not one win'),
         draws=at('Draws with'), eve=at('Everton'), ful=at('Fulham'), spurs=at('Spurs'), leeds=at('Leeds'), defeats=at('Defeats to'), city=at('City'),
         bou=at('Bournemouth'), che=at('Chelsea'), then=at('Then four'), villa=at('Villa'), eighteenth=at('Eighteenth'), points=at('Eight points'),
         arsenal=at('Arsenal top'), carrick=at('Michael Carrick'), poch=at('Mauricio Pochettino'), nov=at('the eighteenth of November'),
         first=at('His first game'), fourth=at("They're fourth"), tenpts=at('ten points clear'), ask=at('Who gets United'), oneword=at('One word'),
         nextq=at('Which club'), end=END)
TOWER = [('0-2 HUL', 'L', 'hull'), ('5-2 IPS', 'W', 'ipswich'), ('2-2 EVE', 'D', 'eve'), ('1-1 FUL', 'D', 'ful'), ('1-1 TOT', 'D', 'spurs'), ('1-1 LEE', 'D', 'leeds'),
         ('0-1 MCI', 'L', 'city'), ('0-3 BOU', 'L', 'bou'), ('0-2 CHE', 'L', 'che'), ('4-4 AVL', 'D', 'villa')]
# position after that game (united_by_matchday.tsv): HUL 17, IPS 10, EVE 11, MCI 13, FUL 12, TOT 13, LEE 13, BOU 16, CHE 17, AVL 18
TRACK = [[0, 3], [B['seventeenth'] - .3, 17], [B['tenth'], 10], [B['eve'] + .3, 11], [B['ful'] + .3, 12], [B['spurs'] + .3, 13], [B['leeds'] + .3, 13],
         [B['city'] + .3, 13], [B['bou'] + .3, 16], [B['che'] + .3, 17], [B['eighteenth'] - .1, 18]]
CRESTS = ['mun', 'ars', 'liv', 'hul']
CREST_DATA = {k: 'data:image/png;base64,' + base64.b64encode(open(f'assets/{k}.png', 'rb').read()).decode() for k in CRESTS}
EP = {'crestData': CREST_DATA, 'beats': B, 'crests': CRESTS, 'colors': {'sky': '#070b16', 'accent': '#ffd54a'},
  'data': {'tower': [{'label': l, 'res': r, 'at': B[k] + .1} for l, r, k in TOWER], 'track': TRACK},
  'cams': [
    {'t': 0, 'p': [0, 1.15, 14.5], 'l': [0, .85, 0], 'fov': 42, 'move': 1},
    {'t': B['g1'], 'p': [.2, 1.15, 14.3], 'l': [.1, .85, 0], 'fov': 42, 'move': 1.2},
    {'t': B['twist'], 'p': [-1.3, .55, 6], 'l': [-1.3, .2, 0], 'fov': 42, 'move': .6},
    {'t': B['since'], 'p': [0, 1.15, 14.5], 'l': [0, .85, 0], 'fov': 42, 'move': .8},
    {'t': B['points'], 'p': [0, .75, 11], 'l': [0, .55, 0], 'fov': 42, 'move': .8},
    {'t': B['carrick'], 'p': [0, 1.05, 13], 'l': [0, .7, 0], 'fov': 42, 'move': .8},
    {'t': B['first'], 'p': [0, .75, 11], 'l': [0, .55, 0], 'fov': 42, 'move': .8},
    {'t': B['ask'], 'p': [0, 3.8, 11.5], 'l': [0, 3.7, 0], 'fov': 42, 'move': 1.0},
  ]}
ov = []
def add(id, s, e, inner, kind='title'): ov.append((id, round(s, 3), round(e, 3), inner, kind))
G = lambda s: f'<b>{s}</b>'
SRC = '<div class="src">Data: football-data.co.uk results, to 8 Nov 2026</div>'
add('t-last', 0.05, B['watch'], f'LAST SEASON<br>{G("3RD")}<div class="gs">Premier League 2025/26</div>')
add('t-now', B['watch'], B['g1'], f'THIS SEASON?')
add('ctx', 0.9, B['g1'] + 1.0, '<span>MAN UTD · PREMIER LEAGUE 2026/27 · GAME BY GAME</span>', 'chip')
add('t-g1', B['g1'], B['g2'], f'GAME 1<div class="gs">Hull 2-0 Man Utd</div>')
add('t-g2', B['g2'], B['twist'], f'GAME 2<div class="gs">Man Utd 5-2 Ipswich</div>')
add('t-last-win', B['twist'], B['aug'], f'{G("LAST WIN")}', 'glitch')
add('st-aug', B['aug'], B['since'], '30 AUG 2026', 'stamp')
add('n-since', B['since'], B['draws'], '<div class="trio"><div><div class="num sm sil">8</div><div class="lab">GAMES</div></div><div data-at="' + str(round(B['notone'] - B['since'], 2)) + '"><div class="num sm red">0</div><div class="lab">WINS</div></div></div>' + SRC, 'stat')
add('t-draws', B['draws'], B['defeats'], f'{G("4")} DRAWS')
add('t-def', B['defeats'], B['then'], f'{G("3")} DEFEATS')
add('t-villa', B['then'], B['eighteenth'], f'4-4<div class="gs">Man Utd v Aston Villa</div>')
add('st-18', B['eighteenth'], B['points'], '18TH · DROP ZONE', 'stamp')
add('n-pts', B['points'], B['carrick'], '<div class="pair"><div><div class="num sm red">8</div><div class="lab">MAN UTD</div></div><div data-at="' + str(round(B['arsenal'] - B['points'], 2)) + '"><div class="num sm">27</div><div class="lab">ARSENAL (1ST)</div></div></div><div class="sub">points after 10 games</div>' + SRC, 'stat')
add('t-carrick', B['carrick'], B['poch'], f'CARRICK<br>{G("SACKED")}<div class="gs">12 Nov 2026</div>')
add('t-poch', B['poch'], B['first'], f'POCHETTINO<div class="gs" data-at="{round(B["nov"] - B["poch"], 2)}">starts 18 Nov</div>')
add('t-first', B['first'], B['fourth'], f'FIRST GAME<br>{G("ANFIELD")}<div class="gs">Liverpool v Man Utd · 22 Nov</div>')
add('n-liv', B['fourth'], B['ask'], '<div class="pair"><div><div class="num sm red">18TH</div><div class="lab">MAN UTD</div><div class="sub">8 pts</div></div><div><div class="num sm">4TH</div><div class="lab">LIVERPOOL</div><div class="sub">18 pts</div></div></div><div class="per" data-at="' + str(round(B['tenpts'] - B['fourth'], 2)) + '">10 POINTS APART</div>' + SRC, 'stat')
add('ask', B['ask'], END - 1.6, f'<div class="q">SQUAD</div><div class="or">or</div><div class="q b">MANAGER?</div><div class="next" data-at="{B["nextq"] - B["ask"]}">Which club goes on the table next? 👇</div>', 'ask')
for k, s in (('dip-1', B['twist']), ('dip-2', B['points']), ('dip-3', B['carrick'])): add(k, s - .1, s + .12, '', 'dip')
DIGITS = [("two nil", "2-0"), ("five two", "5-2"), ("four four", "4-4"), ("twenty seven", "27"), ("seventeenth", "17th"), ("eighteenth", "18th"),
          ("tenth", "10th"), ("fourth", "4th"), ("third", "3rd"), ("thirtieth", "30th"), ("eight", "8"), ("ten", "10"), ("one", "1"), ("two", "2")]
KEYW = {'united', 'hull', 'ipswich', 'win', 'august', 'everton', 'fulham', 'spurs', 'leeds', 'city', 'bournemouth', 'chelsea', 'villa', 'arsenal',
        'carrick', 'sacked', 'pochettino', 'liverpool', 'squad', 'manager', 'draws', 'defeats', 'points'}
PAIRS = {('manchester', 'united'), ('michael', 'carrick'), ('mauricio', 'pochettino'), ('newly', 'promoted'), ('not', '1'), ('last', 'league')}
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
HIDE = [(0, B['watch'] - .05), (B['twist'] - .05, B['aug']), (B['ask'] - .05, END + 1)]
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


sfx = [('impact-2', 0.05, .9), ('cinematic-deep-boom', 0.08, .55), ('whoosh-2', .9, .5), ('whoosh-cine', B['watch'], .5), ('tick-1', B['watch'] + .2, .3), ('tick-1', B['watch'] + .4, .3),
       ('whoosh-2', B['g1'], .55), ('impact-2', B['hull'] + .45, .6), ('whoosh-cine', B['seventeenth'] - .3, .55), ('impact-2', B['seventeenth'] + .4, .6),
       ('whoosh-2', B['g2'], .55), ('impact-2', B['ipswich'] + .45, .6), ('riser-1', B['tenth'] - .6, .35), ('ding-1', B['tenth'] + .5, .5),
       ('tech-glitch-1', B['twist'], .8), ('cinematic-deep-boom', B['twist'] + .05, .6), ('impact-2', B['aug'] + .2, .8),
       ('whoosh-cine', B['since'], .5), ('impact-2', B['since'] + .3, .55), ('impact-2', B['notone'], .7),
       ('whoosh-2', B['draws'], .5), ('whoosh-2', B['defeats'], .5), ('whoosh-cine', B['then'], .5), ('impact-2', B['villa'] + .45, .6),
       ('cinematic-deep-boom', B['eighteenth'], .6), ('impact-2', B['eighteenth'] + .2, .8),
       ('whoosh-cine', B['points'], .5), ('riser-1', B['points'] + .1, .3), ('impact-2', B['arsenal'] + .9, .6),
       ('cinematic-deep-boom', B['carrick'], .55), ('impact-2', B['carrick'] + .9, .7), ('whoosh-2', B['poch'], .5), ('ding-1', B['nov'], .5),
       ('whoosh-cine', B['first'], .5), ('impact-2', B['first'] + .9, .6), ('impact-2', B['fourth'], .55), ('impact-2', B['tenpts'], .7),
       ('whoosh-cine', B['ask'], .5), ('impact-2', B['ask'] + .9, .5), ('ding-1', B['oneword'], .55), ('ding-1', B['nextq'], .5)]
sfx += [('wood-hit', B[k] + .1 + .45, .5) for l, r, k in TOWER[2:9]]
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
